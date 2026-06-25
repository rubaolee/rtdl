from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_goal4641_clean_tree_reproducibility_decision import V4_GOAL4641_DECISION
from rtdsl.v4_goal4641_clean_tree_reproducibility_decision import (
    validate_v4_goal4641_clean_tree_reproducibility,
)


class V4Goal4641CleanTreeReproducibilityTest(unittest.TestCase):
    def test_clean_tree_gate_records_committed_validation(self) -> None:
        decision = validate_v4_goal4641_clean_tree_reproducibility(ROOT)

        self.assertEqual(V4_GOAL4641_DECISION, decision["decision"])
        self.assertTrue(decision["clean_status_before"])
        self.assertTrue(decision["clean_status_after"])
        self.assertTrue(decision["full_v4_tests_passed"])
        self.assertTrue(decision["catalog_dry_run_passed"])
        self.assertTrue(decision["quickstart_passed"])
        self.assertTrue(decision["validated_commit"].startswith("35d04dbf"))
        self.assertIn("tests.v4_goal4641_clean_tree_reproducibility_test", decision["tests"])

    def test_clean_tree_gate_has_committed_evidence(self) -> None:
        decision = validate_v4_goal4641_clean_tree_reproducibility(ROOT)

        evidence = set(decision["evidence"])
        self.assertIn("future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md", evidence)
        self.assertIn("tests/v4_goal4641_clean_tree_reproducibility_test.py", evidence)
        for relative in evidence:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).exists())

    def test_goal4641_never_authorizes_release_or_overclaims(self) -> None:
        decision = validate_v4_goal4641_clean_tree_reproducibility(ROOT)

        for flag in (
            "release_authorized",
            "release_candidate_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "non_python_host_claim_authorized",
        ):
            self.assertFalse(decision[flag])


if __name__ == "__main__":
    unittest.main()
