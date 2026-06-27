#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)
DEFAULT_ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_hausdorff_threshold_summary_large_stability_20260621"
)

STATUS = "hausdorff_threshold_summary_large_stability_evidence_not_promoted"
VERSION = "rtdl.v3.phoenix.hausdorff.threshold_summary.large_stability.v1"


def _run_text(command: list[str], timeout_sec: int = 10) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_sec,
        )
    except Exception as exc:  # pragma: no cover
        return f"unavailable: {exc}"
    return (completed.stdout or completed.stderr).strip()


def environment_probe() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "nvidia_smi": _run_text(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ]
        ),
        "repo_root": str(ROOT),
    }


def build_command(*, backend: str, copies: int, threshold: float, repeat: int, warmup: int) -> list[str]:
    command = [
        sys.executable,
        str(APP),
        "--backend",
        backend,
        "--optix-summary-mode",
        "directed_threshold_prepared",
        "--hausdorff-threshold",
        str(threshold),
        "--copies",
        str(copies),
        "--repeat",
        str(repeat),
        "--warmup",
        str(warmup),
    ]
    if backend == "optix":
        command.append("--require-rt-core")
    return command


def _phase_total(phases: dict[str, Any]) -> float | None:
    total = 0.0
    found = False
    for key in (
        "input_construction_sec",
        "scene_prepare_sec",
        "query_fixed_radius_threshold_reached_count_sec",
        "python_postprocess_sec",
        "validation_sec",
    ):
        value = phases.get(key)
        if isinstance(value, (int, float)):
            total += float(value)
            found = True
    return total if found else None


def _ratio(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if float(denominator) <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _stddev(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return float(statistics.stdev(values))


def _stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "stddev": None,
            "relative_stddev": None,
        }
    mean = float(statistics.mean(values))
    stddev = _stddev(values)
    return {
        "count": len(values),
        "mean": mean,
        "median": float(statistics.median(values)),
        "min": float(min(values)),
        "max": float(max(values)),
        "stddev": stddev,
        "relative_stddev": (float(stddev) / mean if stddev is not None and mean > 0.0 else None),
    }


def run_case(
    *,
    run_index: int,
    backend: str,
    copies: int,
    threshold: float,
    repeat: int,
    warmup: int,
    artifact_dir: Path,
    timeout_sec: int,
    heartbeat_sec: float,
    dry_run: bool,
) -> dict[str, Any]:
    case_id = f"hausdorff_threshold_summary_{backend}_c{copies}_r{repeat}_w{warmup}_sample{run_index:02d}"
    command = build_command(
        backend=backend,
        copies=copies,
        threshold=threshold,
        repeat=repeat,
        warmup=warmup,
    )
    stdout_path = artifact_dir / f"{case_id}.stdout.json"
    stderr_path = artifact_dir / f"{case_id}.stderr.txt"
    row: dict[str, Any] = {
        "case_id": case_id,
        "run_index": run_index,
        "backend": backend,
        "copies": copies,
        "threshold": threshold,
        "repeat": repeat,
        "warmup": warmup,
        "command": command,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "full_hausdorff_witness_claim_authorized": False,
    }
    if dry_run:
        return {**row, "status": "dry_run"}

    print(f"[hausdorff-threshold-stability] start {case_id}", flush=True)
    started = time.perf_counter()
    process = subprocess.Popen(
        [str(part) for part in command],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    deadline = started + float(timeout_sec)
    next_heartbeat = started + float(heartbeat_sec)
    timed_out = False
    while process.poll() is None:
        now = time.perf_counter()
        if now >= deadline:
            timed_out = True
            process.kill()
            break
        if now >= next_heartbeat:
            elapsed = now - started
            print(f"[hausdorff-threshold-stability] heartbeat {case_id} elapsed={elapsed:.1f}s", flush=True)
            next_heartbeat = now + float(heartbeat_sec)
        time.sleep(0.2)
    stdout, stderr = process.communicate()
    wrapper_elapsed_sec = time.perf_counter() - started
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")

    parsed: dict[str, Any] | None = None
    parse_error = None
    try:
        loaded = json.loads(stdout or "")
        if isinstance(loaded, dict):
            parsed = loaded
        else:
            parse_error = "stdout JSON is not an object"
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    phases = dict(parsed.get("run_phases", {})) if parsed else {}
    repeat_protocol = dict(parsed.get("repeat_protocol", {})) if parsed else {}
    return {
        **row,
        "status": "ok" if process.returncode == 0 and parsed is not None and not timed_out else "failed",
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout_json_parse_error": parse_error,
        "wrapper_elapsed_sec": wrapper_elapsed_sec,
        "point_count_a": parsed.get("point_count_a") if parsed else None,
        "point_count_b": parsed.get("point_count_b") if parsed else None,
        "within_threshold": parsed.get("within_threshold") if parsed else None,
        "matches_oracle": parsed.get("matches_oracle") if parsed else None,
        "oracle_decision_matches": parsed.get("oracle_decision_matches") if parsed else None,
        "oracle_identity_matches": parsed.get("oracle_identity_matches") if parsed else None,
        "oracle_within_threshold": parsed.get("oracle_within_threshold") if parsed else None,
        "oracle": parsed.get("oracle") if parsed else None,
        "rt_core_accelerated": parsed.get("rt_core_accelerated") if parsed else None,
        "native_continuation_active": parsed.get("native_continuation_active") if parsed else None,
        "native_continuation_backend": parsed.get("native_continuation_backend") if parsed else None,
        "repeat_protocol": repeat_protocol,
        "run_phases": phases,
        "query_sec": phases.get("query_fixed_radius_threshold_reached_count_sec"),
        "query_total_sec": repeat_protocol.get("measured_query_total_sec"),
        "scene_prepare_sec": phases.get("scene_prepare_sec"),
        "phase_total_sec": _phase_total(phases),
    }


def build_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for run_index in sorted({int(row["run_index"]) for row in rows if row.get("status") in {"ok", "dry_run"}}):
        embree = next((row for row in rows if row.get("run_index") == run_index and row.get("backend") == "embree"), None)
        optix = next((row for row in rows if row.get("run_index") == run_index and row.get("backend") == "optix"), None)
        if not embree or not optix:
            continue
        pairs.append(
            {
                "run_index": run_index,
                "copies": embree.get("copies"),
                "point_count_a": embree.get("point_count_a"),
                "point_count_b": embree.get("point_count_b"),
                "threshold": embree.get("threshold"),
                "repeat": embree.get("repeat"),
                "warmup": embree.get("warmup"),
                "same_decision": embree.get("within_threshold") == optix.get("within_threshold"),
                "same_oracle_decision": embree.get("oracle_within_threshold") == optix.get("oracle_within_threshold"),
                "both_match_oracle": embree.get("matches_oracle") is True and optix.get("matches_oracle") is True,
                "embree_query_sec": embree.get("query_sec"),
                "optix_query_sec": optix.get("query_sec"),
                "query_optix_over_embree": _ratio(embree.get("query_sec"), optix.get("query_sec")),
                "embree_phase_total_sec": embree.get("phase_total_sec"),
                "optix_phase_total_sec": optix.get("phase_total_sec"),
                "phase_total_optix_over_embree": _ratio(embree.get("phase_total_sec"), optix.get("phase_total_sec")),
                "embree_wrapper_elapsed_sec": embree.get("wrapper_elapsed_sec"),
                "optix_wrapper_elapsed_sec": optix.get("wrapper_elapsed_sec"),
                "wrapper_optix_over_embree": _ratio(
                    embree.get("wrapper_elapsed_sec"), optix.get("wrapper_elapsed_sec")
                ),
            }
        )
    return pairs


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload["rows"]
    pairs = payload["pairs"]
    failed_rows = [row["case_id"] for row in rows if row.get("status") not in {"ok", "dry_run"}]
    backend_stats: dict[str, Any] = {}
    for backend in ("embree", "optix"):
        backend_rows = [row for row in rows if row.get("backend") == backend and row.get("status") == "ok"]
        backend_stats[backend] = {
            "query_sec": _stat([float(row["query_sec"]) for row in backend_rows if isinstance(row.get("query_sec"), (int, float))]),
            "phase_total_sec": _stat(
                [float(row["phase_total_sec"]) for row in backend_rows if isinstance(row.get("phase_total_sec"), (int, float))]
            ),
            "wrapper_elapsed_sec": _stat(
                [float(row["wrapper_elapsed_sec"]) for row in backend_rows if isinstance(row.get("wrapper_elapsed_sec"), (int, float))]
            ),
        }
    ratio_stats = {
        "query_optix_over_embree": _stat(
            [float(pair["query_optix_over_embree"]) for pair in pairs if isinstance(pair.get("query_optix_over_embree"), (int, float))]
        ),
        "phase_total_optix_over_embree": _stat(
            [
                float(pair["phase_total_optix_over_embree"])
                for pair in pairs
                if isinstance(pair.get("phase_total_optix_over_embree"), (int, float))
            ]
        ),
        "wrapper_optix_over_embree": _stat(
            [
                float(pair["wrapper_optix_over_embree"])
                for pair in pairs
                if isinstance(pair.get("wrapper_optix_over_embree"), (int, float))
            ]
        ),
    }
    phase_ratios = [
        float(pair["phase_total_optix_over_embree"])
        for pair in pairs
        if isinstance(pair.get("phase_total_optix_over_embree"), (int, float))
    ]
    return {
        "status": STATUS,
        "row_count": len(rows),
        "pair_count": len(pairs),
        "failed_rows": failed_rows,
        "all_pairs_match_oracle": bool(pairs) and all(pair["both_match_oracle"] for pair in pairs),
        "all_pairs_same_decision": bool(pairs) and all(pair["same_decision"] for pair in pairs),
        "all_phase_total_pairs_above_1x": bool(phase_ratios) and all(value > 1.0 for value in phase_ratios),
        "weakest_phase_total_optix_speedup_vs_embree": min(phase_ratios) if phase_ratios else None,
        "backend_stats": backend_stats,
        "ratio_stats": ratio_stats,
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "full_hausdorff_witness_claim_authorized": False,
    }


def _fmt(value: Any, *, suffix: str = "") -> str:
    if not isinstance(value, (int, float)):
        return ""
    return f"{float(value):.6g}{suffix}"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    ratio_stats = summary["ratio_stats"]
    lines = [
        "# Phoenix V3 Hausdorff Threshold-Summary Large-Row Stability Evidence",
        "",
        f"status: {payload['status']}",
        "",
        "This artifact repeats the largest Hausdorff threshold-summary candidate",
        "as independent process runs. It repairs the external-review request for",
        "stability data; it does not authorize promotion by itself.",
        "",
        "## Scope",
        "",
        f"- Copies: `{payload['copies']}`",
        f"- Points per side: `{payload['point_count_per_side']}`",
        f"- Threshold: `{payload['threshold']}`",
        f"- Independent paired samples: `{payload['independent_runs']}`",
        f"- Inner repeat/warmup per sample: `{payload['repeat']}` / `{payload['warmup']}`",
        "",
        "## Summary",
        "",
        f"- All pairs match oracle: `{summary['all_pairs_match_oracle']}`",
        f"- All pairs same decision: `{summary['all_pairs_same_decision']}`",
        f"- All phase-total pairs above 1x: `{summary['all_phase_total_pairs_above_1x']}`",
        f"- Weakest phase-total OptiX/Embree speedup: `{summary['weakest_phase_total_optix_speedup_vs_embree']}`",
        f"- Phase-total ratio mean/stddev: `{ratio_stats['phase_total_optix_over_embree']['mean']}` / `{ratio_stats['phase_total_optix_over_embree']['stddev']}`",
        f"- Query ratio mean/stddev: `{ratio_stats['query_optix_over_embree']['mean']}` / `{ratio_stats['query_optix_over_embree']['stddev']}`",
        f"- Wrapper ratio mean/stddev: `{ratio_stats['wrapper_optix_over_embree']['mean']}` / `{ratio_stats['wrapper_optix_over_embree']['stddev']}`",
        "",
        "## Paired Samples",
        "",
        "| Sample | Embree query | OptiX query | Query speedup | Embree phase total | OptiX phase total | Phase speedup | Wrapper speedup | Oracle |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for pair in payload["pairs"]:
        lines.append(
            "| {sample} | {embree_q} | {optix_q} | {query} | {embree_total} | {optix_total} | {phase} | {wrapper} | `{oracle}` |".format(
                sample=pair["run_index"],
                embree_q=_fmt(pair.get("embree_query_sec")),
                optix_q=_fmt(pair.get("optix_query_sec")),
                query=_fmt(pair.get("query_optix_over_embree"), suffix="x"),
                embree_total=_fmt(pair.get("embree_phase_total_sec")),
                optix_total=_fmt(pair.get("optix_phase_total_sec")),
                phase=_fmt(pair.get("phase_total_optix_over_embree"), suffix="x"),
                wrapper=_fmt(pair.get("wrapper_optix_over_embree"), suffix="x"),
                oracle=pair.get("both_match_oracle"),
            )
        )
    lines.extend(
        [
            "",
            "## Oracle Definition",
            "",
            payload["oracle_definition"],
            "",
            "## Claim Boundary",
            "",
            "- Not full exact Hausdorff distance or witness materialization.",
            "- Not X-HD paper reproduction.",
            "- Not broad V3-over-V2 wording.",
            "- Not all threshold values.",
            "- Not all sizes.",
            "- Not M7 until the evidence packet, external review, and Codex consensus are updated.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "summary.md").write_text(render_markdown(payload) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Hausdorff threshold_summary large-row stability evidence.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--copies", type=int, default=262_144)
    parser.add_argument("--threshold", type=float, default=0.4)
    parser.add_argument("--independent-runs", type=int, default=5)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=3600)
    parser.add_argument("--heartbeat-sec", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    total_cases = int(args.independent_runs) * 2
    case_number = 0
    for run_index in range(1, int(args.independent_runs) + 1):
        for backend in ("embree", "optix"):
            case_number += 1
            print(
                f"[hausdorff-threshold-stability] case {case_number}/{total_cases} "
                f"sample={run_index} backend={backend}",
                flush=True,
            )
            rows.append(
                run_case(
                    run_index=run_index,
                    backend=backend,
                    copies=int(args.copies),
                    threshold=float(args.threshold),
                    repeat=int(args.repeat),
                    warmup=int(args.warmup),
                    artifact_dir=args.artifact_dir,
                    timeout_sec=int(args.timeout_sec),
                    heartbeat_sec=float(args.heartbeat_sec),
                    dry_run=bool(args.dry_run),
                )
            )

    pairs = build_pairs(rows)
    point_count = None
    for row in rows:
        if isinstance(row.get("point_count_a"), int):
            point_count = row["point_count_a"]
            break
    payload: dict[str, Any] = {
        "version": VERSION,
        "status": STATUS,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact_dir": str(args.artifact_dir),
        "copies": int(args.copies),
        "point_count_per_side": point_count,
        "threshold": float(args.threshold),
        "independent_runs": int(args.independent_runs),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "environment": environment_probe() if not args.dry_run else {"repo_root": str(ROOT)},
        "oracle_definition": (
            "The oracle is expected_tiled_hausdorff(copies=N): the app computes the exact "
            "Hausdorff summary on the four-point authored base fixture using brute force, "
            "then scales deterministic row-count metadata by N because the benchmark input "
            "is a tiled repetition of that fixture. The threshold-summary route checks both "
            "directed fixed-radius decisions against oracle_within_threshold = "
            "oracle['hausdorff_distance'] <= threshold."
        ),
        "rows": rows,
        "pairs": pairs,
        "claim_boundary": {
            "m7_promotion_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "full_hausdorff_witness_claim_authorized": False,
        },
    }
    payload["summary"] = summarize(payload)
    write_outputs(payload, args.artifact_dir)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    print(f"wrote {args.artifact_dir / 'summary.json'}", flush=True)
    return 0 if not payload["summary"]["failed_rows"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
