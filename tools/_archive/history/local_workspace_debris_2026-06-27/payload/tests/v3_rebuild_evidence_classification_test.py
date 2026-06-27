import json
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = REPO_ROOT / "docs" / "rebuild" / "v3" / "v3_benchmark_app_classification_2026-06-20.json"
REPORT = REPO_ROOT / "docs" / "rebuild" / "v3" / "v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md"
ENV_GATE = REPO_ROOT / "docs" / "rebuild" / "v3" / "v3_gpu_environment_gate_2026-06-20.md"
INITIAL_ARTIFACT = REPO_ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v2_14_vs_v3_rebuild_non_numba_serious_20260620_051207"
GOAL2626_ARTIFACT = REPO_ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_current_goal2626_clean_env_20260620_055523"
GOAL2636_ARTIFACT = REPO_ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_current_goal2636_full_clean_20260620_060726"
GOAL3828_ARTIFACT = REPO_ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_current_goal3828_full_clean_20260620_060412"
ENV_ARTIFACT = REPO_ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_gpu_python_env_gate_20260620_061058"
ENV_SCRIPT_ARTIFACT = REPO_ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_gpu_python_env_gate_script_20260620_062113"


class V3RebuildEvidenceClassificationTest(unittest.TestCase):
    def load_payload(self):
        return json.loads(CLASSIFICATION.read_text(encoding="utf-8"))

    def load_summary(self, root):
        return json.loads((root / "summary.json").read_text(encoding="utf-8"))

    def test_evidence_files_exist(self):
        self.assertTrue(CLASSIFICATION.exists())
        self.assertTrue(REPORT.exists())
        self.assertTrue(ENV_GATE.exists())
        self.assertTrue(INITIAL_ARTIFACT.exists())
        self.assertTrue((INITIAL_ARTIFACT / "current_goal2626_standard" / "summary.json").exists())
        self.assertTrue((INITIAL_ARTIFACT / "v2_14_goal2626_standard" / "summary.json").exists())
        self.assertTrue((INITIAL_ARTIFACT / "current_goal2636_standard" / "summary.json").exists())
        self.assertTrue((INITIAL_ARTIFACT / "v2_14_goal2636_standard" / "summary.json").exists())
        self.assertTrue((GOAL2626_ARTIFACT / "summary.json").exists())
        self.assertTrue((GOAL2636_ARTIFACT / "summary.json").exists())
        self.assertTrue((GOAL3828_ARTIFACT / "summary.json").exists())
        self.assertTrue((ENV_ARTIFACT / "summary.json").exists())
        self.assertTrue((ENV_SCRIPT_ARTIFACT / "summary.json").exists())

    def test_clean_current_artifacts_have_expected_pass_counts(self):
        goal2626 = self.load_summary(GOAL2626_ARTIFACT)
        self.assertEqual(len(goal2626["rows"]), 22)
        self.assertEqual(Counter(row["status"] for row in goal2626["rows"]), {"ok": 22})

        goal2636 = self.load_summary(GOAL2636_ARTIFACT)
        self.assertEqual(len(goal2636["rows"]), 28)
        self.assertEqual(Counter(row["status"] for row in goal2636["rows"]), {"ok": 28})

        goal3828 = self.load_summary(GOAL3828_ARTIFACT)
        self.assertEqual(len(goal3828["rows"]), 10)
        self.assertEqual(Counter(row["status"] for row in goal3828["rows"]), {"pass": 10})
        self.assertFalse(goal3828["release_authorized"])
        self.assertFalse(goal3828["public_speedup_claim_authorized"])

    def test_gpu_environment_gate_passes(self):
        env_gate = self.load_summary(ENV_ARTIFACT)
        self.assertEqual(env_gate["status"], "pass")
        self.assertEqual(env_gate["checks"]["cupy_rawkernel"]["status"], "pass")
        self.assertEqual(env_gate["checks"]["torch_cuda"]["status"], "pass")
        self.assertEqual(env_gate["checks"]["numba_cuda_jit"]["status"], "pass")
        self.assertEqual(env_gate["packages"]["cupy-cuda12x"], "14.1.1")
        self.assertEqual(env_gate["packages"]["torch"], "2.6.0+cu124")
        self.assertEqual(env_gate["packages"]["nvidia-cuda-nvcc-cu12"], "12.4.131")

        script_gate = self.load_summary(ENV_SCRIPT_ARTIFACT)
        self.assertEqual(script_gate["tool"], "v3_gpu_python_env_gate")
        self.assertEqual(script_gate["status"], "pass")
        self.assertEqual(script_gate["checks"]["cupy_rawkernel"]["status"], "pass")
        self.assertEqual(script_gate["checks"]["torch_cuda"]["status"], "pass")
        self.assertEqual(script_gate["checks"]["numba_cuda_jit"]["status"], "pass")

    def test_release_claims_remain_blocked(self):
        payload = self.load_payload()
        self.assertEqual(payload["status"], "phoenix_boundary_classification_not_release")
        self.assertFalse(payload["v3_release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 8)
        for app in payload["apps"].values():
            self.assertFalse(app["public_claim_allowed_now"])
        self.assertNotIn("release_candidate", CLASSIFICATION.read_text(encoding="utf-8"))

    def test_all_benchmark_apps_are_classified(self):
        payload = self.load_payload()
        self.assertEqual(
            set(payload["apps"]),
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
                "contact_manifold",
            },
        )

    def test_claim_limited_routes_are_not_public_claims(self):
        apps = self.load_payload()["apps"]
        self.assertEqual(apps["spatial_rayjoin"]["classification"], "internal_evidence_not_m7")
        self.assertEqual(apps["raydb_style"]["classification"], "dependency_gated_row_scoped_m7_not_release")
        self.assertEqual(apps["rt_dbscan"]["classification"], "row_scoped_m7_qualified_not_release")
        self.assertEqual(
            apps["rt_dbscan"]["optimized_row_review"]["status"],
            "rtdbscan_component_signature_optimized_rtx_evidence_m7_approved_row_scoped",
        )
        self.assertEqual(apps["barnes_hut"]["classification"], "internal_evidence_not_m7")
        self.assertEqual(
            apps["librts_spatial_index"]["classification"],
            "row_scoped_m7_qualified_not_release",
        )
        self.assertEqual(
            apps["librts_spatial_index"]["calibrated_replacement_row"]["row"],
            "aabb_candidate_stream_all_count_only_float32_32768",
        )
        self.assertEqual(apps["rtnn"]["classification"], "boundary_lesson_not_m7")
        self.assertEqual(apps["contact_manifold"]["classification"], "boundary_lesson_not_m7")
        for app in apps.values():
            self.assertFalse(app["public_claim_allowed_now"])

    def test_triangle_counting_v3_improvement_is_recorded(self):
        triangle = self.load_payload()["apps"]["triangle_counting"]
        self.assertEqual(triangle["classification"], "row_scoped_m7_qualified_not_release")
        self.assertIn(
            "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
            triangle["representative_current_rows"],
        )


if __name__ == "__main__":
    unittest.main()
