from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1856_segment_polygon_v2_partner_perf.py"


class Goal1856SegmentPolygonV2PartnerPerfRunnerTest(unittest.TestCase):
    def test_runner_records_same_contract_timing_boundaries(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("segment_polygon_anyhit_rows_native_bounded_optix", text)
        self.assertIn("segment_polygon_anyhit_rows_optix_partner_columns", text)
        self.assertIn("v1_8_native_optix_rows", text)
        self.assertIn("v2_0_partner_columns_", text)
        self.assertIn("query_median_ratio_vs_v1_8_native", text)
        self.assertIn('"same_contract_timing_row": True', text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', text)
        self.assertIn('"package_install_claim_authorized": False', text)

    def test_runner_prints_progress_for_pod_use(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("[setup]", text)
        self.assertIn("[timing]", text)
        self.assertIn("[artifact]", text)
        self.assertIn("flush=True", text)


if __name__ == "__main__":
    unittest.main()
