import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2046_cupy_witness_continuation_surface_2026-05-14.md"
SOURCE = ROOT / "src" / "rtdsl" / "partner_continuations.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"

sys.path.insert(0, str(ROOT / "src"))


class Goal2046CuPyWitnessContinuationSurfaceTest(unittest.TestCase):
    def test_cupy_surface_is_exported(self):
        source = SOURCE.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        required = [
            "def cupy_group_topk",
            "def cupy_group_argmin_then_global_argmax_with_witness",
            "def directed_hausdorff_2d_cupy_columns",
        ]
        for phrase in required:
            self.assertIn(phrase, source)
        for name in [
            "cupy_group_topk",
            "cupy_group_argmin_then_global_argmax_with_witness",
            "directed_hausdorff_2d_cupy_columns",
        ]:
            self.assertIn(f"from .partner_continuations import {name}", init_text)
            self.assertIn(f'"{name}"', init_text)

    def test_cupy_runtime_matches_numpy_when_available(self):
        if importlib.util.find_spec("cupy") is None:
            self.skipTest("CuPy not installed on this host")

        import cupy
        import numpy as np
        import rtdsl as rt

        if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
            self.skipTest("No CUDA device for CuPy runtime test")

        numpy_result = rt.numpy_group_argmin_then_global_argmax_with_witness(
            group_ids=[0, 0, 1, 1, 2, 2],
            item_ids=[10, 11, 20, 21, 30, 31],
            values=[3.0, 1.0, 2.5, 2.0, 4.0, 5.0],
            group_count=3,
        )
        cupy_result = rt.cupy_group_argmin_then_global_argmax_with_witness(
            group_ids=cupy.asarray([0, 0, 1, 1, 2, 2]),
            item_ids=cupy.asarray([10, 11, 20, 21, 30, 31]),
            values=cupy.asarray([3.0, 1.0, 2.5, 2.0, 4.0, 5.0]),
            group_count=3,
        )
        self.assertEqual(cupy_result["group_id"], numpy_result["group_id"])
        self.assertEqual(cupy_result["item_id"], numpy_result["item_id"])
        self.assertAlmostEqual(cupy_result["value"], numpy_result["value"])

        source = {
            "ids": cupy.asarray([1, 2], dtype=cupy.int64),
            "x": cupy.asarray([0.0, 2.0], dtype=cupy.float64),
            "y": cupy.asarray([0.0, 0.0], dtype=cupy.float64),
        }
        target = {
            "ids": cupy.asarray([10, 11], dtype=cupy.int64),
            "x": cupy.asarray([0.0, 3.0], dtype=cupy.float64),
            "y": cupy.asarray([0.0, 0.0], dtype=cupy.float64),
        }
        result = rt.directed_hausdorff_2d_cupy_columns(source, target, return_metadata=True)
        self.assertEqual(result["metadata"]["partner_reference_contract"], "generic_group_argmin_then_global_argmax_with_witness")
        self.assertEqual(result["metadata"]["source_id"], 2)
        self.assertEqual(result["metadata"]["target_id"], 11)
        self.assertTrue(np.isclose(result["metadata"]["distance"], 1.0))

    def test_report_keeps_pod_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        required = [
            "no pod runtime evidence",
            "no OptiX zero-copy candidate-row handoff",
            "not make exact Hausdorff a large-scale v2.0 speedup claim",
            "does not solve exact facility K=3 ranking",
        ]
        for phrase in required:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
