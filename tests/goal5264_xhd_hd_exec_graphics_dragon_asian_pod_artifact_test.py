from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_DIR / "results"
EXACT = RESULTS / "xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json"
AUTHOR_HD = 0.06536787003278732
PAPER_LOG_HD = 0.06536811590194702


class Goal5264XhdHdExecGraphicsDragonAsianPodArtifactTest(unittest.TestCase):
    def _load(self, path: Path) -> dict[str, object]:
        if not path.exists():
            self.skipTest(f"missing POD artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_exact_witness_graphics_dragon_asian_artifact_matches_author_rerun(self) -> None:
        payload = self._load(EXACT)

        self.assertEqual(payload["RTDL"]["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1")
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-exact-witness")
        self.assertAlmostEqual(payload["HDResult"], 0.06536787240753439)
        self.assertLessEqual(abs(float(payload["HDResult"]) - AUTHOR_HD), 1e-6)
        self.assertGreater(abs(float(payload["HDResult"]) - PAPER_LOG_HD), 1e-7)
        self.assertEqual(payload["RTDL"]["point_count_a"], 437645)
        self.assertEqual(payload["RTDL"]["point_count_b"], 3609600)
        self.assertEqual(payload["RTDL"]["reference_preprocessing"], ["translate_each_input_to_min_bound"])
        self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])
        self.assertGreater(payload["Running"]["AvgTime"], 0.0)
        self.assertIn("not author internal Running.AvgTime parity", payload["Running"]["TimeSemantics"])

    def test_dragon_asian_artifact_keeps_claim_boundary_false(self) -> None:
        payload = self._load(EXACT)

        claim = payload["RTDL"]["claim_boundary"]
        self.assertFalse(claim["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(claim["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(claim["performance_claim_authorized"])
        self.assertFalse(claim["author_performance_parity_claimed"])
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])

    def test_readme_and_manifest_record_dragon_asian_without_promoting_to_exact_paper(self) -> None:
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))

        self.assertIn("Dragon -> AsianDragon", readme)
        self.assertIn("xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("per_source_witness_exact = true", readme)
        self.assertIn("paper log", readme)
        self.assertIn("does not prove exact paper byte-input identity", readme)

        evidence = {item["path"]: item for item in manifest["evidence"]["result_artifacts"]}
        exact = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json"
        ]
        self.assertTrue(exact["matched"])
        self.assertIn("per_source_witness_exact=true", exact["note"])
        self.assertIn("paper-log drift", exact["note"])
        self.assertIn("not exact paper byte-input identity", exact["note"])
        self.assertIn("not full paper reproduction", exact["note"])


if __name__ == "__main__":
    unittest.main()
