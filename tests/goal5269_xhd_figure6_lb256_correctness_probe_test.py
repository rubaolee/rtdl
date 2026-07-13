from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_DIR / "results"
ARTIFACT = RESULTS / "xhd_goal5269_figure6_lb256_correctness_probe_2026-07-09.json"


class Goal5269XhdFigure6Lb256CorrectnessProbeTest(unittest.TestCase):
    def _load(self) -> dict[str, object]:
        if not ARTIFACT.exists():
            self.skipTest(f"missing artifact: {ARTIFACT}")
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_goal5269_keeps_figure6_unreproduced(self) -> None:
        payload = self._load()

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.figure6_lb256_correctness_probe.v1",
        )
        self.assertEqual(
            payload["status"],
            "lb256_failure_classified_as_level_b_candidate_provenance_gap__figure6_still_not_reproduced",
        )
        claim = payload["claim_boundary"]
        self.assertFalse(claim["figure6_reproduced"])
        self.assertFalse(claim["exact_paper_dataset_identity_claimed"])
        self.assertFalse(claim["author_rt_core_equivalence_claimed"])
        self.assertFalse(claim["performance_ratio_claimed"])
        self.assertFalse(claim["lb2048_substitute_authorized_as_figure6"])

    def test_author_exact_paths_are_not_available_on_current_pod(self) -> None:
        payload = self._load()
        target = payload["target"]

        self.assertEqual(target["figure"], "Figure 6")
        self.assertEqual(target["workload"], "Dragon -> AsianDragon")
        self.assertIn("/local/storage/shared/HDDatasets/graphics/dragon.ply", target["script_exact_paths"])
        self.assertFalse(target["script_exact_paths_available_on_current_pod"])

    def test_author_log_and_level_b_candidate_have_different_mbrs(self) -> None:
        payload = self._load()

        log = payload["author_paper_branch_log"]
        candidate = payload["current_level_b_candidate_lb256"]
        self.assertEqual(log["input_num_points"], candidate["input_num_points"])
        self.assertEqual(log["lb"], 256)
        self.assertEqual(candidate["lb"], 256)
        self.assertNotEqual(log["input_mbr_a"], candidate["input_mbr_a"])
        self.assertNotEqual(log["input_mbr_b"], candidate["input_mbr_b"])
        self.assertGreater(max(payload["mbr_differences"]["a_upper_abs_diffs"]), 0.0)
        self.assertGreater(max(payload["mbr_differences"]["b_upper_abs_diffs"]), 0.0)

    def test_lb_threshold_scan_classifies_unsafe_default_and_safe_substitute(self) -> None:
        payload = self._load()
        findings = payload["derived_findings"]

        self.assertTrue(findings["lb_0_is_correct"])
        self.assertTrue(findings["lb_32_to_1152_wrong_same_hd"])
        self.assertTrue(findings["lb_1280_and_above_in_refined_scan_correct"])
        self.assertTrue(findings["lb_1024_check_true_aborts"])
        self.assertTrue(findings["lb_2048_check_true_passes"])

        rows = {row["lb"]: row for row in payload["lb_threshold_scan"]["rows"]}
        self.assertEqual(rows[0]["hd_result"], rows[2048]["hd_result"])
        self.assertNotEqual(rows[0]["hd_result"], rows[256]["hd_result"])

        refine_rows = {row["lb"]: row for row in payload["lb_threshold_scan"]["refine_rows"]}
        self.assertNotEqual(refine_rows[1152]["hd_result"], rows[0]["hd_result"])
        self.assertEqual(refine_rows[1280]["hd_result"], rows[0]["hd_result"])

        check1024 = next(row for row in payload["lb_threshold_scan"]["refine_rows"] if row.get("check") and row["lb"] == 1024)
        check2048 = next(row for row in payload["lb_threshold_scan"]["refine_rows"] if row.get("check") and row["lb"] == 2048)
        self.assertEqual(check1024["returncode"], -6)
        self.assertEqual(check2048["check_obj"]["Pass"], True)


if __name__ == "__main__":
    unittest.main()
