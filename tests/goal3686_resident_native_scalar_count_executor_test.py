from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class Goal3686ResidentNativeScalarCountExecutorTest(unittest.TestCase):
    def test_executor_abi_symbols_are_generic(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        symbols = (
            "rtdl_optix_prepare_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d",
            "rtdl_optix_run_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d",
            "rtdl_optix_destroy_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d",
        )
        for symbol in symbols:
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
            for forbidden in ("rayjoin", "cdb", "county"):
                self.assertNotIn(forbidden, symbol.lower())

    def test_native_executor_reuses_counter_and_param_buffers(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        start = workloads.index("struct PreparedPointClosedShapeRelationStatusCorrectedScalarCountExecutor2D")
        end = workloads.index("static void count_prepared_point_closed_shape_membership_device_filtered", start)
        body = workloads[start:end]
        self.assertIn("DevPtr d_exact_count", body)
        self.assertIn("DevPtr d_candidate_count", body)
        self.assertIn("DevPtr d_boundary_candidate_count", body)
        self.assertIn("DevPtr d_dropped_candidate_count", body)
        self.assertIn("DevPtr d_params", body)
        self.assertIn("cuMemsetD32Async(d_exact_count.ptr", body)
        self.assertIn("run(RtdlNativeClosedShapeScalarCountSummary* summary_out)", body)
        self.assertNotIn("point_ids_out", body)
        self.assertNotIn("shape_ids_out", body)
        for forbidden in ("rayjoin", "cdb", "county"):
            self.assertNotIn(forbidden, body.lower())

    def test_python_executor_front_door_and_harness_metadata(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        script = (ROOT / "scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("PreparedOptixRelationStatusCorrectedScalarCountExecutor2D", runtime)
        self.assertIn("prepare_relation_status_corrected_scalar_count_executor", runtime)
        self.assertIn("reusable_native_executor_used", runtime)
        self.assertIn("resident_native_relation_status_corrected_exact_scalar_count", script)
        self.assertIn("prepare_resident_native_executor_sec", script)
        self.assertIn('"public_speedup_claim_authorized": False', script)
        self.assertIn('"true_zero_copy_claim_authorized": False', script)


if __name__ == "__main__":
    unittest.main()
