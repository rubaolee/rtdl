import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1654_v1_6_x_optix_collect_k_parallel_compact_threshold_sweep_2026-05-10.md"
REPORT_DIR = ROOT / "docs" / "reports"
CAPS = (4096, 8192, 16384, 32768, 65536)


def _probe(capacity: int) -> dict:
    return json.loads(
        (REPORT_DIR / f"goal1654_min_cap_{capacity}_262144.json").read_text(encoding="utf-8")
    )


class Goal1654OptixCollectKParallelCompactThresholdSweepTest(unittest.TestCase):
    def test_report_records_threshold_decision_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`parallel_compact_min_capacity_4096_retained`", text)
        self.assertIn("`do_not_raise_parallel_compact_threshold`", text)
        self.assertIn("does not authorize public", text)
        self.assertIn("speedup wording", text)

    def test_default_threshold_is_the_fastest_measured_case(self) -> None:
        totals = {
            cap: _probe(cap)["cases"][0]["stage_profile"]["stage_median_ms"]["total_ms"]
            for cap in CAPS
        }

        self.assertEqual(min(totals, key=totals.get), 4096)

    def test_raised_thresholds_preserve_parity_but_regress_merge_sync(self) -> None:
        baseline_probe = _probe(4096)
        baseline_case = baseline_probe["cases"][0]
        baseline_medians = baseline_case["stage_profile"]["stage_median_ms"]
        baseline_topology = baseline_case["stage_profile"]["topology"]

        self.assertIs(baseline_probe["accepted_goal1506_evidence"], True)
        self.assertIs(baseline_probe["all_parity_passed"], True)

        for cap in CAPS[1:]:
            with self.subTest(cap=cap):
                probe = _probe(cap)
                case = probe["cases"][0]
                medians = case["stage_profile"]["stage_median_ms"]
                topology = case["stage_profile"]["topology"]

                self.assertIs(probe["accepted_goal1506_evidence"], False)
                self.assertIs(probe["local_fallback_smoke_only"], True)
                self.assertIs(probe["all_parity_passed"], True)
                self.assertLess(topology["merge_launches"], baseline_topology["merge_launches"])
                self.assertGreater(medians["merge_sync_ms"], baseline_medians["merge_sync_ms"])
                self.assertGreater(medians["total_ms"], baseline_medians["total_ms"])


if __name__ == "__main__":
    unittest.main()
