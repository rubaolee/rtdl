from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
FAST = RESULTS / "xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json"
EXACT = RESULTS / "xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json"
AUTHOR_HD = 0.12572988867759705


class Goal5263XhdHdExecGraphicsDragonHappyPodArtifactTest(unittest.TestCase):
    def _load(self, path: Path) -> dict[str, object]:
        if not path.exists():
            self.skipTest(f"missing POD artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_fast_scalar_graphics_hd_exec_artifact_matches_author_rerun(self) -> None:
        payload = self._load(FAST)

        self.assertEqual(payload["RTDL"]["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1")
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-fast-scalar")
        self.assertAlmostEqual(payload["HDResult"], 0.12572988629271128)
        self.assertLessEqual(abs(float(payload["HDResult"]) - AUTHOR_HD), 1e-6)
        self.assertEqual(payload["RTDL"]["point_count_a"], 437645)
        self.assertEqual(payload["RTDL"]["point_count_b"], 543652)
        self.assertEqual(payload["RTDL"]["reference_preprocessing"], ["translate_each_input_to_min_bound"])
        self.assertFalse(payload["RTDL"]["route"]["per_source_witness_exact"])
        self.assertGreater(payload["Running"]["AvgTime"], 0.0)
        self.assertIn("RTDL route wall time", payload["Running"]["TimeSemantics"])

        claim = payload["RTDL"]["claim_boundary"]
        self.assertFalse(claim["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(claim["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(claim["performance_claim_authorized"])
        self.assertFalse(claim["author_performance_parity_claimed"])
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])

    def test_exact_witness_graphics_hd_exec_artifact_matches_author_rerun(self) -> None:
        payload = self._load(EXACT)

        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-exact-witness")
        self.assertAlmostEqual(payload["HDResult"], 0.12572988629271128)
        self.assertLessEqual(abs(float(payload["HDResult"]) - AUTHOR_HD), 1e-6)
        self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])
        self.assertEqual(payload["RTDL"]["point_count_a"], 437645)
        self.assertEqual(payload["RTDL"]["point_count_b"], 543652)
        self.assertEqual(payload["RTDL"]["reference_preprocessing"], ["translate_each_input_to_min_bound"])
        self.assertGreater(payload["Running"]["AvgTime"], 0.0)
        self.assertIn("not author internal Running.AvgTime parity", payload["Running"]["TimeSemantics"])

    def test_fast_and_exact_routes_share_same_hdresult_but_different_witness_contracts(self) -> None:
        fast = self._load(FAST)
        exact = self._load(EXACT)

        self.assertAlmostEqual(fast["HDResult"], exact["HDResult"])
        self.assertFalse(fast["RTDL"]["route"]["per_source_witness_exact"])
        self.assertTrue(exact["RTDL"]["route"]["per_source_witness_exact"])
        self.assertIn("witness_may_be_approximate", fast["RTDL"]["route"]["witness_contract"])
        self.assertIn("per_source_witness_exact", exact["RTDL"]["route"]["witness_contract"])

    def test_readme_and_manifest_record_graphics_entrypoint_evidence_without_overclaim(self) -> None:
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))

        self.assertIn("Dragon -> HappyBuddha", readme)
        self.assertIn("xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json", readme)
        self.assertIn("xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("per_source_witness_exact = true", readme)
        self.assertIn("does not prove exact paper byte-input identity", readme)

        evidence = {item["path"]: item for item in manifest["evidence"]["result_artifacts"]}
        fast = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json"
        ]
        exact = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json"
        ]
        self.assertTrue(fast["matched"])
        self.assertTrue(exact["matched"])
        self.assertIn("per_source_witness_exact=false", fast["note"])
        self.assertIn("per_source_witness_exact=true", exact["note"])
        self.assertIn("not exact paper byte-input identity", fast["note"])
        self.assertIn("full paper reproduction", exact["note"])


if __name__ == "__main__":
    unittest.main()
