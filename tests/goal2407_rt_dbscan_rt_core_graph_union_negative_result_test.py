from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2407_rt_dbscan_rt_core_graph_union_pod"
REPORT = ROOT / "docs" / "reports" / "goal2407_rt_dbscan_rt_core_graph_union_negative_result_2026-05-19.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _tail_median(payload: dict[str, object], mode: str) -> float:
    rows = [row for row in payload["rows"] if row["mode"] == mode]
    return statistics.median(float(row["app_elapsed_sec"]) for row in rows[1:])


class Goal2407RtDbscanRtCoreGraphUnionNegativeResultTest(unittest.TestCase):
    def test_artifacts_record_matching_signatures(self) -> None:
        for name in (
            "clustered3d_4096_repeat3.json",
            "clustered3d_131072_repeat3.json",
            "road3d_4096_repeat3.json",
            "road3d_131072_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertTrue(payload["signatures_match"])
                self.assertIn("optix_rt_core_graph_components_3d", payload["modes"])

    def test_core_graph_union_did_not_beat_goal2405_dense_path(self) -> None:
        payload = _load("clustered3d_131072_repeat3.json")
        goal2405 = _tail_median(payload, "optix_rt_core_flags_cupy_grid_components_3d")
        goal2407 = _tail_median(payload, "optix_rt_core_graph_components_3d")

        self.assertGreater(goal2407, goal2405)

    def test_report_and_future_todo_preserve_the_negative_decision(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("rejected/deferred prototype", report)
        self.assertIn("no runtime API landed", report)
        self.assertIn("simply moving union-find", report)
        self.assertIn("into OptiX any-hit is not the right", report)
        self.assertIn("do not promote raw any-hit", todo.lower())
        self.assertIn("union as the continuation primitive", todo.lower())


if __name__ == "__main__":
    unittest.main()
