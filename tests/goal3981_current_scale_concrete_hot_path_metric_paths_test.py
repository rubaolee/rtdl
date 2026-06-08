import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3981_current_scale_concrete_hot_path_metric_paths_2026-06-08.md"
OUTPUTS = (
    ROOT
    / "docs"
    / "reports"
    / "goal3976_fresh_helper_current_scale_validation_2026-06-08"
    / "outputs"
)
GOAL3984_REPORT = ROOT / "docs" / "reports" / "goal3984_resident_hot_query_summary_contract_2026-06-08.md"
GOAL3984_SUPERSEDED_ROWS = {
    "raydb_style_optix_count_scale_default_262k",
    "robot_collision_optix_scale_default_1024_no_probe_reference",
}


def _lookup_path(payload: object, dotted_path: str) -> object:
    current = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted_path)
        current = current[part]
    return current


class Goal3981CurrentScaleConcreteHotPathMetricPathsTest(unittest.TestCase):
    def test_all_rows_use_concrete_non_placeholder_metric_paths(self) -> None:
        for row in rt.current_benchmark_scale_profiles():
            metric = row["representative_hot_path_metric"]
            with self.subTest(row=row["row_id"]):
                self.assertNotEqual(metric, "payload_timing_summary_or_app_phase_timing")
                self.assertNotIn("wrapper_elapsed", metric)
                self.assertNotIn("scale_runner", metric)

    def test_declared_metric_paths_exist_in_fresh_helper_artifact(self) -> None:
        for row in rt.current_benchmark_scale_profiles():
            metric = row["representative_hot_path_metric"]
            payload_path = OUTPUTS / f"{row['row_id']}.stdout.json"
            with self.subTest(row=row["row_id"]):
                if row["row_id"] in GOAL3984_SUPERSEDED_ROWS:
                    report_text = GOAL3984_REPORT.read_text(encoding="utf-8")
                    self.assertIn(metric, report_text)
                    self.assertEqual(
                        row["scale_calibration_status"],
                        "resident_high_repeat_summary_contract_goal3984",
                    )
                    continue
                payload = json.loads(payload_path.read_text(encoding="utf-8"))
                value = _lookup_path(payload, metric)
                self.assertIsNotNone(value)
                if row["row_id"] != "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default":
                    self.assertIsInstance(value, (int, float))
                    self.assertGreaterEqual(float(value), 0.0)
                else:
                    self.assertIsInstance(value, dict)
                    self.assertIn("metric_scope", value)
                    self.assertIn("pip_one_shot", value)

    def test_report_records_concrete_paths_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "concrete payload paths",
            "representative_hot_path_summary",
            "metadata.prepared_phase_timing_summary.native_call_wall.total_sec",
            "runner_payload.elapsed_median_sec",
            "does not authorize release",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
