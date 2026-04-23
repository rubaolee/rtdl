from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal827CloudArtifactContractAuditTest(unittest.TestCase):
    def test_goal827_report_exists_and_names_fail_closed_contract_audit(self) -> None:
        report = ROOT / "docs" / "reports" / "goal827_cloud_artifact_contract_audit_2026-04-23.md"
        text = report.read_text(encoding="utf-8")

        self.assertIn("cloud_claim_contract", text)
        self.assertIn("required_phase_groups", text)
        self.assertIn("needs_attention", text)

    def test_contract_missing_phase_fails_closed(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal827_test_missing_phase_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "app": "outlier_detection",
                                "cloud_claim_contract": {
                                    "claim_scope": "prepared fixed-radius threshold summary traversal only",
                                    "non_claim": "not row-output",
                                    "required_phase_groups": [
                                        "prepared_optix_warm_query_sec",
                                        "prepared_optix_postprocess_sec",
                                    ],
                                },
                                "prepared_optix_warm_query_sec": {
                                    "min_sec": 0.1,
                                    "median_sec": 0.2,
                                    "max_sec": 0.3,
                                },
                            }
                        ]
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
                                    "app": "outlier_detection",
                                    "path_name": "prepared_fixed_radius_density_summary",
                                    "claim_scope": "prepared fixed-radius threshold summary traversal only",
                                    "non_claim": "not a whole-app RTX speedup claim",
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal827_test_missing_phase_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)

            self.assertEqual(payload["status"], "needs_attention")
            self.assertEqual(payload["rows"][0]["cloud_contract_status"], "missing_required_phases")
            self.assertEqual(payload["rows"][0]["cloud_contract_missing_phases"], ["prepared_optix_postprocess_sec"])
        finally:
            artifact_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
