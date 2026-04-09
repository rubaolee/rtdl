from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_release_reference import segment_polygon_hitcount_reference
from rtdsl.baseline_runner import load_representative_case


def run_case(backend: str, dataset: str) -> dict[str, object]:
    case = load_representative_case("segment_polygon_hitcount", dataset)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "cpu":
        rows = rt.run_cpu(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "embree":
        rows = rt.run_embree(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "optix":
        rows = rt.run_optix(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "vulkan":
        rows = rt.run_vulkan(segment_polygon_hitcount_reference, **case.inputs)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    return {
        "backend": backend,
        "dataset": dataset,
        "row_count": len(rows),
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RTDL segment/polygon hit-count example.")
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument(
        "--dataset",
        default="authored_segment_polygon_minimal",
        help=(
            "Representative dataset name. Supports authored, fixture, and "
            "derived/br_county_subset_segment_polygon_tiled_xN forms."
        ),
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=None,
        help="Shortcut for derived/br_county_subset_segment_polygon_tiled_xN.",
    )
    args = parser.parse_args(argv)
    dataset = (
        rt.segment_polygon_large_dataset_name(copies=args.copies)
        if args.copies is not None
        else args.dataset
    )
    print(json.dumps(run_case(args.backend, dataset), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
