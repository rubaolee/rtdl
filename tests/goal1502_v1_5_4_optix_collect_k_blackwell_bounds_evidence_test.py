import json
from pathlib import Path
import unittest

from scripts.goal1502_v1_5_4_python_optix_collect_k_bounds_probe import validate_probe


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT / "docs" / "reports" / "goal1502_v1_5_4_python_optix_collect_k_bounds_probe_blackwell_2026-05-08.json"
)


class Goal1502V154OptixCollectKBlackwellBoundsEvidenceTest(unittest.TestCase):
    def test_blackwell_bounds_artifact_is_validated_and_claim_conservative(self) -> None:
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        validate_probe(report)

        self.assertEqual(report["goal"], "Goal1502")
        self.assertIn("Blackwell", report["device_name"])
        self.assertTrue(report["measured_on_real_nvidia"])
        for flag, value in report["claim_flags"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)

    def test_blackwell_bounds_artifact_covers_required_edges(self) -> None:
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

        overflow = report["overflow_case"]
        self.assertEqual(overflow["valid_count"], 3)
        self.assertTrue(overflow["overflowed"])
        self.assertTrue(overflow["fail_closed_output_preserved"])

        dynamic = report["dynamic_row_width_case"]
        self.assertEqual(dynamic["row_width"], 3)
        self.assertTrue(dynamic["same_candidate_rows"])
        self.assertTrue(dynamic["same_valid_count"])
        self.assertTrue(dynamic["same_overflowed_flag"])

        int64_max_pair = report["int64_max_pair_case"]
        self.assertEqual(int64_max_pair["row_width"], 2)
        self.assertTrue(int64_max_pair["same_candidate_rows"])
        self.assertTrue(int64_max_pair["same_valid_count"])
        self.assertTrue(int64_max_pair["same_overflowed_flag"])


if __name__ == "__main__":
    unittest.main()
