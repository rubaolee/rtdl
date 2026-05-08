import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py"


class Goal1579V154OptixCollectKNextArchRunnerTest(unittest.TestCase):
    def test_runner_defines_required_counts_and_alias_flag(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("SWEEP_COUNTS = [7, 8192, 12289, 16385, 20481, 24577, 32769, 45057, 49153, 65536, 65537]", source)
        self.assertIn("TARGETED_COUNTS = [49153, 65536, 65537]", source)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC"', source)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS": "1"', source)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE": "1"', source)
        self.assertIn("--candidate-preset-smoke", source)
        self.assertIn("--candidate-preset-repeats", source)

    def test_runner_preserves_claim_boundary_and_writes_summary(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("goal1579_next_arch_validation_recorded", source)
        self.assertIn("summary_json.write_text", source)
        self.assertIn("summary_md.write_text", source)
        self.assertIn("does not authorize public speedup wording", source)
        self.assertIn("stable primitive promotion", source)
        self.assertIn("candidate_preset_json", source)
        self.assertIn("PROFILE_ISOLATION_ENV_KEYS", source)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC"', source)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC"', source)

    def test_runner_runs_focused_static_tests_before_profiles(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for test_name in (
            "tests.goal1573_v1_5_4_optix_collect_k_derived_carry_alias_diagnostic_test",
            "tests.goal1572_v1_5_4_optix_collect_k_carry_pointer_device_counts_diagnostic_test",
            "tests.goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_test",
            "tests.goal1570_v1_5_4_optix_collect_k_carry_alias_implementation_preflight_test",
        ):
            self.assertIn(test_name, source)
        self.assertIn("_run([sys.executable, \"-m\", \"unittest\", *FOCUSED_TESTS]", source)


if __name__ == "__main__":
    unittest.main()
