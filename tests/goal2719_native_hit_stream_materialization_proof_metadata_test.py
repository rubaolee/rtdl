import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2719_native_hit_stream_materialization_proof_metadata_cleanup_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2719_pod_artifacts"
    / "goal2719_native_output_proven_materialization_removed_smoke_pod_69_30_85_171_2026-05-30.json"
)


class Goal2719NativeHitStreamMaterializationProofMetadataTest(unittest.TestCase):
    def test_pod_smoke_exposes_native_output_and_materialization_proof(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_correct"])
        case = payload["cases"][0]
        summary = case["neutral_buffer_handoff_summary"]
        execution = case["torch_carrier_execution"]

        self.assertTrue(case["handoff_native_device_column_output_proven_on_hardware"])
        self.assertTrue(case["handoff_removes_host_materialization_bottleneck"])
        self.assertTrue(summary["native_device_column_output_proven_on_hardware"])
        self.assertTrue(summary["removes_host_materialization_bottleneck"])
        self.assertTrue(execution["adapter_execution_proven_on_hardware"])
        self.assertTrue(execution["same_pointer_evidence_observed"])
        self.assertFalse(case["true_zero_copy_authorized"])
        self.assertTrue(payload["no_public_speedup_claim"])

    def test_report_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("metadata cleanup with pod smoke", text)
        self.assertIn("public true-zero-copy wording", text)
        self.assertIn("broad speedup wording", text)


if __name__ == "__main__":
    unittest.main()
