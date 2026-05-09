#!/usr/bin/env python3
"""Compare optimized-baseline and threshold-4 gated collect-k on current OptiX.

This is internal v1.6.x performance evidence only. It does not authorize public
speedup wording, true zero-copy wording, stable primitive promotion, broad GPU
claims, or release action.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COUNTS = (65536, 65537, 65538, 65552, 69632, 69633)
DEFAULT_JSON = ROOT / "docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_2026-05-09.json"
DEFAULT_MD = ROOT / "docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_2026-05-09.md"
DEFAULT_PREFIX = ROOT / "docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe"

BASELINE_ENV = {
    "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT": "1",
    "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT": "1",
    "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL": "1",
    "RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE": "1",
    "RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT": "1",
    "RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS": "1",
    "RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS": "1",
    "RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS": "1",
}
GATED_ENV = {
    "RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE": "1",
}
ISOLATION_KEYS = sorted(set(BASELINE_ENV) | set(GATED_ENV) | {
    "RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE",
    "RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC",
    "RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC",
    "RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC",
})


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return "unavailable"
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def _git_head() -> str:
    return _run_text(["git", "rev-parse", "HEAD"])


def _gpu_summary() -> str:
    return _run_text(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])


def _clean_env(extra: dict[str, str], *, ld_library_path: str | None) -> dict[str, str]:
    env = os.environ.copy()
    for key in ISOLATION_KEYS:
        env.pop(key, None)
    env.update(extra)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"src{os.pathsep}." + (f"{os.pathsep}{existing_pythonpath}" if existing_pythonpath else "")
    if ld_library_path:
        env["LD_LIBRARY_PATH"] = ld_library_path
    return env


def _run_probe(
    *,
    label: str,
    env_extra: dict[str, str],
    library: Path,
    counts: tuple[int, ...],
    repeats: int,
    round_index: int,
    prefix: Path,
    ld_library_path: str | None,
) -> Path:
    json_path = prefix.with_name(f"{prefix.name}_{label}_round{round_index}.json")
    md_path = prefix.with_name(f"{prefix.name}_{label}_round{round_index}.md")
    jsonl_path = prefix.with_name(f"{prefix.name}_{label}_round{round_index}.jsonl")
    command = [
        sys.executable,
        "scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py",
        "--library",
        str(library),
        "--counts",
        *[str(count) for count in counts],
        "--repeats",
        str(repeats),
        "--profile-jsonl",
        str(jsonl_path),
        "--json-out",
        str(json_path),
        "--md-out",
        str(md_path),
    ]
    subprocess.run(
        command,
        cwd=ROOT,
        env=_clean_env(env_extra, ld_library_path=ld_library_path),
        check=True,
    )
    return json_path


def _load_cases(path: Path) -> dict[int, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("accepted_goal1506_evidence") is not True:
        raise ValueError(f"probe artifact was not accepted Goal1506 evidence: {path}")
    return {int(case["candidate_count"]): case for case in payload["cases"]}


def _case_total_ms(case: dict[str, Any]) -> float:
    return float(case["stage_profile"]["stage_median_ms"]["total_ms"])


def _case_payload_copies(case: dict[str, Any]) -> int:
    return int(case["stage_profile"]["topology"]["carry_payload_copies"])


def _case_parity(case: dict[str, Any]) -> bool:
    return bool(case["same_candidate_rows"])


def summarize_rounds(rounds: list[dict[str, Path]], counts: tuple[int, ...]) -> list[dict[str, Any]]:
    per_count: dict[int, list[dict[str, Any]]] = {count: [] for count in counts}
    for round_index, paths in enumerate(rounds, start=1):
        baseline = _load_cases(paths["baseline"])
        gated = _load_cases(paths["gated"])
        for count in counts:
            base_case = baseline[count]
            gated_case = gated[count]
            base_ms = _case_total_ms(base_case)
            gated_ms = _case_total_ms(gated_case)
            per_count[count].append(
                {
                    "round": round_index,
                    "baseline_total_ms": base_ms,
                    "gated_total_ms": gated_ms,
                    "delta_ms": gated_ms - base_ms,
                    "baseline_payload_copies": _case_payload_copies(base_case),
                    "gated_payload_copies": _case_payload_copies(gated_case),
                    "baseline_parity": _case_parity(base_case),
                    "gated_parity": _case_parity(gated_case),
                }
            )

    rows: list[dict[str, Any]] = []
    for count, records in per_count.items():
        deltas = [float(record["delta_ms"]) for record in records]
        rows.append(
            {
                "candidate_count": count,
                "rounds": records,
                "avg_delta_ms": statistics.fmean(deltas) if deltas else 0.0,
                "median_delta_ms": statistics.median(deltas) if deltas else 0.0,
                "faster_rounds": sum(1 for delta in deltas if delta < 0.0),
                "round_count": len(records),
                "baseline_payload_copies": records[-1]["baseline_payload_copies"] if records else 0,
                "gated_payload_copies": records[-1]["gated_payload_copies"] if records else 0,
                "all_parity": all(record["baseline_parity"] and record["gated_parity"] for record in records),
            }
        )
    return rows


def _write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Goal1625 v1.6.5 OptiX Collect-K Threshold-4 A4500 Probe",
        "",
        "## Verdict",
        "",
        "`internal_threshold4_a4500_probe_recorded`",
        "",
        "## Scope",
        "",
        f"- Git commit: `{report['git_commit']}`",
        f"- GPU summary: `{report['gpu_summary']}`",
        f"- Counts: `{report['counts']}`",
        f"- Rounds: `{report['round_count']}`",
        f"- Repeats per probe: `{report['repeats']}`",
        "",
        "## Results",
        "",
        "| Count | Avg delta ms | Median delta ms | Faster rounds | Payload copies baseline/gated | Parity |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {candidate_count} | {avg_delta_ms:.6f} | {median_delta_ms:.6f} | {faster_rounds}/{round_count} | "
            "{baseline_payload_copies}/{gated_payload_copies} | {all_parity} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            report["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    counts = tuple(args.counts)
    rounds: list[dict[str, Path]] = []
    for round_index in range(1, args.rounds + 1):
        baseline_path = _run_probe(
            label="baseline",
            env_extra=BASELINE_ENV,
            library=args.library,
            counts=counts,
            repeats=args.repeats,
            round_index=round_index,
            prefix=args.artifact_prefix,
            ld_library_path=args.ld_library_path,
        )
        gated_path = _run_probe(
            label="gated",
            env_extra=GATED_ENV,
            library=args.library,
            counts=counts,
            repeats=args.repeats,
            round_index=round_index,
            prefix=args.artifact_prefix,
            ld_library_path=args.ld_library_path,
        )
        rounds.append({"baseline": baseline_path, "gated": gated_path})

    report = {
        "goal": "Goal1625",
        "status": "internal_threshold4_a4500_probe_recorded",
        "git_commit": _git_head(),
        "gpu_summary": _gpu_summary(),
        "counts": list(counts),
        "round_count": args.rounds,
        "repeats": args.repeats,
        "baseline_env": BASELINE_ENV,
        "gated_env": GATED_ENV,
        "artifact_prefix": str(args.artifact_prefix),
        "round_artifacts": [
            {"baseline": str(item["baseline"]), "gated": str(item["gated"])}
            for item in rounds
        ],
        "rows": summarize_rounds(rounds, counts),
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "true_zero_copy_wording_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "broad_rtx_gpu_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1625 is internal same-host OptiX collect-k threshold-4 diagnostic evidence only. "
            "It does not authorize public speedup wording, true zero-copy wording, stable "
            "COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, whole-app speedup claims, "
            "release tags, or release action."
        ),
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(_write_markdown(report), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT / "build/librtdl_optix.so")
    parser.add_argument("--counts", nargs="+", type=int, default=list(DEFAULT_COUNTS))
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=31)
    parser.add_argument("--artifact-prefix", type=Path, default=DEFAULT_PREFIX)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--ld-library-path", default=os.environ.get("LD_LIBRARY_PATH"))
    return parser.parse_args()


def main() -> int:
    report = run(parse_args())
    print(json.dumps({"status": report["status"], "rows": report["rows"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
