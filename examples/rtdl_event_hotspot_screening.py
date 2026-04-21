from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


RADIUS = 0.75
K_MAX = 12
HOTSPOT_THRESHOLD = 3


@rt.kernel(backend="rtdl", precision="float_approx")
def event_hotspot_neighbors():
    events = rt.input("events", rt.Points, role="probe")
    candidates = rt.traverse(events, events, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=RADIUS, k_max=K_MAX))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def make_event_hotspot_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    events: list[rt.Point] = []
    for copy_index in range(copies):
        offset_x = float(copy_index * 5)
        base = copy_index * 100
        events.extend(
            (
                rt.Point(id=base + 1, x=0.0 + offset_x, y=0.0),
                rt.Point(id=base + 2, x=0.2 + offset_x, y=0.1),
                rt.Point(id=base + 3, x=0.3 + offset_x, y=-0.2),
                rt.Point(id=base + 4, x=0.4 + offset_x, y=0.15),
                rt.Point(id=base + 5, x=2.3 + offset_x, y=0.0),
                rt.Point(id=base + 6, x=4.6 + offset_x, y=0.0),
            )
        )
    return {"events": tuple(events)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(event_hotspot_neighbors, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(event_hotspot_neighbors, **case))
    if backend == "embree":
        return tuple(rt.run_embree(event_hotspot_neighbors, **case))
    if backend == "scipy":
        return tuple(
            rt.run_scipy_fixed_radius_neighbors(
                case["events"],
                case["events"],
                radius=RADIUS,
                k_max=K_MAX,
            )
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _run_embree_count_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, int], ...]:
    count_rows = rt.fixed_radius_count_threshold_2d_embree(
        case["events"],
        case["events"],
        radius=RADIUS,
        threshold=0,
    )
    return tuple(
        {
            "query_id": int(row["query_id"]),
            "neighbor_count": max(0, int(row["neighbor_count"]) - 1),
        }
        for row in count_rows
    )


def run_case(
    backend: str,
    *,
    copies: int = 1,
    embree_summary_mode: str = "rows",
) -> dict[str, object]:
    case = make_event_hotspot_case(copies=copies)
    if embree_summary_mode not in {"rows", "count_summary"}:
        raise ValueError("embree_summary_mode must be 'rows' or 'count_summary'")
    rows: tuple[dict[str, object], ...]
    summary_rows: tuple[dict[str, int], ...]
    if backend == "embree" and embree_summary_mode == "count_summary":
        rows = ()
        summary_rows = _run_embree_count_summary(case)
        neighbor_counts = {int(row["query_id"]): int(row["neighbor_count"]) for row in summary_rows}
    else:
        raw_rows = _run_rows(backend, case)
        rows = tuple(row for row in raw_rows if int(row["query_id"]) != int(row["neighbor_id"]))
        summary_rows = ()
        neighbor_counts: dict[int, int] = {point.id: 0 for point in case["events"]}
        for row in rows:
            query_id = int(row["query_id"])
            neighbor_counts[query_id] = neighbor_counts.get(query_id, 0) + 1
    hotspots = [
        {"event_id": event_id, "neighbor_count": neighbor_count}
        for event_id, neighbor_count in neighbor_counts.items()
        if neighbor_count >= HOTSPOT_THRESHOLD
    ]
    hotspots.sort(key=lambda item: (-int(item["neighbor_count"]), int(item["event_id"])))
    return {
        "app": "event_hotspot_screening",
        "backend": backend,
        "radius": RADIUS,
        "k_max": K_MAX,
        "copies": copies,
        "event_count": len(case["events"]),
        "rows": list(rows),
        "summary_rows": summary_rows,
        "neighbor_count_by_event": dict(sorted(neighbor_counts.items())),
        "hotspots": hotspots,
        "hotspot_threshold": HOTSPOT_THRESHOLD,
        "embree_summary_mode": embree_summary_mode if backend == "embree" else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Application example: screen clustered events and flag local hotspots by neighbor count."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument(
        "--embree-summary-mode",
        choices=("rows", "count_summary"),
        default="rows",
        help="Embree-only: emit neighbor rows or compact native count summaries",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_case(args.backend, copies=args.copies, embree_summary_mode=args.embree_summary_mode),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
