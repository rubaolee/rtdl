import unittest
from pathlib import Path

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1634_v1_6_x_optix_collect_k_final_pair_breakdown_2026-05-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1634_final_pair_breakdown_262144_repeats3.json"


class Goal1634OptixCollectKFinalPairBreakdownInstrumentationTest(unittest.TestCase):
    def test_native_profile_emits_final_pair_breakdown_fields(self) -> None:
        text = API.read_text(encoding="utf-8")

        for field in (
            "final_pair_materialize_launch_ms",
            "final_pair_mark_sync_ms",
            "final_pair_prefix_host_ms",
            "final_pair_compact_launch_ms",
        ):
            self.assertIn(field, text)

        self.assertIn("const bool is_final_output = output_rows == rows_out;", text)
        self.assertIn("profile.final_pair_materialize_launch_ms +=", text)
        self.assertIn("profile.final_pair_mark_sync_ms +=", text)
        self.assertIn("profile.final_pair_prefix_host_ms +=", text)
        self.assertIn("profile.final_pair_compact_launch_ms +=", text)

    def test_stage_profile_probe_summarizes_new_fields_and_accepts_old_records(self) -> None:
        for field in (
            "final_pair_materialize_launch_ms",
            "final_pair_mark_sync_ms",
            "final_pair_prefix_host_ms",
            "final_pair_compact_launch_ms",
        ):
            self.assertIn(field, probe.STAGE_FIELDS)

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
                    "total_ms": 0.3,
                }
            ]
        )

        self.assertEqual(summary["stage_median_ms"]["final_pair_materialize_launch_ms"], 0.0)
        self.assertEqual(summary["stage_median_ms"]["final_pair_mark_sync_ms"], 0.0)
        self.assertEqual(summary["stage_median_ms"]["final_pair_prefix_host_ms"], 0.0)
        self.assertEqual(summary["stage_median_ms"]["final_pair_compact_launch_ms"], 0.0)

    def test_a4500_probe_identifies_final_pair_mark_sync_bottleneck(self) -> None:
        import json

        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = payload["cases"][0]
        medians = case["stage_profile"]["stage_median_ms"]

        self.assertTrue(payload["accepted_goal1506_evidence"])
        self.assertEqual(case["candidate_count"], 262144)
        self.assertEqual(case["stage_profile"]["topology"]["tile_count"], 128)
        self.assertGreater(medians["final_pair_mark_sync_ms"], 0.3)
        self.assertLess(medians["final_pair_materialize_launch_ms"], 0.01)
        self.assertLess(medians["final_pair_prefix_host_ms"], 0.03)
        self.assertLess(medians["final_pair_compact_launch_ms"], 0.01)

    def test_report_preserves_internal_boundary_and_next_direction(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`final_pair_mark_sync_identified`", text)
        self.assertIn("profile-only instrumentation", text)
        self.assertIn("final-pair mark/sync stage dominates", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
