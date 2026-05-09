import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1627_v1_6_x_optix_collect_k_defer_merge_sync_diagnostic_2026-05-09.md"
NODEFER_JSON = ROOT / "docs" / "reports" / "goal1627_defer_merge_sync_candidate_repeats5_nodefer.json"
DEFER_JSON = ROOT / "docs" / "reports" / "goal1627_defer_merge_sync_candidate_repeats5_defer.json"


class Goal1627OptixCollectKDeferMergeSyncDiagnosticTest(unittest.TestCase):
    def test_diagnostic_gate_is_opt_in_and_guarded(self) -> None:
        text = API_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC", text)
        self.assertIn("collect_k_defer_merge_sync_diagnostic()", text)
        self.assertIn("const bool can_defer_merge_sync", text)
        self.assertIn("&& use_batched_compact_level", text)
        self.assertIn("&& current_rows.size() != 2", text)
        self.assertIn("&& use_device_prefix_compact", text)
        self.assertIn("&& use_device_level_counts", text)
        self.assertIn("if (!can_defer_merge_sync)", text)

    def test_report_records_internal_only_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("defer_merge_sync_diagnostic_candidate_recorded", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1", text)
        self.assertIn("The default path is unchanged", text)
        self.assertIn("not authorize public speedup wording", text)
        self.assertIn("stable\n`COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)

    def test_a4500_repeats5_artifacts_preserve_parity_and_show_internal_delta(self) -> None:
        nodefer = json.loads(NODEFER_JSON.read_text(encoding="utf-8"))
        defer = json.loads(DEFER_JSON.read_text(encoding="utf-8"))

        self.assertTrue(nodefer["accepted_goal1506_evidence"])
        self.assertTrue(defer["accepted_goal1506_evidence"])
        defer_cases = {case["candidate_count"]: case for case in defer["cases"]}
        for nodefer_case in nodefer["cases"]:
            count = nodefer_case["candidate_count"]
            defer_case = defer_cases[count]
            self.assertTrue(nodefer_case["same_candidate_rows"])
            self.assertTrue(defer_case["same_candidate_rows"])
            nodefer_stage = nodefer_case["stage_profile"]["stage_median_ms"]
            defer_stage = defer_case["stage_profile"]["stage_median_ms"]
            self.assertLess(defer_stage["total_ms"], nodefer_stage["total_ms"])
            self.assertLess(defer_stage["merge_sync_ms"], nodefer_stage["merge_sync_ms"])


if __name__ == "__main__":
    unittest.main()
