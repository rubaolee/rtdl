from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


RADIUS = 0.85
K_MAX = 4


@rt.kernel(backend="rtdl", precision="float_approx")
def service_coverage_neighbors():
    households = rt.input("households", rt.Points, role="probe")
    clinics = rt.input("clinics", rt.Points, role="build")
    candidates = rt.traverse(households, clinics, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=RADIUS, k_max=K_MAX))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def make_service_coverage_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    households: list[rt.Point] = []
    clinics: list[rt.Point] = []
    for copy_index in range(copies):
        offset_x = float(copy_index * 4)
        base = copy_index * 100
        households.extend(
            (
                rt.Point(id=base + 1, x=0.0 + offset_x, y=0.0),
                rt.Point(id=base + 2, x=0.5 + offset_x, y=0.4),
                rt.Point(id=base + 3, x=2.2 + offset_x, y=0.1),
                rt.Point(id=base + 4, x=3.2 + offset_x, y=0.3),
            )
        )
        clinics.extend(
            (
                rt.Point(id=base + 10, x=0.1 + offset_x, y=0.1),
                rt.Point(id=base + 11, x=2.0 + offset_x, y=0.0),
                rt.Point(id=base + 12, x=4.7 + offset_x, y=0.0),
            )
        )
    return {"households": tuple(households), "clinics": tuple(clinics)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(service_coverage_neighbors, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(service_coverage_neighbors, **case))
    if backend == "embree":
        return tuple(rt.run_embree(service_coverage_neighbors, **case))
    if backend == "scipy":
        return tuple(
            rt.run_scipy_fixed_radius_neighbors(
                case["households"],
                case["clinics"],
                radius=RADIUS,
                k_max=K_MAX,
            )
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _run_embree_gap_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, int], ...]:
    return rt.fixed_radius_count_threshold_2d_embree(
        case["households"],
        case["clinics"],
        radius=RADIUS,
        threshold=1,
    )


def run_case(
    backend: str,
    *,
    copies: int = 1,
    embree_summary_mode: str = "rows",
) -> dict[str, object]:
    case = make_service_coverage_case(copies=copies)
    if embree_summary_mode not in {"rows", "gap_summary"}:
        raise ValueError("embree_summary_mode must be 'rows' or 'gap_summary'")
    clinics_by_household: dict[int, list[dict[str, object]]] = {}
    clinic_loads: dict[int, int] = {}
    household_ids = tuple(point.id for point in case["households"])
    coverage_summary_rows: tuple[dict[str, int], ...]
    if backend == "embree" and embree_summary_mode == "gap_summary":
        rows = ()
        coverage_summary_rows = _run_embree_gap_summary(case)
        covered_household_ids = {
            int(row["query_id"])
            for row in coverage_summary_rows
            if int(row["threshold_reached"]) != 0
        }
    else:
        rows = _run_rows(backend, case)
        coverage_summary_rows = ()
        for row in rows:
            query_id = int(row["query_id"])
            neighbor_id = int(row["neighbor_id"])
            clinics_by_household.setdefault(query_id, []).append(
                {"clinic_id": neighbor_id, "distance": float(row["distance"])}
            )
            clinic_loads[neighbor_id] = clinic_loads.get(neighbor_id, 0) + 1
        covered_household_ids = set(clinics_by_household)
    uncovered_household_ids = [household_id for household_id in household_ids if household_id not in covered_household_ids]
    return {
        "app": "service_coverage_gaps",
        "backend": backend,
        "radius": RADIUS,
        "k_max": K_MAX,
        "copies": copies,
        "household_count": len(case["households"]),
        "clinic_count": len(case["clinics"]),
        "rows": list(rows),
        "coverage_summary_rows": coverage_summary_rows,
        "nearby_clinics_by_household": clinics_by_household,
        "uncovered_household_ids": uncovered_household_ids,
        "covered_household_count": len(covered_household_ids),
        "clinic_loads": dict(sorted(clinic_loads.items())),
        "embree_summary_mode": embree_summary_mode if backend == "embree" else None,
        "summary_boundary": (
            "gap_summary reports covered/uncovered households only; use rows mode when clinic ids, "
            "distances, or clinic_loads are required."
            if backend == "embree" and embree_summary_mode == "gap_summary"
            else None
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Application example: detect households that do not have a clinic within a fixed service radius."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument(
        "--embree-summary-mode",
        choices=("rows", "gap_summary"),
        default="rows",
        help="Embree-only: emit neighbor rows or compact covered/uncovered household summary",
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
