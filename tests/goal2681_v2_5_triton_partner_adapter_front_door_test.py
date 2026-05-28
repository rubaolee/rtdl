from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl import partner_adapters as adapters


ROOT = Path(__file__).resolve().parents[1]


class Goal2681V25TritonPartnerAdapterFrontDoorTest(unittest.TestCase):
    def test_source_routes_generic_adapter_front_doors_to_triton_continuations(self):
        source = (ROOT / "src/rtdsl/partner_adapters.py").read_text()

        self.assertIn('if partner == "triton":', source)
        self.assertIn("run_triton_partner_continuation", source)
        self.assertIn('"segmented_count_i64"', source)
        self.assertIn('"segmented_sum_f64"', source)
        self.assertIn('"segmented_min_f64"', source)
        self.assertIn('"segmented_max_f64"', source)
        self.assertIn('"compact_mask_i64"', source)
        self.assertIn('runtime["name"] in ("triton", "torch")', source)
        self.assertIn("Triton partner adapter requires torch CUDA tensors as the launch carrier", source)

    def test_public_api_exports_generic_adapter_front_doors(self):
        for name in (
            "partner_group_count_by_key",
            "partner_group_sum_by_key",
            "partner_metric_table_reduce_by_key",
            "metric_table_payload_to_partner_columns",
            "columnar_payload_to_partner_columns",
            "partner_columnar_predicate_reduce",
            "partner_columnar_predicate_reduce_batch",
            "partner_compact_columns_by_mask",
            "v2_5_triton_front_door_coverage",
            "V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS",
        ):
            self.assertIn(name, rt.__all__)

    def test_front_door_coverage_keeps_dispatcher_only_apps_explicit(self):
        coverage = rt.v2_5_triton_front_door_coverage()
        self.assertEqual(coverage["primary_partner"], "triton")
        self.assertEqual(coverage["benchmark_app_count"], 10)
        self.assertEqual(coverage["fully_front_door_ready_count"], 4)

        rows = {row["app_id"]: row for row in coverage["apps"]}
        self.assertEqual(rows["raydb_style"]["front_door_status"], "adapter_front_door_ready")
        self.assertEqual(rows["triangle_counting"]["front_door_status"], "adapter_front_door_ready")
        self.assertEqual(rows["barnes_hut"]["front_door_status"], "dispatcher_ready_app_wiring_required")
        self.assertIn("bounded_collect_finalize_i64", rows["barnes_hut"]["dispatcher_only_operations"])
        self.assertEqual(rows["contact_manifold"]["dispatcher_only_operations"], ("bounded_collect_finalize_i64",))
        self.assertEqual(rows["contact_manifold"]["missing_operations"], ())

    def test_no_cuda_environment_rejects_triton_front_door_explicitly(self):
        if rt.triton_partner_available():
            self.skipTest("CUDA Triton environment is available; executable checks cover this path")
        with self.assertRaises((ImportError, RuntimeError)):
            adapters.partner_group_count_by_key([], 0, partner="triton")

    def test_non_generic_aabb_payload_adapter_is_not_promoted_to_triton_front_door(self):
        source = (ROOT / "src/rtdsl/partner_adapters.py").read_text()

        self.assertIn("aabb pair payload columns are not a v2.5 Triton generic front door", source)
        self.assertIn("decompose through reviewed generic continuation operations first", source)

    def test_triton_front_door_matches_torch_baselines_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton adapter validation")
        import torch

        keys = torch.tensor([0, 2, 2, 0], dtype=torch.int64, device="cuda")
        values = torch.tensor([1.0, 2.0, 3.0, 4.0], dtype=torch.float64, device="cuda")

        counts = adapters.partner_group_count_by_key(keys, 3, partner="triton")
        sums = adapters.partner_group_sum_by_key(keys, values, 3, partner="triton")
        mins = adapters.partner_group_min_by_key(keys, values, 3, partner="triton", initial=99.0)
        maxes = adapters.partner_group_max_by_key(keys, values, 3, partner="triton", initial=-1.0)

        self.assertEqual(counts.detach().cpu().tolist(), [2, 0, 2])
        self.assertEqual(sums.detach().cpu().tolist(), [5.0, 0.0, 5.0])
        self.assertEqual(mins.detach().cpu().tolist(), [1.0, 99.0, 2.0])
        self.assertEqual(maxes.detach().cpu().tolist(), [4.0, -1.0, 3.0])

    def test_triton_compaction_and_columnar_predicate_front_door_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton adapter validation")
        import torch

        mask = torch.tensor([True, False, True, False], device="cuda")
        indices = adapters.partner_mask_indices(mask, partner="triton")
        self.assertEqual(indices.detach().cpu().tolist(), [0, 2])

        columns = adapters.columnar_payload_to_partner_columns(
            {
                "group": [0, 0, 1, 1],
                "value": [1.0, 2.0, 4.0, 8.0],
                "row_id": [10, 11, 12, 13],
            },
            partner="triton",
        )
        grouped_count = adapters.partner_columnar_predicate_reduce(
            columns,
            (("value", "ge", 2.0),),
            partner="triton",
            reduce="count",
            group_field="group",
            group_count=2,
        )
        grouped_sum = adapters.partner_columnar_predicate_reduce(
            columns,
            (("value", "ge", 2.0),),
            partner="triton",
            reduce="sum",
            group_field="group",
            value_field="value",
            group_count=2,
        )
        selected_ids = adapters.partner_columnar_predicate_reduce(
            columns,
            (("value", "ge", 2.0),),
            partner="triton",
            reduce="ids",
            value_field="row_id",
        )

        self.assertEqual(grouped_count.detach().cpu().tolist(), [1, 2])
        self.assertEqual(grouped_sum.detach().cpu().tolist(), [2.0, 12.0])
        self.assertEqual(selected_ids.detach().cpu().tolist(), [11, 12, 13])

    def test_triton_metric_table_reduce_requires_float64_values_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton adapter validation")
        import torch

        metric_keys = torch.tensor([10, 20, 10], dtype=torch.int64, device="cuda")
        output_metric_keys = torch.tensor([10, 20, 30], dtype=torch.int64, device="cuda")
        values = torch.tensor([1.5, 2.0, 2.5], dtype=torch.float64, device="cuda")
        reduced = adapters.partner_metric_table_reduce_by_key(
            metric_keys,
            values,
            output_metric_keys,
            partner="triton",
            reduce="sum",
        )
        self.assertEqual(reduced.detach().cpu().tolist(), [4.0, 2.0, 0.0])

        with self.assertRaisesRegex(ValueError, "float64"):
            adapters.partner_metric_table_reduce_by_key(
                metric_keys,
                values.to(torch.float32),
                output_metric_keys,
                partner="triton",
                reduce="sum",
            )


if __name__ == "__main__":
    unittest.main()
