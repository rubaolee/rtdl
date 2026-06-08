from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4017_partition_summary_reference_builder_2026-06-08.md"


class Goal4017PartitionSummaryReferenceBuilderTest(unittest.TestCase):
    def test_reference_builder_produces_expected_partition_columns(self) -> None:
        points = (
            rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=2, x=0.2, y=0.0, z=0.0),
            rt.Point3D(id=3, x=1.2, y=0.0, z=0.0),
            rt.Point3D(id=4, x=3.0, y=0.0, z=0.0),
        )
        result = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
        )
        columns = result["columns"]
        metadata = result["metadata"]

        self.assertEqual(columns["point_partition_ids"], (0, 0, 1, 2))
        self.assertEqual(columns["occupied_partition_keys_x"], (0, 2, 6))
        self.assertEqual(columns["occupied_partition_keys_y"], (0, 0, 0))
        self.assertEqual(columns["occupied_partition_keys_z"], (0, 0, 0))
        self.assertEqual(columns["partition_counts"], (2, 1, 1))
        self.assertEqual(columns["partition_offsets"], (0, 2, 3, 4))
        self.assertEqual(columns["near_pair_left_partition_ids"], (0, 0, 1, 2))
        self.assertEqual(columns["near_pair_right_partition_ids"], (0, 1, 1, 2))
        self.assertEqual(columns["near_pair_status"], (1, 2, 1, 1))
        self.assertEqual(metadata["status_counts"]["safe_full_partition_pairs"], 3)
        self.assertEqual(metadata["status_counts"]["ambiguous_partition_pairs"], 1)
        self.assertFalse(metadata["overflow"])
        self.assertEqual(metadata["typed_result_stream"]["producer_primitive"], "fixed_radius_partition_convergence_summary_3d")

    def test_reference_builder_records_overflow_without_silent_promotion(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (3.0, 0.0, 0.0),
        )
        result = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=2,
        )
        columns = result["columns"]
        metadata = result["metadata"]
        self.assertTrue(metadata["overflow"])
        self.assertEqual(metadata["pair_count"], 4)
        self.assertEqual(metadata["visible_pair_count"], 2)
        self.assertEqual(columns["near_pair_left_partition_ids"], (0, 0))
        self.assertEqual(columns["near_pair_right_partition_ids"], (0, 1))
        self.assertEqual(columns["near_pair_status"], (1, 2))
        self.assertFalse(metadata["native_abi_added"])
        self.assertFalse(metadata["runtime_executable"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_reference_builder_fails_closed_on_invalid_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "point_rows must contain at least one point"):
            rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d((), radius=1.0)
        with self.assertRaisesRegex(ValueError, "radius must be positive"):
            rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(((0, 0, 0),), radius=0.0)
        with self.assertRaisesRegex(ValueError, "cell_factor must be positive"):
            rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
                ((0, 0, 0),),
                radius=1.0,
                cell_factor=0.0,
            )
        with self.assertRaisesRegex(ValueError, "pair_capacity must be positive"):
            rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
                ((0, 0, 0),),
                radius=1.0,
                pair_capacity=0,
            )

    def test_source_and_report_record_reference_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "build_v2_8_fixed_radius_partition_convergence_summary_reference_3d",
            "python_reference",
            "near_pair_status",
            "safe-full",
            "ambiguous",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
