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
def sales_grouped_sum_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])


def make_case() -> dict[str, object]:
    return {
        "query": {
            "predicates": (("ship_date", "ge", 11),),
            "group_keys": ("region",),
            "value_field": "revenue",
        },
        "table": (
            {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10, "revenue": 10},
            {"row_id": 5, "region": "west", "ship_date": 13, "quantity": 8, "revenue": 2},
        ),
    }


def run_backend(backend: str) -> dict[str, object]:
    case = make_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(sales_grouped_sum_reference, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(sales_grouped_sum_reference, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")
    return {
        "app": "db_grouped_sum",
        "backend": backend,
        "query": case["query"],
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bounded RTDL v0.7 grouped-sum example.")
    parser.add_argument("--backend", default="cpu_python_reference", choices=("cpu_python_reference", "cpu"))
    args = parser.parse_args(argv)
    print(json.dumps(run_backend(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
