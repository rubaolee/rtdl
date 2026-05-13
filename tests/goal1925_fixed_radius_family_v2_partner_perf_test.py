from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1925_fixed_radius_family_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md"


class Goal1925FixedRadiusFamilyV2PartnerPerfTest(unittest.TestCase):
    def test_harness_covers_the_six_missing_fixed_radius_app_rows(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for app in (
            "facility_knn_assignment",
            "hausdorff_distance",
            "ann_candidate_search",
            "outlier_detection",
            "dbscan_clustering",
            "barnes_hut_force_app",
        ):
            with self.subTest(app=app):
                self.assertIn(app, text)

        self.assertIn("prepare_optix_fixed_radius_count_threshold_2d", text)
        self.assertIn("prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene", text)
        self.assertIn("fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns", text)
        self.assertIn("allocate_fixed_radius_count_threshold_2d_partner_device_output_columns", text)
        self.assertIn("return_metadata=True", text)
        self.assertIn("search_y_offset=1.0", text)
        self.assertIn("search_spacing=4.0", text)

    def test_harness_preserves_claim_boundaries_and_progress_output(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("[goal1925] start app=", text)
        self.assertIn("[goal1925] timing", text)
        self.assertIn("--apps", text)
        self.assertIn("--partners", text)
        self.assertIn("--repeat", text)
        self.assertIn("--output", text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)
        self.assertIn('"fixed_radius_family_true_zero_copy_authorized": False', text)

    def test_report_states_pod_needed_and_no_release_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: harness-ready-pod-needed", text)
        self.assertIn("does not authorize a v2.0 release", text)
        self.assertIn("does not claim true zero-copy for this family", text)
        self.assertIn("not the degenerate identical-point-set", text)
        self.assertIn("pod command", text)
        self.assertIn("family a", text.lower())


if __name__ == "__main__":
    unittest.main()
