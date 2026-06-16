from __future__ import annotations

import json
from pathlib import Path
from unittest import mock
import unittest

from examples.current.apps.geospatial import rtdl_facility_knn_assignment as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/apps/geospatial/rtdl_facility_knn_assignment.py"
RUNNER = ROOT / "scripts/v3_0_m26_facility_partner_dual_measure.py"
REPORT = ROOT / "docs/reports/goal4423_v3_0_m26_facility_partner_dual_2026-06-15.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4423_v3_0_m26_facility_partner_dual_copies2048_2026-06-15.json"
)
LARGE_EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4423_v3_0_m26_facility_partner_dual_copies3072_2026-06-15.json"
)


class Goal4423V30M26FacilityPartnerDualTest(unittest.TestCase):
    def test_facility_app_exposes_numba_partner_front_door(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('if partner == "numba"', source)
        self.assertIn("copy_to_host().tolist()", source)
        self.assertIn('choices=("torch", "cupy", "numba")', source)
        self.assertIn("top_k_nearest_points_2d_partner_columns", source)
        self.assertIn("generic partner point-column algebra", source)
        self.assertIn('"rt_core_accelerated": False', source)
        self.assertIn("int(row[\"query_id\"]), int(row[\"neighbor_rank\"])", source)

    def test_mocked_numba_partner_route_reaches_existing_generic_topk(self) -> None:
        fake_result = {
            "columns": {
                "query_ids": _FakeNumbaColumn([1, 2, 3, 4]),
                "neighbor_ids": _FakeNumbaColumn([10, 11, 12, 12]),
                "distances": _FakeNumbaColumn([0.2, 0.728010988928, 0.905538513814, 0.412310562562]),
                "neighbor_rank": _FakeNumbaColumn([1, 1, 1, 1]),
            },
            "metadata": {
                "adapter": "top_k_nearest_points_2d_partner_columns",
                "partner": "numba",
                "partner_reference_contract": "generic_exact_top_k_nearest_points_2d",
                "v2_11_numba_preview_kernel_status": "device_grouped_topk_after_device_score_rows",
                "numba_grouped_topk_device_rank_used": True,
                "host_rank_materialization_used": False,
            },
        }
        with mock.patch.object(app.rt, "point_rows_to_partner_columns", return_value={"ids": object()}):
            with mock.patch.object(
                app.rt,
                "top_k_nearest_points_2d_partner_columns",
                return_value=fake_result,
            ) as topk:
                payload = app.run_case(
                    "partner_exact",
                    copies=1,
                    output_mode="summary",
                    partner="numba",
                )

        topk.assert_called_once()
        self.assertEqual(topk.call_args.kwargs["k"], 1)
        self.assertEqual(topk.call_args.kwargs["partner"], "numba")
        self.assertTrue(topk.call_args.kwargs["return_metadata"])
        self.assertEqual(payload["backend"], "partner_exact")
        self.assertEqual(payload["partner"], "numba")
        self.assertEqual(payload["k"], 1)
        self.assertEqual(payload["row_count"], 4)
        self.assertEqual(payload["primary_depot_load"], {10: 1, 11: 1, 12: 2})
        self.assertEqual(payload["partner_reference_contract"], "generic_exact_top_k_nearest_points_2d")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertFalse(payload["native_continuation_active"])

    def test_runner_records_best_and_numba_partner_comparison(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("--partners", source)
        self.assertIn("cupy,numba", source)
        self.assertIn("best_observed_partner_by_full_app_median", source)
        self.assertIn("best_partner_and_numba_reference_exposed", source)
        self.assertIn("metadata_numba_status", source)
        self.assertIn("signature_match", source)
        self.assertIn("--numba-cuda-home", source)

    def test_report_and_optional_evidence_capture_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Facility KNN Partner Dual-Path Closure",
            "CuPy and Numba",
            "not an RT-core claim",
            "generic top-k nearest point-column primitive",
            "device_grouped_topk_after_device_score_rows",
            "150,994,944",
            "scale-dependent",
        ):
            self.assertIn(phrase, report)

        if not EVIDENCE_JSON.exists():
            self.skipTest("M26 pod evidence JSON has not been generated on this checkout")

        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["parameters"]["copies"], 2048)
        self.assertEqual(payload["parameters"]["logical_pair_count"], 67_108_864)
        self.assertTrue(payload["comparison"]["signature_match"])
        self.assertFalse(payload["comparison"]["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertTrue(payload["claim_boundary"]["best_partner_and_numba_reference_exposed"])
        rows = {row["partner"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"cupy", "numba"})
        self.assertEqual(
            rows["numba"]["metadata_numba_status"],
            "device_grouped_topk_after_device_score_rows",
        )
        self.assertTrue(rows["numba"]["metadata_numba_device_rank_used"])

        if not LARGE_EVIDENCE_JSON.exists():
            self.skipTest("M26 large pod evidence JSON has not been generated on this checkout")
        large = json.loads(LARGE_EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(large["parameters"]["copies"], 3072)
        self.assertEqual(large["parameters"]["logical_pair_count"], 150_994_944)
        self.assertTrue(large["comparison"]["signature_match"])
        self.assertEqual(large["comparison"]["best_observed_partner_by_full_app_median"], "numba")
        large_rows = {row["partner"]: row for row in large["rows"]}
        self.assertEqual(
            large_rows["numba"]["metadata_numba_status"],
            "device_grouped_topk_after_device_score_rows",
        )
        self.assertLess(
            large_rows["numba"]["full_app_wall_seconds_median"],
            large_rows["cupy"]["full_app_wall_seconds_median"],
        )


class _FakeHostArray:
    def __init__(self, values: list[object]) -> None:
        self._values = values

    def tolist(self) -> list[object]:
        return list(self._values)


class _FakeNumbaColumn:
    def __init__(self, values: list[object]) -> None:
        self._values = values

    def copy_to_host(self) -> _FakeHostArray:
        return _FakeHostArray(self._values)


if __name__ == "__main__":
    unittest.main()
