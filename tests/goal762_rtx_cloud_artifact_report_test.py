from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal762RtxCloudArtifactReportTest(unittest.TestCase):
    def test_dry_run_summary_is_ok_without_benchmark_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "dry_run_summary.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal761_rtx_cloud_run_all.py",
                    "--dry-run",
                    "--only",
                    "robot_collision_screening",
                    "--output-json",
                    str(summary),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze", "to_markdown"])
            payload = module.analyze(summary)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["entry_count"], 1)
            self.assertEqual(payload["rows"][0]["artifact_status"], "dry_run_not_expected")
            markdown = module.to_markdown(payload)
            self.assertIn("does not authorize RTX speedup claims", markdown)

    def test_missing_artifact_after_ok_runner_needs_attention(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "dry_run": False,
                        "results": [
                            {
                                "app": "robot_collision_screening",
                                "path_name": "prepared_pose_flags",
                                "claim_scope": "prepared OptiX ray/triangle any-hit pose-flag summary",
                                "non_claim": "not continuous collision detection",
                                "result": {
                                    "status": "ok",
                                    "returncode": 0,
                                    "command": [
                                        "python3",
                                        "script.py",
                                        "--output-json",
                                        "docs/reports/does_not_exist_goal762.json",
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
            self.assertEqual(payload["rows"][0]["artifact_status"], "missing")

    def test_fixed_radius_scalar_summary_fields_are_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_scalar_summary_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "app": "outlier_detection",
                                "schema_version": "goal825_tier1_phase_contract_v1",
                                "cloud_claim_contract": {
                                    "claim_scope": "prepared fixed-radius threshold summary traversal only",
                                    "non_claim": "not row-output",
                                    "required_phase_groups": [
                                        "prepared_optix_warm_query_sec",
                                        "prepared_optix_postprocess_sec",
                                    ],
                                },
                                "result_mode": "threshold_count",
                                "prepared_optix_warm_query_sec": {
                                    "min_sec": 0.1,
                                    "median_sec": 0.2,
                                    "max_sec": 0.3,
                                },
                                "prepared_optix_postprocess_sec": {
                                    "min_sec": 0.0,
                                    "median_sec": 0.0,
                                    "max_sec": 0.0,
                                },
                                "prepared_output": {
                                    "threshold_reached_count": 6,
                                    "outlier_count": 2,
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
                                            "docs/reports/goal762_test_scalar_summary_tmp.json",
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
            self.assertEqual(row["result_mode"], "threshold_count")
            self.assertEqual(row["threshold_reached_count"], 6)
            self.assertEqual(row["warm_query_median_sec"], 0.2)
            self.assertEqual(row["postprocess_median_sec"], 0.0)
            self.assertEqual(row["cloud_contract_status"], "ok")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_ok_runner_with_missing_contract_needs_attention(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_missing_contract_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "app": "outlier_detection",
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
                                            "docs/reports/goal762_test_missing_contract_tmp.json",
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
            self.assertEqual(payload["rows"][0]["cloud_contract_status"], "missing")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_tier2_service_contract_artifact_is_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_service_contract_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "schema_version": "goal826_tier2_phase_contract_v1",
                        "cloud_claim_contract": {
                            "claim_scope": "prepared OptiX fixed-radius threshold traversal for coverage-gap compact summaries",
                            "non_claim": "not nearest-clinic row output",
                            "required_phase_groups": [
                                "input_build",
                                "optix_prepare",
                                "optix_query",
                                "python_postprocess",
                            ],
                        },
                        "scenario": {
                            "scenario": "service_coverage_gaps",
                            "mode": "optix",
                            "timings_sec": {
                                "input_build": 0.1,
                                "optix_prepare": 0.2,
                                "optix_query": 0.3,
                                "python_postprocess": 0.4,
                            },
                            "result": {
                                "native_summary_row_count": 8,
                            },
                        },
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
                                    "app": "service_coverage_gaps",
                                    "path_name": "prepared_gap_summary",
                                    "claim_scope": "prepared OptiX fixed-radius threshold traversal",
                                    "non_claim": "not whole app",
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal762_test_service_contract_tmp.json",
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
            self.assertEqual(row["schema_version"], "goal826_tier2_phase_contract_v1")
            self.assertEqual(row["cloud_contract_status"], "ok")
            self.assertEqual(row["warm_query_median_sec"], 0.3)
            self.assertEqual(row["native_summary_row_count"], 8)
        finally:
            artifact_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
