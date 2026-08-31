"""Route-independent exact integer oracles for Goal5758/M1 evidence.

This module deliberately imports no V4 compiler, schema, ABI, reducer, V2/V3
application route, or author executable.
"""

from __future__ import annotations

from typing import Iterable, Mapping


I64_MIN = -(1 << 63)
I64_MAX = (1 << 63) - 1
U64_MAX = (1 << 64) - 1


def keyed_i64_identical_dedup(
    rows: Iterable[Mapping[str, int]], *, capacity: int,
) -> tuple[tuple[tuple[int, ...], int], ...]:
    seen: dict[tuple[int, int], tuple[int, int]] = {}
    grouped: dict[tuple[int, ...], int] = {}
    for raw in rows:
        row = dict(raw)
        include = int(row["primitive.include"])
        if include not in {0, 1}:
            raise ValueError("include flag")
        event_id = (int(row["primitive.stable_id"]), int(row["launch_index"]))
        fingerprint = (int(row["primitive.signed_value"]), include)
        if event_id in seen:
            if seen[event_id] != fingerprint:
                raise ValueError("conflicting duplicate")
            continue
        seen[event_id] = fingerprint
        if include == 0:
            continue
        key = (int(row["launch_index"]),)
        value = int(row["primitive.signed_value"])
        if not I64_MIN <= value <= I64_MAX:
            raise OverflowError("i64 input")
        total = grouped.get(key, 0) + value
        if not I64_MIN <= total <= I64_MAX:
            raise OverflowError("i64 sum")
        grouped[key] = total
    if len(grouped) > capacity:
        raise OverflowError("capacity")
    return tuple((key, grouped[key]) for key in sorted(grouped) if grouped[key] != 0)


def checked_u64_sum(values: Iterable[int]) -> int:
    total = 0
    for value in values:
        value = int(value)
        if not 0 <= value <= U64_MAX:
            raise OverflowError("u64 input")
        total += value
        if total > U64_MAX:
            raise OverflowError("u64 sum")
    return total


def checked_u64_product_sum(rows: Iterable[tuple[int, int]]) -> int:
    total = 0
    for value, weight in rows:
        value, weight = int(value), int(weight)
        if not 0 <= value <= U64_MAX or not 0 <= weight <= U64_MAX:
            raise OverflowError("u64 input")
        product = value * weight
        if product > U64_MAX:
            raise OverflowError("u64 product")
        total += product
        if total > U64_MAX:
            raise OverflowError("u64 sum")
    return total


__all__ = ["checked_u64_product_sum", "checked_u64_sum", "keyed_i64_identical_dedup"]
