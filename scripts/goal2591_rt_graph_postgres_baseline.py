from __future__ import annotations

import argparse
import json
import os
import re
import struct
import subprocess
import time
from pathlib import Path


POSTGRES_QUERY = """
EXPLAIN (ANALYZE, TIMING OFF, SUMMARY ON, FORMAT TEXT)
SELECT count(*)
FROM edges e1
JOIN edges e2 ON e1.u = e2.u AND e1.v < e2.v
JOIN edges e3 ON e3.u = e1.v AND e3.v = e2.v;
"""

POSTGRES_COUNT_QUERY = """
SELECT count(*)
FROM edges e1
JOIN edges e2 ON e1.u = e2.u AND e1.v < e2.v
JOIN edges e3 ON e3.u = e1.v AND e3.v = e2.v;
"""


def _run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=input_text,
        check=True,
        capture_output=True,
        text=True,
    )


def _psql(database: str, sql: str, *, tuples_only: bool = False) -> str:
    command = [
        "sudo",
        "-u",
        "postgres",
        "psql",
        "-v",
        "ON_ERROR_STOP=1",
        "-d",
        database,
        "-q",
    ]
    if tuples_only:
        command.append("-At")
    return _run(command, input_text=sql).stdout


def _write_tsv(edge_file: Path, tsv_file: Path) -> int:
    data = edge_file.read_bytes()
    edge_count = 0
    with tsv_file.open("w", encoding="ascii") as output:
        for src, dst in struct.iter_unpack("<ii", data):
            output.write(f"{src}\t{dst}\n")
            edge_count += 1
    os.chmod(tsv_file, 0o644)
    return edge_count


def run_one(name: str, edge_file: Path, *, tmp_dir: Path) -> dict[str, object]:
    tsv_file = tmp_dir / f"{name}.tsv"
    t0 = time.perf_counter()
    input_edges = _write_tsv(edge_file, tsv_file)
    t1 = time.perf_counter()

    _psql(
        "rtdl_tc",
        f"""
DROP TABLE IF EXISTS raw_edges;
DROP TABLE IF EXISTS edges;
CREATE UNLOGGED TABLE raw_edges(src integer NOT NULL, dst integer NOT NULL);
COPY raw_edges FROM '{tsv_file}' WITH (FORMAT text);
CREATE UNLOGGED TABLE edges AS
  SELECT DISTINCT LEAST(src, dst) AS u, GREATEST(src, dst) AS v
  FROM raw_edges
  WHERE src <> dst;
""",
    )
    t2 = time.perf_counter()

    _psql(
        "rtdl_tc",
        """
CREATE UNIQUE INDEX edges_uv_idx ON edges(u, v);
CREATE INDEX edges_vu_idx ON edges(v, u);
ANALYZE edges;
""",
    )
    t3 = time.perf_counter()

    explain = _psql("rtdl_tc", POSTGRES_QUERY)
    t4 = time.perf_counter()
    count = int(_psql("rtdl_tc", POSTGRES_COUNT_QUERY, tuples_only=True).strip())
    t5 = time.perf_counter()
    distinct_edges = int(_psql("rtdl_tc", "SELECT count(*) FROM edges;\n", tuples_only=True).strip())

    execution_match = re.search(r"Execution Time: ([0-9.]+) ms", explain)
    planning_match = re.search(r"Planning Time: ([0-9.]+) ms", explain)
    return {
        "input_file": str(edge_file),
        "input_bytes": edge_file.stat().st_size,
        "input_edges": input_edges,
        "distinct_edges": distinct_edges,
        "triangle_count": count,
        "convert_tsv_ms": (t1 - t0) * 1000.0,
        "load_dedup_ms": (t2 - t1) * 1000.0,
        "index_analyze_ms": (t3 - t2) * 1000.0,
        "explain_wall_ms": (t4 - t3) * 1000.0,
        "query_recheck_wall_ms": (t5 - t4) * 1000.0,
        "postgres_execution_ms": float(execution_match.group(1)) if execution_match else None,
        "postgres_planning_ms": float(planning_match.group(1)) if planning_match else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run indexed PostgreSQL triangle-counting baseline.")
    parser.add_argument("--input", action="append", nargs=2, metavar=("NAME", "EDGE_FILE"), required=True)
    parser.add_argument("--database", default="rtdl_tc")
    parser.add_argument("--tmp-dir", default="/tmp")
    args = parser.parse_args()

    subprocess.run(
        ["pg_ctlcluster", "16", "main", "start"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _psql("postgres", f"DROP DATABASE IF EXISTS {args.database};\n")
    _psql("postgres", f"CREATE DATABASE {args.database};\n")

    tmp_dir = Path(args.tmp_dir)
    results = {
        name: run_one(name, Path(edge_file), tmp_dir=tmp_dir)
        for name, edge_file in args.input
    }
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
