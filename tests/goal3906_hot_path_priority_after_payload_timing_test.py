from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3905_current_scale_after_robot_timing_aliases_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3906_hot_path_priority_after_payload_timing_2026-06-08.md"


def _payload_for(row: dict[str, object]) -> dict[str, object]:
    path = ARTIFACT_DIR / "outputs" / PurePosixPath(str(row["stdout_path"])).name
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3906HotPathPriorityAfterPayloadTimingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.rows = {row["app"]: row for row in cls.summary["rows"]}
        cls.payloads = {app: _payload_for(row) for app, row in cls.rows.items()}

    def test_process_elapsed_is_not_the_hot_signal_for_wrapper_dominated_rows(self) -> None:
        hot_signals = {
            "robot_collision": self.payloads["robot_collision"]["benchmark_timing_sec"]["tail_total_run_sec"],
            "contact_manifold": self.payloads["contact_manifold"]["native_collect_elapsed_sec"],
            "raydb_style": self.payloads["raydb_style"]["elapsed_sec"],
            "rtnn": self.payloads["rtnn"]["runner_payload"]["elapsed_median_sec"],
            "triangle_counting": self.payloads["triangle_counting"]["timing_ms"]["query_median_ms"] / 1000.0,
        }
        for app, hot_sec in hot_signals.items():
            with self.subTest(app=app):
                process_sec = float(self.rows[app]["elapsed_sec"])
                self.assertGreater(process_sec / float(hot_sec), 100.0)

    def test_librts_is_prepare_once_query_many_not_hot_query_failure(self) -> None:
        payload = self.payloads["librts_spatial_index"]
        scene_prepare = payload["run_phases"]["scene_prepare_sec"]
        query_prepare = sum(payload["run_phases"]["query_prepare_sec"].values())
        query_median = payload["repeat_protocol"]["query_sec_median"]

        self.assertGreater(scene_prepare, query_median * 10.0)
        self.assertGreater(query_prepare, query_median * 2.0)
        self.assertTrue(payload["prepared_session_residency"]["prepare_once_query_many_pattern"])
        self.assertTrue(payload["multi_operation_native_used"])

    def test_rt_dbscan_remaining_hot_cost_is_not_signature_materialization(self) -> None:
        payload = self.payloads["rt_dbscan"]
        breakdown = payload["metadata"]["benchmark_timing_breakdown"]["host_observed_sec"]

        self.assertLess(breakdown["column_signature_sec"], 0.01)
        self.assertGreater(breakdown["adapter_run_sec"], breakdown["column_signature_sec"] * 10.0)
        self.assertEqual(payload["metadata"]["column_signature_strategy"], "numba_segmented_count_all_core_labels")

    def test_report_records_next_targets_without_overclaim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3906",
            "prepared-session cache/reuse evidence",
            "generic grouped-union/stream adapter cost",
            "input staging and reusable dataset/session setup",
            "does not authorize release action",
            "not a public performance comparison",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
