from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5501"


class Goal5501MismatchDiagnosticResultTest(unittest.TestCase):
    def test_mismatch_diagnostic_narrows_the_execution_contract(self) -> None:
        payload = json.loads(
            (RESULTS / "mismatch_diagnostic.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["status"], "diagnostic_completed")
        self.assertEqual(len(payload["cases"]), 2)
        self.assertFalse(payload["claim_boundary"]["root_cause_declared"])
        self.assertFalse(payload["claim_boundary"]["full_input_equivalence_claimed"])

        by_name = {case["case_id"].split("_select", 1)[0]: case for case in payload["cases"]}
        parks = by_name["parks_Europe"]
        lakes = by_name["lakes_bz2"]
        self.assertTrue(parks["diagnostic_matches"]["rtdl_equals_cpu_float32"])
        self.assertTrue(lakes["diagnostic_matches"]["rtdl_equals_cpu_float32"])
        self.assertFalse(parks["diagnostic_matches"]["rtdl_equals_author"])
        self.assertTrue(lakes["diagnostic_matches"]["rtdl_equals_author"])
        self.assertEqual(parks["author"]["result_count"], 13_695_048)
        self.assertEqual(parks["rtdl_count"], 13_695_053)
        self.assertEqual(lakes["author"]["result_count"], 12_596_850)
        self.assertEqual(lakes["rtdl_count"], 12_596_850)

    def test_parks_bz2_capacity_probe_is_separate_from_full_oom(self) -> None:
        payload = json.loads(
            (RESULTS / "parks_bz2_capacity.json").read_text(encoding="utf-8")
        )
        case = payload["cases"][0]
        self.assertEqual(case["sample_geometry_count"], 100_000)
        self.assertTrue(case["diagnostic_matches"]["rtdl_equals_cpu_float32"])
        self.assertFalse(case["diagnostic_matches"]["rtdl_equals_author"])
        self.assertEqual(case["author"]["result_count"], 11_815_394)
        self.assertEqual(case["rtdl_count"], 11_815_398)
        self.assertFalse(payload["claim_boundary"]["parks_bz2_oom_resolved"])


if __name__ == "__main__":
    unittest.main()
