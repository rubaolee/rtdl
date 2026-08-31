from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3193_compact_grouped_count_device_columns_2026-06-03.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json"


class Goal3193CompactGroupedCountDeviceColumnsTest(unittest.TestCase):
    def test_native_abi_exposes_compact_grouped_count_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("RtdlNativeDeviceGroupedCountI64CompactColumns", prelude)
        self.assertIn("group_keys_device_ptr", prelude)
        self.assertIn("counts_device_ptr", prelude)
        self.assertIn(
            "rtdl_optix_columnar_device_payload_grouped_count_i64_compact_device_columns_with_capacity",
            prelude,
        )
        self.assertIn("rtdl_optix_release_device_grouped_count_i64_compact_columns", prelude)
        self.assertIn("run_device_column_grouped_count_i64_compact_device_columns_optix_with_capacity", api)
        self.assertIn("NativeDeviceGroupedCountI64CompactColumnsOwner", workloads)
        self.assertIn("device_column_grouped_i64_compact_count_columns_kernel", workloads)
        self.assertIn("compact_count_columns_fn", workloads)
        self.assertIn("columns_out->group_keys_device_ptr", workloads)
        self.assertIn("columns_out->counts_device_ptr", workloads)

    def test_python_front_door_returns_compact_resident_columns(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("    def grouped_count_by_left_id_compact_device_columns(")
        end = runtime.index("    def close(self) -> None:", start)
        body = runtime[start:end]

        self.assertIn(
            "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_COMPACT_DEVICE_COLUMNS_WITH_CAPACITY_SYMBOL",
            body,
        )
        self.assertIn("_RtdlNativeDeviceGroupedCountI64CompactColumns", body)
        self.assertIn("OptixNativeDeviceGroupedCountI64CompactOutput", body)
        self.assertIn("self.left_ids_device_ptr", body)
        self.assertIn("_DEVICE_PAYLOAD_DTYPE_INT64", body)
        self.assertNotIn("rayjoin", body.lower())
        self.assertNotIn("intersection_point", body)

    def test_compact_output_metadata_and_cupy_views_are_bounded(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("class OptixNativeDeviceGroupedCountI64CompactOutput:")
        end = runtime.index("@dataclass\nclass OptixNativeDevicePairColumnOutput:", start)
        body = runtime[start:end]

        self.assertIn("device_resident_compact_grouped_count_columns", body)
        self.assertIn("row_count_materialized_on_host", body)
        self.assertIn("group_key_column_materialized_on_host", body)
        self.assertIn("count_column_materialized_on_host", body)
        self.assertIn("cp.cuda.UnownedMemory", body)
        self.assertIn("as_cupy_group_keys", body)
        self.assertIn("as_cupy_counts", body)
        self.assertIn("true_zero_copy_authorized", body)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "compact grouped-count device columns",
            "does not add app-specific native logic",
            "reuses the existing grouped-count kernel",
            "adds only a generic compact-count-columns kernel",
            "group_key[] and count[] stay resident on CUDA",
            "row count scalar is materialized on host",
            "true_zero_copy_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifact_records_compact_device_count_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3193)
        self.assertEqual(data["focused_unittest_slice"]["status"], "passed")
        self.assertTrue(data["live_smoke"]["all_match_exact_rows"])
        self.assertTrue(data["live_smoke"]["compact_count_result_device_resident"])
        self.assertEqual(data["live_smoke"]["compact_columns"]["schema"], "device_grouped_count_i64_compact_columns")
        self.assertEqual(
            data["live_smoke"]["compact_columns"]["output_residency"],
            "device_resident_compact_grouped_count_columns",
        )
        self.assertEqual(data["live_smoke"]["compact_columns"]["row_count"], 16)
        self.assertEqual(data["live_smoke"]["compact_group_key_view_shape"], [16])
        self.assertEqual(data["live_smoke"]["compact_count_view_shape"], [16])
        self.assertEqual(data["live_smoke"]["compact_group_key_view_dtype"], "int64")
        self.assertEqual(data["live_smoke"]["compact_count_view_dtype"], "int64")
        self.assertFalse(data["live_smoke"]["compact_columns"]["group_key_column_materialized_on_host"])
        self.assertFalse(data["live_smoke"]["compact_columns"]["count_column_materialized_on_host"])
        self.assertTrue(data["live_smoke"]["compact_columns"]["row_count_materialized_on_host"])
        self.assertTrue(data["negative_probe"]["group_capacity_64_overflow"])
        self.assertFalse(data["negative_probe"]["group_capacity_64_device_resident"])
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_specific_native_logic_added"])


if __name__ == "__main__":
    unittest.main()
