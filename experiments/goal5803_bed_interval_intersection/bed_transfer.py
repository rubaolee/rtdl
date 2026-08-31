"""Map default BED interval intersection to RTDL's bounded AABB relation.

The application mapping is deliberately outside ``src/rtdsl``.  RTDL supplies
the checked relation protocol; this module owns the genomic interpretation and
the route-independent CPU oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


MAX_EXACT_F32_INTEGER = 1 << 24
MINIMUM_OVERLAP_F32 = 1.0


@dataclass(frozen=True, slots=True)
class BedInterval:
    chromosome: str
    start: int
    end: int
    interval_id: int

    def __post_init__(self) -> None:
        if not isinstance(self.chromosome, str) or not self.chromosome:
            raise ValueError("BED chromosome must be a nonempty string")
        for name in ("start", "end", "interval_id"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"BED {name} must be an integer")
        if not 0 <= self.start < self.end <= MAX_EXACT_F32_INTEGER:
            raise ValueError(
                "BED interval must satisfy 0 <= start < end <= 2^24")
        if not 0 <= self.interval_id < (1 << 32):
            raise ValueError("BED interval_id must be u32")


def _freeze_side(
    rows: Iterable[BedInterval], *, side: str,
) -> tuple[BedInterval, ...]:
    frozen = tuple(rows)
    if not frozen:
        raise ValueError(f"BED {side} must be nonempty")
    if any(not isinstance(row, BedInterval) for row in frozen):
        raise TypeError(f"BED {side} rows must be BedInterval")
    ids = tuple(row.interval_id for row in frozen)
    if len(ids) != len(set(ids)):
        raise ValueError(f"BED {side} interval ids must be unique")
    return frozen


def freeze_inputs(
    a_rows: Iterable[BedInterval], b_rows: Iterable[BedInterval],
) -> tuple[tuple[BedInterval, ...], tuple[BedInterval, ...]]:
    """Validate and freeze the A and B inputs without importing RTDL."""

    return _freeze_side(a_rows, side="A"), _freeze_side(b_rows, side="B")


def bedtools_default_pair_oracle(
    a_rows: Sequence[BedInterval], b_rows: Sequence[BedInterval],
) -> tuple[tuple[int, int], ...]:
    """Independent default-intersect pair oracle.

    BED intervals are 0-based and half-open.  Consequently, positive overlap
    is ``max(start) < min(end)``; an adjacent boundary alone is not a hit.
    """

    a_frozen, b_frozen = freeze_inputs(a_rows, b_rows)
    pairs = {
        (a.interval_id, b.interval_id)
        for a in a_frozen
        for b in b_frozen
        if a.chromosome == b.chromosome
        and max(a.start, b.start) < min(a.end, b.end)
    }
    return tuple(sorted(pairs))


def relation_rows(
    a_rows: Sequence[BedInterval], b_rows: Sequence[BedInterval],
) -> tuple[
    tuple[tuple[float, float, float, float, int], ...],
    tuple[tuple[float, float, float, float, int], ...],
]:
    """Return ``(indexed_B, source_A)`` rows for the checked relation.

    Chromosome bands are separated by one empty unit, so closed AABBs from
    different chromosomes cannot touch.  Within one chromosome the y-overlap
    is exactly one.  Integer x endpoints up to 2^24 are exact in binary32;
    therefore area >= 1.0 is exactly the default BED rule of at least one
    overlapping base pair, while half-open adjacency has area zero.
    """

    a_frozen, b_frozen = freeze_inputs(a_rows, b_rows)
    chromosomes = tuple(sorted({
        row.chromosome for row in (*a_frozen, *b_frozen)
    }))
    if len(chromosomes) > (MAX_EXACT_F32_INTEGER // 2):
        raise ValueError("too many chromosome bands for exact binary32 mapping")
    bands = {
        chromosome: (float(2 * index), float(2 * index + 1))
        for index, chromosome in enumerate(chromosomes)
    }

    def mapped(row: BedInterval) -> tuple[float, float, float, float, int]:
        lower_y, upper_y = bands[row.chromosome]
        return (
            float(row.start), lower_y, float(row.end), upper_y,
            row.interval_id,
        )

    return tuple(mapped(row) for row in b_frozen), tuple(
        mapped(row) for row in a_frozen)


def build_public_inputs(module, a_rows, b_rows):
    """Construct only the public RTDL input types; never pass the oracle in."""

    indexed_b, source_a = relation_rows(a_rows, b_rows)
    static = module.BoundedRelationStaticInput(indexed_boxes=indexed_b)
    batch = module.BoundedRelationBatch(
        source_boxes=source_a,
        expected_rows=None,
    )
    return static, batch


DEFAULT_A = (
    BedInterval("chr1", 10, 20, 100),
    BedInterval("chr1", 20, 30, 101),
    BedInterval("chr2", 10, 20, 102),
    BedInterval("chr3", 0, 1, 103),
    BedInterval("chr1", 16_777_215, 16_777_216, 104),
)

DEFAULT_B = (
    BedInterval("chr1", 15, 20, 200),
    BedInterval("chr1", 20, 25, 201),
    BedInterval("chr2", 19, 21, 202),
    BedInterval("chr3", 1, 2, 203),
    BedInterval("chr1", 16_777_214, 16_777_216, 204),
    BedInterval("chr1", 18, 22, 205),
    BedInterval("chr4", 10, 20, 206),
)

DEFAULT_EXPECTED_PAIRS = (
    (100, 200),
    (100, 205),
    (101, 201),
    (101, 205),
    (102, 202),
    (104, 204),
)

