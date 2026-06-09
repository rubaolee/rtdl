import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4202_rt_dbscan_single_pass_reference_parity.py"


class Goal4202RtDbscanSinglePassReferenceParityRunnerTest(unittest.TestCase):
    def test_runner_mentions_reference_contract_and_both_policies(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("predicate_aware_boundary_union_reference", text)
        self.assertIn("lowest_candidate_then_root", text)
        self.assertIn("lowest_component_root_two_pass", text)
        self.assertIn("matches_reference_labels", text)
        self.assertIn("default_matches_two_pass_labels", text)

    def test_presets_are_small_enough_for_reference_pair_build(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"adversarial_root_shadow_1d"', text)
        self.assertIn('"clustered3d_512"', text)
        self.assertIn('"road3d_1024"', text)
        self.assertNotIn('"clustered3d_65536"', text)

    def test_list_presets_runs_without_gpu(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-presets"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("adversarial_root_shadow_1d", completed.stdout)
        self.assertIn("tiny", completed.stdout)
        self.assertIn("ngsim_dense_1024", completed.stdout)


if __name__ == "__main__":
    unittest.main()
