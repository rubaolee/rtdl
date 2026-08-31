from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.json"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.md"


class Goal3003RayjoinNumbaCompactMaskL4PodTest(unittest.TestCase):
    def test_l4_artifact_records_all_rayjoin_workloads_pass(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], "Goal3003")
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["app"], "rayjoin_v2_spatial_join")
        self.assertEqual(artifact["mode"], "v2_6_numba_compact_mask_preview")
        self.assertEqual(artifact["operation"], "compact_mask_i64")
        self.assertTrue(artifact["all_workloads_match_cpu"])
        self.assertGreaterEqual(int(artifact["rows"]), 1_000_000)
        self.assertIn("NVIDIA L4", artifact["nvidia_smi"])
        self.assertRegex(artifact["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(artifact["source_dirty"], [])
        self.assertIn("numba_cuda/numba/cuda", artifact["toolchain"]["numba_cuda_module"])
        self.assertEqual(set(artifact["workloads"]), {"pip", "lsi", "overlay_seed"})
        for workload, row in artifact["workloads"].items():
            with self.subTest(workload=workload):
                self.assertEqual(row["status"], "pass")
                self.assertGreater(int(row["selected_count"]), 0)
                self.assertTrue(row["candidates_match_cpu"])
                self.assertTrue(row["indices_match_cpu"])
                self.assertTrue(row["partner_indices_match_cpu"])
                self.assertTrue(row["stable_input_order"])
                self.assertTrue(row["host_prefix_sum_used"])
                self.assertEqual(row["neutral_handoff_status"], "accept")
                self.assertEqual(row["neutral_handoff_errors"], [])
                self.assertFalse(row["uses_legacy_torch_carrier"])
                self.assertFalse(row["uses_torch_conversion"])
                self.assertFalse(row["replaces_rt_traversal"])
                self.assertFalse(row["promoted_performance_path"])

    def test_l4_artifact_keeps_claim_boundary_false(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for flag, value in artifact["claim_boundary"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)

    def test_v2_6_roadmap_indexes_goal3003_without_speedup_claim(self) -> None:
        roadmap = rt.v2_6_roadmap()

        self.assertEqual(roadmap["rayjoin_compact_mask_pod_goal"], "Goal3003")
        self.assertIn("l4_pod_conformance_passed", roadmap["rayjoin_compact_mask_pod_status"])
        self.assertIn("not_speedup_evidence", roadmap["rayjoin_compact_mask_pod_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_report_documents_all_workloads_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3003 passed",
            "pip",
            "lsi",
            "overlay_seed",
            "all workloads match CPU oracle: true",
            "does not prove RayJoin paper reproduction",
            "Prepared generic RTDL count/parity primitives remain the recommended fast path",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
