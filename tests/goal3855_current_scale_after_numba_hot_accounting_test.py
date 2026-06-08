from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3855_current_scale_after_numba_hot_accounting_2026-06-08.md"
ARTIFACT = ROOT / "docs/reports/goal3855_current_scale_after_numba_hot_accounting_a5000/summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _row(payload: dict, app: str) -> dict:
    return next(row for row in payload["rows"] if row["app"] == app)


class Goal3855CurrentScaleAfterNumbaHotAccountingTest(unittest.TestCase):
    def test_full_a5000_packet_keeps_all_promoted_rows_green(self) -> None:
        payload = _load(ARTIFACT)

        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertEqual(len(payload["rows"]), 10)
        self.assertEqual({row["app"] for row in payload["rows"]}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        for row in payload["rows"]:
            self.assertEqual(row["status"], "pass", row["row_id"])
            self.assertEqual(row["stderr_bytes"], 0, row["row_id"])
            self.assertTrue(row["semantic_stdout_check"]["stdout_json_parseable"], row["row_id"])
            self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [], row["row_id"])

    def test_numba_hot_accounting_rows_are_visible(self) -> None:
        payload = _load(ARTIFACT)

        rt_dbscan_payload = _load(ROOT / _row(payload, "rt_dbscan")["stdout_path"])
        self.assertEqual(
            rt_dbscan_payload["metadata"]["path"],
            "optix_rt_count_threshold_numba_prepared_grid_radius_graph_column_signature_3d",
        )
        self.assertLess(rt_dbscan_payload["elapsed_sec"], 0.5)
        self.assertFalse(rt_dbscan_payload["metadata"]["materializes_python_rows"])

        barnes_payload = _load(ROOT / _row(payload, "barnes_hut")["stdout_path"])
        barnes_meta = barnes_payload["partner_metadata"]
        self.assertFalse(barnes_meta["materializes_python_force_rows"])
        self.assertLess(barnes_meta["prepared_force_repeat_protocol"]["median_force_kernel_sec"], 0.02)

    def test_triangle_counting_is_next_hot_target(self) -> None:
        payload = _load(ARTIFACT)
        triangle_payload = _load(ROOT / _row(payload, "triangle_counting")["stdout_path"])
        section = triangle_payload["section"]

        self.assertEqual(section["optix_performance"]["class"], "host_indexed_fallback")
        self.assertFalse(section["rt_core_accelerated"])
        self.assertGreater(section["run_phases"]["query_raw_view_sec"], 0.5)

    def test_report_records_boundary_and_target_selection(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3855",
            "All ten rows passed",
            "RT-DBSCAN is no longer the largest hot path",
            "Triangle counting is now the clearest hot path",
            "host_indexed_fallback",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
