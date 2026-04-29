from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1086_robot_chunked_embree_baseline_intake import build_intake
from scripts.goal1086_robot_chunked_embree_baseline_intake import to_markdown


ROOT = Path(__file__).resolve().parents[1]


def _write_chunk(
    path: Path,
    *,
    pose_count: int = 200_000,
    obstacle_count: int = 4096,
    pose_id_start: int = 1,
    query_sec: float = 0.5,
) -> None:
    path.write_text(
        json.dumps(
            {
                "status": "ok",
                "correctness_parity": True,
                "source_backend": "embree",
                "benchmark_scale": {
                    "pose_count": pose_count,
                    "obstacle_count": obstacle_count,
                    "pose_id_start": pose_id_start,
                    "iterations": 3,
                },
                "phase_seconds": {
                    "native_anyhit_query": query_sec,
                    "backend_scene_prepare": 0.1,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )


class Goal1086RobotChunkedEmbreeBaselineIntakeTest(unittest.TestCase):
    def test_missing_default_chunks_are_reported_without_authorizing_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            intake = build_intake(input_dir=Path(tmpdir))

        self.assertTrue(intake["valid"])
        self.assertEqual(intake["status"], "missing_or_invalid_chunks")
        self.assertFalse(intake["public_speedup_claim_authorized"])
        self.assertEqual(intake["observed"]["chunk_count"], 0)
        self.assertEqual(len(intake["observed"]["missing_indices"]), 180)

    def test_complete_temp_chunk_set_aggregates_phase_sums(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            for index in range(180):
                _write_chunk(
                    directory / f"chunk_{index}.json",
                    pose_id_start=index * 200_000 + 1,
                    query_sec=0.25,
                )

            intake = build_intake(input_dir=directory)

        self.assertEqual(intake["status"], "complete")
        self.assertEqual(intake["observed"]["chunk_count"], 180)
        self.assertEqual(intake["observed"]["total_pose_count"], 36_000_000)
        self.assertEqual(intake["phase_seconds"]["native_anyhit_sum_sec"], 45.0)
        self.assertEqual(intake["phase_seconds"]["native_anyhit_median_chunk_sec"], 0.25)
        self.assertFalse(intake["public_speedup_claim_authorized"])

    def test_invalid_scale_keeps_status_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            for index in range(180):
                _write_chunk(
                    directory / f"chunk_{index}.json",
                    pose_count=100_000,
                    pose_id_start=index * 200_000 + 1,
                )

            intake = build_intake(input_dir=directory)

        self.assertEqual(intake["status"], "missing_or_invalid_chunks")
        self.assertEqual(intake["observed"]["scale_ok_chunk_count"], 0)
        self.assertIn("does not authorize public RTX speedup claims", to_markdown(intake))

    def test_wrong_pose_id_start_keeps_status_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            for index in range(180):
                _write_chunk(
                    directory / f"chunk_{index}.json",
                    pose_id_start=1,
                )

            intake = build_intake(input_dir=directory)

        self.assertEqual(intake["status"], "missing_or_invalid_chunks")
        self.assertEqual(intake["observed"]["scale_ok_chunk_count"], 1)


if __name__ == "__main__":
    unittest.main()
