import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_figure5_timing_denominator_audit.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json"
)
LOG_INDEX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_branch_log_index_goal5176_2026-07-08.json"
)
COVERAGE_GAP = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("build_xhd_figure5_timing_denominator_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5288XhdFigure5TimingDenominatorAuditTest(unittest.TestCase):
    def test_builder_extracts_complete_author_figure5_log_matrix(self):
        module = _load_script()
        artifact = module.build_figure5_audit(
            log_index_path=LOG_INDEX,
            coverage_gap_path=COVERAGE_GAP,
            date="2026-07-09",
        )

        self.assertEqual(
            artifact["status"],
            "figure5_author_timing_denominator_audit_ready__figure5_not_reproduced",
        )
        self.assertTrue(artifact["matched"])
        denominator = artifact["author_figure5_log_denominator"]
        self.assertEqual(denominator["record_count"], 2535)
        self.assertEqual(denominator["unique_pair_count"], 507)
        self.assertEqual(denominator["complete_author_pair_count"], 507)
        self.assertEqual(denominator["incomplete_author_pair_count"], 0)
        self.assertEqual(denominator["section_summary"]["auto_tune"]["record_count"], 1014)
        self.assertEqual(denominator["section_summary"]["rt_gpu"]["record_count"], 507)
        self.assertEqual(denominator["section_summary"]["eb_gpu"]["record_count"], 507)
        self.assertEqual(denominator["section_summary"]["hybrid_gpu"]["record_count"], 507)

    def test_artifact_keeps_category_coverage_and_missing_rtdl_matrix_explicit(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        categories = payload["author_figure5_log_denominator"]["category_summary"]
        timing = payload["timing_denominator"]

        self.assertEqual(categories["BraTS2020_ValidationData"]["record_count"], 2500)
        self.assertEqual(categories["BraTS2020_ValidationData"]["unique_pair_count"], 500)
        self.assertEqual(categories["geo"]["record_count"], 15)
        self.assertEqual(categories["geo"]["unique_pair_count"], 3)
        self.assertEqual(categories["graphics"]["record_count"], 20)
        self.assertEqual(categories["graphics"]["unique_pair_count"], 4)
        self.assertEqual(timing["author_gpu_names"], ["NVIDIA GeForce RTX 3090"])
        self.assertFalse(timing["same_denominator_author_rtdl_performance"])
        self.assertFalse(timing["rtdl_current_coverage"]["brats_full_workload_gate_present"])
        self.assertFalse(timing["rtdl_current_coverage"]["geo_full_workload_gate_present"])
        self.assertFalse(timing["rtdl_current_coverage"]["figure5_full_matrix_gate_present"])
        self.assertEqual(timing["rtdl_current_coverage"]["graphics_representative_count"], 4)
        self.assertTrue(timing["rtdl_current_coverage"]["modelnet40_all400_present_but_not_figure5_category"])

    def test_claim_boundary_forbids_ratio_and_figure5_reproduction(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(payload["decision"]["figure5_reproduced"])
        self.assertFalse(payload["decision"]["performance_ratio_allowed"])
        for value in payload["claim_boundary"].values():
            self.assertFalse(value)
        forbidden = payload["decision"]["forbidden_summaries"]
        self.assertIn("Figure 5 reproduced", forbidden)
        self.assertIn("RTDL/author Figure 5 speedup", forbidden)
        self.assertIn("author Running.AvgTime equals RTDL route wall", forbidden)
        self.assertIn("ModelNet40 all400 proves Figure 5", forbidden)
        self.assertIn("same hardware RTDL route timing for every Figure 5 category", payload["timing_denominator"]["author_missing_fields_for_fair_wall_ratio"])


if __name__ == "__main__":
    unittest.main()
