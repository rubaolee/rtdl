from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/reports/goal2566_benchmark_app_evidence_manifest_2026-05-23.json"
REPORT = ROOT / "docs/reports/goal2566_benchmark_app_evidence_manifest_2026-05-23.md"


class Goal2566BenchmarkAppEvidenceManifestTest(unittest.TestCase):
    def test_manifest_schema_and_app_set(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.benchmark_app_evidence_manifest.v1")
        self.assertEqual(payload["snapshot_label"], "internal-benchmark-apps-2026-05-23")
        self.assertIn("does not authorize public release wording", payload["claim_boundary"])
        self.assertEqual(
            {app["app_id"] for app in payload["apps"]},
            {"rt_dbscan", "robot_collision", "raydb_style", "barnes_hut"},
        )

    def test_manifest_paths_are_reviewable(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for path in payload["consensus_sources"]:
            self.assertTrue((ROOT / path).exists(), path)
        for app in payload["apps"]:
            self.assertTrue((ROOT / app["example_path"]).exists(), app["example_path"])
            self.assertTrue((ROOT / app["closeout_report"]).exists(), app["closeout_report"])
            for artifact in app["performance_artifacts"]:
                self.assertTrue((ROOT / artifact).exists(), artifact)

    def test_manifest_keeps_claim_flags_bounded(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for app in payload["apps"]:
            self.assertFalse(app["native_engine_app_specific_abi"], app["app_id"])
            self.assertFalse(app["authors_code_reproduction_authorized"], app["app_id"])
            self.assertFalse(app["public_speedup_authorized"], app["app_id"])
            self.assertIn("claim_boundary", app)
            self.assertGreaterEqual(len(app["primary_primitives"]), 3)
            self.assertGreaterEqual(len(app["language_runtime_contributions"]), 3)

    def test_report_records_manifest_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2566", text)
        self.assertIn("RT-DBSCAN", text)
        self.assertIn("Robot collision screening", text)
        self.assertIn("RayDB-style columnar aggregate", text)
        self.assertIn("Barnes-Hut / RT-BarnesHut-style", text)
        self.assertIn("review infrastructure only", text)


if __name__ == "__main__":
    unittest.main()
