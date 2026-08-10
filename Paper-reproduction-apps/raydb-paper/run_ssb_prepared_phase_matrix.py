from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from statistics import median
import subprocess
import sys
from typing import Sequence


QUERY_IDS = ("q11", "q12", "q13", "q21", "q22", "q23", "q31", "q32", "q33", "q34", "q41", "q42", "q43")
AUTHOR_TIMING_PATTERN = re.compile(
    r"\[Time\] Build BVH: (?P<build>[0-9.]+) ms.*?"
    r"\[Time\] Launch\(Prepare included\): (?P<prepare>[0-9.]+) ms.*?"
    r"\[Time\] Launch: (?P<launch>[0-9.]+) ms",
    re.DOTALL,
)


def parse_author_timings(author_payload: dict[str, object]) -> dict[str, float]:
    match = AUTHOR_TIMING_PATTERN.search(str(author_payload.get("raw_stdout", "")))
    if match is None:
        raise ValueError("author result does not contain the required Build/Launch timing lines")
    return {
        "build_bvh_ms": float(match.group("build")),
        "launch_prepare_included_ms": float(match.group("prepare")),
        "launch_ms": float(match.group("launch")),
    }


def build_summary(output_dir: Path, author_dir: Path) -> dict[str, object]:
    cases = []
    for query_id in QUERY_IDS:
        rtdl = json.loads((output_dir / f"{query_id}.json").read_text(encoding="utf-8"))
        author = json.loads((author_dir / f"{query_id}.json").read_text(encoding="utf-8"))
        timings = rtdl["phase_timing_seconds"]
        author_timings = parse_author_timings(author)
        launch_ms = float(timings["launch"]) * 1000.0
        if launch_ms <= 0.0:
            raise ValueError(f"{query_id} RTDL native launch time must be positive")
        same_launch_extent = (
            int(rtdl["triangle_count"]) == int(rtdl["row_count"])
            and int(rtdl["ray_grid"]["ray_count"]) > 0
        )
        cases.append(
            {
                "query_id": query_id,
                "same_packet_hashes": bool(rtdl["same_packet_bytes_as_author"]),
                "complete_group_rows_equal": bool(
                    rtdl["rtdl_matches_oracle"]
                    and rtdl["author_matches_oracle"]
                    and rtdl["author_matches_rtdl"]
                    and not rtdl["missing_rows"]
                    and not rtdl["unexpected_rows"]
                ),
                "same_triangle_and_ray_launch_extent_recorded": same_launch_extent,
                "author_ms": author_timings,
                "rtdl_ms": {
                    "scene_prepare": float(timings["prepare_build"]) * 1000.0,
                    "prepared_ray_batch_prepare": float(timings["prepared_ray_batch_prepare"]) * 1000.0,
                    "query_prepare_native": float(timings["query_prepare_native"]) * 1000.0,
                    "launch": launch_ms,
                    "result_download": float(timings["result_download"]) * 1000.0,
                    "legacy_traversal": float(timings["traversal"]) * 1000.0,
                    "prepared_route_total": float(timings["prepared_route_total"]) * 1000.0,
                },
                "author_launch_over_rtdl_launch": author_timings["launch_ms"] / launch_ms,
                "launch_ratio_scope": "same_host_same_packet_level_b_optix_launch_plus_sync_only",
            }
        )
    all_correct = all(
        case["same_packet_hashes"]
        and case["complete_group_rows_equal"]
        and case["same_triangle_and_ray_launch_extent_recorded"]
        for case in cases
    )
    launch_ratios = [float(case["author_launch_over_rtdl_launch"]) for case in cases]
    author_launch_values = [float(case["author_ms"]["launch_ms"]) for case in cases]
    rtdl_launch_values = [float(case["rtdl_ms"]["launch"]) for case in cases]
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_sf1_prepared_phase_matrix.v1",
        "host": "lx1",
        "gpu": "NVIDIA GeForce GTX 1070",
        "input_identity_level": "deterministic_generated_ssb_sf1_same_bytes__not_exact_paper_input",
        "query_count": len(cases),
        "all_correctness_gates_passed": all_correct,
        "native_phase_split_available_for_all_queries": all(
            json.loads((output_dir / f"{query_id}.json").read_text(encoding="utf-8"))["transfer_metadata"][
                "native_phase_split_available"
            ]
            for query_id in QUERY_IDS
        ),
        "phase_contract": {
            "author_launch": "optixLaunch plus synchronization only",
            "rtdl_launch": "optixLaunch plus synchronization only",
            "prepared_ray_batch_prepare": "host-packed query rays uploaded before the measured native grouped-reduction call",
            "rtdl_query_prepare_native": "group output allocation/reset and launch-parameter upload after rays and primitive payload are resident",
            "rtdl_result_download": "grouped aggregates and hit-event count copied to host after launch",
        },
        "launch_only_summary": {
            "author_launch_median_ms": median(author_launch_values),
            "rtdl_launch_median_ms": median(rtdl_launch_values),
            "per_query_author_over_rtdl_ratio_median": median(launch_ratios),
            "per_query_author_over_rtdl_ratio_min": min(launch_ratios),
            "per_query_author_over_rtdl_ratio_max": max(launch_ratios),
            "rtdl_faster_query_count": sum(value > 1.0 for value in launch_ratios),
            "author_faster_query_count": sum(value < 1.0 for value in launch_ratios),
            "tie_query_count": sum(value == 1.0 for value in launch_ratios),
            "cross_query_aggregate_speedup_authorized": False,
            "interpretation": (
                "Per-query launch-only diagnostics are aligned. Their median is a distribution summary, "
                "not a paper Figure-12 aggregate speedup."
            ),
        },
        "cases": cases,
        "decision": {
            "same_host_same_packet_launch_only_ratio_authorized": all_correct,
            "launch_prepare_included_ratio_authorized": False,
            "figure12_ratio_authorized": False,
            "crystal_ratio_authorized": False,
            "paper_performance_claimed": False,
            "next_action": (
                "retain this as a Level-B launch-only matrix; acquire an adequate SF10/SF20 host and the "
                "paper-modified Crystal denominator before any Figure-12 claim"
            ),
        },
        "claim_boundary": {
            "all_13_ssb_sf1_complete_grouped_rows_claimed": all_correct,
            "level_b_same_host_launch_only_comparison_claimed": all_correct,
            "exact_paper_input_claimed": False,
            "figure12_reproduced": False,
            "paper_modified_crystal_reproduced": False,
            "paper_performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all 13 RayDB SF1 packets with prepared-ray phase telemetry")
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--author-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Rebuild the summary from existing per-query outputs without rerunning GPU work",
    )
    parser.add_argument(
        "--packet-runner",
        type=Path,
        default=Path(__file__).with_name("run_ssb_packet_rtdl.py"),
    )
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if not args.summary_only:
        for query_id in QUERY_IDS:
            command = [
                sys.executable,
                str(args.packet_runner),
                "--packet-json",
                str(args.packet_root / query_id / "packet.json"),
                "--author-result",
                str(args.author_root / f"{query_id}.json"),
                "--prepared-ray-batch",
                "--output-json",
                str(args.output_dir / f"{query_id}.json"),
            ]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            (args.output_dir / f"{query_id}.log").write_text(
                completed.stdout + completed.stderr,
                encoding="utf-8",
            )
            if completed.returncode != 0:
                raise RuntimeError(f"{query_id} RTDL phase run failed with exit code {completed.returncode}")
    summary = build_summary(args.output_dir, args.author_root)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["all_correctness_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
