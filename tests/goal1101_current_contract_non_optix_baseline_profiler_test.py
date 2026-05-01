from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class _FakePreparedThreshold:
    def run(self, query_points, *, radius: float, threshold: int = 1):
        return tuple(
            {"query_id": point.id, "neighbor_count": threshold, "threshold_reached": 1}
            for point in query_points
        )

    def close(self) -> None:
        return None


class Goal1101CurrentContractNonOptixBaselineProfilerTest(unittest.TestCase):
    def test_cpu_oracle_facility_recentered_profile_preserves_no_claim_boundary(self) -> None:
        module = __import__(
            "scripts.goal1101_current_contract_non_optix_baseline_profiler",
            fromlist=["run_profile"],
        )

        payload = module.run_profile(
            scenario="facility_service_coverage_recentered",
            backend="cpu_oracle",
            copies=1,
            body_count=1,
            iterations=1,
            radius=1.0,
            barnes_tree_depth=1,
            hit_threshold=1,
            skip_validation=False,
        )

        self.assertEqual(payload["app"], "facility_knn_assignment")
        self.assertEqual(payload["path_name"], "coverage_threshold_prepared_recentered")
        self.assertEqual(payload["backend"], "cpu_oracle")
        self.assertTrue(payload["scenario"]["result"]["matches_oracle"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_source_commit_prefers_git_head_over_stale_source_file(self) -> None:
        module = __import__(
            "scripts.goal1101_current_contract_non_optix_baseline_profiler",
            fromlist=["run_profile"],
        )
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest("git metadata unavailable in archive-style checkout")
        expected_head = completed.stdout.strip()

        payload = module.run_profile(
            scenario="facility_service_coverage_recentered",
            backend="cpu_oracle",
            copies=1,
            body_count=1,
            iterations=1,
            radius=1.0,
            barnes_tree_depth=1,
            hit_threshold=1,
            skip_validation=False,
        )

        self.assertEqual(payload["source_commit"], expected_head)

    def test_source_commit_falls_back_to_source_file_when_git_is_unavailable(self) -> None:
        module = __import__(
            "scripts.goal1101_current_contract_non_optix_baseline_profiler",
            fromlist=["_source_commit"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".rtdl_source_commit").write_text("archive-commit\n", encoding="utf-8")
            completed = subprocess.CompletedProcess(args=["git"], returncode=1, stdout="", stderr="")
            with mock.patch.dict(os.environ, {"RTDL_SOURCE_COMMIT": ""}, clear=False):
                with mock.patch.object(module, "ROOT", root):
                    with mock.patch.object(module.subprocess, "run", return_value=completed):
                        self.assertEqual(module._source_commit(), "archive-commit")

    def test_embree_barnes_profile_uses_prepared_threshold_surface(self) -> None:
        module = __import__(
            "scripts.goal1101_current_contract_non_optix_baseline_profiler",
            fromlist=["run_profile", "rt"],
        )

        with mock.patch.object(
            module.rt,
            "prepare_embree_fixed_radius_count_threshold_2d",
            return_value=_FakePreparedThreshold(),
        ) as prepare:
            payload = module.run_profile(
                scenario="barnes_hut_node_coverage",
                backend="embree",
                copies=1,
                body_count=8,
                iterations=1,
                radius=10.0,
                barnes_tree_depth=1,
                hit_threshold=1,
                skip_validation=False,
            )

        self.assertEqual(payload["app"], "barnes_hut_force_app")
        self.assertEqual(payload["path_name"], "node_coverage_prepared_rich")
        self.assertEqual(payload["backend"], "embree")
        self.assertTrue(payload["scenario"]["result"]["matches_oracle"])
        self.assertGreaterEqual(payload["scenario"]["timings_sec"]["backend_prepare_sec"], 0.0)
        self.assertEqual(prepare.call_count, 1)

    def test_embree_facility_profile_can_skip_validation_for_timing_rows(self) -> None:
        module = __import__(
            "scripts.goal1101_current_contract_non_optix_baseline_profiler",
            fromlist=["run_profile", "rt"],
        )

        with mock.patch.object(
            module.rt,
            "prepare_embree_fixed_radius_count_threshold_2d",
            return_value=_FakePreparedThreshold(),
        ):
            payload = module.run_profile(
                scenario="facility_service_coverage_recentered",
                backend="embree",
                copies=1,
                body_count=1,
                iterations=1,
                radius=1.0,
                barnes_tree_depth=1,
                hit_threshold=1,
                skip_validation=True,
            )

        self.assertEqual(payload["app"], "facility_knn_assignment")
        self.assertEqual(payload["backend"], "embree")
        self.assertIsNone(payload["scenario"]["result"]["matches_oracle"])
        self.assertEqual(payload["scenario"]["timings_sec"]["validation_sec"]["median_sec"], 0.0)
        self.assertFalse(payload["public_speedup_claim_authorized"])

    def test_cli_writes_json_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "baseline.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1101_current_contract_non_optix_baseline_profiler.py",
                    "--scenario",
                    "facility_service_coverage_recentered",
                    "--backend",
                    "cpu_oracle",
                    "--copies",
                    "1",
                    "--iterations",
                    "1",
                    "--radius",
                    "1.0",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("facility_service_coverage_recentered", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "goal1101_current_contract_non_optix_baseline_v1")
            self.assertFalse(payload["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
