from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _goal887_artifact(*, source_commit: str, matches_oracle, median: float) -> dict[str, object]:
    return {
        "source_commit": source_commit,
        "scenario": {
            "mode": "optix",
            "result": {"matches_oracle": matches_oracle},
            "timings_sec": {"optix_query_sec": {"median_sec": median}},
        },
    }


def _robot_artifact(*, source_commit: str, matches_oracle, median: float) -> dict[str, object]:
    return {
        "source_commit": source_commit,
        "mode": "optix",
        "matches_oracle": matches_oracle,
        "phases": {"prepared_pose_flags_warm_query_sec": {"median_sec": median}},
    }


class Goal1118CurrentSourceRtxRerunIntakeTest(unittest.TestCase):
    def _write_complete_artifacts(self, directory: Path, *, median: float = 0.2) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        commit = "abc123"
        artifacts = {
            "facility_recentered_coverage_threshold_2_5m_optix_validation.json": _goal887_artifact(
                source_commit=commit,
                matches_oracle=True,
                median=median,
            ),
            "robot_prepared_pose_flags_validation.json": _robot_artifact(
                source_commit=commit,
                matches_oracle=True,
                median=0.01,
            ),
            "robot_prepared_pose_flags_8m_timing.json": _robot_artifact(
                source_commit=commit,
                matches_oracle=None,
                median=median,
            ),
            "barnes_hut_depth8_4096_validation.json": _goal887_artifact(
                source_commit=commit,
                matches_oracle=True,
                median=0.01,
            ),
            "barnes_hut_depth8_20m_timing.json": _goal887_artifact(
                source_commit=commit,
                matches_oracle=None,
                median=median,
            ),
        }
        for name, payload in artifacts.items():
            (directory / name).write_text(json.dumps(payload), encoding="utf-8")
        (directory / "goal1116_runner.log").write_text("source_commit=abc123\nutc_start=x\nutc_end=y\n", encoding="utf-8")

    def test_complete_current_source_artifacts_pass(self) -> None:
        module = __import__("scripts.goal1118_current_source_rtx_rerun_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir)
            self._write_complete_artifacts(input_dir)

            payload = module.build_intake(input_dir=input_dir)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 5)
        self.assertEqual(payload["summary"]["valid_row_count"], 5)
        self.assertEqual(payload["summary"]["source_commits"], ["abc123"])
        self.assertTrue(payload["summary"]["runner_log_exists"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])

    def test_missing_artifacts_block(self) -> None:
        module = __import__("scripts.goal1118_current_source_rtx_rerun_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(input_dir=Path(tmpdir))

        self.assertFalse(payload["valid"])
        self.assertEqual(payload["summary"]["missing_row_count"], 5)
        self.assertFalse(payload["summary"]["runner_log_exists"])

    def test_timing_below_floor_blocks(self) -> None:
        module = __import__("scripts.goal1118_current_source_rtx_rerun_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir)
            self._write_complete_artifacts(input_dir, median=0.01)

            payload = module.build_intake(input_dir=input_dir)

        self.assertFalse(payload["valid"])
        findings = [finding for row in payload["rows"] for finding in row["findings"]]
        self.assertIn("median_query_below_timing_floor", findings)

    def test_mixed_source_commits_block(self) -> None:
        module = __import__("scripts.goal1118_current_source_rtx_rerun_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir)
            self._write_complete_artifacts(input_dir)
            robot = json.loads((input_dir / "robot_prepared_pose_flags_validation.json").read_text(encoding="utf-8"))
            robot["source_commit"] = "different"
            (input_dir / "robot_prepared_pose_flags_validation.json").write_text(json.dumps(robot), encoding="utf-8")

            payload = module.build_intake(input_dir=input_dir)

        self.assertFalse(payload["valid"])
        self.assertFalse(payload["summary"]["same_source_commit"])


if __name__ == "__main__":
    unittest.main()
