import json
import unittest
from pathlib import Path

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1642_v1_6_x_optix_collect_k_deferred_merge_event_breakdown_2026-05-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1642_merge_event_262144_repeats5.json"


class Goal1642OptixCollectKDeferredMergeEventBreakdownTest(unittest.TestCase):
    def test_merge_event_diagnostic_is_recorded_without_production_flag(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("merge_event_ms", text)
        self.assertIn("PendingMergeEvent", text)
        self.assertIn("resolve_pending_merge_events", text)
        self.assertIn("cuEventRecord(merge_event_start, nullptr)", text)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY", text)

    def test_stage_profile_probe_summarizes_merge_event_field(self) -> None:
        self.assertIn("merge_event_ms", probe.STAGE_FIELDS)

    def test_a4500_artifact_shows_deferred_merge_work_explains_wait(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = payload["cases"][0]
        medians = case["stage_profile"]["stage_median_ms"]

        self.assertTrue(payload["accepted_goal1506_evidence"])
        self.assertTrue(case["same_candidate_rows"])
        self.assertTrue(case["same_valid_count"])
        self.assertEqual(case["candidate_count"], 262144)
        self.assertGreater(medians["merge_event_ms"], 0.3)
        self.assertGreater(medians["merge_event_ms"], medians["final_pair_pre_mark_wait_ms"])
        self.assertGreater(medians["final_pair_pre_mark_wait_ms"], 0.2)

    def test_report_points_next_work_at_merge_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`deferred_merge_work_explains_final_wait`", text)
        self.assertIn("primary remaining cost is the merge chain itself", text)
        self.assertIn("rather than moving the same four final kernels into another graph wrapper", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
