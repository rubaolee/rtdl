from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal831SegmentPolygonNativeArtifactContractTest(unittest.TestCase):
    def test_two_ai_consensus_artifacts_exist(self) -> None:
        ledger = ROOT / "docs" / "reports" / "goal831_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal831_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal831_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        ledger_text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", ledger_text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", ledger_text)
        self.assertIn("No Claude verdict is claimed", ledger_text)

    def test_goal807_gate_emits_claim_contract(self) -> None:
        module = __import__("scripts.goal807_segment_polygon_optix_mode_gate", fromlist=["_cloud_claim_contract"])
        contract = module._cloud_claim_contract()

        self.assertIn("segment/polygon hit-count traversal gate", contract["claim_scope"])
        self.assertIn("not pair-row any-hit output", contract["non_claim"])
        self.assertIn("records", contract["required_phase_groups"])
        self.assertIn("optix_native", contract["required_record_labels"])
        self.assertIn("keep deferred", contract["cloud_policy"])

    def test_artifact_report_extracts_segment_polygon_native_gate(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal831_test_segment_polygon_gate_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "schema_version": "goal831_segment_polygon_native_gate_contract_v1",
                        "cloud_claim_contract": {
                            "claim_scope": "experimental native custom-AABB segment/polygon hit-count traversal gate",
                            "non_claim": "not pair-row any-hit output",
                            "required_phase_groups": [
                                "records",
                                "strict_pass",
                                "strict_failures",
                                "status",
                            ],
                        },
                        "status": "pass",
                        "strict_pass": True,
                        "strict_failures": [],
                        "records": [
                            {
                                "label": "cpu_python_reference",
                                "status": "ok",
                                "sec": 1.0,
                                "parity_vs_cpu_python_reference": True,
                            },
                            {
                                "label": "optix_host_indexed",
                                "status": "ok",
                                "sec": 0.8,
                                "parity_vs_cpu_python_reference": True,
                            },
                            {
                                "label": "optix_native",
                                "status": "ok",
                                "sec": 0.6,
                                "parity_vs_cpu_python_reference": True,
                            },
                            {
                                "label": "postgis",
                                "status": "ok",
                                "sec": 0.7,
                                "parity_vs_cpu_python_reference": True,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "segment_polygon_hitcount",
                                    "path_name": "segment_polygon_hitcount_native_experimental",
                                    "claim_scope": "experimental native custom-AABB segment/polygon hit-count traversal",
                                    "non_claim": "not default public app behavior",
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal831_test_segment_polygon_gate_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)

            row = payload["rows"][0]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(row["artifact_status"], "ok")
            self.assertEqual(row["cloud_contract_status"], "ok")
            self.assertEqual(row["schema_version"], "goal831_segment_polygon_native_gate_contract_v1")
            self.assertTrue(row["strict_pass"])
            self.assertEqual(row["optix_native_status"], "ok")
            self.assertEqual(row["optix_native_sec"], 0.6)
            self.assertTrue(row["postgis_parity"])
        finally:
            artifact_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
