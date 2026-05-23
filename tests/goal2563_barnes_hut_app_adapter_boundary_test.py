from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.app_adapters import barnes_hut as barnes_adapter


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
APP_ADAPTER = ROOT / "src/rtdsl/app_adapters/barnes_hut.py"
INIT = ROOT / "src/rtdsl/__init__.py"
REPORT = ROOT / "docs/reports/goal2563_barnes_hut_app_adapter_boundary_2026-05-23.md"


class Goal2563BarnesHutAppAdapterBoundaryTest(unittest.TestCase):
    def test_pairwise_force_adapter_lives_in_app_adapter_namespace(self) -> None:
        shared_text = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        app_text = APP_ADAPTER.read_text(encoding="utf-8")

        self.assertNotIn("def pairwise_inverse_square_force_2d_partner_columns", shared_text)
        self.assertNotIn("def _cupy_pairwise_force_2d_kernel", shared_text)
        self.assertIn("def pairwise_inverse_square_force_2d_partner_columns", app_text)
        self.assertIn("def _cupy_pairwise_force_2d_kernel", app_text)
        self.assertIn("not a shared RTDL engine primitive", app_text)

    def test_top_level_compatibility_export_remains(self) -> None:
        self.assertIs(
            rt.pairwise_inverse_square_force_2d_partner_columns,
            barnes_adapter.pairwise_inverse_square_force_2d_partner_columns,
        )
        init_text = INIT.read_text(encoding="utf-8")
        self.assertIn("from .app_adapters import pairwise_inverse_square_force_2d_partner_columns", init_text)

    def test_report_records_app_adapter_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2563", text)
        self.assertIn("pairwise inverse-square force adapter moved out of shared partner adapters", text)
        self.assertIn("top-level `rtdsl` compatibility export", text)


if __name__ == "__main__":
    unittest.main()
