#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TEACHING_CONTEXT = {
    "concept_tutorials": [
        "examples/tutorial_programs/nearest_neighbor.py",
        "examples/tutorial_programs/ranked_summary_neighbors.py",
    ],
    "manual_data_flow": [
        "User supplies query point columns on the Torch CUDA device.",
        "RTDL uses prepared point groups as the search structure.",
        "The operator emits the nearest witness id and distance for each query.",
    ],
    "input_columns": {
        "ids": "uint32 query id column",
        "x": "float64 query x coordinate",
        "y": "float64 query y coordinate",
    },
    "relation_output": "one nearest-witness row per query point",
    "continuation": "argmin over candidate distances, with ids and distances kept as output columns",
    "benchmark_bridge": "RTNN and Hausdorff-style nearest witness stages",
}


def make_fixture(torch, query_count: int) -> dict[str, object]:
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    device = torch.device("cuda:0")
    ids_i64 = torch.arange(query_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    x = (ids_i64.to(torch.float64) * 2.0).contiguous()
    y = torch.zeros((query_count,), dtype=torch.float64, device=device)

    search_points = tuple(
        {"id": int(i), "x": float(i * 2.0), "y": 0.0}
        for i in range(query_count)
    )
    point_groups = tuple(
        {
            "id": int(i),
            "point_offset": int(i),
            "point_count": 1,
            "min_x": float(i * 2.0),
            "min_y": 0.0,
            "max_x": float(i * 2.0),
            "max_y": 0.0,
        }
        for i in range(query_count)
    )
    return {
        "search_points": search_points,
        "point_groups": point_groups,
        "query_columns": {
            "ids": ids,
            "x": x,
            "y": y,
        },
        "expected_query_ids": ids,
        "expected_neighbor_ids": ids,
        "expected_distances": torch.zeros((query_count,), dtype=torch.float64, device=device),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="V4 point-group nearest-witness Torch device-array example."
    )
    parser.add_argument("--query-count", "--ray-count", dest="query_count", type=int, default=8192)
    parser.add_argument("--radius", type=float, default=0.5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan: dict[str, Any] = {
        "example": "v4_point_group_nearest_witness_torch_device_arrays",
        "surface": "v4_point_group_nearest_witness_2d_device_arrays",
        "query_count": int(args.query_count),
        "search_count": int(args.query_count),
        "group_count": int(args.query_count),
        "radius": float(args.radius),
        "input_contract": "native_prepared_point_groups_plus_torch_device_query_columns",
        "output_contract": "caller_owned_torch_device_nearest_witness_columns",
        "teaching_context": TEACHING_CONTEXT,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "distance_precision": "float32_computed_float64_output",
        "optix_9_1_validated": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "true_zero_copy_authorized": False,
    }
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        import torch
        import rtdsl.v4_point_group as pg_v4

        fixture = make_fixture(torch, int(args.query_count))
        torch.cuda.synchronize()
        with pg_v4.prepare_point_group_nearest_witness_2d_device_arrays_v4(
            fixture["search_points"],
            fixture["point_groups"],
            max_radius=float(args.radius),
            partner="torch",
        ) as session:
            output_columns = session.allocate_outputs(fixture["query_columns"])
            session.run(
                fixture["query_columns"],
                radius=float(args.radius),
                output_columns=output_columns,
                return_metadata=True,
            )
            torch.cuda.synchronize()
            start = time.perf_counter()
            result = session.run(
                fixture["query_columns"],
                radius=float(args.radius),
                output_columns=output_columns,
                return_metadata=True,
            )
            torch.cuda.synchronize()
            elapsed_s = time.perf_counter() - start

        query_ids_match = bool(torch.equal(output_columns["query_ids"], fixture["expected_query_ids"]))
        neighbor_ids_match = bool(torch.equal(output_columns["neighbor_ids"], fixture["expected_neighbor_ids"]))
        distances_match = bool(torch.allclose(output_columns["distances"], fixture["expected_distances"]))
        payload = {
            "status": "measured",
            **plan,
            "elapsed_s": elapsed_s,
            "correctness_passed": query_ids_match and neighbor_ids_match and distances_match,
            "query_ids_match": query_ids_match,
            "neighbor_ids_match": neighbor_ids_match,
            "distances_match": distances_match,
            "metadata": result["metadata"],
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"dry_run", "measured"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
