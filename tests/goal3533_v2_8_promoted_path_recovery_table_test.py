from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3533_v2_8_promoted_path_recovery_table_2026-06-05.md"
GOAL3531_WARM = ROOT / "docs" / "reports" / "goal3531_barnes_hut_p0_warm_probe_a5000" / "summary.json"
GOAL3532_PACKET = ROOT / "docs" / "reports" / "goal3532_rayjoin_promoted_contract_packet_a5000_cdb_pair" / "summary.json"


class Goal3533PromotedPathRecoveryTableTest(unittest.TestCase):
    def test_report_records_recovery_without_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "internal recovery table for Goal3527",
            "Warm prepared-query: `0.983x` at 8192 bodies, `1.015x` at 32768 bodies",
            "Split into 10 promoted contract rows",
            "not a RayJoin paper reproduction",
            "does not justify public release or speedup claims",
        ):
            self.assertIn(phrase, text)
        forbidden = (
            "release authorized",
            "public speedup authorized",
            "RTDL beats RayJoin",
        )
        lowered = text.lower()
        for phrase in forbidden:
            self.assertNotIn(phrase.lower(), lowered)

    def test_barnes_hut_warm_probe_clears_goal3527_recovery_bar(self) -> None:
        payload = json.loads(GOAL3531_WARM.read_text(encoding="utf-8"))
        ratios = {int(row["body_count"]): row for row in payload["ratios"]}
        self.assertGreaterEqual(ratios[8192]["v28_speedup_vs_v23_warm"], 0.95)
        self.assertGreaterEqual(ratios[32768]["v28_speedup_vs_v23_warm"], 0.95)
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_8_release_authorized"])

    def test_rayjoin_packet_is_split_and_claim_clean(self) -> None:
        payload = json.loads(GOAL3532_PACKET.read_text(encoding="utf-8"))
        self.assertEqual(payload["row_count"], 10)
        row_ids = {row["row_id"] for row in payload["rows"]}
        self.assertIn("rayjoin_relation_grouped_count_cdb_pair", row_ids)
        self.assertIn("rayjoin_overlay_area_tile_executor_cdb_pair", row_ids)
        for row in payload["rows"]:
            boundary = row["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
