from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4462_v3_0_m66_triangle_segmented_com_lj_2026-06-16.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal4462_v3_0_m66_triangle_segmented_com_lj_2026-06-16.json"
SNAP_PREP = ROOT / "docs" / "reports" / "goal4462_snap_prepare_com_lj_2026-06-16.json"
OLD_RTDL_2A1 = ROOT / "docs" / "reports" / "goal2593_paper_dataset_raw" / "goal2593_eval_com_lj_rtdl_2a1.json"
SCRIPT = ROOT / "scripts" / "v3_0_m66_triangle_segmented_paper_dataset_measure.py"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4462V30M66TriangleSegmentedPaperDatasetTest(unittest.TestCase):
    def test_evidence_records_com_lj_segmented_success_without_global_two_hop(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        row = evidence["rows"][0]

        self.assertEqual(4462, evidence["goal"])
        self.assertEqual("segmented_2a1_cupy_paper_dataset", evidence["implementation"])
        self.assertEqual("com_lj", row["dataset"])
        self.assertEqual(34_681_189, row["edge_count"])
        self.assertEqual(177_820_130, row["expected_triangle_count"])
        self.assertEqual(177_820_130, row["observed_triangle_count"])
        self.assertTrue(row["triangle_count_matches_expected"])
        self.assertFalse(row["global_two_hop_summary_materialized"])
        self.assertFalse(evidence["comparison"]["global_two_hop_summary_materialized"])
        self.assertEqual(186, row["segmentation"]["segment_count"])
        self.assertEqual(928_731_472, row["segmentation"]["total_two_hop_rows"])
        self.assertFalse(evidence["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_ties_new_success_to_goal2593_oom(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        old = json.loads(OLD_RTDL_2A1.read_text(encoding="utf-8"))
        prep = json.loads(SNAP_PREP.read_text(encoding="utf-8"))

        old_failure = old["results"]["com_lj"]["methods"]["rtdl_2a1"]
        self.assertEqual("failed", old_failure["status"])
        self.assertIn("7429851776 bytes", old_failure["error"])
        self.assertTrue(prep["datasets"]["com_lj"]["edge_count_matches_snap"])
        self.assertIn("Goal4462", report)
        self.assertIn("com-lj", report)
        self.assertIn("177,820,130", report)
        self.assertIn("7,429,851,776-byte CUDA allocation failure", report)
        self.assertIn("not a public speedup claim", report)

    def test_script_and_registries_record_m66_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("rt_graph_2a1_segmented_generic_rt", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4484.v1", route["version"])
        self.assertIn("Goal4462", route["evidence_refs"])
        self.assertIn("com-lj", route["current_reader_decision"])
        self.assertIn("com-orkut", route["next_runtime_action"])
        self.assertIn("prepared ray-batch weighted-sum API", route["next_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4484.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4462", triangle["evidence_refs"])
        self.assertIn("com-lj", triangle["current_performance_reading"])
        self.assertFalse(triangle["paper_reproduction_claim_authorized"])


if __name__ == "__main__":
    unittest.main()



