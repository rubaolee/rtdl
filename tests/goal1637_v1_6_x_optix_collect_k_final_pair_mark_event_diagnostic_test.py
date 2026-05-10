import unittest
from pathlib import Path

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1637_v1_6_x_optix_collect_k_final_pair_mark_event_probe_2026-05-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1637_final_pair_mark_event_262144_repeats5.json"


class Goal1637OptixCollectKFinalPairMarkEventDiagnosticTest(unittest.TestCase):
    def test_mark_event_diagnostic_is_profile_only_and_opt_in(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC", text)
        self.assertIn("collect_k_use_final_pair_mark_event_diagnostic", text)
        self.assertIn("cuEventRecord(mark_event_start, nullptr)", text)
        self.assertIn("cuEventRecord(mark_event_stop, nullptr)", text)
        self.assertIn("cuEventElapsedTime(&mark_event_ms", text)
        self.assertIn("final_pair_materialize_event_ms", text)
        self.assertIn("final_pair_mark_event_ms", text)
        self.assertIn("final_pair_mark_host_wait_ms", text)
        self.assertIn("final_pair_pre_mark_wait_ms", text)

        event_fn = text[
            text.index("static bool collect_k_use_final_pair_mark_event_diagnostic()"):
            text.index("static bool collect_k_use_carry_pointer_diagnostic()")
        ]
        self.assertNotIn("collect_k_use_fastest_candidate", event_fn)

    def test_stage_profile_probe_summarizes_event_fields_and_old_records(self) -> None:
        self.assertIn("final_pair_mark_event_ms", probe.STAGE_FIELDS)
        self.assertIn("final_pair_mark_host_wait_ms", probe.STAGE_FIELDS)
        self.assertIn("final_pair_materialize_event_ms", probe.STAGE_FIELDS)
        self.assertIn("final_pair_pre_mark_wait_ms", probe.STAGE_FIELDS)

        summary = probe._summarize_records(
            [
                {
                    "native_path": "row_width2_bounded_multi_tile_sort_merge",
                    "tile_count": 2,
                    "merge_levels": 1,
                    "sort_launches": 1,
                    "merge_launches": 3,
                    "carry_copies": 0,
                    "carry_payload_copies": 0,
                    "final_copies": 0,
                    "metadata_fields_downloaded": 1,
                    "module_load_ms": 0.0,
                    "allocation_ms": 0.0,
                    "sort_launch_ms": 0.0,
                    "sort_sync_ms": 0.0,
                    "tile_metadata_download_ms": 0.0,
                    "merge_launch_ms": 0.1,
                    "merge_sync_ms": 0.2,
                    "merge_metadata_download_ms": 0.0,
                    "carry_copy_ms": 0.0,
                    "final_copy_ms": 0.0,
                    "final_pair_materialize_launch_ms": 0.01,
                    "final_pair_mark_sync_ms": 0.02,
                    "final_pair_prefix_host_ms": 0.03,
                    "final_pair_compact_launch_ms": 0.04,
                    "total_ms": 0.3,
                }
            ]
        )

        self.assertEqual(summary["stage_median_ms"]["final_pair_mark_event_ms"], 0.0)
        self.assertEqual(summary["stage_median_ms"]["final_pair_mark_host_wait_ms"], 0.0)
        self.assertEqual(summary["stage_median_ms"]["final_pair_materialize_event_ms"], 0.0)
        self.assertEqual(summary["stage_median_ms"]["final_pair_pre_mark_wait_ms"], 0.0)

    def test_a4500_event_artifact_shows_wait_not_kernel_time(self) -> None:
        import json

        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = payload["cases"][0]
        medians = case["stage_profile"]["stage_median_ms"]

        self.assertTrue(payload["accepted_goal1506_evidence"])
        self.assertTrue(case["same_candidate_rows"])
        self.assertTrue(case["same_valid_count"])
        self.assertEqual(case["candidate_count"], 262144)
        self.assertLess(medians["final_pair_mark_event_ms"], 0.05)
        self.assertGreater(medians["final_pair_mark_host_wait_ms"], 0.25)
        self.assertGreater(medians["final_pair_mark_sync_ms"], medians["final_pair_mark_event_ms"])

    def test_report_records_next_direction_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`final_pair_mark_wait_not_kernel_time`", text)
        self.assertIn("Do not optimize the mark kernel first", text)
        self.assertIn("CUDA graph replay or stream-dependency structure", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
