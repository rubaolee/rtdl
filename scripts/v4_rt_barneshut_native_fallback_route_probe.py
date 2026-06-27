from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rt_barneshut_author_contract import (  # noqa: E402
    load_rt_barneshut_author_dataset,
    run_rt_barneshut_cpu_author_semantics_oracle,
)
from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    run_v4_rt_barneshut_native_author_route,
)


def _relative_error(observed: float, expected: float) -> float:
    return abs(observed - expected) / max(abs(expected), 1.0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the V4 native RT-BarnesHut author-semantics ABI checksum route. "
            "Default mode attempts the Goal4765 RT-core candidate; --force-fallback "
            "keeps the Goal4764 host fallback regression gate. This is not a public speed claim."
        )
    )
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--file-type", required=True, choices=("treelogy", "csv"))
    parser.add_argument("--limit", required=True, type=int)
    parser.add_argument("--optix-lib", default=None, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force-fallback", action="store_true")
    args = parser.parse_args()

    try:
        import cupy as cp
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Goal4764 native fallback probe requires cupy and numpy on the GPU host") from exc

    dataset = load_rt_barneshut_author_dataset(
        args.dataset,
        file_type=args.file_type,
        limit=args.limit,
    )
    point_ids = np.asarray([point.id for point in dataset.points], dtype=np.uint64)
    point_x = np.asarray([point.x for point in dataset.points], dtype=np.float32)
    point_y = np.asarray([point.y for point in dataset.points], dtype=np.float32)
    point_z = np.asarray([point.z for point in dataset.points], dtype=np.float32)
    point_mass = np.asarray([point.mass for point in dataset.points], dtype=np.float32)

    d_point_ids = cp.asarray(point_ids)
    d_point_x = cp.asarray(point_x)
    d_point_y = cp.asarray(point_y)
    d_point_z = cp.asarray(point_z)
    d_point_mass = cp.asarray(point_mass)

    old_force_fallback = os.environ.get("RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK")
    try:
        if args.force_fallback:
            os.environ["RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK"] = "1"
        else:
            os.environ.pop("RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK", None)
        route = run_v4_rt_barneshut_native_author_route(
            point_ids_device_ptr=int(d_point_ids.data.ptr),
            point_x_device_ptr=int(d_point_x.data.ptr),
            point_y_device_ptr=int(d_point_y.data.ptr),
            point_z_device_ptr=int(d_point_z.data.ptr),
            point_mass_device_ptr=int(d_point_mass.data.ptr),
            point_count=dataset.point_count,
            theta=0.5,
            optix_library=args.optix_lib,
        )
    finally:
        if old_force_fallback is None:
            os.environ.pop("RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK", None)
        else:
            os.environ["RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK"] = old_force_fallback
    oracle = run_rt_barneshut_cpu_author_semantics_oracle(
        args.dataset,
        file_type=args.file_type,
        limit=args.limit,
    )
    checksum_relative_error = _relative_error(route.force_checksum, oracle.force_checksum)
    abs_checksum_relative_error = _relative_error(route.force_abs_checksum, oracle.force_abs_checksum)
    validation = {
        "oracle_force_checksum": oracle.force_checksum,
        "native_force_checksum": route.force_checksum,
        "checksum_relative_error": checksum_relative_error,
        "oracle_force_abs_checksum": oracle.force_abs_checksum,
        "native_force_abs_checksum": route.force_abs_checksum,
        "abs_checksum_relative_error": abs_checksum_relative_error,
        "passes_float_output_tolerance": checksum_relative_error <= 1.0e-4
        and abs_checksum_relative_error <= 1.0e-4,
    }
    payload = route.as_dict()
    payload.update(
        {
            "goal": "Goal4764" if args.force_fallback else "Goal4765",
            "goal4765_rt_core_candidate_attempted": not args.force_fallback,
            "dataset": dataset.without_points(),
            "oracle": oracle.without_points() if hasattr(oracle, "without_points") else {
                "force_checksum": oracle.force_checksum,
                "force_abs_checksum": oracle.force_abs_checksum,
                "node_count": oracle.node_count,
                "leaf_count": oracle.leaf_count,
                "grid_size": oracle.grid_size,
            },
            "checksum_validation": validation,
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not validation["passes_float_output_tolerance"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
