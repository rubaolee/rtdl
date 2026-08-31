from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3850_post_aabb_full_scale_refresh_2026-06-08.md"
BASELINE = ROOT / "docs" / "reports" / "goal3844_current_scale_profiles_refresh_a5000" / "summary.json"
ARTIFACT = ROOT / "docs" / "reports" / "goal3850_post_aabb_full_scale_refresh_a5000" / "summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _row(payload: dict, row_id: str) -> dict:
    return next(row for row in payload["rows"] if row["row_id"] == row_id)


class Goal3850PostAabbFullScaleRefreshTest(unittest.TestCase):
    def test_full_packet_keeps_all_promoted_rows_green(self) -> None:
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

    def test_librts_hot_metric_improves_without_public_claim(self) -> None:
        baseline = _load(BASELINE)
        payload = _load(ARTIFACT)
        row_id = "librts_spatial_index_optix_scale_default_32768"
        old_row = _row(baseline, row_id)
        new_row = _row(payload, row_id)
        old_stdout = _load(ROOT / old_row["stdout_path"])
        new_stdout = _load(ROOT / new_row["stdout_path"])

        self.assertEqual(new_stdout["counts"], old_stdout["counts"])
        old_query = old_stdout["repeat_protocol"]["query_sec_median"]
        new_query = new_stdout["repeat_protocol"]["query_sec_median"]
        self.assertLess(new_query, old_query)
        self.assertGreater(old_query / new_query, 1.15)
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["release_authorized"])

    def test_report_records_boundary_and_delta(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3850",
            "NVIDIA RTX A5000",
            "36ed5346",
            "All ten promoted benchmark apps passed",
            "1.1826x",
            "not a public speedup table",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
