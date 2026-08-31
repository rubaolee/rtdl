from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3488_overlay_area_prepared_payload_feasibility_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3488_overlay_area_prepared_payload_feasibility_probe_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3488_overlay_area_prepared_payload_feasibility_pod_2026-06-05.json"


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
            "supported positive-area rows",
            "318,096",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_public_cdb_feasibility(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3488.overlay_area_prepared_payload_feasibility.v1")
        self.assertEqual(data["row_count"], 4543)
        self.assertEqual(data["supported_prepared_payload_row_count"], 4539)
        self.assertEqual(data["unsupported_prepared_payload_row_count"], 4)
        self.assertEqual(data["supported_positive_area_row_count"], 1090)
        self.assertEqual(data["all_positive_area_row_count"], 1090)
        self.assertAlmostEqual(data["supported_area_fraction"], 1.0)
        self.assertAlmostEqual(data["supported_positive_row_fraction"], 1.0)
        self.assertEqual(data["max_supported_triangle_pairs_per_row"], 318096)
        self.assertEqual(
            data["unsupported_reason_counts"],
            {"left=unsupported_triangulation_failed|right=prepared_simple_components": 4},
        )
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_spatial_rayjoin_gap_row_records_feasibility_result(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("covers all positive exact-area rows", spatial["current_best_path"])
        self.assertIn("318,096 triangle pairs", spatial["current_bottleneck"])
        self.assertIn("Goal3488", spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()
