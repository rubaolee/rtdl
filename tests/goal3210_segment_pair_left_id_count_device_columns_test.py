from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"


class Goal3210SegmentPairLeftIdCountDeviceColumnsTest(unittest.TestCase):
    def test_native_abi_exposes_generic_segment_pair_count_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        symbol = "rtdl_optix_prepared_segment_pair_left_id_count_device_columns"
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("run_prepared_segment_pair_left_id_count_device_columns_optix", api)
        self.assertIn("run_prepared_segment_pair_left_id_count_device_columns_optix", workloads)
        self.assertIn("SegmentPairLeftIdCountDeviceColumnsLaunchParams", workloads)
        self.assertIn("g_segment_pair_left_id_count_device_columns", core)
        self.assertIn("segment_pair_left_id_count_device_columns_kernel.cu", workloads)
        self.assertIn("atomicAdd(&params.counts[left.id], 1ull)", workloads)

        combined_native = "\n".join((prelude, api, workloads, core)).lower()
        self.assertNotIn("rayjoin", combined_native)
        self.assertNotIn("spatial_join", combined_native)

    def test_python_runtime_front_door_returns_dense_count_output(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("OPTIX_SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("left_id_count_device_columns", runtime)
        self.assertIn("Count segment-pair hits by pair-column left_id", runtime)
        self.assertIn("OptixNativeDeviceGroupedCountI64Output", runtime)
        self.assertIn("_RtdlNativeDeviceGroupedCountI64Columns", runtime)
        self.assertIn("group_capacity must be positive", runtime)
        self.assertIn("OPTIX_SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertNotIn("rtdl_optix_rayjoin", runtime)

    def test_ctypes_signature_is_registered_as_optional_symbol(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("optional_segment_pair_left_id_count_device_columns")
        end = runtime.index("optional_run_prepared_segment_first_hit", start)
        body = runtime[start:end]

        self.assertIn("ctypes.POINTER(_RtdlSegment)", body)
        self.assertIn("ctypes.POINTER(_RtdlNativeDeviceGroupedCountI64Columns)", body)
        self.assertIn("ctypes.c_size_t", body)
        self.assertIn("restype = ctypes.c_int", body)


if __name__ == "__main__":
    unittest.main()
