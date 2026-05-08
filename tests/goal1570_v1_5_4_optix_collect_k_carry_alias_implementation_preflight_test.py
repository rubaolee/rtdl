import unittest
from pathlib import Path


REPORT = Path("docs/reports/goal1570_v1_5_4_optix_collect_k_carry_alias_implementation_preflight_2026-05-08.md")
API = Path("src/native/optix/rtdl_optix_api.cpp")


class Goal1570V154OptixCollectKCarryAliasImplementationPreflightTest(unittest.TestCase):
    def test_report_identifies_counts_path_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("counts-path gap", text)
        self.assertIn("`use_device_level_counts` currently prevents pointer-descriptor", text)
        self.assertIn("current_counts_device", text)

    def test_report_scopes_opt_in_diagnostic(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC", text)
        self.assertIn("Do not enable this path by default", text)
        self.assertIn("Do not skip the carry count copy", text)

    def test_current_dispatch_prioritizes_device_counts_before_pointer_descriptors(self) -> None:
        source = API.read_text(encoding="utf-8")
        device_counts_index = source.index("if (use_device_level_counts)")
        derived_index = source.index("} else if (use_derived_level_descriptors)", device_counts_index)
        pointer_index = source.index("} else {", derived_index)
        self.assertLess(device_counts_index, derived_index)
        self.assertLess(derived_index, pointer_index)


if __name__ == "__main__":
    unittest.main()
