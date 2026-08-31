from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from scripts import goal2855_v2_5_current_canonical_harness_packet_runner as runner


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2984_barnes_hut_second_arch_profile_policy_2026-06-01.md"
)


class Goal2984BarnesHutSecondArchProfilePolicyTest(unittest.TestCase):
    def test_runner_declares_default_and_second_arch_profiles(self) -> None:
        self.assertEqual(
            ((512, 16), (2048, 32), (8192, 32)),
            runner.BARNES_HUT_CASE_PROFILES["default"],
        )
        self.assertEqual(
            ((512, 16), (2048, 32)),
            runner.BARNES_HUT_CASE_PROFILES["second_arch_bounded"],
        )
        self.assertIn("8192-body Embree", runner.BARNES_HUT_CASE_PROFILE_BOUNDARIES["default"])
        self.assertIn(
            "not a release shortcut",
            runner.BARNES_HUT_CASE_PROFILE_BOUNDARIES["second_arch_bounded"],
        )

    def test_second_arch_profile_rewrites_only_goal2803_command(self) -> None:
        plan = runner.packet_plan(
            python_exe="python3",
            output_dir=Path("/tmp/goal2984_out"),
            work_dir=Path("/tmp/goal2984_work"),
            raw_output_dir=Path("/tmp/goal2984_raw"),
            fail_fast=False,
            barnes_hut_case_profile="second_arch_bounded",
        )
        barnes_hut = next(row for row in plan if row["goal"] == "Goal2803")
        other_rows = [row for row in plan if row["goal"] != "Goal2803"]

        command = " ".join(barnes_hut["command"])
        self.assertIn("--case 512:16", command)
        self.assertIn("--case 2048:32", command)
        self.assertNotIn("8192:32", command)
        self.assertEqual("second_arch_bounded", barnes_hut["barnes_hut_case_profile"])
        self.assertTrue(all(row["barnes_hut_case_profile"] is None for row in other_rows))

    def test_default_profile_remains_full_profile(self) -> None:
        plan = runner.packet_plan(
            python_exe="python3",
            output_dir=Path("/tmp/goal2984_out"),
            work_dir=Path("/tmp/goal2984_work"),
            raw_output_dir=Path("/tmp/goal2984_raw"),
            fail_fast=False,
        )
        barnes_hut = next(row for row in plan if row["goal"] == "Goal2803")
        command = " ".join(barnes_hut["command"])

        self.assertIn("--case 512:16", command)
        self.assertIn("--case 2048:32", command)
        self.assertIn("--case 8192:32", command)
        self.assertEqual("default", barnes_hut["barnes_hut_case_profile"])

    def test_report_and_readiness_keep_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2984",
            "second_arch_bounded",
            "default Goal2855 packet runner still uses",
            "not a release shortcut",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2984_barnes_hut_second_arch_profile_policy_2026-06-01.md"
            ]
        )
        self.assertIn(
            "run_goal2855_second_arch_packet_with_goal2984_bounded_barnes_hut_profile",
            packet["allowed_next_actions"],
        )
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
