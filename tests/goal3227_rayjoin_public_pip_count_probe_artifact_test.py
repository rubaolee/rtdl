from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3227_rayjoin_public_pip_count_probe_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3227_rayjoin_public_pip_count_probe_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3227_rayjoin_public_pip_count_probe_2026-06-03.stdout"


class Goal3227RayJoinPublicPipCountProbeArtifactTest(unittest.TestCase):
    def test_pod_artifact_records_public_pip_count_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3227)
        self.assertEqual(data["schema"], "rtdl.goal3227.rayjoin_public_pip_count_probe.v1")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["commit"], "92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3")
        self.assertEqual(data["hardware"]["nvidia_smi"], "NVIDIA A40, 570.211.01")
        self.assertIn("CUDA Version", data["hardware"]["cuda_driver_query"])
        self.assertIn("release 12.8", data["hardware"]["nvcc_version"])
        self.assertEqual(data["hardware"]["rtdl_optix_library"], "/root/rtdl_goal3151/build/librtdl_optix.so")

        self.assertEqual(len(data["rows"]), 1)
        row = data["rows"][0]
        self.assertEqual(row["case"], "pip_county512")
        self.assertEqual(row["expected_positive_assignment_count"], 1430)
        self.assertEqual(row["observed_counts"], [1430, 1430, 1430, 1430, 1430])
        self.assertTrue(row["counts_match"])

    def test_artifact_preserves_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        boundary = data["claim_boundary"]
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])
        self.assertFalse(boundary["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["release_authorized"])

        row_boundary = data["rows"][0]["claim_boundary"]
        self.assertFalse(row_boundary["public_speedup_claim_authorized"])
        self.assertFalse(row_boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(row_boundary["true_zero_copy_claim_authorized"])
        self.assertFalse(row_boundary["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(row_boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(row_boundary["release_authorized"])
        self.assertEqual(set(row_boundary), set(boundary))
        for measurement in data["rows"][0]["measurements"]["prepared_pip_count"]:
            measurement_boundary = measurement["claim_boundary"]
            self.assertEqual(set(measurement_boundary), set(boundary))
            self.assertTrue(all(value is False for value in measurement_boundary.values()))

    def test_report_and_stdout_are_consistent(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        stdout = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "public CDB PIP",
            "positive_assignment_count",
            "POINT_CLOSED_SHAPE_MEMBERSHIP_2D",
            "1430",
            "does not authorize release",
        ):
            self.assertIn(phrase, report)
        self.assertIn("[goal3227] wrote", stdout)
        self.assertIn("repeat pip_county512/prepared_pip_count 5/5", stdout)


if __name__ == "__main__":
    unittest.main()
