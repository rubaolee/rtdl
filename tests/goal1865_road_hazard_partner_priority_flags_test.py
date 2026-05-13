from __future__ import annotations

import pathlib
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1865_road_hazard_partner_priority_flags_2026-05-13.md"


class _FakeColumn:
    def __init__(self, values):
        self.values = list(values)
        self.shape = (len(self.values),)


def _fake_partner_module(name: str):
    if name != "torch":
        raise AssertionError(name)
    return {
        "name": "torch",
        "sync": lambda: None,
        "greater_equal_uint32": lambda value, threshold: _FakeColumn(
            [1 if int(item) >= int(threshold) else 0 for item in value.values]
        ),
    }


class Goal1865RoadHazardPartnerPriorityFlagsTest(unittest.TestCase):
    def test_adapter_is_exported_and_keeps_native_contract_generic(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIsNotNone(rt.road_hazard_priority_flags_optix_partner_device_columns)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", adapter_source)
        self.assertIn("partner_gpu_threshold_from_hit_counts", adapter_source)
        self.assertIn("generic_ray_primitive_witness_pairs", adapter_source)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", init_source)

    def test_adapter_thresholds_hit_counts_in_partner_columns(self) -> None:
        hitcount_result = {
            "columns": {
                "segment_ids": _FakeColumn([101, 102, 103]),
                "hit_counts": _FakeColumn([2, 1, 0]),
            },
            "metadata": {
                "adapter": "segment_polygon_hitcount_optix_partner_device_count_columns",
                "app_count_materialization": "partner_gpu_from_generic_witness_pairs",
                "app_count_host_materialization": False,
                "input_contract": "caller_supplied_partner_device_columns",
                "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
                "whole_app_true_zero_copy_authorized": True,
                "v2_0_release_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with mock.patch.object(
                partner_adapters,
                "segment_polygon_hitcount_optix_partner_device_count_columns",
                return_value=hitcount_result,
            ):
                result = rt.road_hazard_priority_flags_optix_partner_device_columns(
                    {"ids": _FakeColumn([101, 102, 103])},
                    {"ids": _FakeColumn([11, 12])},
                    _FakeColumn([]),
                    threshold=2,
                    partner="torch",
                    return_metadata=True,
                )

        columns = result["columns"]
        self.assertIs(columns["road_ids"], hitcount_result["columns"]["segment_ids"])
        self.assertIs(columns["hit_counts"], hitcount_result["columns"]["hit_counts"])
        self.assertEqual(columns["priority_flags"].values, [1, 0, 0])
        self.assertEqual(columns["priority_flags"].shape, columns["road_ids"].shape)

        metadata = result["metadata"]
        self.assertEqual(metadata["adapter"], "road_hazard_priority_flags_optix_partner_device_columns")
        self.assertEqual(metadata["app"], "road_hazard_screening")
        self.assertEqual(metadata["priority_threshold"], 2)
        self.assertEqual(metadata["app_count_materialization"], "partner_gpu_from_generic_witness_pairs")
        self.assertEqual(metadata["app_priority_materialization"], "partner_gpu_threshold_from_hit_counts")
        self.assertFalse(metadata["app_priority_host_materialization"])
        self.assertFalse(metadata["v2_0_release_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

    def test_empty_input_preserves_empty_partner_columns_and_boundaries(self) -> None:
        hitcount_result = {
            "columns": {
                "segment_ids": _FakeColumn([]),
                "hit_counts": _FakeColumn([]),
            },
            "metadata": {
                "adapter": "segment_polygon_hitcount_optix_partner_device_count_columns",
                "app_count_materialization": "partner_gpu_from_generic_witness_pairs",
                "app_count_host_materialization": False,
                "input_contract": "caller_supplied_partner_device_columns",
                "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
                "whole_app_true_zero_copy_authorized": True,
                "v2_0_release_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with mock.patch.object(
                partner_adapters,
                "segment_polygon_hitcount_optix_partner_device_count_columns",
                return_value=hitcount_result,
            ):
                result = rt.road_hazard_priority_flags_optix_partner_device_columns(
                    {"ids": _FakeColumn([])},
                    {"ids": _FakeColumn([11])},
                    _FakeColumn([]),
                    threshold=2,
                    partner="torch",
                    return_metadata=True,
                )

        columns = result["columns"]
        self.assertEqual(columns["road_ids"].values, [])
        self.assertEqual(columns["hit_counts"].values, [])
        self.assertEqual(columns["priority_flags"].values, [])
        self.assertEqual(columns["priority_flags"].shape, columns["road_ids"].shape)

        metadata = result["metadata"]
        self.assertEqual(metadata["native_engine_row_contract"], "generic_ray_primitive_witness_pairs")
        self.assertEqual(metadata["app_priority_materialization"], "partner_gpu_threshold_from_hit_counts")
        self.assertFalse(metadata["app_priority_host_materialization"])
        self.assertFalse(metadata["v2_0_release_authorized"])

    def test_negative_threshold_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "threshold must be non-negative"):
            rt.road_hazard_priority_flags_optix_partner_device_columns(
                {"ids": _FakeColumn([101])},
                {"ids": _FakeColumn([11])},
                _FakeColumn([]),
                threshold=-1,
                partner="torch",
            )

    def test_report_keeps_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", report)
        self.assertIn("native_engine_row_contract: generic_ray_primitive_witness_pairs", report)
        self.assertIn("v2_0_release_authorized: false", report)
        self.assertIn("whole_app_speedup_claim_authorized: false", report)
        self.assertIn("No pod timing was run", report)
        self.assertIn("goal1866_copilot_extra_review_goal1865", report)
        self.assertIn("does not replace Claude or Gemini", report)


if __name__ == "__main__":
    unittest.main()
