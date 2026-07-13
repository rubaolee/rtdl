from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_DIR / "results"
AUTHOR = RESULTS / "xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json"
RTDL = RESULTS / "xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json"
SCALED = RESULTS / "xhd_goal5265_thai_statuette_scaled_1e-3_candidate_summary_2026-07-09.json"
PAPER_LOG_HD = 0.21912434697151184


class Goal5265XhdHdExecGraphicsThaiHappyPodArtifactTest(unittest.TestCase):
    def _load(self, path: Path) -> dict[str, object]:
        if not path.exists():
            self.skipTest(f"missing artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_scaled_thai_candidate_matches_paper_log_scale_and_keeps_boundary(self) -> None:
        summary = self._load(SCALED)

        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.scaled_ply_candidate.v1")
        self.assertEqual(summary["goal"], "Goal5265")
        self.assertEqual(summary["vertex_count"], 4_999_996)
        self.assertEqual(summary["scale"], 0.001)
        self.assertEqual(summary["output_format"], "binary_big_endian 1.0")
        self.assertFalse(summary["faces_preserved"])
        self.assertAlmostEqual(summary["coordinate_extents_after_scale"][0], 0.2352239456176758)
        self.assertAlmostEqual(summary["coordinate_extents_after_scale"][1], 0.39604121398925785)
        self.assertAlmostEqual(summary["coordinate_extents_after_scale"][2], 0.20316127014160157)

        claim = summary["claim_boundary"]
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])
        self.assertFalse(claim["full_paper_reproduction_claimed"])
        self.assertFalse(claim["paper_figure_reproduction_claimed"])
        self.assertFalse(claim["performance_ratio_claimed"])

    def test_author_and_rtdl_thai_happy_artifacts_match(self) -> None:
        author = self._load(AUTHOR)
        rtdl = self._load(RTDL)

        self.assertAlmostEqual(author["HDResult"], 0.21912431716918945)
        self.assertAlmostEqual(rtdl["HDResult"], 0.2191243235042005)
        self.assertLessEqual(abs(float(rtdl["HDResult"]) - float(author["HDResult"])), 1e-6)
        self.assertLessEqual(abs(float(rtdl["HDResult"]) - PAPER_LOG_HD), 1e-6)
        self.assertEqual(author["Input"]["Files"][0]["NumPoints"], 4_999_996)
        self.assertEqual(author["Input"]["Files"][1]["NumPoints"], 543_652)
        self.assertEqual(rtdl["RTDL"]["point_count_a"], 4_999_996)
        self.assertEqual(rtdl["RTDL"]["point_count_b"], 543_652)
        self.assertEqual(rtdl["RTDL"]["route_label"], "cell-mbr-exact-witness")
        self.assertEqual(rtdl["RTDL"]["reference_preprocessing"], ["translate_each_input_to_min_bound"])
        self.assertTrue(rtdl["RTDL"]["route"]["per_source_witness_exact"])
        self.assertGreater(rtdl["Running"]["AvgTime"], 0.0)
        self.assertGreater(author["Running"]["AvgTime"], 0.0)

    def test_thai_happy_artifact_keeps_claim_boundary_false(self) -> None:
        payload = self._load(RTDL)

        claim = payload["RTDL"]["claim_boundary"]
        self.assertFalse(claim["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(claim["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(claim["performance_claim_authorized"])
        self.assertFalse(claim["author_performance_parity_claimed"])
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])

    def test_docs_record_thai_happy_without_promoting_to_full_paper(self) -> None:
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
        stanford_readme = (APP_DIR / "data" / "external" / "stanford" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("ThaiStatuette -> HappyBuddha", readme)
        self.assertIn("xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("thai_statuette_scaled_1e-3.ply", readme)
        self.assertIn("does not prove exact paper byte-input identity", readme)

        self.assertIn("ThaiStatuette", stanford_readme)
        self.assertIn("xyzrgb_statuette.ply.gz", stanford_readme)
        self.assertIn("thai_statuette_scaled_1e-3.ply", stanford_readme)

        evidence = {item["path"]: item for item in manifest["evidence"]["result_artifacts"]}
        scaled = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_statuette_scaled_1e-3_candidate_summary_2026-07-09.json"
        ]
        author = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json"
        ]
        rtdl = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json"
        ]
        self.assertTrue(scaled["matched"] is None)
        self.assertTrue(author["matched"])
        self.assertTrue(rtdl["matched"])
        self.assertIn("not exact paper byte-input identity", rtdl["note"])
        self.assertIn("not full paper reproduction", rtdl["note"])


if __name__ == "__main__":
    unittest.main()
