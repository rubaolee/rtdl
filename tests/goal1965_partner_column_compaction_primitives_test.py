from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1965_partner_column_compaction_primitives_2026-05-14.md"


class Goal1965PartnerColumnCompactionPrimitivesTest(unittest.TestCase):
    def test_partner_adapter_exposes_column_compaction_primitives(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        for name in (
            "partner_mask_indices",
            "partner_take_columns_by_indices",
            "partner_compact_columns_by_mask",
        ):
            self.assertIn(f"def {name}", adapters)
            self.assertIn(f"from .partner_adapters import {name}", init_text)
            self.assertIn(f'"{name}"', init_text)
        self.assertIn("torch.nonzero", adapters)
        self.assertIn("cupy.nonzero", adapters)
        self.assertIn("column[indices]", adapters)

    def test_report_positions_compaction_as_row_materialization_debt_work(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("partner_compact_columns_by_mask", report)
        self.assertIn("row materialization", report)
        self.assertIn("generic column tables", report)
        self.assertIn("does not add app rows to native code", report)
        self.assertIn("tests.goal1965_partner_column_compaction_primitives_test", preflight)


if __name__ == "__main__":
    unittest.main()
