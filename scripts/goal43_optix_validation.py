from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_goal10_reference import point_nearest_segment_reference
from examples.reference.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.reference.rtdl_language_reference import county_soil_overlay_reference
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference
from examples.reference.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from rtdsl.baseline_runner import load_representative_case
from rtdsl.baseline_contracts import compare_baseline_rows


@dataclass(frozen=True)
class ValidationTarget:
    workload: str
    dataset: str
    kernel: object


TARGETS: tuple[ValidationTarget, ...] = (
    ValidationTarget("lsi", "authored_lsi_minimal", county_zip_join_reference),
    ValidationTarget("pip", "authored_pip_minimal", point_in_counties_reference),
    ValidationTarget("overlay", "authored_overlay_minimal", county_soil_overlay_reference),
    ValidationTarget("ray_tri_hitcount", "authored_ray_tri_minimal", ray_triangle_hitcount_reference),
    ValidationTarget("segment_polygon_hitcount", "authored_segment_polygon_minimal", segment_polygon_hitcount_reference),
    ValidationTarget("point_nearest_segment", "authored_point_nearest_segment_minimal", point_nearest_segment_reference),
    ValidationTarget("lsi", "derived/br_county_subset_segments_tiled_x8", county_zip_join_reference),
    ValidationTarget("pip", "derived/br_county_subset_polygons_tiled_x8", point_in_counties_reference),
)


def target_to_dict(target: ValidationTarget) -> dict[str, str]:
    return {
        "workload": target.workload,
        "dataset": target.dataset,
        "kernel": target.kernel.__name__,
    }


def run_target(target: ValidationTarget) -> dict[str, object]:
    case = load_representative_case(target.workload, target.dataset)
    started_cpu = time.perf_counter()
    cpu_rows = rt.run_cpu(target.kernel, **case.inputs)
    cpu_sec = time.perf_counter() - started_cpu

    started_optix = time.perf_counter()
    optix_rows = rt.run_optix(target.kernel, **case.inputs)
    optix_sec = time.perf_counter() - started_optix

    return {
        "workload": target.workload,
        "dataset": target.dataset,
        "kernel": target.kernel.__name__,
        "cpu_sec": cpu_sec,
        "optix_sec": optix_sec,
        "cpu_count": len(cpu_rows),
        "optix_count": len(optix_rows),
        "parity": compare_baseline_rows(target.workload, cpu_rows, optix_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Goal 43 OptiX validation ladder.")
    parser.add_argument("--output", type=Path, required=True, help="Path to write JSON results.")
    args = parser.parse_args()

    records = [run_target(target) for target in TARGETS]
    payload = {
        "suite": "goal43_optix_validation",
        "optix_version": rt.optix_version(),
        "targets": [target_to_dict(target) for target in TARGETS],
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
