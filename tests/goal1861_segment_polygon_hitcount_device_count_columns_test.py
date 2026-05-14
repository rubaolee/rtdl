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
REPORT = ROOT / "docs" / "reports" / "goal1861_segment_polygon_hitcount_device_count_columns_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1861_segment_polygon_hitcount_device_count_columns_pod_smoke.json"


class _FakeColumn:
    def __init__(self, values):
        self.values = list(values)
        self.shape = (len(self.values),)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return _FakeColumn(self.values[item])
        return self.values[item]


def _fake_count_unique_pairs_by_ids(segment_ids, witness_ray_ids, witness_primitive_ids):
    seen = set(zip(witness_ray_ids.values, witness_primitive_ids.values))
    counts = []
    for segment_id in segment_ids.values:
        counts.append(sum(1 for ray_id, _ in seen if ray_id == segment_id))
    return _FakeColumn(counts)


def _fake_tensor(values, dtype, device):
    return _FakeColumn(values)


class Goal1861SegmentPolygonHitcountDeviceCountColumnsTest(unittest.TestCase):
    def test_adapter_is_exported_and_documents_partner_gpu_materialization(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIsNotNone(rt.segment_polygon_hitcount_optix_partner_device_count_columns)
        self.assertIn("segment_polygon_hitcount_optix_partner_device_count_columns", adapter_source)
        self.assertIn("segment_polygon_hitcount_optix_partner_device_count_columns", init_source)
        self.assertIn("partner_columns_from_host_exact_filter", adapter_source)
        self.assertIn("app_count_host_materialization", adapter_source)

    def test_adapter_keeps_counts_in_partner_columns(self) -> None:
        runtime = {
            "name": "fake",
            "device": "cuda:0",
            "uint32": "uint32",
            "tensor": _fake_tensor,
            "to_host": lambda value: [int(item) for item in value.values],
            "slice": lambda value, count: value[:count],
            "sync": lambda: None,
            "count_unique_pairs_by_ids": _fake_count_unique_pairs_by_ids,
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
                "true_zero_copy_authorized": True,
                "v2_0_release_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }

        with mock.patch.object(
            partner_adapters,
            "_segment_polygon_all_witness_columns_optix_partner_columns",
            return_value=witness_result,
        ):
            result = rt.segment_polygon_hitcount_optix_partner_device_count_columns(
                segment_ray_columns,
                polygon_triangle_columns,
                _FakeColumn([]),
                partner="torch",
                return_metadata=True,
            )

        self.assertIs(result["columns"]["segment_ids"], segment_ray_columns["ids"])
        self.assertEqual(result["columns"]["hit_counts"].values, [2, 1, 0])
        metadata = result["metadata"]
        self.assertEqual(metadata["adapter"], "segment_polygon_hitcount_optix_partner_device_count_columns")
        self.assertEqual(metadata["app_count_materialization"], "partner_columns_from_host_exact_filter")
        self.assertTrue(metadata["app_count_host_materialization"])
        self.assertFalse(metadata["whole_app_true_zero_copy_authorized"])
        self.assertFalse(metadata["v2_0_release_authorized"])

    def test_report_keeps_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("candidate witness IDs", report)
        self.assertIn("whole_app_true_zero_copy_authorized: false", report)
        self.assertIn("v2_0_release_authorized: false", report)
        self.assertEqual(artifact["status"], "pass")
        self.assertIn("NVIDIA RTX A4500", artifact["gpu"])
        for partner in ("cupy", "torch"):
            with self.subTest(partner=partner):
                result = artifact["results"][partner]
                self.assertEqual(result["columns"]["segment_ids"], [101, 102, 103])
                self.assertEqual(result["columns"]["hit_counts"], [2, 2, 0])
                metadata = result["metadata"]
                self.assertEqual(metadata["adapter"], "segment_polygon_hitcount_optix_partner_device_count_columns")
                self.assertIn(metadata["app_count_materialization"], {
                    "partner_gpu_from_generic_witness_pairs",
                    "partner_columns_from_host_exact_filter",
                })
                self.assertFalse(metadata["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
