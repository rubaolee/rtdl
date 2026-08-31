from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4016_partition_convergence_typed_stream_contract_2026-06-08.md"


class Goal4016PartitionConvergenceTypedStreamContractTest(unittest.TestCase):
    def test_partition_convergence_summary_contract_has_required_columns(self) -> None:
        contract = rt.make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
            1024,
            64,
            512,
            data_ptrs={
                "point_partition_ids": 1000,
                "partition_point_ordinals": 1500,
                "near_pair_left_partition_ids": 2000,
                "near_pair_right_partition_ids": 3000,
                "near_pair_status": 4000,
                "row_count": 5000,
                "capacity": 6000,
                "overflow": 7000,
                "complete_candidate_coverage": 8000,
            },
        )
        metadata = contract.to_metadata()
        self.assertEqual(metadata["stream_kind"], "candidate_stream")
        self.assertEqual(metadata["producer_primitive"], "fixed_radius_partition_convergence_summary_3d")
        self.assertEqual(metadata["ordering"], "group_ordered")
        self.assertEqual(metadata["page_capacity"], 512)
        for name in (
            "point_partition_ids",
            "partition_point_ordinals",
            "occupied_partition_keys_x",
            "occupied_partition_keys_y",
            "occupied_partition_keys_z",
            "partition_offsets",
            "partition_counts",
            "partition_aabb_min_x",
            "partition_aabb_min_y",
            "partition_aabb_min_z",
            "partition_aabb_max_x",
            "partition_aabb_max_y",
            "partition_aabb_max_z",
            "near_pair_left_partition_ids",
            "near_pair_right_partition_ids",
            "near_pair_status",
        ):
            self.assertIn(name, metadata["column_names"])
        self.assertEqual(contract.column("partition_offsets").buffer.shape, (65,))
        self.assertEqual(contract.column("partition_point_ordinals").buffer.shape, (1024,))
        self.assertEqual(contract.column("near_pair_status").buffer.shape, (512,))
        self.assertGreaterEqual(metadata["device_resident_column_count"], 4)

    def test_contract_validates_and_remains_non_authorizing(self) -> None:
        contract = rt.make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
            128,
            16,
            64,
        )
        validation = rt.validate_typed_result_stream_contract(contract)
        self.assertEqual(validation["status"], "accept")
        metadata = contract.to_metadata()
        for flag in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "hidden_dispatch_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            self.assertFalse(metadata[flag])

    def test_invalid_sizes_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "point_count must be positive"):
            rt.make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(0, 1, 1)
        with self.assertRaisesRegex(ValueError, "partition_count must be positive"):
            rt.make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(1, 0, 1)
        with self.assertRaisesRegex(ValueError, "pair_capacity must be positive"):
            rt.make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(1, 1, 0)

    def test_source_and_report_are_app_agnostic_and_documented(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract",
            "fixed_radius_partition_convergence_summary_3d",
            "point_partition_ids",
            "partition_point_ordinals",
            "occupied_partition_keys",
            "near_pair_status",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)
        factory_source = source.split(
            "def make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract",
            1,
        )[1].split("def _unsupported_reason", 1)[0]
        forbidden = ("dbscan", "cluster", "epsilon", "min_points")
        lowered = factory_source.lower()
        for word in forbidden:
            self.assertNotIn(word, lowered)


if __name__ == "__main__":
    unittest.main()
