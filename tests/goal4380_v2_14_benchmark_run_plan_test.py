from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_14_benchmark_run_plan import (
    HUMAN_SCALE_SELECTION_BY_ROW_ID,
    markdown_v2_14_benchmark_run_plan,
    v2_14_benchmark_run_plan_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_14_benchmark_run_plan.py"
HUMAN_SCALE_SCRIPT = ROOT / "scripts" / "rtdl_human_scale_rt_vs_embree_comparison.py"


class Goal4380V214BenchmarkRunPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = v2_14_benchmark_run_plan_packet(
            python_executable="python3",
            output_dir="docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14",
        )

    def test_packet_is_executable_plan_not_release_evidence(self) -> None:
        self.assertEqual("accept_executable_plan", self.packet["validation"]["status"], self.packet["validation"]["errors"])
        self.assertFalse(self.packet["summary"]["release_ready"])
        self.assertEqual(12, self.packet["summary"]["row_count"])
        self.assertEqual(11, self.packet["summary"]["human_scale_row_count"])
        self.assertEqual(1, self.packet["summary"]["overlay_row_count"])
        self.assertEqual(0, self.packet["summary"]["public_wording_authorized_count"])
        self.assertEqual(0, self.packet["summary"]["release_evidence_count"])

    def test_plan_covers_cleanup_rows_with_expected_runners(self) -> None:
        by_id = {row["row_id"]: row for row in self.packet["rows"]}
        self.assertEqual(
            set(HUMAN_SCALE_SELECTION_BY_ROW_ID) | {"spatial_rayjoin_overlay"},
            set(by_id),
        )
        for row_id, selection in HUMAN_SCALE_SELECTION_BY_ROW_ID.items():
            row = by_id[row_id]
            self.assertEqual("human_scale_same_contract", row["runner"], row_id)
            self.assertIn("--only", row["command"], row_id)
            self.assertIn(selection, row["command"], row_id)
            self.assertIn("scripts/rtdl_human_scale_rt_vs_embree_comparison.py", row["command"], row_id)
            self.assertFalse(row["release_evidence"], row_id)
            self.assertFalse(row["public_wording_authorized"], row_id)

        overlay = by_id["spatial_rayjoin_overlay"]
        self.assertEqual("rayjoin_section57_overlay", overlay["runner"])
        for required in (
            "scripts/rayjoin_section57_overlay_matrix.py",
            "run",
            "--query-exec",
            "--polyover-exec",
            "--summary-json",
        ):
            self.assertIn(required, overlay["command"])
        self.assertIn("author hot-compute parity", overlay["claim_boundary"])

    def test_markdown_renderer_contains_commands_and_boundary(self) -> None:
        markdown = markdown_v2_14_benchmark_run_plan(self.packet)
        self.assertIn("Goal4380 v2.14 Executable Benchmark Run Plan", markdown)
        self.assertIn("spatial_rayjoin_overlay", markdown)
        self.assertIn("scripts/rayjoin_section57_overlay_matrix.py run", markdown)
        self.assertIn("author-hot-compute parity wording", markdown)
        self.assertIn("not release evidence", markdown)

    def test_script_writes_run_plan_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "plan.json"
            out_md = Path(tmp) / "plan.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--python-executable",
                    "python3",
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept_executable_plan", payload["validation"]["status"])
            self.assertIn("spatial_rayjoin_overlay", report)

    def test_human_scale_runner_supports_only_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(HUMAN_SCALE_SCRIPT),
                    "--dry-run",
                    "--only",
                    "spatial_rayjoin_lsi",
                    "--output-dir",
                    str(Path(tmp) / "dry"),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout[completed.stdout.find("{") :])
            labels = {row["label"] for row in payload["runs"]}
            self.assertEqual(
                {
                    "rayjoin_lsi_optix_dense_r20000",
                    "rayjoin_lsi_embree_t8_r2000",
                    "rayjoin_lsi_embree_t64_r2000",
                },
                labels,
            )


if __name__ == "__main__":
    unittest.main()
