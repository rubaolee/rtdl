from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1868_road_hazard_partner_priority_flags_pod_smoke.py"
REPORT = ROOT / "docs" / "reports" / "goal1868_road_hazard_partner_priority_flags_pod_smoke_plan_2026-05-13.md"


class Goal1868RoadHazardPartnerPriorityFlagsPodSmokePlanTest(unittest.TestCase):
    def test_runner_targets_goal1865_adapter_and_prints_progress(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", text)
        self.assertIn("[setup]", text)
        self.assertIn("[partner]", text)
        self.assertIn("[artifact]", text)
        self.assertIn("flush=True", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("whole_app_speedup_claim_authorized", text)

    def test_runner_validates_both_partners_and_expected_flags(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("cupy,torch", text)
        self.assertIn("expected_counts", text)
        self.assertIn("expected_flags", text)
        self.assertIn("priority flags mismatch", text)
        self.assertIn("hit counts mismatch", text)

    def test_report_keeps_pod_evidence_pending(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: ready-for-pod", report)
        self.assertIn("does not contain hardware evidence yet", report)
        self.assertIn("does not authorize v2.0", report)
        self.assertIn("release wording", report)
        self.assertIn("goal1868_road_hazard_partner_priority_flags_pod_smoke.json", report)


if __name__ == "__main__":
    unittest.main()
