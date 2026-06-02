from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.md"
)
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.json"
)


class Goal2993V26NumbaNeutralHandoffL4PodTest(unittest.TestCase):
    def test_report_records_toolchain_fix_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "v2.6 neutral",
            "NVIDIA L4",
            "PTX `.version 8.7`",
            "PTX `8.6`",
            "numba-cuda[cu12]",
            "NUMBA_CUDA_USE_NVIDIA_BINDING=1",
            "NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1",
            "without the legacy torch carrier",
            "large L4 pod runtime conformance passed",
            "does not authorize v2.6 release",
            "true-zero-copy wording",
            "automatic partner selection",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_successful_l4_numba_conformance(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["goal"], "Goal2991")
        self.assertIn("NVIDIA L4", data["gpu"])
        self.assertEqual(data["rows"], 1_000_000)
        self.assertEqual(data["groups"], 4096)
        self.assertEqual(data["block_size"], 256)
        self.assertTrue(data["counts_match_cpu"])
        self.assertTrue(data["sums_match_cpu"])
        self.assertLess(data["max_sum_abs_error"], 1e-9)
        self.assertEqual(
            data["source_commit"],
            "ed36a366cca2ddbaf2f33bcb89393de9f24bf3d5",
        )

        handoff = data["handoff"]
        self.assertEqual(handoff["selected_partner"], "numba")
        self.assertEqual(handoff["validation"]["status"], "accept")
        self.assertEqual(handoff["runtime_observed_descriptor_count"], 2)
        self.assertTrue(handoff["all_columns_device_resident"])
        self.assertTrue(handoff["all_leases_completed"])
        self.assertFalse(handoff["torch_conversion_used"])
        self.assertFalse(handoff["torch_carrier_used"])

    def test_artifact_records_numba_cuda_target_metadata(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        toolchain = data["toolchain"]
        self.assertEqual(toolchain["python_version"], "3.12.3")
        self.assertEqual(toolchain["numba_version"], "0.65.1")
        self.assertEqual(toolchain["numpy_version"], "2.1.2")
        self.assertIn("numba_cuda/numba/cuda/__init__.py", toolchain["numba_cuda_module"])
        self.assertEqual(toolchain["numba_cuda_use_nvidia_binding"], "1")
        self.assertEqual(toolchain["numba_cuda_enable_minor_version_compatibility"], "1")

    def test_artifact_claim_boundary_authorizes_nothing(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for field, value in data["claim_boundary"].items():
            self.assertIs(
                value,
                False,
                msg=f"{field} must remain false for Goal2993 pod evidence",
            )
        for phase_name in ("count_phase_timing", "sum_phase_timing"):
            phase = data[phase_name]
            self.assertEqual(phase["validation"]["status"], "accept")
            self.assertFalse(phase["promoted_performance_path"])
            self.assertFalse(phase["same_phase_contract_as_basis"])

    def test_roadmap_indexes_goal2993_without_claim_authorization(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(roadmap, repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual(roadmap["pod_evidence_goal"], "Goal2993")
        self.assertIn("l4_pod_runtime_conformance_passed", roadmap["pod_evidence_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])
        self.assertFalse(roadmap["true_zero_copy_claim_authorized"])

    def test_readiness_exposes_review_and_next_demonstrator_actions(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=REPO_ROOT)
        self.assertIn(
            "request_external_review_for_goal2993_l4_numba_neutral_handoff",
            packet["allowed_next_actions"],
        )
        self.assertIn(
            "begin_goal2994_numba_benchmark_app_demonstrator_after_goal2993_review",
            packet["allowed_next_actions"],
        )
        self.assertEqual("accept", packet["core_validations"]["v2_6_roadmap"]["status"])


if __name__ == "__main__":
    unittest.main()
