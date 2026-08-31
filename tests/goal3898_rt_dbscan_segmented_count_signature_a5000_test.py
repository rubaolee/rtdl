from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3898_rt_dbscan_segmented_count_signature_a5000"
NEW_PAYLOAD = ARTIFACT_DIR / "rt_dbscan_segmented_count_signature_65k.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
OLD_PAYLOAD = (
    ROOT
    / "docs"
    / "reports"
    / "goal3894_current_scale_with_runtime_provenance_a5000"
    / "outputs"
    / "rt_dbscan_optix_numba_scale_default_65536_no_validation.stdout.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3898_rt_dbscan_segmented_count_signature_2026-06-08.md"


class Goal3898RtDbscanSegmentedCountSignatureA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.new_payload = json.loads(NEW_PAYLOAD.read_text(encoding="utf-8"))
        cls.old_payload = json.loads(OLD_PAYLOAD.read_text(encoding="utf-8"))
        cls.new_breakdown = cls.new_payload["metadata"]["benchmark_timing_breakdown"]
        cls.old_breakdown = cls.old_payload["metadata"]["benchmark_timing_breakdown"]

    def test_pod_artifact_matches_previous_signature_and_uses_fast_strategy(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertEqual(self.new_payload["signature"], self.old_payload["signature"])
        metadata = self.new_payload["metadata"]
        self.assertEqual(metadata["partner"], "numba")
        self.assertEqual(
            metadata["path"],
            "optix_rt_grouped_stream_numba_radius_graph_column_signature_3d",
        )
        self.assertEqual(metadata["column_signature_strategy"], "numba_segmented_count_all_core_labels")
        self.assertTrue(metadata["column_signature_uses_numba_segmented_count"])
        self.assertFalse(metadata["column_signature_materializes_point_ids"])
        self.assertFalse(metadata["column_signature_materializes_core_flags"])
        self.assertFalse(metadata["app_specific_engine_logic_allowed"])
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_segmented_count_signature_reduces_signature_overhead_not_native_traversal(self) -> None:
        old_signature_sec = self.old_breakdown["host_observed_sec"]["column_signature_sec"]
        new_signature_sec = self.new_breakdown["host_observed_sec"]["column_signature_sec"]
        old_elapsed = self.old_payload["elapsed_sec"]
        new_elapsed = self.new_payload["elapsed_sec"]
        old_native = self.old_breakdown["derived_sec"]["grouped_native_sec"]
        new_native = self.new_breakdown["derived_sec"]["grouped_native_sec"]

        self.assertLess(new_signature_sec, old_signature_sec / 4.0)
        self.assertLess(new_elapsed, old_elapsed * 0.8)
        self.assertLess(abs(new_native - old_native), 0.005)

    def test_report_documents_internal_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3898",
            "generic Numba `segmented_count_i64`",
            "Column-signature sec",
            "Native grouped-union sec",
            "does not authorize release action",
            "not the RT traversal primitive",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
