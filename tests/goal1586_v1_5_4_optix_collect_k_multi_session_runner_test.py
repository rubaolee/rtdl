import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py"


class Goal1586V154OptixCollectKMultiSessionRunnerTest(unittest.TestCase):
    def test_runner_invokes_goal1579_with_distinct_session_prefixes(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py", source)
        self.assertIn('f"{output_prefix.name}_session{session_index}"', source)
        self.assertIn("--candidate-preset-smoke", source)
        self.assertIn("--candidate-preset-repeats", source)
        self.assertIn("--device-label", source)

    def test_runner_aggregates_targeted_counts_and_claim_boundary(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("TARGET_COUNTS = (49153, 65536, 65537)", source)
        self.assertIn("goal1586_multi_session_validation_recorded", source)
        self.assertIn("gpu_metadata", source)
        self.assertIn("--query-gpu=name,driver_version", source)
        self.assertIn("nvidia_smi_cuda_version", source)
        self.assertIn("does not authorize public speedup wording", source)
        self.assertIn("stable primitive promotion", source)

    def test_runner_records_acceptance_and_payload_copy_fields(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for key in (
            "baseline_accepted",
            "alias_accepted",
            "baseline_parity",
            "alias_parity",
            "baseline_topology",
            "alias_topology",
            "baseline_payload_copies",
            "alias_payload_copies",
            "candidate_preset_payload_copies",
        ):
            self.assertIn(key, source)


if __name__ == "__main__":
    unittest.main()
