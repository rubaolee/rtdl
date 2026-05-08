from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1534_v1_5_4_optix_collect_k_parallel_compact_reference_2026-05-08.md"


Row = tuple[int, int]


def rank_only_union_with_holes(first: list[Row], second: list[Row]) -> list[Row | None]:
    """Reference for the rejected Goal1533 shortcut."""
    out: list[Row | None] = [None] * (len(first) + len(second))
    first_set = set(first)
    for index, row in enumerate(first):
        less_in_second = sum(1 for candidate in second if candidate < row)
        out[index + less_in_second] = row
    for index, row in enumerate(second):
        if row in first_set:
            continue
        less_in_first = sum(1 for candidate in first if candidate < row)
        out[index + less_in_first] = row
    return out


def materialize_mark_compact(first: list[Row], second: list[Row], capacity: int) -> tuple[list[Row], int, bool]:
    merged: list[Row] = []
    left = 0
    right = 0
    while left < len(first) or right < len(second):
        if right >= len(second) or (left < len(first) and first[left] <= second[right]):
            merged.append(first[left])
            left += 1
        else:
            merged.append(second[right])
            right += 1

    marks: list[int] = []
    previous: Row | None = None
    for row in merged:
        keep = previous is None or row != previous
        marks.append(1 if keep else 0)
        previous = row

    compact: list[Row] = []
    for row, mark in zip(merged, marks):
        if mark:
            compact.append(row)

    return compact[:capacity], len(compact), len(compact) > capacity


class Goal1534V154OptixCollectKParallelCompactReferenceTest(unittest.TestCase):
    def test_rank_only_union_leaves_holes_when_duplicates_are_skipped(self) -> None:
        first = [(1, 1001), (3, 1003)]
        second = [(1, 1001), (2, 1002)]

        self.assertEqual(
            rank_only_union_with_holes(first, second),
            [(1, 1001), None, (2, 1002), (3, 1003)],
        )

    def test_materialize_mark_compact_matches_sorted_set_union(self) -> None:
        first = [(1, 1001), (3, 1003)]
        second = [(1, 1001), (2, 1002)]

        rows, emitted, overflowed = materialize_mark_compact(first, second, capacity=3)

        self.assertEqual(rows, sorted(set(first) | set(second)))
        self.assertEqual(emitted, 3)
        self.assertFalse(overflowed)

    def test_materialize_mark_compact_reports_overflow_without_overwriting_bound(self) -> None:
        first = [(1, 1001), (3, 1003)]
        second = [(1, 1001), (2, 1002)]

        rows, emitted, overflowed = materialize_mark_compact(first, second, capacity=2)

        self.assertEqual(rows, [(1, 1001), (2, 1002)])
        self.assertEqual(emitted, 3)
        self.assertTrue(overflowed)

    def test_reference_handles_interleaved_goal_style_rows(self) -> None:
        first = [(0, 1000), (74, 1074), (148, 1148), (222, 1222)]
        second = [(37, 1037), (74, 1074), (185, 1185), (222, 1222)]

        rows, emitted, overflowed = materialize_mark_compact(first, second, capacity=6)

        self.assertEqual(rows, sorted(set(first) | set(second)))
        self.assertEqual(emitted, 6)
        self.assertFalse(overflowed)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("correctness reference", text)
        self.assertIn("Prefix-sum the marks", text)
        self.assertIn("serial one-thread merge remains the safe fallback", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
