from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class _FakePreparedThreshold:
    def __init__(self, target, *, max_radius: float):
        self.target = target
        self.max_radius = max_radius
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def count_threshold_reached(self, source, *, radius: float, threshold: int) -> int:
        self.radius = radius
        self.threshold = threshold
        return len(source)

    def close(self) -> None:
        self.closed = True


class Goal1161HausdorffNonanalyticThresholdContractTest(unittest.TestCase):
    def test_dry_run_contract_uses_nonanalytic_fixture(self) -> None:
        module = __import__(
            "scripts.goal1161_hausdorff_nonanalytic_threshold_contract",
            fromlist=["build_payload"],
        )
        payload = module.build_payload(
            mode="dry-run",
            point_count=64,
            radius=0.35,
            iterations=1,
            skip_validation=False,
        )

        self.assertTrue(payload["valid"])
        self.assertTrue(payload["scenario"]["non_analytic_fixture"])
        self.assertTrue(payload["scenario"]["replaces_blocked_tiled_scale_contract"])
        self.assertEqual(payload["scenario"]["result"]["point_count_a"], 64)
        self.assertEqual(payload["scenario"]["result"]["point_count_b"], 64)
        self.assertIn("validation_sec", payload["scenario"]["timings_sec"])
        self.assertIn("does not authorize public RTX speedup wording", payload["boundary"])

    def test_optix_mode_keeps_scalar_threshold_contract(self) -> None:
        module = __import__(
            "scripts.goal1161_hausdorff_nonanalytic_threshold_contract",
            fromlist=["build_payload", "rt"],
        )
        with mock.patch.object(
            module.rt,
            "prepare_optix_fixed_radius_count_threshold_2d",
            side_effect=_FakePreparedThreshold,
        ):
            payload = module.build_payload(
                mode="optix",
                point_count=8,
                radius=0.35,
                iterations=2,
                skip_validation=True,
            )

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["scenario"]["result"]["covered_a_to_b"], 8)
        self.assertEqual(payload["scenario"]["result"]["covered_b_to_a"], 8)
        self.assertIsNone(payload["scenario"]["result"]["matches_oracle"])
        self.assertIn("optix_query_sec", payload["scenario"]["timings_sec"])
        self.assertEqual(
            payload["cloud_claim_contract"]["activation_status"],
            "eligible_for_next_real_rtx_batch_after_2_ai_review",
        )

    def test_cli_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "hausdorff_contract.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1161_hausdorff_nonanalytic_threshold_contract.py",
                    "--mode",
                    "dry-run",
                    "--point-count",
                    "32",
                    "--iterations",
                    "1",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "goal1161_hausdorff_nonanalytic_threshold_contract_v1")
            self.assertEqual(payload["scenario"]["app"], "hausdorff_distance")


if __name__ == "__main__":
    unittest.main()
