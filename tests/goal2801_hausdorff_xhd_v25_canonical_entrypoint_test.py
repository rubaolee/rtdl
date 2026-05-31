from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2801_hausdorff_xhd_v25_canonical_entrypoint.py"
REPORT = ROOT / "docs" / "reports" / "goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_consensus_2026-05-31.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2801_pod_artifacts"
    / "hausdorff_xhd_v25_canonical_entrypoint_4096.json"
)
CLEAN_POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2801_pod_artifacts"
    / "hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.json"
)


class Goal2801HausdorffXHDV25CanonicalEntrypointTest(unittest.TestCase):
    def test_entrypoint_uses_exact_cupy_grid_and_rtdl_optix_witness(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("cupy_grouped_grid_rawkernel", text)
        self.assertIn("hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness", text)
        self.assertIn("rtdl_beats_cupy_grid_claim_authorized", text)
        self.assertIn("native_engine_customization", text)

    def test_manifest_records_goal2801_hausdorff_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "hausdorff_xhd")

        self.assertEqual(row["tier"], "B")
        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2801_canonical_exact_entrypoint")
        self.assertIn("Goal2801", row["pod_evidence_status"])
        self.assertIn("CuPy grid", row["pod_evidence_status"])
        self.assertIn("auto-selection blocked", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_exact_match_without_speedup_claim(self) -> None:
        text = POD_ARTIFACT.read_text(encoding="utf-8")
        clean_text = CLEAN_POD_ARTIFACT.read_text(encoding="utf-8")

        for artifact_text in (text, clean_text):
            self.assertIn('"status": "pass"', artifact_text)
            self.assertIn('"matches_exact_baseline": true', artifact_text)
            self.assertIn('"uses_rt_cores": true', artifact_text)
            self.assertIn('"rtdl_beats_cupy_grid_claim_authorized": false', artifact_text)
            self.assertIn('"paper_reproduction_claim_authorized": false', artifact_text)
            self.assertIn('"native_engine_customization": false', artifact_text)

    def test_clean_pod_artifact_records_source_metadata(self) -> None:
        payload = json.loads(CLEAN_POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(payload["source_dirty"], [])
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertTrue(payload["rtdl"]["uses_rt_cores"])

    def test_report_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Hausdorff/X-HD v2.5 Canonical Entrypoint", report)
        self.assertIn("Goal2801", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("not a speedup claim", report)
        self.assertIn("CuPy grid", report)
        self.assertIn("clean-from-Git pod validated", report)
        self.assertIn("7a764ad8b742fb621c0fcc0154335f5b19c251f1", consensus)


if __name__ == "__main__":
    unittest.main()
