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


K = 3
PRIMARY_K = 1
DEFAULT_SERVICE_RADIUS = 1.0


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


def _enforce_rt_core_requirement(backend: str, optix_summary_mode: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    if optix_summary_mode != "coverage_threshold_prepared":
        raise RuntimeError(
            "facility_knn_assignment RT-core path requires --backend optix "
            "--optix-summary-mode coverage_threshold_prepared"
        )


def facility_coverage_oracle(
    customers: tuple[rt.Point, ...],
    depots: tuple[rt.Point, ...],
    *,
    radius: float,
) -> dict[str, object]:
    if radius < 0:
        raise ValueError("radius must be non-negative")
    uncovered: list[int] = []
    if radius == 0:
        depot_coordinates = {(depot.x, depot.y) for depot in depots}
        for customer in customers:
            if (customer.x, customer.y) not in depot_coordinates:
                uncovered.append(customer.id)
        return {
            "radius": radius,
            "customer_count": len(customers),
            "covered_customer_count": len(customers) - len(uncovered),
            "all_customers_covered": not uncovered,
            "uncovered_customer_ids": uncovered,
        }

    cell_size = radius
    depot_cells: dict[tuple[int, int], list[rt.Point]] = {}
    for depot in depots:
        cell = (math.floor(depot.x / cell_size), math.floor(depot.y / cell_size))
        depot_cells.setdefault(cell, []).append(depot)

    radius_sq = radius * radius
    for customer in customers:
        cx = math.floor(customer.x / cell_size)
        cy = math.floor(customer.y / cell_size)
        has_depot = False
        for nx in (cx - 1, cx, cx + 1):
            for ny in (cy - 1, cy, cy + 1):
                for depot in depot_cells.get((nx, ny), ()):
                    dx = customer.x - depot.x
                    dy = customer.y - depot.y
                    if dx * dx + dy * dy <= radius_sq:
                        has_depot = True
                        break
                if has_depot:
                    break
            if has_depot:
                break
        if not has_depot:
            uncovered.append(customer.id)
    return {
        "radius": radius,
        "customer_count": len(customers),
        "covered_customer_count": len(customers) - len(uncovered),
        "all_customers_covered": not uncovered,
        "uncovered_customer_ids": uncovered,
    }


def _coverage_threshold_from_count_rows(
    rows: tuple[dict[str, object], ...],
    *,
    customers: tuple[rt.Point, ...],
    radius: float,
) -> dict[str, object]:
    by_query = {int(row["query_id"]): row for row in rows}
    uncovered = [
        customer.id
        for customer in customers
        if int(by_query.get(customer.id, {}).get("threshold_reached", 0)) == 0
    ]
    return {
        "radius": radius,
        "customer_count": len(customers),
        "covered_customer_count": len(customers) - len(uncovered),
        "all_customers_covered": not uncovered,
        "uncovered_customer_ids": uncovered,
        "row_count": len(by_query),
    }


def _run_optix_coverage_threshold(
    case: dict[str, tuple[rt.Point, ...]],
    *,
    radius: float,
) -> dict[str, object]:
    with rt.prepare_optix_fixed_radius_count_threshold_2d(case["depots"], max_radius=radius) as prepared:
        covered_count = prepared.count_threshold_reached(case["customers"], radius=radius, threshold=1)
    all_customers_covered = int(covered_count) == len(case["customers"])
    return {
        "radius": radius,
        "customer_count": len(case["customers"]),
        "covered_customer_count": int(covered_count),
        "all_customers_covered": all_customers_covered,
        "uncovered_customer_ids": [] if all_customers_covered else None,
        "identity_parity_available": all_customers_covered,
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
    }


def run_case(
    backend: str,
    *,
    copies: int = 1,
    output_mode: str = "rows",
    optix_summary_mode: str = "rows",
    service_radius: float = DEFAULT_SERVICE_RADIUS,
    require_rt_core: bool = False,
) -> dict[str, object]:
    if output_mode not in {"rows", "primary_assignments", "summary"}:
        raise ValueError("output_mode must be 'rows', 'primary_assignments', or 'summary'")
    if optix_summary_mode not in {"rows", "coverage_threshold_prepared"}:
        raise ValueError("optix_summary_mode must be 'rows' or 'coverage_threshold_prepared'")
    if service_radius < 0:
        raise ValueError("service_radius must be non-negative")
    _enforce_rt_core_requirement(backend, optix_summary_mode, require_rt_core)
    case = make_facility_knn_case(copies=copies)
    if backend == "optix" and optix_summary_mode == "coverage_threshold_prepared":
        coverage = _run_optix_coverage_threshold(case, radius=service_radius)
        oracle = facility_coverage_oracle(case["customers"], case["depots"], radius=service_radius)
        return {
            "app": "facility_knn_assignment",
            "backend": backend,
            "k": None,
            "copies": copies,
            "output_mode": output_mode,
            "optix_summary_mode": optix_summary_mode,
            "service_radius": service_radius,
            "customer_count": len(case["customers"]),
            "depot_count": len(case["depots"]),
            "coverage_threshold": coverage,
            "oracle_coverage_threshold": oracle,
            "matches_oracle": coverage["all_customers_covered"] == oracle["all_customers_covered"],
            "oracle_decision_matches": coverage["all_customers_covered"] == oracle["all_customers_covered"],
            "oracle_identity_matches": (
                coverage["uncovered_customer_ids"] == oracle["uncovered_customer_ids"]
                if coverage["identity_parity_available"]
                else None
            ),
            "native_continuation_active": True,
            "native_continuation_backend": "optix_threshold_count",
            "rt_core_accelerated": True,
            "rtdl_role": (
                "RTDL/OptiX uses prepared fixed-radius threshold traversal to answer "
                "the bounded facility-coverage decision: every customer has at least "
                "one depot within the service radius."
            ),
            "boundary": (
                "Coverage-threshold decision only; this is not nearest-depot ranking, "
                "not K=3 fallback assignment, and not a facility-location optimizer."
            ),
        }
    if backend == "optix":
        raise RuntimeError(
            "facility_knn_assignment OptiX support is limited to "
            "--optix-summary-mode coverage_threshold_prepared"
        )
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
        "optix_summary_mode": None,
        "service_radius": None,
        "customer_count": len(case["customers"]),
        "depot_count": len(case["depots"]),
        "primary_depot_by_customer": dict(sorted(primary_depot_by_customer.items())),
        "primary_depot_load": dict(sorted(primary_load.items())),
        "row_count": len(rows),
        "native_continuation_active": False,
        "native_continuation_backend": "none",
        "rt_core_accelerated": False,
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
        choices=("cpu_python_reference", "cpu", "embree", "optix", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument(
        "--output-mode",
        choices=("rows", "primary_assignments", "summary"),
        default="rows",
        help="Use compact primary_assignments or summary when K=3 fallback choices are not needed.",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "coverage_threshold_prepared"),
        default="rows",
        help="OptiX-only: use prepared fixed-radius threshold traversal for service-coverage decisions.",
    )
    parser.add_argument(
        "--service-radius",
        type=float,
        default=DEFAULT_SERVICE_RADIUS,
        help="service radius for --optix-summary-mode coverage_threshold_prepared",
    )
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_case(
                args.backend,
                copies=args.copies,
                output_mode=args.output_mode,
                optix_summary_mode=args.optix_summary_mode,
                service_radius=args.service_radius,
                require_rt_core=args.require_rt_core,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
