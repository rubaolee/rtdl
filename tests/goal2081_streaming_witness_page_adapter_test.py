from __future__ import annotations

import pathlib
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal2081_streaming_witness_page_adapter_2026-05-15.md"
PERF = ROOT / "scripts" / "goal2081_streaming_witness_page_perf.py"


class _FakeColumn:
    def __init__(self, values):
        self.values = list(values)
        self.shape = (len(self.values),)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return _FakeColumn(self.values[item])
        return self.values[item]


def _fake_tensor(values, dtype, device):
    return _FakeColumn(values)


class _FakePreparedScene:
    def __init__(self, polygon_triangle_columns):
        self.polygon_triangle_columns = polygon_triangle_columns
        self._partner_exact_filter_triangle_lookup_cache = {}


class Goal2081StreamingWitnessPageAdapterTest(unittest.TestCase):
    def test_adapter_is_public_and_keeps_engine_generic(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIsNotNone(rt.segment_polygon_exact_witness_pair_page_optix_partner_columns)
        self.assertIsNotNone(rt.segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns)
        self.assertIn("segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns", adapter_source)
        self.assertIn("generic_ray_primitive_candidate_witness_pairs", adapter_source)
        self.assertIn("not_performed_exact_witness_columns_only", adapter_source)
        self.assertIn("full_python_row_table_materialization_avoided", adapter_source)
        self.assertIn("segment_polygon_exact_witness_pair_page_optix_partner_columns", init_source)

    def test_prepared_adapter_pages_exact_witness_columns_without_python_rows(self) -> None:
        runtime = {
            "name": "fake",
            "device": "cuda:0",
            "uint32": "uint32",
            "tensor": _fake_tensor,
            "to_host": lambda value: [int(item) for item in value.values],
            "to_host_float": lambda value: [float(item) for item in value.values],
            "slice": lambda value, count: value[:count],
            "sync": lambda: None,
        }
        segment_ray_columns = {
            "ids": _FakeColumn([101, 102, 103]),
            "ox": _FakeColumn([-0.25, -0.25, 2.0]),
            "oy": _FakeColumn([0.25, 0.25, 2.0]),
            "dx": _FakeColumn([1.5, 1.5, 1.0]),
            "dy": _FakeColumn([0.0, 0.0, 0.0]),
            "tmax": _FakeColumn([1.0, 1.0, 1.0]),
        }
        polygon_triangle_columns = {
            "ids": _FakeColumn([11, 12]),
            "x0": _FakeColumn([0.0, 0.25]),
            "y0": _FakeColumn([0.0, 0.20]),
            "x1": _FakeColumn([1.0, 0.75]),
            "y1": _FakeColumn([0.0, 0.20]),
            "x2": _FakeColumn([0.0, 0.25]),
            "y2": _FakeColumn([1.0, 0.80]),
        }
        witness_result = {
            "runtime": runtime,
            "witness_ray_ids": _FakeColumn([101, 101, 101, 102]),
            "witness_primitive_ids": _FakeColumn([11, 12, 12, 12]),
            "emitted_count": 4,
            "metadata": {
                "native_engine_row_contract": "generic_ray_primitive_candidate_witness_pairs",
                "emitted_count": 4,
                "overflowed": False,
                "v2_0_release_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }

        with mock.patch.object(
            partner_adapters,
            "_segment_polygon_all_witness_columns_optix_partner_columns",
            return_value=witness_result,
        ):
            result = rt.segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns(
                _FakePreparedScene(polygon_triangle_columns),
                segment_ray_columns,
                partner="torch",
                page_offset=1,
                page_limit=2,
                return_metadata=True,
            )

        columns = result["columns"]
        self.assertEqual(columns["witness_ray_ids"].values, [101, 102])
        self.assertEqual(columns["witness_primitive_ids"].values, [12, 12])
        metadata = result["metadata"]
        self.assertEqual(metadata["adapter"], "segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns")
        self.assertEqual(metadata["exact_witness_count"], 3)
        self.assertEqual(metadata["page_row_count"], 2)
        self.assertEqual(metadata["app_row_materialization"], "not_performed_exact_witness_columns_only")
        self.assertTrue(metadata["full_python_row_table_materialization_avoided"])
        self.assertFalse(metadata["v2_0_release_authorized"])

    def test_report_records_design_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        perf = PERF.read_text(encoding="utf-8")
        self.assertIn("generic ray/primitive candidate witness pairs", report)
        self.assertIn("does not add app logic to the native engine", report)
        self.assertIn("Pod timing is still required", report)
        self.assertIn("v2_0_streaming_exact_witness_page_columns", perf)
        self.assertIn("segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns", perf)
        self.assertIn("ratio_vs_old_v2_full_rows", perf)


if __name__ == "__main__":
    unittest.main()
