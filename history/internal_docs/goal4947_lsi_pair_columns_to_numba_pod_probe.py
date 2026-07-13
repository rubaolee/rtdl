from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import rtdsl as rt
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix


def _fixture_segments() -> tuple[list[dict[str, float | int]], list[dict[str, float | int]]]:
    right = [
        {"id": 0, "x0": 0.5, "y0": -1.0, "x1": 0.5, "y1": 4.0},
        {"id": 1, "x0": 2.5, "y0": -1.0, "x1": 2.5, "y1": 4.0},
        {"id": 2, "x0": 10.0, "y0": -1.0, "x1": 10.0, "y1": 4.0},
    ]
    left = [
        {"id": 0, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},
        {"id": 1, "x0": 2.0, "y0": 1.0, "x1": 3.0, "y1": 1.0},
        {"id": 2, "x0": 0.0, "y0": 2.0, "x1": 3.0, "y1": 2.0},
        {"id": 3, "x0": 20.0, "y0": 2.0, "x1": 21.0, "y1": 2.0},
    ]
    return left, right


def run_probe() -> dict[str, object]:
    left, right = _fixture_segments()
    expected_counts = [1, 1, 2, 0]

    with prepare_segment_pair_intersection_optix(right) as prepared:
        columns = prepared.candidate_device_columns(left, max_rows=16)
        try:
            row_buffer = rt.device_column_row_buffer_from_native_pair_columns(
                columns,
                producer="goal4947_lsi_candidate_pair_columns",
            )
            packet = rt.prepare_device_column_row_buffer_partner_handoff(
                row_buffer,
                partner="numba",
                consumer="run_numba_segmented_count_i64",
            )
            result = rt.run_numba_segmented_count_i64(
                row_buffer.columns["left_id"],
                group_count=len(left),
                validate_group_ids=True,
            )
            counts = result["outputs"]["counts"].copy_to_host().astype(np.int64).tolist()
            metadata = row_buffer.to_metadata()
            return {
                "schema": "rtdl.goal4947.lsi_pair_columns_to_numba.v1",
                "goal": 4947,
                "fixture": "small_segment_pair_lsi_candidate_columns",
                "row_count": row_buffer.row_count,
                "columns": list(row_buffer.columns.keys()),
                "device_resident_candidate": row_buffer.device_resident_candidate,
                "native_device_column_output_proven_on_hardware": (
                    row_buffer.native_device_column_output_proven_on_hardware
                ),
                "host_rows_materialized_before_partner_handoff": metadata[
                    "host_rows_materialized_before_partner_handoff"
                ],
                "partner_packet_status": packet["status"],
                "torch_conversion_used": packet["torch_conversion_used"],
                "counts": counts,
                "expected_counts": expected_counts,
                "counts_match": counts == expected_counts,
                "numba_operation": result["operation"],
                "phase_timing": result["phase_timing"],
                "native_symbol": columns.native_symbol,
                "true_zero_copy_claim_authorized": metadata["true_zero_copy_claim_authorized"],
                "public_speedup_claim_authorized": metadata["public_speedup_claim_authorized"],
                "claim_boundary": {
                    "speedup_claim_authorized": False,
                    "rayjoin_app_claim_authorized": False,
                    "whole_app_claim_authorized": False,
                    "layer1_2_capability_only": True,
                },
            }
        finally:
            columns.owner.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    payload = run_probe()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    if not payload["counts_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
