#!/usr/bin/env python3
"""Independent SQLite oracle for the bounded integer bag equijoin.

This module deliberately imports neither RTDL nor the application adapter.  It
accepts plain ``(row_id, join_key)`` rows, executes the externally implemented
SQLite join, and separately reconstructs the mathematical equality relation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Iterable

import _sqlite3  # type: ignore[import-not-found]  # exact linked extension identity


MAX_EXACT_JOIN_KEY = (1 << 24) - 1
MAX_U32 = (1 << 32) - 1
DDL_A = "CREATE TABLE a(row_id INTEGER PRIMARY KEY, join_key INTEGER NOT NULL)"
DDL_B = "CREATE TABLE b(row_id INTEGER PRIMARY KEY, join_key INTEGER NOT NULL)"
QUERY = (
    "SELECT a.row_id, b.row_id FROM a INNER JOIN b "
    "ON a.join_key = b.join_key "
    "ORDER BY a.row_id ASC, b.row_id ASC"
)


def _sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _freeze_plain_side(
    rows: Iterable[tuple[int, int]], *, side: str,
) -> tuple[tuple[int, int], ...]:
    frozen: list[tuple[int, int]] = []
    for index, raw in enumerate(rows):
        if not isinstance(raw, (tuple, list)) or len(raw) != 2:
            raise ValueError(f"SQLite oracle {side}[{index}] must have arity two")
        row_id, join_key = raw
        for name, value, upper in (
            ("row_id", row_id, MAX_U32),
            ("join_key", join_key, MAX_EXACT_JOIN_KEY),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(
                    f"SQLite oracle {side}[{index}].{name} must be an integer")
            if not 0 <= value <= upper:
                raise ValueError(
                    f"SQLite oracle {side}[{index}].{name} outside domain")
        frozen.append((row_id, join_key))
    result = tuple(frozen)
    if not result:
        raise ValueError(f"SQLite oracle side {side} must be nonempty")
    ids = tuple(row[0] for row in result)
    if len(ids) != len(set(ids)):
        raise ValueError(f"SQLite oracle side {side} row ids must be unique")
    return result


def pure_python_integer_bag_oracle(
    a_rows: Iterable[tuple[int, int]],
    b_rows: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    """Route-independent mathematical crosscheck of integer equality."""

    a_frozen = _freeze_plain_side(a_rows, side="A")
    b_frozen = _freeze_plain_side(b_rows, side="B")
    return tuple(sorted(
        (a_id, b_id)
        for a_id, a_key in a_frozen
        for b_id, b_key in b_frozen
        if a_key == b_key
    ))


@dataclass(frozen=True, slots=True)
class SQLiteOracleResult:
    pairs: tuple[tuple[int, int], ...]
    sqlite_version: str
    sqlite_source_id: str
    sqlite_extension_path: str
    sqlite_extension_sha256: str
    oracle_source_sha256: str
    query_utf8_sha256: str
    input_canonical_sha256: str
    independent_python_pairs_sha256: str

    def to_payload(self) -> dict[str, object]:
        return {
            "schema": "rtdl.goal5803.sql_integer_bag_equijoin.sqlite_oracle.v1",
            "pairs": [list(row) for row in self.pairs],
            "sqlite_version": self.sqlite_version,
            "sqlite_source_id": self.sqlite_source_id,
            "sqlite_extension_path": self.sqlite_extension_path,
            "sqlite_extension_sha256": self.sqlite_extension_sha256,
            "oracle_source_sha256": self.oracle_source_sha256,
            "query": QUERY,
            "query_utf8_sha256": self.query_utf8_sha256,
            "input_canonical_sha256": self.input_canonical_sha256,
            "independent_python_pairs_sha256": (
                self.independent_python_pairs_sha256),
            "imports_rtdsl": False,
            "imports_application_adapter": False,
            "network_call_count": 0,
        }


def sqlite_integer_bag_equijoin_oracle(
    a_rows: Iterable[tuple[int, int]],
    b_rows: Iterable[tuple[int, int]],
) -> SQLiteOracleResult:
    """Execute SQLite and require a separately written equality crosscheck."""

    a_frozen = _freeze_plain_side(a_rows, side="A")
    b_frozen = _freeze_plain_side(b_rows, side="B")
    python_pairs = pure_python_integer_bag_oracle(a_frozen, b_frozen)
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(DDL_A)
        connection.execute(DDL_B)
        connection.executemany("INSERT INTO a VALUES (?, ?)", a_frozen)
        connection.executemany("INSERT INTO b VALUES (?, ?)", b_frozen)
        stored_types = tuple(connection.execute(
            "SELECT typeof(join_key) FROM a UNION ALL "
            "SELECT typeof(join_key) FROM b"
        ))
        if any(row != ("integer",) for row in stored_types):
            raise RuntimeError("SQLite oracle join keys did not remain INTEGER")
        sqlite_pairs = tuple(
            (int(row[0]), int(row[1]))
            for row in connection.execute(QUERY)
        )
        source_id_row = connection.execute(
            "SELECT sqlite_source_id()"
        ).fetchone()
        if source_id_row is None or not isinstance(source_id_row[0], str):
            raise RuntimeError("SQLite oracle omitted sqlite_source_id")
        source_id = source_id_row[0]
    finally:
        connection.close()
    if sqlite_pairs != python_pairs:
        raise RuntimeError(
            "SQLite result differs from the independent integer equality oracle")

    input_payload = {
        "A": [list(row) for row in a_frozen],
        "B": [list(row) for row in b_frozen],
    }
    extension_path = Path(_sqlite3.__file__).resolve()
    source_path = Path(__file__).resolve()
    return SQLiteOracleResult(
        pairs=sqlite_pairs,
        sqlite_version=sqlite3.sqlite_version,
        sqlite_source_id=source_id,
        sqlite_extension_path=str(extension_path),
        sqlite_extension_sha256=_sha_file(extension_path),
        oracle_source_sha256=_sha_file(source_path),
        query_utf8_sha256=_sha_bytes(QUERY.encode("utf-8")),
        input_canonical_sha256=_sha_bytes(_canonical_bytes(input_payload)),
        independent_python_pairs_sha256=_sha_bytes(_canonical_bytes(
            [list(row) for row in python_pairs])),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"A", "B"}:
        raise ValueError("oracle input must contain exactly A and B")
    result = sqlite_integer_bag_equijoin_oracle(
        payload["A"], payload["B"])
    output = result.to_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(output, sort_keys=True, indent=2).encode("utf-8") + b"\n")
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DDL_A",
    "DDL_B",
    "MAX_EXACT_JOIN_KEY",
    "MAX_U32",
    "QUERY",
    "SQLiteOracleResult",
    "pure_python_integer_bag_oracle",
    "sqlite_integer_bag_equijoin_oracle",
]

