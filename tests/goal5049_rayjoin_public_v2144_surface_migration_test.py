from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class _FakeCudaColumn:
    dtype = "int64"

    def __init__(self, length: int, ptr: int, typestr: str) -> None:
        self.shape = (int(length),)
        self._ptr = int(ptr)
        self._typestr = str(typestr)

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.indices(self.shape[0])
            if step != 1:
                raise ValueError("test fake supports contiguous slices only")
            return _FakeCudaColumn(max(0, stop - start), self._ptr + start * 8, self._typestr)
        raise TypeError("test fake only supports slicing")

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": self._typestr,
            "data": (self._ptr, False),
            "version": 3,
            "device": 0,
        }


def _load_app_module():
    module_name = "goal5049_section57_overlay_columnar_binary"
    sys.path.insert(0, str(APP.parent))
    spec = importlib.util.spec_from_file_location(module_name, APP)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class Goal5049RayJoinPublicV2144SurfaceMigrationTest(unittest.TestCase):
    def test_native_lexsort_route_uses_public_device_order_by_surface(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("from rtdsl import device_column_buffer", source)
        self.assertIn("from rtdsl import device_order_by", source)
        self.assertIn("def _run_public_device_order_by_native_lexsort", source)
        self.assertIn("public_device_order_by_used", source)
        self.assertNotIn("from rtdsl import optix_runtime", source)
        self.assertNotIn("optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device", source)

    def test_public_order_by_helper_slices_to_valid_count_and_records_metadata(self) -> None:
        module = _load_app_module()
        edge = _FakeCudaColumn(8, 0x504900, "<i8")
        dist = _FakeCudaColumn(8, 0x504980, "<f8")
        tie = _FakeCudaColumn(8, 0x504A00, "<i8")
        order = _FakeCudaColumn(8, 0x504A80, "<i8")

        def fake_order_by(buffer, *, keys, backend):
            self.assertEqual(("edge_key", "dist_key", "tie_key", "order_key"), tuple(keys))
            self.assertEqual("native_cuda", backend)
            self.assertEqual(3, buffer.row_count)
            self.assertEqual("section57_sort_test", buffer.producer)
            self.assertTrue(buffer.device_resident_candidate)
            return mock.Mock(
                metadata={
                    "backend": "native_thrust_lexsort_i64_f64_i64_i64",
                    "public_device_order_by_contract_version": "rtdl.device_order_by.v2_14_4.public.v1",
                }
            )

        with mock.patch.object(module, "device_order_by", side_effect=fake_order_by):
            metadata = module._run_public_device_order_by_native_lexsort(
                edge,
                dist,
                tie,
                order,
                count=3,
                producer="section57_sort_test",
            )

        self.assertTrue(metadata["public_device_order_by_used"])
        self.assertEqual(
            "rtdl.device_order_by.v2_14_4.public.v1",
            metadata["public_device_order_by_contract_version"],
        )

    def test_migration_is_api_surface_only_not_a_new_performance_claim(self) -> None:
        source = APP.read_text(encoding="utf-8")
        helper = source.split("def _run_public_device_order_by_native_lexsort", 1)[1].split(
            "def sort_xsect_indices_for_map_numba_device",
            1,
        )[0]

        self.assertNotIn("rayjoin_overlay", helper)
        self.assertNotIn("output_chain", helper.lower())
        self.assertNotIn("authorofficial", helper.lower())
        self.assertNotIn("speedup", helper.lower())


if __name__ == "__main__":
    unittest.main()
