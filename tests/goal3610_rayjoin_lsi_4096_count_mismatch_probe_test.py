from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3610_rayjoin_lsi_4096_count_mismatch_probe_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3610_rayjoin_lsi_4096_count_mismatch_probe_a5000" / "summary.json"
SCRIPT = ROOT / "scripts" / "goal3610_rayjoin_lsi_4096_mismatch_probe.py"


class Goal3610RayJoinLsi4096CountMismatchProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_artifact_records_concentrated_lsi_mismatch(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3610.rayjoin_lsi_4096_count_mismatch_probe.v1")
        self.assertEqual(payload["goal"], 3610)
        self.assertEqual(payload["cupy_total"], 4977)
        self.assertEqual(payload["rtdl_optix_total"], 4985)
        self.assertEqual(payload["diff_count"], 8)
        self.assertEqual(payload["delta_sum"], 8)
        self.assertEqual(payload["left_segment_count"], 68840)
        self.assertEqual(payload["right_segment_count"], 114534)
        self.assertEqual(payload["candidate_pair_count"], 7884520560)

    def test_each_sample_is_one_extra_rtdl_hit(self):
        for row in self.payload["diff_sample"]:
            with self.subTest(left_id=row["left_id"]):
                self.assertEqual(row["delta"], 1)
                self.assertEqual(row["rtdl_optix"], row["cupy"] + 1)
                self.assertEqual(len(row["segment"]), 4)

    def test_report_and_script_define_repair_boundary(self):
        self.assertIn("same-contract definition problem", self.report)
        self.assertIn("near-degenerate segment policy", self.report)
        self.assertIn("generic robust segment-pair intersection contract", self.report)
        self.assertIn("include_rows=True", self.script)
        self.assertIn("flags.reshape((left_count, right_count)).sum(axis=1)", self.script)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
