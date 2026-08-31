from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STANDARD_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal3583_rayjoin_hot_promoted_routes_a5000"
    / "summary.json"
)
STRESS_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal3583_rayjoin_hot_promoted_routes_stress_a5000"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3583_rayjoin_hot_promoted_routes_2026-06-06.md"


class Goal3583RayjoinHotPromotedRoutesA5000Test(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        self.assertTrue(path.exists(), f"missing artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _assert_hot_promoted_packet(self, payload: dict) -> None:
        rows = {row["case_id"]: row for row in payload["rows"]}
        optix_rows = {
            case_id: row
            for case_id, row in rows.items()
            if case_id.startswith("rayjoin_optix_promoted_")
        }
        self.assertEqual(len(optix_rows), 3)
        for case_id, row in optix_rows.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(row["status"], "ok")
                self.assertEqual(row["primary_metric_source"], "phases_sec.prepared_query_sec")
                protocol = row["payload"]["repeat_protocol"]
                self.assertEqual(protocol["repeat"], 5)
                self.assertEqual(protocol["warmup"], 1)
                self.assertEqual(protocol["reported_query_metric"], "prepared_query_median")
                self.assertGreater(float(protocol["measured_query_total_sec"]), 0.0)
                boundary = row["payload"]["claim_boundary"]
                for key, value in boundary.items():
                    if key.endswith("_authorized") or key in {
                        "full_rayjoin_reproduction",
                        "paper_scale_perf_claim_authorized",
                        "rtdl_beats_rayjoin_claim_authorized",
                        "whole_app_speedup_claim_authorized",
                    }:
                        self.assertFalse(value, f"{case_id} leaked claim flag {key}")

        ratios = payload["ratios"]
        self.assertEqual(len(ratios), 3)
        for ratio in ratios:
            with self.subTest(group=ratio["comparison_group"]):
                self.assertEqual(ratio["metric_sources"]["optix"], "phases_sec.prepared_query_sec")
                self.assertGreater(float(ratio["optix_speedup_vs_embree"]), 1.0)

    def test_standard_a5000_packet_uses_hot_prepared_promoted_routes(self) -> None:
        payload = self._load(STANDARD_SUMMARY)
        self.assertEqual(payload["tier"], "standard")
        self._assert_hot_promoted_packet(payload)

    def test_optional_stress_a5000_packet_uses_same_hot_contract(self) -> None:
        if not STRESS_SUMMARY.exists():
            self.skipTest("stress artifact was not captured for this run")
        payload = self._load(STRESS_SUMMARY)
        self.assertEqual(payload["tier"], "stress")
        self._assert_hot_promoted_packet(payload)

    def test_report_documents_hot_contract_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("phases_sec.prepared_query_sec", text)
        self.assertIn("repeat `5`, warmup `1`", text)
        self.assertIn("hot prepared-query comparison", text)
        self.assertIn("not full polygon overlay materialization", text)
        self.assertIn("does not authorize", text)
        self.assertIn("full RayJoin paper reproduction", text)


if __name__ == "__main__":
    unittest.main()
