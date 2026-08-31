"""Application-facing fixtures for the generic Goal5758/M1 product contract."""

from __future__ import annotations

from rtdsl.v4_triangle_standard_library import (
    COUNT_SOURCE,
    KEYED_SOURCE,
    all_hit_count_schema as all_hit_schema,
    compile_count_callback,
    compile_keyed_callback,
    keyed_i64_sum_schema as keyed_schema,
    weighted_hit_count_schema as weighted_schema,
)


__all__ = [
    "COUNT_SOURCE", "KEYED_SOURCE", "all_hit_schema", "compile_count_callback",
    "compile_keyed_callback", "keyed_schema", "weighted_schema",
]
