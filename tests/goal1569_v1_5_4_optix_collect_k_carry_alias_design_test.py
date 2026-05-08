import unittest
from pathlib import Path


REPORT = Path("docs/reports/goal1569_v1_5_4_optix_collect_k_carry_alias_design_2026-05-08.md")
API = Path("src/native/optix/rtdl_optix_api.cpp")


class Goal1569V154OptixCollectKCarryAliasDesignTest(unittest.TestCase):
    def test_report_rejects_naive_pointer_alias_with_derived_descriptors(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a safe one-line pointer alias", text)
        self.assertIn("current_base = current_rows.front()", text)
        self.assertIn("break the device-side address calculation", text)

    def test_report_names_viable_designs_and_recommended_diagnostic(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Pointer Descriptor Mode For Odd Levels", text)
        self.assertIn("Carry Alias Flag Plus Mixed Addressing Kernel", text)
        self.assertIn("Ping-Pong Layout Reservation", text)
        self.assertIn("Start with Design A as a diagnostic-only experiment", text)
        self.assertIn("keep the carry count copy", text)
        self.assertIn("measure pointer-array upload cost separately", text)

    def test_report_records_external_review_caveats(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Claude reviewed this design", text)
        self.assertIn("removes row-data carry copies, not carry count copies", text)
        self.assertIn("materialize and compact variants must be switched", text)
        self.assertIn("goal1569_claude_carry_alias_design_review_2026-05-08.md", text)

    def test_current_code_copies_carry_to_preserve_contiguous_layout(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("cuMemcpyDtoD(", source)
        self.assertIn("carry_output", source)
        self.assertIn("current_rows.back()", source)
        self.assertIn("current_rows.front()", source)


if __name__ == "__main__":
    unittest.main()
