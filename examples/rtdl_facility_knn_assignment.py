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
PRIMARY_K = 1


@rt.kernel(backend="rtdl", precision="float_approx")
def facility_knn_assignment():
    customers = rt.input("customers", rt.Points, role="probe")
    depots = rt.input("depots", rt.Points, role="build")
    candidates = rt.traverse(customers, depots, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=K))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def facility_primary_assignment():
    customers = rt.input("customers", rt.Points, role="probe")
    depots = rt.input("depots", rt.Points, role="build")
    candidates = rt.traverse(customers, depots, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=PRIMARY_K))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def make_facility_knn_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be >= 1")
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


def _run_rows(
    backend: str,
    case: dict[str, tuple[rt.Point, ...]],
    *,
    primary_only: bool = False,
) -> tuple[dict[str, object], ...]:
    kernel = facility_primary_assignment if primary_only else facility_knn_assignment
    k = PRIMARY_K if primary_only else K
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(kernel, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(kernel, **case))
    if backend == "embree":
        return tuple(rt.run_embree(kernel, **case))
    if backend == "scipy":
        return tuple(rt.run_scipy_knn_rows(case["customers"], case["depots"], k=k))
    raise ValueError(f"unsupported backend `{backend}`")


def run_case(backend: str, *, copies: int = 1, output_mode: str = "rows") -> dict[str, object]:
    if output_mode not in {"rows", "primary_assignments", "summary"}:
        raise ValueError("output_mode must be 'rows', 'primary_assignments', or 'summary'")
    case = make_facility_knn_case(copies=copies)
    primary_only = output_mode != "rows"
    rows = _run_rows(backend, case, primary_only=primary_only)
    choices: dict[int, list[dict[str, object]]] = {}
    primary_load: dict[int, int] = {}
    primary_depot_by_customer: dict[int, int] = {}
    for row in rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        rank = int(row["neighbor_rank"])
        option = {
            "depot_id": neighbor_id,
            "neighbor_rank": rank,
            "distance": float(row["distance"]),
        }
        choices.setdefault(query_id, []).append(option)
        if rank == 1:
            primary_depot_by_customer[query_id] = neighbor_id
            primary_load[neighbor_id] = primary_load.get(neighbor_id, 0) + 1

    for options in choices.values():
        options.sort(key=lambda item: int(item["neighbor_rank"]))

    payload: dict[str, object] = {
        "app": "facility_knn_assignment",
        "backend": backend,
        "k": PRIMARY_K if primary_only else K,
        "copies": copies,
        "output_mode": output_mode,
        "customer_count": len(case["customers"]),
        "depot_count": len(case["depots"]),
        "primary_depot_by_customer": dict(sorted(primary_depot_by_customer.items())),
        "primary_depot_load": dict(sorted(primary_load.items())),
        "row_count": len(rows),
        "boundary": (
            "Rows mode emits K=3 nearest-depot fallback choices. Compact "
            "primary_assignments and summary modes use a K=1 RTDL KNN kernel "
            "when fallback choices are not needed."
        ),
    }
    if output_mode == "rows":
        payload["rows"] = list(rows)
        payload["choices_by_customer"] = dict(sorted(choices.items()))
    elif output_mode == "summary":
        payload.pop("primary_depot_by_customer")
    return payload


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
    parser.add_argument(
        "--output-mode",
        choices=("rows", "primary_assignments", "summary"),
        default="rows",
        help="Use compact primary_assignments or summary when K=3 fallback choices are not needed.",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
