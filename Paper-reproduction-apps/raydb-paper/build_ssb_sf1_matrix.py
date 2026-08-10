from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Sequence


DBGEN_REPOSITORY = "https://github.com/vadimtk/ssb-dbgen"
DBGEN_COMMIT = "0741e06d4c3e811bcec233378a39db2fc0be5d79"
GENERATION_PROFILE = (
    "ssb_dbgen_default_customer_supplier_then_individual_part_date_lineorder_v1"
)

LINEORDER_COLUMNS = {
    "lo_orderkey": "BIGINT", "lo_linenumber": "INTEGER", "lo_custkey": "INTEGER",
    "lo_partkey": "INTEGER", "lo_suppkey": "INTEGER", "lo_orderdate": "VARCHAR",
    "lo_orderpriority": "VARCHAR", "lo_shippriority": "INTEGER", "lo_quantity": "INTEGER",
    "lo_extendedprice": "INTEGER", "lo_ordtotalprice": "INTEGER", "lo_discount": "INTEGER",
    "lo_revenue": "INTEGER", "lo_supplycost": "INTEGER", "lo_tax": "INTEGER",
    "lo_commitdate": "VARCHAR", "lo_shipmode": "VARCHAR", "trailing": "VARCHAR",
}
CUSTOMER_COLUMNS = {
    "c_custkey": "INTEGER", "c_name": "VARCHAR", "c_address": "VARCHAR", "c_city": "VARCHAR",
    "c_nation": "VARCHAR", "c_region": "VARCHAR", "c_phone": "VARCHAR",
    "c_mktsegment": "VARCHAR", "trailing": "VARCHAR",
}
SUPPLIER_COLUMNS = {
    "s_suppkey": "INTEGER", "s_name": "VARCHAR", "s_address": "VARCHAR", "s_city": "VARCHAR",
    "s_nation": "VARCHAR", "s_region": "VARCHAR", "s_phone": "VARCHAR", "trailing": "VARCHAR",
}
PART_COLUMNS = {
    "p_partkey": "INTEGER", "p_name": "VARCHAR", "p_mfgr": "VARCHAR", "p_category": "VARCHAR",
    "p_brand1": "VARCHAR", "p_color": "VARCHAR", "p_type": "VARCHAR", "p_size": "INTEGER",
    "p_container": "VARCHAR", "trailing": "VARCHAR",
}

NATIONS = (
    "ALGERIA", "ARGENTINA", "BRAZIL", "CANADA", "EGYPT", "ETHIOPIA", "FRANCE",
    "GERMANY", "INDIA", "INDONESIA", "IRAN", "IRAQ", "JAPAN", "JORDAN", "KENYA",
    "MOROCCO", "MOZAMBIQUE", "PERU", "CHINA", "ROMANIA", "SAUDI ARABIA", "VIETNAM",
    "RUSSIA", "UNITED KINGDOM", "UNITED STATES",
)
REGIONS = ("AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST")


def _case_code(column: str, values: Sequence[str]) -> str:
    clauses = " ".join(f"WHEN {column} = '{value}' THEN {index}" for index, value in enumerate(values))
    return f"CASE {clauses} ELSE error('unrecognized categorical value') END"


NATION_CODE = {prefix: _case_code(f"{prefix}_nation", NATIONS) for prefix in ("c", "s")}
REGION_CODE = {prefix: _case_code(f"{prefix}_region", REGIONS) for prefix in ("c", "s")}
CITY_CODE = {
    prefix: f"(({NATION_CODE[prefix]}) * 10 + CAST(right({prefix}_city, 1) AS INTEGER))"
    for prefix in ("c", "s")
}
YEAR = "CAST(substr(lo_orderdate, 1, 4) AS INTEGER)"
YEARMONTH = "CAST(replace(substr(lo_orderdate, 1, 7), '-', '') AS INTEGER)"
ISO_WEEK = "CAST(week(CAST(lo_orderdate AS DATE)) AS INTEGER)"
PART_MFGR = "CAST(substr(p_mfgr, 6) AS INTEGER)"
PART_CATEGORY = "CAST(substr(p_category, 6) AS INTEGER)"
PART_BRAND = "CAST(substr(p_brand1, 6) AS INTEGER)"


@dataclass(frozen=True)
class QuerySpec:
    query_id: str
    interval_x: int
    interval_y: int
    aggregate: str
    groups: tuple[str, ...]
    scans: tuple[str, ...]
    predicate_lines: tuple[str, ...]
    scan_types: tuple[int, ...]
    filter_sql: str
    joins: tuple[str, ...] = ()
    extra_multiplier: str | None = None


QUERY_SPECS = (
    QuerySpec("q11", 6, 1, "lo_extendedprice", ("0",), (YEAR, "lo_discount", "lo_quantity"),
              ("1993", "1,3", "1,24"), (1, 0, 0),
              f"{YEAR}=1993 AND lo_discount BETWEEN 1 AND 3 AND lo_quantity BETWEEN 1 AND 24",
              extra_multiplier="lo_discount"),
    QuerySpec("q12", 100, 1, "lo_extendedprice", ("0",), (YEARMONTH, "lo_discount", "lo_quantity"),
              ("199401", "4,6", "26,35"), (1, 0, 0),
              f"{YEARMONTH}=199401 AND lo_discount BETWEEN 4 AND 6 AND lo_quantity BETWEEN 26 AND 35",
              extra_multiplier="lo_discount"),
    QuerySpec("q13", 200, 1, "lo_extendedprice", ("0",), (ISO_WEEK, YEAR, "lo_discount", "lo_quantity"),
              ("6", "1994", "5,7", "26,35"), (1, 1, 0, 0),
              f"{ISO_WEEK}=6 AND {YEAR}=1994 AND lo_discount BETWEEN 5 AND 7 AND lo_quantity BETWEEN 26 AND 35",
              extra_multiplier="lo_discount"),
    QuerySpec("q21", 2000, 14, "lo_revenue", (YEAR, PART_BRAND), (PART_CATEGORY, REGION_CODE["s"]),
              ("12", "1"), (1, 1), f"{PART_CATEGORY}=12 AND {REGION_CODE['s']}=1", ("part", "supplier")),
    QuerySpec("q22", 2000, 350, "lo_revenue", (YEAR, PART_BRAND), (REGION_CODE["s"], PART_BRAND),
              ("2", "2221,2228"), (1, 0), f"{REGION_CODE['s']}=2 AND {PART_BRAND} BETWEEN 2221 AND 2228", ("part", "supplier")),
    QuerySpec("q23", 2000, 140, "lo_revenue", (YEAR, PART_BRAND), (REGION_CODE["s"], PART_BRAND),
              ("3", "2239"), (1, 1), f"{REGION_CODE['s']}=3 AND {PART_BRAND}=2239", ("part", "supplier")),
    QuerySpec("q31", 50, 875, "lo_revenue", (YEAR, NATION_CODE["c"], NATION_CODE["s"]),
              (REGION_CODE["c"], REGION_CODE["s"], YEAR), ("2", "2", "1992,1997"), (1, 1, 0),
              f"{REGION_CODE['c']}=2 AND {REGION_CODE['s']}=2 AND {YEAR} BETWEEN 1992 AND 1997", ("customer", "supplier")),
    QuerySpec("q32", 500, 43750, "lo_revenue", (YEAR, CITY_CODE["c"], CITY_CODE["s"]),
              (NATION_CODE["c"], NATION_CODE["s"], YEAR), ("24", "24", "1992,1997"), (1, 1, 0),
              f"{NATION_CODE['c']}=24 AND {NATION_CODE['s']}=24 AND {YEAR} BETWEEN 1992 AND 1997", ("customer", "supplier")),
    QuerySpec("q33", 20000, 4375, "lo_revenue", (YEAR, CITY_CODE["c"], CITY_CODE["s"]),
              (CITY_CODE["c"], CITY_CODE["s"], YEAR), ("231,235", "231,235", "1992,1997"), (2, 2, 0),
              f"{CITY_CODE['c']} IN (231,235) AND {CITY_CODE['s']} IN (231,235) AND {YEAR} BETWEEN 1992 AND 1997", ("customer", "supplier")),
    QuerySpec("q34", 20000, 8750, "lo_revenue", (YEAR, CITY_CODE["c"], CITY_CODE["s"]),
              (CITY_CODE["c"], CITY_CODE["s"], YEARMONTH), ("231,235", "231,235", "199712"), (2, 2, 1),
              f"{CITY_CODE['c']} IN (231,235) AND {CITY_CODE['s']} IN (231,235) AND {YEARMONTH}=199712", ("customer", "supplier")),
    QuerySpec("q41", 100, 18, "lo_revenue-lo_supplycost", (YEAR, NATION_CODE["c"]),
              (REGION_CODE["c"], REGION_CODE["s"], PART_MFGR), ("1", "1", "1,2"), (1, 1, 2),
              f"{REGION_CODE['c']}=1 AND {REGION_CODE['s']}=1 AND {PART_MFGR} IN (1,2)", ("customer", "supplier", "part")),
    QuerySpec("q42", 500, 88, "lo_revenue-lo_supplycost", (YEAR, NATION_CODE["s"], PART_CATEGORY),
              (REGION_CODE["c"], REGION_CODE["s"], PART_MFGR, YEAR), ("1", "1", "1,2", "1997,1998"), (1, 1, 2, 0),
              f"{REGION_CODE['c']}=1 AND {REGION_CODE['s']}=1 AND {PART_MFGR} IN (1,2) AND {YEAR} BETWEEN 1997 AND 1998", ("customer", "supplier", "part")),
    QuerySpec("q43", 200, 350000, "lo_revenue-lo_supplycost", (YEAR, CITY_CODE["s"], PART_BRAND),
              (NATION_CODE["s"], PART_CATEGORY, YEAR), ("24", "14", "1997,1998"), (1, 1, 0),
              f"{NATION_CODE['s']}=24 AND {PART_CATEGORY}=14 AND {YEAR} BETWEEN 1997 AND 1998", ("supplier", "part")),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def validate_dataset_provenance(
    provenance_path: Path,
    *,
    dataset_dir: Path,
    scale_factor: int,
    table_paths: dict[str, Path],
    table_row_counts: dict[str, int],
) -> dict[str, object]:
    """Validate generated-SSB identity from pinned source, hashes, and cardinalities."""
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("schema") != "rtdl.paper_reproduction.raydb.ssb_generated_dataset_provenance.v1":
        raise ValueError("unsupported generated-SSB dataset provenance schema")
    if provenance.get("dbgen_repository") != DBGEN_REPOSITORY:
        raise ValueError("dataset provenance dbgen repository does not match the pinned generator")
    if provenance.get("dbgen_commit") != DBGEN_COMMIT:
        raise ValueError("dataset provenance dbgen commit does not match the pinned generator")
    if int(provenance.get("scale_factor", -1)) != int(scale_factor):
        raise ValueError("dataset provenance scale factor does not match --scale-factor")
    if provenance.get("dataset_identity_level") != "deterministic_generated_same_source_not_exact_paper_input":
        raise ValueError("dataset provenance identity level is not the bounded generated contract")
    if provenance.get("generation_profile") != GENERATION_PROFILE:
        raise ValueError("dataset provenance generation profile is not the pinned SSB command sequence")
    commands = provenance.get("generation_commands")
    if not isinstance(commands, list) or not commands:
        raise ValueError("dataset provenance must record non-empty generation_commands")
    command_argv = provenance.get("generation_command_argv")
    if not isinstance(command_argv, list) or not command_argv or any(
        not isinstance(command, list)
        or not command
        or any(not isinstance(argument, str) for argument in command)
        for command in command_argv
    ):
        raise ValueError("dataset provenance must record exact generation command argv")
    if provenance.get("dbgen_checkout_clean") is not True:
        raise ValueError("dataset provenance requires a clean pinned dbgen checkout")
    for field in (
        "dbgen_tracked_source_tree_sha256",
        "dbgen_binary_sha256",
        "dists_dss_sha256",
    ):
        if not _is_sha256(provenance.get(field)):
            raise ValueError(f"dataset provenance field {field} must be a SHA-256 digest")
    if int(provenance.get("dbgen_tracked_source_tree_file_count", 0)) <= 0:
        raise ValueError("dataset provenance tracked source file count must be positive")
    if provenance.get("provenance_scope") != "bounded_same_source_only_not_exact_paper":
        raise ValueError("dataset provenance scope is not the bounded same-source contract")
    claim_boundary = provenance.get("claim_boundary")
    if not isinstance(claim_boundary, dict) or not (
        claim_boundary.get("bounded_same_source_only") is True
        and claim_boundary.get("exact_paper_input_claimed") is False
        and claim_boundary.get("exact_paper_dataset_claimed") is False
    ):
        raise ValueError("dataset provenance claim boundary is missing or unsafe")

    expected_cardinalities = {
        "customer": 30_000 * int(scale_factor),
        "supplier": 2_000 * int(scale_factor),
        "part": 200_000 * math.floor(1.0 + math.log2(float(scale_factor))),
    }
    for name, expected in expected_cardinalities.items():
        if int(table_row_counts[name]) != expected:
            raise ValueError(
                f"{name} cardinality does not match pinned dbgen SF{scale_factor}: "
                f"expected {expected}, got {table_row_counts[name]}"
            )
    lineorder_count = int(table_row_counts["lineorder"])
    if not 5_500_000 * int(scale_factor) <= lineorder_count <= 6_500_000 * int(scale_factor):
        raise ValueError("lineorder cardinality is outside the pinned dbgen scale envelope")
    if int(provenance.get("lineorder_row_count", -1)) != lineorder_count:
        raise ValueError("dataset provenance lineorder row count does not match the loaded table")

    manifest_tables = provenance.get("tables")
    if not isinstance(manifest_tables, dict):
        raise ValueError("dataset provenance tables must be a mapping")
    verified_hashes: dict[str, str] = {}
    for name, path in table_paths.items():
        entry = manifest_tables.get(name)
        if not isinstance(entry, dict):
            raise ValueError(f"dataset provenance is missing table entry: {name}")
        if entry.get("file_name") != path.name:
            raise ValueError(f"dataset provenance file name mismatch for {name}")
        actual = sha256_file(path)
        if entry.get("sha256") != actual:
            raise ValueError(f"dataset provenance SHA-256 mismatch for {name}")
        if int(entry.get("row_count", -1)) != int(table_row_counts[name]):
            raise ValueError(f"dataset provenance row count mismatch for {name}")
        verified_hashes[name] = actual
    return {
        "path": str(provenance_path),
        "sha256": sha256_file(provenance_path),
        "verified": True,
        "scale_factor": int(scale_factor),
        "table_sha256": verified_hashes,
        "table_row_counts": {name: int(value) for name, value in table_row_counts.items()},
        "dataset_dir": str(dataset_dir),
    }


def _register_table(connection, name: str, path: Path, columns: dict[str, str]) -> None:
    relation = connection.read_csv(
        str(path), columns=columns, delimiter=",", quotechar='"', header=False, null_padding=True
    )
    relation.create_view(name)


def _from_sql(spec: QuerySpec) -> str:
    joins = []
    if "customer" in spec.joins:
        joins.append("JOIN customer ON lo_custkey=c_custkey")
    if "supplier" in spec.joins:
        joins.append("JOIN supplier ON lo_suppkey=s_suppkey")
    if "part" in spec.joins:
        joins.append("JOIN part ON lo_partkey=p_partkey")
    return "lineorder " + " ".join(joins)


def build_query_packet(
    connection,
    spec: QuerySpec,
    output_root: Path,
    *,
    row_count: int,
    scale_factor: int = 1,
) -> dict[str, object]:
    import numpy as np

    case_dir = output_root / spec.query_id
    case_dir.mkdir(parents=True, exist_ok=True)
    select_columns = [spec.aggregate, *spec.groups, *spec.scans]
    if spec.extra_multiplier is not None:
        select_columns.append(spec.extra_multiplier)
    aliases = ["aggregate_value"]
    aliases.extend(f"group_{index}" for index in range(len(spec.groups)))
    aliases.extend(f"scan_{index}" for index in range(len(spec.scans)))
    if spec.extra_multiplier is not None:
        aliases.append("extra_multiplier")
    select_sql = ", ".join(f"CAST(({expression}) AS INTEGER) AS {alias}" for expression, alias in zip(select_columns, aliases))
    relation = connection.execute(
        f"SELECT {select_sql} FROM {_from_sql(spec)} ORDER BY lo_orderkey, lo_linenumber"
    ).fetchnumpy()
    if len(relation[aliases[0]]) != row_count:
        raise ValueError(f"{spec.query_id} join did not preserve the lineorder row count")
    data_path = case_dir / "data.bin"
    with data_path.open("wb") as stream:
        for alias in aliases:
            values = np.asarray(relation[alias])
            if values.size and (
                int(values.min()) < -0x80000000
                or int(values.max()) > 0x7FFFFFFF
            ):
                raise ValueError(f"{spec.query_id} column {alias} does not fit the author's signed int reader")
            np.asarray(values, dtype="<i4").tofile(stream)
    predicate_path = case_dir / "predicate.txt"
    predicate_path.write_text(
        "\n".join((*spec.predicate_lines, ",".join(str(value) for value in spec.scan_types))) + "\n",
        encoding="ascii",
    )

    group_select = ", ".join(f"CAST(({expression}) AS INTEGER) AS group_{index}" for index, expression in enumerate(spec.groups))
    group_by = ", ".join(str(index + 1) for index in range(len(spec.groups)))
    value_expression = spec.aggregate
    if spec.extra_multiplier is not None:
        value_expression = f"CAST(({spec.aggregate}) AS BIGINT) * ({spec.extra_multiplier})"
    oracle_rows = connection.execute(
        f"SELECT {group_select}, SUM(CAST(({value_expression}) AS BIGINT)) AS value "
        f"FROM {_from_sql(spec)} WHERE {spec.filter_sql} GROUP BY {group_by} ORDER BY {group_by}"
    ).fetchall()
    expected_rows = [
        {"group": [int(value) for value in row[:-1]], "value": int(row[-1])}
        for row in oracle_rows
        if int(row[-1]) != 0
    ]
    expected_path = case_dir / "expected_rows.json"
    expected_path.write_text(json.dumps(expected_rows, indent=2) + "\n", encoding="utf-8")
    packet = {
        "schema": "rtdl.paper_reproduction.raydb.ssb_packet.v2",
        "case_id": f"ssb_sf{scale_factor}_{spec.query_id}",
        "query_id": spec.query_id,
        "scale_factor": int(scale_factor),
        "row_count": row_count,
        "group_dimension_count": len(spec.groups),
        "predicate_dimension_count": len(spec.scans),
        "column_count": len(aliases),
        "column_order": aliases,
        "interval_x": spec.interval_x,
        "interval_y": spec.interval_y,
        "scan_types": list(spec.scan_types),
        "complex_aggregate": spec.extra_multiplier is not None,
        "data_path": str(data_path),
        "predicate_path": str(predicate_path),
        "expected_rows_path": str(expected_path),
        "data_sha256": sha256_file(data_path),
        "predicate_sha256": sha256_file(predicate_path),
        "expected_rows_sha256": sha256_file(expected_path),
        "expected_rows": expected_rows,
        "zero_sum_group_semantics": "author_text_contract_omits_zero_sum_groups",
        "author_cli": [
            "-n", str(row_count), "-x", str(spec.interval_x), "-y", str(spec.interval_y),
            "-g", str(len(spec.groups)), "-p", str(len(spec.scans)),
            "-s", str(predicate_path), "-i", str(data_path),
            *( ["-a"] if spec.extra_multiplier is not None else [] ),
        ],
        "input_identity_level": (
            f"deterministic_generated_ssb_sf{scale_factor}_same_bytes__not_exact_paper_input"
        ),
        "oracle_contract": "independent DuckDB SSB relational filter/grouped integer SUM over the pinned generated tables",
        "claim_boundary": {
            "author_executed": False,
            "rtdl_executed": False,
            "all_13_queries_claimed": False,
            "paper_performance_claimed": False,
        },
    }
    packet_path = case_dir / "packet.json"
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    return packet


def _open_dataset(dataset_dir: Path):
    import duckdb

    paths = {name: dataset_dir / f"{name}.tbl" for name in ("lineorder", "customer", "supplier", "part")}
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"missing SSB table: {path}")
    connection = duckdb.connect()
    _register_table(connection, "lineorder", paths["lineorder"], LINEORDER_COLUMNS)
    _register_table(connection, "customer", paths["customer"], CUSTOMER_COLUMNS)
    _register_table(connection, "supplier", paths["supplier"], SUPPLIER_COLUMNS)
    _register_table(connection, "part", paths["part"], PART_COLUMNS)
    return connection, paths


def build_matrix(
    dataset_dir: Path,
    output_root: Path,
    *,
    scale_factor: int = 1,
    dataset_provenance_path: Path | None = None,
) -> dict[str, object]:
    connection, paths = _open_dataset(dataset_dir)
    row_count = int(connection.execute("SELECT count(*) FROM lineorder").fetchone()[0])
    table_row_counts = {
        name: int(connection.execute(f"SELECT count(*) FROM {name}").fetchone()[0])
        for name in paths
    }
    provenance = (
        validate_dataset_provenance(
            dataset_provenance_path,
            dataset_dir=dataset_dir,
            scale_factor=scale_factor,
            table_paths=paths,
            table_row_counts=table_row_counts,
        )
        if dataset_provenance_path is not None
        else {"verified": False}
    )
    packets = [
        build_query_packet(
            connection,
            spec,
            output_root,
            row_count=row_count,
            scale_factor=scale_factor,
        )
        for spec in QUERY_SPECS
    ]
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_matrix.v2",
        "dbgen_repository": DBGEN_REPOSITORY,
        "dbgen_commit": DBGEN_COMMIT,
        "scale_factor": int(scale_factor),
        "dataset_dir": str(dataset_dir),
        "table_sha256": {name: sha256_file(path) for name, path in paths.items()},
        "table_row_counts": table_row_counts,
        "dataset_provenance": provenance,
        "row_count": row_count,
        "query_count": len(packets),
        "packets": packets,
        "all_13_queries_executed": False,
        "paper_performance_claimed": False,
    }


def build_single_query(
    dataset_dir: Path,
    output_root: Path,
    *,
    query_id: str,
    scale_factor: int,
    memory_limit: str | None = None,
    temp_directory: Path | None = None,
    dataset_provenance_path: Path | None = None,
) -> dict[str, object]:
    matches = [spec for spec in QUERY_SPECS if spec.query_id == query_id]
    if len(matches) != 1:
        raise ValueError(f"unknown SSB query_id: {query_id}")
    connection, paths = _open_dataset(dataset_dir)
    if memory_limit:
        connection.execute(f"SET memory_limit='{memory_limit}'")
    if temp_directory is not None:
        temp_directory.mkdir(parents=True, exist_ok=True)
        escaped = str(temp_directory).replace("'", "''")
        connection.execute(f"SET temp_directory='{escaped}'")
    row_count = int(connection.execute("SELECT count(*) FROM lineorder").fetchone()[0])
    table_row_counts = {
        name: int(connection.execute(f"SELECT count(*) FROM {name}").fetchone()[0])
        for name in paths
    }
    provenance = (
        validate_dataset_provenance(
            dataset_provenance_path,
            dataset_dir=dataset_dir,
            scale_factor=scale_factor,
            table_paths=paths,
            table_row_counts=table_row_counts,
        )
        if dataset_provenance_path is not None
        else {"verified": False}
    )
    packet = build_query_packet(
        connection,
        matches[0],
        output_root,
        row_count=row_count,
        scale_factor=scale_factor,
    )
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_single_query_packet_build.v1",
        "dbgen_repository": DBGEN_REPOSITORY,
        "dbgen_commit": DBGEN_COMMIT,
        "scale_factor": int(scale_factor),
        "dataset_dir": str(dataset_dir),
        "table_sha256": {name: sha256_file(path) for name, path in paths.items()},
        "table_row_counts": table_row_counts,
        "dataset_provenance": provenance,
        "row_count": row_count,
        "query_id": query_id,
        "packet": packet,
        "exact_paper_input_claimed": False,
        "paper_performance_claimed": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build all 13 deterministic RayDB SSB SF1 packets")
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--query-id", choices=tuple(spec.query_id for spec in QUERY_SPECS))
    parser.add_argument("--scale-factor", type=int, default=1)
    parser.add_argument("--memory-limit")
    parser.add_argument("--temp-directory", type=Path)
    parser.add_argument("--dataset-provenance-json", type=Path)
    args = parser.parse_args(argv)
    if args.scale_factor <= 0:
        parser.error("--scale-factor must be positive")
    if args.query_id:
        result = build_single_query(
            args.dataset_dir,
            args.output_root,
            query_id=args.query_id,
            scale_factor=args.scale_factor,
            memory_limit=args.memory_limit,
            temp_directory=args.temp_directory,
            dataset_provenance_path=args.dataset_provenance_json,
        )
    else:
        result = build_matrix(
            args.dataset_dir,
            args.output_root,
            scale_factor=args.scale_factor,
            dataset_provenance_path=args.dataset_provenance_json,
        )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output_json.with_name(args.output_json.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output_json)
    print(
        json.dumps(
            {
                "row_count": result["row_count"],
                "query_count": result.get("query_count", 1),
                "query_id": result.get("query_id"),
                "scale_factor": result.get("scale_factor", 1),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
