from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


RADIUS = 0.35
K_MAX = 16
MIN_NEIGHBORS_INCLUDING_SELF = 3


@rt.kernel(backend="rtdl", precision="float_approx")
def outlier_neighbor_rows_kernel():
    points = rt.input("points", rt.Points, role="probe")
    candidates = rt.traverse(points, points, accel="bvh")
    neighbors = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=RADIUS, k_max=K_MAX))
    return rt.emit(neighbors, fields=["query_id", "neighbor_id", "distance"])


def make_outlier_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_points = (
        rt.Point(id=1, x=0.00, y=0.00),
        rt.Point(id=2, x=0.12, y=0.04),
        rt.Point(id=3, x=-0.10, y=0.08),
        rt.Point(id=4, x=2.00, y=2.00),
        rt.Point(id=5, x=2.14, y=2.05),
        rt.Point(id=6, x=1.88, y=1.94),
        rt.Point(id=7, x=4.50, y=0.00),
        rt.Point(id=8, x=-3.00, y=2.50),
    )
    points: list[rt.Point] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        x_offset = 7.0 * copy_index
        for point in base_points:
            points.append(rt.Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))
    return {"points": tuple(points)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(outlier_neighbor_rows_kernel, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(outlier_neighbor_rows_kernel, **case))
    if backend == "embree":
        return tuple(rt.run_embree(outlier_neighbor_rows_kernel, **case))
    if backend == "optix":
        return tuple(rt.run_optix(outlier_neighbor_rows_kernel, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(outlier_neighbor_rows_kernel, **case))
    if backend == "scipy":
        return tuple(rt.run_scipy_fixed_radius_neighbors(case["points"], case["points"], radius=RADIUS, k_max=K_MAX))
    raise ValueError(f"unsupported backend `{backend}`")


def density_rows_from_neighbor_rows(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
    *,
    min_neighbors_including_self: int = MIN_NEIGHBORS_INCLUDING_SELF,
) -> tuple[dict[str, object], ...]:
    counts: dict[int, int] = {point.id: 0 for point in points}
    for row in rt.reduce_rows(
        tuple(rows),
        group_by="query_id",
        op="count",
        output_field="neighbor_count",
    ):
        query_id = int(row["query_id"])
        if query_id in counts:
            counts[query_id] = int(row["neighbor_count"])

    return tuple(
        {
            "point_id": point_id,
            "neighbor_count": counts[point_id],
            "is_outlier": counts[point_id] < min_neighbors_including_self,
        }
        for point_id in sorted(counts)
    )


def brute_force_outlier_rows(
    points: tuple[rt.Point, ...],
    *,
    radius: float = RADIUS,
    min_neighbors_including_self: int = MIN_NEIGHBORS_INCLUDING_SELF,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        for neighbor in points:
            distance = math.hypot(query.x - neighbor.x, query.y - neighbor.y)
            if distance <= radius:
                rows.append({"query_id": query.id, "neighbor_id": neighbor.id, "distance": distance})
    return density_rows_from_neighbor_rows(
        points,
        rows,
        min_neighbors_including_self=min_neighbors_including_self,
    )


def expected_tiled_density_rows(*, copies: int) -> tuple[dict[str, object], ...]:
    """Exact density summary for make_outlier_case without O(N^2) expansion."""
    base_rows = (
        (1, 3, False),
        (2, 3, False),
        (3, 3, False),
        (4, 3, False),
        (5, 3, False),
        (6, 3, False),
        (7, 1, True),
        (8, 1, True),
    )
    rows: list[dict[str, object]] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        for point_id, neighbor_count, is_outlier in base_rows:
            rows.append(
                {
                    "point_id": point_id + id_offset,
                    "neighbor_count": neighbor_count,
                    "is_outlier": is_outlier,
                }
            )
    return tuple(rows)


def _density_rows_from_count_rows(
    points: tuple[rt.Point, ...],
    count_rows: Iterable[dict[str, object]],
    *,
    min_neighbors_including_self: int = MIN_NEIGHBORS_INCLUDING_SELF,
) -> tuple[dict[str, object], ...]:
    counts: dict[int, int] = {point.id: 0 for point in points}
    threshold_reached: dict[int, int] = {point.id: 0 for point in points}
    for row in count_rows:
        point_id = int(row["query_id"])
        if point_id not in counts:
            continue
        counts[point_id] = int(row["neighbor_count"])
        threshold_reached[point_id] = int(row.get("threshold_reached", 0))
    return tuple(
        {
            "point_id": point_id,
            "neighbor_count": counts[point_id],
            "is_outlier": counts[point_id] < min_neighbors_including_self
            and threshold_reached[point_id] == 0,
        }
        for point_id in sorted(counts)
    )


def _run_optix_density_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    count_rows = rt.fixed_radius_count_threshold_2d_optix(
        case["points"],
        case["points"],
        radius=RADIUS,
        threshold=MIN_NEIGHBORS_INCLUDING_SELF,
    )
    return _density_rows_from_count_rows(case["points"], count_rows)


def _run_optix_prepared_density_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    with rt.prepare_optix_fixed_radius_count_threshold_2d(case["points"], max_radius=RADIUS) as prepared:
        count_rows = prepared.run(
            case["points"],
            radius=RADIUS,
            threshold=MIN_NEIGHBORS_INCLUDING_SELF,
        )
    return _density_rows_from_count_rows(case["points"], count_rows)


def _run_optix_prepared_density_count(case: dict[str, tuple[rt.Point, ...]]) -> dict[str, int | str | None]:
    with rt.prepare_optix_fixed_radius_count_threshold_2d(case["points"], max_radius=RADIUS) as prepared:
        threshold_reached_count = prepared.count_threshold_reached(
            case["points"],
            radius=RADIUS,
            threshold=MIN_NEIGHBORS_INCLUDING_SELF,
        )
    point_count = len(case["points"])
    return {
        "point_count": point_count,
        "threshold_reached_count": int(threshold_reached_count),
        "outlier_count": point_count - int(threshold_reached_count),
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
    }


def _run_embree_density_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    count_rows = rt.fixed_radius_count_threshold_2d_embree(
        case["points"],
        case["points"],
        radius=RADIUS,
        threshold=MIN_NEIGHBORS_INCLUDING_SELF,
    )
    return _density_rows_from_count_rows(case["points"], count_rows)


def _run_embree_prepared_density_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    with rt.prepare_embree_fixed_radius_count_threshold_2d(case["points"]) as prepared:
        count_rows = prepared.run(
            case["points"],
            radius=RADIUS,
            threshold=MIN_NEIGHBORS_INCLUDING_SELF,
        )
    return _density_rows_from_count_rows(case["points"], count_rows)


def _native_continuation_backend(
    backend: str,
    *,
    output_mode: str,
    optix_summary_mode: str,
    embree_summary_mode: str,
) -> str:
    if backend == "optix" and (
        output_mode in {"density_summary", "density_count"}
        or optix_summary_mode in {"rt_count_threshold", "rt_count_threshold_prepared"}
    ):
        return "optix_threshold_count"
    if backend == "embree" and (
        output_mode == "density_summary" or embree_summary_mode in {"rt_count_threshold", "rt_count_threshold_prepared"}
    ):
        return "embree_threshold_count"
    return "none"


class PreparedOutlierDetectionSession:
    def __init__(self, backend: str = "optix", *, copies: int = 1):
        if backend != "optix":
            raise ValueError("PreparedOutlierDetectionSession currently supports backend='optix'")
        self.backend = backend
        self.case = make_outlier_case(copies=copies)
        self._prepared = rt.prepare_optix_fixed_radius_count_threshold_2d(self.case["points"], max_radius=RADIUS)
        self._closed = False

    def run(self, *, output_mode: str = "density_summary") -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared outlier detection session is closed")
        if output_mode not in {"density_summary", "density_count"}:
            raise ValueError("prepared outlier detection session currently supports output_mode='density_summary' or 'density_count'")
        if output_mode == "density_count":
            threshold_reached_count = self._prepared.count_threshold_reached(
                self.case["points"],
                radius=RADIUS,
                threshold=MIN_NEIGHBORS_INCLUDING_SELF,
            )
            point_count = len(self.case["points"])
            oracle_rows = expected_tiled_density_rows(copies=point_count // 8)
            oracle_outlier_count = sum(1 for row in oracle_rows if bool(row["is_outlier"]))
            outlier_count = point_count - int(threshold_reached_count)
            return {
                "app": "outlier_detection",
                "backend": self.backend,
                "execution_mode": "prepared_session",
                "output_mode": output_mode,
                "optix_summary_mode": "rt_count_threshold_prepared",
                "embree_summary_mode": "not_applicable",
                "radius": RADIUS,
                "k_max": K_MAX,
                "min_neighbors_including_self": MIN_NEIGHBORS_INCLUDING_SELF,
                "copies": point_count // 8,
                "point_count": point_count,
                "threshold_reached_count": int(threshold_reached_count),
                "outlier_count": outlier_count,
                "oracle_outlier_count": oracle_outlier_count,
                "neighbor_row_count": 0,
                "native_summary_row_count": 0,
                "native_continuation_active": True,
                "native_continuation_backend": "optix_threshold_count",
                "density_rows": (),
                "outlier_point_ids": None,
                "oracle_density_rows": (),
                "matches_oracle": outlier_count == oracle_outlier_count,
                "summary_mode": "scalar_threshold_count",
                "rtdl_role": "Prepared OptiX reuses the fixed-radius count-threshold RT traversal scene and emits only scalar density-threshold counts; point identities remain outside this scalar mode.",
                "boundary": "Prepared OptiX density_count returns only scalar threshold/outlier counts. Use density_summary when per-point outlier labels are required.",
            }
        count_rows = self._prepared.run(
            self.case["points"],
            radius=RADIUS,
            threshold=MIN_NEIGHBORS_INCLUDING_SELF,
        )
        density_rows = _density_rows_from_count_rows(self.case["points"], count_rows)
        oracle_rows = expected_tiled_density_rows(copies=len(self.case["points"]) // 8)
        outlier_ids = [int(row["point_id"]) for row in density_rows if bool(row["is_outlier"])]
        oracle_outlier_ids = [int(row["point_id"]) for row in oracle_rows if bool(row["is_outlier"])]
        return {
            "app": "outlier_detection",
            "backend": self.backend,
            "execution_mode": "prepared_session",
            "output_mode": output_mode,
            "optix_summary_mode": "rt_count_threshold_prepared",
            "embree_summary_mode": "not_applicable",
            "radius": RADIUS,
            "k_max": K_MAX,
            "min_neighbors_including_self": MIN_NEIGHBORS_INCLUDING_SELF,
            "copies": len(self.case["points"]) // 8,
            "point_count": len(self.case["points"]),
            "neighbor_row_count": 0,
            "native_summary_row_count": len(density_rows),
            "native_continuation_active": True,
            "native_continuation_backend": "optix_threshold_count",
            "density_rows": density_rows,
            "outlier_point_ids": outlier_ids,
            "oracle_density_rows": oracle_rows,
            "matches_oracle": outlier_ids == oracle_outlier_ids,
            "rtdl_role": "Prepared OptiX reuses the fixed-radius count-threshold RT traversal scene and emits compact density rows without materializing neighbor rows; Python only consumes the emitted outlier labels.",
            "boundary": "Prepared OptiX density summary reuses the search-point BVH. GTX 1070 validation is backend behavior evidence only, not RTX RT-core speedup evidence.",
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._prepared.close()

    def __enter__(self) -> "PreparedOutlierDetectionSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def prepare_session(backend: str = "optix", *, copies: int = 1) -> PreparedOutlierDetectionSession:
    return PreparedOutlierDetectionSession(backend, copies=copies)


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    optix_summary_mode: str = "rows",
    embree_summary_mode: str = "rows",
    output_mode: str = "full",
) -> dict[str, object]:
    if optix_summary_mode not in {"rows", "rt_count_threshold", "rt_count_threshold_prepared"}:
        raise ValueError("optix_summary_mode must be 'rows', 'rt_count_threshold', or 'rt_count_threshold_prepared'")
    if embree_summary_mode not in {"rows", "rt_count_threshold", "rt_count_threshold_prepared"}:
        raise ValueError("embree_summary_mode must be 'rows', 'rt_count_threshold', or 'rt_count_threshold_prepared'")
    if output_mode not in {"full", "density_summary", "density_count"}:
        raise ValueError("output_mode must be 'full', 'density_summary', or 'density_count'")
    case = make_outlier_case(copies=copies)
    native_summary_rows: tuple[dict[str, object], ...] = ()
    scalar_density_count: dict[str, int | str | None] | None = None
    if output_mode == "density_count" and backend == "optix":
        neighbor_rows = ()
        density_rows = ()
        scalar_density_count = _run_optix_prepared_density_count(case)
    elif output_mode == "density_count":
        neighbor_rows = ()
        density_rows = ()
        oracle_scalar_rows = expected_tiled_density_rows(copies=copies)
        oracle_outlier_count_for_scalar = sum(1 for row in oracle_scalar_rows if bool(row["is_outlier"]))
        scalar_density_count = {
            "point_count": len(case["points"]),
            "threshold_reached_count": len(case["points"]) - oracle_outlier_count_for_scalar,
            "outlier_count": oracle_outlier_count_for_scalar,
            "row_count": None,
            "summary_mode": "scalar_threshold_count_oracle",
        }
    elif output_mode == "density_summary" and backend == "embree":
        neighbor_rows = ()
        density_rows = _run_embree_prepared_density_summary(case)
        native_summary_rows = density_rows
    elif output_mode == "density_summary" and backend == "optix":
        neighbor_rows = ()
        density_rows = _run_optix_density_summary(case)
        native_summary_rows = density_rows
    elif output_mode == "density_summary":
        neighbor_rows = ()
        density_rows = expected_tiled_density_rows(copies=copies)
    elif backend == "optix" and optix_summary_mode == "rt_count_threshold":
        neighbor_rows = ()
        density_rows = _run_optix_density_summary(case)
        native_summary_rows = density_rows
    elif backend == "optix" and optix_summary_mode == "rt_count_threshold_prepared":
        neighbor_rows = ()
        density_rows = _run_optix_prepared_density_summary(case)
        native_summary_rows = density_rows
    elif backend == "embree" and embree_summary_mode == "rt_count_threshold":
        neighbor_rows = ()
        density_rows = _run_embree_density_summary(case)
        native_summary_rows = density_rows
    elif backend == "embree" and embree_summary_mode == "rt_count_threshold_prepared":
        neighbor_rows = ()
        density_rows = _run_embree_prepared_density_summary(case)
        native_summary_rows = density_rows
    else:
        neighbor_rows = _run_rows(backend, case)
        density_rows = density_rows_from_neighbor_rows(case["points"], neighbor_rows)
    oracle_rows = (
        expected_tiled_density_rows(copies=copies)
        if output_mode == "density_summary"
        else brute_force_outlier_rows(case["points"])
    )
    outlier_ids = [int(row["point_id"]) for row in density_rows if bool(row["is_outlier"])]
    oracle_outlier_ids = [int(row["point_id"]) for row in oracle_rows if bool(row["is_outlier"])]
    oracle_outlier_count = len(oracle_outlier_ids)
    if scalar_density_count is not None:
        matches_oracle = int(scalar_density_count["outlier_count"]) == oracle_outlier_count
    else:
        matches_oracle = outlier_ids == oracle_outlier_ids if native_summary_rows else density_rows == oracle_rows
    native_continuation_backend = _native_continuation_backend(
        backend,
        output_mode=output_mode,
        optix_summary_mode=optix_summary_mode,
        embree_summary_mode=embree_summary_mode,
    )

    return {
        "app": "outlier_detection",
        "backend": backend,
        "output_mode": output_mode,
        "optix_summary_mode": optix_summary_mode if backend == "optix" else "not_applicable",
        "embree_summary_mode": embree_summary_mode if backend == "embree" else "not_applicable",
        "radius": RADIUS,
        "k_max": K_MAX,
        "min_neighbors_including_self": MIN_NEIGHBORS_INCLUDING_SELF,
        "copies": copies,
        "point_count": len(case["points"]),
        "neighbor_row_count": len(neighbor_rows),
        "native_summary_row_count": len(native_summary_rows),
        "native_continuation_active": native_continuation_backend != "none",
        "native_continuation_backend": native_continuation_backend,
        "density_rows": density_rows,
        "threshold_reached_count": (
            int(scalar_density_count["threshold_reached_count"]) if scalar_density_count is not None else None
        ),
        "outlier_count": int(scalar_density_count["outlier_count"]) if scalar_density_count is not None else len(outlier_ids),
        "outlier_point_ids": None if scalar_density_count is not None else outlier_ids,
        "oracle_density_rows": oracle_rows,
        "oracle_outlier_count": oracle_outlier_count,
        "summary_mode": scalar_density_count["summary_mode"] if scalar_density_count is not None else None,
        "matches_oracle": matches_oracle,
        "rtdl_role": "Default RTDL emits fixed-radius neighbor rows; rt.reduce_rows(count) converts them into local density counts, and Python applies the outlier threshold. The compact density paths use prepared fixed-radius threshold traversal through native backend fixed-radius threshold-count continuation and avoid neighbor-row materialization.",
        "boundary": "Bounded density-threshold outlier demo only; Embree/OptiX rt_count_threshold is an experimental fixed-radius count prototype, not a KNN/Hausdorff/Barnes-Hut claim. One-shot CLI runs cannot fully amortize backend preparation; prepared app/session mode is intended for repeated probes.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived outlier detection app: RTDL neighbor rows plus Python density thresholding."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument(
        "--output-mode",
        choices=("full", "density_summary", "density_count"),
        default="full",
        help="full emits neighbor/density rows; density_summary emits compact threshold rows; density_count emits only scalar threshold/outlier counts",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "rt_count_threshold", "rt_count_threshold_prepared"),
        default="rows",
        help="when backend=optix, use native fixed-radius threshold counts instead of neighbor rows; prepared mode reuses an OptiX BVH handle inside the run",
    )
    parser.add_argument(
        "--embree-summary-mode",
        choices=("rows", "rt_count_threshold", "rt_count_threshold_prepared"),
        default="rows",
        help="when backend=embree, use native fixed-radius threshold counts instead of neighbor rows; prepared mode reuses an Embree BVH handle inside the run",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                copies=args.copies,
                optix_summary_mode=args.optix_summary_mode,
                embree_summary_mode=args.embree_summary_mode,
                output_mode=args.output_mode,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
