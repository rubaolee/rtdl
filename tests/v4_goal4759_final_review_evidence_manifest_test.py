from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_JSON = ROOT / "future" / "v4" / "evidence" / "v4_goal4759_final_review_evidence_manifest_2026-06-26.json"
MANIFEST_MD = ROOT / "future" / "v4" / "v4_goal4759_final_review_evidence_manifest_2026-06-26.md"
SCRIPT = ROOT / "scripts" / "v4_goal4759_final_review_evidence_manifest.py"


class V4Goal4759FinalReviewEvidenceManifestTest(unittest.TestCase):
    def test_manifest_exists_and_indexes_final_review_artifacts(self) -> None:
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(MANIFEST_JSON.exists())
        self.assertTrue(MANIFEST_MD.exists())
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))

        self.assertEqual("ready_for_external_review_not_release_authorization", manifest["status"])
        self.assertFalse(manifest["release_authorized"])
        self.assertFalse(manifest["public_tag_authorized"])
        self.assertTrue(manifest["external_review_debt_open"])
        self.assertEqual(27, manifest["artifact_count"])
        self.assertEqual([], manifest["missing_artifacts"])
        self.assertEqual([], manifest["empty_artifacts"])

        ids = {artifact["id"] for artifact in manifest["artifacts"]}
        for artifact_id in (
            "goal4757_release_packet",
            "goal4757_call_for_review",
            "goal4757_forward_message",
            "goal4757_external_review_debt",
            "goal4758_completion_audit",
            "goal4756_matrix_analysis_json",
            "goal4758_full_v4_gate_log",
            "goal4759_full_v4_gate_log",
            "goal4758_wheel",
            "goal4758_wheel_install_smoke_summary",
            "goal4769_barnes_hut_author_phase_report",
            "goal4769_barnes_hut_author_phase_stdout",
            "goal4770_barnes_hut_delta_json",
            "goal4770_barnes_hut_delta_md",
            "goal4770_barnes_hut_delta_review_debt",
            "readme",
            "current_v4_status",
            "app_level_benchmark_summary",
            "goal4757_machine_gate",
            "goal4758_machine_gate",
        ):
            self.assertIn(artifact_id, ids)

    def test_manifest_preserves_matrix_and_installed_wheel_facts(self) -> None:
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        matrix = manifest["matrix_summary"]
        smoke = manifest["wheel_install_smoke"]

        self.assertEqual(10, matrix["app_count"])
        self.assertTrue(matrix["all_rows_have_v2_v3_v4"])
        self.assertEqual([], matrix["regression_apps"])
        self.assertEqual(["triangle_counting", "barnes_hut"], matrix["material_candidate_apps"])
        self.assertEqual("passed", smoke["status"])
        self.assertEqual(10, smoke["matrix_apps"])
        self.assertEqual(30, smoke["matrix_rows"])
        self.assertEqual(["cupy", "numba", "rtdl_native", "torch"], smoke["measured_partners"])
        self.assertEqual("certified_partner_measured_ready", smoke["cupy_grouped_vector_sum_status"])
        self.assertEqual("tier2_measured_ready", smoke["numba_component_union_status"])
        self.assertFalse(smoke["release_authorized"])
        self.assertFalse(smoke["public_tag_authorized"])

    def test_manifest_artifact_hashes_are_populated(self) -> None:
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        for artifact in manifest["artifacts"]:
            with self.subTest(artifact=artifact["id"]):
                self.assertTrue(artifact["exists"])
                self.assertGreater(artifact["size_bytes"], 0)
                self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
