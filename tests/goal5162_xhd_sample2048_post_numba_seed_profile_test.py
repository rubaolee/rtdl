from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5162XhdSample2048PostNumbaSeedProfileTest(unittest.TestCase):
    def test_seeded_performance_matrix_supports_sample2048(self) -> None:
        script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_seeded_performance_matrix.py"
        )
        text = script.read_text(encoding="utf-8")
        self.assertIn('"sample2048"', text)
        self.assertIn("stanford_dragon_res4_sample2048.ply", text)
        self.assertIn("stanford_happy_res4_sample2048.ply", text)

    def test_post_numba_seed_sample2048_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample2048_post_numba_seed_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5162 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        cases = {case["case"]: case for case in payload["cases"]}
        self.assertIn("sample2048", cases)
        sample2048 = cases["sample2048"]
        self.assertTrue(sample2048["matched"])
        self.assertEqual(sample2048["point_count_a"], 2048)
        self.assertEqual(sample2048["point_count_b"], 2048)
        self.assertEqual(sample2048["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(sample2048["rtdl"]["rtdl_matches_exact_reference"])
        self.assertEqual(
            sample2048["rtdl"]["directed_a_to_b"]["initial_cell_mbr_selection"],
            "numba_loop_min_distance_then_cell_id",
        )
        self.assertGreater(sample2048["rtdl"]["route_sec_median"], 0.0)


if __name__ == "__main__":
    unittest.main()
