from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import goal933_prepared_segment_polygon_optix_profiler as profiler


ROOT = Path(__file__).resolve().parents[1]


class Goal933PreparedSegmentPolygonProfilerTest(unittest.TestCase):
    def test_dry_run_segment_profile_records_contract_without_optix(self) -> None:
        payload = profiler.run_profile(
            scenario="segment_polygon_hitcount_prepared",
            copies=2,
            iterations=3,
            mode="dry-run",
            skip_validation=False,
        )

        self.assertEqual(payload["schema_version"], "goal933_prepared_segment_polygon_optix_contract_v1")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["scenario"], "segment_polygon_hitcount_prepared")
        self.assertIn("cpu_reference_total_sec", payload["timings_sec"])
        self.assertIn("optix_prepare_sec", payload["cloud_claim_contract"]["required_phase_groups"])
        self.assertIn("not a public speedup claim", payload["cloud_claim_contract"]["non_claim"])

    def test_dry_run_road_profile_records_priority_summary(self) -> None:
        payload = profiler.run_profile(
            scenario="road_hazard_prepared_summary",
            copies=2,
            iterations=3,
            mode="dry-run",
            skip_validation=False,
        )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["scenario"], "road_hazard_prepared_summary")
        self.assertEqual(payload["result"]["road_count"], 6)
        self.assertEqual(payload["result"]["hazard_count"], 6)
        self.assertGreater(payload["result"]["priority_segment_count"], 0)

    def test_road_run_profile_uses_threshold_count_not_row_materialization(self) -> None:
        class FakePrepared:
            def __init__(self):
                self.closed = False

            def count_at_least(self, roads, *, threshold):
                self.threshold = threshold
                self.road_count = len(roads)
                return 2

            def run(self, roads):
                raise AssertionError("road summary profiler should not materialize hit-count rows")

            def close(self):
                self.closed = True

        fake = FakePrepared()
        with mock.patch.object(profiler.rt, "prepare_optix_segment_polygon_hitcount_2d", return_value=fake):
            payload = profiler.run_profile(
                scenario="road_hazard_prepared_summary",
                copies=1,
                iterations=2,
                mode="run",
                skip_validation=True,
            )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["result"]["priority_segment_count"], 2)
        self.assertEqual(payload["result"]["actual_digest"], None)
        self.assertEqual(fake.threshold, 2)
        self.assertEqual(fake.road_count, 3)
        self.assertTrue(fake.closed)

    def test_segment_run_profile_uses_native_aggregate_not_row_materialization(self) -> None:
        class FakePrepared:
            def __init__(self):
                self.closed = False

            def aggregate(self, segments, *, positive_threshold):
                self.positive_threshold = positive_threshold
                self.segment_count = len(segments)
                return {"row_count": len(segments), "hit_sum": 3, "positive_count": 2}

            def run(self, segments):
                raise AssertionError("segment profiler should not materialize hit-count rows")

            def close(self):
                self.closed = True

        fake = FakePrepared()
        with mock.patch.object(profiler.rt, "prepare_optix_segment_polygon_hitcount_2d", return_value=fake):
            payload = profiler.run_profile(
                scenario="segment_polygon_hitcount_prepared",
                copies=2,
                iterations=2,
                mode="run",
                skip_validation=True,
        )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["result"]["actual_digest"]["row_count"], fake.segment_count)
        self.assertEqual(payload["result"]["actual_digest"]["hit_sum"], 3)
        self.assertEqual(payload["result"]["actual_digest"]["positive_count"], 2)
        self.assertEqual(fake.positive_threshold, 1)
        self.assertGreater(fake.segment_count, 0)
        self.assertTrue(fake.closed)

    def test_cli_writes_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output = Path(tmpdir) / "goal933.json"
            rc = profiler.main(
                [
                    "--scenario",
                    "road_hazard_prepared_summary",
                    "--copies",
                    "1",
                    "--mode",
                    "dry-run",
                    "--output-json",
                    str(output),
                ]
            )

            self.assertEqual(rc, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["scenario"], "road_hazard_prepared_summary")

    def test_artifact_analyzer_accepts_goal933_schema_for_segment_and_road(self) -> None:
        analyzer = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            tmp = Path(tmpdir)
            segment_artifact = tmp / "segment.json"
            road_artifact = tmp / "road.json"
            common = {
                "schema_version": "goal933_prepared_segment_polygon_optix_contract_v1",
                "mode": "run",
                "strict_pass": True,
                "strict_failures": [],
                "cloud_claim_contract": {
                    "claim_scope": "prepared OptiX custom-AABB segment/polygon traversal",
                    "non_claim": "not a public speedup claim",
                    "required_phase_groups": [
                        "input_build_sec",
                        "optix_prepare_sec",
                        "optix_query_sec",
                        "python_postprocess_sec",
                        "validation_sec",
                        "optix_close_sec",
                    ],
                },
                "timings_sec": {
                    "input_build_sec": 0.1,
                    "optix_prepare_sec": 0.2,
                    "optix_query_sec": {"median_sec": 0.3},
                    "python_postprocess_sec": {"median_sec": 0.01},
                    "validation_sec": {"median_sec": 0.4},
                    "optix_close_sec": 0.01,
                },
                "result": {"matches_oracle": True, "priority_segment_count": 2},
            }
            segment_artifact.write_text(
                json.dumps({**common, "scenario": "segment_polygon_hitcount_prepared", "dataset": "d"}),
                encoding="utf-8",
            )
            road_artifact.write_text(
                json.dumps({**common, "scenario": "road_hazard_prepared_summary", "copies": 8}),
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
                                "app": "segment_polygon_hitcount",
                                "path_name": "segment_polygon_hitcount_native_experimental",
                                "claim_scope": "prepared",
                                "non_claim": "not speedup",
                                "baseline_review_contract": {"status": "required_before_public_speedup_claim", "minimum_repeated_runs": 3, "requires_correctness_parity": True, "requires_phase_separation": True, "forbidden_comparison": "none", "comparable_metric_scope": "same", "required_baselines": ["cpu"], "required_phases": ["optix_query_sec"], "claim_limit": "none"},
                                "result": {"status": "ok", "returncode": 0, "command": ["python3", "x", "--output-json", str(segment_artifact.relative_to(ROOT))]},
                            },
                            {
                                "app": "road_hazard_screening",
                                "path_name": "road_hazard_native_summary_gate",
                                "claim_scope": "prepared",
                                "non_claim": "not speedup",
                                "baseline_review_contract": {"status": "required_before_public_speedup_claim", "minimum_repeated_runs": 3, "requires_correctness_parity": True, "requires_phase_separation": True, "forbidden_comparison": "none", "comparable_metric_scope": "same", "required_baselines": ["cpu"], "required_phases": ["optix_query_sec"], "claim_limit": "none"},
                                "result": {"status": "ok", "returncode": 0, "command": ["python3", "x", "--output-json", str(road_artifact.relative_to(ROOT))]},
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = analyzer.analyze(summary)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["rows"][0]["schema_version"], "goal933_prepared_segment_polygon_optix_contract_v1")
        self.assertEqual(payload["rows"][0]["cloud_contract_status"], "ok")
        self.assertTrue(payload["rows"][0]["matches_oracle"])
        self.assertEqual(payload["rows"][1]["cloud_contract_status"], "ok")
        self.assertEqual(payload["rows"][1]["priority_segment_count"], 2)

    def test_rejects_invalid_scenario(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported scenario"):
            profiler.run_profile(
                scenario="bad",
                copies=1,
                iterations=1,
                mode="dry-run",
                skip_validation=False,
            )


if __name__ == "__main__":
    unittest.main()
