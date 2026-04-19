from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def conjunctive_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"))
    return rt.emit(groups, fields=["region", "sum"])


WORKLOADS = {
    "conjunctive_scan": {
        "kernel": conjunctive_scan_kernel,
        "probe_name": "predicates",
        "probe": (("ship_date", "between", 12, 20), ("discount", "eq", 6), ("quantity", "lt", 30)),
    },
    "grouped_count": {
        "kernel": grouped_count_kernel,
        "probe_name": "query",
        "probe": {"group_keys": ("region",), "predicates": (("discount", "ge", 5), ("quantity", "lt", 40))},
    },
    "grouped_sum": {
        "kernel": grouped_sum_kernel,
        "probe_name": "query",
        "probe": {
            "group_keys": ("region",),
            "value_field": "revenue",
            "predicates": (("discount", "ge", 5), ("quantity", "lt", 40)),
        },
    },
}


def make_table(row_count: int) -> tuple[dict[str, object], ...]:
    regions = ("east", "west", "north", "south")
    return tuple(
        {
            "row_id": index + 1,
            "region": regions[index % len(regions)],
            "ship_date": index % 31,
            "discount": index % 10,
            "quantity": (index * 7) % 50,
            "revenue": 50 + ((index * 13) % 1000),
        }
        for index in range(row_count)
    )


def median_seconds(fn, iterations: int) -> tuple[float, object]:
    samples = []
    last = None
    for _ in range(iterations):
        start = time.perf_counter()
        last = fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples), last


def run_cpu(workload, table, iterations):
    return median_seconds(
        lambda: rt.run_cpu_python_reference(workload["kernel"], table=table, **{workload["probe_name"]: workload["probe"]}),
        iterations,
    )


def run_backend(name: str, workload, table, iterations):
    runner = {
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
        "hiprt_one_shot": rt.run_hiprt,
    }[name]
    return median_seconds(
        lambda: runner(workload["kernel"], table=table, **{workload["probe_name"]: workload["probe"]}),
        iterations,
    )


def run_prepared_hiprt(workload, table, iterations):
    start = time.perf_counter()
    prepared = rt.prepare_hiprt(workload["kernel"], table=table)
    prepare_seconds = time.perf_counter() - start
    try:
        query_seconds, rows = median_seconds(
            lambda: prepared.run(**{workload["probe_name"]: workload["probe"]}),
            iterations,
        )
    finally:
        prepared.close()
    return prepare_seconds, query_seconds, rows


def run_postgresql(workload_name: str, workload, table, iterations: int, dsn: str):
    if not rt.postgresql_available():
        return {"available": False, "error": "psycopg2 is not installed"}
    table_name = f"rtdl_goal568_{workload_name}"
    connection = rt.connect_postgresql(dsn)
    try:
        start = time.perf_counter()
        if workload_name == "conjunctive_scan":
            rt.prepare_postgresql_denorm_table(connection, table, workload["probe"], table_name=table_name)
            query_fn = lambda: rt.query_postgresql_conjunctive_scan(connection, workload["probe"], table_name=table_name)
        elif workload_name == "grouped_count":
            query = rt.normalize_grouped_query(workload["probe"])
            rt.prepare_postgresql_denorm_table(connection, table, query.predicates, table_name=table_name)
            query_fn = lambda: rt.query_postgresql_grouped_count(connection, query, table_name=table_name)
        else:
            query = rt.normalize_grouped_query(workload["probe"])
            rt.prepare_postgresql_denorm_table(connection, table, query.predicates, table_name=table_name)
            query_fn = lambda: rt.query_postgresql_grouped_sum(connection, query, table_name=table_name)
        setup_seconds = time.perf_counter() - start
        query_seconds, rows = median_seconds(query_fn, iterations)
        return {
            "available": True,
            "setup_seconds": setup_seconds,
            "query_seconds": query_seconds,
            "rows": rows,
        }
    except Exception as exc:
        return {"available": False, "error": repr(exc)}
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--postgresql-dsn", default="dbname=postgres")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    table = make_table(args.rows)
    result = {
        "goal": 568,
        "host": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "rows": args.rows,
        "iterations": args.iterations,
        "workloads": {},
    }
    for workload_name, workload in WORKLOADS.items():
        cpu_seconds, expected = run_cpu(workload, table, args.iterations)
        entry = {
            "cpu_python_seconds": cpu_seconds,
            "expected_row_count": len(expected),
            "backends": {},
        }
        for backend in ("embree", "optix", "vulkan", "hiprt_one_shot"):
            try:
                seconds, rows = run_backend(backend, workload, table, args.iterations)
                entry["backends"][backend] = {
                    "available": True,
                    "seconds": seconds,
                    "matches_cpu": rows == expected,
                    "row_count": len(rows),
                }
            except Exception as exc:
                entry["backends"][backend] = {"available": False, "error": repr(exc)}
        try:
            prepare_seconds, query_seconds, rows = run_prepared_hiprt(workload, table, args.iterations)
            entry["backends"]["hiprt_prepared"] = {
                "available": True,
                "prepare_seconds": prepare_seconds,
                "query_seconds": query_seconds,
                "matches_cpu": rows == expected,
                "row_count": len(rows),
            }
            one_shot = entry["backends"]["hiprt_one_shot"]
            if one_shot.get("available"):
                entry["backends"]["hiprt_prepared"]["speedup_vs_hiprt_one_shot"] = (
                    one_shot["seconds"] / query_seconds if query_seconds else None
                )
        except Exception as exc:
            entry["backends"]["hiprt_prepared"] = {"available": False, "error": repr(exc)}
        entry["backends"]["postgresql_indexed"] = run_postgresql(
            workload_name,
            workload,
            table,
            args.iterations,
            args.postgresql_dsn,
        )
        if entry["backends"]["postgresql_indexed"].get("available"):
            entry["backends"]["postgresql_indexed"]["matches_cpu"] = (
                tuple(entry["backends"]["postgresql_indexed"].pop("rows")) == expected
            )
        result["workloads"][workload_name] = entry

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
