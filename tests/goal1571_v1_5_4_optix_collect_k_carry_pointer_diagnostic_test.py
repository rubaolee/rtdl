import unittest
from pathlib import Path
import json


API = Path("src/native/optix/rtdl_optix_api.cpp")
ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "docs" / "reports" / "goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_profile_2026-05-08.json"
REPORT = ROOT / "docs" / "reports" / "goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_negative_result_2026-05-08.md"


class Goal1571V154OptixCollectKCarryPointerDiagnosticTest(unittest.TestCase):
    def test_carry_pointer_diagnostic_is_env_gated(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC", source)
        self.assertIn("collect_k_use_carry_pointer_diagnostic", source)
        self.assertIn("collect_k_use_carry_pointer_diagnostic() && use_device_level_counts", source)

    def test_pointer_carry_level_uses_pointer_descriptors_and_host_counts(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("use_pointer_carry_level", source)
        self.assertIn("level_use_device_level_counts", source)
        self.assertIn("level_use_derived_level_descriptors", source)
        self.assertIn("download(current_counts.data(), current_counts_level_device, current_rows.size())", source)
        self.assertIn("merge_first_rows[pair_index] = static_cast<uint64_t>(current_rows[pair_index * 2]);", source)
        self.assertIn("upload(next_counts_level_device, next_counts.data(), pair_count);", source)

    def test_pointer_carry_alias_skips_row_copy_but_keeps_count_copy(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("? current_rows.back()", source)
        self.assertIn("if (!use_pointer_carry_level)", source)
        self.assertIn("cuMemcpyDtoD(", source)
        self.assertIn("carry_count_dest", source)

    def test_measured_artifact_records_parity_but_not_accepted_goal1506(self) -> None:
        data = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertFalse(data["accepted_goal1506_evidence"])
        self.assertTrue(data["local_fallback_smoke_only"])
        by_count = {case["candidate_count"]: case for case in data["cases"]}
        self.assertTrue(by_count[65537]["same_candidate_rows"])
        self.assertTrue(by_count[65537]["same_valid_count"])
        self.assertFalse(by_count[65537]["profile_topology_matches_expected"])
        self.assertTrue(by_count[131072]["profile_topology_matches_expected"])

    def test_negative_report_rejects_production_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not promote `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC`", text)
        self.assertIn("count downloads plus\ndescriptor/count uploads", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
