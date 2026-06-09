from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal4075_numba_signature_workspace_reset_fusion_2026-06-09.md"


class Goal4075NumbaSignatureWorkspaceResetFusionTest(unittest.TestCase):
    def test_signature_path_uses_fused_workspace_reset_kernel(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("_NUMBA_I64_SIGNATURE_WORKSPACE_ZERO_KERNEL", source)
        self.assertIn("def _numba_i64_signature_workspace_zero_kernel", source)
        self.assertIn("self.signature_workspace_zero_kernel = _numba_i64_signature_workspace_zero_kernel(cuda)", source)
        self.assertIn("self.signature_workspace_zero_kernel[self.signature_count_blocks, self.threads]", source)
        self.assertNotIn("self.i64_zero_kernel[(1,), self.threads](self.signature_flag_true_count, 1)", source)
        self.assertNotIn("self.i64_zero_kernel[(1,), self.threads](self.signature_negative_label_count, 1)", source)

    def test_report_records_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4075",
            "zero_signature_workspace_kernel",
            "generic partner-continuation cleanup",
            "does not alter the native grouped-union primitive",
            "does not authorize release",
            "native ABI",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
