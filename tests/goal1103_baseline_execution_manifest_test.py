from __future__ import annotations

import unittest

from scripts.goal1103_baseline_execution_manifest import build_manifest
from scripts.goal1103_baseline_execution_manifest import to_markdown


class Goal1103BaselineExecutionManifestTest(unittest.TestCase):
    def test_manifest_has_four_ordered_rows_and_no_claim_boundary(self) -> None:
        payload = build_manifest()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["row_count"], 4)
        self.assertEqual([row["recommended_order"] for row in payload["rows"]], [1, 2, 3, 4])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_current_mac_recommendations_do_not_blindly_run_large_rows(self) -> None:
        rows = {row["name"]: row for row in build_manifest()["rows"]}

        self.assertEqual(rows["barnes_hut_validation_embree"]["current_mac_recommendation"], "safe_to_run")
        self.assertEqual(rows["facility_cpu_oracle"]["current_mac_recommendation"], "prefer_linux_or_windows_large_ram")
        self.assertEqual(rows["facility_embree"]["current_mac_recommendation"], "prefer_linux_or_windows_large_ram")
        self.assertEqual(
            rows["barnes_hut_timing_embree"]["current_mac_recommendation"],
            "do_not_run_on_16gb_mac_without_user_approval",
        )
        self.assertIn("2.5M copies expands to 10M customers", rows["facility_cpu_oracle"]["why"])

    def test_commands_target_goal1101_profiler_and_goal1102_artifact_names(self) -> None:
        payload = build_manifest()

        for row in payload["rows"]:
            self.assertIn("scripts/goal1101_current_contract_non_optix_baseline_profiler.py", row["command"])
            self.assertIn(row["expected_artifact"], row["command"])
            self.assertTrue(row["expected_artifact"].startswith("docs/reports/goal1101_current_contract_non_optix_baselines/"))

    def test_markdown_includes_row_by_row_commands(self) -> None:
        markdown = to_markdown(build_manifest())

        self.assertIn("Goal1103 Baseline Execution Manifest", markdown)
        self.assertIn("Recommended next local action", markdown)
        self.assertIn("barnes_hut_validation_embree", markdown)
        self.assertIn("do_not_run_on_16gb_mac_without_user_approval", markdown)


if __name__ == "__main__":
    unittest.main()
