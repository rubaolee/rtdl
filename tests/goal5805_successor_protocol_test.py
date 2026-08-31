"""Host-only hostile checks for the Goal5805 successor protocol."""

from __future__ import annotations

import copy
from pathlib import Path
import unittest

from experiments.goal5805_successor.evaluate import evaluate
from experiments.goal5805_successor.protocol import (
    BLOCK_COUNT, build_freeze, validate_freeze,
)


ROOT = Path(__file__).resolve().parents[1]


class Goal5805SuccessorProtocolTest(unittest.TestCase):
    def test_freeze_rehashes_and_protocol_mutation_rejects(self):
        value = build_freeze(ROOT, predecessor_result_sha256="a" * 64)
        validate_freeze(value, ROOT, rehash=True)
        mutant = copy.deepcopy(value)
        mutant["steady_repetitions"] += 1
        with self.assertRaisesRegex(RuntimeError, "seal"):
            validate_freeze(mutant, ROOT, rehash=False)

    def test_evaluator_uses_all_six_rows_and_all_blocks(self):
        workers = []
        ordinal = 0
        for task in ("relation", "triangle"):
            for block in range(BLOCK_COUNT):
                for arm in ("RTDL", "PYOPTIX", "PYOPTIX", "RTDL"):
                    factor = 102 if arm == "RTDL" else 100
                    workers.append({
                        "ordinal": ordinal, "task": task, "block": block,
                        "arm": arm,
                        "result": {
                            "deployment_cold_ns": factor * 10,
                            "prepare_ns": factor * 20,
                            "steady_median_ns": factor * 30,
                            "registered_performance_timing_count": 66,
                        },
                    })
                    ordinal += 1
        value = evaluate({"workers": workers})
        self.assertEqual(value["row_count"], 6)
        self.assertEqual(value["pass_count"], 6)
        self.assertEqual(value["formal_worker_count"], 128)
        self.assertEqual(value["registered_performance_timing_count"], 8448)
        self.assertTrue(all(len(row["blocks"]) == 16 for row in value["rows"]))


if __name__ == "__main__":
    unittest.main()

