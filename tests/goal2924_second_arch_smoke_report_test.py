from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2924_hausdorff_prepared_radius_guard_second_arch_smoke_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2924_second_arch_smoke_after_radius_guard"


class Goal2924SecondArchitectureSmokeReportTest(unittest.TestCase):
    def test_report_documents_fix_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2924",
            "prepared-radius",
            "radius exceeds prepared max_radius",
            "native engine ABI",
            "second-architecture smoke only",
            "not a release-performance claim",
            "next packet must be rerun",
        ):
            self.assertIn(phrase, text)

    def test_hausdorff_clean_smoke_passes_with_rt_path(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "hausdorff_gtx1070_1024.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual("6ad6314192e9db0f659c76acc58a20767a194697", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertIn("GTX 1070", payload["gpu"])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertTrue(payload["rtdl"]["uses_rt_cores"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

    def test_rtnn_clean_smoke_passes_all_distributions(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "rtnn_gtx1070_4096.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual("6ad6314192e9db0f659c76acc58a20767a194697", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertIn("GTX 1070", payload["gpu"])
        self.assertEqual(["uniform", "clustered", "shell"], [row["distribution"] for row in payload["rows"]])
        for row in payload["rows"]:
            self.assertEqual("pass", row["status"])
            self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rtnn_claim_authorized"])

    def test_toolchain_marks_second_architecture_smoke_only(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "toolchain_gtx1070.json").read_text(encoding="utf-8-sig"))

        self.assertEqual("6ad6314192e9db0f659c76acc58a20767a194697", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual("compute_61", payload["rtdl_optix_ptx_arch"])
        self.assertTrue(payload["optix_header_exists"])
        self.assertTrue(payload["rtdl_optix_library_exists"])
        self.assertTrue(payload["second_architecture_smoke_only"])
        self.assertFalse(payload["release_performance_evidence_authorized"])


if __name__ == "__main__":
    unittest.main()
