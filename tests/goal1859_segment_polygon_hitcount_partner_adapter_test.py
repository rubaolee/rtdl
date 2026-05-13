from __future__ import annotations

import pathlib
import json
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1859_segment_polygon_hitcount_partner_adapter_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1859_segment_polygon_hitcount_partner_adapter_pod_smoke.json"


class _FakeColumn:
    def __init__(self, values):
        self.values = list(values)
        self.shape = (len(self.values),)


def _fake_partner_module(name: str):
    if name != "torch":
        raise AssertionError(name)
    return {
        "name": "torch",
        "device": "cuda:0",
        "uint32": "uint32",
        "float64": "float64",
        "float32": "float32",
        "tensor": lambda values, dtype, device: _FakeColumn(values),
        "zeros": lambda shape, dtype, device: _FakeColumn([0] * int(shape[0])),
        "sync": lambda: None,
        "to_host": lambda value: [int(item) for item in value.values],
    }


class Goal1859SegmentPolygonHitcountPartnerAdapterTest(unittest.TestCase):
    def test_hitcount_adapter_is_exported_and_keeps_native_contract_generic(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIsNotNone(rt.segment_polygon_hitcount_optix_partner_columns)
        self.assertIn("segment_polygon_hitcount_optix_partner_columns", adapter_source)
        self.assertIn("python_from_generic_witness_pairs", adapter_source)
        self.assertIn("generic_ray_primitive_witness_pairs", adapter_source)
        self.assertIn("segment_polygon_hitcount_optix_partner_columns", init_source)

    def test_hitcount_adapter_counts_deduplicated_witness_rows_per_segment(self) -> None:
        segment_ray_columns = {"ids": _FakeColumn([101, 102, 103])}
        witness_rows = (
            {"segment_id": 101, "polygon_id": 11},
            {"segment_id": 101, "polygon_id": 12},
            {"segment_id": 101, "polygon_id": 12},
            {"segment_id": 102, "polygon_id": 12},
        )

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with mock.patch.object(
                partner_adapters,
                "segment_polygon_anyhit_rows_optix_partner_columns",
                return_value={
                    "rows": witness_rows,
                    "metadata": {
                        "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
                        "v2_0_release_authorized": False,
                        "whole_app_speedup_claim_authorized": False,
                    },
                },
            ):
                result = rt.segment_polygon_hitcount_optix_partner_columns(
                    segment_ray_columns,
                    {"ids": _FakeColumn([11, 12])},
                    _FakeColumn([0.0] * 12),
                    partner="torch",
                    return_metadata=True,
                )

        self.assertEqual(
            result["rows"],
            (
                {"segment_id": 101, "hit_count": 2},
                {"segment_id": 102, "hit_count": 1},
                {"segment_id": 103, "hit_count": 0},
            ),
        )
        self.assertEqual(result["metadata"]["adapter"], "segment_polygon_hitcount_optix_partner_columns")
        self.assertEqual(result["metadata"]["app_count_materialization"], "python_from_generic_witness_pairs")
        self.assertTrue(result["metadata"]["app_count_host_materialization"])
        self.assertFalse(result["metadata"]["whole_app_true_zero_copy_authorized"])
        self.assertFalse(result["metadata"]["v2_0_release_authorized"])

    def test_report_and_pod_artifact_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("second app-level v2.0 OptiX partner adapter", report)
        self.assertEqual(artifact["status"], "pass")
        self.assertIn("NVIDIA RTX A4500", artifact["gpu"])
        expected_rows = [
            {"hit_count": 2, "segment_id": 101},
            {"hit_count": 2, "segment_id": 102},
            {"hit_count": 0, "segment_id": 103},
        ]
        for partner in ("cupy", "torch"):
            with self.subTest(partner=partner):
                result = artifact["results"][partner]
                self.assertEqual(result["rows"], expected_rows)
                metadata = result["metadata"]
                self.assertEqual(metadata["adapter"], "segment_polygon_hitcount_optix_partner_columns")
                self.assertEqual(metadata["app_count_materialization"], "python_from_generic_witness_pairs")
                self.assertTrue(metadata["app_count_host_materialization"])
                self.assertFalse(metadata["whole_app_true_zero_copy_authorized"])
                self.assertEqual(metadata["native_engine_row_contract"], "generic_ray_primitive_witness_pairs")
                self.assertTrue(metadata["true_zero_copy_authorized"])
                self.assertTrue(metadata["exact_row_semantics_authorized"])
                self.assertFalse(metadata["v2_0_release_authorized"])
                self.assertFalse(metadata["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
