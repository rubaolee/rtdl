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
from examples.reference.rtdl_release_reference import segment_polygon_anyhit_rows_reference
from rtdsl.baseline_runner import load_representative_case


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("segment_polygon_anyhit_rows")
    return {"class": support.performance_class, "note": support.note}


def _summarize_rows(rows: tuple[dict[str, object], ...], segments: tuple[object, ...]) -> dict[str, object]:
    counts = {int(segment.id): 0 for segment in segments}
    polygon_ids_by_segment = {int(segment.id): [] for segment in segments}
    for row in rows:
        segment_id = int(row["segment_id"])
        counts[segment_id] = counts.get(segment_id, 0) + 1
        polygon_ids_by_segment.setdefault(segment_id, []).append(int(row["polygon_id"]))
    return {
        "segment_flags": tuple(
            {"segment_id": segment_id, "any_hit": int(count > 0)}
            for segment_id, count in sorted(counts.items())
        ),
        "segment_counts": tuple(
            {"segment_id": segment_id, "hit_count": count}
            for segment_id, count in sorted(counts.items())
        ),
        "polygon_ids_by_segment": {
            str(segment_id): sorted(polygon_ids)
            for segment_id, polygon_ids in sorted(polygon_ids_by_segment.items())
        },
    }


def _run_anyhit_rows(backend: str, case) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(segment_polygon_anyhit_rows_reference, **case.inputs)
    if backend == "cpu":
        return rt.run_cpu(segment_polygon_anyhit_rows_reference, **case.inputs)
    if backend == "embree":
        return rt.run_embree(segment_polygon_anyhit_rows_reference, **case.inputs)
    if backend == "optix":
        return rt.run_optix(segment_polygon_anyhit_rows_reference, **case.inputs)
    if backend == "vulkan":
        return rt.run_vulkan(segment_polygon_anyhit_rows_reference, **case.inputs)
    raise ValueError(f"unsupported backend `{backend}`")


def _run_hitcount_rows(backend: str, case) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(segment_polygon_hitcount_reference, **case.inputs)
    if backend == "cpu":
        return rt.run_cpu(segment_polygon_hitcount_reference, **case.inputs)
    if backend == "embree":
        return rt.run_embree(segment_polygon_hitcount_reference, **case.inputs)
    if backend == "optix":
        return rt.run_optix(segment_polygon_hitcount_reference, **case.inputs)
    if backend == "vulkan":
        return rt.run_vulkan(segment_polygon_hitcount_reference, **case.inputs)
    raise ValueError(f"unsupported backend `{backend}`")


def _summarize_hitcount_rows(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    counts = {
        int(row["segment_id"]): int(row["hit_count"])
        for row in rows
    }
    return {
        "segment_flags": tuple(
            {"segment_id": segment_id, "any_hit": int(hit_count > 0)}
            for segment_id, hit_count in sorted(counts.items())
        ),
        "segment_counts": tuple(
            {"segment_id": segment_id, "hit_count": hit_count}
            for segment_id, hit_count in sorted(counts.items())
        ),
    }


def run_case(backend: str, dataset: str, output_mode: str = "rows") -> dict[str, object]:
    if output_mode not in {"rows", "segment_flags", "segment_counts"}:
        raise ValueError("output_mode must be 'rows', 'segment_flags', or 'segment_counts'")
    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    if output_mode == "rows":
        rows = _run_anyhit_rows(backend, case)
        summary = _summarize_rows(rows, case.inputs["segments"])
        row_count = len(rows)
        summary_source = "segment_polygon_anyhit_rows"
    else:
        rows = _run_hitcount_rows(backend, case)
        summary = _summarize_hitcount_rows(rows)
        row_count = len(rows)
        summary_source = "segment_polygon_hitcount"
    payload: dict[str, object] = {
        "app": "segment_polygon_anyhit_rows",
        "backend": backend,
        "dataset": dataset,
        "output_mode": output_mode,
        "row_count": row_count,
        "summary_source": summary_source,
        "optix_performance": _optix_performance(),
        "boundary": (
            "Rows mode emits segment/polygon pair rows. Compact segment_flags and "
            "segment_counts use the RTDL segment_polygon_hitcount primitive to avoid "
            "materializing full pair rows. OptiX app exposure is still classified "
            "separately from RT-core performance; use optix_performance for the "
            "current classification."
        ),
    }
    if output_mode == "rows":
        payload["rows"] = rows
    elif output_mode == "segment_flags":
        payload["segment_flags"] = summary["segment_flags"]
    else:
        payload["segment_counts"] = summary["segment_counts"]
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RTDL segment/polygon any-hit rows example.")
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
        "--output-mode",
        choices=("rows", "segment_flags", "segment_counts"),
        default="rows",
        help="Use segment_flags or segment_counts to avoid emitting full segment/polygon pair rows.",
    )
    args = parser.parse_args(argv)
    dataset = (
        rt.segment_polygon_large_dataset_name(copies=args.copies)
        if args.copies is not None
        else args.dataset
    )
    print(json.dumps(run_case(args.backend, dataset, args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
