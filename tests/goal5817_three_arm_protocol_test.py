from __future__ import annotations

from collections import Counter
import unittest

from experiments.goal5817_three_arm.evaluate import evaluate
from experiments.goal5817_three_arm.protocol import (
    ARMS, BLOCK_COUNT, COMPARISONS, REGIMES, TASKS, schedule,
)


def _synthetic_workers() -> list[dict[str, object]]:
    scale = {"DIRECT": 100, "PYOPTIX": 500, "RTDL": 510}
    return [
        {
            **row,
            "pid": 10_000 + int(row["ordinal"]),
            "metric_ns": scale[str(row["arm"])] * (100 + int(row["block"])),
            "registered_performance_timing_count": (
                64 if row["regime"] == "STEADY_E2E" else 1),
        }
        for row in schedule()
    ]


class Goal5817ThreeArmProtocolTest(unittest.TestCase):
    def test_schedule_is_complete_and_position_balanced(self) -> None:
        rows = schedule()
        self.assertEqual(
            len(rows), len(TASKS) * len(REGIMES) * BLOCK_COUNT * len(ARMS))
        self.assertEqual(len({row["worker_id"] for row in rows}), len(rows))
        for task in TASKS:
            for regime in REGIMES:
                selected = [row for row in rows
                            if row["task"] == task and row["regime"] == regime]
                positions = Counter(
                    (row["arm"], row["position"]) for row in selected)
                self.assertEqual(
                    set(positions.values()), {BLOCK_COUNT // len(ARMS)})

    def test_evaluator_reports_all_three_pairwise_decompositions(self) -> None:
        result = evaluate({"workers": _synthetic_workers()})
        self.assertEqual(
            result["row_count"],
            len(TASKS) * len(REGIMES) * len(COMPARISONS))
        ratios = {
            (row["numerator"], row["denominator"]): row["ratio"]
            for row in result["rows"]
            if row["task"] == "relation" and row["regime"] == "STEADY_E2E"
        }
        self.assertAlmostEqual(ratios[("RTDL", "PYOPTIX")], 1.02)
        self.assertAlmostEqual(ratios[("PYOPTIX", "DIRECT")], 5.0)
        self.assertAlmostEqual(ratios[("RTDL", "DIRECT")], 5.1)
        self.assertEqual(result["gated_row_count"], len(TASKS) * len(REGIMES))
        self.assertIs(result["current_source_direct_arm_present"], True)
        self.assertIs(result["historical_goal5802_values_used"], False)

    def test_evaluator_rejects_row_drop_and_pid_reuse(self) -> None:
        workers = _synthetic_workers()
        with self.assertRaisesRegex(RuntimeError, "universe"):
            evaluate({"workers": workers[:-1]})
        workers[1]["pid"] = workers[0]["pid"]
        with self.assertRaisesRegex(RuntimeError, "freshness"):
            evaluate({"workers": workers})


if __name__ == "__main__":
    unittest.main()
