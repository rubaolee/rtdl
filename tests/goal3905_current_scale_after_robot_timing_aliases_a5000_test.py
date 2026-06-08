from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3905_current_scale_after_robot_timing_aliases_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
PREVIOUS_SUMMARY = ROOT / "docs" / "reports" / "goal3902_current_scale_with_payload_timing_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3905_current_scale_after_robot_timing_aliases_2026-06-08.md"


def _local_stdout_path(row: dict[str, object]) -> Path:
    remote_or_local = str(row["stdout_path"])
    return ARTIFACT_DIR / "outputs" / PurePosixPath(remote_or_local).name


class Goal3905CurrentScaleAfterRobotTimingAliasesA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.previous = json.loads(PREVIOUS_SUMMARY.read_text(encoding="utf-8"))

    def test_full_scale_packet_passes_with_clean_runtime_provenance(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        self.assertEqual(len(self.summary["rows"]), 10)
        env = self.summary["runtime_environment"]
        self.assertEqual(env["source_commit_short"], "fb94b687")
        self.assertTrue(env["working_tree_clean"])
        self.assertEqual(env["git_status_short"], [])
        self.assertIn("NVIDIA RTX A5000", env["nvidia_smi"])

        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual(row["status"], "pass")
                self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

    def test_robot_row_now_exposes_standard_timing_scalars(self) -> None:
        row = next(row for row in self.summary["rows"] if row["app"] == "robot_collision")
        previous_row = next(row for row in self.previous["rows"] if row["app"] == "robot_collision")
        timing = row["semantic_stdout_check"]["payload_timing_summary"]
        previous_timing = previous_row["semantic_stdout_check"]["payload_timing_summary"]

        self.assertEqual(previous_timing["timing_scalar_count"], 0)
        self.assertEqual(timing["timing_scalar_count"], 7)
        paths = {item["path"] for item in timing["timing_scalars_sample"]}
        self.assertIn("$.benchmark_timing_sec.app_lowering_sec", paths)
        self.assertIn("$.benchmark_timing_sec.tail_total_run_sec", paths)
        self.assertIn("$.benchmark_timing_sec.tail_phase_traversal_sec", paths)
        self.assertIn("$.benchmark_timing_sec.tail_phase_prepared_query_build_sec", paths)

        payload = json.loads(_local_stdout_path(row).read_text(encoding="utf-8"))
        self.assertIn("benchmark_timing_sec", payload)
        self.assertEqual(
            payload["benchmark_timing_sec"]["tail_total_run_sec"],
            payload["tail_medians"]["total_run_seconds"],
        )
        self.assertEqual(
            payload["benchmark_timing_sec"]["tail_phase_traversal_sec"],
            payload["tail_medians"]["phase_timing_seconds"]["traversal"],
        )

    def test_report_preserves_internal_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3905",
            "timing_scalar_count = 7",
            "not a public performance comparison",
            "does not authorize release action",
            "process elapsed remains pod-budget evidence",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
