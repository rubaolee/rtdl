from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.md"
STDOUT = ROOT / "docs" / "reports" / "goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.stdout"


class Goal3220SpatialRayJoinCurrentBestCountHarnessArtifactTest(unittest.TestCase):
    def test_pod_artifact_records_current_best_rayjoin_count_harness(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "Goal3220")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["harness_version"], "rtdl.goal3220.spatial_rayjoin_current_best_count_harness.v1")
        self.assertEqual(data["source_commit"], "06d86d597574550cde3f3775b3fc6c975e380606")
        self.assertEqual(data["gpu"], "NVIDIA A40, 570.211.01")
        self.assertEqual(data["execution_route_policy"], "lsi_dense_count_else_prepared_optix_count")
        self.assertEqual(data["row_count"], 3)

        rows = {row["workload"]: row for row in data["rows"]}
        self.assertEqual(rows["pip"]["execution_route"], "prepared_optix")
        self.assertEqual(rows["lsi"]["execution_route"], "prepared_optix_left_id_dense_count")
        self.assertEqual(rows["overlay_seed"]["execution_route"], "prepared_optix")
        self.assertEqual(rows["lsi"]["generic_primitive"], "SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_2D")
        for row in rows.values():
            self.assertEqual(row["status"], "pass")
            self.assertTrue(row["matches_cpu_reference"])
            self.assertEqual(row["expected_count"], row["observed_count"])
            self.assertTrue(row["uses_prepared_optix_rt_backend"])
            self.assertFalse(row["include_rows"])

        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["native_engine_customization"])

    def test_report_and_stdout_preserve_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        stdout = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "current best route policy",
            "`lsi`: new fused dense left-id count route",
            "matches_cpu_reference: true",
            "RayJoin workload interpretation stays in Python",
            "does not authorize release",
            "RayJoin\npaper-reproduction claims",
        ):
            self.assertIn(phrase, report)
        self.assertIn('"status": "pass"', stdout)
        self.assertIn('"execution_route": "prepared_optix_left_id_dense_count"', stdout)


if __name__ == "__main__":
    unittest.main()
