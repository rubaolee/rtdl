from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3474_shape_pair_exact_overlay_area_shapely_oracle.py"
REPORT = ROOT / "docs" / "reports" / "goal3474_shape_pair_exact_overlay_area_shapely_oracle_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json"


class Goal3474ShapePairExactOverlayAreaShapelyOracleTest(unittest.TestCase):
    def test_script_defines_external_oracle_not_runtime_path(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3474.shape_pair_exact_overlay_area_shapely_oracle.v1",
            "external_cpu_correctness_oracle_not_rtdl_runtime_dependency",
            "prepare_rayjoin_optix_shape_pair_active_count",
            "as_cupy_ordinal_columns",
            "intersection(right_geometries",
            "all_oracle_exception_counts_zero",
            "claim_boundary",
        ):
            self.assertIn(phrase, text)

    def test_report_preserves_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "correctness oracle",
            "does not add that runtime primitive",
            "Shapely is optional external oracle tooling",
            "not an RTDL runtime dependency",
            "not as RTDL performance evidence",
        ):
            self.assertIn(phrase, text)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3474 pod artifact pending")
    def test_pod_artifact_records_exact_overlay_oracle(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3474.shape_pair_exact_overlay_area_shapely_oracle.v1")
        self.assertEqual(payload["goal"], 3474)
        self.assertEqual(
            payload["oracle_dependency_scope"],
            "external_cpu_correctness_oracle_not_rtdl_runtime_dependency",
        )
        self.assertTrue(payload["synthetic_exact_overlay_fixture"]["passed"])
        self.assertTrue(payload["all_row_counts_stable"])
        self.assertTrue(payload["all_total_exact_areas_stable"])
        self.assertTrue(payload["all_oracle_exception_counts_zero"])
        self.assertGreater(payload["row_counts"][0], 0)
        self.assertGreater(payload["positive_area_row_counts"][0], 0)
        self.assertGreater(payload["total_exact_areas"][0], 0.0)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
