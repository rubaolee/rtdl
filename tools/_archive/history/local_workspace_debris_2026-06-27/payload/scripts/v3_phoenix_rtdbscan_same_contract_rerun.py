#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
DEFAULT_ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtdbscan_same_contract_20260620"
)

STATUS = "rtdbscan_same_contract_fresh_evidence_not_promoted"
VERSION = "rtdl.v3.phoenix.rtdbscan.same_contract_rerun.v1"

EMBREE_MODE = "embree_core_flags_numba_prepared_grid_column_signature_3d"
OPTIX_MODE = "optix_rt_core_flags_numba_prepared_grid_column_signature_3d"


def default_protocols(point_counts: tuple[int, ...]) -> tuple[dict[str, Any], ...]:
    protocols: list[dict[str, Any]] = [
        {
            "point_count": 4096,
            "repeat": 3,
            "warmup": 1,
            "validation": True,
            "purpose": "small validated control for both same-contract app modes",
        }
    ]
    for point_count in point_counts:
        if point_count == 4096:
            continue
        repeat = 5 if point_count <= 131_072 else 3
        protocols.append(
            {
                "point_count": int(point_count),
                "repeat": repeat,
                "warmup": 1,
                "validation": False,
                "purpose": "serious same-contract component-signature timing row",
            }
        )
    return tuple(protocols)


def build_cases(
    *,
    dataset: str,
    point_counts: tuple[int, ...],
    seed: int,
) -> tuple[dict[str, Any], ...]:
    cases: list[dict[str, Any]] = []
    for protocol in default_protocols(point_counts):
        point_count = int(protocol["point_count"])
        repeat = int(protocol["repeat"])
        warmup = int(protocol["warmup"])
        for backend, mode in (("embree", EMBREE_MODE), ("optix", OPTIX_MODE)):
            case_id = f"rtdbscan_{backend}_same_contract_{dataset}_{point_count}_r{repeat}"
            command = [
                sys.executable,
                str(APP),
                "--mode",
                mode,
                "--dataset",
                dataset,
                "--point-count",
                str(point_count),
                "--seed",
                str(seed),
                "--partner",
                "numba",
                "--repeat",
                str(repeat),
                "--warmup",
                str(warmup),
            ]
            if not bool(protocol["validation"]):
                command.append("--no-validation")
            cases.append(
                {
                    "case_id": case_id,
                    "backend": backend,
                    "mode": mode,
                    "dataset": dataset,
                    "point_count": point_count,
                    "repeat": repeat,
                    "warmup": warmup,
                    "validation_requested": bool(protocol["validation"]),
                    "purpose": protocol["purpose"],
                    "command": command,
                }
            )
    return tuple(cases)


def canonical_component_signature(signature: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(signature, dict):
        return None
    cluster_sizes = signature.get("cluster_sizes")
    if not isinstance(cluster_sizes, dict):
        return None
    return {
        "cluster_sizes": tuple(sorted(int(value) for value in cluster_sizes.values() if int(value) > 0)),
        "core_count": int(signature.get("core_count", -1)),
        "noise_count": int(signature.get("noise_count", -1)),
    }


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
    except Exception as exc:  # pragma: no cover - platform probe best effort
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


def run_case(case: dict[str, Any], artifact_dir: Path, *, timeout_sec: int, dry_run: bool) -> dict[str, Any]:
    case_id = str(case["case_id"])
    stdout_path = artifact_dir / f"{case_id}.stdout.json"
    stderr_path = artifact_dir / f"{case_id}.stderr.txt"
    command = [str(part) for part in case["command"]]
    row: dict[str, Any] = {
        **case,
        "command": command,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }
    if dry_run:
        return {**row, "status": "dry_run"}

    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_sec,
    )
    wrapper_elapsed_sec = time.perf_counter() - started
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    parsed: dict[str, Any] | None = None
    parse_error = None
    try:
        loaded = json.loads(completed.stdout)
        if isinstance(loaded, dict):
            parsed = loaded
        else:
            parse_error = "stdout JSON is not an object"
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    metadata = dict(parsed.get("metadata", {})) if parsed else {}
    protocol = dict(metadata.get("prepared_query_repeat_protocol", {}))
    timing = dict(metadata.get("timing_breakdown_sec", {}))
    signature = parsed.get("signature") if parsed else None
    status = "ok" if completed.returncode == 0 and parsed is not None else "failed"
    return {
        **row,
        "status": status,
        "returncode": completed.returncode,
        "wrapper_elapsed_sec": wrapper_elapsed_sec,
        "stdout_json_parse_error": parse_error,
        "app_elapsed_sec": parsed.get("elapsed_sec") if parsed else None,
        "matches_reference": parsed.get("matches_reference") if parsed else None,
        "reference_signature_present": bool(parsed.get("reference_signature")) if parsed else False,
        "signature": signature,
        "canonical_signature": canonical_component_signature(signature),
        "metadata_path": metadata.get("path"),
        "native_execution_path": metadata.get("native_execution_path"),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "embree_backend_used": bool(metadata.get("embree_backend_used", False)),
        "optix_backend_used": bool(metadata.get("optix_backend_used", False)),
        "materializes_python_rows": metadata.get("materializes_python_rows"),
        "prepared_query_repeat_protocol": protocol,
        "timing_extract": {
            "embree_threshold_compact_rows_sec": metadata.get("embree_threshold_compact_rows_sec"),
            "embree_native_traversal_sec": metadata.get("embree_native_traversal_sec"),
            "embree_threshold_columns_upload_sec": metadata.get("embree_threshold_columns_upload_sec"),
            "optix_rt_count_threshold_sec": metadata.get("optix_rt_count_threshold_sec"),
            "numba_component_continuation_sec": metadata.get("numba_component_continuation_sec"),
            "prepare_sec": protocol.get("prepare_sec"),
            "elapsed_sec_total": protocol.get("elapsed_sec_total"),
            "timing_breakdown_sec": timing,
        },
    }


def _ratio(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if float(denominator) <= 0.0:
        return None
    return float(numerator) / float(denominator)


def build_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, int, int], dict[str, dict[str, Any]]] = {}
    for row in rows:
        if row.get("status") not in {"ok", "dry_run"}:
            continue
        key = (
            str(row["dataset"]),
            int(row["point_count"]),
            int(row["repeat"]),
            int(row["warmup"]),
        )
        grouped.setdefault(key, {})[str(row["backend"])] = row

    pairs: list[dict[str, Any]] = []
    for (dataset, point_count, repeat, warmup), by_backend in sorted(grouped.items()):
        embree = by_backend.get("embree")
        optix = by_backend.get("optix")
        if not embree or not optix:
            continue
        embree_sig = embree.get("canonical_signature")
        optix_sig = optix.get("canonical_signature")
        embree_sec = embree.get("app_elapsed_sec")
        optix_sec = optix.get("app_elapsed_sec")
        embree_timing = dict(embree.get("timing_extract") or {})
        optix_timing = dict(optix.get("timing_extract") or {})
        pairs.append(
            {
                "dataset": dataset,
                "point_count": point_count,
                "repeat": repeat,
                "warmup": warmup,
                "validation_control": bool(embree.get("validation_requested") and optix.get("validation_requested")),
                "embree_case_id": embree["case_id"],
                "optix_case_id": optix["case_id"],
                "same_canonical_component_signature": embree_sig == optix_sig and embree_sig is not None,
                "embree_matches_reference": embree.get("matches_reference"),
                "optix_matches_reference": optix.get("matches_reference"),
                "embree_sec": embree_sec,
                "optix_sec": optix_sec,
                "optix_speedup_vs_embree": _ratio(embree_sec, optix_sec),
                "embree_threshold_compact_rows_sec": embree_timing.get("embree_threshold_compact_rows_sec"),
                "embree_native_traversal_sec": embree_timing.get("embree_native_traversal_sec"),
                "optix_rt_count_threshold_sec": optix_timing.get("optix_rt_count_threshold_sec"),
                "rt_threshold_speedup_vs_embree_compact_rows": _ratio(
                    embree_timing.get("embree_threshold_compact_rows_sec"),
                    optix_timing.get("optix_rt_count_threshold_sec"),
                ),
                "embree_numba_component_continuation_sec": embree_timing.get("numba_component_continuation_sec"),
                "optix_numba_component_continuation_sec": optix_timing.get("numba_component_continuation_sec"),
                "continuation_dominates_optix": (
                    isinstance(optix_timing.get("numba_component_continuation_sec"), (int, float))
                    and isinstance(optix_timing.get("optix_rt_count_threshold_sec"), (int, float))
                    and float(optix_timing["numba_component_continuation_sec"])
                    > float(optix_timing["optix_rt_count_threshold_sec"])
                ),
                "canonical_signature": embree_sig,
                "public_speedup_claim_authorized": False,
                "m7_promotion_authorized": False,
            }
        )
    return pairs


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload["rows"]
    pairs = payload["pairs"]
    failed_rows = [row["case_id"] for row in rows if row["status"] not in {"ok", "dry_run"}]
    serious_pairs = [pair for pair in pairs if int(pair["point_count"]) >= 65_536]
    large_pairs = [pair for pair in pairs if int(pair["point_count"]) >= 524_288]
    validation_pairs = [pair for pair in pairs if pair["validation_control"]]
    large_signature_pass = bool(large_pairs) and all(pair["same_canonical_component_signature"] for pair in large_pairs)
    validation_reference_pass = bool(validation_pairs) and all(
        pair["embree_matches_reference"] is True and pair["optix_matches_reference"] is True for pair in validation_pairs
    )
    speedups = [
        float(pair["optix_speedup_vs_embree"])
        for pair in serious_pairs
        if isinstance(pair.get("optix_speedup_vs_embree"), (int, float))
    ]
    strongest_speedup = max(speedups) if speedups else None
    weakest_speedup = min(speedups) if speedups else None
    return {
        "status": STATUS,
        "row_count": len(rows),
        "pair_count": len(pairs),
        "failed_rows": failed_rows,
        "validation_reference_pass": validation_reference_pass,
        "large_signature_pass": large_signature_pass,
        "serious_pair_count": len(serious_pairs),
        "large_pair_count": len(large_pairs),
        "strongest_serious_optix_speedup_vs_embree": strongest_speedup,
        "weakest_serious_optix_speedup_vs_embree": weakest_speedup,
        "m7_candidate_interpretation": (
            "same-contract RTDBSCAN evidence can be reviewed as a row-scoped candidate only if "
            "validation control passes, large signatures match, and external review accepts the "
            "component-signature boundary"
        ),
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def _fmt(value: Any, *, suffix: str = "") -> str:
    if not isinstance(value, (int, float)):
        return ""
    return f"{float(value):.6g}{suffix}"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Phoenix V3 RTDBSCAN Same-Contract Rerun Evidence",
        "",
        f"status: {payload['status']}",
        "",
        "This packet compares Embree and OptiX on the same RTDBSCAN component-signature",
        "contract: fixed-radius count-threshold rows/columns feeding the same Numba prepared",
        "grid component-signature continuation. It is a fresh evidence packet, not release",
        "authorization.",
        "",
        "## Claim Boundary",
        "",
        "- Not full DBSCAN paper reproduction.",
        "- Not full DBSCAN label publication.",
        "- Not broad V3 speedup wording.",
        "- Not M7 promotion until external review and Codex consensus.",
        "- Component-signature equality is the large-row validation contract; the small control row also checks CPU reference parity.",
        "",
        "## Summary",
        "",
        f"- Validation control reference pass: `{summary['validation_reference_pass']}`",
        f"- Large same-signature pass: `{summary['large_signature_pass']}`",
        f"- Serious pairs: `{summary['serious_pair_count']}`",
        f"- Large pairs: `{summary['large_pair_count']}`",
        f"- Strongest serious OptiX/Embree speedup: `{summary['strongest_serious_optix_speedup_vs_embree']}`",
        f"- Weakest serious OptiX/Embree speedup: `{summary['weakest_serious_optix_speedup_vs_embree']}`",
        "",
        "## Pairs",
        "",
        "| Point count | Repeat | Embree sec | OptiX sec | OptiX speedup | RT-threshold speedup | Same signature | Continuation dominates OptiX |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for pair in payload["pairs"]:
        lines.append(
            "| {point_count} | {repeat} | {embree} | {optix} | {speedup} | {threshold} | `{same}` | `{dominates}` |".format(
                point_count=pair["point_count"],
                repeat=pair["repeat"],
                embree=_fmt(pair.get("embree_sec")),
                optix=_fmt(pair.get("optix_sec")),
                speedup=_fmt(pair.get("optix_speedup_vs_embree"), suffix="x"),
                threshold=_fmt(pair.get("rt_threshold_speedup_vs_embree_compact_rows"), suffix="x"),
                same=pair.get("same_canonical_component_signature"),
                dominates=pair.get("continuation_dominates_optix"),
            )
        )
    lines.extend(
        [
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            "1. Was I foolish? No: this packet replaces a misleading row-materialization comparison with a same-contract rerun.",
            "2. If yes, what actions made the decision foolish? Not applicable for this decision; the known foolish action would be treating the old 1483x row as public proof.",
            "3. Was there another path? Yes: promote only the old grouped-stream M23 hot label result, but that would still lack a fair Embree baseline.",
            "4. Can I now try a different path? Yes: use this same-contract packet to decide whether RTDBSCAN is a modest row-scoped candidate, an internal-only route, or needs further engine work.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "summary.md").write_text(render_markdown(payload) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Phoenix V3 RTDBSCAN same-contract Embree/OptiX evidence.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--dataset", default="clustered3d", choices=("clustered3d", "road3d", "ngsim_dense"))
    parser.add_argument("--point-count", type=int, action="append", default=[65_536, 262_144, 524_288])
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--timeout-sec", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    point_counts = tuple(sorted(set(int(value) for value in args.point_count)))
    cases = build_cases(dataset=args.dataset, point_counts=point_counts, seed=args.seed)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, case in enumerate(cases, start=1):
        print(f"[rtdbscan-same-contract] {index}/{len(cases)} {case['case_id']}", flush=True)
        rows.append(run_case(case, args.artifact_dir, timeout_sec=args.timeout_sec, dry_run=args.dry_run))

    payload: dict[str, Any] = {
        "version": VERSION,
        "status": STATUS,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact_dir": str(args.artifact_dir),
        "dataset": args.dataset,
        "point_counts": list(point_counts),
        "environment": environment_probe() if not args.dry_run else {"repo_root": str(ROOT)},
        "rows": rows,
        "pairs": build_pairs(rows),
        "claim_boundary": {
            "m7_promotion_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }
    payload["summary"] = summarize(payload)
    write_outputs(payload, args.artifact_dir)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.artifact_dir / 'summary.json'}")
    return 0 if not payload["summary"]["failed_rows"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
