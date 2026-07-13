from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    goal5367 = _read_json(RESULTS / "xhd_goal5367_lb_author_radius_probe.json")
    noinline = _read_json(
        RESULTS / "xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json"
    )
    author_rows = int(goal5367["author_reference"]["offloading_size_rows"])
    inline_rows = int(goal5367["rtdl_routes"]["author_iteration_radius_lb256_probe"]["heavy_offload_peak_rows"])
    full_cover_rows = int(
        goal5367["rtdl_routes"]["full_cover_radius_lb256_from_goal5365"]["heavy_offload_peak_rows"]
    )
    noinline_kind2 = int(noinline["frontier"]["raw_frontier_kind2_rows"])
    noinline_attempted = int(noinline["frontier"]["attempted_count"])
    noinline_kind_counts = dict(noinline["frontier"]["raw_frontier_kind_counts"])
    artifact = {
        "goal": "Goal5368",
        "date": "2026-07-09",
        "status": "raw_kind_count_telemetry_ready__author_lb_denominator_still_unmatched",
        "exit_label": "raw_kind2_denominator_probe_shows_author_queue_state_gap",
        "purpose": (
            "Add generic native raw frontier kind-count telemetry so count-only "
            "overflow probes can measure offload-kind rows without materializing "
            "hundreds of millions of frontier rows."
        ),
        "input_scope": {
            "input1": noinline["input1"],
            "input2": noinline["input2"],
            "point_count_a": int(noinline["point_count_a"]),
            "point_count_b": int(noinline["point_count_b"]),
            "preprocessing": list(noinline["preprocessing"]),
            "exact_paper_dataset_identity_proven": False,
            "scope": "Dragon -> AsianDragon temporary public/POD input, not exact paper dataset",
        },
        "author_reference": {
            "lb": 256,
            "hd_result": float(goal5367["author_reference"]["hd_result"]),
            "radius": float(goal5367["author_reference"]["iteration_radius"]),
            "offloading_size_rows": author_rows,
            "wl_heavy_peak_bytes": int(goal5367["author_reference"]["wl_heavy_peak_bytes"]),
            "author_byte_formula": "OffloadingSize * 2 * sizeof(uint32_t)",
        },
        "rtdl_reference_rows": {
            "full_cover_lb256_heavy_rows_from_goal5367": full_cover_rows,
            "author_radius_inline_lb256_heavy_rows_from_goal5367": inline_rows,
            "author_radius_noinline_raw_kind2_rows_from_goal5368": noinline_kind2,
            "author_radius_noinline_attempted_all_kinds": noinline_attempted,
            "author_radius_noinline_raw_kind_counts": noinline_kind_counts,
        },
        "comparison": {
            "author_offloading_size_rows": author_rows,
            "rtdl_noinline_raw_kind2_rows": noinline_kind2,
            "rtdl_noinline_kind2_div_author": noinline_kind2 / author_rows,
            "row_delta_author_minus_noinline_kind2": author_rows - noinline_kind2,
            "row_count_parity": noinline_kind2 == author_rows,
            "noinline_raw_kind2_greater_than_author": noinline_kind2 > author_rows,
            "noinline_raw_kind2_greater_than_inline_materialized_rows": noinline_kind2 > inline_rows,
            "inline_materialized_rows_div_author": inline_rows / author_rows,
            "full_cover_materialized_rows_div_author": full_cover_rows / author_rows,
        },
        "telemetry": {
            "schema": noinline["frontier"]["native_memory_telemetry"]["schema"],
            "overflowed": bool(noinline["frontier"]["overflowed"]),
            "overflow_telemetry_only": bool(noinline["frontier"]["overflow_telemetry_only"]),
            "frontier_row_capacity": int(noinline["frontier_row_capacity"]),
            "native_symbol": noinline["frontier"]["native_symbol"],
            "raw_frontier_kind_counts_semantics": noinline["frontier"]["native_memory_telemetry"][
                "raw_frontier_kind_counts_semantics"
            ],
        },
        "interpretation": {
            "what_goal5368_proves": (
                "The native producer can now report raw generic frontier kind counts "
                "before row download and host sort/unique, even in overflow/count-only mode."
            ),
            "denominator_result": (
                "The no-inline raw kind2/offload denominator is much larger than author "
                "OffloadingSize, so the author denominator is not merely all raw cells "
                "above the lb threshold under the same scalar radius."
            ),
            "next_required_alignment": (
                "Align author iterative queue state: in_queue_idx, per-iteration cmin2/current "
                "best, radius schedule, and raw offload emission semantics."
            ),
        },
        "claim_boundary": {
            "generic_system_telemetry_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "validation": {
            "local_tests": [
                "py -m py_compile src/rtdsl/optix_runtime.py",
                "py -m py_compile src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py",
                "py -m unittest tests.goal5368_cell_mbr_frontier_kind_count_telemetry_test",
            ],
            "pod_tests": [
                "py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight",
                "make build-optix in /tmp/rtdl_goal5364",
                "small POD smoke returned raw_frontier_kind_counts {'1': 1, '2': 1, '3': 1}",
                "Dragon -> AsianDragon no-inline count-only probe completed without row materialization",
            ],
        },
        "input_artifacts": {
            "goal5367": str(RESULTS / "xhd_goal5367_lb_author_radius_probe.json"),
            "goal5368_pod_probe": str(
                RESULTS / "xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json"
            ),
        },
    }
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, sort_keys=True))


if __name__ == "__main__":
    main()
