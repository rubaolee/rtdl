from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


K = 1


@rt.kernel(backend="rtdl", precision="float_approx")
def ann_candidate_rows_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    candidate_points = rt.input("candidate_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, candidate_points, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.knn_rows(k=K))
    return rt.emit(nearest, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def make_ann_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_search = (
        rt.Point(id=101, x=0.00, y=0.00),
        rt.Point(id=102, x=0.12, y=0.00),
        rt.Point(id=103, x=5.00, y=5.00),
        rt.Point(id=104, x=5.20, y=5.00),
        rt.Point(id=105, x=10.00, y=0.00),
        rt.Point(id=106, x=10.50, y=0.00),
    )
    base_queries = (
        rt.Point(id=1, x=0.05, y=0.00),
        rt.Point(id=2, x=5.18, y=5.00),
        rt.Point(id=3, x=10.10, y=0.00),
    )
    representative_ids = {101, 103, 105}

    search_points: list[rt.Point] = []
    query_points: list[rt.Point] = []
    candidate_points: list[rt.Point] = []
    for copy_index in range(copies):
        id_offset = 1000 * copy_index
        x_offset = 12.0 * copy_index
        for point in base_search:
            copied = rt.Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y)
            search_points.append(copied)
            if point.id in representative_ids:
                candidate_points.append(copied)
        for point in base_queries:
            query_points.append(rt.Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))

    return {
        "query_points": tuple(query_points),
        "search_points": tuple(search_points),
        "candidate_points": tuple(candidate_points),
    }


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    inputs = {"query_points": case["query_points"], "candidate_points": case["candidate_points"]}
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(ann_candidate_rows_kernel, **inputs))
    if backend == "cpu":
        return tuple(rt.run_cpu(ann_candidate_rows_kernel, **inputs))
    if backend == "embree":
        return tuple(rt.run_embree(ann_candidate_rows_kernel, **inputs))
    if backend == "optix":
        return tuple(rt.run_optix(ann_candidate_rows_kernel, **inputs))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(ann_candidate_rows_kernel, **inputs))
    if backend == "scipy":
        return tuple(rt.run_scipy_knn_rows(case["query_points"], case["candidate_points"], k=K))
    raise ValueError(f"unsupported backend `{backend}`")


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("ann_candidate_search")
    return {"class": support.performance_class, "note": support.note}


def _enforce_rt_core_requirement(backend: str, optix_summary_mode: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    if optix_summary_mode != "candidate_threshold_prepared":
        raise RuntimeError(
            "ann_candidate_search RT-core path requires --backend optix "
            "--optix-summary-mode candidate_threshold_prepared"
        )


def exact_knn_rows(
    query_points: tuple[rt.Point, ...],
    search_points: tuple[rt.Point, ...],
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in query_points:
        distance, neighbor_id = min(
            (
                (math.hypot(query.x - search.x, query.y - search.y), search.id)
                for search in search_points
            ),
            key=lambda item: (item[0], item[1]),
        )
        rows.append(
            {
                "query_id": query.id,
                "neighbor_id": neighbor_id,
                "distance": distance,
                "neighbor_rank": 1,
            }
        )
    return tuple(sorted(rows, key=lambda row: int(row["query_id"])))


def _rows_by_query(rows: tuple[dict[str, object], ...]) -> dict[int, dict[str, object]]:
    return {int(row["query_id"]): row for row in rows}


def evaluate_approximation(
    approximate_rows: tuple[dict[str, object], ...],
    exact_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    approximate_by_query = _rows_by_query(approximate_rows)
    exact_by_query = _rows_by_query(exact_rows)
    exact_hits = 0
    distance_ratios: list[float] = []
    comparison_rows: list[dict[str, object]] = []
    for query_id in sorted(exact_by_query):
        exact = exact_by_query[query_id]
        approximate = approximate_by_query[query_id]
        exact_distance = float(exact["distance"])
        approximate_distance = float(approximate["distance"])
        exact_match = int(approximate["neighbor_id"]) == int(exact["neighbor_id"])
        if exact_match:
            exact_hits += 1
        ratio = 1.0 if exact_distance == 0.0 else approximate_distance / exact_distance
        distance_ratios.append(ratio)
        comparison_rows.append(
            {
                "query_id": query_id,
                "approx_neighbor_id": int(approximate["neighbor_id"]),
                "exact_neighbor_id": int(exact["neighbor_id"]),
                "approx_distance": approximate_distance,
                "exact_distance": exact_distance,
                "exact_match": exact_match,
                "distance_ratio": ratio,
            }
        )

    return {
        "exact_match_count": exact_hits,
        "query_count": len(exact_rows),
        "recall_at_1": exact_hits / len(exact_rows) if exact_rows else 0.0,
        "mean_distance_ratio": sum(distance_ratios) / len(distance_ratios) if distance_ratios else 0.0,
        "comparison_rows": tuple(comparison_rows),
    }


def _approximate_summary(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    return rt.summarize_knn_rows(rows)


def candidate_threshold_oracle(
    query_points: tuple[rt.Point, ...],
    candidate_points: tuple[rt.Point, ...],
    *,
    radius: float,
) -> dict[str, object]:
    uncovered: list[int] = []
    for query in query_points:
        has_candidate = any(
            math.hypot(query.x - candidate.x, query.y - candidate.y) <= radius
            for candidate in candidate_points
        )
        if not has_candidate:
            uncovered.append(query.id)
    return {
        "radius": radius,
        "query_count": len(query_points),
        "covered_query_count": len(query_points) - len(uncovered),
        "within_candidate_radius": not uncovered,
        "uncovered_query_ids": uncovered,
    }


def expected_tiled_candidate_threshold(*, copies: int, radius: float) -> dict[str, object]:
    """Exact threshold summary for make_ann_case without cross-copy expansion."""
    if copies < 1:
        raise ValueError("copies must be at least 1")
    base = make_ann_case(copies=1)
    base_oracle = candidate_threshold_oracle(
        base["query_points"],
        base["candidate_points"],
        radius=radius,
    )
    base_uncovered = tuple(int(query_id) for query_id in base_oracle["uncovered_query_ids"])
    uncovered: list[int] = []
    for copy_index in range(copies):
        id_offset = 1000 * copy_index
        uncovered.extend(query_id + id_offset for query_id in base_uncovered)
    query_count = int(base_oracle["query_count"]) * copies
    return {
        "radius": radius,
        "query_count": query_count,
        "covered_query_count": query_count - len(uncovered),
        "within_candidate_radius": not uncovered,
        "uncovered_query_ids": uncovered,
    }


def _candidate_threshold_from_count_rows(
    rows: tuple[dict[str, object], ...],
    *,
    query_points: tuple[rt.Point, ...],
    radius: float,
) -> dict[str, object]:
    by_query = {int(row["query_id"]): row for row in rows}
    uncovered = [
        query.id
        for query in query_points
        if int(by_query.get(query.id, {}).get("threshold_reached", 0)) == 0
    ]
    return {
        "radius": radius,
        "query_count": len(query_points),
        "covered_query_count": len(query_points) - len(uncovered),
        "within_candidate_radius": not uncovered,
        "uncovered_query_ids": uncovered,
        "row_count": len(by_query),
    }


def _run_optix_candidate_threshold(
    case: dict[str, tuple[rt.Point, ...]],
    *,
    radius: float,
) -> dict[str, object]:
    with rt.prepare_optix_fixed_radius_count_threshold_2d(case["candidate_points"], max_radius=radius) as prepared:
        covered_count = prepared.count_threshold_reached(case["query_points"], radius=radius, threshold=1)
    within_candidate_radius = int(covered_count) == len(case["query_points"])
    return {
        "radius": radius,
        "query_count": len(case["query_points"]),
        "covered_query_count": int(covered_count),
        "within_candidate_radius": within_candidate_radius,
        "uncovered_query_ids": [] if within_candidate_radius else None,
        "identity_parity_available": within_candidate_radius,
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
    }


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    output_mode: str = "full",
    optix_summary_mode: str = "rows",
    candidate_radius: float = 0.2,
    require_rt_core: bool = False,
) -> dict[str, object]:
    if output_mode not in {"full", "rerank_summary", "quality_summary"}:
        raise ValueError("output_mode must be 'full', 'rerank_summary', or 'quality_summary'")
    if optix_summary_mode not in {"rows", "candidate_threshold_prepared"}:
        raise ValueError("optix_summary_mode must be 'rows' or 'candidate_threshold_prepared'")
    if candidate_radius < 0:
        raise ValueError("candidate_radius must be non-negative")
    _enforce_rt_core_requirement(backend, optix_summary_mode, require_rt_core)
    case = make_ann_case(copies=copies)
    if backend == "optix" and optix_summary_mode == "candidate_threshold_prepared":
        coverage = _run_optix_candidate_threshold(case, radius=candidate_radius)
        oracle = candidate_threshold_oracle(
            case["query_points"],
            case["candidate_points"],
            radius=candidate_radius,
        )
        return {
            "app": "ann_candidate_search",
            "backend": backend,
            "k": K,
            "copies": copies,
            "output_mode": output_mode,
            "optix_summary_mode": optix_summary_mode,
            "candidate_radius": candidate_radius,
            "query_count": len(case["query_points"]),
            "search_count": len(case["search_points"]),
            "candidate_count": len(case["candidate_points"]),
            "candidate_threshold": coverage,
            "oracle_candidate_threshold": oracle,
            "matches_oracle": coverage["within_candidate_radius"] == oracle["within_candidate_radius"],
            "oracle_decision_matches": coverage["within_candidate_radius"] == oracle["within_candidate_radius"],
            "oracle_identity_matches": (
                coverage["uncovered_query_ids"] == oracle["uncovered_query_ids"]
                if coverage["identity_parity_available"]
                else None
            ),
            "rtdl_role": (
                "RTDL/OptiX uses prepared fixed-radius threshold traversal to answer "
                "the bounded ANN candidate-coverage decision: every query has at "
                "least one Python-selected candidate within the acceptance radius."
            ),
            "optix_performance": _optix_performance(),
            "rt_core_accelerated": True,
            "boundary": (
                "Candidate-threshold decision only; this is not a full ANN index, "
                "not nearest-neighbor ranking, and not a recall/latency optimizer. "
                "Python still owns candidate-set construction and any quality policy."
            ),
        }

    approximate_rows = _run_rows(backend, case)
    base_payload = {
        "app": "ann_candidate_search",
        "backend": backend,
        "k": K,
        "copies": copies,
        "optix_summary_mode": optix_summary_mode if backend == "optix" else None,
        "candidate_radius": None,
        "output_mode": output_mode,
        "query_count": len(case["query_points"]),
        "search_count": len(case["search_points"]),
        "candidate_count": len(case["candidate_points"]),
        **_approximate_summary(approximate_rows),
        "native_continuation_active": True,
        "native_continuation_backend": "oracle_cpp",
        "rtdl_role": "RTDL emits k=1 nearest-neighbor rows for candidate-subset kNN reranking over a Python-selected candidate subset; Python evaluates approximation quality against exact search.",
        "optix_performance": _optix_performance(),
        "rt_core_accelerated": False,
        "boundary": "Bounded ANN candidate-search demo only; RTDL does not yet provide an ANN index, training phase, or recall/latency optimizer. rerank_summary measures only the RTDL candidate-subset KNN reranking slice; full quality evaluation still uses Python exact full-set comparison.",
    }
    if output_mode == "rerank_summary":
        return base_payload

    exact_rows = exact_knn_rows(case["query_points"], case["search_points"])
    evaluation = evaluate_approximation(approximate_rows, exact_rows)
    if output_mode == "quality_summary":
        return {**base_payload, **{key: value for key, value in evaluation.items() if key != "comparison_rows"}}

    return {
        **base_payload,
        "approximate_rows": approximate_rows,
        "exact_rows": exact_rows,
        **evaluation,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived ANN candidate-search app: RTDL kNN over a Python-selected approximate candidate set."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument(
        "--output-mode",
        choices=("full", "rerank_summary", "quality_summary"),
        default="full",
        help="choose full quality rows, RTDL candidate-rerank summary, or compact quality metrics",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "candidate_threshold_prepared"),
        default="rows",
        help="OptiX-only: use prepared fixed-radius threshold traversal for candidate-coverage decisions",
    )
    parser.add_argument(
        "--candidate-radius",
        type=float,
        default=0.2,
        help="acceptance radius for --optix-summary-mode candidate_threshold_prepared",
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
                copies=args.copies,
                output_mode=args.output_mode,
                optix_summary_mode=args.optix_summary_mode,
                candidate_radius=args.candidate_radius,
                require_rt_core=args.require_rt_core,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
