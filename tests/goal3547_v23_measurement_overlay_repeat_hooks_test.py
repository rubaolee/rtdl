from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.md"
PATCH = ROOT / "docs" / "patches" / "goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_POD_V2_9_REPEAT_HOOK_10S_RERUN_2026-06-06.md"


class Goal3547V23MeasurementOverlayRepeatHooksTest(unittest.TestCase):
    def test_report_documents_overlay_boundary_and_validation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "measurement-only repeat protocol",
            "preserving the historical v2.3 implementation semantics",
            "apply check passed",
            "all five formerly partial rows plan as `internal_repeat_knob`",
            "must not be described as a v2.3 feature change",
            "No release, public speedup",
        ):
            self.assertIn(phrase, text)

    def test_patch_contains_expected_measurement_files_and_not_later_modes(self) -> None:
        text = PATCH.read_text(encoding="utf-8")
        for path in (
            "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "examples/current/apps/simulation/rtdl_barnes_hut_force_app.py",
            "examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
            "examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
            "scripts/goal2626_benchmark_embree_optix_baseline.py",
        ):
            self.assertIn(path, text)
        self.assertIn("_phase_repeat_time", text)
        self.assertIn("query_summed_median_sec", text)
        self.assertNotIn("v2_6_numba_compact_mask_plan", text)
        self.assertNotIn("point_order_mode", text)
        self.assertNotIn("segment_order_mode", text)

    def test_pod_handoff_uses_overlay_patch(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch", text)
        self.assertIn("--v23-root /root/rtdl_v23_overlay", text)
        self.assertIn("--v28-root /root/rtdl_v29_current", text)
        self.assertIn("same-contract measurement overlay", text)


if __name__ == "__main__":
    unittest.main()
