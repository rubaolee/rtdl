import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2722_raydb_prepared_device_hit_stream_large_scale_pod_evidence_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2722_pod_artifacts"
    / "goal2722_raydb_prepared_device_hit_stream_large_pod_69_30_85_171_2026-05-30.json"
)

PREPARED_BACKEND = "paper_rt_optix_device_hit_stream_triton_prepared"
UNPREPARED_BACKEND = "paper_rt_optix_device_hit_stream_triton"


class Goal2722RaydbPreparedDeviceHitStreamLargeScalePodEvidenceTest(unittest.TestCase):
    def test_large_pod_artifact_has_expected_shape(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(payload["row_counts"], [250000, 1000000])
        self.assertEqual(payload["modes"], ["count", "sum"])
        self.assertEqual(payload["group_count"], 256)
        self.assertEqual(payload["repeats"], 3)
        self.assertEqual(payload["warmup"], 1)

    def test_large_prepared_cases_preserve_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        prepared_cases = [case for case in payload["cases"] if case["backend"] == PREPARED_BACKEND]

        self.assertEqual(len(prepared_cases), 4)
        for case in prepared_cases:
            with self.subTest(row_count=case["row_count"], mode=case["mode"]):
                self.assertTrue(case["matches_cpu_reference"])
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

    def test_large_prepared_path_is_faster_in_every_case(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        by_key = {
            (case["row_count"], case["mode"], case["backend"]): case
            for case in payload["cases"]
        }
        expected_min_ratios = {
            (250000, "count"): 60.0,
            (250000, "sum"): 5.0,
            (1000000, "count"): 200.0,
            (1000000, "sum"): 10.0,
        }

        for key, min_ratio in expected_min_ratios.items():
            row_count, mode = key
            unprepared = by_key[(row_count, mode, UNPREPARED_BACKEND)]
            prepared = by_key[(row_count, mode, PREPARED_BACKEND)]
            ratio = unprepared["median_wall_sec"] / prepared["median_wall_sec"]
            with self.subTest(row_count=row_count, mode=mode):
                self.assertLess(prepared["median_wall_sec"], unprepared["median_wall_sec"])
                self.assertGreater(ratio, min_ratio)

    def test_report_documents_large_results_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB Prepared Device Hit-Stream Large-Scale Pod Evidence", text)
        self.assertIn("65.416x", text)
        self.assertIn("210.336x", text)
        self.assertIn("true-zero-copy wording", text)
        self.assertIn("RayDB paper reproduction claims", text)
        self.assertIn("prepared steady-state timing", text)


if __name__ == "__main__":
    unittest.main()
