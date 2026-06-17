from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from examples.current.research_benchmarks.rtnn import rtdl_rtnn_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
REPORT = ROOT / "docs/reports/goal4503_v3_0_m107_rtnn_point_file_front_door_2026-06-17.md"


class Goal4503V30M107RtnnPointFileFrontDoorTest(unittest.TestCase):
    def test_cli_exposes_point_file_for_prepared_optix_route(self) -> None:
        help_text = subprocess.check_output(
            [sys.executable, str(APP), "--help"],
            cwd=ROOT,
            text=True,
        )
        self.assertIn("--point-file", help_text)
        self.assertIn("prepared_optix_ranked_summary", help_text)

    def test_external_point_file_uses_full_batch_without_generation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rtdl_rtnn_m107_") as tmp:
            point_file = Path(tmp) / "points.csv"
            point_file.write_text(
                "0.0,0.0,0.0\n1.0,0.0,0.0\n0.0,1.0,0.0\n",
                encoding="utf-8",
            )

            def fake_runner(args):
                return {
                    "ok": True,
                    "point_file": str(args.point_file),
                    "query_batch_size": args.query_batch_size,
                    "result_mode": args.result_mode,
                    "query_count": 3,
                    "search_count": 3,
                    "ranked_aggregate_summary": {
                        "row_count": 3,
                        "bounded_neighbor_count": 3,
                        "nearest_id_checksum": 3,
                        "kth_id_checksum": 3,
                        "sum_distance": 0.0,
                    },
                }

            with mock.patch(
                "scripts.goal2348_rtnn_v2_2_external_runner.generate_point_file"
            ) as generate, mock.patch(
                "scripts.goal2348_rtnn_v2_2_external_runner.run_rtdl_batched_3d_neighbors",
                side_effect=fake_runner,
            ):
                payload = app.rtnn_prepared_optix_ranked_summary_payload(
                    point_count=None,
                    radius=1.0,
                    k=50,
                    repeat=2,
                    query_batch_size=None,
                    distribution="uniform",
                    seed=20260519,
                    point_file=point_file,
                )

        generate.assert_not_called()
        self.assertEqual(3, payload["point_count"])
        self.assertEqual(3, payload["query_batch_size"])
        self.assertTrue(payload["external_point_file_used"])
        self.assertFalse(payload["generated_input"]["generated"])
        self.assertEqual("external_point_file", payload["generated_input"]["source"])
        self.assertEqual("ranked-summary-aggregate-prepared-query-batch-float32", payload["runner_payload"]["result_mode"])
        self.assertEqual(3, payload["runner_payload"]["query_batch_size"])
        self.assertIn("fixed_radius_neighbors_3d_ranked_summary", json.dumps(payload["prepared_session_residency"], sort_keys=True))

    def test_m107_report_and_readme_document_point_file_route(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn("--point-file", report)
        self.assertIn("external_point_file_used", report)
        self.assertIn("goal4503_rtnn_kitti_1m_app_point_file", report)
        self.assertIn("--point-file", readme)
        self.assertIn("external_point_file_used", readme)


if __name__ == "__main__":
    unittest.main()
