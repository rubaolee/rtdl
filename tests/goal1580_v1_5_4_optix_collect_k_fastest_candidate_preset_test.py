import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNNER = ROOT / "scripts" / "goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py"
PROBE = ROOT / "scripts" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_2026-05-08.md"


class Goal1580V154OptixCollectKFastestCandidatePresetTest(unittest.TestCase):
    def test_candidate_preset_is_explicitly_opt_in(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE", source)
        self.assertIn("static bool collect_k_use_fastest_candidate()", source)
        self.assertIn("collect_k_env_enabled(\"RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE\")", source)

    def test_candidate_preset_enables_only_positive_bundle_switches(self) -> None:
        source = API.read_text(encoding="utf-8")
        for flag in (
            "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT",
            "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT",
            "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL",
            "RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT",
            "RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS",
            "RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS",
            "RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS",
            "RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC",
            "RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE",
        ):
            self.assertIn(f"collect_k_use_fastest_candidate() || collect_k_env_enabled(\"{flag}\")", source)

    def test_candidate_preset_does_not_enable_rejected_pointer_diagnostics(self) -> None:
        source = API.read_text(encoding="utf-8")
        host_pointer_fn = source[
            source.index("static bool collect_k_use_carry_pointer_diagnostic()"):
            source.index("static bool collect_k_use_carry_pointer_device_counts_diagnostic()")
        ]
        device_pointer_fn = source[
            source.index("static bool collect_k_use_carry_pointer_device_counts_diagnostic()"):
            source.index("static bool collect_k_use_derived_carry_alias_diagnostic()")
        ]
        self.assertNotIn("collect_k_use_fastest_candidate", host_pointer_fn)
        self.assertNotIn("collect_k_use_fastest_candidate", device_pointer_fn)

    def test_next_arch_runner_can_smoke_the_single_flag_preset(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("CANDIDATE_PRESET_ENV", source)
        self.assertIn("--candidate-preset-smoke", source)
        self.assertIn("use_candidate_preset=True", source)

    def test_stage_profile_probe_understands_single_flag_preset(self) -> None:
        source = PROBE.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE", source)
        self.assertIn("use_fastest_candidate or _collect_k_env_enabled(\"RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT\")", source)
        self.assertIn("use_fastest_candidate or _collect_k_env_enabled(\"RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC\")", source)

    def test_report_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("opt-in candidate preset", text)
        self.assertIn("does not change default behavior", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("does not enable the rejected pointer-carry diagnostics", text)


if __name__ == "__main__":
    unittest.main()
