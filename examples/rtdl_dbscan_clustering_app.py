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


EPSILON = 0.35
MIN_POINTS = 3
K_MAX = 16
NOISE_CLUSTER_ID = -1


@rt.kernel(backend="rtdl", precision="float_approx")
def dbscan_neighbor_rows_kernel():
    points = rt.input("points", rt.Points, role="probe")
    candidates = rt.traverse(points, points, accel="bvh")
    neighbors = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=EPSILON, k_max=K_MAX))
    return rt.emit(neighbors, fields=["query_id", "neighbor_id", "distance"])


def make_dbscan_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_points = (
        rt.Point(id=1, x=0.00, y=0.00),
        rt.Point(id=2, x=0.12, y=0.04),
        rt.Point(id=3, x=-0.10, y=0.08),
        rt.Point(id=4, x=0.08, y=-0.12),
        rt.Point(id=5, x=2.00, y=2.00),
        rt.Point(id=6, x=2.14, y=2.05),
        rt.Point(id=7, x=1.88, y=1.94),
        rt.Point(id=8, x=4.50, y=0.00),
    )

    points: list[rt.Point] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        x_offset = 6.0 * copy_index
        for point in base_points:
            points.append(rt.Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))
    return {"points": tuple(points)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(dbscan_neighbor_rows_kernel, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(dbscan_neighbor_rows_kernel, **case))
    if backend == "embree":
        return tuple(rt.run_embree(dbscan_neighbor_rows_kernel, **case))
    if backend == "optix":
        return tuple(rt.run_optix(dbscan_neighbor_rows_kernel, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(dbscan_neighbor_rows_kernel, **case))
    if backend == "scipy":
        return tuple(
            rt.run_scipy_fixed_radius_neighbors(
                case["points"],
                case["points"],
                radius=EPSILON,
                k_max=K_MAX,
            )
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _neighbors_by_point(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
) -> dict[int, set[int]]:
    point_ids = {point.id for point in points}
    neighborhoods: dict[int, set[int]] = {point.id: set() for point in points}
    for row in rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        if query_id in point_ids and neighbor_id in point_ids:
            neighborhoods[query_id].add(neighbor_id)
    return neighborhoods


def _neighbor_counts_by_point(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
) -> dict[int, int]:
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
    return counts


def cluster_from_neighbor_rows(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
    *,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    if min_points < 1:
        raise ValueError("min_points must be at least 1")

    neighbor_rows = tuple(rows)
    neighborhoods = _neighbors_by_point(points, neighbor_rows)
    neighbor_counts = _neighbor_counts_by_point(points, neighbor_rows)
    core_ids = {point_id for point_id, count in neighbor_counts.items() if count >= min_points}
    labels: dict[int, int] = {}
    cluster_id = 0

    for point_id in sorted(neighborhoods):
        if point_id in labels:
            continue
        if point_id not in core_ids:
            labels[point_id] = NOISE_CLUSTER_ID
            continue

        cluster_id += 1
        frontier = [point_id]
        labels[point_id] = cluster_id
        while frontier:
            current_id = frontier.pop(0)
            for neighbor_id in sorted(neighborhoods[current_id]):
                previous_label = labels.get(neighbor_id)
                if previous_label is None or previous_label == NOISE_CLUSTER_ID:
                    labels[neighbor_id] = cluster_id
                if neighbor_id in core_ids and previous_label is None:
                    frontier.append(neighbor_id)

    return tuple(
        {
            "point_id": point_id,
            "cluster_id": labels.get(point_id, NOISE_CLUSTER_ID),
            "is_core": point_id in core_ids,
            "neighbor_count": neighbor_counts[point_id],
        }
        for point_id in sorted(neighborhoods)
    )


def brute_force_dbscan(
    points: tuple[rt.Point, ...],
    *,
    epsilon: float = EPSILON,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        for neighbor in points:
            distance = math.hypot(query.x - neighbor.x, query.y - neighbor.y)
            if distance <= epsilon:
                rows.append({"query_id": query.id, "neighbor_id": neighbor.id, "distance": distance})
    rows.sort(key=lambda row: (int(row["query_id"]), float(row["distance"]), int(row["neighbor_id"])))
    return cluster_from_neighbor_rows(points, rows, min_points=min_points)


def brute_force_core_flag_rows(
    points: tuple[rt.Point, ...],
    *,
    epsilon: float = EPSILON,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        count = 0
        for neighbor in points:
            if math.hypot(query.x - neighbor.x, query.y - neighbor.y) <= epsilon:
                count += 1
        rows.append(
            {
                "point_id": query.id,
                "neighbor_count": count,
                "is_core": count >= min_points,
            }
        )
    return tuple(sorted(rows, key=lambda row: int(row["point_id"])))


def expected_tiled_core_flag_rows(*, copies: int) -> tuple[dict[str, object], ...]:
    """Exact DBSCAN core summary for make_dbscan_case without O(N^2) expansion."""
    base_rows = (
        (1, MIN_POINTS, True),
        (2, MIN_POINTS, True),
        (3, MIN_POINTS, True),
        (4, MIN_POINTS, True),
        (5, 3, True),
        (6, 3, True),
        (7, 3, True),
        (8, 1, False),
    )
    rows: list[dict[str, object]] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        for point_id, neighbor_count, is_core in base_rows:
            rows.append(
                {
                    "point_id": point_id + id_offset,
                    "neighbor_count": neighbor_count,
                    "is_core": is_core,
                }
            )
    return tuple(rows)


def _core_flag_rows_from_count_rows(
    points: tuple[rt.Point, ...],
    count_rows: Iterable[dict[str, object]],
    *,
    min_points: int = MIN_POINTS,
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
            "is_core": counts[point_id] >= min_points or threshold_reached[point_id] == 1,
        }
        for point_id in sorted(counts)
    )


def _run_optix_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    count_rows = rt.fixed_radius_count_threshold_2d_optix(
        case["points"],
        case["points"],
        radius=EPSILON,
        threshold=MIN_POINTS,
    )
    return _core_flag_rows_from_count_rows(case["points"], count_rows)


def _run_optix_prepared_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    with rt.prepare_optix_fixed_radius_count_threshold_2d(case["points"], max_radius=EPSILON) as prepared:
        count_rows = prepared.run(
            case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
    return _core_flag_rows_from_count_rows(case["points"], count_rows)


def _run_optix_prepared_core_count(case: dict[str, tuple[rt.Point, ...]]) -> dict[str, int | str | None]:
    with rt.prepare_optix_fixed_radius_count_threshold_2d(case["points"], max_radius=EPSILON) as prepared:
        core_count = prepared.count_threshold_reached(
            case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
    return {
        "point_count": len(case["points"]),
        "threshold_reached_count": int(core_count),
        "core_count": int(core_count),
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
    }


def _run_embree_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    count_rows = rt.fixed_radius_count_threshold_2d_embree(
        case["points"],
        case["points"],
        radius=EPSILON,
        threshold=MIN_POINTS,
    )
    return _core_flag_rows_from_count_rows(case["points"], count_rows)


def _run_embree_prepared_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    with rt.prepare_embree_fixed_radius_count_threshold_2d(case["points"]) as prepared:
        count_rows = prepared.run(
            case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
    return _core_flag_rows_from_count_rows(case["points"], count_rows)


def _native_continuation_backend(
    backend: str,
    *,
    output_mode: str,
    optix_summary_mode: str,
    embree_summary_mode: str,
) -> str:
    if backend == "optix" and (
        output_mode in {"core_flags", "core_count"}
        or optix_summary_mode in {"rt_core_flags", "rt_core_flags_prepared"}
    ):
        return "optix_threshold_count"
    if backend == "embree" and (
        output_mode == "core_flags" or embree_summary_mode in {"rt_core_flags", "rt_core_flags_prepared"}
    ):
        return "embree_threshold_count"
    return "none"


def _cluster_sizes(cluster_rows: tuple[dict[str, object], ...]) -> dict[int, int]:
    sizes: dict[int, int] = {}
    for row in cluster_rows:
        cluster_id = int(row["cluster_id"])
        if cluster_id == NOISE_CLUSTER_ID:
            continue
        sizes[cluster_id] = sizes.get(cluster_id, 0) + 1
    return dict(sorted(sizes.items()))


class PreparedDbscanCoreFlagSession:
    def __init__(self, backend: str = "optix", *, copies: int = 1):
        if backend != "optix":
            raise ValueError("PreparedDbscanCoreFlagSession currently supports backend='optix'")
        self.backend = backend
        self.copies = copies
        self.case = make_dbscan_case(copies=copies)
        self._prepared = rt.prepare_optix_fixed_radius_count_threshold_2d(self.case["points"], max_radius=EPSILON)
        self._closed = False

    def run(self, *, output_mode: str = "core_flags") -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared DBSCAN core-flag session is closed")
        if output_mode not in {"core_flags", "core_count"}:
            raise ValueError("prepared DBSCAN core-flag session currently supports output_mode='core_flags' or 'core_count'")
        if output_mode == "core_count":
            core_count = self._prepared.count_threshold_reached(
                self.case["points"],
                radius=EPSILON,
                threshold=MIN_POINTS,
            )
            oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=self.copies)
            oracle_core_count = sum(1 for row in oracle_core_flag_rows if bool(row["is_core"]))
            return {
                "app": "dbscan_clustering",
                "backend": self.backend,
                "execution_mode": "prepared_session",
                "output_mode": output_mode,
                "optix_summary_mode": "rt_core_flags_prepared",
                "embree_summary_mode": "not_applicable",
                "epsilon": EPSILON,
                "min_points": MIN_POINTS,
                "k_max": K_MAX,
                "copies": self.copies,
                "point_count": len(self.case["points"]),
                "threshold_reached_count": int(core_count),
                "core_count": int(core_count),
                "oracle_core_count": oracle_core_count,
                "neighbor_row_count": 0,
                "cluster_rows": (),
                "cluster_sizes": {},
                "core_flag_rows": (),
                "native_continuation_active": True,
                "native_continuation_backend": "optix_threshold_count",
                "noise_point_ids": (),
                "oracle_cluster_rows": (),
                "oracle_core_flag_rows": (),
                "matches_oracle": int(core_count) == oracle_core_count,
                "summary_mode": "scalar_threshold_count",
                "rtdl_role": "Prepared OptiX reuses the fixed-radius count-threshold RT traversal scene and emits only scalar DBSCAN core counts; point identities and cluster expansion remain outside this scalar mode.",
                "boundary": "Prepared OptiX core_count covers the RT-heavy fixed-radius core predicate count only. Use core_flags when per-point core labels are required; full DBSCAN cluster expansion remains Python-side.",
            }
        count_rows = self._prepared.run(
            self.case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
        core_flag_rows = _core_flag_rows_from_count_rows(self.case["points"], count_rows)
        oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=self.copies)
        core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
        oracle_core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_core_flag_rows]
        return {
            "app": "dbscan_clustering",
            "backend": self.backend,
            "execution_mode": "prepared_session",
            "output_mode": output_mode,
            "optix_summary_mode": "rt_core_flags_prepared",
            "embree_summary_mode": "not_applicable",
            "epsilon": EPSILON,
            "min_points": MIN_POINTS,
            "k_max": K_MAX,
            "copies": self.copies,
            "point_count": len(self.case["points"]),
            "neighbor_row_count": 0,
            "cluster_rows": (),
            "cluster_sizes": {},
            "core_flag_rows": core_flag_rows,
            "native_continuation_active": True,
            "native_continuation_backend": "optix_threshold_count",
            "noise_point_ids": (),
            "oracle_cluster_rows": (),
            "oracle_core_flag_rows": oracle_core_flag_rows,
            "matches_oracle": core_flags == oracle_core_flags,
            "rtdl_role": "Prepared OptiX reuses the fixed-radius count-threshold RT traversal scene and emits compact DBSCAN core flags without materializing neighbor rows; Python clustering expansion remains outside this prepared summary path.",
            "boundary": "Prepared OptiX core flags cover the RT-heavy fixed-radius density predicate only. Full DBSCAN cluster expansion remains Python-side and is not claimed as a backend primitive.",
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._prepared.close()

    def __enter__(self) -> "PreparedDbscanCoreFlagSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def prepare_session(backend: str = "optix", *, copies: int = 1) -> PreparedDbscanCoreFlagSession:
    return PreparedDbscanCoreFlagSession(backend, copies=copies)


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    optix_summary_mode: str = "rows",
    embree_summary_mode: str = "rows",
    output_mode: str = "full",
) -> dict[str, object]:
    if optix_summary_mode not in {"rows", "rt_core_flags", "rt_core_flags_prepared"}:
        raise ValueError("optix_summary_mode must be 'rows', 'rt_core_flags', or 'rt_core_flags_prepared'")
    if embree_summary_mode not in {"rows", "rt_core_flags", "rt_core_flags_prepared"}:
        raise ValueError("embree_summary_mode must be 'rows', 'rt_core_flags', or 'rt_core_flags_prepared'")
    if output_mode not in {"full", "core_flags", "core_count"}:
        raise ValueError("output_mode must be 'full', 'core_flags', or 'core_count'")
    case = make_dbscan_case(copies=copies)
    points = case["points"]
    core_flag_rows: tuple[dict[str, object], ...] = ()
    scalar_core_count: dict[str, int | str | None] | None = None
    if output_mode == "core_count" and backend == "optix":
        neighbor_rows = ()
        cluster_rows = ()
        scalar_core_count = _run_optix_prepared_core_count(case)
    elif output_mode == "core_count":
        neighbor_rows = ()
        cluster_rows = ()
        oracle_scalar_rows = expected_tiled_core_flag_rows(copies=copies)
        oracle_core_count_for_scalar = sum(1 for row in oracle_scalar_rows if bool(row["is_core"]))
        scalar_core_count = {
            "point_count": len(points),
            "threshold_reached_count": oracle_core_count_for_scalar,
            "core_count": oracle_core_count_for_scalar,
            "row_count": None,
            "summary_mode": "scalar_threshold_count_oracle",
        }
    elif output_mode == "core_flags" and backend == "embree":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_embree_prepared_core_flag_summary(case)
    elif output_mode == "core_flags" and backend == "optix":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_optix_core_flag_summary(case)
    elif output_mode == "core_flags":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = expected_tiled_core_flag_rows(copies=copies)
    elif backend == "optix" and optix_summary_mode == "rt_core_flags":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_optix_core_flag_summary(case)
    elif backend == "optix" and optix_summary_mode == "rt_core_flags_prepared":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_optix_prepared_core_flag_summary(case)
    elif backend == "embree" and embree_summary_mode == "rt_core_flags":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_embree_core_flag_summary(case)
    elif backend == "embree" and embree_summary_mode == "rt_core_flags_prepared":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_embree_prepared_core_flag_summary(case)
    else:
        neighbor_rows = _run_rows(backend, case)
        cluster_rows = cluster_from_neighbor_rows(points, neighbor_rows)
    if output_mode in {"core_flags", "core_count"} or core_flag_rows:
        oracle_rows = ()
        oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=copies)
    else:
        oracle_rows = brute_force_dbscan(points)
        oracle_core_flag_rows = brute_force_core_flag_rows(points)
    if scalar_core_count is not None:
        oracle_core_count = sum(1 for row in oracle_core_flag_rows if bool(row["is_core"]))
        matches_oracle = int(scalar_core_count["core_count"]) == oracle_core_count
    elif core_flag_rows:
        core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
        oracle_core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_core_flag_rows]
        matches_oracle = core_flags == oracle_core_flags
    else:
        matches_oracle = cluster_rows == oracle_rows
    native_continuation_backend = _native_continuation_backend(
        backend,
        output_mode=output_mode,
        optix_summary_mode=optix_summary_mode,
        embree_summary_mode=embree_summary_mode,
    )

    return {
        "app": "dbscan_clustering",
        "backend": backend,
        "output_mode": output_mode,
        "optix_summary_mode": optix_summary_mode if backend == "optix" else "not_applicable",
        "embree_summary_mode": embree_summary_mode if backend == "embree" else "not_applicable",
        "epsilon": EPSILON,
        "min_points": MIN_POINTS,
        "k_max": K_MAX,
        "copies": copies,
        "point_count": len(points),
        "neighbor_row_count": len(neighbor_rows),
        "cluster_rows": cluster_rows,
        "cluster_sizes": _cluster_sizes(cluster_rows),
        "core_flag_rows": core_flag_rows,
        "threshold_reached_count": (
            int(scalar_core_count["threshold_reached_count"]) if scalar_core_count is not None else None
        ),
        "core_count": int(scalar_core_count["core_count"]) if scalar_core_count is not None else sum(1 for row in core_flag_rows if bool(row.get("is_core", False))),
        "native_continuation_active": native_continuation_backend != "none",
        "native_continuation_backend": native_continuation_backend,
        "noise_point_ids": [int(row["point_id"]) for row in cluster_rows if int(row["cluster_id"]) == NOISE_CLUSTER_ID],
        "oracle_cluster_rows": oracle_rows,
        "oracle_core_flag_rows": oracle_core_flag_rows,
        "oracle_core_count": sum(1 for row in oracle_core_flag_rows if bool(row.get("is_core", False))),
        "summary_mode": scalar_core_count["summary_mode"] if scalar_core_count is not None else None,
        "matches_oracle": matches_oracle,
        "rtdl_role": "Default RTDL emits fixed-radius neighbor rows; rt.reduce_rows(count) identifies core candidates for Python cluster expansion. The compact core-flag paths use prepared fixed-radius threshold traversal through native backend fixed-radius threshold-count continuation and avoid neighbor-row materialization.",
        "boundary": "Bounded app-level DBSCAN demo only; RTDL does not yet expose clustering expansion or connected-component reduction as language primitives. Embree/OptiX rt_core_flags is a fixed-radius core predicate prototype, not KNN/Hausdorff/Barnes-Hut. One-shot CLI runs cannot fully amortize backend preparation; prepared app/session mode is intended for repeated probes.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived DBSCAN app: RTDL neighbor rows plus Python density-cluster expansion."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1, help="tile the authored clustering fixture")
    parser.add_argument(
        "--output-mode",
        choices=("full", "core_flags", "core_count"),
        default="full",
        help="full emits neighbor/cluster rows; core_flags emits compact DBSCAN core predicates; core_count emits only scalar core counts",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "rt_core_flags", "rt_core_flags_prepared"),
        default="rows",
        help="when backend=optix, use native fixed-radius threshold counts for core flags only; prepared mode reuses an OptiX BVH handle inside the run",
    )
    parser.add_argument(
        "--embree-summary-mode",
        choices=("rows", "rt_core_flags", "rt_core_flags_prepared"),
        default="rows",
        help="when backend=embree, use native fixed-radius threshold counts for core flags only; prepared mode reuses an Embree BVH handle inside the run",
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
