from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence


LINEORDER_COLUMNS = {
    "lo_orderkey": "BIGINT",
    "lo_linenumber": "INTEGER",
    "lo_custkey": "INTEGER",
    "lo_partkey": "INTEGER",
    "lo_suppkey": "INTEGER",
    "lo_orderdate": "VARCHAR",
    "lo_orderpriority": "VARCHAR",
    "lo_shippriority": "INTEGER",
    "lo_quantity": "INTEGER",
    "lo_extendedprice": "INTEGER",
    "lo_ordtotalprice": "INTEGER",
    "lo_discount": "INTEGER",
    "lo_revenue": "INTEGER",
    "lo_supplycost": "INTEGER",
    "lo_tax": "INTEGER",
    "lo_commitdate": "VARCHAR",
    "lo_shipmode": "VARCHAR",
    "trailing": "VARCHAR",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_q11_packet(
    lineorder_path: Path,
    output_dir: Path,
    *,
    dbgen_commit: str,
    delimiter: str = ",",
    dbgen_repository: str = "https://github.com/vadimtk/ssb-dbgen",
    case_id: str = "ssb_sf1_q11",
    input_identity_level: str = "deterministic_generated_ssb_sf1_same_bytes__not_exact_paper_input",
) -> dict[str, object]:
    import duckdb
    import numpy as np

    output_dir.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect()
    relation = connection.read_csv(
        str(lineorder_path),
        columns=LINEORDER_COLUMNS,
        delimiter=delimiter,
        quotechar='"',
        header=False,
        null_padding=True,
    )
    relation.create_view("lineorder")
    row_count = int(connection.execute("SELECT count(*) FROM lineorder").fetchone()[0])
    columns = connection.execute(
        """
        SELECT
          lo_extendedprice::INTEGER AS aggregate_value,
          0::INTEGER AS group_value,
          CAST(substr(lo_orderdate, 1, 4) AS INTEGER) AS scan_year,
          lo_discount::INTEGER AS scan_discount,
          lo_quantity::INTEGER AS scan_quantity,
          lo_discount::INTEGER AS extra_multiplier
        FROM lineorder
        ORDER BY lo_orderkey, lo_linenumber
        """
    ).fetchnumpy()
    expected_value = int(
        connection.execute(
            """
            SELECT sum(CAST(lo_extendedprice AS BIGINT) * lo_discount)
            FROM lineorder
            WHERE CAST(substr(lo_orderdate, 1, 4) AS INTEGER) = 1993
              AND lo_discount BETWEEN 1 AND 3
              AND lo_quantity BETWEEN 1 AND 24
            """
        ).fetchone()[0]
    )
    data_path = output_dir / "ssb_sf1_q11_data.bin"
    with data_path.open("wb") as stream:
        for name in (
            "aggregate_value",
            "group_value",
            "scan_year",
            "scan_discount",
            "scan_quantity",
            "extra_multiplier",
        ):
            np.asarray(columns[name], dtype="<i4").tofile(stream)
    predicate_path = output_dir / "ssb_sf1_q11_predicate.txt"
    predicate_path.write_text("1993\n1,3\n1,24\n1,0,0\n", encoding="ascii")
    expected_rows = [{"group": [0], "value": expected_value}]
    expected_path = output_dir / "ssb_sf1_q11_expected_rows.json"
    expected_path.write_text(json.dumps(expected_rows, indent=2) + "\n", encoding="utf-8")
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_sf1_q11_packet.v1",
        "case_id": case_id,
        "dbgen_repository": dbgen_repository,
        "dbgen_commit": dbgen_commit,
        "lineorder_path": str(lineorder_path),
        "lineorder_sha256": sha256_file(lineorder_path),
        "row_count": row_count,
        "group_dimension_count": 1,
        "predicate_dimension_count": 3,
        "column_order": [
            "lo_extendedprice",
            "constant_group_zero",
            "year(lo_orderdate)",
            "lo_discount",
            "lo_quantity",
            "lo_discount_extra_multiplier",
        ],
        "data_sha256": sha256_file(data_path),
        "predicate_sha256": sha256_file(predicate_path),
        "expected_rows_sha256": sha256_file(expected_path),
        "expected_rows": expected_rows,
        "author_cli": [
            "-n", str(row_count), "-x", "6", "-y", "1", "-g", "1",
            "-p", "3", "-s", str(predicate_path), "-i", str(data_path), "-a",
        ],
        "input_identity_level": input_identity_level,
        "claim_boundary": {
            "author_executed": False,
            "rtdl_executed": False,
            "all_13_queries_claimed": False,
            "paper_performance_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic RayDB SSB SF1 q11 packet")
    parser.add_argument("--lineorder", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dbgen-commit", required=True)
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--dbgen-repository", default="https://github.com/vadimtk/ssb-dbgen")
    parser.add_argument("--case-id", default="ssb_sf1_q11")
    parser.add_argument(
        "--input-identity-level",
        default="deterministic_generated_ssb_sf1_same_bytes__not_exact_paper_input",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_q11_packet(
        args.lineorder,
        args.output_dir,
        dbgen_commit=args.dbgen_commit,
        delimiter=args.delimiter,
        dbgen_repository=args.dbgen_repository,
        case_id=args.case_id,
        input_identity_level=args.input_identity_level,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
