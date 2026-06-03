from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3191_dense_grouped_count_device_columns_2026-06-03.md"


class Goal3191DenseGroupedCountDeviceColumnsTest(unittest.TestCase):
    def test_native_abi_exposes_generic_dense_grouped_count_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("RtdlNativeDeviceGroupedCountI64Columns", prelude)
        self.assertIn("counts_device_ptr", prelude)
        self.assertIn("group_capacity", prelude)
        self.assertIn(
            "rtdl_optix_columnar_device_payload_grouped_count_i64_device_columns_with_capacity",
            prelude,
        )
        self.assertIn("rtdl_optix_release_device_grouped_count_i64_columns", prelude)
        self.assertIn("run_device_column_grouped_count_i64_device_columns_optix_with_capacity", api)
        self.assertIn("NativeDeviceGroupedCountI64ColumnsOwner", workloads)
        self.assertIn("ensure_device_column_grouped_i64_pipeline()", workloads)
        self.assertIn("params.operation = kDeviceColumnGroupedOpCount", workloads)
        self.assertIn("columns_out->counts_device_ptr", workloads)

    def test_python_pair_column_front_door_keeps_dense_counts_resident(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("    def grouped_count_by_left_id_device_columns(")
        end = runtime.index("    def close(self) -> None:", start)
        body = runtime[start:end]

        self.assertIn(
            "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_DEVICE_COLUMNS_WITH_CAPACITY_SYMBOL",
            body,
        )
        self.assertIn("_RtdlNativeDeviceGroupedCountI64Columns", body)
        self.assertIn("OptixNativeDeviceGroupedCountI64Output", body)
        self.assertIn("self.left_ids_device_ptr", body)
        self.assertIn("_DEVICE_PAYLOAD_DTYPE_INT64", body)
        self.assertNotIn("rayjoin", body.lower())
        self.assertNotIn("intersection_point", body)

    def test_dense_output_metadata_and_cupy_view_are_bounded(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("class OptixNativeDeviceGroupedCountI64Output:")
        end = runtime.index("@dataclass\nclass OptixNativeDevicePairColumnOutput:", start)
        body = runtime[start:end]

        self.assertIn("device_resident_dense_grouped_count_column", body)
        self.assertIn("direct-address key capacity", body)
        self.assertIn("group_key_column_materialized_on_host", body)
        self.assertIn("count_column_materialized_on_host", body)
        self.assertIn("true_zero_copy_authorized", body)
        self.assertIn("cp.cuda.UnownedMemory", body)
        self.assertIn("dtype=cp.int64", body)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "dense direct-address grouped-count result",
            "does not add app-specific native logic",
            "reuses the existing grouped-count kernel",
            "keeps the dense `count[group_id]` column resident on CUDA",
            "group_capacity must exceed the maximum non-negative group key",
            "true_zero_copy_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
