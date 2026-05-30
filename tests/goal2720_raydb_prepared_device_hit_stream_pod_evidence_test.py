import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2720_raydb_prepared_device_hit_stream_steady_state_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2720_pod_artifacts"
    / "goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json"
)

PREPARED_BACKEND = "paper_rt_optix_device_hit_stream_triton_prepared"
UNPREPARED_BACKEND = "paper_rt_optix_device_hit_stream_triton"


class Goal2720RaydbPreparedDeviceHitStreamPodEvidenceTest(unittest.TestCase):
    def test_pod_artifact_records_prepared_reuse_and_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(payload["row_counts"], [10000, 100000])
        self.assertEqual(payload["modes"], ["count", "sum"])
        self.assertIn(PREPARED_BACKEND, payload["backends"])

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

    def test_prepared_path_is_faster_than_unprepared_smoke_cases(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        by_key = {
            (case["row_count"], case["mode"], case["backend"]): case
            for case in payload["cases"]
        }

        for row_count in payload["row_counts"]:
            for mode in payload["modes"]:
                unprepared = by_key[(row_count, mode, UNPREPARED_BACKEND)]
                prepared = by_key[(row_count, mode, PREPARED_BACKEND)]
                with self.subTest(row_count=row_count, mode=mode):
                    self.assertLess(prepared["median_wall_sec"], unprepared["median_wall_sec"])
                    self.assertGreater(
                        unprepared["median_wall_sec"] / prepared["median_wall_sec"],
                        4.0,
                    )

    def test_report_documents_results_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB Prepared Device Hit-Stream Steady-State Path", text)
        self.assertIn("5.522x", text)
        self.assertIn("23.938x", text)
        self.assertIn("public true-zero-copy wording", text)
        self.assertIn("RayDB paper reproduction claims", text)
        self.assertIn("prepared steady-state timing replaces cold whole-app timing", text)


if __name__ == "__main__":
    unittest.main()
