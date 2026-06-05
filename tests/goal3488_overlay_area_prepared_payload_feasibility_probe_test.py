from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3488_overlay_area_prepared_payload_feasibility_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3488_overlay_area_prepared_payload_feasibility_probe_2026-06-05.md"


class Goal3488OverlayAreaPreparedPayloadFeasibilityProbeTest(unittest.TestCase):
    def test_script_classifies_prepared_payload_feasibility(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "prepared_simple_components",
            "unsupported_holes",
            "supported_prepared_payload_row_count",
            "supported_area_fraction",
            "unsupported_reason_counts",
            "triangulate_simple_polygon_ear_clip",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_records_boundary_and_expected_artifact(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "public-CDB feasibility probe",
            "no-hole simple polygon components",
            "external CPU oracle/classifier",
            "does not authorize",
            "goal3488_overlay_area_prepared_payload_feasibility_pod_2026-06-05.json",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
