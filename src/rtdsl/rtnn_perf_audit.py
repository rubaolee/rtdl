from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Dict


@dataclass(frozen=True)
class FixedRadiusMismatchSummary:
    strict_parity_ok: bool
    reference_row_count: int
    candidate_row_count: int
    missing_pair_count: int
    extra_pair_count: int
    first_missing_pair: Optional[Tuple[int, int]]
    first_extra_pair: Optional[Tuple[int, int]]
    first_reference_row: Optional[Dict[str, object]]
    first_candidate_row: Optional[Dict[str, object]]


def summarize_fixed_radius_mismatch(
    reference_rows: tuple[dict[str, object], ...],
    candidate_rows: tuple[dict[str, object], ...],
    *,
    strict_parity_ok: bool,
) -> FixedRadiusMismatchSummary:
    reference_pairs = {
        (int(row["query_id"]), int(row["neighbor_id"])) for row in reference_rows
    }
    candidate_pairs = {
        (int(row["query_id"]), int(row["neighbor_id"])) for row in candidate_rows
    }
    missing_pairs = tuple(sorted(reference_pairs - candidate_pairs))
    extra_pairs = tuple(sorted(candidate_pairs - reference_pairs))

    first_reference_row = None
    first_candidate_row = None
    for reference_row, candidate_row in zip(reference_rows, candidate_rows):
        if reference_row != candidate_row:
            first_reference_row = dict(reference_row)
            first_candidate_row = dict(candidate_row)
            break

    if first_reference_row is None and len(reference_rows) != len(candidate_rows):
        if reference_rows:
            first_reference_row = dict(reference_rows[min(len(candidate_rows), len(reference_rows) - 1)])
        if candidate_rows:
            first_candidate_row = dict(candidate_rows[min(len(reference_rows), len(candidate_rows) - 1)])

    return FixedRadiusMismatchSummary(
        strict_parity_ok=strict_parity_ok,
        reference_row_count=len(reference_rows),
        candidate_row_count=len(candidate_rows),
        missing_pair_count=len(missing_pairs),
        extra_pair_count=len(extra_pairs),
        first_missing_pair=missing_pairs[0] if missing_pairs else None,
        first_extra_pair=extra_pairs[0] if extra_pairs else None,
        first_reference_row=first_reference_row,
        first_candidate_row=first_candidate_row,
    )
