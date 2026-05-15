import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2048_cupy_witness_pod_validation_2026-05-15.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2048_cupy_witness_scaling.json"


class Goal2048CuPyWitnessPodValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_records_pod_and_boundary(self):
        self.assertEqual(self.artifact["host"], "66.92.198.234:11830")
        self.assertEqual(self.artifact["gpu"], "NVIDIA L4")
        self.assertEqual(self.artifact["driver"], "570.195.03")
        self.assertIn("no OptiX zero-copy handoff", self.artifact["claim_boundary"])

    def test_all_rows_match_oracle(self):
        self.assertEqual(len(self.artifact["rows"]), 6)
        for row in self.artifact["rows"]:
            self.assertTrue(row["matches_oracle"], row)
            self.assertEqual(
                row["partner_reference_contract"],
                "generic_group_argmin_then_global_argmax_with_witness",
            )

    def test_large_cupy_beats_numpy_reference(self):
        rows = {
            (row["backend"], row["point_count_a"]): row["elapsed_sec"]
            for row in self.artifact["rows"]
        }
        numpy_large = rows[("partner_numpy_exact", 2048)]
        cupy_large = rows[("partner_cupy_witness_exact", 2048)]
        self.assertLess(cupy_large, numpy_large / 4.0)

    def test_report_blocks_overclaims(self):
        required = [
            "not v2.0 release authorization",
            "OptiX zero-copy candidate-row handoff",
            "RT-core acceleration for exact Hausdorff witness extraction",
            "does not yet consume OptiX-written candidate rows",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
