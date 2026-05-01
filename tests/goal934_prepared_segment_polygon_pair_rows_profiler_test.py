from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal934_prepared_segment_polygon_pair_rows_optix_profiler as profiler


ROOT = Path(__file__).resolve().parents[1]


class Goal934PreparedSegmentPolygonPairRowsProfilerTest(unittest.TestCase):
    def test_dry_run_records_pair_row_contract_without_optix(self) -> None:
        payload = profiler.run_profile(
            copies=2,
            iterations=3,
            output_capacity=64,
            mode="dry-run",
            skip_validation=False,
        )

        self.assertEqual(payload["schema_version"], "goal934_prepared_segment_polygon_pair_rows_optix_contract_v1")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["scenario"], "segment_polygon_anyhit_rows_prepared_bounded")
        self.assertEqual(payload["result"]["emitted_count"], 22)
        self.assertFalse(payload["result"]["overflowed"])
        self.assertIn("optix_query_sec", payload["cloud_claim_contract"]["required_phase_groups"])
        self.assertIn("bounded output", payload["cloud_claim_contract"]["claim_scope"])

    def test_dry_run_fails_when_capacity_is_too_small_for_reference_rows(self) -> None:
        payload = profiler.run_profile(
            copies=2,
            iterations=3,
            output_capacity=4,
            mode="dry-run",
            skip_validation=False,
        )

        self.assertEqual(payload["status"], "fail")
        self.assertFalse(payload["strict_pass"])
        self.assertTrue(payload["result"]["overflowed"])
        self.assertIn("smaller than CPU reference row count", payload["strict_failures"][0])

    def test_cli_writes_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output = Path(tmpdir) / "goal934.json"
            rc = profiler.main(
                [
                    "--copies",
                    "1",
                    "--mode",
                    "dry-run",
                    "--output-capacity",
                    "32",
                    "--output-json",
                    str(output),
                ]
            )

            self.assertEqual(rc, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["scenario"], "segment_polygon_anyhit_rows_prepared_bounded")

    def test_artifact_analyzer_accepts_goal934_schema(self) -> None:
        analyzer = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            tmp = Path(tmpdir)
            artifact = tmp / "pair_rows.json"
            artifact.write_text(
                json.dumps(
                    {
                        "schema_version": "goal934_prepared_segment_polygon_pair_rows_optix_contract_v1",
                        "mode": "run",
                        "output_capacity": 64,
                        "strict_pass": True,
                        "strict_failures": [],
                        "cloud_claim_contract": {
                            "claim_scope": "prepared bounded pair rows",
                            "non_claim": "not unbounded rows",
                            "required_phase_groups": [
                                "input_build_sec",
                                "cpu_reference_total_sec",
                                "optix_prepare_sec",
                                "optix_query_sec",
                                "python_postprocess_sec",
                                "validation_sec",
                                "optix_close_sec",
                                "emitted_count",
                                "copied_count",
                                "overflowed",
                            ],
                        },
                        "timings_sec": {
                            "input_build_sec": 0.1,
                            "cpu_reference_total_sec": 0.2,
                            "optix_prepare_sec": 0.3,
                            "optix_query_sec": {"median_sec": 0.4},
                            "python_postprocess_sec": {"median_sec": 0.01},
                            "validation_sec": {"median_sec": 0.0},
                            "optix_close_sec": 0.01,
                        },
                        "result": {
                            "matches_oracle": True,
                            "emitted_count": 22,
                            "copied_count": 22,
                            "overflowed": False,
                        },
                    }
                ),
                encoding="utf-8",
            )
            summary = tmp / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "dry_run": False,
                        "results": [
                            {
                                "app": "segment_polygon_anyhit_rows",
                                "path_name": "segment_polygon_anyhit_rows_prepared_bounded_gate",
                                "claim_scope": "prepared bounded pair rows",
                                "non_claim": "not unbounded rows",
                                "baseline_review_contract": {
                                    "status": "required_before_public_speedup_claim",
                                    "minimum_repeated_runs": 3,
                                    "requires_correctness_parity": True,
                                    "requires_phase_separation": True,
                                    "forbidden_comparison": "none",
                                    "comparable_metric_scope": "same",
                                    "required_baselines": ["cpu"],
                                    "required_phases": ["optix_query_sec"],
                                    "claim_limit": "none",
                                },
                                "result": {
                                    "status": "ok",
                                    "returncode": 0,
                                    "command": ["python3", "x", "--output-json", str(artifact.relative_to(ROOT))],
                                },
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = analyzer.analyze(summary)

        self.assertEqual(payload["status"], "ok")
        row = payload["rows"][0]
        self.assertEqual(row["schema_version"], "goal934_prepared_segment_polygon_pair_rows_optix_contract_v1")
        self.assertEqual(row["cloud_contract_status"], "ok")
        self.assertTrue(row["matches_oracle"])
        self.assertEqual(row["warm_query_median_sec"], 0.4)
        self.assertEqual(row["emitted_count"], 22)

    def test_rejects_invalid_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_capacity must be positive"):
            profiler.run_profile(
                copies=1,
                iterations=1,
                output_capacity=0,
                mode="dry-run",
                skip_validation=False,
            )


if __name__ == "__main__":
    unittest.main()
