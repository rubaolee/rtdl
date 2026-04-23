from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_release_reference import segment_polygon_hitcount_reference
from rtdsl.baseline_runner import load_representative_case


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("segment_polygon_hitcount")
    return {"class": support.performance_class, "note": support.note}


@contextmanager
def _temporary_optix_segpoly_mode(optix_mode: str):
    previous = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
    if optix_mode == "native":
        os.environ["RTDL_OPTIX_SEGPOLY_MODE"] = "native"
    elif optix_mode == "host_indexed":
        os.environ.pop("RTDL_OPTIX_SEGPOLY_MODE", None)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("RTDL_OPTIX_SEGPOLY_MODE", None)
        else:
            os.environ["RTDL_OPTIX_SEGPOLY_MODE"] = previous


def run_case(backend: str, dataset: str, *, optix_mode: str = "auto") -> dict[str, object]:
    if optix_mode not in {"auto", "host_indexed", "native"}:
        raise ValueError("optix_mode must be 'auto', 'host_indexed', or 'native'")
    case = load_representative_case("segment_polygon_hitcount", dataset)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "cpu":
        rows = rt.run_cpu(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "embree":
        rows = rt.run_embree(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "optix":
        with _temporary_optix_segpoly_mode(optix_mode):
            rows = rt.run_optix(segment_polygon_hitcount_reference, **case.inputs)
    elif backend == "vulkan":
        rows = rt.run_vulkan(segment_polygon_hitcount_reference, **case.inputs)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    return {
        "app": "segment_polygon_hitcount",
        "backend": backend,
        "dataset": dataset,
        "optix_mode": optix_mode if backend == "optix" else "not_applicable",
        "row_count": len(rows),
        "rows": rows,
        "optix_performance": _optix_performance(),
        "boundary": "RT-core performance remains classified separately: OptiX mode 'native' explicitly requests the experimental native custom-AABB path, but current public performance class stays host_indexed_fallback until a focused correctness/performance gate passes.",
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
    parser.add_argument(
        "--optix-mode",
        choices=("auto", "host_indexed", "native"),
        default="auto",
        help="OptiX only: preserve current default, force host-indexed fallback, or request experimental native custom-AABB mode.",
    )
    args = parser.parse_args(argv)
    dataset = (
        rt.segment_polygon_large_dataset_name(copies=args.copies)
        if args.copies is not None
        else args.dataset
    )
    print(json.dumps(run_case(args.backend, dataset, optix_mode=args.optix_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
