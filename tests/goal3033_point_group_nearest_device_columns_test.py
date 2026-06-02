from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3033PointGroupNearestDeviceColumnsTest(unittest.TestCase):
    def test_native_export_is_generic_and_split_kernel_is_device_column_only(self) -> None:
        symbol = "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns"
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        core = OPTIX_CORE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("split_point_group_nearest_columns", core)
        self.assertIn("g_point_group_nearest_split_columns", core)
        self.assertIn("write_prepared_point_group_nearest_witness_2d_device_columns_optix", workloads)
        self.assertIn("materializes", OPTIX_RUNTIME.read_text(encoding="utf-8"))
        for source in (api, prelude, core, workloads):
            self.assertNotIn("hausdorff", source.lower())
            self.assertNotIn("xhd", source.lower())

    def test_python_runtime_exposes_device_column_writer_with_closed_claims(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        class_block = source[
            source.index("class PreparedOptixPointGroupNearestWitness2D"):
            source.index("def prepare_optix_point_group_nearest_witness_2d")
        ]

        self.assertIn("def write_device_nearest_witness_columns", class_block)
        self.assertIn("_OPTIX_PREPARED_POINT_GROUP_NEAREST_WITNESS_2D_DEVICE_COLUMNS_SYMBOL", class_block)
        self.assertIn('"query_ids", query_ids_out, {"uint32"}', class_block)
        self.assertIn('"neighbor_ids", neighbor_ids_out, {"uint32"}', class_block)
        self.assertIn('"distances", distances_out, {"float64", "double"}', class_block)
        self.assertIn('"materializes_neighbor_rows": False', class_block)
        self.assertIn('"true_zero_copy_authorized": False', class_block)
        self.assertIn('"rt_core_speedup_claim_authorized": False', class_block)
        self.assertIn('"v2_6_release_authorized": False', class_block)

    def test_ctypes_binding_uses_void_p_for_partner_device_outputs(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        binding = source[
            source.index("optional_write_point_group_nearest_device_columns"):
            source.index("optional_reduce_point_group_nearest")
        ]

        self.assertIn("_OPTIX_PREPARED_POINT_GROUP_NEAREST_WITNESS_2D_DEVICE_COLUMNS_SYMBOL", binding)
        self.assertGreaterEqual(binding.count("ctypes.c_void_p"), 4)
        self.assertIn("optional_write_point_group_nearest_device_columns.restype = ctypes.c_int", binding)


if __name__ == "__main__":
    unittest.main()
