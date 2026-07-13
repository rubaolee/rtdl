from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _to_jsonable_columns(columns: dict[str, object]) -> dict[str, list[object]]:
    return {name: values.tolist() for name, values in columns.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_goal5397_native_status_stream_smoke_pod.json"
        ),
    )
    args = parser.parse_args()

    import numpy as np
    import rtdsl as rt

    query_coords = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [3.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )
    query_point_ids = np.asarray([100, 101], dtype=np.int64)
    cell_ids = np.asarray([10, 11], dtype=np.int64)
    point_begin_offsets = np.asarray([0, 1], dtype=np.uint64)
    point_counts = np.asarray([1, 1], dtype=np.uint64)
    cell_mbr_min = np.asarray(
        [
            [0.0, -0.1, -0.1],
            [5.0, -0.1, -0.1],
        ],
        dtype=np.float64,
    )
    cell_mbr_max = np.asarray(
        [
            [0.0, 0.1, 0.1],
            [5.0, 0.1, 0.1],
        ],
        dtype=np.float64,
    )
    current_best_distances = np.asarray([np.inf, np.inf], dtype=np.float64)
    current_best_item_ids = np.asarray([-1, -1], dtype=np.int64)

    result = rt.collect_active_query_status_stream_3d_optix(
        query_coords=query_coords,
        query_point_ids=query_point_ids,
        cell_ids=cell_ids,
        point_begin_offsets=point_begin_offsets,
        point_counts=point_counts,
        cell_mbr_min=cell_mbr_min,
        cell_mbr_max=cell_mbr_max,
        radius=10.0,
        current_best_distances=current_best_distances,
        current_best_item_ids=current_best_item_ids,
        max_inline_points=0,
        row_capacity=16,
        emit_pruned_rows=True,
        inline_nearest=False,
    )

    columns = result["columns"]
    valid_count = int(result["valid_count"])
    status_codes = columns["status_codes"].astype(np.int64)
    active_queue_indices = columns["active_queue_indices"].astype(np.int64)
    source_ids = columns["source_ids"].astype(np.int64)
    cell_ids_out = columns["cell_ids"].astype(np.int64)

    expected_active_queries = {0, 1}
    observed_active_queries = set(active_queue_indices.tolist())
    observed_source_ids = set(source_ids.tolist())
    observed_cell_ids = set(cell_ids_out.tolist())
    status_codes_are_offload = bool(valid_count > 0 and np.all(status_codes == 2))
    matched = (
        valid_count >= 2
        and observed_active_queries == expected_active_queries
        and observed_source_ids == {100, 101}
        and observed_cell_ids == {10, 11}
        and status_codes_are_offload
    )

    summary = {
        "goal": "Goal5397",
        "schema": "rtdl.paper_reproduction.xhd.goal5397.native_status_stream_smoke.v1",
        "status": "native_v7_status_stream_smoke_passed" if matched else "native_v7_status_stream_smoke_failed",
        "matched": matched,
        "fixture": "synthetic_two_query_two_cell_status_stream",
        "native_result_metadata": {
            key: value
            for key, value in result.items()
            if key not in {"columns"}
        },
        "observed": {
            "valid_count": valid_count,
            "attempted_count": int(result["attempted_count"]),
            "active_queue_indices": sorted(observed_active_queries),
            "source_ids": sorted(observed_source_ids),
            "cell_ids": sorted(observed_cell_ids),
            "status_codes": sorted(set(status_codes.tolist())),
            "status_codes_are_offload": status_codes_are_offload,
        },
        "columns": _to_jsonable_columns(columns),
        "claim_boundary": {
            "native_v7_symbol_smoke_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
