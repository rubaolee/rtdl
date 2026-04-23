from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def _timed_call(fn):
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


@rt.kernel(backend="rtdl", precision="float_approx")
def risky_order_scan():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def risky_order_count_by_region():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def risky_order_revenue_by_region():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])


def make_sales_case(copies: int = 1) -> tuple[dict[str, object], dict[str, object]]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    base_table = (
        {"row_id": 1, "region": "east", "ship_date": 10, "discount": 4, "quantity": 8, "revenue": 120},
        {"row_id": 2, "region": "east", "ship_date": 12, "discount": 7, "quantity": 18, "revenue": 310},
        {"row_id": 3, "region": "west", "ship_date": 12, "discount": 6, "quantity": 12, "revenue": 280},
        {"row_id": 4, "region": "west", "ship_date": 13, "discount": 6, "quantity": 9, "revenue": 150},
        {"row_id": 5, "region": "central", "ship_date": 13, "discount": 2, "quantity": 40, "revenue": 500},
        {"row_id": 6, "region": "central", "ship_date": 11, "discount": 6, "quantity": 14, "revenue": 260},
    )
    rows: list[dict[str, object]] = []
    for copy_index in range(copies):
        row_id_offset = copy_index * len(base_table)
        for row in base_table:
            copied = dict(row)
            copied["row_id"] = int(row["row_id"]) + row_id_offset
            rows.append(copied)
    table = tuple(rows)
    risky_predicates = (
        ("ship_date", "between", 11, 13),
        ("discount", "ge", 6),
        ("quantity", "lt", 20),
    )
    grouped_query = {
        "predicates": risky_predicates,
        "group_keys": ("region",),
        "value_field": "revenue",
    }
    return {"table": table, "predicates": risky_predicates}, {"table": table, "query": grouped_query}


def _run_scan_rows(backend: str, case: dict[str, object]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(risky_order_scan, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(risky_order_scan, **case))
    if backend == "embree":
        return tuple(rt.run_embree(risky_order_scan, **case))
    if backend == "optix":
        return tuple(rt.run_optix(risky_order_scan, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(risky_order_scan, **case))
    raise ValueError(f"unsupported backend: {backend}")


def _run_grouped_count_rows(backend: str, case: dict[str, object]) -> tuple[dict[str, object], ...]:
    adjusted = dict(case)
    adjusted["query"] = {
        "predicates": case["query"]["predicates"],
        "group_keys": case["query"]["group_keys"],
    }
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(risky_order_count_by_region, **adjusted))
    if backend == "cpu":
        return tuple(rt.run_cpu(risky_order_count_by_region, **adjusted))
    if backend == "embree":
        return tuple(rt.run_embree(risky_order_count_by_region, **adjusted))
    if backend == "optix":
        return tuple(rt.run_optix(risky_order_count_by_region, **adjusted))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(risky_order_count_by_region, **adjusted))
    raise ValueError(f"unsupported backend: {backend}")


def _run_grouped_sum_rows(backend: str, case: dict[str, object]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(risky_order_revenue_by_region, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(risky_order_revenue_by_region, **case))
    if backend == "embree":
        return tuple(rt.run_embree(risky_order_revenue_by_region, **case))
    if backend == "optix":
        return tuple(rt.run_optix(risky_order_revenue_by_region, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(risky_order_revenue_by_region, **case))
    raise ValueError(f"unsupported backend: {backend}")


def _prepare_dataset(backend: str, table):
    kwargs = {
        "primary_fields": ("ship_date", "discount", "quantity"),
        "transfer": "columnar",
    }
    if backend == "embree":
        return rt.prepare_embree_db_dataset(table, **kwargs)
    if backend == "optix":
        return rt.prepare_optix_db_dataset(table, **kwargs)
    if backend == "vulkan":
        return rt.prepare_vulkan_db_dataset(table, **kwargs)
    raise ValueError(f"unsupported prepared backend: {backend}")


def _run_prepared_rows(backend: str, scan_case: dict[str, object], grouped_case: dict[str, object]):
    dataset = _prepare_dataset(backend, scan_case["table"])
    try:
        predicates = scan_case["predicates"]
        query = grouped_case["query"]
        count_query = {
            "predicates": query["predicates"],
            "group_keys": query["group_keys"],
        }
        return (
            tuple(dataset.conjunctive_scan(predicates)),
            tuple(dataset.grouped_count(count_query)),
            tuple(dataset.grouped_sum(query)),
            {
                "transfer": dataset._dataset.transfer,
                "row_count": dataset.row_count,
            },
        )
    finally:
        dataset.close()


class PreparedSalesRiskSession:
    def __init__(self, backend: str, copies: int = 1):
        if copies <= 0:
            raise ValueError("copies must be positive")
        self.backend = backend
        self.copies = copies
        case_start = time.perf_counter()
        self.scan_case, self.grouped_case = make_sales_case(copies)
        self.input_construction_sec = time.perf_counter() - case_start
        self._closed = False
        self._dataset = None
        self.prepare_sec = 0.0
        if backend in {"embree", "optix", "vulkan"}:
            prepare_start = time.perf_counter()
            self._dataset = _prepare_dataset(backend, self.scan_case["table"])
            self.prepare_sec = time.perf_counter() - prepare_start

    def __enter__(self) -> "PreparedSalesRiskSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if not self._closed and self._dataset is not None:
            self._dataset.close()
        self._closed = True

    def run(self, output_mode: str = "full") -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared sales-risk session is closed")
        if output_mode not in {"full", "summary", "compact_summary"}:
            raise ValueError(f"unsupported output_mode: {output_mode}")
        prepared_dataset = None
        run_phases: dict[str, float] = {}
        if self.backend in {"embree", "optix", "vulkan"}:
            assert self._dataset is not None
            predicates = self.scan_case["predicates"]
            query = self.grouped_case["query"]
            count_query = {
                "predicates": query["predicates"],
                "group_keys": query["group_keys"],
            }
            if output_mode == "compact_summary" and hasattr(self._dataset, "conjunctive_scan_count"):
                risky_scan_count, run_phases["query_conjunctive_scan_count_sec"] = _timed_call(
                    lambda: self._dataset.conjunctive_scan_count(predicates)
                )
                risky_rows = ()
            else:
                risky_rows, run_phases["query_conjunctive_scan_and_materialize_sec"] = _timed_call(
                    lambda: tuple(self._dataset.conjunctive_scan(predicates))
                )
                risky_scan_count = len(risky_rows)
            count_rows, run_phases["query_grouped_count_and_materialize_sec"] = _timed_call(
                lambda: tuple(self._dataset.grouped_count(count_query))
            )
            sum_rows, run_phases["query_grouped_sum_and_materialize_sec"] = _timed_call(
                lambda: tuple(self._dataset.grouped_sum(query))
            )
            prepared_dataset = {
                "transfer": self._dataset._dataset.transfer,
                "row_count": self._dataset.row_count,
            }
        else:
            risky_rows, run_phases["query_conjunctive_scan_and_materialize_sec"] = _timed_call(
                lambda: _run_scan_rows(self.backend, self.scan_case)
            )
            risky_scan_count = len(risky_rows)
            count_rows, run_phases["query_grouped_count_and_materialize_sec"] = _timed_call(
                lambda: _run_grouped_count_rows(self.backend, self.grouped_case)
            )
            sum_rows, run_phases["query_grouped_sum_and_materialize_sec"] = _timed_call(
                lambda: _run_grouped_sum_rows(self.backend, self.grouped_case)
            )
        postprocess_start = time.perf_counter()
        region_counts = {str(row["region"]): int(row["count"]) for row in count_rows}
        region_revenue = {
            str(row["region"]): int(row["sum"]) if float(row["sum"]).is_integer() else float(row["sum"])
            for row in sum_rows
        }
        risky_order_ids = [int(row["row_id"]) for row in risky_rows]
        highest_risk_region = max(region_counts.items(), key=lambda item: (item[1], item[0]))[0]
        run_phases["python_summary_postprocess_sec"] = time.perf_counter() - postprocess_start
        summary = {
            "risky_order_count": risky_scan_count,
            "risky_order_count_by_region": region_counts,
            "risky_revenue_by_region": region_revenue,
            "highest_risk_region": highest_risk_region,
        }
        if output_mode != "compact_summary":
            summary["risky_order_ids"] = risky_order_ids
        return {
            "app": "sales_risk_screening",
            "backend": self.backend,
            "copies": self.copies,
            "output_mode": output_mode,
            "execution_mode": "prepared_session",
            "session": {
                "input_construction_sec": self.input_construction_sec,
                "prepare_sec": self.prepare_sec,
            },
            "run_phases": run_phases,
            "prepared_dataset": prepared_dataset,
            "summary": summary,
            "row_counts": {
                "scan": risky_scan_count,
                "grouped_count": len(count_rows),
                "grouped_sum": len(sum_rows),
            },
            "rows": {} if output_mode in {"summary", "compact_summary"} else {
                "scan": list(risky_rows),
                "grouped_count": list(count_rows),
                "grouped_sum": list(sum_rows),
            },
        }


def prepare_session(backend: str, copies: int = 1) -> PreparedSalesRiskSession:
    return PreparedSalesRiskSession(backend, copies=copies)


def run_case(backend: str, copies: int = 1, output_mode: str = "full") -> dict[str, object]:
    if output_mode not in {"full", "summary", "compact_summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    if output_mode == "compact_summary" and backend in {"embree", "optix", "vulkan"}:
        with prepare_session(backend, copies=copies) as session:
            return session.run(output_mode=output_mode)
    scan_case, grouped_case = make_sales_case(copies)
    prepared_dataset = None
    if backend in {"embree", "optix", "vulkan"}:
        risky_rows, count_rows, sum_rows, prepared_dataset = _run_prepared_rows(backend, scan_case, grouped_case)
    else:
        risky_rows = _run_scan_rows(backend, scan_case)
        count_rows = _run_grouped_count_rows(backend, grouped_case)
        sum_rows = _run_grouped_sum_rows(backend, grouped_case)
    region_counts = {str(row["region"]): int(row["count"]) for row in count_rows}
    region_revenue = {
        str(row["region"]): int(row["sum"]) if float(row["sum"]).is_integer() else float(row["sum"])
        for row in sum_rows
    }
    return {
        "app": "sales_risk_screening",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "execution_mode": "one_shot",
        "prepared_dataset": prepared_dataset,
        "summary": {
            "risky_order_count": len(risky_rows),
            "risky_order_ids": [int(row["row_id"]) for row in risky_rows],
            "risky_order_count_by_region": region_counts,
            "risky_revenue_by_region": region_revenue,
            "highest_risk_region": max(region_counts.items(), key=lambda item: (item[1], item[0]))[0],
        },
        "row_counts": {
            "scan": len(risky_rows),
            "grouped_count": len(count_rows),
            "grouped_sum": len(sum_rows),
        },
        "rows": {} if output_mode in {"summary", "compact_summary"} else {
            "scan": list(risky_rows),
            "grouped_count": list(count_rows),
            "grouped_sum": list(sum_rows),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="App-style RTDL v0.7 demo: scan risky orders and summarize counts and revenue by region."
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic sales table this many times.")
    parser.add_argument("--output-mode", default="full", choices=("full", "summary", "compact_summary"))
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
