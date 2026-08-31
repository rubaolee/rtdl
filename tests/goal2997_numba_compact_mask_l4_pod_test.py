from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2997_numba_compact_mask_l4_pod_2026-06-01.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal2997_numba_compact_mask_l4_pod_2026-06-01.json"


class Goal2997NumbaCompactMaskL4PodTest(unittest.TestCase):
    def test_report_records_compact_mask_evidence_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Status: passed on NVIDIA L4 pod",
            "compact_mask_i64",
            "RayJoin-style",
            "triangle-counting-style",
            "stable input order: true",
            "host prefix sum used: true",
            "does not authorize",
            "future performance pass",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_stable_compact_mask_pass(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal2997")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["operation"], "compact_mask_i64")
        self.assertEqual(data["rows"], 1_000_000)
        self.assertEqual(data["selected_count"], 193_279)
        self.assertIn("NVIDIA L4", data["gpu"])
        self.assertEqual(data["source_commit"], "afca574838d2519def88c9bed45d999a4e0b153b")
        self.assertTrue(data["values_match_cpu"])
        self.assertTrue(data["indices_match_cpu"])
        self.assertTrue(data["partner_indices_match_cpu"])
        self.assertTrue(data["stable_input_order"])
        self.assertTrue(data["host_prefix_sum_used"])
        self.assertEqual(data["toolchain"]["numba_version"], "0.65.1")
        self.assertIn("numba_cuda/numba/cuda/__init__.py", data["toolchain"]["numba_cuda_module"])

    def test_artifact_claim_boundary_authorizes_nothing(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for field, value in data["claim_boundary"].items():
            self.assertIs(value, False, msg=f"{field} must remain false")

    def test_roadmap_indexes_compact_mask_as_second_numba_primitive_family(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(roadmap, repo_root=REPO_ROOT)
        self.assertEqual(validation["status"], "accept", validation["errors"])
        self.assertEqual(roadmap["compact_mask_goal"], "Goal2997")
        self.assertIn("compact_mask_i64", roadmap["compact_mask_status"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])

        packet = rt.v2_5_internal_readiness_packet(repo_root=REPO_ROOT)
        self.assertIn(
            "request_external_review_for_goal2997_numba_compact_mask",
            packet["allowed_next_actions"],
        )


if __name__ == "__main__":
    unittest.main()
