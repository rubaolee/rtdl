from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4153_rtdbscan_current_vs_single_pass_factor025_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4153_rtdbscan_current_vs_single_pass_negative_probe_2026-06-09.md"


class Goal4153RtDbscanCurrentVsSinglePassNegativeProbeTest(unittest.TestCase):
    def test_probe_rejects_current_vs_single_pass_as_same_contract(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("Goal4153", data["goal"])
        self.assertFalse(data["all_signatures_match_current"])
        self.assertFalse(data["single_pass_promoted_default"])
        self.assertFalse(data["release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["automatic_partner_selection_authorized"])
        self.assertFalse(data["automatic_partition_cell_factor_selection_authorized"])
        self.assertFalse(data["automatic_convergence_mode_selection_authorized"])
        self.assertEqual(15, len(data["rows"]))
        for row in data["rows"]:
            self.assertFalse(row["same_signature_vs_current"], row)

    def test_report_blocks_unfair_speedup_table(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "reject-as-performance-comparison",
            "signatures do not match",
            "not valid same-contract performance comparisons",
            "used as a benchmark claim",
            "does not authorize route promotion",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
