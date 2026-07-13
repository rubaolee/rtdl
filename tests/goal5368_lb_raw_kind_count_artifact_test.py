import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json"
)
POD_PROBE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json"
)
PROBE_SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_cell_mbr_frontier_kind_count_probe.py"
)
PARTNER = ROOT / "src" / "rtdsl" / "partner_continuations.py"


class Goal5368LbRawKindCountArtifactTest(unittest.TestCase):
    def test_artifact_records_kind2_denominator_gap_without_authorizing_lb(self):
        data = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            "raw_kind_count_telemetry_ready__author_lb_denominator_still_unmatched",
            data["status"],
        )
        self.assertEqual(
            "raw_kind2_denominator_probe_shows_author_queue_state_gap",
            data["exit_label"],
        )
        comparison = data["comparison"]
        self.assertEqual(27_133_990, comparison["author_offloading_size_rows"])
        self.assertEqual(304_981_889, comparison["rtdl_noinline_raw_kind2_rows"])
        self.assertFalse(comparison["row_count_parity"])
        self.assertGreater(comparison["rtdl_noinline_kind2_div_author"], 11.0)
        self.assertLess(comparison["inline_materialized_rows_div_author"], 1.0)
        self.assertGreater(
            comparison["rtdl_noinline_raw_kind2_rows"],
            data["rtdl_reference_rows"]["author_radius_inline_lb256_heavy_rows_from_goal5367"],
        )
        claims = data["claim_boundary"]
        self.assertTrue(claims["generic_system_telemetry_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "same_denominator_memory_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "rtdl_author_performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(claims[key], key)

    def test_pod_probe_is_count_only_overflow_telemetry(self):
        data = json.loads(POD_PROBE.read_text(encoding="utf-8"))
        frontier = data["frontier"]
        self.assertTrue(frontier["overflowed"])
        self.assertTrue(frontier["overflow_telemetry_only"])
        self.assertEqual(0, frontier["row_count"])
        self.assertEqual(0, frontier["row_capacity"])
        self.assertEqual(589_961_522, frontier["attempted_count"])
        self.assertEqual(
            {"1": 284_979_633, "2": 304_981_889, "3": 0},
            {str(k): int(v) for k, v in frontier["raw_frontier_kind_counts"].items()},
        )
        telemetry = frontier["native_memory_telemetry"]
        self.assertEqual(
            "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v3",
            telemetry["schema"],
        )
        self.assertEqual(304_981_889, telemetry["raw_frontier_kind2_rows"])

    def test_probe_uses_generic_overflow_telemetry_not_downstream_hd(self):
        script = PROBE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("allow_overflow_telemetry=True", script)
        self.assertIn("cell_mbr_nearest_frontier_native_3d_optix_columns", script)
        self.assertNotIn("exact_hausdorff", script)
        self.assertNotIn("nearest_witness_from_cell_mbr_frontier", script)
        self.assertNotIn("max_nearest_distance_witness", script)
        self.assertNotIn("hd_exec", script.lower())
        partner = PARTNER.read_text(encoding="utf-8")
        self.assertIn("allow_overflow_telemetry: bool = False", partner)
        self.assertIn("allow_overflow_telemetry=bool(allow_overflow_telemetry)", partner)


if __name__ == "__main__":
    unittest.main()
