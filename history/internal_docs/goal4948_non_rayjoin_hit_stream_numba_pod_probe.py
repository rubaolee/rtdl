from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import rtdsl as rt
from rtdsl.reference import Ray3D, Triangle3D


def _fixture() -> tuple[tuple[Ray3D, ...], tuple[Triangle3D, ...]]:
    triangles = (
        Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        Triangle3D(1, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0),
        Triangle3D(2, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0),
    )
    rays = (
        Ray3D(0, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
        Ray3D(1, 2.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
        Ray3D(2, 10.0, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
    )
    return rays, triangles


def run_probe() -> dict[str, object]:
    rays, triangles = _fixture()
    expected_counts = [2, 1, 0]

    with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
        hit_columns = scene.ray_triangle_hit_stream_device_columns(
            rays,
            max_rows=8,
            deduplicate_primitives=False,
        )
        row_buffer = rt.device_column_row_buffer_from_hit_stream_handoff(
            hit_columns,
            producer="goal4948_ray_triangle_hit_stream",
        )
        result = rt.run_numba_segmented_count_i64(
            row_buffer.columns["ray_ids"],
            group_count=len(rays),
            validate_group_ids=True,
        )
        counts = result["outputs"]["counts"].copy_to_host().astype(np.int64).tolist()
        metadata = row_buffer.to_metadata()
        return {
            "schema": "rtdl.goal4948.non_rayjoin_hit_stream_numba.v1",
            "goal": 4948,
            "fixture": "ray_triangle_hit_stream_per_ray_count",
            "producer": row_buffer.producer,
            "row_count": row_buffer.row_count,
            "columns": list(row_buffer.columns.keys()),
            "device_resident_candidate": row_buffer.device_resident_candidate,
            "native_device_column_output_proven_on_hardware": (
                row_buffer.native_device_column_output_proven_on_hardware
            ),
            "host_rows_materialized_before_partner_handoff": metadata[
                "host_rows_materialized_before_partner_handoff"
            ],
            "counts": counts,
            "expected_counts": expected_counts,
            "counts_match": counts == expected_counts,
            "numba_operation": result["operation"],
            "phase_timing": result["phase_timing"],
            "native_symbol": hit_columns.native_symbol,
            "true_zero_copy_claim_authorized": metadata["true_zero_copy_claim_authorized"],
            "public_speedup_claim_authorized": metadata["public_speedup_claim_authorized"],
            "claim_boundary": {
                "non_rayjoin_genericity_gate": True,
                "rayjoin_app_claim_authorized": False,
                "speedup_claim_authorized": False,
                "whole_app_claim_authorized": False,
                "layer1_2_capability_only": True,
            },
        }


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
