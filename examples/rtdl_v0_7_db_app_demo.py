from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.db_reference import conjunctive_scan_cpu
from rtdsl.db_reference import grouped_count_cpu
from rtdsl.db_reference import grouped_sum_cpu
from rtdsl.db_reference import normalize_denorm_table
from rtdsl.db_reference import normalize_grouped_query
from rtdsl.db_reference import normalize_predicate_bundle


BACKENDS = ("cpu_python_reference", "cpu_reference", "embree", "optix", "vulkan")


def _timed_call(fn):
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _native_db_continuation_backend(backend: str, output_mode: str, run_phases: dict[str, float]) -> str:
    if output_mode != "compact_summary" or backend not in {"embree", "optix", "vulkan"}:
        return "none"
    if any("materialize" in phase for phase in run_phases):
        return "none"
    return f"{backend}_db_compact_summary"


def make_orders(copies: int = 1) -> tuple[dict[str, object], ...]:
    """Small denormalized app table; a real app would load this from its own store."""
    if copies <= 0:
        raise ValueError("copies must be positive")
    base_rows = (
        {"row_id": 1, "region": "east", "channel": "web", "ship_date": 10, "discount": 5, "quantity": 12, "revenue": 120},
        {"row_id": 2, "region": "west", "channel": "store", "ship_date": 11, "discount": 8, "quantity": 30, "revenue": 300},
        {"row_id": 3, "region": "east", "channel": "web", "ship_date": 12, "discount": 6, "quantity": 18, "revenue": 180},
        {"row_id": 4, "region": "west", "channel": "web", "ship_date": 13, "discount": 6, "quantity": 10, "revenue": 150},
        {"row_id": 5, "region": "west", "channel": "web", "ship_date": 13, "discount": 6, "quantity": 8, "revenue": 90},
        {"row_id": 6, "region": "south", "channel": "store", "ship_date": 14, "discount": 3, "quantity": 6, "revenue": 70},
        {"row_id": 7, "region": "east", "channel": "store", "ship_date": 15, "discount": 6, "quantity": 16, "revenue": 160},
    )
    rows: list[dict[str, object]] = []
    for copy_index in range(copies):
        row_id_offset = copy_index * len(base_rows)
        for row in base_rows:
            copied = dict(row)
            copied["row_id"] = int(row["row_id"]) + row_id_offset
            rows.append(copied)
    return tuple(rows)


PROMO_SCAN = (
    ("ship_date", "between", 12, 15),
    ("discount", "eq", 6),
    ("quantity", "lt", 20),
)

REGION_WORKLOAD = {
    "predicates": (
        ("ship_date", "ge", 12),
        ("quantity", "lt", 20),
    ),
    "group_keys": ("region",),
}

REGION_REVENUE = {
    "predicates": (
        ("ship_date", "ge", 12),
        ("channel", "eq", "web"),
    ),
    "group_keys": ("region",),
    "value_field": "revenue",
}


def _sort_rows(rows: tuple[dict[str, object], ...]) -> list[dict[str, object]]:
    def key(row: dict[str, object]) -> tuple[object, ...]:
        if "row_id" in row:
            return (int(row["row_id"]),)
        if "region" in row:
            return (str(row["region"]),)
        return tuple(str(row[name]) for name in sorted(row))

    return sorted((dict(row) for row in rows), key=key)


def _run_cpu_reference(table: tuple[dict[str, object], ...]) -> dict[str, Any]:
    normalized = normalize_denorm_table(table)
    return {
        "promo_order_ids": _sort_rows(conjunctive_scan_cpu(normalized, normalize_predicate_bundle(PROMO_SCAN))),
        "open_order_count_by_region": _sort_rows(grouped_count_cpu(normalized, normalize_grouped_query(REGION_WORKLOAD))),
        "web_revenue_by_region": _sort_rows(grouped_sum_cpu(normalized, normalize_grouped_query(REGION_REVENUE))),
    }


def _prepare_dataset(backend: str, table: tuple[dict[str, object], ...]):
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


def _run_prepared_backend(backend: str, table: tuple[dict[str, object], ...]) -> dict[str, Any]:
    dataset = _prepare_dataset(backend, table)
    try:
        return {
            "prepared_transfer": dataset._dataset.transfer,
            "prepared_row_count": dataset.row_count,
            "promo_order_ids": _sort_rows(dataset.conjunctive_scan(PROMO_SCAN)),
            "open_order_count_by_region": _sort_rows(dataset.grouped_count(REGION_WORKLOAD)),
            "web_revenue_by_region": _sort_rows(dataset.grouped_sum(REGION_REVENUE)),
        }
    finally:
        dataset.close()


class PreparedRegionalDashboardSession:
    def __init__(self, backend: str, copies: int = 1):
        if copies <= 0:
            raise ValueError("copies must be positive")
        self.requested_backend = backend
        self.copies = copies
        table_start = time.perf_counter()
        self.table = make_orders(copies)
        self.table_construction_sec = time.perf_counter() - table_start
        select_start = time.perf_counter()
        self.backend, self.fallback_note = choose_backend(backend, self.table)
        self.backend_selection_sec = time.perf_counter() - select_start
        self._closed = False
        self._dataset = None
        self.prepare_sec = 0.0
        if self.backend != "cpu_reference":
            prepare_start = time.perf_counter()
            self._dataset = _prepare_dataset(self.backend, self.table)
            self.prepare_sec = time.perf_counter() - prepare_start

    def __enter__(self) -> "PreparedRegionalDashboardSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if not self._closed and self._dataset is not None:
            self._dataset.close()
        self._closed = True

    def run(self, output_mode: str = "full") -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("prepared regional dashboard session is closed")
        if output_mode not in {"full", "summary", "compact_summary"}:
            raise ValueError(f"unsupported output_mode: {output_mode}")
        run_phases: dict[str, float] = {}
        native_db_phases: dict[str, object] = {}
        if self.backend == "cpu_reference":
            results, run_phases["cpu_reference_execute_and_postprocess_sec"] = _timed_call(
                lambda: _run_cpu_reference(self.table)
            )
            prepared_summary = None
        else:
            assert self._dataset is not None
            compact_group_count_summary = None
            compact_group_sum_summary = None
            if output_mode == "compact_summary" and hasattr(self._dataset, "conjunctive_scan_count"):
                promo_order_count, run_phases["query_conjunctive_scan_count_sec"] = _timed_call(
                    lambda: self._dataset.conjunctive_scan_count(PROMO_SCAN)
                )
                promo_order_ids = []
                if hasattr(self._dataset, "last_phase_timings"):
                    native_db_phases["conjunctive_scan_count"] = self._dataset.last_phase_timings()
            else:
                promo_order_ids, run_phases["query_conjunctive_scan_and_materialize_sec"] = _timed_call(
                    lambda: _sort_rows(self._dataset.conjunctive_scan(PROMO_SCAN))
                )
                promo_order_count = len(promo_order_ids)
                if hasattr(self._dataset, "last_phase_timings"):
                    native_db_phases["conjunctive_scan"] = self._dataset.last_phase_timings()
            if output_mode == "compact_summary" and hasattr(self._dataset, "grouped_count_summary"):
                compact_group_count_summary, run_phases["query_grouped_count_summary_sec"] = _timed_call(
                    lambda: self._dataset.grouped_count_summary(REGION_WORKLOAD)
                )
                open_order_count_by_region = []
                if hasattr(self._dataset, "last_phase_timings"):
                    native_db_phases["grouped_count_summary"] = self._dataset.last_phase_timings()
            else:
                open_order_count_by_region, run_phases["query_grouped_count_and_materialize_sec"] = _timed_call(
                    lambda: _sort_rows(self._dataset.grouped_count(REGION_WORKLOAD))
                )
                if hasattr(self._dataset, "last_phase_timings"):
                    native_db_phases["grouped_count"] = self._dataset.last_phase_timings()
            if output_mode == "compact_summary" and hasattr(self._dataset, "grouped_sum_summary"):
                compact_group_sum_summary, run_phases["query_grouped_sum_summary_sec"] = _timed_call(
                    lambda: self._dataset.grouped_sum_summary(REGION_REVENUE)
                )
                web_revenue_by_region = []
                if hasattr(self._dataset, "last_phase_timings"):
                    native_db_phases["grouped_sum_summary"] = self._dataset.last_phase_timings()
            else:
                web_revenue_by_region, run_phases["query_grouped_sum_and_materialize_sec"] = _timed_call(
                    lambda: _sort_rows(self._dataset.grouped_sum(REGION_REVENUE))
                )
                if hasattr(self._dataset, "last_phase_timings"):
                    native_db_phases["grouped_sum"] = self._dataset.last_phase_timings()
            results = {
                "promo_order_ids": promo_order_ids,
                "open_order_count_by_region": open_order_count_by_region,
                "web_revenue_by_region": web_revenue_by_region,
            }
            prepared_summary = {
                "transfer": self._dataset._dataset.transfer,
                "row_count": self._dataset.row_count,
            }
        summary_start = time.perf_counter()
        if (
            self.backend != "cpu_reference"
            and output_mode == "compact_summary"
            and compact_group_count_summary is not None
            and compact_group_sum_summary is not None
        ):
            summary = {
                "promo_order_count": promo_order_count,
                "open_order_count_by_region": dict(compact_group_count_summary),
                "web_revenue_by_region": dict(compact_group_sum_summary),
            }
        else:
            summary = _summarize_results(results)
            if self.backend != "cpu_reference" and output_mode == "compact_summary":
                summary["promo_order_count"] = promo_order_count
        run_phases["python_summary_postprocess_sec"] = time.perf_counter() - summary_start
        native_continuation_backend = _native_db_continuation_backend(self.backend, output_mode, run_phases)

        return {
            "app": "regional_order_dashboard",
            "requested_backend": self.requested_backend,
            "backend": self.backend,
            "copies": self.copies,
            "output_mode": output_mode,
            "fallback_note": self.fallback_note,
            "execution_mode": "prepared_session",
            "session": {
                "table_construction_sec": self.table_construction_sec,
                "backend_selection_sec": self.backend_selection_sec,
                "prepare_sec": self.prepare_sec,
            },
            "run_phases": run_phases,
            "native_db_phases": native_db_phases,
            "native_continuation_active": native_continuation_backend != "none",
            "native_continuation_backend": native_continuation_backend,
            "data_flow": [
                "app order rows",
                "RTDL v0.7 bounded DB workload",
                "reused prepared RT dataset over encoded row boxes" if self.backend != "cpu_reference" else "reused CPU reference evaluator input",
                "application-ready JSON rows",
            ],
            "input_table": {
                "row_count": len(self.table),
                "fields": sorted(self.table[0]),
            },
            "queries": {
                "promo_order_ids": {
                    "operation": "conjunctive_scan",
                    "predicates": PROMO_SCAN,
                    "meaning": "Which discounted small-quantity orders shipped during the campaign window?",
                },
                "open_order_count_by_region": {
                    "operation": "grouped_count",
                    "query": REGION_WORKLOAD,
                    "meaning": "How many small post-window orders remain by region?",
                },
                "web_revenue_by_region": {
                    "operation": "grouped_sum",
                    "query": REGION_REVENUE,
                    "meaning": "How much web-channel revenue is covered by region?",
                },
            },
            "prepared_dataset": prepared_summary,
            "results": results if output_mode == "full" else {},
            "summary": summary,
            "honesty_boundary": "Demo of bounded v0.7 DB kernels; not a SQL engine, optimizer, transaction system, or DBMS.",
        }


def prepare_session(backend: str, copies: int = 1) -> PreparedRegionalDashboardSession:
    return PreparedRegionalDashboardSession(backend, copies=copies)


def _canonical_backend(backend: str) -> str:
    if backend == "cpu_python_reference":
        return "cpu_reference"
    return backend


def choose_backend(requested: str, table: tuple[dict[str, object], ...]) -> tuple[str, str | None]:
    if requested != "auto":
        return _canonical_backend(requested), None
    for backend in ("embree", "optix", "vulkan"):
        try:
            dataset = _prepare_dataset(backend, table)
            dataset.close()
            return backend, None
        except Exception as exc:
            last_error = f"{backend}: {exc}"
    return "cpu_reference", f"no RT backend prepared successfully; using CPU reference ({last_error})"


def _summarize_results(results: dict[str, Any]) -> dict[str, Any]:
    promo_order_ids = results["promo_order_ids"]
    counts = {str(row["region"]): int(row["count"]) for row in results["open_order_count_by_region"]}
    revenue = {
        str(row["region"]): int(row["sum"]) if float(row["sum"]).is_integer() else float(row["sum"])
        for row in results["web_revenue_by_region"]
    }
    return {
        "promo_order_count": len(promo_order_ids),
        "open_order_count_by_region": counts,
        "web_revenue_by_region": revenue,
    }


def run_app(backend: str, copies: int = 1, output_mode: str = "full") -> dict[str, Any]:
    if output_mode not in {"full", "summary", "compact_summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    if output_mode == "compact_summary" and _canonical_backend(backend) != "cpu_reference":
        with prepare_session(backend, copies=copies) as session:
            return session.run(output_mode=output_mode)
    table = make_orders(copies)
    selected_backend, fallback_note = choose_backend(backend, table)
    if selected_backend == "cpu_reference":
        results = _run_cpu_reference(table)
        prepared_summary = None
    else:
        results = _run_prepared_backend(selected_backend, table)
        prepared_summary = {
            "transfer": results.pop("prepared_transfer"),
            "row_count": results.pop("prepared_row_count"),
        }

    return {
        "app": "regional_order_dashboard",
        "requested_backend": backend,
        "backend": selected_backend,
        "copies": copies,
        "output_mode": output_mode,
        "execution_mode": "one_shot",
        "fallback_note": fallback_note,
        "data_flow": [
            "app order rows",
            "RTDL v0.7 bounded DB workload",
            "prepared RT dataset over encoded row boxes" if selected_backend != "cpu_reference" else "CPU reference evaluator",
            "application-ready JSON rows",
        ],
        "input_table": {
            "row_count": len(table),
            "fields": sorted(table[0]),
        },
        "queries": {
            "promo_order_ids": {
                "operation": "conjunctive_scan",
                "predicates": PROMO_SCAN,
                "meaning": "Which discounted small-quantity orders shipped during the campaign window?",
            },
            "open_order_count_by_region": {
                "operation": "grouped_count",
                "query": REGION_WORKLOAD,
                "meaning": "How many small post-window orders remain by region?",
            },
            "web_revenue_by_region": {
                "operation": "grouped_sum",
                "query": REGION_REVENUE,
                "meaning": "How much web-channel revenue is covered by region?",
            },
        },
        "prepared_dataset": prepared_summary,
        "native_continuation_active": False,
        "native_continuation_backend": "none",
        "results": results if output_mode == "full" else {},
        "summary": _summarize_results(results),
        "honesty_boundary": "Demo of bounded v0.7 DB kernels; not a SQL engine, optimizer, transaction system, or DBMS.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RTDL v0.7 app demo for bounded DB workloads.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("auto", *BACKENDS),
        help="Use the CPU reference everywhere, or run a prepared RT backend when available.",
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic order table this many times.")
    parser.add_argument("--output-mode", default="full", choices=("full", "summary", "compact_summary"))
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
