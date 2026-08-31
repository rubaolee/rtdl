from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal3872_prepared_session_amortization_probe.py"
REPORT = ROOT / "docs/reports/goal3872_prepared_session_amortization_2026-06-08.md"
ARTIFACT = ROOT / "docs/reports/goal3872_prepared_session_amortization_a5000/summary.json"
EXIT_CODE = ROOT / "docs/reports/goal3872_prepared_session_amortization_a5000/exit_code"
TODO = ROOT / "docs/research/future_version_to_do_list.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3872PreparedSessionAmortizationTest(unittest.TestCase):
    def test_probe_script_uses_generic_prepared_rows_and_claim_guard(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepared_session_amortization_probe", text)
        self.assertIn("fixed_radius_threshold_2d", text)
        self.assertIn("aabb_index_query_2d", text)
        self.assertIn("fixed_radius_neighbors_3d_ranked_summary", text)
        self.assertIn("ray_triangle_weighted_any_hit_sum_3d", text)
        self.assertIn("FORBIDDEN_TRUE_FLAGS", text)
        self.assertIn("all_claim_boundaries_clean", text)

    def test_a5000_artifact_quantifies_prepare_to_query_gap(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        payload = _load(ARTIFACT)

        self.assertEqual(payload["schema"], "rtdl.goal3872.prepared_session_amortization_probe.v1")
        self.assertEqual(payload["source_commit_short"], "391b9648")
        self.assertEqual(payload["git_status_short"], "")
        self.assertTrue(payload["summary"]["all_pass"])
        self.assertTrue(payload["summary"]["all_claim_boundaries_clean"])
        self.assertEqual(payload["summary"]["row_count"], 4)
        self.assertGreater(payload["summary"]["geomean_prepare_to_single_query_ratio"], 400.0)

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"hausdorff_xhd", "librts_spatial_index", "rtnn", "triangle_counting"})
        self.assertGreater(rows["rtnn"]["metrics"]["prepare_to_single_query_ratio"], 10000.0)
        self.assertGreater(rows["triangle_counting"]["metrics"]["prepare_to_single_query_ratio"], 2000.0)
        self.assertGreater(rows["hausdorff_xhd"]["metrics"]["prepare_to_single_query_ratio"], 50.0)
        self.assertGreater(rows["librts_spatial_index"]["metrics"]["prepare_to_single_query_ratio"], 10.0)
        for row in rows.values():
            self.assertEqual(row["status"], "pass")
            self.assertEqual(row["claim_flag_violations"], [])
            self.assertFalse(row["claim_boundary"]["release_authorized"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_and_future_todo_record_residency_direction_without_overclaim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        for phrase in (
            "Prepared-Session Amortization",
            "prepare once and issue many queries",
            "12757.870x",
            "2605.920x",
            "not another local per-query micro-optimization",
            "does not authorize release action",
        ):
            self.assertIn(phrase, report)
        for phrase in (
            "Prepared-Session Residency And Amortization",
            "stable cache keys",
            "visible lifetime/invalidation policy",
            "no hidden automatic partner/backend selection",
            "not a true-zero-copy or public speedup claim",
        ):
            self.assertIn(phrase, todo)


if __name__ == "__main__":
    unittest.main()
