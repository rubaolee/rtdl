from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5127XhdGenericNearestPipelineExtractionTest(unittest.TestCase):
    def test_directed_hd_result_is_composable_from_generic_nearest_pipeline(self) -> None:
        import rtdsl as rt
        from rtdsl.reference import Point3D

        source = (
            Point3D(id=10, x=0.0, y=0.0, z=0.0),
            Point3D(id=11, x=3.0, y=0.0, z=0.0),
        )
        target = (
            Point3D(id=20, x=0.0, y=0.0, z=0.0),
            Point3D(id=21, x=1.0, y=0.0, z=0.0),
        )
        source_columns = rt.point_rows_to_numpy_columns_3d(source)
        target_columns = rt.point_rows_to_numpy_columns_3d(target)

        candidates = rt.pairwise_l2_distance_candidate_rows_numpy_columns(
            source_columns,
            target_columns,
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )
        candidate_rows = candidates["candidate_rows"]
        self.assertEqual(candidates["metadata"]["contract"], "generic_pairwise_l2_distance_candidate_rows")
        self.assertEqual(candidates["metadata"]["app_semantics"], "none")
        self.assertEqual(candidate_rows.query_ids.tolist(), [0, 0, 1, 1])
        self.assertEqual(candidate_rows.primitive_ids.tolist(), [20, 21, 20, 21])
        self.assertEqual(candidate_rows.values.tolist(), [0.0, 1.0, 3.0, 2.0])

        nearest = rt.nearest_witness_numpy_columns(
            candidate_rows,
            candidates["source_ids"],
            return_metadata=True,
        )
        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_columns")
        self.assertEqual(nearest["columns"]["source_ids"].tolist(), [10, 11])
        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [20, 21])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [0.0, 2.0])

        witness = rt.max_nearest_distance_witness_numpy_columns(
            nearest["columns"],
            group_ids=nearest["per_group_argmin"]["group_ids"],
            return_metadata=True,
        )
        self.assertEqual(witness["metadata"]["contract"], "generic_max_nearest_distance_with_witness")
        self.assertEqual(witness["source_id"], 11)
        self.assertEqual(witness["item_id"], 21)
        self.assertAlmostEqual(witness["value"], 2.0, delta=1e-12)

        wrapper = rt.directed_hausdorff_3d_numpy_columns(
            source_columns,
            target_columns,
            return_metadata=True,
        )
        self.assertEqual(wrapper["metadata"]["source_id"], witness["source_id"])
        self.assertEqual(wrapper["metadata"]["target_id"], witness["item_id"])
        self.assertAlmostEqual(wrapper["metadata"]["distance"], witness["value"], delta=1e-12)
        self.assertIn("pairwise_l2_distance_candidate_rows", wrapper["metadata"]["generic_pipeline_contract"])

    def test_generic_nearest_pipeline_surface_is_app_neutral(self) -> None:
        import rtdsl

        root = Path(rtdsl.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def pairwise_l2_distance_candidate_rows_numpy_columns")
        end = source.index("def directed_hausdorff_2d_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("def nearest_witness_numpy_columns", generic_window)
        self.assertIn("def max_nearest_distance_witness_numpy_columns", generic_window)
        self.assertNotIn("xhd", generic_window)
        self.assertNotIn("x-hd", generic_window)
        self.assertNotIn("paper", generic_window)
        self.assertNotIn("hd_exec", generic_window)

    def test_pairwise_candidate_rows_reject_bad_dimension_contract(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "coordinate_fields must contain at least one"):
            rt.pairwise_l2_distance_candidate_rows_numpy_columns(
                {"ids": [0], "x": [0.0]},
                {"ids": [1], "x": [1.0]},
                coordinate_fields=(),
            )
        with self.assertRaisesRegex(ValueError, "source ids/x/z must have the same shape"):
            rt.pairwise_l2_distance_candidate_rows_numpy_columns(
                {"ids": [0, 1], "x": [0.0, 1.0], "z": [0.0]},
                {"ids": [10], "x": [0.0], "z": [0.0]},
                coordinate_fields=("x", "z"),
            )


if __name__ == "__main__":
    unittest.main()
