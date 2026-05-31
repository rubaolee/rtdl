from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
HIT_STREAM_HANDOFF = REPO_ROOT / "src" / "rtdsl" / "hit_stream_handoff.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2789_neutral_buffer_torch_carrier_reconciliation_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2789_gemini_review_neutral_buffer_torch_carrier_reconciliation_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2789_neutral_buffer_torch_carrier_reconciliation_consensus_2026-05-31.md"


class Goal2789NeutralBufferTorchCarrierReconciliationTest(unittest.TestCase):
    def test_old_implicit_torch_column_helper_is_removed(self) -> None:
        source = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")

        self.assertNotIn("_maybe_torch_column", source)
        self.assertIn("_prepare_triton_tensor_carrier_column", source)
        self.assertIn("silent_cross_partner_torch_coercion_allowed", source)
        self.assertIn('"neutral_buffer_seam_contract_version"', source)

    def test_host_bridge_columns_remain_neutral_buffer_accounted(self) -> None:
        hit_stream = {
            "primitive": rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
            "row_schema": rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA,
            "rows": ({"ray_id": 0, "primitive_id": 1}, {"ray_id": 1, "primitive_id": 0}),
            "max_rows": 2,
            "backend": "reference",
            "overflow": False,
            "phase_timing_seconds": {},
        }
        hit_columns = rt.prepare_generic_hit_stream_columns_from_rows(hit_stream)
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            [0, 1],
            [10.0, 20.0],
            group_count=2,
        )
        adapter = rt.describe_v2_5_hit_stream_torch_carrier_adapter(hit_columns, payload_columns)
        hit_metadata = hit_columns.to_metadata()
        payload_metadata = payload_columns.to_metadata()

        self.assertEqual(hit_metadata["neutral_buffer_seam_contract_version"], rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION)
        self.assertEqual(payload_metadata["neutral_buffer_seam_contract_version"], rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION)
        self.assertFalse(hit_metadata["true_zero_copy_authorized"])
        self.assertFalse(adapter["silent_cross_partner_torch_coercion_allowed"])
        self.assertEqual(adapter["torch_carrier_allowed_only_for_partner"], "triton")
        self.assertFalse(adapter["true_zero_copy_authorized"])
        self.assertTrue(
            any(
                seam["transfer_status"] == "host_stage"
                for seam in hit_metadata["neutral_buffer_seams"]
            )
        )

    def test_report_records_reconciliation_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2789", report)
        self.assertIn("explicit Triton tensor-carrier preparation", report)
        self.assertIn("not true zero-copy", report)
        self.assertIn("accept-with-boundary", report)

    def test_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("silent cross-partner torch coercion remains disallowed", review)
        self.assertIn("Codex + Gemini", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("not a zero-copy promotion", consensus)


if __name__ == "__main__":
    unittest.main()
