import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py"


class Goal2665V25TritonGroupedRunnerTest(unittest.TestCase):
    def test_dry_run_does_not_require_triton_or_torch(self):
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
                "--include-numba",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["row_counts"], [8, 16])
        self.assertEqual(payload["group_count"], 4)
        self.assertTrue(payload["include_numba"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertTrue(payload["pod_validation_required"])

    def test_script_records_count_sum_and_claim_boundary(self):
        source = SCRIPT.read_text()

        self.assertIn("run_triton_segmented_count_i64", source)
        self.assertIn("run_triton_segmented_sum_f64", source)
        self.assertIn("run_numba_segmented_count_i64", source)
        self.assertIn("run_numba_segmented_sum_f64", source)
        self.assertIn("--include-numba", source)
        self.assertIn("torch.bincount", source)
        self.assertIn("scatter_add_", source)
        self.assertIn("partner_continuation_only", source)
        self.assertIn("no_public_speedup_claim", source)


if __name__ == "__main__":
    unittest.main()
