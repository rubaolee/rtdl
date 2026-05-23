from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2471_grouped_union_atomic_telemetry_2026-05-20.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2471_gemini_review_grouped_union_telemetry_2026-05-20.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal2471_codex_gemini_consensus_grouped_union_telemetry_2026-05-20.md"
POD_SMOKE = ROOT / "scripts" / "goal2471_grouped_union_telemetry_pod_smoke.py"


class Goal2471GroupedUnionAtomicTelemetryTest(unittest.TestCase):
    def test_native_telemetry_symbol_preserves_existing_default_symbol(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("telemetry_out", core)
        self.assertIn("union_grouped_min_root_with_telemetry", core)
        self.assertIn("atomicAdd(telemetry_out + 0", core)
        self.assertIn("atomicAdd(telemetry_out + 1", core)
        self.assertIn("atomicAdd(params.telemetry_out + 2", core)
        self.assertIn("atomicAdd(params.telemetry_out + 3", core)
        self.assertIn("rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs(", api)
        self.assertIn(
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry",
            api + prelude + workloads,
        )
        self.assertTrue(
            "nullptr, item_count" in api
            or "nullptr, true, item_count" in api
            or "nullptr, true, false, item_count" in api,
            "default grouped-union symbol must keep telemetry disabled",
        )

    def test_python_runtime_exposes_explicit_device_telemetry_without_default_overhead(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_TELEMETRY_SYMBOL", runtime)
        self.assertIn("telemetry_out=None", runtime)
        self.assertIn("grouped-union telemetry_out must use dtype uint64", runtime)
        self.assertIn("grouped-union telemetry_out must contain at least four counters", runtime)
        self.assertIn("grouped_union_telemetry_requested", runtime)
        self.assertIn("uint64[0]=parent_atomic_attempts", runtime)

    def test_report_keeps_telemetry_as_instrumentation_not_optimization(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("not an optimization", report)
        self.assertIn("does not authorize a performance claim", report)
        self.assertIn("telemetry[0] = parent_atomic_attempts", report)
        self.assertIn("telemetry[3] = fallback_atomic_successes", report)
        self.assertIn("No DBSCAN-specific native ABI is introduced", report)
        self.assertIn("Pod validation confirms the counters execute on the OptiX path", report)

    def test_review_consensus_keeps_pod_gate_open(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: ACCEPT", gemini)
        self.assertIn("pending pod validation", consensus)
        self.assertIn("does not authorize a performance claim", consensus)
        self.assertIn("Connection refused", consensus)

    def test_pod_smoke_runner_records_required_telemetry_checks(self) -> None:
        script = POD_SMOKE.read_text(encoding="utf-8")

        self.assertIn("apply_device_grouped_union_all_self", script)
        self.assertIn("apply_device_grouped_union_self", script)
        self.assertIn("parent_attempts_positive", script)
        self.assertIn("fallback_counters_zero", script)
        self.assertIn("fallback_attempts_positive", script)
        self.assertIn("telemetry_overhead_ratio", script)
        self.assertIn("\"dbscan_native_abi_added\": False", script)


if __name__ == "__main__":
    unittest.main()
