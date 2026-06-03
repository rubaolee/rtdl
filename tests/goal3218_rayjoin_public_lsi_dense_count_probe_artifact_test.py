from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3218_rayjoin_public_lsi_dense_count_probe_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3218_rayjoin_public_lsi_dense_count_probe_2026-06-03.md"


class Goal3218RayJoinPublicLsiDenseCountProbeArtifactTest(unittest.TestCase):
    def test_artifact_records_public_lsi_dense_count_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3218)
        self.assertEqual(data["schema"], "rtdl.goal3218.rayjoin_public_lsi_dense_count_probe.v1")
        self.assertEqual(data["commit"], "34cd58f4b99d66ef1d4f491612633be83328eb19")
        self.assertIn("NVIDIA A40", data["hardware"]["nvidia_smi"])
        self.assertTrue(data["hardware"]["nvcc_version"])
        self.assertEqual(data["repeats"], 5)
        self.assertEqual(data["warmups"], 1)
        self.assertEqual(len(data["rows"]), 6)

        for row in data["rows"]:
            self.assertTrue(row["validation"]["counts_match"])
            self.assertFalse(row["measurements"]["include_rows_measured"])
            self.assertLess(row["medians"]["dense_over_compact_ratio"], 0.15)
            self.assertGreater(row["left_segment_count"], 3000)
            self.assertGreater(row["right_segment_count"], 800)
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["release_authorized"])

    def test_report_interprets_results_without_overclaim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "bounded public RayJoin-style Brazil county/soil CDB slices",
            "Measured repetitions: `include_rows=False`",
            "All six rows have `counts_match: true`",
            "not only visible on synthetic all-crossing fixtures",
            "native code sees only a generic segment-pair left-id count device-column primitive",
            "does not authorize release",
            "RayJoin paper\nreproduction claims",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
