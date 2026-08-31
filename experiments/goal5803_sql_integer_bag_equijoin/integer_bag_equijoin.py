"""Map a bounded SQLite-style integer bag equijoin to public RTDL AABBs.

This is application-owned interpretation code.  It intentionally imports no
RTDL module: the caller injects the installed public module only when building
the public input objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


MAX_EXACT_JOIN_KEY = (1 << 24) - 1
MAX_U32 = (1 << 32) - 1
MINIMUM_OVERLAP_F32 = 1.0


@dataclass(frozen=True, slots=True)
class IntegerJoinRow:
    """One non-NULL integer-key SQL row with an application-visible id."""

    row_id: int
    join_key: int

    def __post_init__(self) -> None:
        for name, value in (("row_id", self.row_id),
                            ("join_key", self.join_key)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"SQL equijoin {name} must be an integer")
        if not 0 <= self.row_id <= MAX_U32:
            raise ValueError("SQL equijoin row_id must be u32")
        if not 0 <= self.join_key <= MAX_EXACT_JOIN_KEY:
            raise ValueError(
                "SQL equijoin join_key must satisfy 0 <= key < 2^24")

    def as_pair(self) -> tuple[int, int]:
        return self.row_id, self.join_key


def _freeze_side(
    rows: Iterable[IntegerJoinRow], *, side: str,
) -> tuple[IntegerJoinRow, ...]:
    frozen = tuple(rows)
    if not frozen:
        raise ValueError(f"SQL equijoin side {side} must be nonempty")
    if any(not isinstance(row, IntegerJoinRow) for row in frozen):
        raise TypeError(
            f"SQL equijoin side {side} rows must be IntegerJoinRow")
    ids = tuple(row.row_id for row in frozen)
    if len(ids) != len(set(ids)):
        raise ValueError(
            f"SQL equijoin side {side} row ids must be unique")
    return frozen


def freeze_inputs(
    a_rows: Iterable[IntegerJoinRow],
    b_rows: Iterable[IntegerJoinRow],
) -> tuple[tuple[IntegerJoinRow, ...], tuple[IntegerJoinRow, ...]]:
    """Validate and freeze both SQL inputs without importing RTDL."""

    return _freeze_side(a_rows, side="A"), _freeze_side(b_rows, side="B")


def relation_rows(
    a_rows: Sequence[IntegerJoinRow],
    b_rows: Sequence[IntegerJoinRow],
) -> tuple[
    tuple[tuple[float, float, float, float, int], ...],
    tuple[tuple[float, float, float, float, int], ...],
]:
    """Return ``(indexed_B, source_A)`` unit AABBs.

    For integer keys in the declared domain, every endpoint is exact in
    binary32.  Equal keys give intersection area one.  Unequal integer keys
    either do not intersect or only touch at a zero-area boundary, so RTDL's
    sealed minimum area of one implements integer equality exactly.
    """

    a_frozen, b_frozen = freeze_inputs(a_rows, b_rows)

    def mapped(
        row: IntegerJoinRow,
    ) -> tuple[float, float, float, float, int]:
        key = row.join_key
        return float(key), 0.0, float(key + 1), 1.0, row.row_id

    return tuple(mapped(row) for row in b_frozen), tuple(
        mapped(row) for row in a_frozen)


def build_public_inputs(module, a_rows, b_rows):
    """Construct only public RTDL inputs and never pass the SQL oracle."""

    indexed_b, source_a = relation_rows(a_rows, b_rows)
    static = module.BoundedRelationStaticInput(indexed_boxes=indexed_b)
    batch = module.BoundedRelationBatch(
        source_boxes=source_a,
        expected_rows=None,
    )
    return static, batch


DEFAULT_A = (
    IntegerJoinRow(10, 0),
    IntegerJoinRow(11, 7),
    IntegerJoinRow(12, 7),
    IntegerJoinRow(13, 8),
    IntegerJoinRow(14, MAX_EXACT_JOIN_KEY),
    IntegerJoinRow(15, 42),
)

DEFAULT_B = (
    IntegerJoinRow(100, 0),
    IntegerJoinRow(101, 7),
    IntegerJoinRow(102, 7),
    IntegerJoinRow(103, 8),
    IntegerJoinRow(104, 9),
    IntegerJoinRow(105, MAX_EXACT_JOIN_KEY),
    IntegerJoinRow(106, 43),
)

DEFAULT_EXPECTED_PAIRS = (
    (10, 100),
    (11, 101),
    (11, 102),
    (12, 101),
    (12, 102),
    (13, 103),
    (14, 105),
)

REUSE_A = (
    IntegerJoinRow(20, 7),
    IntegerJoinRow(21, 9),
    IntegerJoinRow(22, 43),
    IntegerJoinRow(23, 6),
)

REUSE_EXPECTED_PAIRS = (
    (20, 101),
    (20, 102),
    (21, 104),
    (22, 106),
)


__all__ = [
    "DEFAULT_A",
    "DEFAULT_B",
    "DEFAULT_EXPECTED_PAIRS",
    "IntegerJoinRow",
    "MAX_EXACT_JOIN_KEY",
    "MAX_U32",
    "MINIMUM_OVERLAP_F32",
    "REUSE_A",
    "REUSE_EXPECTED_PAIRS",
    "build_public_inputs",
    "freeze_inputs",
    "relation_rows",
]

