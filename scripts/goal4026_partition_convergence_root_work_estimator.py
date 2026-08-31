from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARTITION = ROOT / "docs" / "reports" / "goal4014_compressed_partition_enumeration_accounting.json"
DEFAULT_TELEMETRY = ROOT / "docs" / "reports" / "goal4007_grouped_union_root_read_telemetry_pod"


def _load_grouped_union_telemetry(directory: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = str(data["profile"])
        variant = data["rows"][0]["variants"][0]
        telemetry = tuple(int(value) for value in variant["last_telemetry"])
        rows[profile] = {
            "profile": profile,
            "radius": float(data["radius"]),
            "point_count": int(data["point_counts"][0]),
            "current_median_elapsed_sec": float(variant["median_elapsed_sec"]),
            "current_median_native_elapsed_sec": float(variant["median_native_elapsed_sec"]),
            "current_radius_candidate_hits_after_predicate": telemetry[4],
            "current_same_root_culled_candidate_hits": telemetry[5],
            "current_reported_intersection_candidates": telemetry[7],
            "current_root_find_invocations": telemetry[8],
            "current_root_find_parent_link_steps": telemetry[9],
        }
    return rows


def estimate_root_work(partition_artifact: Path, telemetry_dir: Path) -> dict:
    partition = json.loads(partition_artifact.read_text(encoding="utf-8"))
    telemetry_by_profile = _load_grouped_union_telemetry(telemetry_dir)
    rows = []
    for partition_row in partition["rows"]:
        profile = str(partition_row["profile"])
        telemetry = telemetry_by_profile[profile]
        summary = partition_row["best_ambiguous_pair_ratio"]
        current_root_reads = int(telemetry["current_root_find_invocations"])
        ambiguous_ratio = float(summary["ambiguous_of_near_pair_ratio"])
        ambiguous_root_read_upper = int(round(current_root_reads * ambiguous_ratio))
        safe_full_partition_union_root_read_upper = 2 * int(summary["safe_full_cell_pairs"])
        estimated_future_root_read_upper = (
            ambiguous_root_read_upper + safe_full_partition_union_root_read_upper
        )
        reduction = 1.0 - (estimated_future_root_read_upper / current_root_reads)
        rows.append({
            "profile": profile,
            "point_count": telemetry["point_count"],
            "radius": telemetry["radius"],
            "cell_size_label": summary["cell_size_label"],
            "occupied_partitions": int(summary["occupied_cells"]),
            "enumerated_cell_pairs": int(summary["enumerated_cell_pairs"]),
            "safe_full_partition_pairs": int(summary["safe_full_cell_pairs"]),
            "ambiguous_partition_pairs": int(summary["ambiguous_cell_pairs"]),
            "ambiguous_pair_upper": int(summary["ambiguous_pair_upper"]),
            "near_pair_upper": int(summary["near_pair_upper"]),
            "ambiguous_of_near_pair_ratio": ambiguous_ratio,
            "current_root_find_invocations": current_root_reads,
            "current_root_find_parent_link_steps": int(telemetry["current_root_find_parent_link_steps"]),
            "current_median_native_elapsed_sec": telemetry["current_median_native_elapsed_sec"],
            "estimated_ambiguous_root_read_upper": ambiguous_root_read_upper,
            "estimated_safe_full_partition_union_root_read_upper": safe_full_partition_union_root_read_upper,
            "estimated_partition_route_root_read_upper": estimated_future_root_read_upper,
            "estimated_root_read_reduction_ratio": reduction,
            "estimated_root_read_reduction_x": (
                current_root_reads / estimated_future_root_read_upper
                if estimated_future_root_read_upper > 0 else None
            ),
        })
    return {
        "goal": "Goal4026",
        "input_partition_artifact": str(partition_artifact.as_posix()),
        "input_telemetry_dir": str(telemetry_dir.as_posix()),
        "estimator_boundary": {
            "diagnostic_only": True,
            "timing_claim_authorized": False,
            "native_abi_added": False,
            "release_authorized": False,
            "conservative_safe_full_root_reads_per_partition_pair": 2,
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition-artifact", type=Path, default=DEFAULT_PARTITION)
    parser.add_argument("--telemetry-dir", type=Path, default=DEFAULT_TELEMETRY)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = estimate_root_work(args.partition_artifact, args.telemetry_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
