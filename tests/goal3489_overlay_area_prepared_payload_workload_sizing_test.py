from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3489_overlay_area_prepared_payload_workload_sizing.py"
REPORT = ROOT / "docs" / "reports" / "goal3489_overlay_area_prepared_payload_workload_sizing_2026-06-05.md"


class Goal3489OverlayAreaPreparedPayloadWorkloadSizingTest(unittest.TestCase):
    def test_script_measures_component_and_triangle_pair_work(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "total_component_pair_rows",
            "total_triangle_pairs",
            "max_triangle_pairs_per_relation",
            "triangle_pairs_per_relation_percentiles",
            "component_pairs_per_relation_percentiles",
            "max_triangle_pair_samples",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_records_boundary_and_expected_artifact(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "workload-sizing probe",
            "expanded component-pair rows",
            "total triangle-pair work",
            "does not authorize",
            "goal3489_overlay_area_prepared_payload_workload_sizing_pod_2026-06-05.json",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
