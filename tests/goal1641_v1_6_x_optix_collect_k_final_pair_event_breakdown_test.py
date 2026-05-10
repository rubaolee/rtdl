import json
import unittest
from pathlib import Path

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1641_v1_6_x_optix_collect_k_final_pair_event_breakdown_2026-05-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1641_final_pair_materialize_event_262144_repeats5.json"


class Goal1641OptixCollectKFinalPairEventBreakdownTest(unittest.TestCase):
    def test_materialize_event_fields_are_opt_in_profile_only(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("final_pair_materialize_event_ms", text)
        self.assertIn("final_pair_pre_mark_wait_ms", text)
        self.assertIn("materialize_event_start", text)
        self.assertIn("cuEventElapsedTime(&materialize_event_ms", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC", text)

        event_fn = text[
            text.index("static bool collect_k_use_final_pair_mark_event_diagnostic()"):
            text.index("static bool collect_k_use_carry_pointer_diagnostic()")
        ]
        self.assertNotIn("collect_k_use_fastest_candidate", event_fn)

    def test_stage_profile_probe_summarizes_new_fields(self) -> None:
        self.assertIn("final_pair_materialize_event_ms", probe.STAGE_FIELDS)
        self.assertIn("final_pair_pre_mark_wait_ms", probe.STAGE_FIELDS)

    def test_a4500_artifact_shows_pre_mark_wait_dominates(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = payload["cases"][0]
        medians = case["stage_profile"]["stage_median_ms"]

        self.assertTrue(payload["accepted_goal1506_evidence"])
        self.assertTrue(case["same_candidate_rows"])
        self.assertTrue(case["same_valid_count"])
        self.assertEqual(case["candidate_count"], 262144)
        self.assertLess(medians["final_pair_materialize_event_ms"], 0.08)
        self.assertLess(medians["final_pair_mark_event_ms"], 0.05)
        self.assertGreater(medians["final_pair_pre_mark_wait_ms"], 0.2)
        self.assertGreater(
            medians["final_pair_pre_mark_wait_ms"],
            medians["final_pair_materialize_event_ms"] + medians["final_pair_mark_event_ms"],
        )

    def test_report_records_next_direction_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`pre_mark_wait_dominates_final_pair_sync`", text)
        self.assertIn("not another mark/materialize kernel rewrite", text)
        self.assertIn("dependency structure leading into the final pair", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
