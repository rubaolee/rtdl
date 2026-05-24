from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/reports/goal2575_librts_rtspatial_authors_pod_evidence_2026-05-24.json"
REPORT = ROOT / "docs/reports/goal2575_librts_rtspatial_authors_pod_evidence_2026-05-24.md"


class LibRTSRTSpatialPodEvidenceTest(unittest.TestCase):
    def test_artifact_records_authors_code_environment_and_cuda_fix(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source"]["rtspatial_head"], "52509e8022abeab722f5a9a89d1917e8b481defe")
        self.assertEqual(artifact["pod"]["gpu"], "NVIDIA RTX A5000")
        self.assertEqual(artifact["toolchain"]["failed_cuda"]["failure"], "cudaErrorUnsupportedPtxVersion")
        self.assertEqual(artifact["toolchain"]["successful_cuda"]["version"], "12.6.85")

    def test_10k_counts_match_cpu_reference(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        row = artifact["results"]["uniform_10k_1k"]
        self.assertTrue(row["cpu_reference_counts_available"])
        self.assertTrue(row["all_counts_match_cpu_reference"])
        raw = json.loads(
            (ROOT / artifact["raw_summaries"]["uniform_10k_1k"]).read_text(encoding="utf-8")
        )
        for operation, expected in raw["cpu_counts"].items():
            self.assertEqual(raw["rtspatial"][operation]["results"], expected)
            self.assertTrue(raw["rtspatial"][operation]["matches_cpu_reference"])

    def test_large_rows_record_range_intersects_as_slowest(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for dataset in ("uniform_100k_1k", "uniform_1m_1k"):
            timings = artifact["results"][dataset]["rtspatial_query_ms"]
            self.assertGreater(timings["range_intersects"], timings["point_contains"])
            self.assertGreater(timings["range_intersects"], timings["range_contains"])

    def test_report_keeps_claim_boundary_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not an RTDL performance claim", text)
        self.assertIn("does not reproduce the paper's headline speedups yet", text)
        self.assertIn("No public speedup wording is authorized", text)


if __name__ == "__main__":
    unittest.main()
