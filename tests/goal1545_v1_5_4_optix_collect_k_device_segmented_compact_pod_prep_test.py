from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1545_v1_5_4_optix_collect_k_device_segmented_compact_pod_prep_2026-05-08.md"

Row = tuple[int, int]


def materialize_mark_compact_level(
    pairs: list[tuple[list[Row], list[Row]]],
    *,
    output_capacity: int,
) -> tuple[list[list[Row]], list[int], list[bool]]:
    outputs: list[list[Row]] = []
    counts: list[int] = []
    overflowed: list[bool] = []
    for first, second in pairs:
        merged = sorted(first + second)
        compact: list[Row] = []
        previous: Row | None = None
        for row in merged:
            if previous is None or row != previous:
                compact.append(row)
            previous = row
        outputs.append(compact[:output_capacity])
        counts.append(len(compact))
        overflowed.append(len(compact) > output_capacity)
    return outputs, counts, overflowed


def atomic_compact_can_break_sorted_order(block_outputs: list[list[Row]]) -> list[Row]:
    """Model an allowed atomicAdd schedule where block 1 wins before block 0."""
    out: list[Row] = []
    for block in reversed(block_outputs):
        out.extend(block)
    return out


def device_prefix_topology(candidate_count: int) -> dict[str, int]:
    tile_size = 2048
    tile_count = (candidate_count + tile_size - 1) // tile_size
    current_segments = tile_count
    segment_capacity = tile_size
    merge_launches = 0
    carry_copies = 0
    while current_segments > 1:
        pair_count = current_segments // 2
        has_carry = (current_segments % 2) != 0
        output_segment_capacity = segment_capacity * 2
        if output_segment_capacity >= 4096:
            merge_launches += 4 if current_segments != 2 else pair_count * 3
        else:
            merge_launches += 1
        if has_carry:
            carry_copies += 1
        current_segments = pair_count + (1 if has_carry else 0)
        segment_capacity = output_segment_capacity
    return {
        "tile_count": tile_count,
        "sort_launches": 1,
        "merge_launches": merge_launches,
        "carry_copies": carry_copies,
    }


class Goal1545V154OptixCollectKDeviceSegmentedCompactPodPrepTest(unittest.TestCase):
    def test_segmented_reference_preserves_pair_boundaries_and_order(self) -> None:
        pairs = [
            ([(1, 10), (3, 30)], [(1, 10), (2, 20)]),
            ([(0, 0), (5, 50)], [(4, 40), (5, 50)]),
        ]

        outputs, counts, overflowed = materialize_mark_compact_level(pairs, output_capacity=3)

        self.assertEqual(outputs[0], [(1, 10), (2, 20), (3, 30)])
        self.assertEqual(outputs[1], [(0, 0), (4, 40), (5, 50)])
        self.assertEqual(counts, [3, 3])
        self.assertEqual(overflowed, [False, False])

    def test_segmented_reference_reports_overflow_without_overwriting_bound(self) -> None:
        pairs = [([(1, 10), (3, 30)], [(1, 10), (2, 20)])]

        outputs, counts, overflowed = materialize_mark_compact_level(pairs, output_capacity=2)

        self.assertEqual(outputs[0], [(1, 10), (2, 20)])
        self.assertEqual(counts, [3])
        self.assertEqual(overflowed, [True])

    def test_atomic_compact_is_not_sorted_order_safe(self) -> None:
        block0 = [(1, 10), (2, 20)]
        block1 = [(3, 30), (4, 40)]

        self.assertEqual(atomic_compact_can_break_sorted_order([block0, block1]), [(3, 30), (4, 40), (1, 10), (2, 20)])
        self.assertNotEqual(atomic_compact_can_break_sorted_order([block0, block1]), block0 + block1)

    def test_device_prefix_candidate_topology_is_explicit(self) -> None:
        self.assertEqual(
            device_prefix_topology(4097),
            {"tile_count": 3, "sort_launches": 1, "merge_launches": 7, "carry_copies": 1},
        )
        self.assertEqual(
            device_prefix_topology(65537),
            {"tile_count": 33, "sort_launches": 1, "merge_launches": 23, "carry_copies": 5},
        )
        self.assertEqual(
            device_prefix_topology(131072),
            {"tile_count": 64, "sort_launches": 1, "merge_launches": 23, "carry_copies": 0},
        )

    def test_report_keeps_pod_queue_and_claim_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("Prepared and compile-validated", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT", text)
        self.assertIn("Linux compile validation passed", text)
        self.assertIn("Atomic compact should only be tested", text)
        self.assertIn("Clean sync to `origin/main`", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
