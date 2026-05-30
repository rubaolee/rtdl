import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2726_raydb_v24_native_vs_v25_prepared_probe_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2726_pod_artifacts"
    / "goal2726_raydb_v24_native_vs_v25_prepared_probe_pod_69_30_85_171_2026-05-30.json"
)

OLD_BACKEND = "paper_rt_optix"
PREPARED_BACKEND = "paper_rt_optix_device_hit_stream_triton_prepared"


class Goal2726RaydbV24NativeVsV25PreparedProbeTest(unittest.TestCase):
    def test_pod_artifact_has_expected_shape(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(payload["backends"], [OLD_BACKEND, PREPARED_BACKEND])
        self.assertEqual(payload["row_counts"], [250000, 1000000])
        self.assertEqual(payload["modes"], ["count", "sum"])
        self.assertEqual(payload["group_count"], 256)
        self.assertEqual(payload["repeats"], 3)
        self.assertEqual(payload["warmup"], 1)
        self.assertIn("NVIDIA RTX A5000", payload["nvidia_smi"])

    def test_existing_native_cases_are_rt_core_diagnostic_not_handoff_path(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        old_cases = [case for case in payload["cases"] if case["backend"] == OLD_BACKEND]

        self.assertEqual(len(old_cases), 4)
        for case in old_cases:
            with self.subTest(row_count=case["row_count"], mode=case["mode"]):
                self.assertTrue(case["matches_cpu_reference"])
                self.assertTrue(case["rt_core_accelerated"])
                self.assertEqual(
                    case["native_symbol"],
                    "rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction",
                )
                self.assertEqual(
                    case["phase_timing"]["phase_contract_version"],
                    "rtdl.partner.v2.4",
                )
                self.assertIsNone(case["native_device_column_path_used"])
                self.assertIsNone(case["native_device_hit_stream_columns_ready"])
                self.assertIsNone(case["host_row_bridge_bypassed"])
                self.assertIsNone(case["true_zero_copy_authorized"])

    def test_prepared_cases_preserve_v25_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        prepared_cases = [case for case in payload["cases"] if case["backend"] == PREPARED_BACKEND]

        self.assertEqual(len(prepared_cases), 4)
        for case in prepared_cases:
            with self.subTest(row_count=case["row_count"], mode=case["mode"]):
                self.assertTrue(case["matches_cpu_reference"])
                self.assertTrue(case["rt_core_accelerated"])
                self.assertTrue(case["prepared_steady_state"])
                self.assertTrue(case["prepared_payload_columns_reused"])
                self.assertTrue(case["prepared_optix_scene_reused"])
                self.assertTrue(case["native_device_column_path_used"])
                self.assertTrue(case["native_device_hit_stream_columns_ready"])
                self.assertTrue(case["host_row_bridge_bypassed"])
                self.assertFalse(case["handoff_materializes_host_rows_for_bridge"])
                self.assertTrue(case["handoff_native_device_column_output_proven_on_hardware"])
                self.assertTrue(case["handoff_removes_host_materialization_bottleneck"])
                self.assertTrue(case["torch_carrier_same_pointer_evidence_observed"])
                self.assertFalse(case["true_zero_copy_authorized"])
                self.assertIn("does not authorize true zero-copy", case["claim_boundary"])

    def test_prepared_path_beats_existing_native_probe_in_every_case(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        by_key = {
            (case["row_count"], case["mode"], case["backend"]): case
            for case in payload["cases"]
        }
        expected_min_ratios = {
            (250000, "count"): 60.0,
            (250000, "sum"): 10.0,
            (1000000, "count"): 300.0,
            (1000000, "sum"): 10.0,
        }

        for key, min_ratio in expected_min_ratios.items():
            row_count, mode = key
            old_case = by_key[(row_count, mode, OLD_BACKEND)]
            prepared = by_key[(row_count, mode, PREPARED_BACKEND)]
            ratio = old_case["median_wall_sec"] / prepared["median_wall_sec"]
            with self.subTest(row_count=row_count, mode=mode):
                self.assertLess(prepared["median_wall_sec"], old_case["median_wall_sec"])
                self.assertGreater(ratio, min_ratio)

    def test_report_documents_diagnostic_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB v2.4 Native vs v2.5 Prepared Diagnostic Probe", text)
        self.assertIn("64.018x", text)
        self.assertIn("342.722x", text)
        self.assertIn("not a prepared steady-state same-contract opponent", text)
        self.assertIn("does not authorize a public v2.5 speedup claim", text)
        self.assertIn("true-zero-copy wording remains unauthorized", text)


if __name__ == "__main__":
    unittest.main()
