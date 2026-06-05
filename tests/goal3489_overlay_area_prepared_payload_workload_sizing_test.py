from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3489_overlay_area_prepared_payload_workload_sizing.py"
REPORT = ROOT / "docs" / "reports" / "goal3489_overlay_area_prepared_payload_workload_sizing_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3489_overlay_area_prepared_payload_workload_sizing_pod_2026-06-05.json"


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
            "9,653,005",
            "318,096",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_workload_sizing(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3489.overlay_area_prepared_payload_workload_sizing.v1")
        self.assertEqual(data["row_count"], 4543)
        self.assertEqual(data["supported_row_count"], 4539)
        self.assertEqual(data["unsupported_row_count"], 4)
        self.assertEqual(data["total_component_pair_rows"], 39947)
        self.assertEqual(data["total_triangle_pairs"], 9653005)
        self.assertEqual(data["max_component_pair_rows_per_relation"], 484)
        self.assertEqual(data["max_triangle_pairs_per_relation"], 318096)
        self.assertEqual(data["triangle_pairs_per_relation_percentiles"], {"p50": 294, "p90": 3450, "p99": 25530})
        self.assertEqual(data["component_pairs_per_relation_percentiles"], {"p50": 4, "p90": 20, "p99": 66})
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_spatial_rayjoin_gap_row_records_workload_sizing(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("9,653,005 triangle pairs", spatial["current_bottleneck"])
        self.assertIn("split large relation rows", spatial["current_bottleneck"])
        self.assertIn("Goal3489", spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()
