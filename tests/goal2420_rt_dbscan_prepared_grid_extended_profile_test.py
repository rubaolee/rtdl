from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2420_rt_dbscan_prepared_grid_extended_profile"
REPORT = ROOT / "docs" / "reports" / "goal2420_rt_dbscan_prepared_grid_extended_profile_2026-05-19.md"

PURE_CUPY = "partner_cupy_grid_components_3d"
OLD_RT_GRID = "optix_rt_core_flags_cupy_grid_components_3d"
PREPARED_RT_GRID = "optix_rt_core_flags_cupy_prepared_grid_components_3d"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _tail_median(payload: dict[str, object], mode: str) -> float:
    rows = [row for row in payload["rows"] if row["mode"] == mode]
    return statistics.median(float(row["app_elapsed_sec"]) for row in rows[1:])


class Goal2420RtDbscanPreparedGridExtendedProfileTest(unittest.TestCase):
    def test_extended_artifacts_exist_and_match(self) -> None:
        for name in (
            "clustered3d_262144_repeat3.json",
            "road3d_262144_repeat3.json",
            "ngsim_dense_32768_repeat3.json",
            "ngsim_dense_65536_repeat3.json",
            "ngsim_dense_131072_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertTrue(payload["signatures_match"])
                self.assertEqual(payload["modes"], [PURE_CUPY, OLD_RT_GRID, PREPARED_RT_GRID])
                prepared_rows = [row for row in payload["rows"] if row["mode"] == PREPARED_RT_GRID]
                self.assertEqual([row.get("prepared_grid_reused") for row in prepared_rows], [False, True, True])

    def test_large_clustered_and_road_rows_cross_over_against_pure_cupy(self) -> None:
        for name in (
            "clustered3d_262144_repeat3.json",
            "road3d_262144_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertLess(_tail_median(payload, PREPARED_RT_GRID), _tail_median(payload, PURE_CUPY))
                self.assertLess(_tail_median(payload, PREPARED_RT_GRID), _tail_median(payload, OLD_RT_GRID))

    def test_ngsim_dense_still_favors_pure_cupy_and_report_is_explicit(self) -> None:
        for name in (
            "ngsim_dense_32768_repeat3.json",
            "ngsim_dense_65536_repeat3.json",
            "ngsim_dense_131072_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertLess(_tail_median(payload, PURE_CUPY), _tail_median(payload, PREPARED_RT_GRID))
                self.assertLess(_tail_median(payload, PREPARED_RT_GRID), _tail_median(payload, OLD_RT_GRID))

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Pure CuPy remains faster", report)
        self.assertIn("explicit plan/explain path", report)
        self.assertIn("never claim paper-level RT-DBSCAN reproduction", report)

    def test_report_keeps_dispatch_and_release_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("not hide this behind a magical dispatcher", report)
        self.assertIn("It does not authorize", report)
        self.assertIn("v2.x release closure", report)
        self.assertIn("DBSCAN-specific native engine customization", report)


if __name__ == "__main__":
    unittest.main()
