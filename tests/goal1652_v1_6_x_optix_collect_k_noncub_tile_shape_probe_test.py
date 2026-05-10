import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1652_v1_6_x_optix_collect_k_noncub_tile_shape_probe_2026-05-10.md"
FASTEST_JSON = ROOT / "docs" / "reports" / "goal1652_fastest_cub_262144.json"
NONCUB_JSON = ROOT / "docs" / "reports" / "goal1652_noncub_4096_262144.json"


class Goal1652OptixCollectKNonCubTileShapeProbeTest(unittest.TestCase):
    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`noncub_4096_tile_shape_rejected`", text)
        self.assertIn("`do_not_promote`", text)
        self.assertIn("does not authorize", text)
        self.assertIn("public speedup wording", text)
        self.assertIn("preserve the CUB tile sort path", text)

    def test_baseline_fastest_cub_remains_accepted_and_fast(self) -> None:
        probe = json.loads(FASTEST_JSON.read_text(encoding="utf-8"))
        case = probe["cases"][0]
        topology = case["stage_profile"]["topology"]
        medians = case["stage_profile"]["stage_median_ms"]

        self.assertIs(probe["accepted_goal1506_evidence"], True)
        self.assertIs(probe["all_parity_passed"], True)
        self.assertEqual(topology["tile_count"], 128)
        self.assertEqual(topology["sort_launches"], 1)
        self.assertEqual(topology["merge_launches"], 27)
        self.assertLess(medians["total_ms"], 1.0)

    def test_noncub_4096_shape_is_rejected_despite_fewer_merge_launches(self) -> None:
        fastest = json.loads(FASTEST_JSON.read_text(encoding="utf-8"))["cases"][0]
        noncub_probe = json.loads(NONCUB_JSON.read_text(encoding="utf-8"))
        noncub = noncub_probe["cases"][0]
        fastest_topology = fastest["stage_profile"]["topology"]
        noncub_topology = noncub["stage_profile"]["topology"]
        fastest_medians = fastest["stage_profile"]["stage_median_ms"]
        noncub_medians = noncub["stage_profile"]["stage_median_ms"]

        self.assertIs(noncub_probe["accepted_goal1506_evidence"], False)
        self.assertIs(noncub_probe["local_fallback_smoke_only"], True)
        self.assertIs(noncub_probe["all_parity_passed"], True)
        self.assertLess(noncub_topology["tile_count"], fastest_topology["tile_count"])
        self.assertLess(noncub_topology["merge_launches"], fastest_topology["merge_launches"])
        self.assertGreater(noncub_topology["sort_launches"], fastest_topology["sort_launches"])
        self.assertGreater(noncub_medians["sort_sync_ms"], fastest_medians["sort_sync_ms"] * 100)
        self.assertGreater(noncub_medians["total_ms"], fastest_medians["total_ms"] * 50)


if __name__ == "__main__":
    unittest.main()
