#!/usr/bin/env python3
"""Plan the next OptiX collect-k k-way merge-chain diagnostic.

This is a local, no-GPU planning helper. It keeps the next native probe honest
by separating topology expectations and row contract from pod timing.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_TILE_COUNT = 128
DEFAULT_SEGMENT_CAPACITY = 2048
DEFAULT_CANDIDATE_COUNT = 262144


@dataclass(frozen=True)
class MergeTopology:
    fan_in: int
    input_segments: int
    segment_chain: list[int]
    merge_levels: int
    non_final_levels: int
    final_levels: int
    estimated_kernel_launches: int
    final_segment_capacity: int


def merge_topology(
    *,
    input_segments: int = DEFAULT_TILE_COUNT,
    segment_capacity: int = DEFAULT_SEGMENT_CAPACITY,
    fan_in: int,
) -> MergeTopology:
    if input_segments <= 0:
        raise ValueError("input_segments must be positive")
    if segment_capacity <= 0:
        raise ValueError("segment_capacity must be positive")
    if fan_in < 2:
        raise ValueError("fan_in must be at least 2")

    chain = [input_segments]
    current = input_segments
    current_capacity = segment_capacity
    estimated_launches = 0
    while current > 1:
        groups = current // fan_in
        carry = 1 if current % fan_in else 0
        if groups == 0:
            groups = 1
            carry = 0
        next_segments = groups + carry
        is_final = next_segments == 1
        estimated_launches += 3 if is_final else 4
        current_capacity *= fan_in
        current = next_segments
        chain.append(current)

    return MergeTopology(
        fan_in=fan_in,
        input_segments=input_segments,
        segment_chain=chain,
        merge_levels=len(chain) - 1,
        non_final_levels=max(0, len(chain) - 2),
        final_levels=1 if len(chain) > 1 else 0,
        estimated_kernel_launches=estimated_launches,
        final_segment_capacity=current_capacity,
    )


def _dedupe_sorted(rows: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    last: tuple[int, int] | None = None
    for row in sorted(rows):
        if row != last:
            result.append(row)
            last = row
    return result


def kway_merge_reference(segments: list[list[tuple[int, int]]], *, capacity: int | None = None) -> list[tuple[int, int]]:
    """Reference contract for the proposed native diagnostic.

    Inputs are sorted row-width=2 segments. The output is globally sorted,
    duplicate-free, and optionally capacity-bounded.
    """

    merged = _dedupe_sorted(row for segment in segments for row in segment)
    if capacity is not None:
        return merged[:capacity]
    return merged


def build_report() -> dict:
    binary = merge_topology(fan_in=2)
    four_way = merge_topology(fan_in=4)
    eight_way = merge_topology(fan_in=8)
    sample_segments = [
        [(1, 10), (2, 20), (4, 40)],
        [(1, 10), (3, 30), (7, 70)],
        [(0, 0), (4, 40), (8, 80)],
        [(2, 20), (5, 50), (9, 90)],
    ]
    return {
        "goal": "Goal1656",
        "status": "kway_merge_plan_recorded",
        "candidate_count": DEFAULT_CANDIDATE_COUNT,
        "tile_count": DEFAULT_TILE_COUNT,
        "segment_capacity": DEFAULT_SEGMENT_CAPACITY,
        "topologies": {
            "binary_current": asdict(binary),
            "four_way_candidate": asdict(four_way),
            "eight_way_reference_only": asdict(eight_way),
        },
        "reference_sample": {
            "segments": sample_segments,
            "unbounded": kway_merge_reference(sample_segments),
            "capacity_5": kway_merge_reference(sample_segments, capacity=5),
        },
        "claim_boundary": {
            "gpu_timing_recorded": False,
            "public_speedup_wording_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
    }


def write_markdown(report: dict, path: Path) -> None:
    binary = report["topologies"]["binary_current"]
    four_way = report["topologies"]["four_way_candidate"]
    eight_way = report["topologies"]["eight_way_reference_only"]
    text = f"""# Goal1656 v1.6.x OptiX Collect-K K-Way Merge Plan

## Verdict

`kway_merge_native_probe_prepared`

This is a local planning artifact for the next OptiX `COLLECT_K_BOUNDED`
merge-chain diagnostic. It records topology and correctness expectations only;
it does not contain GPU timing.

## Current Shape

- Candidate count: `{report['candidate_count']}`.
- CUB tile count: `{report['tile_count']}`.
- Segment capacity: `{report['segment_capacity']}`.
- Current binary segment chain: `{binary['segment_chain']}`.
- Current estimated merge-side kernel launches: `{binary['estimated_kernel_launches']}`.

## Candidate Shape

- Four-way segment chain: `{four_way['segment_chain']}`.
- Four-way merge levels: `{four_way['merge_levels']}`.
- Four-way estimated merge-side kernel launches: `{four_way['estimated_kernel_launches']}`.
- Eight-way reference-only chain: `{eight_way['segment_chain']}`.

The first native diagnostic should target four-way merge rather than eight-way
merge. Four-way reduces the merge chain substantially while keeping the rank
calculation bounded to three peer searches per input row. Eight-way is kept as
a topology reference only because seven peer searches per row is more likely to
increase register pressure and memory traffic before proving the idea.

## Correctness Contract

The diagnostic must preserve the existing row-width=2 `COLLECT_K_BOUNDED`
contract:

- Input segments are individually sorted.
- Output rows are globally sorted.
- Duplicate rows across any input segment are emitted once.
- Capacity bounds are applied after global sort and dedupe.
- Overflow behavior and emitted-count semantics must match the accepted path.

Reference sample unbounded output:

`{report['reference_sample']['unbounded']}`

Reference sample capacity-5 output:

`{report['reference_sample']['capacity_5']}`

## Next Native Probe

Add an opt-in diagnostic only, not enabled by
`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`, that compares:

- Control: current accepted CUB + binary compact-level merge path.
- Candidate: current CUB sort plus four-way compact-level merge for eligible
  full groups, falling back to the accepted binary/carry handling where needed.

The pod acceptance gate should require parity, same emitted count, same
overflow flag, and a measured total-time win before considering any promotion.

## Claim Boundary

This report does not authorize public speedup wording, stable
`COLLECT_K_BOUNDED` promotion, fastest-candidate promotion, release tags, or
release action.
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    report = build_report()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, args.md_out)
    if not args.json_out and not args.md_out:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
