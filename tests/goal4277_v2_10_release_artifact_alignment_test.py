from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs" / "release_reports" / "v2_10" / "README.md"
PARTNER_BOUNDARIES = ROOT / "docs" / "partner_acceleration_boundaries.md"
REPORT = ROOT / "docs" / "reports" / "goal4277_v2_10_release_artifact_alignment_2026-06-11.md"


class Goal4277V210ReleaseArtifactAlignmentTest(unittest.TestCase):
    def test_root_version_marker_matches_current_source_tree_surface(self) -> None:
        self.assertEqual("v2.10", (ROOT / "VERSION").read_text(encoding="utf-8").strip())

    def test_v2_10_release_package_uses_current_paths_and_boundaries(self) -> None:
        text = RELEASE.read_text(encoding="utf-8")

        self.assertIn("RTDL v2.10 Release Package", text)
        self.assertIn("Version marker: `v2.10`", text)
        self.assertIn("examples/current/getting_started/rtdl_hello_world.py", text)
        self.assertIn("tutorials", text)
        self.assertIn("source-tree milestone", text)
        self.assertIn("not a package-install release", text)
        self.assertIn("not a broad RT-core speedup claim", text)
        self.assertIn("not an automatic partner-selection promise", text)
        self.assertIn("not a general zero-copy/device-residency product claim", text)
        self.assertIn("Do not move the existing tag", text)
        self.assertNotIn("examples/v2_0", text)
        self.assertNotIn("Version marker: `v2.6`", text)

    def test_release_package_links_to_existing_evidence(self) -> None:
        text = RELEASE.read_text(encoding="utf-8")
        required_targets = (
            "goal4267_v2_10_milestone_release_packet_2026-06-10.md",
            "goal4268_claude_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md",
            "goal4269_gemini_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md",
            "goal4270_v2_10_milestone_release_3ai_consensus_2026-06-10.md",
            "goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md",
            "goal4271_v2_10_user_doc_cleanup_audit_2026-06-10.md",
            "goal4274_current_doc_recheck_2026-06-10.md",
            "goal4276_top_level_tutorial_reorganization_2026-06-10.md",
        )

        for target in required_targets:
            self.assertIn(target, text)
            self.assertTrue(any(path.name == target for path in ROOT.rglob(target)), target)

    def test_partner_boundary_report_names_are_real_current_artifacts(self) -> None:
        text = PARTNER_BOUNDARIES.read_text(encoding="utf-8")
        self.assertIn("goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md", text)
        self.assertIn("goal4267_v2_10_milestone_release_packet_2026-06-10.md", text)
        self.assertIn("goal4270_v2_10_milestone_release_3ai_consensus_2026-06-10.md", text)

        self.assertNotIn("goal4266_cupy_numba_user_partner_decision_matrix_2026-06-10.md", text)
        self.assertNotIn("goal4267_v2_10_milestone_release_readiness_2026-06-10.md", text)
        self.assertNotIn("goal4270_v2_10_public_release_tag_push_2026-06-10.md", text)

    def test_existing_v2_10_tag_is_recorded_but_not_moved_by_this_cleanup(self) -> None:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "v2.10"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not move the existing tag", report)
        self.assertIn("2888b5ba", report)
        self.assertIn("1b66bddf", report)


if __name__ == "__main__":
    unittest.main()
