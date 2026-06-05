from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3477_shape_pair_exact_overlay_output_complexity_oracle.py"
REPORT = ROOT / "docs" / "reports" / "goal3477_shape_pair_exact_overlay_output_complexity_oracle_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3477_shape_pair_exact_overlay_output_complexity_oracle_pod_2026-06-05.json"


class Goal3477ShapePairExactOverlayOutputComplexityOracleTest(unittest.TestCase):
    def test_script_records_output_complexity(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3477.shape_pair_exact_overlay_output_complexity_oracle.v1",
            "external_cpu_output_complexity_oracle_not_rtdl_runtime_dependency",
            "geometry_type_counts",
            "positive_geometry_type_counts",
            "max_polygon_components_per_row",
            "max_output_vertices_per_row",
            "as_cupy_ordinal_columns",
            "claim_boundary",
        ):
            self.assertIn(phrase, text)

    def test_report_preserves_contract_question(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "output full intersection geometry",
            "scalar exact-area continuation",
            "streamed output-geometry contract",
            "external CPU oracle evidence",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3477 pod artifact pending")
    def test_pod_artifact_records_complexity(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3477.shape_pair_exact_overlay_output_complexity_oracle.v1")
        self.assertEqual(payload["goal"], 3477)
        self.assertEqual(
            payload["oracle_dependency_scope"],
            "external_cpu_output_complexity_oracle_not_rtdl_runtime_dependency",
        )
        complexity = payload["first_run_complexity"]
        self.assertEqual(complexity["exception_count"], 0)
        self.assertGreater(complexity["positive_area_row_count"], 0)
        self.assertGreater(complexity["total_exact_area"], 0.0)
        self.assertGreaterEqual(complexity["max_output_vertices_per_row"], 0)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
