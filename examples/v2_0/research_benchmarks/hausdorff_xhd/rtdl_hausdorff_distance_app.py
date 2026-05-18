from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.reference import Point


@rt.kernel(backend="rtdl", precision="float_approx")
def hausdorff_nearest_rows_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.knn_rows(k=1))
    return rt.emit(nearest, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def make_authored_point_sets(copies: int = 1) -> dict[str, tuple[Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_a = (
        Point(id=1, x=0.0, y=0.0),
        Point(id=2, x=1.0, y=0.0),
        Point(id=3, x=1.0, y=1.0),
        Point(id=4, x=0.0, y=1.0),
    )
    base_b = (
        Point(id=101, x=0.0, y=0.0),
        Point(id=102, x=1.2, y=0.1),
        Point(id=103, x=1.0, y=1.3),
        Point(id=104, x=-0.2, y=0.8),
    )

    points_a: list[Point] = []
    points_b: list[Point] = []
    for copy_index in range(copies):
        offset = 10.0 * copy_index
        id_offset = 1000 * copy_index
        for point in base_a:
            points_a.append(Point(id=point.id + id_offset, x=point.x + offset, y=point.y))
        for point in base_b:
            points_b.append(Point(id=point.id + id_offset, x=point.x + offset, y=point.y))
    return {"points_a": tuple(points_a), "points_b": tuple(points_b)}


def _run_nearest(backend: str, query_points: tuple[Point, ...], search_points: tuple[Point, ...]):
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "cpu":
        return rt.run_cpu(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "embree":
        return rt.run_embree(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "optix":
        return rt.run_optix(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "vulkan":
        return rt.run_vulkan(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("hausdorff_distance")
    return {"class": support.performance_class, "note": support.note}


def _enforce_rt_core_requirement(backend: str, optix_summary_mode: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    if optix_summary_mode != "directed_threshold_prepared":
        raise RuntimeError(
            "hausdorff_distance RT-core path requires --backend optix "
            "--optix-summary-mode directed_threshold_prepared"
        )


def _directed_from_rows(rows: Iterable[dict[str, object]], label: str) -> dict[str, object]:
    nearest_rows = list(rows)
    if not nearest_rows:
        raise ValueError(f"directed Hausdorff pass `{label}` produced no nearest-neighbor rows")

    distance_rows = rt.reduce_rows(
        nearest_rows,
        op="max",
        value="distance",
        output_field="directed_distance",
    )
    directed_distance = float(distance_rows[0]["directed_distance"])
    witness = max(
        nearest_rows,
        key=lambda row: (float(row["distance"]), -int(row["query_id"]), -int(row["neighbor_id"])),
    )
    return {
        "distance": directed_distance,
        "source_id": int(witness["query_id"]),
        "target_id": int(witness["neighbor_id"]),
        "row_count": len(nearest_rows),
        "distance_reduction_rows": distance_rows,
    }


def directed_hausdorff_bruteforce(source: tuple[Point, ...], target: tuple[Point, ...]) -> dict[str, object]:
    if not source or not target:
        raise ValueError("Hausdorff distance requires non-empty point sets")

    best_source: Point | None = None
    best_target: Point | None = None
    best_distance = -1.0
    for source_point in source:
        nearest_target = min(
            target,
            key=lambda target_point: (
                math.hypot(source_point.x - target_point.x, source_point.y - target_point.y),
                target_point.id,
            ),
        )
        distance = math.hypot(source_point.x - nearest_target.x, source_point.y - nearest_target.y)
        if (
            distance > best_distance
            or (math.isclose(distance, best_distance) and best_source is not None and source_point.id < best_source.id)
            or best_source is None
        ):
            best_source = source_point
            best_target = nearest_target
            best_distance = distance

    assert best_source is not None
    assert best_target is not None
    return {
        "distance": best_distance,
        "source_id": best_source.id,
        "target_id": best_target.id,
        "row_count": len(source),
    }


def brute_force_hausdorff(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    directed_ab = directed_hausdorff_bruteforce(points_a, points_b)
    directed_ba = directed_hausdorff_bruteforce(points_b, points_a)
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    return {
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
    }


def expected_tiled_hausdorff(*, copies: int) -> dict[str, object]:
    """Exact Hausdorff summary for make_authored_point_sets without O(N^2) expansion."""
    base = make_authored_point_sets(copies=1)
    expected = brute_force_hausdorff(base["points_a"], base["points_b"])
    expected = json.loads(json.dumps(expected))
    expected["directed_a_to_b"]["row_count"] = 4 * copies
    expected["directed_b_to_a"]["row_count"] = 4 * copies
    expected["directed_a_to_b"]["distance_reduction_rows"] = [
        {"directed_distance": expected["directed_a_to_b"]["distance"]}
    ]
    expected["directed_b_to_a"]["distance_reduction_rows"] = [
        {"directed_distance": expected["directed_b_to_a"]["distance"]}
    ]
    return expected


def _directed_threshold_from_count_rows(
    rows: Iterable[dict[str, object]],
    *,
    source: tuple[Point, ...],
    radius: float,
    label: str,
) -> dict[str, object]:
    by_query = {int(row["query_id"]): row for row in rows}
    violating = [
        point.id
        for point in source
        if int(by_query.get(point.id, {}).get("threshold_reached", 0)) == 0
    ]
    return {
        "label": label,
        "radius": radius,
        "source_count": len(source),
        "within_threshold": not violating,
        "violating_source_ids": violating,
        "row_count": len(by_query),
    }


def _run_prepared_directed_threshold(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    backend: str,
    radius: float,
    label: str,
) -> dict[str, object]:
    result = rt.run_generic_prepared_fixed_radius_threshold_reached_count_2d(
        search_points=target,
        query_points=source,
        radius=radius,
        threshold=1,
        backend=backend,
        max_radius=radius,
    )
    covered_count = int(result["threshold_reached_count"])
    run_phases = result["run_phases"]
    prepare_sec = float(run_phases["scene_prepare_sec"])
    query_sec = float(run_phases["query_fixed_radius_threshold_reached_count_sec"])
    violating = [] if covered_count == len(source) else None
    return {
        "label": label,
        "radius": radius,
        "source_count": len(source),
        "covered_source_count": covered_count,
        "within_threshold": covered_count == len(source),
        "violating_source_ids": violating,
        "identity_parity_available": violating is not None,
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
        "generic_primitive": result["primitive"],
        "summary_primitive": result["summary_primitive"],
        "run_phases": {
            "scene_prepare_sec": prepare_sec,
            "query_fixed_radius_threshold_reached_count_sec": query_sec,
        },
    }


def _native_continuation_backend(
    backend: str,
    *,
    embree_result_mode: str,
    optix_summary_mode: str,
) -> str:
    if backend == "optix" and optix_summary_mode == "directed_threshold_prepared":
        return "optix_threshold_count"
    if backend == "embree" and optix_summary_mode == "directed_threshold_prepared":
        return "embree_threshold_count"
    if backend == "embree" and embree_result_mode == "directed_summary":
        return "embree_directed_hausdorff"
    return "none"


def _run_partner_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    partner: str,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_partner_columns(source, partner=partner)
    target_columns = rt.point_rows_to_partner_columns(target, partner=partner)
    result = rt.directed_hausdorff_2d_partner_columns(
        source_columns,
        target_columns,
        partner=partner,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
    }


def _run_partner_numpy_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_numpy_columns(source)
    target_columns = rt.point_rows_to_numpy_columns(target)
    result = rt.directed_hausdorff_2d_numpy_columns(
        source_columns,
        target_columns,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
    }


def _run_partner_cupy_witness_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_partner_columns(source, partner="cupy")
    target_columns = rt.point_rows_to_partner_columns(target, partner="cupy")
    result = rt.directed_hausdorff_2d_cupy_columns(
        source_columns,
        target_columns,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
    }


def run_app(
    backend: str = "cpu_python_reference",
    copies: int = 1,
    *,
    embree_result_mode: str = "rows",
    optix_summary_mode: str = "rows",
    hausdorff_threshold: float = 0.4,
    require_rt_core: bool = False,
    partner: str = "cupy",
) -> dict[str, object]:
    input_start = time.perf_counter()
    case = make_authored_point_sets(copies=copies)
    run_phases: dict[str, float] = {"input_construction_sec": time.perf_counter() - input_start}
    points_a = case["points_a"]
    points_b = case["points_b"]
    if not points_a or not points_b:
        raise ValueError("Hausdorff distance requires non-empty point sets")
    if embree_result_mode not in {"rows", "directed_summary"}:
        raise ValueError("embree_result_mode must be 'rows' or 'directed_summary'")
    if optix_summary_mode not in {"rows", "directed_threshold_prepared"}:
        raise ValueError("optix_summary_mode must be 'rows' or 'directed_threshold_prepared'")
    if backend == "partner_exact" and partner not in {"torch", "cupy"}:
        raise ValueError("partner must be 'torch' or 'cupy'")
    if hausdorff_threshold < 0:
        raise ValueError("hausdorff_threshold must be non-negative")
    _enforce_rt_core_requirement(backend, optix_summary_mode, require_rt_core)
    native_continuation_backend = _native_continuation_backend(
        backend,
        embree_result_mode=embree_result_mode,
        optix_summary_mode=optix_summary_mode,
    )

    if backend == "partner_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_exact_directed(points_a, points_b, partner=partner, label="a_to_b")
        directed_ba = _run_partner_exact_directed(points_b, points_a, partner=partner, label="b_to_a")
        run_phases["partner_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": partner,
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2 partner exact mode converts Python point rows into generic partner "
                "point columns, computes nearest distance per source point, then reduces the "
                "nearest distances with max. The native engine is not app-customized."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_exact_directed_hausdorff_2d",
            "run_phases": run_phases,
        }

    if backend == "partner_numpy_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_numpy_exact_directed(points_a, points_b, label="a_to_b")
        directed_ba = _run_partner_numpy_exact_directed(points_b, points_a, label="b_to_a")
        run_phases["partner_numpy_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": "numpy",
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2 NumPy reference mode converts Python point rows into generic "
                "partner point columns, computes per-source nearest witnesses, and "
                "uses a generic group-argmin-then-global-argmax continuation. The "
                "native engine is not app-customized."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
            "run_phases": run_phases,
        }

    if backend == "partner_cupy_witness_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_cupy_witness_exact_directed(points_a, points_b, label="a_to_b")
        directed_ba = _run_partner_cupy_witness_exact_directed(points_b, points_a, label="b_to_a")
        run_phases["partner_cupy_witness_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": "cupy",
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2 CuPy witness mode converts Python point rows into generic "
                "partner device columns, computes per-source nearest witnesses, and "
                "uses the generic CuPy group-argmin-then-global-argmax continuation. "
                "The native engine is not app-customized."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
            "run_phases": run_phases,
        }

    if backend in {"embree", "optix"} and optix_summary_mode == "directed_threshold_prepared":
        directed_ab = _run_prepared_directed_threshold(
            points_a,
            points_b,
            backend=backend,
            radius=hausdorff_threshold,
            label="a_to_b",
        )
        directed_ba = _run_prepared_directed_threshold(
            points_b,
            points_a,
            backend=backend,
            radius=hausdorff_threshold,
            label="b_to_a",
        )
        run_phases["scene_prepare_sec"] = float(directed_ab["run_phases"]["scene_prepare_sec"]) + float(
            directed_ba["run_phases"]["scene_prepare_sec"]
        )
        run_phases["query_fixed_radius_threshold_reached_count_sec"] = float(
            directed_ab["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
        ) + float(
            directed_ba["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
        )
        postprocess_start = time.perf_counter()
        within_threshold = bool(directed_ab["within_threshold"] and directed_ba["within_threshold"])
        run_phases["python_postprocess_sec"] = time.perf_counter() - postprocess_start
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        oracle_within_threshold = float(oracle["hausdorff_distance"]) <= hausdorff_threshold + 1e-12
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": optix_summary_mode,
            "hausdorff_threshold": hausdorff_threshold,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": None,
            "within_threshold": within_threshold,
            "oracle": oracle,
            "oracle_within_threshold": oracle_within_threshold,
            "matches_oracle": within_threshold == oracle_within_threshold,
            "oracle_decision_matches": within_threshold == oracle_within_threshold,
            "oracle_identity_matches": (
                True
                if directed_ab["identity_parity_available"] and directed_ba["identity_parity_available"]
                else None
            ),
            "rtdl_role": (
                f"RTDL/{backend} uses prepared fixed-radius threshold traversal to answer "
                "the Hausdorff decision subproblem: every source point has at least "
                "one target within the threshold. Python combines the two directed "
                "decisions and validates against the deterministic oracle."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": native_continuation_backend != "none",
            "native_continuation_backend": native_continuation_backend,
            "rt_core_accelerated": backend == "optix",
            "run_phases": run_phases,
        }

    if backend == "embree" and embree_result_mode == "directed_summary":
        query_start = time.perf_counter()
        directed_ab = rt.directed_hausdorff_2d_embree(points_a, points_b)
        directed_ba = rt.directed_hausdorff_2d_embree(points_b, points_a)
        run_phases["native_directed_summary_sec"] = time.perf_counter() - query_start
        rtdl_role = (
            "RTDL/Embree runs k=1 nearest-neighbor traversal and directed max reduction "
            "inside the native Embree summary path; Python keeps only undirected comparison "
            "and oracle validation."
        )
    elif embree_result_mode == "directed_summary":
        query_start = time.perf_counter()
        oracle_summary = expected_tiled_hausdorff(copies=copies)
        run_phases["analytic_summary_sec"] = time.perf_counter() - query_start
        directed_ab = oracle_summary["directed_a_to_b"]
        directed_ba = oracle_summary["directed_b_to_a"]
        rtdl_role = (
            "Compact CPU/reference mode uses the exact deterministic tiled-fixture Hausdorff "
            "summary so large app-level Embree comparisons do not spend time in an O(N^2) oracle."
        )
    else:
        query_start = time.perf_counter()
        rows_ab = _run_nearest(backend, points_a, points_b)
        rows_ba = _run_nearest(backend, points_b, points_a)
        run_phases["query_and_materialize_sec"] = time.perf_counter() - query_start
        reduction_start = time.perf_counter()
        directed_ab = _directed_from_rows(rows_ab, "a_to_b")
        directed_ba = _directed_from_rows(rows_ba, "b_to_a")
        run_phases["python_reduction_sec"] = time.perf_counter() - reduction_start
        rtdl_role = (
            "RTDL emits k=1 nearest-neighbor rows; rt.reduce_rows(max) computes directed "
            "Hausdorff distances, while Python keeps witness selection and undirected comparison."
        )
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    validation_start = time.perf_counter()
    oracle = (
        expected_tiled_hausdorff(copies=copies)
        if embree_result_mode == "directed_summary"
        else brute_force_hausdorff(points_a, points_b)
    )
    run_phases["validation_sec"] = time.perf_counter() - validation_start

    return {
        "app": "hausdorff_distance",
        "backend": backend,
        "partner": None,
        "copies": copies,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "embree_result_mode": embree_result_mode if backend == "embree" else None,
        "optix_summary_mode": optix_summary_mode if backend == "optix" else None,
        "hausdorff_threshold": None,
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
        "oracle": oracle,
        "matches_oracle": math.isclose(
            float(undirected[1]["distance"]),
            float(oracle["hausdorff_distance"]),
            rel_tol=1e-5,
            abs_tol=1e-5,
        ),
        "rtdl_role": rtdl_role,
        "optix_performance": _optix_performance(),
        "native_continuation_active": native_continuation_backend != "none",
        "native_continuation_backend": native_continuation_backend,
        "rt_core_accelerated": False,
        "run_phases": run_phases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived Hausdorff distance app: RTDL nearest-neighbor rows plus Python reduction."
    )
    parser.add_argument(
        "--backend",
        choices=(
            "cpu_python_reference",
            "cpu",
            "embree",
            "optix",
            "vulkan",
            "partner_exact",
            "partner_numpy_exact",
            "partner_cupy_witness_exact",
        ),
        default="cpu_python_reference",
    )
    parser.add_argument("--partner", choices=("torch", "cupy"), default="cupy")
    parser.add_argument("--copies", type=int, default=1, help="tile the small authored point sets")
    parser.add_argument(
        "--embree-result-mode",
        choices=("rows", "directed_summary"),
        default="rows",
        help="Embree-only: emit KNN rows or native directed-Hausdorff summaries",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "directed_threshold_prepared"),
        default="rows",
        help="OptiX-only: use prepared fixed-radius threshold traversal for Hausdorff <= radius decisions",
    )
    parser.add_argument(
        "--hausdorff-threshold",
        type=float,
        default=0.4,
        help="Decision radius for --optix-summary-mode directed_threshold_prepared",
    )
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                args.copies,
                embree_result_mode=args.embree_result_mode,
                optix_summary_mode=args.optix_summary_mode,
                hausdorff_threshold=args.hausdorff_threshold,
                require_rt_core=args.require_rt_core,
                partner=args.partner,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
