from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1895_v2_partner_perf_matrix_status_2026-05-13.md"
FIXED_RADIUS = ROOT / "docs" / "reports" / "goal1881_fixed_radius_reusable_outputs_pod.json"
SEG_POLY_512 = ROOT / "docs" / "reports" / "goal1886_segment_polygon_prepared_reuse_pod_512.json"
SEG_POLY_2048 = ROOT / "docs" / "reports" / "goal1886_segment_polygon_prepared_reuse_pod_2048.json"
ROAD_64 = ROOT / "docs" / "reports" / "goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_64.json"
ROAD_256 = ROOT / "docs" / "reports" / "goal1889_road_hazard_prepared_reuse_local_gtx1070_smoke_256.json"


class Goal1895V2PartnerPerfMatrixStatusTest(unittest.TestCase):
    def test_report_lists_current_evidence_and_missing_pod_rows(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: partial-matrix-pod-pending", text)
        self.assertIn("service coverage gaps", text)
        self.assertIn("event hotspot screening", text)
        self.assertIn("segment/polygon hitcount", text)
        self.assertIn("road hazard priority flags", text)
        self.assertIn("goal1881_fixed_radius_reusable_outputs_pod.json", text)
        self.assertIn("goal1886_segment_polygon_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1886_segment_polygon_prepared_reuse_pod_2048.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", text)
        self.assertIn("does not authorize v2.0 release readiness", text)

    def test_referenced_artifacts_exist_and_keep_boundaries(self) -> None:
        fixed = json.loads(FIXED_RADIUS.read_text(encoding="utf-8"))
        self.assertEqual(fixed["status"], "measurement")
        self.assertTrue(fixed["results"])

        for path, count in ((SEG_POLY_512, 512), (SEG_POLY_2048, 2048)):
            artifact = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(artifact["status"], "pass")
            self.assertEqual(artifact["count"], count)
            self.assertIn("NVIDIA GeForce RTX 3090", artifact["gpu"])
            self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

        for path, count in ((ROAD_64, 64), (ROAD_256, 256)):
            artifact = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(artifact["status"], "pass")
            self.assertEqual(artifact["goal_extension"], "Goal1889")
            self.assertEqual(artifact["count"], count)
            self.assertIn("NVIDIA GeForce GTX 1070", artifact["gpu"])
            self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
