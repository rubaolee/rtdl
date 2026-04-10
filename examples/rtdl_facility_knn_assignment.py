from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


K = 3


@rt.kernel(backend="rtdl", precision="float_approx")
def facility_knn_assignment():
    customers = rt.input("customers", rt.Points, role="probe")
    depots = rt.input("depots", rt.Points, role="build")
    candidates = rt.traverse(customers, depots, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=K))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def make_facility_knn_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    customers: list[rt.Point] = []
    depots: list[rt.Point] = []
    for copy_index in range(copies):
        offset_x = float(copy_index * 6)
        base = copy_index * 100
        customers.extend(
            (
                rt.Point(id=base + 1, x=0.0 + offset_x, y=0.0),
                rt.Point(id=base + 2, x=0.8 + offset_x, y=0.2),
                rt.Point(id=base + 3, x=2.1 + offset_x, y=-0.1),
                rt.Point(id=base + 4, x=3.4 + offset_x, y=0.3),
            )
        )
        depots.extend(
            (
                rt.Point(id=base + 10, x=-0.2 + offset_x, y=0.0),
                rt.Point(id=base + 11, x=1.5 + offset_x, y=0.0),
                rt.Point(id=base + 12, x=3.0 + offset_x, y=0.1),
                rt.Point(id=base + 13, x=4.5 + offset_x, y=0.0),
            )
        )
    return {"customers": tuple(customers), "depots": tuple(depots)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(facility_knn_assignment, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(facility_knn_assignment, **case))
    if backend == "embree":
        return tuple(rt.run_embree(facility_knn_assignment, **case))
    if backend == "scipy":
        return tuple(rt.run_scipy_knn_rows(case["customers"], case["depots"], k=K))
    raise ValueError(f"unsupported backend `{backend}`")


def run_case(backend: str, *, copies: int = 1) -> dict[str, object]:
    case = make_facility_knn_case(copies=copies)
    rows = _run_rows(backend, case)
    choices: dict[int, list[dict[str, object]]] = {}
    primary_load: dict[int, int] = {}
    for row in rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        rank = int(row["neighbor_rank"])
        choices.setdefault(query_id, []).append(
            {
                "depot_id": neighbor_id,
                "neighbor_rank": rank,
                "distance": float(row["distance"]),
            }
        )
        if rank == 1:
            primary_load[neighbor_id] = primary_load.get(neighbor_id, 0) + 1
    primary_depot_by_customer = {
        customer_id: int(options[0]["depot_id"])
        for customer_id, options in choices.items()
        if options
    }
    return {
        "app": "facility_knn_assignment",
        "backend": backend,
        "k": K,
        "copies": copies,
        "customer_count": len(case["customers"]),
        "depot_count": len(case["depots"]),
        "rows": list(rows),
        "choices_by_customer": choices,
        "primary_depot_by_customer": dict(sorted(primary_depot_by_customer.items())),
        "primary_depot_load": dict(sorted(primary_load.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Application example: assign each customer the nearest depot plus two fallback choices."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend, copies=args.copies), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
