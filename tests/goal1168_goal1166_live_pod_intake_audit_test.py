import unittest
from pathlib import Path

from scripts.goal1168_goal1166_live_pod_intake_audit import DEFAULT_ARTIFACT_DIR, audit


class Goal1168Goal1166LivePodIntakeAuditTest(unittest.TestCase):
    def test_live_pod_artifacts_are_engineering_accepted_but_claim_blocked(self):
        payload = audit(DEFAULT_ARTIFACT_DIR)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["engineering_verdict"], "accept")
        self.assertEqual(payload["claim_grade_verdict"], "blocked")
        self.assertIn(
            "source tree was copied from a dirty local working tree",
            payload["claim_grade_blockers"],
        )
        self.assertIn("Jaccard chunk256 remains an expected diagnostic failure", payload["claim_grade_blockers"])
        self.assertEqual(
            payload["source_markers"],
            ["d0ebf9d69041cf013b7af4dcb20a570d25d92c3f-local-dirty-goal1166"],
        )

    def test_all_checks_are_explicitly_true(self):
        payload = audit(DEFAULT_ARTIFACT_DIR)

        false_checks = [name for name, result in payload["checks"].items() if result is not True]
        self.assertEqual(false_checks, [])

    def test_expected_artifact_directory_is_present(self):
        self.assertTrue(Path(DEFAULT_ARTIFACT_DIR).exists())


if __name__ == "__main__":
    unittest.main()
