from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_aabb_index_3d_point_membership_gate.py"
    spec = importlib.util.spec_from_file_location("run_aabb_index_3d_point_membership_gate", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load 3D AABB point-membership gate runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5146OptixAabbIndex3DPointMembershipTest(unittest.TestCase):
    def test_native_symbols_are_declared_and_generic(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")

        for text in (prelude, api):
            self.assertIn("rtdl_optix_prepare_aabb_index_3d", text)
            self.assertIn("rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows", text)
            self.assertIn("rtdl_optix_destroy_prepared_aabb_index_3d", text)
        self.assertIn("prepare_aabb_index_3d_optix", workloads)
        self.assertIn("collect_prepared_aabb_index_3d_point_contains_rows_optix", workloads)
        self.assertIn("PreparedAabbIndex3DOptix", workloads)

        start = workloads.index("struct GpuAabb3D")
        end = workloads.index("static void ensure_pack_triangle2d_device_columns_kernel")
        generic_window = workloads[start:end].lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec"):
            self.assertNotIn(forbidden, generic_window)

    def test_python_wrapper_exports_generic_3d_aabb_route(self) -> None:
        import rtdsl as rt
        from rtdsl import optix_runtime

        self.assertIn("prepare_optix_aabb_index_3d", rt.__all__)
        self.assertIn("collect_aabb_point_membership_pair_rows_3d_optix", rt.__all__)
        self.assertTrue(hasattr(rt, "prepare_optix_aabb_index_3d"))
        self.assertTrue(hasattr(rt, "collect_aabb_point_membership_pair_rows_3d_optix"))

        packed = optix_runtime.pack_aabbs_3d([(7, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0)])
        self.assertEqual(packed.count, 1)
        self.assertEqual(packed.records[0].id, 7)
        self.assertEqual(packed.records[0].max_z, 3.0)

    def test_pack_aabbs_3d_rejects_reversed_bounds(self) -> None:
        from rtdsl import optix_runtime

        with self.assertRaisesRegex(ValueError, "3D AABB max bounds"):
            optix_runtime.pack_aabbs_3d([(0.0, 0.0, 0.0, -1.0, 1.0, 1.0)])

    def test_gate_runner_fixture_expected_rows_are_discriminating(self) -> None:
        runner = _load_runner()
        boxes, points = runner._fixture()
        rows = runner._expected_rows(boxes, points)
        self.assertEqual(rows, [[100, 10], [101, 10], [101, 11], [102, 11], [103, 12]])


if __name__ == "__main__":
    unittest.main()
