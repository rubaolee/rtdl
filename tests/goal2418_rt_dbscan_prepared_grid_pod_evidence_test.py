from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2418_rt_dbscan_prepared_grid_pod_evidence"
REPORT = ROOT / "docs" / "reports" / "goal2418_rt_dbscan_prepared_grid_pod_evidence_2026-05-19.md"

PURE_CUPY = "partner_cupy_grid_components_3d"
OLD_RT_GRID = "optix_rt_core_flags_cupy_grid_components_3d"
PREPARED_RT_GRID = "optix_rt_core_flags_cupy_prepared_grid_components_3d"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _tail_median(payload: dict[str, object], mode: str) -> float:
    rows = [row for row in payload["rows"] if row["mode"] == mode]
    return statistics.median(float(row["app_elapsed_sec"]) for row in rows[1:])


class Goal2418RtDbscanPreparedGridPodEvidenceTest(unittest.TestCase):
    def test_artifacts_exist_and_signatures_match(self) -> None:
        for name in (
            "clustered3d_32768_repeat3.json",
            "clustered3d_65536_repeat3.json",
            "clustered3d_131072_repeat3.json",
            "road3d_32768_repeat3.json",
            "road3d_65536_repeat3.json",
            "road3d_131072_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertTrue(payload["signatures_match"])
                self.assertEqual(
                    payload["modes"],
                    [PURE_CUPY, OLD_RT_GRID, PREPARED_RT_GRID],
                )
                prepared_rows = [row for row in payload["rows"] if row["mode"] == PREPARED_RT_GRID]
                self.assertEqual([row.get("prepared_grid_reused") for row in prepared_rows], [False, True, True])
                self.assertTrue(all(row.get("rt_core_accelerated") is True for row in prepared_rows))

    def test_prepared_grid_beats_old_rt_grid_on_all_pod_rows(self) -> None:
        for name in (
            "clustered3d_32768_repeat3.json",
            "clustered3d_65536_repeat3.json",
            "clustered3d_131072_repeat3.json",
            "road3d_32768_repeat3.json",
            "road3d_65536_repeat3.json",
            "road3d_131072_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertLess(_tail_median(payload, PREPARED_RT_GRID), _tail_median(payload, OLD_RT_GRID))

    def test_clustered_rows_beat_pure_cupy_and_road_boundary_is_explicit(self) -> None:
        for name in (
            "clustered3d_65536_repeat3.json",
            "clustered3d_131072_repeat3.json",
        ):
            payload = _load(name)
            self.assertLess(_tail_median(payload, PREPARED_RT_GRID), _tail_median(payload, PURE_CUPY))

        road_large = _load("road3d_131072_repeat3.json")
        self.assertLess(_tail_median(road_large, PREPARED_RT_GRID), 1.05 * _tail_median(road_large, PURE_CUPY))

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Road-shaped data remains the weak spot", report)
        self.assertIn("only near parity at 131k", report)

    def test_report_claim_boundary_stays_narrow(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Prepared generic partner continuation improves", report)
        self.assertIn("It does not authorize", report)
        self.assertIn("paper reproduction", report)
        self.assertIn("a DBSCAN-specific native ABI", report)


if __name__ == "__main__":
    unittest.main()
