from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
RUNNER = ROOT / "scripts" / "goal2467_grouped_stream_baseline_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2477_intersection_direct_grouped_union_experiment_2026-05-21.md"
POD_OFF = ROOT / "docs" / "reports" / "goal2477_direct_side_effect_ab_off" / "summary.json"
POD_ON = ROOT / "docs" / "reports" / "goal2477_direct_side_effect_ab_on" / "summary.json"
POD_131K_OFF = ROOT / "docs" / "reports" / "goal2477_direct_side_effect_scale_131k_off" / "summary.json"
POD_131K_ON = ROOT / "docs" / "reports" / "goal2477_direct_side_effect_scale_131k_on" / "summary.json"
GEMINI = ROOT / "docs" / "reviews" / "goal2477_gemini_review_intersection_direct_grouped_union_2026-05-21.md"
GEMINI_FOLLOWUP = ROOT / "docs" / "reviews" / "goal2477_gemini_followup_exact_numbers_2026-05-21.md"
GEMINI_FOLLOWUP_131K = (
    ROOT / "docs" / "reviews" / "goal2477_gemini_followup_exact_numbers_with_131k_2026-05-21.md"
)
CONSENSUS = ROOT / "docs" / "reviews" / "goal2477_codex_gemini_consensus_intersection_direct_grouped_union_2026-05-21.md"


class Goal2477IntersectionDirectGroupedUnionExperimentTest(unittest.TestCase):
    def test_native_direct_side_effect_is_guarded_by_default_off_launch_option(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("uint32_t direct_side_effect;", core)
        self.assertIn("uint32_t direct_side_effect;", workloads)
        self.assertIn("apply_grouped_union_side_effect(source, prim, parent_union_candidate);", core)
        self.assertIn("params.direct_side_effect != 0u", core)
        self.assertIn("optixReportIntersection(params.radius, 0u);", core)
        self.assertIn("lp.direct_side_effect = direct_side_effect ? 1u : 0u;", workloads)

    def test_c_abi_adds_execution_options_without_changing_existing_options_symbols(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        for text in (api, prelude):
            self.assertIn(
                "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_execution_options",
                text,
            )
            self.assertIn(
                "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options",
                text,
            )
            self.assertIn(
                "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_execution_options",
                text,
            )
            self.assertIn(
                "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_execution_options",
                text,
            )
        self.assertIn("same_root_culling != 0u, false, item_count", api)
        self.assertIn("same_root_culling != 0u, direct_side_effect != 0u, item_count", api)

    def test_python_runtime_and_adapter_expose_default_off_experiment(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        adapters = ADAPTERS.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("direct_side_effect: bool = False", runtime)
        self.assertIn("_grouped_union_direct_side_effect_policy", runtime)
        self.assertIn("intersection_program_side_effect_no_anyhit_report", runtime)
        self.assertIn("disabled_by_default_anyhit_side_effect", runtime)
        self.assertIn("grouped_union_direct_side_effect: bool = False", adapters)
        self.assertIn("self.grouped_union_direct_side_effect", adapters)
        self.assertIn("direct_side_effect=self.grouped_union_direct_side_effect", adapters)
        self.assertIn("--enable-grouped-union-direct-side-effect", app)
        self.assertIn("--enable-grouped-union-direct-side-effect", runner)
        self.assertIn("_direct_side_effect", runner)

    def test_report_keeps_claim_and_review_boundaries_explicit(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("default-off", report.lower())
        self.assertIn("no DBSCAN-native ABI", report)
        self.assertIn("Public performance claims remain blocked", report)
        self.assertIn("external review", report.lower())
        self.assertIn("must not replace the anyhit default", report)
        self.assertIn("0.0249137636", report)
        self.assertIn("0.0680980021", report)
        self.assertIn("0.2503216779", report)
        self.assertIn("performance is mixed to negative", report)
        self.assertIn("Keep the experiment default-off", report)

    def test_pod_ab_artifacts_show_correctness_but_no_promotion_signal(self) -> None:
        off = json.loads(POD_OFF.read_text(encoding="utf-8"))
        on = json.loads(POD_ON.read_text(encoding="utf-8"))

        self.assertEqual(off["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertEqual(on["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertFalse(off["grouped_union_direct_side_effect"])
        self.assertTrue(on["grouped_union_direct_side_effect"])
        by_count = {row["point_count"]: row for row in off["summaries"]}
        on_by_count = {row["point_count"]: row for row in on["summaries"]}
        for point_count in (32768, 65536):
            self.assertTrue(by_count[point_count]["signatures_match"])
            self.assertTrue(on_by_count[point_count]["signatures_match"])
        self.assertGreater(
            on_by_count[32768]["grouped_native_tail_median_sec"],
            by_count[32768]["grouped_native_tail_median_sec"],
        )
        self.assertLess(
            on_by_count[65536]["grouped_native_tail_median_sec"],
            by_count[65536]["grouped_native_tail_median_sec"],
        )
        off_131k = json.loads(POD_131K_OFF.read_text(encoding="utf-8"))
        on_131k = json.loads(POD_131K_ON.read_text(encoding="utf-8"))
        self.assertTrue(off_131k["summaries"][0]["signatures_match"])
        self.assertTrue(on_131k["summaries"][0]["signatures_match"])
        self.assertGreater(
            on_131k["summaries"][0]["grouped_native_tail_median_sec"],
            off_131k["summaries"][0]["grouped_native_tail_median_sec"],
        )

    def test_external_review_and_consensus_accept_only_default_off_experiment(self) -> None:
        review = GEMINI.read_text(encoding="utf-8")
        followup = GEMINI_FOLLOWUP.read_text(encoding="utf-8")
        followup_131k = GEMINI_FOLLOWUP_131K.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Blocking Issues", review)
        self.assertIn("None", review)
        self.assertIn("Verdict: Approved", review)
        self.assertIn("Verdict: Accepted", followup)
        self.assertIn("Verdict: Accepted", followup_131k)
        self.assertIn("131072", followup_131k)
        self.assertIn("default-off OptiX grouped-union experiment", consensus)
        self.assertIn("not accepted as a default-path promotion", consensus)
        self.assertIn("131072 points: direct path is slower", consensus)
        self.assertIn("Public performance claims remain blocked", consensus)


if __name__ == "__main__":
    unittest.main()
