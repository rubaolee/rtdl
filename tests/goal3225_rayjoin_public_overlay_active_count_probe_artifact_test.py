from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.stdout"


class Goal3225RayJoinPublicOverlayActiveCountProbeArtifactTest(unittest.TestCase):
    def test_pod_artifact_records_public_overlay_active_count_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3225)
        self.assertEqual(data["schema"], "rtdl.goal3225.rayjoin_public_overlay_active_count_probe.v1")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["commit"], "021ee498711eb5ad8b21231872930b35461ed4a6")
        self.assertEqual(data["hardware"]["nvidia_smi"], "NVIDIA A40, 570.211.01")
        self.assertIn("CUDA Version", data["hardware"]["cuda_driver_query"])
        self.assertIn("release 12.8", data["hardware"]["nvcc_version"])
        self.assertEqual(data["hardware"]["rtdl_optix_library"], "/root/rtdl_goal3151/build/librtdl_optix.so")

        rows = {row["case"]: row for row in data["rows"]}
        self.assertEqual(set(rows), {"overlay_county128_soil128", "overlay_county256_soil256"})
        self.assertEqual(rows["overlay_county128_soil128"]["expected_active_seed_count"], 1)
        self.assertEqual(rows["overlay_county128_soil128"]["observed_counts"], [1, 1, 1, 1, 1])
        self.assertTrue(rows["overlay_county128_soil128"]["counts_match"])
        self.assertEqual(rows["overlay_county256_soil256"]["expected_active_seed_count"], 9)
        self.assertEqual(rows["overlay_county256_soil256"]["observed_counts"], [9, 9, 9, 9, 9])
        self.assertTrue(rows["overlay_county256_soil256"]["counts_match"])

    def test_artifact_preserves_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        boundary = data["claim_boundary"]
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["release_authorized"])

        for row in data["rows"]:
            row_boundary = row["claim_boundary"]
            self.assertFalse(row_boundary["public_speedup_claim_authorized"])
            self.assertFalse(row_boundary["rt_core_speedup_claim_authorized"])
            self.assertFalse(row_boundary["rayjoin_paper_reproduction_claim_authorized"])
            self.assertFalse(row_boundary["rtdl_beats_rayjoin_claim_authorized"])
            self.assertFalse(row_boundary["release_authorized"])

    def test_report_and_stdout_are_consistent(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        stdout = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "bounded public RayJoin-style Brazil",
            "active_seed_count",
            "overlay_active_pair_dependency_count",
            "SHAPE_PAIR_RELATION_FLAGS_2D",
            "does not authorize release",
            "row overlay continuation path remains deferred",
        ):
            self.assertIn(phrase, report)
        self.assertIn("[goal3225] wrote", stdout)
        self.assertIn("repeat overlay_county256_soil256/prepared_overlay_active_count 5/5", stdout)


if __name__ == "__main__":
    unittest.main()
