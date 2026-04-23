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
    return {
        "approximate_row_count": len(rows),
        "query_count_with_candidate": len({int(row["query_id"]) for row in rows}),
        "max_neighbor_rank": max((int(row["neighbor_rank"]) for row in rows), default=0),
    }


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    output_mode: str = "full",
) -> dict[str, object]:
    if output_mode not in {"full", "rerank_summary", "quality_summary"}:
        raise ValueError("output_mode must be 'full', 'rerank_summary', or 'quality_summary'")
    case = make_ann_case(copies=copies)
    approximate_rows = _run_rows(backend, case)
    base_payload = {
        "app": "ann_candidate_search",
        "backend": backend,
        "k": K,
        "copies": copies,
        "output_mode": output_mode,
        "query_count": len(case["query_points"]),
        "search_count": len(case["search_points"]),
        "candidate_count": len(case["candidate_points"]),
        **_approximate_summary(approximate_rows),
        "rtdl_role": "RTDL emits k=1 nearest-neighbor rows for candidate-subset kNN reranking over a Python-selected candidate subset; Python evaluates approximation quality against exact search.",
        "optix_performance": _optix_performance(),
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
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
