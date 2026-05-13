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
REPORT = ROOT / "docs" / "reports" / "goal1886_segment_polygon_prepared_partner_reuse_2026-05-13.md"
RUNNER = ROOT / "scripts" / "goal1863_segment_polygon_hitcount_v2_partner_perf.py"
ARTIFACT_2048 = ROOT / "docs" / "reports" / "goal1886_segment_polygon_prepared_reuse_pod_2048.json"


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


class Goal1886SegmentPolygonPreparedPartnerReuseTest(unittest.TestCase):
    def test_prepared_helpers_are_exported_and_bounded(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        for symbol in (
            "prepare_segment_polygon_anyhit_optix_partner_device_scene",
            "allocate_segment_polygon_witness_partner_device_output_columns",
            "segment_polygon_hitcount_optix_prepared_partner_device_count_columns",
            "road_hazard_priority_flags_optix_prepared_partner_device_columns",
        ):
            self.assertIn(symbol, adapter)
            self.assertIn(symbol, init_text)
            self.assertTrue(hasattr(rt, symbol))
        self.assertIn("prepared_scene_reused", adapter)
        self.assertIn("witness_output_columns_reused", adapter)
        self.assertIn("length must match output_capacity", adapter)
        self.assertIn('"v2_0_release_authorized": False', adapter)

    def test_prepared_hitcount_reuses_generic_witness_result(self) -> None:
        runtime = {
            "name": "fake",
            "slice": lambda value, count: value[:count],
            "sync": lambda: None,
            "count_unique_pairs_by_ids": _fake_count_unique_pairs_by_ids,
        }
        witness_result = {
            "runtime": runtime,
            "witness_ray_ids": _FakeColumn([101, 101, 102]),
            "witness_primitive_ids": _FakeColumn([11, 12, 12]),
            "emitted_count": 3,
            "metadata": {
                "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
                "prepared_scene_reused": True,
                "witness_output_columns_reused": True,
                "true_zero_copy_authorized": True,
                "v2_0_release_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }

        with mock.patch.object(
            partner_adapters,
            "_segment_polygon_all_witness_columns_optix_partner_columns",
            return_value=witness_result,
        ) as all_witness:
            result = rt.segment_polygon_hitcount_optix_prepared_partner_device_count_columns(
                object(),
                {"ids": _FakeColumn([101, 102, 103])},
                partner="torch",
                output_capacity=4,
                witness_output_columns={
                    "witness_ray_ids": _FakeColumn([0, 0, 0, 0]),
                    "witness_primitive_ids": _FakeColumn([0, 0, 0, 0]),
                },
                return_metadata=True,
            )

        self.assertTrue(all_witness.call_args.kwargs["prepared_scene"] is not None)
        self.assertEqual(result["columns"]["hit_counts"].values, [2, 1, 0])
        metadata = result["metadata"]
        self.assertEqual(metadata["adapter"], "segment_polygon_hitcount_optix_prepared_partner_device_count_columns")
        self.assertEqual(metadata["app_count_materialization"], "partner_gpu_from_prepared_generic_witness_pairs")
        self.assertTrue(metadata["prepared_scene_reused"])
        self.assertTrue(metadata["witness_output_columns_reused"])
        self.assertFalse(metadata["v2_0_release_authorized"])

    def test_prepared_road_hazard_thresholds_prepared_hit_counts(self) -> None:
        hitcount_result = {
            "columns": {
                "segment_ids": _FakeColumn([101, 102, 103]),
                "hit_counts": _FakeColumn([2, 1, 0]),
            },
            "metadata": {
                "adapter": "segment_polygon_hitcount_optix_prepared_partner_device_count_columns",
                "app_count_materialization": "partner_gpu_from_prepared_generic_witness_pairs",
                "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
                "v2_0_release_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }
        runtime = {
            "name": "torch",
            "sync": lambda: None,
            "greater_equal_uint32": lambda value, threshold: _FakeColumn(
                [1 if int(item) >= int(threshold) else 0 for item in value.values]
            ),
        }

        with mock.patch.object(partner_adapters, "_partner_module", return_value=runtime):
            with mock.patch.object(
                partner_adapters,
                "segment_polygon_hitcount_optix_prepared_partner_device_count_columns",
                return_value=hitcount_result,
            ):
                result = rt.road_hazard_priority_flags_optix_prepared_partner_device_columns(
                    object(),
                    {"ids": _FakeColumn([101, 102, 103])},
                    threshold=2,
                    partner="torch",
                    return_metadata=True,
                )

        self.assertEqual(result["columns"]["priority_flags"].values, [1, 0, 0])
        metadata = result["metadata"]
        self.assertEqual(metadata["adapter"], "road_hazard_priority_flags_optix_prepared_partner_device_columns")
        self.assertEqual(metadata["app_priority_materialization"], "partner_gpu_threshold_from_prepared_hit_counts")
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

    def test_report_keeps_pod_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: measured-with-boundary", report)
        self.assertIn("generic_ray_primitive_witness_pairs", report)
        self.assertIn("reusable witness output columns", report)
        self.assertIn("does not authorize broad RT-core speedup wording", report)
        self.assertIn("Speedup vs v1.8 prepared", report)

    def test_timing_runner_records_goal1886_prepared_reuse_rows(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("prepare_segment_polygon_anyhit_optix_partner_device_scene", runner)
        self.assertIn("allocate_segment_polygon_witness_partner_device_output_columns", runner)
        self.assertIn("segment_polygon_hitcount_optix_prepared_partner_device_count_columns", runner)
        self.assertIn("v2_0_prepared_partner_device_count_columns_", runner)
        self.assertIn("goal1886_prepared_reuse", runner)
        self.assertIn("query_median_ratio_vs_goal1863_unprepared_partner", runner)

    def test_pod_artifact_records_prepared_reuse_speedups_and_boundaries(self) -> None:
        artifact = json.loads(ARTIFACT_2048.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 2048)
        self.assertIn("NVIDIA GeForce RTX 3090", artifact["gpu"])
        prepared_baseline = artifact["prepared_baseline"]["query_summary"]["median_s"]
        for partner in ("cupy", "torch"):
            row = artifact["partners"][partner]["goal1886_prepared_reuse"]
            self.assertTrue(row["prepared_scene_reused"])
            self.assertTrue(row["witness_output_columns_reused"])
            self.assertLess(row["query_summary"]["median_s"], prepared_baseline)
            self.assertLess(row["query_median_ratio_vs_goal1863_unprepared_partner"], 1.0)
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(artifact["claim_boundary"]["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
