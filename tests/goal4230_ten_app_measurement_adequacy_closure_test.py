from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4230_ten_app_measurement_adequacy_closure_2026-06-09.md"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Goal4230TenAppMeasurementAdequacyClosureTest(unittest.TestCase):
    def test_all_ten_apps_have_second_level_measurement_evidence(self) -> None:
        values = {
            "hausdorff_xhd": _load(
                "docs/reports/goal4185_short_row_stress_calibration_rtx4000ada/hausdorff_xhd_stress.stdout.json"
            )["repeat_protocol"]["measured_query_total_sec"],
            "spatial_rayjoin": _load(
                "docs/reports/goal4225_release_grade_current_scale_packet_rtx4000ada/outputs/"
                "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default.stdout.json"
            )["representative_hot_path_summary"]["wrapper_elapsed_sec"],
            "rt_dbscan": _load("docs/reports/goal4228_rtdbscan_long_repeat_rtx4000ada/summary.json")[
                "elapsed_sec_total"
            ],
            "robot_collision": _load(
                "docs/reports/goal4225_release_grade_current_scale_packet_rtx4000ada/outputs/"
                "robot_collision_optix_scale_default_1024_no_probe_reference.stdout.json"
            )["run_summary"]["phase_timing_seconds"]["traversal"]["total_sec"],
            "contact_manifold": _load(
                "docs/reports/goal4186_contact_native_collect_repeat_accounting_rtx4000ada/"
                "contact_manifold_optix_grid64_repeat10000.stdout.json"
            )["native_collect_total_sec"],
            "raydb_style": _load(
                "docs/reports/goal4225_release_grade_current_scale_packet_rtx4000ada/outputs/"
                "raydb_style_optix_count_scale_default_262k.stdout.json"
            )["metadata"]["prepared_phase_timing_summary"]["native_call_wall"]["total_sec"],
            "barnes_hut": _load("docs/reports/goal4229_barnes_hut_numba_long_repeat_rtx4000ada/summary.json")[
                "force_kernel_total_sec"
            ],
            "librts_spatial_index": _load(
                "docs/reports/goal4185_short_row_stress_calibration_rtx4000ada/"
                "librts_spatial_index_stress.stdout.json"
            )["repeat_protocol"]["query_sec_total"],
            "rtnn": sum(
                _load(
                    "docs/reports/goal4189_rtnn_repeat10000_stress_rtx4000ada/"
                    "rtnn_prepared_optix_65536_repeat10000.stdout.json"
                )["runner_payload"]["elapsed_runs_sec"]
            ),
            "triangle_counting": _load(
                "docs/reports/goal4185_short_row_stress_calibration_rtx4000ada/"
                "triangle_counting_stress.stdout.json"
            )["timing_ms"]["run_backend"]
            / 1000.0,
        }

        self.assertEqual(
            set(values),
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            },
        )
        for app, seconds in values.items():
            self.assertGreater(seconds, 1.0, app)

    def test_report_lists_all_apps_and_keeps_release_boundary_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for app in (
            "hausdorff_xhd",
            "spatial_rayjoin",
            "rt_dbscan",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "barnes_hut",
            "librts_spatial_index",
            "rtnn",
            "triangle_counting",
        ):
            self.assertIn(f"`{app}`", text)
        for phrase in (
            "not a release authorization",
            "does not authorize release action",
            "AMD/HIPRT functional and timing evidence",
            "fresh multi-AI review",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
