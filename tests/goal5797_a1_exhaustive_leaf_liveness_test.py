from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts.goal5797_build_exhaustive_leaf_liveness import build


ROOT = Path(__file__).resolve().parents[1]
PREACTION = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_preaction_20260823.json")
RESULT = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json")
INDEPENDENT = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_independent_verification_20260823.json")


class Goal5797A1ExhaustiveLeafLivenessTest(unittest.TestCase):
    def test_result_rebuilds_and_covers_exact_frozen_leaf_universe(self):
        preaction = json.loads(PREACTION.read_text(encoding="utf-8"))
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(build(), result)
        self.assertEqual(len(preaction["mutations"]), 19)
        self.assertEqual(result["populated_leaf_count"], 19)
        self.assertEqual(result["decision_bearing_count"], 19)
        self.assertEqual(result["non_decision_bearing_count"], 0)
        self.assertEqual(result["projection_bytes_unchanged_count"], 19)
        self.assertEqual(result["single_expected_finding_count"], 19)
        self.assertEqual(
            result["preaction"]["sha256"],
            hashlib.sha256(PREACTION.read_bytes()).hexdigest())

    def test_require_status_ok_is_individually_decision_bearing(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        row = result["require_status_ok"]
        self.assertEqual(row["path"], "role_effects.finalize[1]")
        self.assertEqual(row["old_value"], "require_status_ok")
        self.assertEqual(row["mutated_value"], "allow_status_error")
        self.assertEqual(row["verdict_delta"], "ACCEPT_TO_REJECT")
        self.assertEqual(row["reason_ids"], ["CP001_ROLE_EFFECT_MISMATCH"])
        self.assertTrue(row["projection_bytes_unchanged"])

    def test_independent_verifier_imports_no_rtdl_and_agrees(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
        self.assertFalse(independent["imports_rtdl"])
        self.assertEqual(independent["status"], "PASS")
        self.assertEqual(independent["leaf_universe_count"], 19)
        self.assertEqual(independent["decision_bearing_count"], 19)
        self.assertTrue(independent["require_status_ok_decision_bearing"])
        self.assertEqual(
            independent["result_file_sha256"],
            hashlib.sha256(RESULT.read_bytes()).hexdigest())
        self.assertEqual(result["registered_performance_timing_count"], 0)
        self.assertEqual(independent["registered_performance_timing_count"], 0)


if __name__ == "__main__":
    unittest.main()
