from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3271_closed_shape_membership_point_id_count_device_columns_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3271_pod_closed_shape_point_id_count_device_columns_smoke_2026-06-03.json"


class Goal3271ClosedShapeMembershipPointIdCountDeviceColumnsTest(unittest.TestCase):
    def test_native_surface_exports_generic_grouped_count_continuation(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        symbol = "rtdl_optix_prepared_point_closed_shape_membership_point_id_count_device_columns_2d"

        for text in (prelude, api):
            self.assertIn(symbol, text)
            self.assertIn("RtdlNativeDeviceGroupedCountI64Columns", text)
            self.assertNotIn("rayjoin", text.lower())

    def test_kernel_counts_by_point_id_without_candidate_or_host_rows(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("g_pip_point_id_count_device_columns", core)
        self.assertIn("ensure_pip_point_id_count_device_columns_pipeline", workloads)
        self.assertIn("point_closed_shape_point_id_count_device_columns_kernel.cu", workloads)
        self.assertIn("const uint32_t group_key = params.point_ids[pidx]", workloads)
        self.assertIn("atomicAdd(params.counts + group_key, 1ull)", workloads)

        start = workloads.index("static void run_prepared_point_closed_shape_membership_point_id_count_device_columns_2d_optix")
        end = workloads.index("struct ShapePairRelationFlagComputation", start)
        body = workloads[start:end]
        self.assertIn("NativeDeviceGroupedCountI64ColumnsOwner", body)
        self.assertNotIn("RtdlPointClosedShapeMembershipRow", body)
        self.assertNotIn("RtdlNativeDevicePairColumns", body)
        self.assertNotIn("download(chunk_rows", body)
        self.assertNotIn("exact_point_in_polygon", body)
        self.assertNotIn("rayjoin", body.lower())

    def test_python_runtime_exposes_device_resident_count_output(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_POINT_ID_COUNT_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("def point_id_count_device_columns(", runtime)
        self.assertIn("OptixNativeDeviceGroupedCountI64Output", runtime)
        self.assertIn("group_capacity must be positive", runtime)
        self.assertIn("direct-address key capacity", runtime)

    def test_report_records_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "device-resident grouped count column",
            "keyed by caller point ID",
            "no candidate pair array is materialized",
            "RayJoin-specific native logic added: false",
            "release authorized: false",
            "true zero-copy claim authorized: false",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifact_records_live_grouped_count_smoke(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3271)
        self.assertEqual(data["build"]["status"], "passed")
        self.assertEqual(data["focused_unittest_slice"]["status"], "passed")
        smoke = data["live_smoke"]
        self.assertEqual(smoke["status"], "ok")
        self.assertEqual(smoke["exact_device_filtered_count"], 2)
        self.assertEqual(smoke["source_row_count"], 2)
        self.assertFalse(smoke["overflow"])
        self.assertTrue(smoke["device_resident"])
        self.assertEqual(smoke["group_capacity"], 64)
        self.assertEqual(smoke["selected_counts"], {"10": 1, "20": 1, "30": 0})
        self.assertEqual(smoke["metadata_schema"], "device_grouped_count_i64_dense_columns")
        self.assertEqual(smoke["metadata_output_residency"], "device_resident_dense_grouped_count_column")
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_specific_native_logic_added"])


if __name__ == "__main__":
    unittest.main()
