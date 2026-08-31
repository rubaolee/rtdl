from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }


def _fixture() -> tuple[tuple[rt.Polygon, ...], tuple[rt.Polygon, ...]]:
    left = (
        rt.Polygon(id=3, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
        rt.Polygon(id=20, vertices=((5.0, 5.0), (6.0, 5.0), (6.0, 6.0), (5.0, 6.0))),
        rt.Polygon(id=31, vertices=((10.0, 10.0), (11.0, 10.0), (11.0, 11.0), (10.0, 11.0))),
    )
    right = (
        rt.Polygon(id=10, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),
        rt.Polygon(id=11, vertices=((0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75))),
        rt.Polygon(id=12, vertices=((20.0, 20.0), (21.0, 20.0), (21.0, 21.0), (20.0, 21.0))),
        rt.Polygon(id=13, vertices=((4.0, 4.0), (7.0, 4.0), (7.0, 7.0), (4.0, 7.0))),
    )
    return left, right


def _as_list(array) -> list:
    import cupy as cp  # type: ignore

    cp.cuda.Stream.null.synchronize()
    return cp.asnumpy(array).tolist()


def run_probe() -> dict[str, object]:
    left, right = _fixture()
    with prepare_rayjoin_optix_shape_pair_active_count(
        right,
        dataset="goal3455_sparse_id_ordinal_columns_fixture",
        dataset_note="Goal3455 generic relation ordinal-column fixture.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left)
        with prepared.active_relation_device_columns(packed_left, max_rows=32) as columns:
            ids = columns.as_cupy_columns()
            ordinals = columns.as_cupy_ordinal_columns()
            metadata = columns.to_metadata()
            observed_rows = [
                {
                    "left_id": int(left_id),
                    "right_id": int(right_id),
                    "left_ordinal": int(left_ordinal),
                    "right_ordinal": int(right_ordinal),
                }
                for left_id, right_id, left_ordinal, right_ordinal in zip(
                    _as_list(ids["left_id"]),
                    _as_list(ids["right_id"]),
                    _as_list(ordinals["left_ordinal"]),
                    _as_list(ordinals["right_ordinal"]),
                )
            ]
    observed_rows = sorted(observed_rows, key=lambda row: (row["left_id"], row["right_id"]))
    expected_rows = [
        {"left_id": 3, "right_id": 10, "left_ordinal": 0, "right_ordinal": 0},
        {"left_id": 3, "right_id": 11, "left_ordinal": 0, "right_ordinal": 1},
        {"left_id": 20, "right_id": 13, "left_ordinal": 1, "right_ordinal": 3},
    ]
    return {
        "schema": "rtdl.goal3455.shape_pair_relation_ordinal_columns.v1",
        "goal": 3455,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "fixture": "sparse_id_three_left_four_right_rectangles",
        "observed_rows": observed_rows,
        "expected_rows": expected_rows,
        "ordinal_rows_match": observed_rows == expected_rows,
        "metadata_ordinal_columns": metadata["runtime"]["ordinal_columns"],
        "metadata_geometry_payload": metadata["runtime"]["geometry_payload"],
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3455 relation ordinal-column probe.")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["ordinal_rows_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
