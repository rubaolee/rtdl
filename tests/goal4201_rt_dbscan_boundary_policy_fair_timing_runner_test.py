import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4201_rt_dbscan_boundary_policy_fair_timing.py"


class Goal4201RtDbscanBoundaryPolicyFairTimingRunnerTest(unittest.TestCase):
    def test_runner_exposes_dense_and_sparse_presets(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("clustered3d_64k", text)
        self.assertIn("road3d_64k", text)
        self.assertIn("ngsim_dense_64k", text)
        self.assertIn("single_pass_candidate_root_rebased", text)
        self.assertIn("lowest_component_root_two_pass", text)

    def test_runner_is_fair_order_and_claim_boundary_aware(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("order = POLICIES if index % 2 == 0 else tuple(reversed(POLICIES))", text)
        self.assertIn("route_promotion_authorized", text)
        self.assertIn("public_speedup_claim_authorized", text)
        self.assertIn("true_zero_copy_claim_authorized", text)
        self.assertIn("same_counts_only_signature", text)
        self.assertIn("two_pass_vs_default_median_ratio", text)

    def test_list_presets_runs_without_gpu(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-presets"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("clustered3d_16k", completed.stdout)
        self.assertIn("road3d_64k", completed.stdout)


if __name__ == "__main__":
    unittest.main()
