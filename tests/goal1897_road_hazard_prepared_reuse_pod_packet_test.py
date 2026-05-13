from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1897_road_hazard_prepared_reuse_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal1897_road_hazard_prepared_reuse_pod_packet_2026-05-13.md"


class Goal1897RoadHazardPreparedReusePodPacketTest(unittest.TestCase):
    def test_runner_records_environment_builds_optix_and_runs_goal1889_artifacts(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("nvidia-smi", text)
        self.assertIn("REQUIRE_RTX", text)
        self.assertIn('if [[ "${REQUIRE_RTX}" == "1"', text)
        self.assertIn("make build-optix", text)
        self.assertIn("partner_probe.json", text)
        self.assertIn("tests.goal1889_road_hazard_prepared_partner_reuse_perf_test", text)
        self.assertIn("tests.goal1869_road_hazard_v2_partner_perf_plan_test", text)
        self.assertIn("RTDL_SOURCE_COMMIT_LABEL", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_${count}.json", text)
        self.assertIn("goal1897_road_hazard_prepared_reuse_pod_summary.json", text)
        self.assertIn("goal_extension", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("whole_app_speedup_claim_authorized", text)

    def test_report_keeps_local_dry_run_and_release_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pre-pod-ready", text)
        self.assertIn("scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", text)
        self.assertIn("REQUIRE_RTX=0", text)
        self.assertIn("must not be used for accepted RTX evidence", text)
        self.assertIn("Focused tests passed: 14 tests", text)
        self.assertIn("0.1093116635", text)
        self.assertIn("only proves the packet mechanics", text)
        self.assertIn("does not authorize v2.0 release readiness", text)
        self.assertIn("development evidence only", text)


if __name__ == "__main__":
    unittest.main()
