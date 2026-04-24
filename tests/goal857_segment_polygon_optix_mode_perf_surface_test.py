from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class Goal857SegmentPolygonOptixModePerfSurfaceTest(unittest.TestCase):
    def test_segment_polygon_perf_runner_propagates_optix_mode(self) -> None:
        module = __import__("scripts.goal726_segment_polygon_compact_summary_perf", fromlist=["run"])
        observed: list[tuple[str, str, str]] = []

        def fake_run_case(backend: str, dataset: str, output_mode: str, optix_mode: str = "auto"):
            observed.append((backend, output_mode, optix_mode))
            if output_mode == "rows":
                return {
                    "row_count": 10,
                    "summary_source": "segment_polygon_anyhit_rows",
                }
            return {
                "row_count": 4,
                "summary_source": "segment_polygon_hitcount",
            }

        with mock.patch.object(module.app, "run_case", side_effect=fake_run_case):
            payload = module.run(backend="optix", copies=(16,), repeats=2, optix_mode="native")

        self.assertEqual(payload["optix_mode"], "native")
        self.assertEqual(payload["cases"][0]["optix_mode"], "native")
        self.assertIn(("optix", "rows", "native"), observed)
        self.assertIn(("optix", "segment_counts", "native"), observed)

    def test_road_hazard_perf_runner_propagates_optix_mode(self) -> None:
        module = __import__("scripts.goal729_road_hazard_compact_output_perf", fromlist=["run"])
        observed: list[tuple[str, str, str]] = []

        def fake_run_case(backend: str, *, copies: int, output_mode: str, optix_mode: str = "auto"):
            observed.append((backend, output_mode, optix_mode))
            return {
                "row_count": 12,
                "priority_segment_count": 3,
                "priority_segments": [1, 2, 3],
            }

        with mock.patch.object(module.app, "run_case", side_effect=fake_run_case):
            payload = module.run(backend="optix", copies=(32,), repeats=2, optix_mode="host_indexed")

        self.assertEqual(payload["optix_mode"], "host_indexed")
        self.assertEqual(payload["cases"][0]["optix_mode"], "host_indexed")
        self.assertIn(("optix", "rows", "host_indexed"), observed)
        self.assertIn(("optix", "priority_segments", "host_indexed"), observed)

    def test_cli_writes_optix_mode_into_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "payload.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal726_segment_polygon_compact_summary_perf.py",
                    "--backend",
                    "cpu_python_reference",
                    "--optix-mode",
                    "native",
                    "--copies",
                    "4",
                    "--repeats",
                    "1",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            summary = json.loads(completed.stdout)
            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(summary["optix_mode"], "not_applicable")
        self.assertEqual(payload["optix_mode"], "not_applicable")
        self.assertEqual(payload["cases"][0]["optix_mode"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
