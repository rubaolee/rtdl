from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.json"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.md"


class Goal3007NumbaGroupedArgReducerL4PodTest(unittest.TestCase):
    def test_artifact_records_clean_l4_conformance(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["goal"], "Goal3007")
        self.assertEqual(data["selected_partner"], "numba")
        self.assertEqual(data["operation_family"], "numba_grouped_argmin_argmax_f64")
        self.assertEqual(data["source_dirty"], [])
        self.assertIn("a8933b1b", data["source_commit"])
        self.assertTrue(data["all_cases_match_cpu_reference"])
        self.assertEqual(data["toolchain"]["gpu_name"], "NVIDIA L4")
        self.assertIn("numba_cuda/numba/cuda", data["toolchain"]["numba_cuda_module"])
        self.assertFalse(data["uses_legacy_torch_carrier"])
        self.assertFalse(data["uses_torch_conversion"])
        self.assertFalse(data["release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["numba_speedup_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["whole_app_speedup_claim_authorized"])
        self.assertFalse(data["true_zero_copy_claim_authorized"])
        self.assertFalse(data["automatic_partner_selection_allowed"])
        self.assertFalse(data["app_specific_native_engine_logic_authorized"])

    def test_artifact_cases_cover_ties_and_large_stream(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["case"]: row for row in data["case_results"]}

        self.assertEqual(set(rows), {"tie_fixture", "large_stream"})
        self.assertEqual(rows["large_stream"]["row_count"], 1_000_000)
        self.assertEqual(rows["large_stream"]["group_count"], 4096)
        for row in rows.values():
            self.assertTrue(row["argmin_all_match"])
            self.assertTrue(row["argmax_all_match"])
            self.assertEqual(row["argmin_tie_break"], "lowest_score_then_lowest_item_id")
            self.assertEqual(row["argmax_tie_break"], "highest_score_then_lowest_item_id")
            self.assertTrue(all(row["argmin_matches"].values()))
            self.assertTrue(all(row["argmax_matches"].values()))

    def test_report_and_roadmap_keep_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Status: pass",
            "Source dirty | `[]`",
            "host-observed present-group compaction",
            "does not authorize",
            "v2.6 release",
            "Numba speedup wording",
            "true-zero-copy wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["numba_grouped_arg_goal"], "Goal3006")
        self.assertEqual(roadmap["numba_grouped_arg_pod_goal"], "Goal3007")
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual(validation["errors"], ())


if __name__ == "__main__":
    unittest.main()
