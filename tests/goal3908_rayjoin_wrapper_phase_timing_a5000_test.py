from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3908_rayjoin_wrapper_phase_timing_a5000"
PROFILE = ARTIFACT_DIR / "rayjoin_wrapper_phase_profile.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
SOURCE_COMMIT = ARTIFACT_DIR / "source_commit.txt"
REPORT = ROOT / "docs" / "reports" / "goal3908_rayjoin_wrapper_phase_timing_a5000_2026-06-08.md"


class Goal3908RayJoinWrapperPhaseTimingA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_focused_rayjoin_run_passed_with_clean_commit(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertEqual(SOURCE_COMMIT.read_text(encoding="utf-8").strip()[:8], "fe4f3a4b")
        self.assertEqual(self.profile["git_commit"][:8], "fe4f3a4b")
        self.assertEqual(self.profile["git_status_short"], "")
        self.assertTrue(self.profile["all_counts_match"])
        self.assertEqual(
            self.profile["representative_hot_path_summary"]["metric_scope"],
            "per_contract_hot_medians_not_wrapper_wall_time",
        )

    def test_wrapper_phase_timing_identifies_lsi_overlay_as_dominant_phase(self) -> None:
        phases = self.profile["wrapper_phase_timing_sec"]

        self.assertGreater(phases["profile_total_sec"], 9.0)
        self.assertAlmostEqual(phases["profile_total_sec"], self.profile["wrapper_elapsed_sec"])
        self.assertGreater(phases["lsi_overlay_probe_sec"], 6.0)
        self.assertGreater(phases["pip_one_shot_probe_sec"], 2.0)
        self.assertLess(phases["pip_batch_probe_sec"], 1.0)
        self.assertLess(phases["data_dir_resolve_sec"], 0.01)
        self.assertGreater(phases["lsi_overlay_probe_sec"], phases["pip_one_shot_probe_sec"])

    def test_hot_contract_routes_remain_the_same(self) -> None:
        hot = self.profile["representative_hot_path_summary"]

        self.assertLess(hot["pip_one_shot"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertGreater(hot["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["pip_repeated_requests"]["per_request_speedup_vs_single_request"], 8.0)
        self.assertFalse(hot["automatic_partner_selection_authorized"])
        self.assertFalse(hot["public_speedup_claim_authorized"])

    def test_report_preserves_boundary_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3908",
            "LSI/overlay probe wrapper",
            "duplicate data loading/staging",
            "not a public performance comparison",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
