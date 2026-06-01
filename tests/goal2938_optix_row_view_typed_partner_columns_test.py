from __future__ import annotations

import ctypes
import unittest
from dataclasses import dataclass
from pathlib import Path

import rtdsl as rt


class _FakeRow(ctypes.Structure):
    _fields_ = (
        ("left_id", ctypes.c_uint32),
        ("right_id", ctypes.c_uint32),
        ("score", ctypes.c_double),
    )


@dataclass
class _FakeRowView:
    rows_ptr: object
    row_count: int
    row_type: object
    field_names: tuple[str, ...]


class Goal2938OptixRowViewTypedPartnerColumnsTest(unittest.TestCase):
    def test_row_view_converts_to_torch_partner_columns_without_dict_rows(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch is not installed")
        if not torch.cuda.is_available():
            self.skipTest("torch CUDA is not available")

        rows = (_FakeRow * 3)(
            _FakeRow(1, 10, 1.5),
            _FakeRow(2, 11, 2.5),
            _FakeRow(3, 12, 3.5),
        )
        view = _FakeRowView(
            rows_ptr=ctypes.cast(rows, ctypes.POINTER(_FakeRow)),
            row_count=3,
            row_type=_FakeRow,
            field_names=("left_id", "right_id", "score"),
        )

        result = rt.optix_row_view_to_partner_columns(view, partner="torch", return_metadata=True)
        columns = result["columns"]
        metadata = result["metadata"]

        self.assertEqual([1, 2, 3], [int(item) for item in columns["left_id"].detach().cpu().tolist()])
        self.assertEqual([10, 11, 12], [int(item) for item in columns["right_id"].detach().cpu().tolist()])
        self.assertEqual([1.5, 2.5, 3.5], [float(item) for item in columns["score"].detach().cpu().tolist()])
        self.assertEqual("optix_row_view_to_partner_columns", metadata["adapter"])
        self.assertEqual("typed_primitive_payload_columns", metadata["partner_reference_contract"])
        self.assertTrue(metadata["host_stage_copy_used"])
        self.assertFalse(metadata["python_dict_row_materialization_used"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["v2_5_release_authorized"])

    def test_missing_field_fails_closed(self) -> None:
        rows = (_FakeRow * 1)(_FakeRow(1, 10, 1.5))
        view = _FakeRowView(
            rows_ptr=ctypes.cast(rows, ctypes.POINTER(_FakeRow)),
            row_count=1,
            row_type=_FakeRow,
            field_names=("left_id", "right_id", "score"),
        )

        with self.assertRaisesRegex(ValueError, "missing requested fields"):
            rt.optix_row_view_to_partner_columns(view, fields=("left_id", "missing"), partner="torch")

    def test_report_and_readiness_index_document_bridge(self) -> None:
        root = Path(__file__).resolve().parents[1]
        report = root / "docs" / "reports" / "goal2938_optix_row_view_typed_partner_columns_2026-06-01.md"
        text = report.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=root)

        self.assertIn("optix_row_view_to_partner_columns", text)
        self.assertIn("host_stage_copy_used: true", text)
        self.assertIn("not the final v3-style device-resident", text)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2938_optix_row_view_typed_partner_columns_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2938_optix_row_view_typed_partner_columns_green", packet["allowed_next_actions"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=root)["status"])


if __name__ == "__main__":
    unittest.main()
