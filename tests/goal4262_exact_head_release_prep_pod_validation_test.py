import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4262_exact_head_release_prep_pod_validation_2026-06-09.md"


class Goal4262ExactHeadReleasePrepPodValidationTest(unittest.TestCase):
    def test_report_records_exact_head_validation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Source commit | `3cbd7557`", text)
        self.assertIn("NVIDIA RTX 4000 Ada Generation", text)
        self.assertIn("Ran 18 tests", text)
        self.assertIn("OK", text)

    def test_report_records_validated_release_prep_slice(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for module in (
            "tests.goal4219_major_performance_target_map_test",
            "tests.goal4257_v2_10_release_candidate_packet_draft_test",
            "tests.goal4258_public_claim_wording_repair_closure_test",
            "tests.goal4254_v2_10_public_claim_wording_candidate_test",
            "tests.goal4248_current_public_docs_claim_boundary_scan_test",
        ):
            self.assertIn(module, text)

    def test_boundary_stays_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize release", text)
        self.assertIn("RTDL-beats-RayJoin", text)
        self.assertIn("AMD/HIPRT", text)
        self.assertIn("app-specific native-engine logic", text)


if __name__ == "__main__":
    unittest.main()
