from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal3996_grouped_union_extended_telemetry_sweep_pod.py"
REPORT = ROOT / "docs" / "reports" / "goal4007_grouped_union_root_read_telemetry_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4007_grouped_union_root_read_telemetry_pod"


class Goal4007GroupedUnionRootReadTelemetryTest(unittest.TestCase):
    def test_native_records_root_read_counters_without_new_abi(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        self.assertIn("find_grouped_union_root_readonly", core)
        self.assertIn("grouped_union_telemetry_add(8u, 1ull)", core)
        self.assertIn("grouped_union_telemetry_add(9u, 1ull)", core)
        self.assertNotIn("rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_root_read", core)

    def test_runtime_exposes_ten_counter_contract_as_diagnostic_only(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        for fragment in [
            "use_root_read_telemetry = telemetry_buffer_length >= 10",
            "10 if use_root_read_telemetry else 8 if use_extended_telemetry",
            "grouped_union_root_read_telemetry_enabled",
            "uint64[8]=root_find_invocations",
            "uint64[9]=root_find_parent_link_steps",
        ]:
            self.assertIn(fragment, runtime)
        self.assertIn("true_zero_copy_authorized\": False", runtime)
        self.assertIn("paper_speedup_claim_authorized\": False", runtime)

    def test_pod_sweep_runner_allows_ten_counter_buffer_without_changing_default(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--telemetry-counters", type=int, default=8)', script)
        self.assertIn("telemetry = cp.zeros((telemetry_counters,), dtype=cp.uint64)", script)
        self.assertIn('"telemetry_counter_capacity": args.telemetry_counters', script)
        self.assertIn("--telemetry-counters must be at least 4", script)

    def test_pod_artifacts_record_root_read_diagnostics(self) -> None:
        for name in ["clustered3d_65536.json", "road3d_65536.json", "ngsim_dense_65536.json"]:
            payload = json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["telemetry_counter_capacity"], 10)
            self.assertFalse(payload["claim_boundary"]["performance_claim_authorized"])
            self.assertFalse(payload["claim_boundary"]["release_authorized"])
            row = payload["rows"][0]
            default = next(
                variant for variant in row["variants"]
                if variant["label"] == "same_root_on_direct_off"
            )
            telemetry = default["last_telemetry"]
            metadata = default["last_metadata"]
            self.assertEqual(metadata["grouped_union_telemetry_counter_count"], 10)
            self.assertTrue(metadata["grouped_union_root_read_telemetry_enabled"])
            self.assertIn("root_find_invocations", metadata["grouped_union_telemetry_contract"])
            self.assertGreater(telemetry[8], 0)
            self.assertGreaterEqual(telemetry[9], telemetry[8] - row["point_count"])

    def test_report_frames_root_read_telemetry_as_next_design_evidence(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "root-find telemetry",
            "diagnostic only",
            "does not add a native ABI",
            "does not authorize release",
            "partition-convergence hybrid",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
