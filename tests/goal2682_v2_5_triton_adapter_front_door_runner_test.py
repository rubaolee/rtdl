from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2682_v2_5_triton_adapter_front_door_pod_runner.py"


class Goal2682V25TritonAdapterFrontDoorRunnerTest(unittest.TestCase):
    def test_dry_run_does_not_require_triton_or_torch_cuda(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--row-counts",
                "8,16",
                "--group-count",
                "4",
                "--repeats",
                "1",
            ],
            cwd=ROOT,
            env={"PYTHONPATH": "src:."},
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"status": "dry_run"', completed.stdout)
        self.assertIn('"goal": "Goal2682 v2.5 Triton adapter front-door pod runner"', completed.stdout)
        self.assertIn('"pod_validation_required": true', completed.stdout)

    def test_runner_uses_public_partner_adapter_front_door(self):
        source = SCRIPT.read_text()

        self.assertIn('partner_group_count_by_key(keys, group_count, partner="triton")', source)
        self.assertIn('partner_group_sum_by_key(keys, values, group_count, partner="triton")', source)
        self.assertIn('partner_group_min_by_key(keys, values, group_count, partner="triton"', source)
        self.assertIn('partner_group_max_by_key(keys, values, group_count, partner="triton"', source)
        self.assertIn('partner_mask_indices(mask, partner="triton")', source)
        self.assertIn('partner_columnar_predicate_reduce(', source)
        self.assertNotIn("cupy", source.lower())
        self.assertIn('"no_public_speedup_claim": True', source)


if __name__ == "__main__":
    unittest.main()
