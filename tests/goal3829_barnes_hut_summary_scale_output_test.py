from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "apps" / "simulation" / "rtdl_barnes_hut_force_app.py"
BENCHMARK = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal3829_barnes_hut_summary_scale_output_2026-06-07.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3828_current_benchmark_scale_profiles_a5000" / "summary.json"


class Goal3829BarnesHutSummaryScaleOutputTest(unittest.TestCase):
    def test_partner_exact_force_records_checksums_for_summary_output(self) -> None:
        text = APP.read_text(encoding="utf-8")
        self.assertIn('payload["checksum_force_x"]', text)
        self.assertIn('payload["checksum_force_y"]', text)
        self.assertIn('if output_mode == "full"', text)

    def test_benchmark_wrapper_exposes_force_output_mode(self) -> None:
        text = BENCHMARK.read_text(encoding="utf-8")
        self.assertIn("force_output_mode: str = \"full\"", text)
        self.assertIn("--force-output-mode", text)
        self.assertIn("force_summary", text)
        self.assertIn("output_mode=force_output_mode", text)

    def test_scale_profile_uses_summary_output_for_barnes_hut(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "barnes_hut")
        command = row["command"]
        self.assertIn("--force-output-mode", command)
        mode_index = command.index("--force-output-mode")
        self.assertEqual(command[mode_index + 1], "force_summary")
        self.assertEqual(row["expected_runtime_class"], "safe_summary_output")

    def test_report_records_non_authorizing_output_hygiene_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        lower_text = " ".join(text.lower().split())
        for phrase in (
            "Goal3829",
            "bounded summary output",
            "does not authorize release action",
            "A5000 scale-profile artifact",
            "3400 bytes",
        ):
            self.assertIn(phrase, text)
        self.assertIn("does not change the numba force kernel", lower_text)
        self.assertIn("does not add rt-core acceleration", lower_text)

    def test_a5000_artifact_uses_summary_output_for_barnes_hut(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        row = next(row for row in payload["rows"] if row["row_id"] == "barnes_hut_numba_scale_default_8192")

        self.assertEqual(row["status"], "pass")
        self.assertLess(row["stdout_bytes"], 10_000)
        self.assertIn("--force-output-mode", row["command"])
        self.assertIn("force_summary", row["command"])
        self.assertIn('"output_mode": "force_summary"', row["stdout_tail"])
        self.assertIn('"checksum_force_x"', row["stdout_tail"])
        self.assertFalse(row["semantic_stdout_check"]["claim_flag_violations"])


if __name__ == "__main__":
    unittest.main()
