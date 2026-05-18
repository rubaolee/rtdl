import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal2292_rayjoin_current_prepared_comparison.py"
REPORT = ROOT / "docs" / "reports" / "goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json"


class Goal2312PreparedClosedShapeRawRowViewTest(unittest.TestCase):
    def test_runtime_exposes_generic_prepared_raw_row_view(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")
        start = text.index("class PreparedOptixPointClosedShapeMembership2D")
        end = text.index("def prepare_point_closed_shape_membership_2d_optix", start)
        body = text[start:end]

        self.assertIn('def run_raw(self, points, *, result_mode: str = "positive_hits") -> OptixRowView:', body)
        self.assertIn('field_names=("point_id", "shape_id", "membership")', body)
        self.assertIn("_free_on_close=False", body)
        self.assertIn("def run(self, points, *, result_mode: str = \"positive_hits\")", body)
        self.assertIn("view = self.run_raw(points, result_mode=result_mode)", body)

    def test_rayjoin_comparison_uses_row_view_not_python_dict_materialization(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("def run_positive_raw_count() -> int:", text)
        self.assertIn('rows = prepared.run_raw(packed_points, result_mode="positive_hits")', text)
        self.assertIn("return int(rows.row_count)", text)
        self.assertNotIn('lambda: len(prepared.run(packed_points, result_mode="positive_hits"))', text)

    def test_pod_artifact_records_single_digit_ms_positive_rows(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.rayjoin.current_prepared_comparison.v1")
        self.assertEqual(data["pip"]["positive_rows"]["values"], [8686] * data["repeats"])
        self.assertEqual(data["pip"]["scalar_count"]["values"], [8686] * data["repeats"])
        self.assertTrue(data["pip"]["row_count_parity"])
        self.assertLess(data["pip"]["positive_rows"]["median_sec"], 0.010)
        self.assertLess(data["pip"]["scalar_count"]["median_sec"], 0.010)
        self.assertLess(data["lsi"]["raw_rows"]["median_sec"], 0.011)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("2.68x improvement", text)
        self.assertIn("working at", text)
        self.assertIn("No RayJoin-specific primitive", text)
        self.assertIn("RTDL beats the RayJoin paper implementation", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("device-resident row-stream", text)


if __name__ == "__main__":
    unittest.main()
