from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3272_rayjoin_point_id_count_route_probe_2026-06-03.md"


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
            "performance verdict pending pod measurement",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
