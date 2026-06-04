from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3272_rayjoin_point_id_count_route_probe_2026-06-03.md"
DEVICE_FILTERED_ARTIFACT = ROOT / "docs" / "reports" / "goal3272_pod" / "device_filtered_validated_same_slice.json"
POINT_ID_ARTIFACT = ROOT / "docs" / "reports" / "goal3272_pod" / "point_id_count_device_columns_same_slice.json"


class Goal3272RayJoinPointIdCountRouteProbeTest(unittest.TestCase):
    def test_app_exposes_validated_point_id_count_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('"point_id_count_device_columns_validated"', app)
        self.assertIn("def _run_prepared_point_id_count_device_columns_with_boundary_mode", app)
        self.assertIn("prepared.point_id_count_device_columns", app)
        self.assertIn("point_to_shape_positive_hit_count_by_point_id_device_columns_validated", app)
        self.assertIn("point_id_count_device_columns", app)
        self.assertIn("validated device-side closed-shape count did not match exact prepared count", app)
        self.assertNotIn("rayjoin", app[app.index("def _run_prepared_point_id_count_device_columns_with_boundary_mode"):app.index("def run_rayjoin_prepared_optix_workload")].lower())

    def test_runner_accepts_new_mode_as_validated_device_side_lane(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn('"point_id_count_device_columns_validated"', runner)
        self.assertIn("validated device-side count was not validated against exact count", runner)
        self.assertIn("Validated device-side modes time the selected device-side count", runner)

    def test_report_records_measurement_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "experimental RayJoin PIP count route",
            "point-id grouped-count device column",
            "validated against exact prepared count",
            "not a release claim",
            "not a RayJoin paper reproduction claim",
            "not the fastest RayJoin PIP scalar-count path",
            "Goal3272 therefore closes as a route/provenance probe",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifacts_record_point_id_route_boundary(self) -> None:
        self.assertTrue(DEVICE_FILTERED_ARTIFACT.exists())
        self.assertTrue(POINT_ID_ARTIFACT.exists())

        device_filtered = json.loads(DEVICE_FILTERED_ARTIFACT.read_text(encoding="utf-8"))
        point_id = json.loads(POINT_ID_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(device_filtered["rtdl_commit"], point_id["rtdl_commit"])
        self.assertEqual(device_filtered["rtdl"]["pip"]["count_mode"], "device_filtered_validated")
        self.assertEqual(point_id["rtdl"]["pip"]["count_mode"], "point_id_count_device_columns_validated")
        self.assertEqual(device_filtered["rtdl"]["pip"]["counts"]["last"], 1430)
        self.assertEqual(point_id["rtdl"]["pip"]["counts"]["last"], 1430)
        self.assertLess(
            point_id["rtdl"]["pip"]["prepared_query_ms"]["median"],
            point_id["rtdl"]["pip"]["validation_exact_query_ms"]["median"],
        )
        self.assertLess(
            device_filtered["rtdl"]["pip"]["prepared_query_ms"]["median"],
            point_id["rtdl"]["pip"]["prepared_query_ms"]["median"],
        )
        for artifact in (device_filtered, point_id):
            boundary = artifact["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
