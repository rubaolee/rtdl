from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
APP = ROOT / "examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
REPORT = ROOT / "docs/reports/goal3737_shape_pair_active_count_executor_and_rayjoin_perf_2026-06-07.md"
DIRECT_ARTIFACT = ROOT / "docs/reports/goal3737_shape_pair_active_count_executor_direct_a5000/summary.json"
COMPOSITE_BEFORE = (
    ROOT / "docs/reports/goal3737_rayjoin_safe_mixed_prepared_left_cross_size_a5000/summary.json"
)
COMPOSITE_AFTER = ROOT / "docs/reports/goal3737_rayjoin_safe_mixed_executor_cross_size_a5000/summary.json"


class Goal3737ShapePairActiveCountExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.app = APP.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_native_executor_abi_is_generic(self) -> None:
        symbols = (
            "rtdl_optix_prepare_shape_pair_relation_active_device_prepared_left_executor",
            "rtdl_optix_run_shape_pair_relation_active_device_prepared_left_executor",
            "rtdl_optix_destroy_shape_pair_relation_active_device_prepared_left_executor",
        )
        for symbol in symbols:
            self.assertIn(symbol, self.prelude)
            self.assertIn(symbol, self.api)
        for forbidden in ("RayJoin", "county", "soil", "overlay_seed"):
            executor_block = self.workloads.split(
                "struct PreparedShapePairRelationActiveCountPreparedLeftExecutor",
                1,
            )[1].split("struct NativeShapePairRelationDeviceColumnsOwner", 1)[0]
            self.assertNotIn(forbidden, executor_block)

    def test_native_executor_reuses_buffers_and_params(self) -> None:
        block = self.workloads.split(
            "struct PreparedShapePairRelationActiveCountPreparedLeftExecutor",
            1,
        )[1].split("struct NativeShapePairRelationDeviceColumnsOwner", 1)[0]
        self.assertIn("DevPtr d_output", block)
        self.assertIn("DevPtr d_active_count", block)
        self.assertIn("DevPtr d_params", block)
        self.assertIn("upload(d_params.ptr, &params, 1)", block)
        self.assertIn("reset_shape_pair_relation_phase_timings(6u)", block)
        self.assertIn("optixLaunch", block)

    def test_python_runtime_and_app_use_executor_front_door(self) -> None:
        for token in (
            "PreparedOptixShapePairRelationActiveCountPreparedLeftExecutor",
            "prepare_active_count_prepared_left_executor",
            "active_count_device_continuation_prepared_left_executor",
            "OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_RUN_SYMBOL",
        ):
            self.assertIn(token, self.runtime)
        run_block = self.app.split("def run_packed_left_device_continuation", 1)[1].split(
            "def active_relation_device_columns",
            1,
        )[0]
        self.assertIn("prepare_active_count_prepared_left_executor", run_block)
        self.assertIn("executor.run", run_block)
        self.assertIn("timed_query_uses_executor_run", run_block)
        self.assertIn("RayJoin overlay-seed interpretation", run_block)

    def test_a5000_direct_artifact_records_executor_mode_and_speed(self) -> None:
        payload = json.loads(DIRECT_ARTIFACT.read_text(encoding="utf-8"))
        rows = {int(row["count"]): row for row in payload["rows"]}
        self.assertEqual(set(rows), {1024, 2048, 4096})
        row4096 = rows[4096]
        self.assertEqual(row4096["row_count"], 4250)
        self.assertEqual(
            row4096["native_phase_timings"]["mode"],
            "active_count_device_continuation_prepared_left_executor",
        )
        self.assertEqual(row4096["native_phase_timings"]["left_upload"], 0.0)
        self.assertLess(row4096["phases_sec"]["prepared_query_sec"], 0.0017)
        self.assertTrue(row4096["prepared_active_count_executor"]["reusable_native_executor"])
        for key, value in payload["claim_boundary"].items():
            if key.endswith("_authorized"):
                self.assertFalse(value, key)

    def test_cross_size_composite_improves_after_executor(self) -> None:
        before = json.loads(COMPOSITE_BEFORE.read_text(encoding="utf-8"))
        after = json.loads(COMPOSITE_AFTER.read_text(encoding="utf-8"))
        self.assertTrue(after["summary"]["all_counts_match"])
        self.assertGreater(
            after["summary"]["geomean_recommended_safe_mixed_speedup_vs_all_cupy"],
            before["summary"]["geomean_recommended_safe_mixed_speedup_vs_all_cupy"],
        )
        self.assertGreater(
            after["summary"]["min_recommended_safe_mixed_speedup_vs_all_cupy"],
            before["summary"]["min_recommended_safe_mixed_speedup_vs_all_cupy"],
        )
        self.assertGreater(after["summary"]["geomean_recommended_safe_mixed_speedup_vs_all_cupy"], 300.0)
        rows = {int(row["chain_count"]): row for row in after["rows"]}
        self.assertGreater(rows[4096]["recommended_safe_mixed_speedup_vs_all_cupy"], 600.0)

    def test_report_documents_boundary_and_oom(self) -> None:
        self.assertIn("Goal3737", self.report)
        self.assertIn("reusable, app-agnostic native executor", self.report)
        self.assertIn("Composite geomean speedup improved", self.report)
        self.assertIn("32.9GB", self.report)
        self.assertIn("does not authorize", self.report)


if __name__ == "__main__":
    unittest.main()
