import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1653_v1_6_x_optix_collect_k_defer_merge_sync_remeasure_2026-05-10.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1653_fastest_262144.json"
DEFER_JSON = ROOT / "docs" / "reports" / "goal1653_defer_merge_sync_262144.json"


class Goal1653OptixCollectKDeferMergeSyncRemeasureTest(unittest.TestCase):
    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`defer_merge_sync_candidate_rejected_for_262144`", text)
        self.assertIn("`do_not_promote_for_262144`", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_deferred_sync_preserves_parity_but_does_not_improve_total_time(self) -> None:
        baseline_probe = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
        defer_probe = json.loads(DEFER_JSON.read_text(encoding="utf-8"))
        baseline = baseline_probe["cases"][0]["stage_profile"]["stage_median_ms"]
        deferred = defer_probe["cases"][0]["stage_profile"]["stage_median_ms"]

        self.assertIs(baseline_probe["accepted_goal1506_evidence"], True)
        self.assertIs(defer_probe["accepted_goal1506_evidence"], True)
        self.assertIs(baseline_probe["all_parity_passed"], True)
        self.assertIs(defer_probe["all_parity_passed"], True)
        self.assertLess(deferred["merge_sync_ms"], baseline["merge_sync_ms"] * 0.1)
        self.assertGreater(deferred["final_pair_mark_sync_ms"], baseline["final_pair_mark_sync_ms"] * 5)
        self.assertGreater(deferred["total_ms"], baseline["total_ms"])


if __name__ == "__main__":
    unittest.main()
