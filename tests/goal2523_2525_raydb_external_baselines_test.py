import json
from importlib import util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOAL2523_SCRIPT = ROOT / "scripts/goal2523_postgresql_diagnostic_timing.py"
GOAL2524_SCRIPT = ROOT / "scripts/goal2524_duckdb_quick_baseline.py"
GOAL2525_SCRIPT = ROOT / "scripts/goal2525_gpu_database_candidate_gate.py"
GOAL2523_REPORT = ROOT / "docs/reports/goal2523_postgresql_diagnostic_timing_2026-05-23.md"
GOAL2524_REPORT = ROOT / "docs/reports/goal2524_duckdb_quick_baseline_2026-05-23.md"
GOAL2525_REPORT = ROOT / "docs/reports/goal2525_gpu_database_candidate_gate_2026-05-23.md"
GOAL2523_ARTIFACT = ROOT / "docs/reports/goal2523_postgresql_diagnostic_timing_pod_2026-05-23.json"
GOAL2524_ARTIFACT = ROOT / "docs/reports/goal2524_duckdb_quick_baseline_pod_2026-05-23.json"
GOAL2525_ARTIFACT = ROOT / "docs/reports/goal2525_gpu_database_candidate_gate_pod_2026-05-23.json"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"


def _load_module(path: Path, name: str):
    spec = util.spec_from_file_location(name, path)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal2523To2525RaydbExternalBaselinesTest(unittest.TestCase):
    def test_goal2523_postgresql_pod_timing_artifact_is_bounded_and_successful(self) -> None:
        payload = json.loads(GOAL2523_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "goal2523_postgresql_diagnostic_timing")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["repeats"], 500)
        self.assertTrue(payload["postgres_available"])
        self.assertFalse(payload["performance_claim_authorized"])
        self.assertIn("PostgreSQL 16.14", payload["postgres_version"])
        self.assertGreater(payload["postgres_timing_ms"]["median"], 0)
        self.assertGreater(payload["python_reference_timing_ms"]["median"], 0)
        self.assertGreater(payload["postgres_over_python_median_ratio"], 1.0)
        self.assertIn("diagnostic", payload["claim_boundary"])

    def test_goal2524_duckdb_pod_baseline_matches_reference_and_is_bounded(self) -> None:
        payload = json.loads(GOAL2524_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "goal2524_duckdb_quick_baseline")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["query_contract"], "single_grouped_sql_query_count_sum_min_max_sum_count")
        self.assertTrue(payload["duckdb_available"])
        self.assertEqual(payload["duckdb_version"], "1.5.3")
        self.assertTrue(payload["all_match_cpu_reference"])
        self.assertFalse(payload["performance_claim_authorized"])
        self.assertGreater(payload["duckdb_timing_ms"]["median"], 0)
        self.assertGreater(payload["duckdb_over_python_median_ratio"], 1.0)
        self.assertIn("diagnostic", payload["claim_boundary"])

    def test_goal2525_gpu_database_gate_selects_no_quick_gpu_db(self) -> None:
        payload = json.loads(GOAL2525_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "goal2525_gpu_database_candidate_gate")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("NVIDIA RTX 4000 Ada", payload["gpu_probe"]["stdout"])
        self.assertFalse(payload["gpu_database_timing_available_now"])
        self.assertEqual(payload["recommended_first_gpu_database_candidate"], "rapids_cudf")
        self.assertFalse(payload["python_package_status"]["cudf"]["available"])
        self.assertFalse(payload["python_package_status"]["pylibcudf"]["available"])
        self.assertEqual(
            payload["candidate_decisions"]["rapids_cudf"]["status"],
            "defer_to_dedicated_install_goal",
        )
        self.assertFalse(payload["performance_claim_authorized"])

    def test_scripts_have_blocked_paths_for_missing_optional_baselines(self) -> None:
        goal2523 = _load_module(GOAL2523_SCRIPT, "goal2523_postgresql_diagnostic_timing")
        goal2524 = _load_module(GOAL2524_SCRIPT, "goal2524_duckdb_quick_baseline")
        missing_postgres = goal2523.run_timing(repeats=1, psql="/definitely/missing/psql")
        self.assertEqual(missing_postgres["status"], "blocked")
        self.assertIn("psql executable not found", missing_postgres["blocked_reason"])
        duckdb_payload = goal2524.run_baseline(repeats=1)
        self.assertIn(duckdb_payload["status"], {"ok", "blocked"})
        self.assertFalse(duckdb_payload["performance_claim_authorized"])

    def test_reports_and_readme_record_pod_and_no_public_claim_boundary(self) -> None:
        for path in (GOAL2523_REPORT, GOAL2524_REPORT, GOAL2525_REPORT):
            text = path.read_text(encoding="utf-8")
            self.assertIn("ssh root@213.173.108.13 -p 15902", text)
            self.assertIn("does not authorize", text)
            self.assertIn("public speedup", text)
        readme = README.read_text(encoding="utf-8")
        self.assertIn("Goal2523", readme)
        self.assertIn("Goal2524", readme)
        self.assertIn("Goal2525", readme)
        self.assertIn("RAPIDS/cuDF", readme)


if __name__ == "__main__":
    unittest.main()
