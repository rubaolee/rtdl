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
TYPED = ROOT / "src" / "rtdsl" / "v2_8_geometry_relation_typed_stream.py"
REPORT = ROOT / "docs" / "reports" / "goal3185_segment_pair_candidate_device_columns_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3185_pod_segment_pair_candidate_device_columns_2026-06-03.json"


class Goal3185SegmentPairCandidateDeviceColumnsTest(unittest.TestCase):
    def test_native_surface_exports_generic_pair_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        for text in (prelude, api):
            self.assertIn("RtdlNativeDevicePairColumns", text)
            self.assertIn("rtdl_optix_prepared_segment_pair_candidate_device_columns", text)
            self.assertIn("rtdl_optix_release_segment_pair_candidate_device_columns", text)
        self.assertIn("left_ids_device_ptr", prelude)
        self.assertIn("right_ids_device_ptr", prelude)

        self.assertNotIn("rayjoin", prelude.lower())
        self.assertNotIn("rayjoin", api.lower())

    def test_candidate_kernel_writes_device_columns_not_host_rows(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("g_segment_pair_candidate_device_columns", core)
        self.assertIn("ensure_segment_pair_candidate_device_columns_pipeline", workloads)
        self.assertIn("segment_pair_candidate_device_columns_kernel.cu", workloads)
        self.assertIn("params.left_ids[slot] = (unsigned long long)left.id", workloads)
        self.assertIn("params.right_ids[slot] = (unsigned long long)right.id", workloads)
        self.assertIn("candidate_event_count", workloads)

        start = workloads.index("static void run_prepared_segment_pair_candidate_device_columns_optix")
        end = workloads.index("static void release_segment_pair_candidate_device_columns_optix", start)
        body = workloads[start:end]
        self.assertIn("NativeSegmentPairCandidateDeviceColumnsOwner", body)
        self.assertIn("RtdlNativeDevicePairColumns", body)
        self.assertNotIn("RtdlSegmentPairIntersectionRow", body)
        self.assertNotIn("finalize_segment_pair_intersection_rows", body)
        self.assertNotIn("download(gpu_rows", body)

    def test_python_runtime_exposes_raii_output_and_metadata(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("class _RtdlNativeDevicePairColumns", runtime)
        self.assertIn("class _OptixNativeDevicePairColumnsOwner", runtime)
        self.assertIn("class OptixNativeDevicePairColumnOutput", runtime)
        self.assertIn("def candidate_device_columns(", runtime)
        self.assertIn("OPTIX_SEGMENT_PAIR_CANDIDATE_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("geometry_relation_typed_stream_metadata_for_device_pair_columns", runtime)
        self.assertIn("exact_relation_witness_rows_materialized", runtime)
        self.assertIn("true_zero_copy_authorized", runtime)

    def test_typed_metadata_declares_candidate_columns_only(self) -> None:
        typed = TYPED.read_text(encoding="utf-8")

        self.assertIn("segment_pair_candidate_2d_device_columns", typed)
        self.assertIn("segment_pair_candidate_2d", typed)
        self.assertIn("device_resident_candidate_id_columns", typed)
        self.assertIn("geometry_relation_typed_stream_metadata_for_device_pair_columns", typed)
        self.assertIn("exact_relation_witness_rows_materialized", typed)
        self.assertIn('"true_zero_copy_claim_authorized": False', typed)

    def test_report_records_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "device-resident candidate ID columns",
            "not exact intersection witness rows",
            "single-launch first slice",
            "chunked append remains future work",
            "true_zero_copy_claim_authorized: False",
            "public_speedup_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifact_records_device_column_smoke(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["commit"], "32ab41a0")
        self.assertEqual(artifact["focused_tests"]["status"], "ok")
        smoke = artifact["live_smoke"]
        self.assertEqual(smoke["status"], "ok")
        self.assertEqual(smoke["exact_row_count"], 64)
        self.assertEqual(smoke["candidate_row_count"], 64)
        self.assertEqual(smoke["candidate_event_count"], 64)
        self.assertFalse(smoke["overflow"])
        self.assertTrue(smoke["device_resident"])
        self.assertEqual(smoke["stream_device_resident_column_count"], 2)

        for value in artifact["claim_boundary"].values():
            self.assertIs(value, False)


if __name__ == "__main__":
    unittest.main()
