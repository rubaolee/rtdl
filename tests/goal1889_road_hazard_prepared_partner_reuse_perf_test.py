from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1869_road_hazard_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1889_road_hazard_prepared_partner_reuse_2026-05-13.md"
LOCAL_SMOKE_64 = ROOT / "docs" / "reports" / "goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_64.json"
LOCAL_SMOKE_256 = ROOT / "docs" / "reports" / "goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_256.json"


class Goal1889RoadHazardPreparedPartnerReusePerfTest(unittest.TestCase):
    def test_runner_records_prepared_partner_reuse_row(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_segment_polygon_anyhit_optix_partner_device_scene", text)
        self.assertIn("allocate_segment_polygon_witness_partner_device_output_columns", text)
        self.assertIn("road_hazard_priority_flags_optix_prepared_partner_device_columns", text)
        self.assertIn("v2_0_prepared_partner_road_hazard_priority_flags_", text)
        self.assertIn("goal1889_prepared_reuse", text)
        self.assertIn("query_median_ratio_vs_goal1869_unprepared_partner", text)
        self.assertIn('"prepared_scene_reused": True', text)
        self.assertIn('"witness_output_columns_reused": True', text)
        self.assertIn("prepared_partner_scene.close()", text)

    def test_report_keeps_claim_boundary_and_pod_plan(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: local-smoke-pass-pod-pending", report)
        self.assertIn("road_hazard_priority_flags_optix_prepared_partner_device_columns", report)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", report)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", report)
        self.assertIn("goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_64.json", report)
        self.assertIn("goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_256.json", report)
        self.assertIn("They do not replace RTX 3090 pod timing evidence", report)
        self.assertIn("same-contract", report)
        self.assertIn("does not authorize v2.0 release wording", report)
        self.assertIn("whole-app speedup", report)
        self.assertIn("broad RT-core speedup", report)

    def test_local_linux_smoke_artifacts_record_prepared_reuse_boundaries(self) -> None:
        import json

        for path, count in ((LOCAL_SMOKE_64, 64), (LOCAL_SMOKE_256, 256)):
            with self.subTest(path=path.name):
                artifact = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(artifact["status"], "pass")
                self.assertEqual(artifact["count"], count)
                self.assertIn("NVIDIA GeForce GTX 1070", artifact["gpu"])
                self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
                for partner in ("cupy", "torch"):
                    prepared = artifact["partners"][partner]["goal1889_prepared_reuse"]
                    self.assertEqual(prepared["row_count"], count)
                    self.assertEqual(prepared["output_contract"], "prepared_partner_owned_road_hazard_priority_columns")
                    self.assertTrue(prepared["prepared_scene_reused"])
                    self.assertTrue(prepared["witness_output_columns_reused"])
                    self.assertLess(prepared["query_median_ratio_vs_goal1869_unprepared_partner"], 1.0)
                boundary = artifact["claim_boundary"]
                self.assertTrue(boundary["same_contract_timing_row"])
                self.assertFalse(boundary["v2_0_release_authorized"])
                self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
                self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
