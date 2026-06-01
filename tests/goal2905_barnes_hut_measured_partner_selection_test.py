import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal2902_v2_5_current_packet_perf_triage as triage


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2905_barnes_hut_measured_partner_selection_2026-05-31.md"
HARNESS = ROOT / "scripts" / "goal2803_barnes_hut_v25_consolidated_harness.py"


class Goal2905BarnesHutMeasuredPartnerSelectionTest(unittest.TestCase):
    def test_harness_records_selected_partner_fields(self) -> None:
        text = HARNESS.read_text(encoding="utf-8")

        self.assertIn('"selected_partner"', text)
        self.assertIn('"selected_partner_median_sec"', text)
        self.assertIn('"selected_partner_reason"', text)
        self.assertIn('"triton_preview_promoted"', text)
        self.assertIn("torch_scatter_add_wins_same_contract_timing", text)

    def test_triage_no_longer_marks_barnes_target_when_torch_is_selected(self) -> None:
        payload = {
            "status": "pass",
            "max_optix_membership_speedup_vs_embree": 162.0,
            "vector_sum": {
                "triton_over_torch_ratio": 4.25,
                "selected_partner": "torch",
                "selected_partner_median_sec": 0.001,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "barnes.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            row = triage._barnes(path)

        self.assertEqual(row["performance_status"], "current_path_acceptable_with_measured_partner_selection")
        self.assertEqual(row["severity_ratio"], 1.0)
        self.assertEqual(row["selected_vector_sum_partner"], "torch")
        self.assertIn("Triton remains preview", row["next_action"])

    def test_triage_keeps_old_artifacts_as_target_until_selection_is_recorded(self) -> None:
        payload = {
            "status": "pass",
            "max_optix_membership_speedup_vs_embree": 162.0,
            "vector_sum": {"triton_over_torch_ratio": 4.25},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "barnes.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            row = triage._barnes(path)

        self.assertEqual(row["performance_status"], "performance_target")
        self.assertEqual(row["severity_ratio"], 4.25)

    def test_triage_treats_hausdorff_near_parity_as_acceptable(self) -> None:
        payload = {
            "status": "pass",
            "rtdl_over_cupy_grid_elapsed_ratio": 1.067,
            "rtdl": {
                "method": "rtdl_rt_grouped_reduced_nearest_witness",
                "median_elapsed_sec": 0.004801,
            },
            "baseline": {"median_elapsed_sec": 0.004499},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hausdorff.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            row = triage._hausdorff(path)

        self.assertEqual(row["performance_status"], "current_path_acceptable_near_parity")
        self.assertEqual(row["severity_ratio"], 1.0)
        self.assertEqual(row["near_parity_limit"], 1.10)
        self.assertIn("reduced_nearest_witness", row["route"])

    def test_report_records_design_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("user-selectable partners", text)
        self.assertIn("selected_partner", text)
        self.assertIn("Triton remains available", text)
        self.assertIn("No native app-specific engine logic is added", text)


if __name__ == "__main__":
    unittest.main()
