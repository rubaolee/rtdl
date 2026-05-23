from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.columnar_partner import partner_resident_columnar_native_execution_requirements


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/columnar_partner.py"
REPORT = ROOT / "docs/reports/goal2561_columnar_partner_wording_boundary_2026-05-23.md"


class Goal2561ColumnarPartnerWordingBoundaryTest(unittest.TestCase):
    def test_shared_columnar_partner_contract_does_not_name_raydb(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("RayDB-style", text)
        self.assertNotIn("native DB path", text)
        self.assertNotIn("OptiX DB dataset", text)
        self.assertIn("numeric columnar aggregate columns only", text)
        self.assertIn("OptiX native columnar", text)

    def test_runtime_requirements_return_generic_first_slice(self) -> None:
        requirements = partner_resident_columnar_native_execution_requirements()
        self.assertIn("numeric columnar aggregate columns only", requirements["first_executable_slice"])
        combined = "\n".join(
            str(value)
            for value in (
                requirements["current_blockers"],
                requirements["first_executable_slice"],
                requirements["claim_boundary"],
            )
        )
        self.assertNotIn("RayDB-style", combined)
        self.assertNotIn("native DB path", combined)
        self.assertNotIn("OptiX DB dataset", combined)

    def test_report_records_wording_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2561", text)
        self.assertIn("numeric columnar aggregate columns only", text)
        self.assertIn("No behavior or native ABI changes", text)


if __name__ == "__main__":
    unittest.main()
