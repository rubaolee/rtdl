import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_triangle_prepared_graph_intake.py"
EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_triangle_prepared_graph_20260620"
    / "triangle_prepared_graph_intake_summary.json"
)
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md"


class V3PhoenixTrianglePreparedGraphIntakeTest(unittest.TestCase):
    def load(self):
        return json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_intake_passes_as_internal_candidate_not_m7(self):
        payload = self.load()
        self.assertEqual(payload["status"], "internal_triangle_prepared_graph_candidate_not_m7")
        self.assertEqual(payload["generic_capability"], "prepared_graph_chunk")
        self.assertEqual(
            payload["generic_capability_status"],
            "candidate_executor_linkage_not_closed",
        )
        expected_blockers = {
            "synthetic_k4_clique_ladder_not_paper_dataset",
            "not_graph_database_or_full_triangle_counting_app",
            "no_author_code_or_paper_dataset_comparison",
            "prepared_graph_chunk_executor_linkage_not_closed",
            "hot_query_vs_wall_timing_ratio_not_characterized_for_release",
            "public_row_level_external_review_not_done",
        }
        self.assertTrue(expected_blockers.issubset(set(payload["m7_blockers"])))
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertEqual(payload["claim_boundary"]["m7_qualified_release_rows"], 0)
        comparison = payload["comparison"]
        self.assertTrue(comparison["intake_pass"])
        self.assertEqual(comparison["errors"], [])
        self.assertEqual(comparison["row_count"], 4)
        self.assertEqual(comparison["group_count"], 2)
        self.assertTrue(comparison["all_rows_ok"])
        self.assertTrue(comparison["all_match_oracle"])
        self.assertTrue(comparison["all_claim_flags_blocked"])
        self.assertTrue(comparison["all_phase_timing_accept"])
        self.assertTrue(comparison["same_metric_source"])
        self.assertTrue(comparison["same_contract"])
        self.assertTrue(comparison["optix_rt_core_and_embree_non_rt_core"])
        self.assertFalse(comparison["m7_qualified"])

    def test_pairs_preserve_strong_rows_but_keep_boundaries(self):
        payload = self.load()
        pairs = {pair["comparison_group"]: pair for pair in payload["pairs"]}
        self.assertGreater(
            pairs["triangle_count_rt_graph_2a1_cliques_20000"]["optix_speedup_vs_embree"],
            100.0,
        )
        self.assertGreater(
            pairs["triangle_count_rt_graph_2a1_cliques_80000"]["optix_speedup_vs_embree"],
            300.0,
        )
        for pair in pairs.values():
            self.assertEqual(pair["claim_status"], "internal_candidate_not_m7")
            self.assertTrue(pair["same_metric_source"])
            self.assertTrue(pair["same_contract"])
            self.assertFalse(pair["embree_rt_core_accelerated"])
            self.assertTrue(pair["optix_rt_core_accelerated"])
            self.assertGreater(pair["optix_wall_speedup_vs_embree"], 1.0)
            self.assertLess(pair["optix_wall_speedup_vs_embree"], pair["optix_speedup_vs_embree"])
            self.assertGreater(pair["embree_wall_median_sec"], pair["embree_query_median_sec"])
            self.assertGreater(pair["optix_wall_median_sec"], pair["optix_query_median_sec"])

    def test_rows_block_public_claim_flags_and_preserve_phase_contract(self):
        payload = self.load()
        for row in payload["rows"]:
            self.assertTrue(row["triangle_count_matches_oracle"])
            self.assertTrue(row["claim_flags_blocked"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["paper_reproduction"])
            self.assertFalse(row["full_graph_database_claim"])
            self.assertTrue(row["phase_timing_accept"])
            self.assertTrue(row["same_phase_contract_as_basis"])
            self.assertEqual(row["phase_contract_version"], "rtdl.partner.v2.4")
            self.assertGreater(row["wall_median_sec"], row["primary_metric_sec"])
            self.assertEqual(
                row["synthetic_fixture_boundary"],
                "K4 clique ladder; not graph database or paper dataset",
            )

    def test_script_rebuilds_intake_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "triangle_intake.json"
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
            "not a graph database workload or full triangle-counting app",
            "not yet closed against the V3 prepared-graph chunk executor",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "m7_qualified: false",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
