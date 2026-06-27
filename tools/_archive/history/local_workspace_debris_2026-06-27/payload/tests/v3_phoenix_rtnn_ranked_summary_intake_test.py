import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_ranked_summary_intake.py"
EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_ranked_summary_20260620"
    / "rtnn_ranked_summary_intake_summary.json"
)
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md"


class V3PhoenixRtnnRankedSummaryIntakeTest(unittest.TestCase):
    def load(self):
        return json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_intake_passes_as_internal_candidate_not_m7(self):
        payload = self.load()
        self.assertEqual(payload["status"], "internal_rtnn_ranked_summary_candidate_not_m7")
        self.assertEqual(payload["generic_capability"], "ranked_summary")
        self.assertEqual(
            payload["generic_capability_status"],
            "distribution_specific_candidate_wall_regression",
        )
        expected_blockers = {
            "wall_timing_optix_slower_than_embree_for_all_three_distributions",
            "distribution_specific_not_universal_rtnn_acceleration",
            "paper_equivalent_rtnn_row_false",
            "summary_rows_materialized",
            "no_author_code_or_external_ann_baseline_comparison",
            "prepared_cuda_graph_replay_false",
            "no_multi_run_variance_evidence",
            "public_row_level_external_review_not_done",
        }
        self.assertTrue(expected_blockers.issubset(set(payload["m7_blockers"])))
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertEqual(payload["claim_boundary"]["m7_qualified_release_rows"], 0)
        comparison = payload["comparison"]
        self.assertTrue(comparison["intake_pass"])
        self.assertEqual(comparison["errors"], [])
        self.assertEqual(comparison["row_count"], 6)
        self.assertEqual(comparison["group_count"], 3)
        self.assertTrue(comparison["all_rows_ok"])
        self.assertTrue(comparison["all_same_contract"])
        self.assertTrue(comparison["all_same_metric_source"])
        self.assertTrue(comparison["all_aggregate_summaries_match"])
        self.assertTrue(comparison["all_claim_flags_blocked"])
        self.assertTrue(comparison["all_hot_optix_faster_than_embree"])
        self.assertTrue(comparison["all_wall_optix_slower_than_embree"])
        self.assertFalse(comparison["m7_qualified"])

    def test_pairs_show_hot_signal_and_wall_blocker(self):
        payload = self.load()
        pairs = {pair["distribution"]: pair for pair in payload["pairs"]}
        self.assertGreater(pairs["clustered"]["hot_optix_speedup_vs_embree"], 3.0)
        self.assertGreater(pairs["shell"]["hot_optix_speedup_vs_embree"], 1.0)
        self.assertGreater(pairs["uniform"]["hot_optix_speedup_vs_embree"], 1.0)
        for pair in pairs.values():
            self.assertEqual(pair["claim_status"], "internal_candidate_not_m7")
            self.assertTrue(pair["same_metric_source"])
            self.assertTrue(pair["same_contract"])
            self.assertTrue(pair["aggregate_summary_matches"])
            self.assertLess(pair["wall_optix_speedup_vs_embree"], 1.0)
            self.assertLess(pair["wall_optix_speedup_vs_embree"], pair["hot_optix_speedup_vs_embree"])

    def test_rows_block_public_claims_and_preserve_summary_boundaries(self):
        payload = self.load()
        for row in payload["rows"]:
            self.assertEqual(row["query_count"], 65536)
            self.assertEqual(row["row_count"], 65536)
            self.assertEqual(row["k_max"], 50)
            self.assertTrue(row["claim_flags_blocked"])
            self.assertEqual(row["missing_claim_boundary_flags"], [])
            self.assertTrue(row["materializes_summary_rows"])
            self.assertFalse(row["materializes_neighbor_rows"])
            self.assertFalse(row["paper_equivalent_rtnn_row"])
            self.assertFalse(row["prepared_cuda_graph_replay"])
            self.assertFalse(row["rt_core_neighbor_search_claim_authorized"])
            self.assertFalse(row["rtdl_speedup_claim_authorized"])

    def test_script_rebuilds_intake_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rtnn_intake.json"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(out)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(rebuilt["comparison"]["intake_pass"])
            self.assertEqual(rebuilt["pairs"], self.load()["pairs"])
            self.assertEqual(rebuilt["claim_boundary"], self.load()["claim_boundary"])

    def test_report_keeps_release_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not M7 release evidence",
            "does not authorize V3 release wording",
            "all_wall_optix_slower_than_embree: true",
            "universal RTNN acceleration",
            "OptiX wall timing is slower than Embree",
            "public_speedup_claim_authorized: false",
            "m7_qualified: false",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
