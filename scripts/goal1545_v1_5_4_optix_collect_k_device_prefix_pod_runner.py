#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py"
DEFAULT_LIBRARY_PATH = ROOT / "build" / "librtdl_optix.so"
DEFAULT_REPORT_DIR = ROOT / "docs" / "reports"
DEFAULT_COUNTS = (4097, 65537, 131072)
REPORT_STEM = "goal1545_v1_5_4_optix_collect_k_device_prefix_compact_pod_runner_2026-05-08"


CONTROL_ENV = {
    "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT": "1",
    "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT": "1",
    "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL": "1",
    "RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE": "1",
}

CANDIDATE_ENV = {
    **CONTROL_ENV,
    "RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT": "1",
}


def _run_probe(
    *,
    label: str,
    env_flags: dict[str, str],
    library_path: Path,
    report_dir: Path,
    counts: tuple[int, ...],
    repeats: int,
) -> Path:
    json_path = report_dir / f"{REPORT_STEM}_{label}.json"
    md_path = report_dir / f"{REPORT_STEM}_{label}.md"
    jsonl_path = report_dir / f"{REPORT_STEM}_{label}.jsonl"
    env = os.environ.copy()
    env.update(env_flags)
    env["PYTHONPATH"] = f"src{os.pathsep}."
    command = [
        sys.executable,
        str(PROBE),
        "--library",
        str(library_path),
        "--counts",
        *(str(count) for count in counts),
        "--repeats",
        str(repeats),
        "--json-out",
        str(json_path),
        "--md-out",
        str(md_path),
        "--profile-jsonl",
        str(jsonl_path),
    ]
    subprocess.run(command, cwd=ROOT, env=env, check=True)
    return json_path


def _case_map(path: Path) -> dict[int, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(case["candidate_count"]): case for case in data["cases"]}


def _stage(case: dict[str, Any]) -> dict[str, float]:
    return case["stage_profile"]["stage_median_ms"]


def _write_summary(
    *,
    control_json: Path,
    candidate_json: Path,
    output_json: Path,
    output_md: Path,
    counts: tuple[int, ...],
) -> None:
    control = _case_map(control_json)
    candidate = _case_map(candidate_json)
    rows: list[dict[str, Any]] = []
    for count in counts:
        control_stage = _stage(control[count])
        candidate_stage = _stage(candidate[count])
        rows.append(
            {
                "candidate_count": count,
                "control_total_ms": control_stage["total_ms"],
                "candidate_total_ms": candidate_stage["total_ms"],
                "total_speedup": control_stage["total_ms"] / candidate_stage["total_ms"],
                "control_merge_launch_ms": control_stage.get("merge_launch_ms"),
                "candidate_merge_launch_ms": candidate_stage.get("merge_launch_ms"),
                "control_merge_launches": control[count]["stage_profile"]["topology"]["merge_launches"],
                "candidate_merge_launches": candidate[count]["stage_profile"]["topology"]["merge_launches"],
                "candidate_parity": (
                    candidate[count]["same_candidate_rows"]
                    and candidate[count]["same_valid_count"]
                    and candidate[count]["same_overflowed_flag"]
                    and candidate[count]["profile_topology_matches_expected"]
                ),
            }
        )
    accepted_candidate = all(row["candidate_parity"] for row in rows) and (
        rows[-1]["candidate_total_ms"] < rows[-1]["control_total_ms"]
    )
    summary = {
        "status": "goal1545_device_prefix_compact_comparison_recorded",
        "accepted_candidate_by_runner_rule": accepted_candidate,
        "control_json": str(control_json),
        "candidate_json": str(candidate_json),
        "rows": rows,
        "claim_boundary": (
            "Runner output is measurement input only; public claims still require review and consensus."
        ),
    }
    output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Goal 1545: Device Prefix Compact Pod Runner Summary",
        "",
        "## Verdict",
        "",
        f"Accepted by runner rule: `{accepted_candidate}`",
        "",
        "The runner rule requires parity/topology success for all counts and a total-time improvement at the largest count.",
        "",
        "## Results",
        "",
        "| candidates | control total ms | candidate total ms | speedup | control launches | candidate launches | parity |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {candidate_count} | {control_total_ms:.6f} | {candidate_total_ms:.6f} | "
            "{total_speedup:.3f}x | {control_merge_launches} | {candidate_merge_launches} | {candidate_parity} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- `{control_json}`",
            f"- `{candidate_json}`",
            "",
            "## Claim Boundary",
            "",
            "This runner summary does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action.",
        ]
    )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--counts", type=int, nargs="+", default=list(DEFAULT_COUNTS))
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_REPORT_DIR / f"{REPORT_STEM}_summary.json")
    parser.add_argument("--md-out", type=Path, default=DEFAULT_REPORT_DIR / f"{REPORT_STEM}_summary.md")
    args = parser.parse_args()

    args.report_dir.mkdir(parents=True, exist_ok=True)
    control_json = _run_probe(
        label="control_goal1543",
        env_flags=CONTROL_ENV,
        library_path=args.library,
        report_dir=args.report_dir,
        counts=tuple(args.counts),
        repeats=args.repeats,
    )
    candidate_json = _run_probe(
        label="candidate_device_prefix",
        env_flags=CANDIDATE_ENV,
        library_path=args.library,
        report_dir=args.report_dir,
        counts=tuple(args.counts),
        repeats=args.repeats,
    )
    _write_summary(
        control_json=control_json,
        candidate_json=candidate_json,
        output_json=args.json_out,
        output_md=args.md_out,
        counts=tuple(args.counts),
    )
    print(json.dumps({"status": "goal1545_device_prefix_compact_pod_runner_completed"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
