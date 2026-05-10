import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1655_v1_6_x_optix_collect_k_skip_tile_overflow_probe_2026-05-10.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1655_baseline_262144.json"
SKIP_JSON = ROOT / "docs" / "reports" / "goal1655_skip_tile_overflow_262144.json"


class Goal1655OptixCollectKSkipTileOverflowProbeTest(unittest.TestCase):
    def test_rejected_skip_overflow_flag_is_not_retained(self) -> None:
        api = API.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_SKIP_TILE_OVERFLOW_CHECK_DIAGNOSTIC", api)
        self.assertNotIn("collect_k_skip_tile_overflow_check_diagnostic", api)

    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`skip_tile_overflow_check_candidate_rejected`", text)
        self.assertIn("`do_not_promote`", text)
        self.assertIn("candidate code is not retained", text)
        self.assertIn("does not authorize", text)
        self.assertIn("public speedup wording", text)

    def test_skip_probe_reduces_metadata_but_not_total_time(self) -> None:
        baseline_probe = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
        skip_probe = json.loads(SKIP_JSON.read_text(encoding="utf-8"))
        baseline_case = baseline_probe["cases"][0]
        skip_case = skip_probe["cases"][0]
        baseline_medians = baseline_case["stage_profile"]["stage_median_ms"]
        skip_medians = skip_case["stage_profile"]["stage_median_ms"]

        self.assertIs(baseline_probe["accepted_goal1506_evidence"], True)
        self.assertIs(skip_probe["accepted_goal1506_evidence"], False)
        self.assertIs(skip_probe["local_fallback_smoke_only"], True)
        self.assertIs(skip_probe["all_parity_passed"], True)
        self.assertLess(
            skip_case["stage_profile"]["topology"]["metadata_fields_downloaded"],
            baseline_case["stage_profile"]["topology"]["metadata_fields_downloaded"],
        )
        self.assertLess(skip_medians["tile_metadata_download_ms"], baseline_medians["tile_metadata_download_ms"])
        self.assertGreater(skip_medians["total_ms"], baseline_medians["total_ms"])


if __name__ == "__main__":
    unittest.main()
