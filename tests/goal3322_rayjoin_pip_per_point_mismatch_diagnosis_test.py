from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.json"
EXPECTED_COMMIT = "568d95227cf6c83638ecdc4a86d2500d1d75d29f"


class Goal3322RayJoinPipPerPointMismatchDiagnosisTest(unittest.TestCase):
    def test_artifact_records_structured_county_overcount_and_soil_match(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3322.rayjoin_pip_per_point_mismatch_diagnosis.v1")
        self.assertEqual(data["goal"], 3322)
        self.assertEqual(data["rtdl_commit"], EXPECTED_COMMIT)
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["query_axis"], "z_point")
        self.assertEqual(data["boundary_mode"], "inclusive")

        rows = {row["label"]: row for row in data["rows"]}
        self.assertEqual(set(rows), {"county_fail", "soil_pass"})

        county = rows["county_fail"]
        self.assertEqual(county["exact_total"], 1417)
        self.assertEqual(county["fast_total"], 1429)
        self.assertEqual(county["delta_total"], 12)
        self.assertEqual(county["mismatch_point_count"], 7)
        self.assertEqual(county["positive_delta_count"], 7)
        self.assertEqual(county["negative_delta_count"], 0)
        self.assertEqual(county["mismatch_sample"][0]["point_id"], 522)
        self.assertEqual(county["mismatch_sample"][0]["exact"], 2)
        self.assertEqual(county["mismatch_sample"][0]["fast"], 3)
        self.assertTrue(county["point_id_count_metadata"]["device_resident"])
        self.assertFalse(county["point_id_count_metadata"]["true_zero_copy_authorized"])

        soil = rows["soil_pass"]
        self.assertEqual(soil["exact_total"], 1471)
        self.assertEqual(soil["fast_total"], 1471)
        self.assertEqual(soil["delta_total"], 0)
        self.assertEqual(soil["mismatch_point_count"], 0)
        self.assertEqual(soil["mismatch_sample"], [])

        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)

    def test_report_names_the_design_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3322 - RayJoin PIP Per-Point Mismatch Diagnosis", text)
        self.assertIn("all mismatches are overcounts", text)
        self.assertIn("duplicate coordinates", text)
        self.assertIn("generic face/topology-aware closed-shape membership/count contract", text)
        self.assertIn("not be another RayJoin-specific native function", text)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", text)


if __name__ == "__main__":
    unittest.main()

