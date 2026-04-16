from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def sales_conjunctive_scan_reference():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


def make_case() -> dict[str, object]:
    return {
        "predicates": (
            ("ship_date", "between", 11, 13),
            ("discount", "eq", 6),
            ("quantity", "lt", 20),
        ),
        "table": (
            {"row_id": 1, "ship_date": 10, "discount": 5, "quantity": 12},
            {"row_id": 2, "ship_date": 11, "discount": 8, "quantity": 30},
            {"row_id": 3, "ship_date": 12, "discount": 6, "quantity": 18},
            {"row_id": 4, "ship_date": 13, "discount": 6, "quantity": 10},
        ),
    }


def run_backend(backend: str) -> dict[str, object]:
    case = make_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(sales_conjunctive_scan_reference, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(sales_conjunctive_scan_reference, **case)
    elif backend == "embree":
        rows = rt.run_embree(sales_conjunctive_scan_reference, **case)
    elif backend == "optix":
        rows = rt.run_optix(sales_conjunctive_scan_reference, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(sales_conjunctive_scan_reference, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")
    return {
        "app": "db_conjunctive_scan",
        "backend": backend,
        "predicates": list(case["predicates"]),
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bounded RTDL v0.7 conjunctive-scan example.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_backend(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
