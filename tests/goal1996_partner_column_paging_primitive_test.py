from __future__ import annotations

import pathlib
import unittest
from unittest import mock

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1996_partner_column_paging_primitive_2026-05-14.md"


class Goal1996PartnerColumnPagingPrimitiveTest(unittest.TestCase):
    def test_partner_page_columns_is_public(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def partner_page_columns", adapters)
        self.assertIn("without Python row materialization", adapters)
        self.assertIn("source_row_count", adapters)
        self.assertIn("from .partner_adapters import partner_page_columns", init_text)
        self.assertIn('"partner_page_columns"', init_text)

    def test_partner_page_columns_works_on_torch_columns(self) -> None:
        import rtdsl.partner_adapters as adapters

        columns = {
            "left_index": np.arange(6, dtype=np.int64),
            "right_index": np.arange(10, 16, dtype=np.int64),
        }
        with mock.patch.object(adapters, "_partner_module", return_value={"name": "torch"}):
            page = adapters.partner_page_columns(columns, offset=2, limit=3, partner="torch")

        self.assertEqual(page["left_index"].tolist(), [2, 3, 4])
        self.assertEqual(page["right_index"].tolist(), [12, 13, 14])
        self.assertEqual(page["_metadata"]["adapter"], "partner_page_columns")
        self.assertEqual(page["_metadata"]["offset"], 2)
        self.assertEqual(page["_metadata"]["limit"], 3)
        self.assertEqual(page["_metadata"]["row_count"], 3)
        self.assertEqual(page["_metadata"]["source_row_count"], 6)
        self.assertFalse(page["_metadata"]["whole_app_speedup_claim_authorized"])

    def test_report_and_preflight_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("bounded paging", report)
        self.assertIn("not a new native RTDL engine feature", report)
        self.assertIn("does not by itself authorize a broad row-output speedup claim", report)
        self.assertIn("tests.goal1996_partner_column_paging_primitive_test", preflight)


if __name__ == "__main__":
    unittest.main()
