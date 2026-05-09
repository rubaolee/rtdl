from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from scripts import goal1614_v1_6_4_collect_k_bounds_stress as goal1614


class Goal1614CollectKBoundsStressTest(unittest.TestCase):
    def test_fake_native_package_accepts_exact_bounds_stress(self) -> None:
        payload = goal1614.validate_package(goal1614.run_package())

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_local_bounds_stress")
        self.assertEqual(payload["case_count"], 9)
        self.assertEqual(len(payload["records"]), 9)
        self.assertEqual(payload["failed"], ())
        self.assertEqual(payload["skipped_required"], ())

    def test_overflow_cases_fail_closed_and_preserve_output_when_present(self) -> None:
        payload = goal1614.validate_package(goal1614.run_package())
        overflow_records = [record for record in payload["records"] if record["expected_status"] == "overflow"]

        self.assertEqual(len(overflow_records), 2)
        for record in overflow_records:
            with self.subTest(case=record["case"]):
                self.assertTrue(record["overflow_fail_closed"])
                self.assertFalse(record["partial_result_returned"])
                self.assertTrue(record["output_buffer_preserved"])

    def test_invalid_shape_cases_are_caught_as_expected(self) -> None:
        payload = goal1614.validate_package(goal1614.run_package())
        invalid_records = [record for record in payload["records"] if record["expected_status"] == "value_error"]

        self.assertEqual(len(invalid_records), 2)
        for record in invalid_records:
            with self.subTest(case=record["case"]):
                self.assertEqual(record["status"], "pass")
                self.assertIn("ValueError", record["observed_error"])

    def test_authorization_flags_remain_false(self) -> None:
        payload = goal1614.validate_package(goal1614.run_package())

        for flag in (
            "stable_collect_k_promotion_authorized",
            "public_speedup_wording_authorized",
            "true_zero_copy_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rtx_wording_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(payload[flag], False)

    def test_artifact_generation_preserves_scope_and_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "bounds.json"
            md_path = Path(tmp) / "bounds.md"
            rc = goal1614.main(["--json-out", str(json_path), "--md-out", str(md_path)])

            self.assertEqual(rc, 0)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertTrue(payload["accepted"])
        self.assertIn("exact-bounds stress evidence", markdown)
        self.assertIn("Timing is not performance evidence", markdown)
        self.assertIn("does not authorize stable promotion", markdown)
        self.assertIn("true zero-copy wording", markdown)

    def test_external_reviews_and_consensus_exist_without_overclaiming(self) -> None:
        root = Path(__file__).resolve().parents[1]
        review_paths = (
            root / "docs/reviews/goal1614_v1_6_4_collect_k_bounds_stress_claude_review_2026-05-09.md",
            root / "docs/reviews/goal1614_v1_6_4_collect_k_bounds_stress_gemini_review_2026-05-09.md",
            root / "docs/reviews/goal1614_v1_6_4_collect_k_bounds_stress_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("local correctness evidence", consensus)
        self.assertIn("does not\nauthorize stable", consensus)
        self.assertIn("not representative RTX evidence", consensus)


if __name__ == "__main__":
    unittest.main()
