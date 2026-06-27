from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
APP = ROOT / "examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
REPORT = ROOT / "docs/reports/goal3734_shape_pair_prepared_left_active_count_2026-06-07.md"
DIRECT_ARTIFACT = (
    ROOT / "docs/reports/goal3734_shape_pair_prepared_left_active_count_a5000_overlay_direct_summary.json"
)
COMPOSITE_ARTIFACT = (
    ROOT / "docs/reports/goal3734_shape_pair_prepared_left_active_count_a5000_safe_mixed_summary.json"
)


class Goal3734ShapePairPreparedLeftActiveCountTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.prelude = PRELUDE.read_text(encoding="utf-8")
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.app = APP.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_native_prepared_left_handle_stores_device_payload(self) -> None:
        block = self.workloads.split("struct PreparedShapePairRelationLeftSet", 1)[1].split(
            "struct NativeShapePairRelationDeviceColumnsOwner",
            1,
        )[0]
        for token in (
            "DevPtr d_left_polygons",
            "DevPtr d_left_vx",
            "DevPtr d_left_vy",
            "DevPtr d_left_bounds",
            "max_edges",
            "upload(d_left_polygons.ptr",
            "upload(d_left_bounds.ptr",
        ):
            self.assertIn(token, block)

    def test_native_abi_exposes_generic_prepared_left_active_count(self) -> None:
        symbols = (
            "rtdl_optix_prepare_shape_pair_relation_left_set",
            "rtdl_optix_count_prepared_shape_pair_relation_active_device_prepared_left",
            "rtdl_optix_destroy_prepared_shape_pair_relation_left_set",
        )
        for symbol in symbols:
            self.assertIn(symbol, self.prelude)
            self.assertIn(symbol, self.api)

        helper = self.workloads.split(
            "static void count_shape_pair_relation_active_device_with_prepared_left_optix",
            1,
        )[1].split("static void run_prepared_shape_pair_relation_active_device_columns_optix", 1)[0]
        self.assertIn("reset_shape_pair_relation_phase_timings(5u)", helper)
        self.assertIn("prepared_left->d_left_polygons.ptr", helper)
        self.assertIn("prepared_left->d_left_bounds.ptr", helper)
        self.assertNotIn("upload(d_left", helper)

    def test_runtime_binding_and_mode_decoder_are_present(self) -> None:
        for token in (
            "OPTIX_SHAPE_PAIR_RELATION_PREPARE_LEFT_SET_SYMBOL",
            "class PreparedOptixShapePairRelationLeftSet",
            "def prepare_shape_pair_relation_left_set_optix",
            "def count_active_device_continuation_prepared_left",
            "active_count_device_continuation_prepared_left",
            "optional_count_prepared_shape_pair_relation_active_device_prepared_left.argtypes",
        ):
            self.assertIn(token, self.runtime)

    def test_rayjoin_app_adopts_prepared_left_without_native_app_language(self) -> None:
        block = self.app.split("class RayJoinOptixShapePairActiveCountPackedLeftShapes", 1)[1].split(
            "def pack_rayjoin_optix_shape_pair_active_count_left_shapes",
            1,
        )[0]
        self.assertIn("prepare_shape_pair_relation_left_set_optix", block)
        self.assertIn("prepared_left_set_sec", block)
        self.assertIn("def close(self)", block)

        run_block = self.app.split("def run_packed_left_device_continuation", 1)[1].split(
            "def active_relation_device_columns",
            1,
        )[0]
        self.assertIn("prepare_active_count_prepared_left_executor", run_block)
        self.assertIn("executor.run", run_block)
        self.assertIn("timed_query_uses_executor_run", run_block)
        self.assertIn("native_prepared_left_set_enabled", run_block)
        self.assertIn("shape-pair relation", run_block)
        self.assertIn("RayJoin overlay-seed interpretation", run_block)

    def test_report_records_claim_boundary_and_pod_plan(self) -> None:
        self.assertIn("Goal3734", self.report)
        self.assertIn("generic prepared-left shape-pair relation active-count", self.report)
        self.assertIn("left upload out of the hot repeated query path", self.report)
        self.assertIn("does not authorize", self.report)
        self.assertIn("Pod Validation Plan", self.report)

    def test_a5000_direct_overlay_artifact_proves_left_upload_removed(self) -> None:
        payload = json.loads(DIRECT_ARTIFACT.read_text(encoding="utf-8"))
        timings = payload["native_phase_timings"]
        reuse = payload["packed_left_reuse"]

        self.assertEqual(payload["row_count"], 4250)
        self.assertEqual(timings["mode"], "active_count_device_continuation_prepared_left")
        self.assertEqual(timings["active_count"], 4250)
        self.assertEqual(timings["pair_count"], 15006618)
        self.assertEqual(timings["left_prepare"], 0.0)
        self.assertEqual(timings["left_upload"], 0.0)
        self.assertLess(payload["phases_sec"]["prepared_query_sec"], 0.0035)
        self.assertTrue(reuse["native_prepared_left_set_enabled"])
        for key, value in payload["claim_boundary"].items():
            if key.endswith("_authorized"):
                self.assertFalse(value, key)

    def test_a5000_safe_mixed_composite_records_overlay_speedup(self) -> None:
        payload = json.loads(COMPOSITE_ARTIFACT.read_text(encoding="utf-8"))
        row = payload["rows"][0]
        self.assertEqual(payload["git_commit"], "c8f3a67c7e770e1e9a7d684ce4521d6b37c9273b")
        self.assertTrue(row["all_counts_match"])
        self.assertGreater(row["recommended_safe_mixed_speedup_vs_all_cupy"], 300.0)
        by_workload = {entry["workload"]: entry for entry in row["workloads"]}
        self.assertGreater(by_workload["overlay_seed"]["recommended_speedup_vs_cupy"], 50.0)
        self.assertLess(
            by_workload["overlay_seed"]["recommended_route"]["hot_median_sec"],
            0.0035,
        )


if __name__ == "__main__":
    unittest.main()
