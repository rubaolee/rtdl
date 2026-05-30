import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2715_raydb_native_device_hit_stream_pointer_pod_evidence_2026-05-30.md"
FULL_GRID = (
    ROOT
    / "docs"
    / "reports"
    / "goal2715_pod_artifacts"
    / "goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.json"
)
SMOKE = (
    ROOT
    / "docs"
    / "reports"
    / "goal2716_pod_artifacts"
    / "goal2716_hit_stream_carrier_execution_flag_smoke_pod_69_30_85_171_2026-05-30.json"
)


class Goal2715RaydbNativeDeviceHitStreamPointerPodEvidenceTest(unittest.TestCase):
    def test_full_grid_records_native_device_pointer_evidence_without_claims(self) -> None:
        payload = json.loads(FULL_GRID.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertEqual(len(payload["cases"]), 30)
        self.assertFalse(payload.get("public_speedup_claim_authorized", False))
        self.assertTrue(payload["no_public_speedup_claim"])

        device_cases = [
            case
            for case in payload["cases"]
            if case["backend"] == "paper_rt_optix_device_hit_stream_triton"
        ]
        self.assertEqual(len(device_cases), 15)
        self.assertTrue(all(case["native_device_column_path_used"] for case in device_cases))
        self.assertTrue(all(case["host_row_bridge_bypassed"] for case in device_cases))
        self.assertTrue(
            all(case["handoff_materializes_host_rows_for_bridge"] is False for case in device_cases)
        )
        self.assertTrue(
            all(case["torch_carrier_same_pointer_evidence_observed"] is True for case in device_cases)
        )
        self.assertTrue(all(case["true_zero_copy_authorized"] is False for case in device_cases))
        self.assertTrue(
            all(case["metadata_timings"]["hit_stream_rt_traversal"] > 0.0 for case in device_cases)
        )

    def test_latest_smoke_marks_executed_adapter_evidence_but_not_zero_copy(self) -> None:
        payload = json.loads(SMOKE.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_correct"])
        case = payload["cases"][0]
        execution = case["torch_carrier_execution"]

        self.assertTrue(execution["adapter_execution_proven_on_hardware"])
        self.assertTrue(execution["same_pointer_evidence_observed"])
        self.assertTrue(execution["primitive_ids_same_pointer_as_input"])
        self.assertTrue(execution["primitive_group_ids_same_pointer_as_input"])
        self.assertTrue(execution["primitive_values_same_pointer_as_input"])
        self.assertFalse(execution["true_zero_copy_authorized"])
        self.assertFalse(case["true_zero_copy_authorized"])

    def test_report_states_boundary_and_next_work(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("same-pointer carrier execution observed", text)
        self.assertIn("No public true-zero-copy claim", text)
        self.assertIn("No public whole-app speedup claim", text)
        self.assertIn("Reduce `hit_stream_column_handoff`", text)


if __name__ == "__main__":
    unittest.main()
