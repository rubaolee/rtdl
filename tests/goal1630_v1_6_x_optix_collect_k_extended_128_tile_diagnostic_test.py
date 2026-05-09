import os
import unittest
from pathlib import Path

from scripts.goal1503_v1_5_4_optix_collect_k_scaling_probe import _expected_native_path


ROOT = Path(__file__).resolve().parents[1]
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1630_v1_6_x_optix_collect_k_extended_128_tile_diagnostic_2026-05-09.md"
PROBE_JSON = ROOT / "docs" / "reports" / "goal1630_extended_128_tile_262144_probe.json"
NODEFER_JSON = ROOT / "docs" / "reports" / "goal1630_extended_128_tile_262144_nodefer_repeats5.json"
DEFER_JSON = ROOT / "docs" / "reports" / "goal1630_extended_128_tile_262144_defer_repeats5.json"


class Goal1630OptixCollectKExtended128TileDiagnosticTest(unittest.TestCase):
    def test_native_extension_is_opt_in_and_bounded(self) -> None:
        text = API_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC", text)
        self.assertIn("kCollectKRowWidth2BaseMaxTiledCandidates = 131072", text)
        self.assertIn("kCollectKRowWidth2ExtendedMaxTiledCandidates = 262144", text)
        self.assertIn("kCollectKRowWidth2ExtendedMaxTileSegments = 128", text)
        self.assertIn("kCollectKRowWidth2ExtendedMaxPrefixBlocks = 1024", text)
        self.assertIn("COLLECT_K_BOUNDED compact-level descriptor capacity exceeded", text)

    def test_stage_profile_expected_path_honors_opt_in_extension(self) -> None:
        original = os.environ.get("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC")
        try:
            os.environ.pop("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC", None)
            self.assertEqual(
                _expected_native_path(131073, 2),
                "dynamic_row_width_single_thread_fallback",
            )

            os.environ["RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC"] = "1"
            self.assertEqual(
                _expected_native_path(131073, 2),
                "row_width2_bounded_multi_tile_sort_merge",
            )
            self.assertEqual(
                _expected_native_path(262144, 2),
                "row_width2_bounded_multi_tile_sort_merge",
            )
            self.assertEqual(
                _expected_native_path(262145, 2),
                "dynamic_row_width_single_thread_fallback",
            )
        finally:
            if original is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC"] = original

    def test_a4500_artifacts_record_accepted_128_tile_path(self) -> None:
        import json

        probe = json.loads(PROBE_JSON.read_text(encoding="utf-8"))
        case = probe["cases"][0]
        topology = case["stage_profile"]["topology"]

        self.assertTrue(probe["accepted_goal1506_evidence"])
        self.assertEqual(case["candidate_count"], 262144)
        self.assertEqual(topology["native_path"], "row_width2_bounded_multi_tile_sort_merge")
        self.assertEqual(topology["tile_count"], 128)

    def test_a4500_repeats5_comparison_preserves_parity_and_internal_delta(self) -> None:
        import json

        nodefer = json.loads(NODEFER_JSON.read_text(encoding="utf-8"))
        defer = json.loads(DEFER_JSON.read_text(encoding="utf-8"))
        nodefer_case = nodefer["cases"][0]
        defer_case = defer["cases"][0]
        nodefer_stage = nodefer_case["stage_profile"]["stage_median_ms"]
        defer_stage = defer_case["stage_profile"]["stage_median_ms"]

        self.assertTrue(nodefer["accepted_goal1506_evidence"])
        self.assertTrue(defer["accepted_goal1506_evidence"])
        self.assertTrue(nodefer_case["same_candidate_rows"])
        self.assertTrue(defer_case["same_candidate_rows"])
        self.assertEqual(nodefer_case["stage_profile"]["topology"]["tile_count"], 128)
        self.assertEqual(defer_case["stage_profile"]["topology"]["tile_count"], 128)
        self.assertLess(defer_stage["total_ms"], nodefer_stage["total_ms"])

    def test_report_keeps_claim_boundary_internal(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("extended_128_tile_diagnostic_candidate_recorded", text)
        self.assertIn("default tiled boundary remains `131072`", text)
        self.assertIn("tile count: `128`", text)
        self.assertIn("does\nnot authorize public speedup wording", text)
        self.assertIn("stable\n`COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
