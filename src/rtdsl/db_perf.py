from __future__ import annotations

import hashlib
import json
import time

from . import connect_postgresql
from . import prepare_postgresql_denorm_table
from . import query_postgresql_conjunctive_scan
from . import query_postgresql_grouped_count
from . import query_postgresql_grouped_sum
from . import run_cpu
from . import run_cpu_python_reference
from . import run_embree
from . import run_optix
from . import run_vulkan
from . import run_postgresql_conjunctive_scan
from . import run_postgresql_grouped_count
from . import run_postgresql_grouped_sum
from .db_reference import normalize_grouped_query
from .api import emit
from .api import grouped_count
from .api import grouped_sum
from .api import input
from .api import kernel
from .api import refine
from .api import traverse
from .layout_types import DenormTable
from .layout_types import GroupedQuery
from .layout_types import PredicateSet


@kernel(backend="rtdl", precision="float_approx")
def db_perf_conjunctive_scan_reference():
    predicates = input("predicates", PredicateSet, role="probe")
    table = input("table", DenormTable, role="build")
    candidates = traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = refine(candidates, predicate=__import__("rtdsl").conjunctive_scan(exact=True))
    return emit(matches, fields=["row_id"])


@kernel(backend="rtdl", precision="float_approx")
def db_perf_grouped_count_reference():
    query = input("query", GroupedQuery, role="probe")
    table = input("table", DenormTable, role="build")
    candidates = traverse(query, table, accel="bvh", mode="db_group")
    groups = refine(candidates, predicate=grouped_count(group_keys=("region",)))
    return emit(groups, fields=["region", "count"])


@kernel(backend="rtdl", precision="float_approx")
def db_perf_grouped_sum_reference():
    query = input("query", GroupedQuery, role="probe")
    table = input("table", DenormTable, role="build")
    candidates = traverse(query, table, accel="bvh", mode="db_group")
    groups = refine(candidates, predicate=grouped_sum(group_keys=("region",), value_field="revenue"))
    return emit(groups, fields=["region", "sum"])


def median_seconds(samples: list[float]) -> float:
    ordered = sorted(float(value) for value in samples)
    if not ordered:
        raise ValueError("median_seconds requires at least one sample")
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def hash_rows(rows) -> str:
    payload = json.dumps(list(rows), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_sales_perf_table(row_count: int) -> tuple[dict[str, object], ...]:
    if row_count <= 0:
        raise ValueError("row_count must be positive")
    regions = ("east", "west", "north", "south", "central", "coastal", "mountain", "metro")
    rows = []
    for index in range(row_count):
        row_id = index + 1
        ship_date = 1 + (index % 365)
        discount = 1 + ((index * 7) % 10)
        quantity = 1 + ((index * 11) % 40)
        revenue = 10 + ((index * 13) % 500)
        region = regions[(index * 5) % len(regions)]
        rows.append(
            {
                "row_id": row_id,
                "region": region,
                "ship_date": ship_date,
                "discount": discount,
                "quantity": quantity,
                "revenue": revenue,
            }
        )
    return tuple(rows)


def make_conjunctive_scan_case(row_count: int) -> dict[str, object]:
    return {
        "table": make_sales_perf_table(row_count),
        "predicates": (
            ("ship_date", "between", 40, 220),
            ("discount", "between", 3, 7),
            ("quantity", "lt", 20),
        ),
    }


def make_grouped_count_case(row_count: int) -> dict[str, object]:
    return {
        "table": make_sales_perf_table(row_count),
        "query": {
            "predicates": (
                ("ship_date", "between", 40, 220),
                ("quantity", "lt", 20),
            ),
            "group_keys": ("region",),
        },
    }


def make_grouped_sum_case(row_count: int) -> dict[str, object]:
    return {
        "table": make_sales_perf_table(row_count),
        "query": {
            "predicates": (
                ("ship_date", "ge", 60),
                ("discount", "le", 8),
            ),
            "group_keys": ("region",),
            "value_field": "revenue",
        },
    }


def _backend_runner(backend_name: str):
    if backend_name == "embree":
        return run_embree
    if backend_name == "optix":
        return run_optix
    if backend_name == "vulkan":
        return run_vulkan
    raise ValueError(f"unsupported backend family {backend_name!r}")


def measure_backend_family(
    kernel_fn,
    inputs: dict[str, object],
    *,
    repeats: int = 3,
    backend_name: str = "embree",
) -> dict[str, object]:
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    backend_runner = _backend_runner(backend_name)
    reference_rows = run_cpu_python_reference(kernel_fn, **inputs)
    cpu_rows = run_cpu(kernel_fn, **inputs)
    backend_rows = backend_runner(kernel_fn, **inputs)
    if cpu_rows != reference_rows:
        raise AssertionError("CPU oracle rows do not match Python truth")
    if backend_rows != reference_rows:
        raise AssertionError(f"{backend_name} rows do not match Python truth")

    cpu_samples = []
    backend_samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        cpu_again = run_cpu(kernel_fn, **inputs)
        cpu_samples.append(time.perf_counter() - start)
        if cpu_again != reference_rows:
            raise AssertionError("CPU oracle drifted during timing")

        start = time.perf_counter()
        backend_again = backend_runner(kernel_fn, **inputs)
        backend_samples.append(time.perf_counter() - start)
        if backend_again != reference_rows:
            raise AssertionError(f"{backend_name} drifted during timing")

    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        "cpu_seconds_samples": tuple(cpu_samples),
        "cpu_seconds_median": median_seconds(cpu_samples),
        f"{backend_name}_seconds_samples": tuple(backend_samples),
        f"{backend_name}_seconds_median": median_seconds(backend_samples),
    }


def measure_postgresql_conjunctive_scan(table_rows, predicates, *, dsn: str, repeats: int = 3) -> dict[str, object]:
    setup_samples = []
    query_samples = []
    reference_rows = None
    for repeat_index in range(repeats):
        table_name = f"rtdl_denorm_table_tmp_scan_{repeat_index}"
        with connect_postgresql(dsn) as connection:
            start = time.perf_counter()
            prepare_postgresql_denorm_table(connection, table_rows, predicates, table_name=table_name)
            setup_samples.append(time.perf_counter() - start)
            start = time.perf_counter()
            rows = query_postgresql_conjunctive_scan(connection, predicates, table_name=table_name)
            query_samples.append(time.perf_counter() - start)
        if reference_rows is None:
            reference_rows = rows
        elif rows != reference_rows:
            raise AssertionError("PostgreSQL conjunctive scan drifted across repeats")
    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        "postgresql_setup_seconds_samples": tuple(setup_samples),
        "postgresql_setup_seconds_median": median_seconds(setup_samples),
        "postgresql_query_seconds_samples": tuple(query_samples),
        "postgresql_query_seconds_median": median_seconds(query_samples),
    }


def measure_postgresql_grouped_count(table_rows, query, *, dsn: str, repeats: int = 3) -> dict[str, object]:
    setup_samples = []
    query_samples = []
    reference_rows = None
    for repeat_index in range(repeats):
        table_name = f"rtdl_denorm_table_tmp_gcount_{repeat_index}"
        normalized_query = normalize_grouped_query(query)
        with connect_postgresql(dsn) as connection:
            start = time.perf_counter()
            prepare_postgresql_denorm_table(connection, table_rows, normalized_query.predicates, table_name=table_name)
            setup_samples.append(time.perf_counter() - start)
            if hasattr(connection, "_rtdl_fake_db"):
                connection._rtdl_fake_grouped_query = normalized_query
            start = time.perf_counter()
            rows = query_postgresql_grouped_count(connection, normalized_query, table_name=table_name)
            query_samples.append(time.perf_counter() - start)
        if reference_rows is None:
            reference_rows = rows
        elif rows != reference_rows:
            raise AssertionError("PostgreSQL grouped_count drifted across repeats")
    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        "postgresql_setup_seconds_samples": tuple(setup_samples),
        "postgresql_setup_seconds_median": median_seconds(setup_samples),
        "postgresql_query_seconds_samples": tuple(query_samples),
        "postgresql_query_seconds_median": median_seconds(query_samples),
    }


def measure_postgresql_grouped_sum(table_rows, query, *, dsn: str, repeats: int = 3) -> dict[str, object]:
    setup_samples = []
    query_samples = []
    reference_rows = None
    for repeat_index in range(repeats):
        table_name = f"rtdl_denorm_table_tmp_gsum_{repeat_index}"
        normalized_query = normalize_grouped_query(query)
        with connect_postgresql(dsn) as connection:
            start = time.perf_counter()
            prepare_postgresql_denorm_table(connection, table_rows, normalized_query.predicates, table_name=table_name)
            setup_samples.append(time.perf_counter() - start)
            if hasattr(connection, "_rtdl_fake_db"):
                connection._rtdl_fake_grouped_query = normalized_query
            start = time.perf_counter()
            rows = query_postgresql_grouped_sum(connection, normalized_query, table_name=table_name)
            query_samples.append(time.perf_counter() - start)
        if reference_rows is None:
            reference_rows = rows
        elif rows != reference_rows:
            raise AssertionError("PostgreSQL grouped_sum drifted across repeats")
    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        "postgresql_setup_seconds_samples": tuple(setup_samples),
        "postgresql_setup_seconds_median": median_seconds(setup_samples),
        "postgresql_query_seconds_samples": tuple(query_samples),
        "postgresql_query_seconds_median": median_seconds(query_samples),
    }
