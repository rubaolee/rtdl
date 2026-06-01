from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2929_tier_c_no_regression_and_10_benchmark_foundation_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2929_tier_c_no_regression_pod"


class Goal2929TierCNoRegressionFoundationTest(unittest.TestCase):
    def test_contact_manifold_optix_smoke_matches_reference(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "contact_manifold_grid512_optix.json").read_text(encoding="utf-8"))

        self.assertEqual("bounded_collision_witness_contact_manifold", payload["app"])
        self.assertEqual("aabb_broadphase_collect_k", payload["mode"])
        self.assertEqual("optix", payload["candidate_discovery_backend"])
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertFalse(payload["overflowed"])
        self.assertIn("AABB_INDEX_QUERY_2D", payload["candidate_discovery_primitive"])
        self.assertFalse(payload["engine_boundary"]["native_collision_logic_allowed"])

    def test_robot_validation_and_timing_smokes_are_bounded(self) -> None:
        validation = json.loads((ARTIFACT_DIR / "robot_pose_flags_512_256_validation.json").read_text(encoding="utf-8"))
        timing = json.loads((ARTIFACT_DIR / "robot_pose_flags_65536_1024_timing_skip_validation.json").read_text(encoding="utf-8"))

        self.assertEqual("robot_collision_screening", validation["app"])
        self.assertEqual("prepared_pose_flags", validation["optix_summary_mode"])
        self.assertTrue(validation["matches_oracle"])
        self.assertEqual("cpu_oracle", validation["validation_mode"])
        self.assertTrue(validation["native_continuation_active"])

        self.assertEqual(65536, timing["pose_count"])
        self.assertIsNone(timing["matches_oracle"])
        self.assertEqual("skipped", timing["validation_mode"])
        self.assertTrue(timing["native_continuation_active"])
        self.assertIn("one collision flag per pose", timing["boundary"])

    def test_toolchain_and_report_preserve_no_regression_boundary(self) -> None:
        toolchain = json.loads((ARTIFACT_DIR / "toolchain.json").read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual("1ec2cf9efe23eb2c4067671b394cc32d52c64e11", toolchain["source_commit"])
        self.assertEqual([], toolchain["source_dirty"])
        self.assertEqual("compute_86", toolchain["rtdl_optix_ptx_arch"])
        self.assertEqual("nvcc", toolchain["rtdl_optix_ptx_compiler"])
        self.assertTrue(toolchain["tier_c_no_regression_only"])
        self.assertFalse(toolchain["release_authorized"])
        self.assertFalse(toolchain["public_speedup_claim_authorized"])

        for phrase in (
            "Goal2929",
            "10-Benchmark Position",
            "Tier C no-regression",
            "does not authorize v2.5 release",
            "not public speedup",
        ):
            self.assertIn(phrase, report)

    def test_manifest_promotes_contact_and_robot_to_goal2929_current_smoke(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        apps = {row["app_id"]: row for row in manifest["apps"]}

        self.assertEqual(10, manifest["benchmark_app_count"])
        self.assertEqual({"A": 3, "B": 4, "C": 3}, manifest["tier_counts"])
        self.assertIn("goal2929", apps["contact_manifold"]["canonical_harness_status"])
        self.assertIn("Goal2929", apps["contact_manifold"]["pod_evidence_status"])
        self.assertIn("goal2929", apps["robot_collision"]["canonical_harness_status"])
        self.assertIn("Goal2929", apps["robot_collision"]["pod_evidence_status"])
        self.assertEqual("accept", rt.validate_v2_5_tiered_benchmark_manifest()["status"])


if __name__ == "__main__":
    unittest.main()
