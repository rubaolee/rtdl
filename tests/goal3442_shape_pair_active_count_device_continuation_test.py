from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
SCRIPT = ROOT / "scripts" / "goal3442_shape_pair_active_count_device_continuation_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3442_shape_pair_active_count_device_continuation_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3442_shape_pair_active_count_device_continuation_pod_2026-06-05.json"


class Goal3442ShapePairActiveCountDeviceContinuationTest(unittest.TestCase):
    def test_native_device_continuation_surface_is_generic(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        for phrase in (
            "kShapePairRelationActiveCountDeviceKernelSrc",
            "shape_pair_relation_active_count_device_kernel",
            "count_shape_pair_relation_active_device_with_prepared_right_optix",
            "rtdl_optix_count_prepared_shape_pair_relation_active_device",
        ):
            self.assertIn(phrase, core + workloads + prelude + api)

        native_slice_start = workloads.index("static void count_shape_pair_relation_active_device_with_prepared_right_optix")
        native_slice_end = workloads.index("static void run_shape_pair_relation_flags_optix", native_slice_start)
        native_slice = workloads[native_slice_start:native_slice_end].lower()
        for forbidden in ("rayjoin", "cdb", "county", "soil"):
            self.assertNotIn(forbidden, native_slice)

    def test_python_and_app_expose_opt_in_device_continuation(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        for phrase in (
            "def count_active_device_continuation(self, left_polygons) -> int:",
            "rtdl_optix_count_prepared_shape_pair_relation_active_device",
            '3: "active_count_device_continuation"',
        ):
            self.assertIn(phrase, runtime)
        for phrase in (
            "def run_packed_left_host_exact(",
            "def run_packed_left_device_continuation(",
            "active_count_device_continuation_sec",
            "prepared_optix_shape_pair_active_count_device_continuation_reuse",
            "only the scalar count is copied back",
        ):
            self.assertIn(phrase, app)
        self.assertIn("return self.run_packed_left_device_continuation(", app)

    def test_probe_and_report_keep_claim_boundaries_and_oracle_comparison(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3442.shape_pair_active_count_device_continuation.v1",
            "all_counts_match",
            "host_active_count_sec",
            "device_active_count_sec",
            "device_speedup_vs_host",
            "rayjoin_paper_reproduction_claim_authorized",
        ):
            self.assertIn(phrase, script)
        for phrase in (
            "Goal3442",
            "device-side continuation",
            "opt-in",
            "host exact path",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3442 pod artifact pending")
    def test_pod_artifact_counts_match_and_flags_are_closed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3442.shape_pair_active_count_device_continuation.v1")
        self.assertEqual(payload["goal"], 3442)
        self.assertTrue(payload["all_counts_match"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))
        self.assertEqual(payload["host_counts"], payload["device_counts"])
        self.assertGreater(payload["device_speedup_vs_host"]["median"], 1.0)
        for run in payload["runs"]:
            self.assertTrue(run["counts_match"])
            self.assertEqual(
                run["device_native_phase_timings"]["mode"],
                "active_count_device_continuation",
            )


if __name__ == "__main__":
    unittest.main()
