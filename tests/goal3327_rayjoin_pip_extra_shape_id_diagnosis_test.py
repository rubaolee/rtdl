import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3327_rayjoin_pip_extra_shape_id_diagnosis_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3327_rayjoin_pip_extra_shape_id_diagnosis_2026-06-04.md"


class Goal3327RayJoinPipExtraShapeIdDiagnosisTest(unittest.TestCase):
    def test_artifact_records_county_extra_shape_ids(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3327.rayjoin_pip_extra_shape_id_diagnosis.v1")
        county = next(item for item in data["datasets"] if "br_county_start256_count512" in item["dataset"])
        self.assertEqual(county["exact_row_count"], 1417)
        self.assertEqual(county["device_column_row_count"], 1429)
        self.assertEqual(county["delta_total"], 12)
        self.assertEqual(county["mismatch_point_count"], 7)
        self.assertEqual(county["positive_delta_count"], 7)
        self.assertEqual(county["negative_delta_count"], 0)
        self.assertFalse(county["overflow"])

        by_point = {int(row["point_id"]): row for row in county["known_mismatch_points"]}
        self.assertEqual(set(by_point), {522, 523, 538, 539, 540, 564, 565})
        self.assertEqual(by_point[522]["extra_shape_ids"], [521])
        self.assertEqual(by_point[523]["extra_shape_ids"], [521])
        self.assertEqual(by_point[538]["extra_shape_ids"], [418, 540])
        self.assertEqual(by_point[539]["extra_shape_ids"], [418, 540])
        self.assertEqual(by_point[540]["extra_shape_ids"], [535, 539])
        self.assertEqual(by_point[564]["extra_shape_ids"], [437, 559])
        self.assertEqual(by_point[565]["extra_shape_ids"], [437, 559])
        self.assertTrue(all(not row["missing_shape_ids"] for row in by_point.values()))

    def test_soil_control_remains_clean(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        soil = next(item for item in data["datasets"] if "br_soil_start256_count512" in item["dataset"])
        self.assertEqual(soil["exact_row_count"], 1471)
        self.assertEqual(soil["device_column_row_count"], 1471)
        self.assertEqual(soil["delta_total"], 0)
        self.assertEqual(soil["mismatch_point_count"], 0)
        self.assertEqual(soil["mismatch_sample"], [])

    def test_claims_stay_blocked(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for dataset in data["datasets"]:
            boundary = dataset["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["rayjoin_paper_reproduction_claim_authorized"])
            self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
            self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
            self.assertFalse(boundary["true_zero_copy_claim_authorized"])

    def test_report_states_design_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("topology-aware closed-shape membership/count contract", text)
        self.assertIn("CDB chain/face interpretation and RayJoin benchmark acceptance policy remain app code", text)
        self.assertIn("fast route must be rejected", text)
        self.assertIn("does not make the current fast route generally correct", text)


if __name__ == "__main__":
    unittest.main()
