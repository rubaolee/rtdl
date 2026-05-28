#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


DEFAULT_JSON = ROOT / "docs" / "reports" / "goal2645_raydb_rt_perf_pod_2026-05-27.json"
DEFAULT_MD = ROOT / "docs" / "reports" / "goal2645_raydb_rt_perf_pod_2026-05-27.md"
PAPER_RT_BACKEND = raydb.PAPER_RT_OPTIX_BACKEND
PAPER_RT_CPU_BACKEND = raydb.PAPER_RT_CPU_REFERENCE_BACKEND
PAPER_RT_EMBREE_BACKEND = raydb.PAPER_RT_EMBREE_BACKEND


def _run_command(command: list[str], *, timeout: int = 120, cwd: Path = ROOT) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "elapsed_sec": time.perf_counter() - started,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-12000:],
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": 127,
            "elapsed_sec": time.perf_counter() - started,
            "stdout": "",
            "stderr": str(exc),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "elapsed_sec": time.perf_counter() - started,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-12000:] if isinstance(exc.stderr, str) else "",
        }


def _parse_csv_ints(text: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("expected comma-separated positive integers")
    return values


def _parse_csv_text(text: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in text.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected comma-separated names")
    return values


def _environment_snapshot() -> dict[str, Any]:
    git_commit_result = _run_command(["git", "rev-parse", "HEAD"], timeout=10)
    git_status_result = _run_command(["git", "status", "--short"], timeout=10)
    source_commit = git_commit_result["stdout"].strip()
    status_lines = git_status_result["stdout"].splitlines()
    if not source_commit:
        source_commit = os.environ.get("RTDL_SOURCE_COMMIT", "")
    if not source_commit and (ROOT / ".rtdl_source_commit").exists():
        source_commit = (ROOT / ".rtdl_source_commit").read_text(encoding="utf-8").strip()
    if not status_lines and (ROOT / ".rtdl_source_status").exists():
        status_lines = (ROOT / ".rtdl_source_status").read_text(encoding="utf-8").splitlines()
    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "cwd": str(ROOT),
        "git_commit": source_commit or "unknown",
        "git_status_short": status_lines,
        "nvidia_smi": _run_command(["nvidia-smi"], timeout=20),
        "nvcc_version": _run_command(["nvcc", "--version"], timeout=20),
        "make_build_optix_target": "make build-optix",
        "make_build_embree_target": "make build-embree",
        "rtdl_source_tree": str(ROOT),
    }


def _build_backends_if_requested(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.dry_run:
        return {"skipped": True, "reason": "dry_run"}
    results: dict[str, Any] = {}
    if args.skip_build_embree:
        results["embree"] = {"skipped": True, "reason": "skip_build_embree"}
    else:
        results["embree"] = _run_command(["make", "build-embree"], timeout=args.build_timeout_sec)
    if args.skip_build_optix:
        results["optix"] = {"skipped": True, "reason": "skip_build_optix"}
    else:
        results["optix"] = _run_command(["make", "build-optix"], timeout=args.build_timeout_sec)
    return results


def _measure_once(backend: str, mode: str, copies: int, args: argparse.Namespace) -> dict[str, Any]:
    started = time.perf_counter()
    payload = raydb.run_result_mode(
        mode,
        backend=backend,
        copies=copies,
        fixture_kind=args.fixture_kind,
        generated_rows=args.generated_rows,
        generated_groups=args.generated_groups,
        generated_revenue_mod=args.generated_revenue_mod,
    )
    wall_sec = time.perf_counter() - started
    metadata = dict(payload.get("metadata", {}))
    timings = dict(metadata.get("timings", {}))
    return {
        "backend": backend,
        "mode": mode,
        "copies": copies,
        "row_count": int(payload.get("row_count", 0)),
        "elapsed_sec": float(payload.get("elapsed_sec", wall_sec)),
        "wall_sec": float(wall_sec),
        "matches_cpu_reference": bool(payload.get("matches_cpu_reference", True)),
        "row_count_out": len(payload.get("rows", [])),
        "rows": payload.get("rows", []),
        "contract": metadata.get("contract"),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "native_symbol": metadata.get("native_symbol"),
        "triangle_count": metadata.get("triangle_count"),
        "ray_count": metadata.get("ray_count"),
        "fixture": metadata.get("fixture"),
        "fixture_generation": metadata.get("fixture_generation"),
        "hit_event_count_before_dedup": metadata.get("hit_event_count_before_dedup"),
        "timings": timings,
        "claim_boundary": metadata.get("claim_boundary"),
        "engine_boundary": metadata.get("engine_boundary"),
    }


def _summarize_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    elapsed = [float(sample["elapsed_sec"]) for sample in samples]
    wall = [float(sample["wall_sec"]) for sample in samples]
    first = samples[0]
    return {
        "backend": first["backend"],
        "mode": first["mode"],
        "copies": first["copies"],
        "row_count": first["row_count"],
        "sample_count": len(samples),
        "elapsed_sec_median": float(statistics.median(elapsed)),
        "elapsed_sec_min": float(min(elapsed)),
        "elapsed_sec_max": float(max(elapsed)),
        "wall_sec_median": float(statistics.median(wall)),
        "all_match_cpu_reference": all(bool(sample["matches_cpu_reference"]) for sample in samples),
        "rt_core_accelerated": all(bool(sample["rt_core_accelerated"]) for sample in samples),
        "contract": first["contract"],
        "native_symbol": first["native_symbol"],
        "triangle_count": first["triangle_count"],
        "ray_count": first["ray_count"],
        "hit_event_count_before_dedup": first["hit_event_count_before_dedup"],
        "timings_first_sample": first["timings"],
        "rows_first_sample": first["rows"],
        "claim_boundary": first["claim_boundary"],
    }


def _run_matrix(args: argparse.Namespace) -> dict[str, Any]:
    matrix: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if args.dry_run:
        return {
            "matrix": [],
            "errors": [],
            "dry_run_matrix_shape": {
                "backends": list(args.backends),
                "modes": list(args.modes),
                "copies_ladder": list(args.copies_ladder),
                "repeat": args.repeat,
                "warmup": args.warmup,
            },
        }

    for copies in args.copies_ladder:
        for backend in args.backends:
            if backend == PAPER_RT_CPU_BACKEND and copies > args.paper_cpu_max_copies:
                matrix.append(
                    {
                        "backend": backend,
                        "copies": copies,
                        "status": "skipped",
                        "reason": f"paper RT CPU reference skipped above {args.paper_cpu_max_copies} copies",
                    }
                )
                continue
            for mode in args.modes:
                samples: list[dict[str, Any]] = []
                for iteration in range(args.warmup + args.repeat):
                    print(
                        "running",
                        f"backend={backend}",
                        f"mode={mode}",
                        f"copies={copies}",
                        f"fixture={args.fixture_kind}",
                        f"iteration={iteration + 1}/{args.warmup + args.repeat}",
                        flush=True,
                    )
                    try:
                        sample = _measure_once(backend, mode, copies, args)
                    except Exception as exc:  # noqa: BLE001 - runner must preserve failure in JSON.
                        errors.append(
                            {
                                "backend": backend,
                                "mode": mode,
                                "copies": copies,
                                "iteration": iteration,
                                "error_type": type(exc).__name__,
                                "error": str(exc),
                            }
                        )
                        break
                    if iteration >= args.warmup:
                        samples.append(sample)
                if samples:
                    matrix.append(_summarize_samples(samples))
    return {"matrix": matrix, "errors": errors}


def _speedup_rows(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (row.get("backend"), row.get("mode"), row.get("copies")): row
        for row in matrix
        if row.get("status") != "skipped"
    }
    rows: list[dict[str, Any]] = []
    for key, optix_row in by_key.items():
        backend, mode, copies = key
        if backend != PAPER_RT_BACKEND:
            continue
        embree_row = by_key.get((PAPER_RT_EMBREE_BACKEND, mode, copies))
        cpu_row = by_key.get(("cpu_python_reference", mode, copies))
        paper_cpu_row = by_key.get((PAPER_RT_CPU_BACKEND, mode, copies))
        for label, baseline in (
            ("paper_rt_embree", embree_row),
            ("cpu_python_reference", cpu_row),
            ("paper_rt_cpu_reference", paper_cpu_row),
        ):
            if not baseline:
                continue
            optix_sec = float(optix_row["elapsed_sec_median"])
            baseline_sec = float(baseline["elapsed_sec_median"])
            rows.append(
                {
                    "mode": mode,
                    "copies": copies,
                    "baseline_backend": label,
                    "baseline_elapsed_sec_median": baseline_sec,
                    "paper_rt_optix_elapsed_sec_median": optix_sec,
                    "speedup_baseline_over_paper_rt_optix": baseline_sec / optix_sec if optix_sec > 0 else None,
                    "same_contract_rt_vs_embree": label == "paper_rt_embree",
                    "same_output": bool(optix_row.get("all_match_cpu_reference"))
                    and bool(baseline.get("all_match_cpu_reference")),
                    "rt_core_accelerated": bool(optix_row.get("rt_core_accelerated")),
                }
            )
    return rows


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal2645 RayDB Paper-RT Perf Pod Evidence",
        "",
        "Status: internal evidence only; public speedup wording remains unauthorized pending review.",
        "",
        "## Provenance",
        "",
        f"- timestamp UTC: `{payload['environment']['timestamp_utc']}`",
        f"- host: `{payload['environment']['hostname']}`",
        f"- git commit: `{payload['environment']['git_commit']}`",
        f"- script: `{payload['script']}`",
        f"- output JSON: `{payload['output_json']}`",
        f"- build command: `{payload['environment']['make_build_optix_target']}`",
        f"- Embree build/probe command: `{payload['environment']['make_build_embree_target']}`",
        "",
        "## Contract",
        "",
        "- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.",
        "- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.",
        "- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.",
        "",
        "## Matrix",
        "",
        "| backend | mode | fixture | copies | rows | triangles | rays | median s | RT core | correct |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["results"]["matrix"]:
        if row.get("status") == "skipped":
            lines.append(f"| {row['backend']} | all | - | {row['copies']} | - | - | - | skipped | - | - |")
            continue
        lines.append(
            "| {backend} | {mode} | {fixture} | {copies} | {row_count} | {triangles} | {rays} | {sec:.6f} | {rt} | {ok} |".format(
                backend=row["backend"],
                mode=row["mode"],
                fixture=row.get("fixture", ""),
                copies=row["copies"],
                row_count=row["row_count"],
                triangles=row.get("triangle_count", "-"),
                rays=row.get("ray_count", "-"),
                sec=float(row["elapsed_sec_median"]),
                rt=row.get("rt_core_accelerated"),
                ok=row.get("all_match_cpu_reference"),
            )
        )
    lines.extend(["", "## Speedup Diagnostics", ""])
    if payload["speedup_diagnostics"]:
        lines.extend(
            [
                "| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |",
                "|---|---:|---|---:|---:|---:|---|",
            ]
        )
        for row in payload["speedup_diagnostics"]:
            ratio = row["speedup_baseline_over_paper_rt_optix"]
            lines.append(
                "| {mode} | {copies} | {baseline} | {base:.6f} | {optix:.6f} | {ratio:.3f}x | {ok} |".format(
                    mode=row["mode"],
                    copies=row["copies"],
                    baseline=row["baseline_backend"],
                    base=float(row["baseline_elapsed_sec_median"]),
                    optix=float(row["paper_rt_optix_elapsed_sec_median"]),
                    ratio=float(ratio) if ratio is not None else 0.0,
                    ok=row["same_output"],
                )
            )
    else:
        lines.append("No successful paper RT OptiX comparison rows were produced.")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- performance claim authorized: `{payload['performance_claim_authorized']}`",
            "- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    environment = _environment_snapshot()
    build = _build_backends_if_requested(args)
    results = _run_matrix(args)
    payload = {
        "goal": "Goal2645 RayDB paper-shaped RT-core perf evidence",
        "script": str(Path(__file__).resolve()),
        "output_json": str(args.output_json),
        "output_markdown": str(args.output_markdown),
        "environment": environment,
        "build": build,
        "arguments": {
            "backends": list(args.backends),
            "modes": list(args.modes),
                "copies_ladder": list(args.copies_ladder),
                "fixture_kind": args.fixture_kind,
                "generated_rows": args.generated_rows,
                "generated_groups": args.generated_groups,
                "generated_revenue_mod": args.generated_revenue_mod,
                "repeat": args.repeat,
            "warmup": args.warmup,
            "paper_cpu_max_copies": args.paper_cpu_max_copies,
            "skip_build_optix": args.skip_build_optix,
            "skip_build_embree": args.skip_build_embree,
            "dry_run": args.dry_run,
        },
        "results": results,
        "speedup_diagnostics": _speedup_rows(results["matrix"]),
        "output_contract": {
            "paper_rt_optix": (
                "Rows are grouped aggregate rows over the same RayDB-style fixture. "
                "Correctness is judged by exact equality with the CPU columnar oracle."
            ),
            "paper_rt_embree": (
                "Same RayDB-style rays, triangles, primitive ids, group ids, i64 values, "
                "primitive-id deduplication, and grouped reductions as paper_rt_optix."
            ),
            "rt_core_evidence_required": (
                "paper_rt_optix rows must report rt_core_accelerated=true and native_symbol="
                "rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction."
            ),
        },
        "performance_claim_authorized": False,
    }
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RayDB paper-shaped RT-core perf matrix on a CUDA/OptiX pod.")
    parser.add_argument("--copies-ladder", type=_parse_csv_ints, default=_parse_csv_ints("1,100,1000,10000"))
    parser.add_argument("--fixture-kind", choices=("repeated", "generated"), default="repeated")
    parser.add_argument("--generated-rows", type=int, default=raydb.DEFAULT_GENERATED_ROW_COUNT)
    parser.add_argument("--generated-groups", type=int, default=raydb.DEFAULT_GENERATED_GROUP_COUNT)
    parser.add_argument("--generated-revenue-mod", type=int, default=raydb.DEFAULT_GENERATED_REVENUE_MOD)
    parser.add_argument("--modes", type=_parse_csv_text, default=_parse_csv_text("count,sum,min,max,avg_as_sum_count"))
    parser.add_argument(
        "--backends",
        type=_parse_csv_text,
        default=_parse_csv_text("paper_rt_embree,paper_rt_optix"),
    )
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--paper-cpu-max-copies", type=int, default=100)
    parser.add_argument("--skip-build-optix", action="store_true")
    parser.add_argument("--skip-build-embree", action="store_true")
    parser.add_argument("--build-timeout-sec", type=int, default=600)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    if args.repeat <= 0:
        parser.error("--repeat must be positive")
    if args.warmup < 0:
        parser.error("--warmup must be non-negative")
    if args.generated_rows <= 0:
        parser.error("--generated-rows must be positive")
    if args.generated_groups <= 0:
        parser.error("--generated-groups must be positive")
    if args.generated_revenue_mod <= 0:
        parser.error("--generated-revenue-mod must be positive")
    for mode in args.modes:
        if mode not in raydb.RESULT_MODES:
            parser.error(f"unsupported mode: {mode}")
    for backend in args.backends:
        if backend not in raydb.BACKENDS:
            parser.error(f"unsupported backend: {backend}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, args.output_markdown)
    print(json.dumps({"output_json": str(args.output_json), "errors": payload["results"]["errors"]}, sort_keys=True))
    return 1 if payload["results"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
