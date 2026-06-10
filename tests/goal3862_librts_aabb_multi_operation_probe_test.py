from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3862_librts_aabb_multi_operation_probe_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3862_librts_aabb_multi_operation_streams_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
OLD_SUMMARY = ROOT / "docs/reports/goal3861_librts_aabb_prepared_probe_a5000/summary.json"
SCALE_SUMMARY = ARTIFACT_DIR / "scale_profile_summary.json"
NATIVE_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
NATIVE_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
NATIVE_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
PY_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
APP = ROOT / "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3862LibRtsAabbMultiOperationProbeTest(unittest.TestCase):
    def test_generic_native_and_python_surfaces_exist(self) -> None:
        symbol = "rtdl_optix_count_prepared_aabb_index_2d_multi_operation_packed_queries"

        self.assertIn(symbol, NATIVE_API.read_text(encoding="utf-8"))
        self.assertIn(symbol, NATIVE_PRELUDE.read_text(encoding="utf-8"))
        self.assertIn("count_prepared_aabb_index_2d_multi_operation_packed_queries_optix", NATIVE_WORKLOADS.read_text(encoding="utf-8"))
        self.assertIn("count_prepared_query_set", PY_RUNTIME.read_text(encoding="utf-8"))

        native_text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in (NATIVE_API, NATIVE_PRELUDE, NATIVE_WORKLOADS)
        )
        self.assertNotIn("librts", native_text)

    def test_app_uses_multi_operation_path_only_for_prepared_all_operation(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('if prepared_queries and operation == "all":', app)
        self.assertIn("prepared.count_prepared_query_set", app)
        self.assertIn("multi_operation_native_used", app)

    def test_a5000_artifacts_match_old_counts_and_show_modest_hot_result(self) -> None:
        summary = _load(SUMMARY)
        old_summary = _load(OLD_SUMMARY)
        old_rows = {row["name"]: row for row in old_summary["rows"]}

        self.assertTrue(summary["all_counts_match_goal3861"])
        rows = {row["name"]: row for row in summary["rows"]}
        self.assertEqual(set(rows), {"all_32768_repeat20", "all_65536_repeat10"})

        for name, row in rows.items():
            self.assertEqual(row["stderr_tail"], "")
            self.assertTrue(row["multi_operation_native_used"])
            self.assertEqual(row["counts"], old_rows[name]["counts"])
            self.assertGreater(row["query_median_speedup_vs_goal3861"], 0.95)
            self.assertLess(row["query_median_speedup_vs_goal3861"], 1.10)

        self.assertGreater(rows["all_65536_repeat10"]["query_median_speedup_vs_goal3861"], 1.02)

    def test_current_scale_profile_row_passes_on_multi_operation_path(self) -> None:
        summary = _load(SCALE_SUMMARY)

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["json_pass_count"], 1)
        row = summary["rows"][0]
        self.assertEqual(row["app"], "librts_spatial_index")
        self.assertEqual(row["status"], "pass")
        self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

        payload = _load(ROOT / row["stdout_path"])
        self.assertTrue(payload["multi_operation_native_used"])
        self.assertEqual(payload["run_phases"]["query_sec"].keys(), {"multi_operation_packed_queries"})
        self.assertFalse(payload["native_engine_customization"])

    def test_report_is_honest_about_boundary_and_not_major_speedup(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3862",
            "not LibRTS-specific",
            "correct and app-agnostic",
            "measured hot speedup is only modest",
            "not a major performance direction",
            "does not authorize",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
