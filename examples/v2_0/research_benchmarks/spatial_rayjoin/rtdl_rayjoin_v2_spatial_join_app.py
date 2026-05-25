from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_soil_overlay_reference
from examples.reference.rtdl_language_reference import county_zip_join_reference
from rtdsl.baseline_runner import DatasetCase
from rtdsl.baseline_runner import load_representative_case
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_polygons
from rtdsl.datasets import chains_to_probe_points
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb


_WORKLOADS = ("pip", "lsi", "overlay_seed")
_PREPARED_OPTIX_WORKLOADS = ("pip", "lsi")

_DEFAULT_DATASETS = {
    "pip": "tests/fixtures/rayjoin/br_county_subset.cdb",
    "lsi": "tests/fixtures/rayjoin/br_county_subset.cdb",
    "overlay_seed": "tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb",
}


@rt.kernel(backend="rtdl", precision="float_approx")
def rayjoin_point_location_positive_hits_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(
            exact=False,
            boundary_mode="inclusive",
            result_mode="positive_hits",
        ),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


_KERNELS = {
    "pip": rayjoin_point_location_positive_hits_reference,
    "lsi": county_zip_join_reference,
    "overlay_seed": county_soil_overlay_reference,
}

_BASELINE_WORKLOAD = {
    "pip": "pip",
    "lsi": "lsi",
    "overlay_seed": "overlay",
}


def _resolve_dataset_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def _split_dataset_paths(dataset: str) -> tuple[Path, ...]:
    return tuple(_resolve_dataset_path(part.strip()) for part in dataset.split("+") if part.strip())


def _load_external_cdb_case(workload: str, dataset: str) -> DatasetCase:
    paths = _split_dataset_paths(dataset)
    if workload == "pip":
        if len(paths) == 1:
            point_dataset = polygon_dataset = load_cdb(paths[0])
            note = "External CDB point-location case using probe points and polygons from one file."
        elif len(paths) == 2:
            point_dataset = load_cdb(paths[0])
            polygon_dataset = load_cdb(paths[1])
            note = "External CDB point-location case using points from the left file and polygons from the right file."
        else:
            raise ValueError("external PIP dataset must be `path.cdb` or `points.cdb + polygons.cdb`")
        return DatasetCase(
            workload="pip",
            dataset=dataset,
            inputs={
                "points": chains_to_probe_points(point_dataset),
                "polygons": chains_to_polygons(polygon_dataset),
            },
            note=note,
        )
    if workload == "lsi":
        if len(paths) != 2:
            raise ValueError("external LSI dataset must be `left.cdb + right.cdb`")
        left = load_cdb(paths[0])
        right = load_cdb(paths[1])
        return DatasetCase(
            workload="lsi",
            dataset=dataset,
            inputs={
                "left": segments_from_records(chains_to_segments(left)),
                "right": segments_from_records(chains_to_segments(right)),
            },
            note="External CDB line-segment intersection case using left/right chain segments.",
        )
    if workload == "overlay_seed":
        if len(paths) != 2:
            raise ValueError("external overlay_seed dataset must be `left.cdb + right.cdb`")
        left = load_cdb(paths[0])
        right = load_cdb(paths[1])
        return DatasetCase(
            workload="overlay",
            dataset=dataset,
            inputs={
                "left": chains_to_polygons(left),
                "right": chains_to_polygons(right),
            },
            note="External CDB overlay pair-dependency case using left/right polygon chains.",
        )
    raise ValueError("workload must be one of: pip, lsi, overlay_seed")


def _load_rayjoin_case(workload: str, dataset: str) -> DatasetCase:
    baseline_workload = _BASELINE_WORKLOAD[workload]
    try:
        return load_representative_case(baseline_workload, dataset)
    except ValueError:
        paths = _split_dataset_paths(dataset)
        if paths and all(path.exists() for path in paths):
            return _load_external_cdb_case(workload, dataset)
        raise


def _run_backend(kernel, backend: str, inputs: dict[str, object]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(kernel, **inputs)
    if backend == "cpu":
        return rt.run_cpu(kernel, **inputs)
    if backend == "embree":
        return rt.run_embree(kernel, **inputs)
    if backend == "optix":
        return rt.run_optix(kernel, **inputs)
    raise ValueError("backend must be one of: cpu_python_reference, cpu, embree, optix")


def _positive_pip_assignments(rows: tuple[dict[str, object], ...]) -> tuple[dict[str, int], ...]:
    return tuple(
        {
            "point_id": int(row["point_id"]),
            "polygon_id": int(row["polygon_id"]),
        }
        for row in rows
        if int(row["contains"]) == 1
    )


def _summarize_rows(workload: str, rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    if workload == "pip":
        positives = _positive_pip_assignments(rows)
        return {
            "positive_hit_row_count": len(rows),
            "positive_assignment_count": len(positives),
            "positive_assignments": positives,
            "output_contract": "point_to_polygon_positive_hit_rows",
        }
    if workload == "lsi":
        return {
            "intersection_count": len(rows),
            "output_contract": "segment_segment_intersection_rows",
        }
    active_seed_pairs = tuple(
        {
            "left_polygon_id": int(row["left_polygon_id"]),
            "right_polygon_id": int(row["right_polygon_id"]),
            "requires_lsi": int(row["requires_lsi"]),
            "requires_pip": int(row["requires_pip"]),
        }
        for row in rows
        if int(row["requires_lsi"]) == 1 or int(row["requires_pip"]) == 1
    )
    return {
        "pair_dependency_row_count": len(rows),
        "active_seed_count": len(active_seed_pairs),
        "active_seed_pairs": active_seed_pairs,
        "output_contract": "overlay_pair_dependency_rows_with_lsi_pip_flags",
    }


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def _phase_time(phases: dict[str, float], label: str, fn):
    start = time.perf_counter()
    value = fn()
    phases[label] = time.perf_counter() - start
    return value


def run_rayjoin_prepared_optix_workload(
    workload: str,
    *,
    dataset: str | None = None,
    result_mode: str = "count",
    include_rows: bool = False,
) -> dict[str, object]:
    """Run the RayJoin-style prepared OptiX route with phase boundaries.

    This is the serious v2.x benchmark route for RayJoin-style PIP and LSI.
    It keeps RayJoin policy in Python while using generic prepared RTDL
    primitives underneath.
    """

    if workload not in _PREPARED_OPTIX_WORKLOADS:
        raise ValueError("prepared_optix route currently supports only: pip, lsi")
    if result_mode not in {"count", "rows"}:
        raise ValueError("result_mode must be 'count' or 'rows'")

    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    case = _load_rayjoin_case(workload, resolved_dataset)
    phases: dict[str, float] = {}
    rows: tuple[dict[str, object], ...] = ()
    native_phase_timings: dict[str, object] | None = None

    if workload == "lsi":
        from rtdsl.optix_runtime import pack_segments
        from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix

        packed_left = _phase_time(
            phases,
            "query_pack_sec",
            lambda: pack_segments(records=case.inputs["left"]),
        )
        prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_segment_pair_intersection_optix(case.inputs["right"]),
        )
        try:
            if result_mode == "count":
                row_count = int(_phase_time(phases, "prepared_query_sec", lambda: prepared.count(packed_left)))
            else:
                view = _phase_time(phases, "prepared_query_sec", lambda: prepared.run_raw(packed_left))
                try:
                    row_count = int(view.row_count)
                    if include_rows:
                        rows = tuple(view.to_dict_rows())
                finally:
                    view.close()
            native_phase_timings = prepared.last_phase_timings()
        finally:
            prepared.close()
        summary = {
            "intersection_count": row_count,
            "output_contract": (
                "segment_segment_intersection_count"
                if result_mode == "count"
                else "segment_segment_intersection_rows"
            ),
        }
    else:
        from rtdsl.optix_runtime import pack_points
        from rtdsl.optix_runtime import pack_polygons
        from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

        packed_points = _phase_time(
            phases,
            "query_pack_sec",
            lambda: pack_points(records=case.inputs["points"], dimension=2),
        )
        packed_shapes = _phase_time(
            phases,
            "static_shape_pack_sec",
            lambda: pack_polygons(records=case.inputs["polygons"]),
        )
        prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_point_closed_shape_membership_2d_optix(packed_shapes),
        )
        try:
            if result_mode == "count":
                row_count = int(_phase_time(phases, "prepared_query_sec", lambda: prepared.count(packed_points)))
            else:
                view = _phase_time(
                    phases,
                    "prepared_query_sec",
                    lambda: prepared.run_raw(packed_points, result_mode="positive_hits"),
                )
                try:
                    row_count = int(view.row_count)
                    if include_rows:
                        rows = tuple(view.to_dict_rows())
                finally:
                    view.close()
            native_phase_timings = prepared.last_phase_timings()
        finally:
            prepared.close()
        summary = {
            "positive_hit_row_count": row_count,
            "positive_assignment_count": row_count,
            "output_contract": (
                "point_to_shape_positive_hit_count"
                if result_mode == "count"
                else "point_to_shape_positive_hit_rows"
            ),
        }

    payload: dict[str, object] = {
        "app": "rayjoin_v2_spatial_join",
        "workload": workload,
        "execution_route": "prepared_optix",
        "backend": "optix",
        "dataset": resolved_dataset,
        "dataset_note": case.note,
        "result_mode": result_mode,
        "row_count": row_count,
        "summary": summary,
        "phases_sec": phases,
        "native_phase_timings": native_phase_timings or {},
        "device_resident_continuation_status": (
            "not_complete: prepared query can avoid Python row materialization for counts, "
            "but generic downstream row-stream continuation still needs pod/native work"
        ),
        "native_engine_boundary": (
            "The engine sees generic prepared point/closed-shape or segment-pair contracts. "
            "RayJoin application policy and paper-specific interpretation stay in Python."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
            "requires_pod_for_optix_perf": False,
        },
    }
    if include_rows and result_mode == "rows":
        payload["rows"] = rows
    return payload


def run_rayjoin_workload(
    workload: str,
    *,
    backend: str = "cpu_python_reference",
    dataset: str | None = None,
    include_rows: bool = True,
) -> dict[str, object]:
    if workload not in _WORKLOADS:
        raise ValueError("workload must be one of: pip, lsi, overlay_seed")
    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    baseline_workload = _BASELINE_WORKLOAD[workload]
    case = _load_rayjoin_case(workload, resolved_dataset)
    kernel = _KERNELS[workload]
    start = time.perf_counter()
    rows = _run_backend(kernel, backend, case.inputs)
    elapsed_sec = time.perf_counter() - start
    reference_rows = rows
    parity_vs_cpu_python_reference = True
    if backend != "cpu_python_reference":
        reference_rows = rt.run_cpu_python_reference(kernel, **case.inputs)
        parity_vs_cpu_python_reference = rt.compare_baseline_rows(
            baseline_workload,
            reference_rows,
            rows,
        )
    summary = _summarize_rows(workload, rows)
    payload: dict[str, object] = {
        "app": "rayjoin_v2_spatial_join",
        "workload": workload,
        "backend": backend,
        "dataset": resolved_dataset,
        "dataset_note": case.note,
        "elapsed_sec": elapsed_sec,
        "row_count": len(rows),
        "summary": summary,
        "parity_vs_cpu_python_reference": parity_vs_cpu_python_reference,
        "rt_core_accelerated": backend == "optix",
        "native_engine_boundary": (
            "The engine sees generic point, segment, polygon, traversal, and row contracts. "
            "RayJoin application policy, face metadata, PIP positive filtering, and overlay "
            "continuation stay in Python/partner code."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "v2_0_release_authorized": False,
            "requires_pod_for_optix_perf": backend != "optix",
        },
    }
    if include_rows:
        payload["rows"] = rows
    return payload


def run_rayjoin_suite(
    *,
    backend: str = "cpu_python_reference",
    execution_route: str = "generic_kernel",
    result_mode: str = "rows",
    include_rows: bool = True,
) -> dict[str, object]:
    if execution_route == "prepared_optix":
        workloads = {
            workload: run_rayjoin_prepared_optix_workload(
                workload,
                result_mode=result_mode,
                include_rows=include_rows,
            )
            for workload in _PREPARED_OPTIX_WORKLOADS
        }
        workloads["overlay_seed"] = {
            "app": "rayjoin_v2_spatial_join",
            "workload": "overlay_seed",
            "execution_route": "prepared_optix",
            "status": "not_supported_by_this_route",
            "reason": "overlay needs the generic dependency-row route or a future generic device-resident continuation",
        }
        return {
            "app": "rayjoin_v2_spatial_join",
            "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
            "backend": "optix",
            "execution_route": execution_route,
            "workloads": workloads,
            "all_match_cpu_python_reference": None,
            "implementation_stage": "prepared_v2_benchmark_route",
            "next_stage": (
                "Run this route on an RTX pod against RayJoin-exported streams and compare "
                "phase boundaries to RayJoin query_exec."
            ),
        }
    workloads = {
        workload: run_rayjoin_workload(
            workload,
            backend=backend,
            include_rows=include_rows,
        )
        for workload in _WORKLOADS
    }
    return {
        "app": "rayjoin_v2_spatial_join",
        "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
        "backend": backend,
        "execution_route": execution_route,
        "workloads": workloads,
        "all_match_cpu_python_reference": all(
            bool(row["parity_vs_cpu_python_reference"])
            for row in workloads.values()
        ),
        "implementation_stage": "first_v2_user_slice",
        "next_stage": (
            "Run the same suite on an OptiX pod, then promote the highest-value path "
            "from compatibility evidence into reviewed performance evidence."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run RTDL v2 RayJoin-style PIP, LSI, and overlay-seed workloads."
    )
    parser.add_argument(
        "--workload",
        choices=(*_WORKLOADS, "all"),
        default="all",
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix"),
        default="cpu_python_reference",
    )
    parser.add_argument(
        "--execution-route",
        choices=("generic_kernel", "prepared_optix"),
        default="generic_kernel",
        help="Use the generic kernel route or the prepared OptiX benchmark route for PIP/LSI.",
    )
    parser.add_argument(
        "--result-mode",
        choices=("rows", "count"),
        default="rows",
        help="For prepared_optix, return witness rows or scalar counts.",
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help="Override the default dataset for a single workload run.",
    )
    parser.add_argument(
        "--no-rows",
        action="store_true",
        help="Omit full row arrays and keep only summaries.",
    )
    args = parser.parse_args(argv)
    include_rows = not args.no_rows
    if args.workload == "all":
        if args.dataset is not None:
            raise ValueError("--dataset is only valid when --workload is not all")
        payload = run_rayjoin_suite(
            backend=args.backend,
            execution_route=args.execution_route,
            result_mode=args.result_mode,
            include_rows=include_rows,
        )
    else:
        if args.execution_route == "prepared_optix":
            payload = run_rayjoin_prepared_optix_workload(
                args.workload,
                dataset=args.dataset,
                result_mode=args.result_mode,
                include_rows=include_rows,
            )
        else:
            payload = run_rayjoin_workload(
                args.workload,
                backend=args.backend,
                dataset=args.dataset,
                include_rows=include_rows,
            )
    print(json.dumps(_json_ready(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
