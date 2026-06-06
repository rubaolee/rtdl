from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3546_v2_9_v23_same_contract_repeat_adapter_audit_2026-06-06.md"


class Goal3546V23SameContractRepeatAdapterAuditTest(unittest.TestCase):
    def test_report_records_historical_commit_and_missing_harness(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("2a28365d0246d51f3e3322b546f8a68c58632db4", text)
        self.assertIn("scripts/goal3536_v2_8_vs_v2_3_10s_steady_state.py", text)
        self.assertIn("does not exist in the v2.3 evidence commit", text)

    def test_report_records_patch_probe_results(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "direct patch from Goal3542 fails",
            "narrower measurement-only patch",
            "Applied patch to Hausdorff app cleanly",
            "Applied patch to RayJoin app with conflicts",
            "RayJoin-specific",
        ):
            self.assertIn(phrase, text)

    def test_report_defines_same_contract_adapter_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Do not backport unrelated v2.6/v2.8 app-layer options",
            "stable row-count checks for repeated raw views",
            "same-contract measurement",
            "must not change the historical v2.3 app/primitive semantics",
            "does not authorize v2.9 release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
