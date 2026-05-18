from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2348_v2_2_rtnn_external_runner_2026-05-18.md"


def _load_runner():
    spec = importlib.util.spec_from_file_location("goal2348_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load goal2348 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal2348RtnnV22ExternalRunnerTest(unittest.TestCase):
    def test_parse_rtnn_timing_lines(self) -> None:
        runner = _load_runner()
        timings = runner.parse_rtnn_timings(
            "time search compute: 1.25 ms\n"
            "noise\n"
            "time result copy D2H: 0.50 ms\n"
            "time search compute: 1.75 ms\n"
        )
        self.assertEqual(timings["search compute"], [1.25, 1.75])
        self.assertEqual(timings["result copy D2H"], [0.5])

    def test_generate_point_file_is_deterministic_rtnn_xyz(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            first = pathlib.Path(tmp) / "a.txt"
            second = pathlib.Path(tmp) / "b.txt"
            runner.generate_uniform_point_file(first, point_count=4, dimension=2, seed=7)
            runner.generate_uniform_point_file(second, point_count=4, dimension=2, seed=7)
            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            rows = first.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(len(row.split(",")) == 3 for row in rows))
            self.assertTrue(all(row.endswith(",0.000000000") for row in rows))

    def test_cli_generate_writes_boundary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            point_file = pathlib.Path(tmp) / "points.txt"
            json_out = pathlib.Path(tmp) / "out.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "generate",
                    "--point-file",
                    str(point_file),
                    "--point-count",
                    "3",
                    "--dimension",
                    "3",
                    "--json-out",
                    str(json_out),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(payload["generated"]["format"], "rtnn_csv_xyz")
            self.assertFalse(payload["claim_boundary"]["paper_dataset"])
            self.assertTrue(payload["claim_boundary"]["synthetic_input_only"])

    def test_rtdl_smoke_loader_uses_public_record_shape(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('{"id": idx, "x": x, "y": y}', text)
        self.assertNotIn("rt.Point2D", text)

    def test_report_names_runner_as_next_harness(self) -> None:
        campaign = (
            ROOT
            / "docs"
            / "reports"
            / "goal2346_v2_2_rtnn_nearest_neighbor_campaign_2026-05-18.md"
        ).read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("pod-ready RTNN harness", campaign)
        self.assertIn("parse RTNN timing blocks into JSON", campaign)
        self.assertIn("scripts/goal2348_rtnn_v2_2_external_runner.py", report)
        self.assertIn("current-v2.1 2-D smoke evidence", report)
        self.assertIn("v2.2 3-D bounded-neighbor evidence", report)
        self.assertIn("accept-with-boundary", report)


if __name__ == "__main__":
    unittest.main()
