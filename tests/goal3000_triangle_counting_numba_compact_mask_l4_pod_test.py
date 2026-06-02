from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.json"
)
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.md"
)


class Goal3000TriangleCountingNumbaCompactMaskL4PodTest(unittest.TestCase):
    def test_l4_artifact_records_app_level_numba_compaction_pass(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], "Goal3000")
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["app"], "triangle_counting")
        self.assertEqual(artifact["mode"], "v2_6_numba_compact_mask_preview")
        self.assertEqual(artifact["operation"], "compact_mask_i64")
        self.assertEqual(artifact["selected_partner"], "numba")
        self.assertGreaterEqual(int(artifact["rows"]), 1_000_000)
        self.assertGreater(int(artifact["selected_count"]), 0)
        self.assertTrue(artifact["candidates_match_cpu"])
        self.assertTrue(artifact["indices_match_cpu"])
        self.assertTrue(artifact["partner_indices_match_cpu"])
        self.assertTrue(artifact["stable_input_order"])
        self.assertTrue(artifact["host_prefix_sum_used"])
        self.assertEqual(artifact["neutral_handoff_status"], "accept")
        self.assertEqual(artifact["neutral_handoff_errors"], [])
        self.assertFalse(artifact["uses_legacy_torch_carrier"])
        self.assertFalse(artifact["uses_torch_conversion"])
        self.assertFalse(artifact["replaces_rt_traversal"])
        self.assertFalse(artifact["promoted_performance_path"])
        self.assertIn("NVIDIA L4", artifact["nvidia_smi"])
        self.assertRegex(artifact["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(artifact["source_dirty"], [])
        self.assertIn("numba_cuda/numba/cuda", artifact["toolchain"]["numba_cuda_module"])

    def test_l4_artifact_keeps_claim_boundary_false(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for flag, value in artifact["claim_boundary"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)

    def test_v2_6_roadmap_indexes_goal3000_without_release_authorization(self) -> None:
        roadmap = rt.v2_6_roadmap()

        self.assertEqual(roadmap["triangle_compact_mask_pod_goal"], "Goal3000")
        self.assertIn("l4_pod_conformance_passed", roadmap["triangle_compact_mask_pod_status"])
        self.assertIn("not_speedup_evidence", roadmap["triangle_compact_mask_pod_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])

    def test_report_documents_toolchain_fix_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3000 passed",
            "NVIDIA L4",
            "source dirty status: empty",
            "numba_cuda/numba/cuda",
            "_numba_cuda_redirector",
            "does not authorize",
            "recommended fast scalar path",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
