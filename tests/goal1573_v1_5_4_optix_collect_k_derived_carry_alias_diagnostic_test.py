import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py"


class Goal1573V154OptixCollectKDerivedCarryAliasDiagnosticTest(unittest.TestCase):
    def test_derived_carry_alias_is_env_gated(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC", source)
        self.assertIn("collect_k_use_derived_carry_alias_diagnostic", source)
        self.assertIn("(use_candidate_bundle_for_case || collect_k_use_derived_carry_alias_diagnostic())", source)
        self.assertIn("&& use_device_level_counts", source)

    def test_alias_is_limited_to_topologies_where_carry_stays_unpaired(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("const size_t next_segment_count = pair_count + (has_carry ? 1 : 0);", source)
        self.assertIn("const bool derived_carry_alias_safe_next =", source)
        self.assertIn("next_segment_count == 2 || (next_segment_count % 2) != 0", source)
        self.assertIn("&& derived_carry_alias_safe_next", source)

    def test_alias_preserves_derived_descriptor_path_and_skips_only_safe_row_copy(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("use_derived_carry_alias_level", source)
        self.assertIn("use_derived_level_descriptors", source)
        self.assertIn("(use_pointer_carry_level || use_derived_carry_alias_level)", source)
        self.assertIn("if (!use_pointer_carry_level && !use_derived_carry_alias_level)", source)
        self.assertIn("CU_CHECK(cuMemcpyDtoD(", source)

    def test_alias_takes_precedence_over_pointer_diagnostics_when_enabled(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("&& !use_derived_carry_alias_diagnostic", source)
        self.assertIn("use_pointer_device_counts_carry_level", source)
        self.assertIn("use_pointer_host_counts_carry_level", source)

    def test_profiler_distinguishes_topology_carries_from_payload_copies(self) -> None:
        api = API.read_text(encoding="utf-8")
        probe = PROBE.read_text(encoding="utf-8")
        self.assertIn("carry_payload_copies", api)
        self.assertIn("bool copied_carry_payload = false;", api)
        self.assertIn("if (copied_carry_payload) {", api)
        self.assertIn("carry_payload_copies", probe)
        self.assertIn("if not use_pointer_carry_level and not use_derived_carry_alias_level:", probe)


if __name__ == "__main__":
    unittest.main()
