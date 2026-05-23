import json
from importlib import util
from pathlib import Path
import subprocess
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2522_postgresql_correctness_oracle.py"
REPORT = ROOT / "docs/reports/goal2522_postgresql_correctness_oracle_2026-05-23.md"
ARTIFACT = ROOT / "docs/reports/goal2522_postgresql_correctness_oracle_2026-05-23.json"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"


EXPECTED_ROWS = {
    "count": [
        {"region_id": 0, "count": 2},
        {"region_id": 1, "count": 1},
        {"region_id": 2, "count": 1},
    ],
    "sum": [
        {"region_id": 0, "sum": 190},
        {"region_id": 1, "sum": 200},
        {"region_id": 2, "sum": 80},
    ],
    "min": [
        {"region_id": 0, "min": 90},
        {"region_id": 1, "min": 200},
        {"region_id": 2, "min": 80},
    ],
    "max": [
        {"region_id": 0, "max": 100},
        {"region_id": 1, "max": 200},
        {"region_id": 2, "max": 80},
    ],
    "avg_as_sum_count": [
        {"region_id": 0, "sum": 190, "count": 2},
        {"region_id": 1, "sum": 200, "count": 1},
        {"region_id": 2, "sum": 80, "count": 1},
    ],
}


def _load_runner():
    spec = util.spec_from_file_location("goal2522_postgresql_correctness_oracle", SCRIPT)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal2522PostgresqlCorrectnessOracleTest(unittest.TestCase):
    def test_runner_computes_expected_cpu_contract_rows_without_postgres(self) -> None:
        runner = _load_runner()
        self.assertEqual(runner.expected_rows(), EXPECTED_ROWS)

    def test_sql_contains_exact_fixture_predicate_grouping_and_modes(self) -> None:
        runner = _load_runner()
        sql = runner.build_sql()
        for phrase in (
            "CREATE TEMP TABLE rtdl_goal2522_raydb_style_fixture",
            "(1, 0, 1994, 5, 10, 100)",
            "(8, 0, 1994, 6, 12, 90)",
            "ship_year BETWEEN 1994 AND 1995",
            "discount BETWEEN 4 AND 6",
            "quantity < 25",
            "GROUP BY region_id",
            "avg_as_sum_count",
            "jsonb_build_object",
        ):
            self.assertIn(phrase, sql)

    def test_missing_psql_is_recorded_as_blocked_not_failure(self) -> None:
        runner = _load_runner()
        payload = runner.run_oracle(psql="/definitely/missing/psql")
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("psql executable not found", payload["blocked_reason"])
        self.assertEqual(payload["expected_cpu_reference_rows"], EXPECTED_ROWS)
        self.assertIs(payload["postgres_rows"], None)
        self.assertFalse(payload["performance_claim_authorized"])
        self.assertIn("correctness oracle", payload["claim_boundary"])

    def test_fake_psql_success_path_parses_and_compares_rows(self) -> None:
        runner = _load_runner()
        completed = subprocess.CompletedProcess(
            args=["/fake/psql"],
            returncode=0,
            stdout=json.dumps(EXPECTED_ROWS, sort_keys=True) + "\n",
            stderr="",
        )
        with (
            mock.patch.object(runner.shutil, "which", return_value="/fake/psql"),
            mock.patch.object(runner.subprocess, "run", return_value=completed),
        ):
            payload = runner.run_oracle(psql="psql")

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["postgresql_correctness_oracle_available"])
        self.assertTrue(payload["all_match_cpu_reference"])
        self.assertEqual(payload["postgres_rows"], EXPECTED_ROWS)
        self.assertEqual(
            payload["matches_cpu_reference_by_mode"],
            {mode: True for mode in EXPECTED_ROWS},
        )
        self.assertFalse(payload["performance_claim_authorized"])

    def test_artifact_records_current_local_block_or_success(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "goal2522_postgresql_correctness_oracle")
        self.assertIn(payload["status"], {"blocked", "ok"})
        self.assertEqual(payload["expected_cpu_reference_rows"], EXPECTED_ROWS)
        self.assertFalse(payload["performance_claim_authorized"])
        if payload["status"] == "ok":
            self.assertTrue(payload["postgresql_correctness_oracle_available"])
            self.assertTrue(payload["all_match_cpu_reference"])
            self.assertEqual(payload["postgres_rows"], EXPECTED_ROWS)
        else:
            self.assertFalse(payload["postgresql_correctness_oracle_available"])
            self.assertIn("blocked_reason", payload)

    def test_report_and_readme_keep_claim_boundary_and_next_sequence_clear(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        for text in (report, readme):
            self.assertIn("PostgreSQL correctness-oracle", text)
            self.assertIn("does not authorize", text)
            self.assertIn("performance comparison", text)
        self.assertIn("DuckDB quick baseline", report)
        self.assertIn("GPU database baseline", report)
        self.assertIn("psql executable not found: psql", report)


if __name__ == "__main__":
    unittest.main()
