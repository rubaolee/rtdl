from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"


class Goal5107RtDbscanUci3droadContractAnalysisTest(unittest.TestCase):
    def test_author_directional_contract_explains_uci_3droad_1k_mismatch(self):
        summary = json.loads(
            (
                APP_DIR
                / "results"
                / "uci_3droad_1k_goal5107_contract_analysis.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(summary["point_count"], 1000)
        self.assertEqual(summary["core_count"], 329)
        self.assertEqual(summary["conventional_mismatch_count"], 12)
        self.assertEqual(summary["author_directional_mismatch_count"], 0)
        self.assertEqual(summary["author_noise_conventional_cluster_count"], 12)
        first = summary["first_author_noise_conventional_cluster_points"][0]
        self.assertEqual(first["point_id"], 136)
        self.assertEqual(first["higher_index_core_neighbor_count"], 0)
        self.assertGreater(first["lower_index_core_neighbor_count"], 0)
        self.assertIn("xID > primID", summary["contract_hypothesis"])

    def test_skip_teardown_patch_is_host_cleanup_only(self):
        patch = (
            APP_DIR
            / "author_patches"
            / "goal5107_authorofficial_skip_context_destroy_after_payload.patch"
        ).read_text(encoding="utf-8")
        self.assertIn("RTDL_AUTHOROFFICIAL_SKIP_CONTEXT_DESTROY", patch)
        self.assertIn("return 0;", patch)
        self.assertIn("owlContextDestroy(context)", patch)
        self.assertIn("samples/cmdline/s02-rtdbscan/hostCode.cpp", patch)
        self.assertNotIn("deviceCode.cu", patch)
        self.assertNotIn("Spheres()", patch)

    def test_clean_author_outputs_are_recorded_without_claiming_exact_gate(self):
        one_k = json.loads(
            (
                APP_DIR / "results" / "uci_3droad_1k_author_goal5107_clean.jsonl"
            ).read_text(encoding="utf-8").splitlines()[-1]
        )
        sixteen_k = json.loads(
            (
                APP_DIR / "results" / "uci_3droad_16k_author_goal5107_clean.jsonl"
            ).read_text(encoding="utf-8").splitlines()[-1]
        )
        self.assertEqual(one_k["point_count"], 1000)
        self.assertEqual(one_k["core_count"], 329)
        self.assertEqual(one_k["component_sizes"], [90, 168, 181])
        self.assertEqual(one_k["noise_count"], 561)
        self.assertEqual(sixteen_k["point_count"], 16000)
        self.assertEqual(sixteen_k["core_count"], 12625)
        self.assertEqual(len(sixteen_k["component_sizes"]), 22)


if __name__ == "__main__":
    unittest.main()
