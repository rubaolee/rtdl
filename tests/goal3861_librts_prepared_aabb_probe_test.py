from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3861_librts_prepared_aabb_probe_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3861_librts_aabb_prepared_probe_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3861LibRtsPreparedAabbProbeTest(unittest.TestCase):
    def test_probe_artifact_records_operation_decomposition(self) -> None:
        summary = _load(SUMMARY)
        rows = {row["name"]: row for row in summary["rows"]}

        self.assertEqual(
            set(rows),
            {
                "all_32768_repeat20",
                "point_32768_repeat20",
                "range_contains_32768_repeat20",
                "range_intersects_32768_repeat20",
                "all_65536_repeat10",
            },
        )
        for row in rows.values():
            self.assertEqual(row["returncode"], 0)
            self.assertEqual(row["stderr_tail"], "")
            self.assertGreater(row["payload_elapsed_sec"], row["query_median_sec"])
            self.assertGreater(row["scene_prepare_sec"], 0.0)

        self.assertLess(rows["point_32768_repeat20"]["query_median_sec"], 0.010)
        self.assertLess(rows["range_contains_32768_repeat20"]["query_median_sec"], 0.010)
        self.assertLess(rows["range_intersects_32768_repeat20"]["query_median_sec"], 0.020)
        self.assertGreater(rows["all_65536_repeat10"]["query_median_sec"], rows["all_32768_repeat20"]["query_median_sec"] * 3.0)

    def test_payload_level_timing_is_cold_prepare_dominated(self) -> None:
        summary = _load(SUMMARY)
        all_32k = next(row for row in summary["rows"] if row["name"] == "all_32768_repeat20")
        all_65k = next(row for row in summary["rows"] if row["name"] == "all_65536_repeat10")

        query_prepare_32k = sum(float(value) for value in all_32k["query_prepare_sec"].values())
        query_prepare_65k = sum(float(value) for value in all_65k["query_prepare_sec"].values())

        self.assertGreater(all_32k["scene_prepare_sec"] + query_prepare_32k, all_32k["query_median_sec"] * 20.0)
        self.assertGreater(all_65k["scene_prepare_sec"] + query_prepare_65k, all_65k["query_median_sec"] * 5.0)

    def test_report_records_generic_next_targets_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3861",
            "prepared-session accounting/front-door contract",
            "generic multi-operation AABB count primitive",
            "prepared_aabb_index_multi_count_2d",
            "not LibRTS-specific vocabulary",
            "does not authorize",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()

