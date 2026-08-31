from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4388_partner_dual_implementation_policy_and_app_perf_2026-06-15.md"
PARTNER_MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
WORDING = ROOT / "docs/release_reports/v2_14/public_wording_boundaries.md"
FINAL_CLOSEOUT = ROOT / "docs/release_reports/v2_14/final_closeout.md"
M1_UNLOCK = ROOT / "docs/reports/goal4387_v3_0_m1_design_only_unlock_2026-06-15.md"


class Goal4388PartnerDualImplementationPolicyTest(unittest.TestCase):
    def test_report_summarizes_current_app_performance(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "RTNN ranked summary",
            "RTDBSCAN core flags",
            "RayJoin LSI",
            "RayJoin PIP",
            "RayJoin overlay",
            "RayDB-style grouped count",
            "LibRTS AABB",
            "Triangle counting",
            "Barnes-Hut node coverage",
            "Hausdorff threshold",
            "Robot collision",
            "Contact manifold",
        ):
            self.assertIn(phrase, text)
        self.assertIn("total 1.05x OptiX over Embree", text)
        self.assertIn("AABB query 1.23x", text)

    def test_partner_needed_rows_require_best_partner_and_numba(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("current best-performance partner", text)
        self.assertIn("Numba implementation", text)
        self.assertIn("no-C++/CUDA-kernel-writing path", text)
        self.assertIn("RTDBSCAN", text)
        self.assertIn("RayJoin PIP/overlay", text)
        self.assertIn("Barnes-Hut full force", text)
        self.assertIn("Triangle candidate compaction", text)

    def test_policy_is_carried_into_partner_matrix_and_release_boundaries(self) -> None:
        matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        self.assertIn("current v2.14 closeout guidance", matrix)
        self.assertIn("current best-performance partner", matrix)
        self.assertIn("Numba implementation", matrix)
        self.assertIn("same contract, data, repeat protocol, and oracle", matrix)

        wording = WORDING.read_text(encoding="utf-8")
        self.assertIn("both the current best partner and a same-contract Numba reference", wording)

    def test_v3_m1_unlock_inherits_dual_partner_gate(self) -> None:
        closeout = FINAL_CLOSEOUT.read_text(encoding="utf-8")
        self.assertIn("partner-dependent benchmark claims include both", closeout)
        self.assertIn("same-contract Numba reference", closeout)

        unlock = M1_UNLOCK.read_text(encoding="utf-8")
        self.assertIn("current best partner plus Numba reference", unlock)


if __name__ == "__main__":
    unittest.main()
