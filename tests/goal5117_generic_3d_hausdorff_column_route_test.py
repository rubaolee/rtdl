from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5117Generic3dHausdorffColumnRouteTest(unittest.TestCase):
    def test_public_3d_numpy_column_route_is_app_neutral(self) -> None:
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
        result = rt.directed_hausdorff_3d_numpy_columns(
            source_columns,
            target_columns,
            return_metadata=True,
        )
        metadata = result["metadata"]

        self.assertEqual(metadata["adapter"], "directed_hausdorff_3d_numpy_columns")
        self.assertEqual(metadata["partner_reference_contract"], "generic_group_argmin_then_global_argmax_with_witness")
        self.assertEqual(metadata["native_engine_row_contract"], "not_called_partner_reference_only")
        self.assertEqual(metadata["source_id"], 11)
        self.assertEqual(metadata["target_id"], 21)
        self.assertAlmostEqual(metadata["distance"], 2.0, delta=1e-12)
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertEqual(set(source_columns), {"ids", "x", "y", "z"})

    def test_public_3d_numpy_column_route_rejects_mismatched_columns(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "source ids/x/y/z must have the same shape"):
            rt.directed_hausdorff_3d_numpy_columns(
                {"ids": [0, 1], "x": [0.0, 1.0], "y": [0.0, 0.0], "z": [0.0]},
                {"ids": [10], "x": [0.0], "y": [0.0], "z": [0.0]},
            )

    def test_core_surface_contains_no_xhd_identity(self) -> None:
        import rtdsl
        from pathlib import Path

        root = Path(rtdsl.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        window = source[
            source.index("def point_rows_to_numpy_columns_3d") : source.index("def cupy_group_topk")
        ]

        self.assertIn("def directed_hausdorff_3d_numpy_columns", window)
        self.assertNotIn("xhd", window.lower())
        self.assertNotIn("x-hd", window.lower())
        self.assertNotIn("paper", window.lower())
        self.assertNotIn("hd_exec", window.lower())


if __name__ == "__main__":
    unittest.main()
