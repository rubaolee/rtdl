from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1964_partner_group_min_max_reductions_2026-05-14.md"


class Goal1964PartnerGroupMinMaxReductionsTest(unittest.TestCase):
    def test_partner_adapter_exposes_min_max_group_reductions(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        for name in ("partner_group_max_by_key", "partner_group_min_by_key"):
            self.assertIn(f"def {name}", adapters)
            self.assertIn(f"from .partner_adapters import {name}", init_text)
            self.assertIn(f'"{name}"', init_text)
        self.assertIn('reduce="amax"', adapters)
        self.assertIn('reduce="amin"', adapters)
        self.assertIn("cupy.maximum.at", adapters)
        self.assertIn("cupy.minimum.at", adapters)
        self.assertIn("group_count must be non-negative", adapters)

    def test_report_positions_min_max_as_generic_continuation_algebra(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("partner_group_max_by_key", report)
        self.assertIn("partner_group_min_by_key", report)
        self.assertIn("exact Hausdorff", report)
        self.assertIn("Barnes-Hut", report)
        self.assertIn("does not add app semantics to the native engine", report)
        self.assertIn("tests.goal1964_partner_group_min_max_reductions_test", preflight)


if __name__ == "__main__":
    unittest.main()
