from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2415_rt_dbscan_microcell_pod_evidence"
REPORT = ROOT / "docs" / "reports" / "goal2415_rt_dbscan_microcell_pod_evidence_2026-05-19.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


RT_GRID = "optix_rt_core_flags_cupy_grid_components_3d"
RT_MICROCELL = "optix_rt_core_flags_cupy_microcell_graph_components_3d"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _tail_median(payload: dict[str, object], mode: str) -> float:
    rows = [row for row in payload["rows"] if row["mode"] == mode]
    return statistics.median(float(row["app_elapsed_sec"]) for row in rows[1:])


class Goal2415RtDbscanMicrocellPodEvidenceTest(unittest.TestCase):
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
                self.assertIn(RT_GRID, payload["modes"])
                self.assertIn(RT_MICROCELL, payload["modes"])

    def test_microcell_fast_path_activated_but_did_not_beat_existing_rt_grid(self) -> None:
        activated = 0
        for name in (
            "clustered3d_65536_repeat3.json",
            "clustered3d_131072_repeat3.json",
            "road3d_32768_repeat3.json",
            "road3d_65536_repeat3.json",
            "road3d_131072_repeat3.json",
        ):
            payload = _load(name)
            micro_rows = [row for row in payload["rows"] if row["mode"] == RT_MICROCELL]
            activated += sum(1 for row in micro_rows if row.get("cell_graph_fast_path_active") is True)
            self.assertGreaterEqual(_tail_median(payload, RT_MICROCELL), _tail_median(payload, RT_GRID))
        self.assertGreater(activated, 0)

    def test_clustered_32768_records_correct_fallback(self) -> None:
        payload = _load("clustered3d_32768_repeat3.json")
        micro_rows = [row for row in payload["rows"] if row["mode"] == RT_MICROCELL]

        self.assertTrue(all(row.get("cell_graph_fast_path_active") is False for row in micro_rows))
        self.assertTrue(all(row.get("fallback_reason") == "not_all_points_core" for row in micro_rows))

    def test_report_and_future_todo_record_negative_decision_and_pivot(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("performance-negative", report)
        self.assertIn("Do not promote the microcell continuation", report)
        self.assertIn("prepared CuPy grid continuation hardening", report)
        self.assertIn("Goal2415 tested the corrected clique-safe microcell continuation", todo)
        self.assertIn("treat microcell graph compression as the next performance path", todo)


if __name__ == "__main__":
    unittest.main()
