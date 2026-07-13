from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_DIR / "results"
AUTHOR = RESULTS / "xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json"
EXACT = RESULTS / "xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json"
AUTHOR_HD = 0.28763842582702637
PAPER_LOG_HD = 0.28763845562934875


class Goal5266XhdHdExecGraphicsThaiAsianPodArtifactTest(unittest.TestCase):
    def _load(self, path: Path) -> dict[str, object]:
        if not path.exists():
            self.skipTest(f"missing POD artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_author_thai_asian_artifact_matches_paper_log_scale(self) -> None:
        payload = self._load(AUTHOR)

        self.assertAlmostEqual(payload["HDResult"], AUTHOR_HD)
        self.assertLessEqual(abs(float(payload["HDResult"]) - PAPER_LOG_HD), 1e-6)
        self.assertEqual(payload["Input"]["Files"][0]["NumPoints"], 4_999_996)
        self.assertEqual(payload["Input"]["Files"][1]["NumPoints"], 3_609_600)
        self.assertGreater(payload["Running"]["AvgTime"], 0.0)

    def test_exact_witness_thai_asian_artifact_matches_author_rerun(self) -> None:
        payload = self._load(EXACT)

        self.assertEqual(payload["RTDL"]["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1")
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-exact-witness")
        self.assertAlmostEqual(payload["HDResult"], 0.2876384148709406)
        self.assertLessEqual(abs(float(payload["HDResult"]) - AUTHOR_HD), 1e-6)
        self.assertLessEqual(abs(float(payload["HDResult"]) - PAPER_LOG_HD), 1e-6)
        self.assertEqual(payload["RTDL"]["point_count_a"], 4_999_996)
        self.assertEqual(payload["RTDL"]["point_count_b"], 3_609_600)
        self.assertEqual(payload["RTDL"]["reference_preprocessing"], ["translate_each_input_to_min_bound"])
        self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])
        self.assertGreater(payload["Running"]["AvgTime"], 0.0)
        self.assertIn("not author internal Running.AvgTime parity", payload["Running"]["TimeSemantics"])

    def test_thai_asian_artifact_keeps_claim_boundary_false(self) -> None:
        payload = self._load(EXACT)

        claim = payload["RTDL"]["claim_boundary"]
        self.assertFalse(claim["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(claim["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(claim["performance_claim_authorized"])
        self.assertFalse(claim["author_performance_parity_claimed"])
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])

    def test_readme_and_manifest_record_thai_asian_without_overclaim(self) -> None:
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))

        self.assertIn("ThaiStatuette -> AsianDragon", readme)
        self.assertIn("xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json", readme)
        self.assertIn("xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("per_source_witness_exact = true", readme)
        self.assertIn("not exact paper byte-input identity", readme)

        evidence = {item["path"]: item for item in manifest["evidence"]["result_artifacts"]}
        author = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json"
        ]
        exact = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json"
        ]
        self.assertTrue(author["matched"])
        self.assertTrue(exact["matched"])
        self.assertIn("ThaiStatuette scaled 1e-3 -> AsianDragon", author["note"])
        self.assertIn("per_source_witness_exact=true", exact["note"])
        self.assertIn("not exact paper byte-input identity", exact["note"])
        self.assertIn("not full paper reproduction", exact["note"])


if __name__ == "__main__":
    unittest.main()
