from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3595_rayjoin_public_cdb_repeat200_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3595_rayjoin_public_cdb_long_repeat_stability_2026-06-06.md"


class Goal3595RayJoinPublicCdbLongRepeatStabilityTest(unittest.TestCase):
    def test_repeat200_artifact_preserves_contract_and_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3593.rayjoin_public_cdb_cupy_same_contract_probe.v1")
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["repeat"], 200)
        self.assertEqual(payload["warmup"], 5)
        self.assertEqual(payload["git_status_short"], "")
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertGreater(payload["summary"]["geomean_rtdl_optix_speedup_vs_cupy_cuda_core"], 10.0)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction_claim_authorized"])

    def test_repeat200_rows_show_expected_mixed_route_direction(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["case_id"]: row for row in payload["rows"]}
        self.assertLess(rows["pip_county512"]["rtdl_optix_speedup_vs_cupy_cuda_core"], 1.0)
        self.assertGreater(rows["lsi_county512_soil512"]["rtdl_optix_speedup_vs_cupy_cuda_core"], 100.0)
        self.assertGreater(rows["overlay_county512_soil512"]["rtdl_optix_speedup_vs_cupy_cuda_core"], 90.0)
        self.assertGreater(rows["overlay_county512_soil512"]["cupy_cuda_core_baseline"]["hot_total_sec"], 9.0)
        for row in rows.values():
            self.assertTrue(row["counts_match"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["paper_reproduction_claim_authorized"])

    def test_report_states_internal_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "internal evidence only",
            "not a RayJoin reproduction",
            "Overlay active-pair dependency count remains strongly RTDL/OptiX-favorable",
            "automatic partner/backend selection",
            "route choice visible",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
