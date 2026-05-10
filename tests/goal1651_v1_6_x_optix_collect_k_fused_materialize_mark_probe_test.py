import unittest
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1651_v1_6_x_optix_collect_k_fused_materialize_mark_probe_2026-05-10.md"
FUSED_JSON = ROOT / "docs" / "reports" / "goal1651_fused_262144.json"


class Goal1651OptixCollectKFusedMaterializeMarkProbeTest(unittest.TestCase):
    def test_rejected_fused_materialize_mark_flag_is_not_retained(self) -> None:
        api = API.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_FUSED_MATERIALIZE_MARK_DIAGNOSTIC", api)
        self.assertNotIn("collect_k_use_fused_materialize_mark_diagnostic()", api)
        self.assertIn("g_collect_k_i64_row_width2_final_materialize_mark_counts_level_counts.fn", api)

    def test_report_records_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`fused_materialize_mark_candidate_rejected`", text)
        self.assertIn("candidate code is not retained", text)
        self.assertIn("`do_not_promote`", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_negative_artifact_records_regression(self) -> None:
        case = json.loads(FUSED_JSON.read_text(encoding="utf-8"))["cases"][0]

        self.assertTrue(case["same_candidate_rows"])
        self.assertGreater(case["stage_profile"]["stage_median_ms"]["total_ms"], 1.0)
        self.assertGreater(case["stage_profile"]["stage_median_ms"]["merge_sync_ms"], 0.6)


if __name__ == "__main__":
    unittest.main()
