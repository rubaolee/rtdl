from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1903_v2_partner_pod_batch_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal1918_fixed_radius_reference_oom_guard_2026-05-13.md"


class Goal1918FixedRadiusReferenceOomGuardTest(unittest.TestCase):
    def test_runner_caps_dense_fixed_radius_reference_pairs(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("FIXED_RADIUS_MAX_REFERENCE_PAIRS", text)
        self.assertIn("--max-reference-pairs", text)
        self.assertIn("50000000", text)

    def test_report_documents_pod_failure_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("OutOfMemoryError", text)
        self.assertIn("event_hotspot_flags_partner_columns", text)
        self.assertIn("not the v2 native OptiX partner-device", text)
        self.assertIn("does not authorize release wording", text)


if __name__ == "__main__":
    unittest.main()
