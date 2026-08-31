from __future__ import annotations

import pathlib
import unittest
import json


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3684_native_relation_status_corrected_scalar_count_2026-06-07.md"
ARTIFACT = ROOT / "docs/reports/goal3684_native_relation_status_corrected_scalar_count_a5000/summary.json"


class Goal3684NativeRelationStatusCorrectedScalarCountTest(unittest.TestCase):
    def test_native_symbol_and_summary_contract_are_generic(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        symbol = (
            "rtdl_optix_count_prepared_point_closed_shape_membership_"
            "relation_status_corrected_prepared_points_2d"
        )
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("RtdlNativeClosedShapeScalarCountSummary", prelude)
        self.assertIn("boundary_candidate_event_count", prelude)
        self.assertIn("dropped_candidate_event_count", prelude)
        for forbidden in ("rayjoin", "cdb", "county"):
            self.assertNotIn(forbidden, symbol.lower())

    def test_optix_path_uses_native_double_lookup_without_boundary_rows(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        start = workloads.index("static void ensure_pip_relation_status_corrected_scalar_count_pipeline")
        end = workloads.index("static void ensure_pip_point_id_count_device_columns_pipeline", start)
        body = workloads[start:end]
        self.assertIn("exact_boundary_contact_f64", body)
        self.assertIn("points_x_f64", body)
        self.assertIn("vertices_x_f64", body)
        self.assertIn("atomicAdd(params.candidate_count, 1u)", body)
        self.assertIn("atomicAdd(params.boundary_candidate_count, 1u)", body)
        self.assertIn("atomicAdd(params.dropped_candidate_count, 1u)", body)
        self.assertIn("point_closed_shape_relation_status_corrected_scalar_count_kernel.cu", body)
        self.assertNotIn("point_ids_out", body)
        self.assertNotIn("shape_ids_out", body)
        for forbidden in ("rayjoin", "cdb", "county"):
            self.assertNotIn(forbidden, body.lower())

    def test_prepared_handles_keep_float_traversal_and_double_correction_columns(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        shape_start = workloads.index("struct PreparedShapePairRelationBuild")
        shape_end = workloads.index("struct NativeShapePairRelationDeviceColumnsOwner", shape_start)
        point_start = workloads.index("struct PreparedPointProbeColumns2D")
        point_end = workloads.index("static PreparedShapePairRelationBuild*", point_start)
        shape_body = workloads[shape_start:shape_end]
        point_body = workloads[point_start:point_end]
        self.assertIn("std::vector<float> right_vx", shape_body)
        self.assertIn("std::vector<double> right_vx_f64", shape_body)
        self.assertIn("DevPtr d_right_vx_f64", shape_body)
        self.assertIn("std::vector<float> points_x", point_body)
        self.assertIn("std::vector<double> points_x_f64", point_body)
        self.assertIn("DevPtr d_points_x_f64", point_body)

    def test_python_front_door_and_timing_harness_are_non_authorizing(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        script = (ROOT / "scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("count_relation_status_corrected_prepared_points_native", runtime)
        self.assertIn("native_exact_device_scalar_count_produced", runtime)
        self.assertIn("boundary_candidate_row_stream_materialized", runtime)
        self.assertIn("native_relation_status_corrected_exact_scalar_count", script)
        self.assertIn('"public_speedup_claim_authorized": False', script)
        self.assertIn('"true_zero_copy_claim_authorized": False', script)
        self.assertIn('"native_default_route_authorized": False', script)

    def test_report_and_artifact_record_exact_native_scalar_count(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("native relation-status corrected exact scalar count", report)
        self.assertIn("does not authorize", report)
        self.assertTrue(artifact["correctness"]["native_all_match_exact_count"])
        self.assertEqual(artifact["correctness"]["native_corrected_count"], 47262)
        self.assertEqual(artifact["correctness"]["exact_count"], 47262)
        native = artifact["timings"]["native_relation_status_corrected_exact_scalar_count"]
        resident = artifact["timings"]["resident_relation_status_corrected_exact_numba_count"]
        self.assertEqual(native["stability_value"], 47262)
        self.assertLess(native["hot_median_sec"], resident["hot_median_sec"])
        self.assertFalse(
            native["runs"][-1]["boundary_candidate_row_stream_materialized"],
            "native scalar correction must not materialize dense boundary rows",
        )
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
