from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
RUNNER = ROOT / "scripts" / "goal2467_grouped_stream_baseline_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2476_same_root_culling_ab_toggle_2026-05-21.md"
POD_ON = ROOT / "docs" / "reports" / "goal2476_same_root_ab_on" / "summary.json"
POD_OFF = ROOT / "docs" / "reports" / "goal2476_same_root_ab_off" / "summary.json"
GEMINI = ROOT / "docs" / "reviews" / "goal2476_gemini_review_same_root_ab_toggle_2026-05-21.md"
GEMINI_FOLLOWUP = (
    ROOT / "docs" / "reviews" / "goal2476_gemini_followup_exact_numbers_same_root_ab_toggle_2026-05-21.md"
)
CONSENSUS = ROOT / "docs" / "reviews" / "goal2476_codex_gemini_consensus_same_root_ab_toggle_2026-05-21.md"


class Goal2476GroupedUnionSameRootToggleTest(unittest.TestCase):
    def test_native_same_root_culling_is_runtime_guarded_and_default_enabled(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("uint32_t same_root_culling;", core)
        self.assertIn("parent_union_candidate && params.same_root_culling != 0u", core)
        self.assertIn(
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_options",
            api,
        )
        self.assertIn(
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_options",
            api,
        )
        self.assertIn(
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_options",
            api,
        )
        self.assertIn("telemetry_out, true, false, item_count", api)
        self.assertIn("same_root_culling != 0u, false, item_count", api)
        kernel_start = core.index("kFixedRadiusGroupedUnion3DRtKernelSrc")
        kernel_end = core.index(')CUDA";', kernel_start)
        kernel = core[kernel_start:kernel_end].lower()
        self.assertNotIn("dbscan", kernel)
        self.assertNotIn("cluster", kernel)

    def test_python_runtime_exposes_default_on_controlled_ab_surface(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("same_root_culling: bool = True", runtime)
        self.assertIn("_require_bool(same_root_culling, name=\"same_root_culling\")", runtime)
        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_OPTIONS_SYMBOL", runtime)
        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_RANGE_DEVICE_OUTPUT_OPTIONS_SYMBOL", runtime)
        self.assertIn("grouped_union_same_root_culling_enabled", runtime)
        self.assertIn("parent_union_same_root_before_anyhit", runtime)
        self.assertIn("disabled_by_caller", runtime)

    def test_adapter_and_benchmark_runner_thread_toggle_to_native_calls(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("grouped_union_same_root_culling: bool = True", adapters)
        self.assertIn("self.grouped_union_same_root_culling", adapters)
        self.assertIn("same_root_culling=self.grouped_union_same_root_culling", adapters)
        self.assertIn("--disable-grouped-union-same-root-culling", app)
        self.assertIn("grouped_union_same_root_culling=not args.disable_grouped_union_same_root_culling", app)
        self.assertIn("--disable-grouped-union-same-root-culling", runner)
        self.assertIn("_same_root_off", runner)
        self.assertIn("grouped_same_root_culling_enabled", runner)

    def test_report_states_boundary_and_evidence_plan(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("controlled A/B", report)
        self.assertIn("default-on", report)
        self.assertIn("No DBSCAN-specific native ABI", report)
        self.assertIn("Public performance claims remain blocked", report)
        self.assertIn("same build", report)

    def test_pod_ab_artifacts_show_same_build_positive_default_on_culling(self) -> None:
        on = json.loads(POD_ON.read_text(encoding="utf-8"))
        off = json.loads(POD_OFF.read_text(encoding="utf-8"))

        self.assertEqual(on["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertEqual(off["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertTrue(on["grouped_union_same_root_culling"])
        self.assertFalse(off["grouped_union_same_root_culling"])
        by_count = {row["point_count"]: row for row in on["summaries"]}
        off_by_count = {row["point_count"]: row for row in off["summaries"]}
        for point_count in (32768, 65536):
            self.assertTrue(by_count[point_count]["signatures_match"])
            self.assertTrue(off_by_count[point_count]["signatures_match"])
            self.assertLess(
                by_count[point_count]["grouped_native_tail_median_sec"],
                off_by_count[point_count]["grouped_native_tail_median_sec"],
            )
            self.assertLess(
                by_count[point_count]["tail_median_sec"],
                off_by_count[point_count]["tail_median_sec"],
            )

    def test_external_review_and_consensus_keep_public_claims_blocked(self) -> None:
        review = GEMINI.read_text(encoding="utf-8")
        followup = GEMINI_FOLLOWUP.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Blocking Issues", review)
        self.assertIn("None", review)
        self.assertIn("Verdict:** Accepted", followup)
        self.assertIn("All report numbers are accurate", followup)
        self.assertIn("accepted as an internal app-agnostic grouped-union engineering step", consensus)
        self.assertIn("Public performance claims remain blocked", consensus)


if __name__ == "__main__":
    unittest.main()
