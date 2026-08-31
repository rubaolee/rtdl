from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SMOKE = ROOT / "scripts" / "goal3992_grouped_union_extended_telemetry_pod_smoke.py"
REPORT = ROOT / "docs" / "reports" / "goal3992_grouped_union_extended_telemetry_2026-06-08.md"
POD_SMOKE = ROOT / "docs" / "reports" / "goal3992_grouped_union_extended_telemetry_pod_smoke.json"


class Goal3992GroupedUnionExtendedTelemetryContractTest(unittest.TestCase):
    def test_native_launch_params_are_length_aware(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("uint32_t telemetry_count;", core)
        self.assertIn("grouped_union_telemetry_add", core)
        self.assertIn("index < params.telemetry_count", core)
        self.assertIn("lp.telemetry_count", workloads)
        self.assertIn("static_cast<uint32_t>((std::min)", workloads)

    def test_extended_counters_are_generic_candidate_diagnostics(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        for fragment in [
            "grouped_union_telemetry_add(4u, 1ull)",
            "grouped_union_telemetry_add(5u, 1ull)",
            "grouped_union_telemetry_add(6u, 1ull)",
            "grouped_union_telemetry_add(7u, 1ull)",
            "radius_candidate_hits_after_predicate",
            "same_root_culled_candidate_hits",
            "direct_side_effect_candidate_hits",
            "reported_intersection_candidates",
        ]:
            self.assertIn(fragment, core + runtime)

    def test_new_export_preserves_old_four_counter_abi(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        symbol = (
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_"
            "self_device_outputs_with_extended_telemetry_and_execution_options"
        )
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, runtime)
        self.assertIn("telemetry_out must contain at least four counters", runtime)
        self.assertIn("telemetry_count, same_root_culling", api)
        self.assertIn("telemetry_out, 4, true, false, item_count", api)
        self.assertIn("telemetry_out, 4, same_root_culling != 0u", api)

    def test_runtime_selects_extended_symbol_only_with_eight_counters(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("telemetry_buffer_length >= 8", runtime)
        self.assertIn("grouped_union_telemetry_buffer_length", runtime)
        self.assertIn("grouped_union_extended_telemetry_enabled", runtime)
        self.assertIn("grouped_union_telemetry_counter_count", runtime)
        self.assertIn("ctypes.c_size_t(telemetry_buffer_length)", runtime)

    def test_pod_smoke_checks_old_and_extended_paths(self) -> None:
        script = SMOKE.read_text(encoding="utf-8")
        for fragment in [
            "telemetry_old = cp.zeros((4,), dtype=cp.uint64)",
            "telemetry_extended = cp.zeros((8,), dtype=cp.uint64)",
            "grouped_union_extended_telemetry_enabled",
            "old_parent_atomic_attempts_positive",
            "extended_parent_atomic_attempts_positive",
            "extended_radius_candidate_hits_positive",
            "performance_claim_authorized",
        ]:
            self.assertIn(fragment, script)

    def test_pod_artifact_proves_extended_path_and_boundaries(self) -> None:
        payload = json.loads(POD_SMOKE.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["claim_boundary"]["performance_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        old_meta = payload["smoke"]["old_four_counter"]["metadata"]
        extended = payload["smoke"]["extended_eight_counter"]
        extended_meta = extended["metadata"]
        self.assertFalse(old_meta["grouped_union_extended_telemetry_enabled"])
        self.assertEqual(old_meta["grouped_union_telemetry_counter_count"], 4)
        self.assertTrue(extended_meta["grouped_union_extended_telemetry_enabled"])
        self.assertEqual(extended_meta["grouped_union_telemetry_counter_count"], 8)
        self.assertIn("extended_telemetry", extended_meta["native_symbol"])
        self.assertGreater(extended["telemetry"][4], extended["telemetry"][0])
        self.assertGreater(extended["telemetry"][5], extended["telemetry"][1])

    def test_report_explains_telemetry_not_speedup(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "This is instrumentation",
            "not a performance optimization",
            "Do not compare the old and extended elapsed times",
            "next performance primitive should reduce candidate/root-read work",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
