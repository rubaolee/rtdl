from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1922_numba_triton_strategy_preplanning_2026-05-13.md"


class Goal1922NumbaTritonStrategyPreplanningTest(unittest.TestCase):
    def test_strategy_keeps_v2_clean_and_places_kernel_interop_later(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: exploratory-roadmap-note", text)
        self.assertIn("Do not make Numba, Triton, or CuPy `RawKernel` part of the v2.0 release", text)
        self.assertIn("v2.0: partner tensor composition only", text)
        self.assertIn("v2.5: external custom-kernel interop examples", text)
        self.assertIn("v3.0: possible custom engine/shader extension ABI", text)
        self.assertIn("outside the", text)
        self.assertIn("RTDL native engine", text)
        self.assertIn("This note does not change v2.0 release criteria", text)


if __name__ == "__main__":
    unittest.main()
