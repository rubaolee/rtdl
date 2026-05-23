from pathlib import Path
import json
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2535_barnes_hut_materialization_pressure_2026-05-23.md"
TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2535_barnes_hut_materialization_pressure_local_2026-05-23.json"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
SCRIPT = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

import rtdsl as rt


class Goal2535BarnesHutMaterializationPressureTest(unittest.TestCase):
    def test_pressure_estimator_classifies_small_and_large_cases(self) -> None:
        small = rt.estimate_vector_sum_materialization_pressure_2d(
            accepted_aggregate_row_count=10,
            fallback_exact_row_count=20,
            source_count=5,
            python_warning_bytes=100000,
        )
        large = rt.estimate_vector_sum_materialization_pressure_2d(
            accepted_aggregate_row_count=1000,
            fallback_exact_row_count=1000,
            source_count=10,
            python_contribution_row_bytes=320,
            python_warning_bytes=100000,
        )
        self.assertEqual(
            small["metadata"]["contract"],
            rt.VECTOR_SUM_MATERIALIZATION_PRESSURE_2D_CONTRACT,
        )
        self.assertFalse(small["summary"]["python_materialization_warning"])
        self.assertEqual(small["summary"]["recommended_execution"], "materialized_reference_allowed")
        self.assertTrue(large["summary"]["python_materialization_warning"])
        self.assertEqual(large["summary"]["recommended_execution"], "streamed_or_native_fused")

    def test_pressure_mode_cli_outputs_guarded_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "materialization_pressure_bucketized_cpu",
                "--body-count",
                "64",
                "--bucket-size",
                "8",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["benchmark_metadata"]["mode"], "materialization_pressure_bucketized_cpu")
        self.assertEqual(
            payload["benchmark_metadata"]["contract"],
            rt.VECTOR_SUM_MATERIALIZATION_PRESSURE_2D_CONTRACT,
        )
        self.assertIn("materialization_pressure", payload)
        self.assertFalse(payload["benchmark_metadata"]["public_speedup_claim_authorized"])

    def test_pressure_estimator_rejects_invalid_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "accepted_aggregate_row_count"):
            rt.estimate_vector_sum_materialization_pressure_2d(
                accepted_aggregate_row_count=-1,
                fallback_exact_row_count=0,
                source_count=1,
            )
        with self.assertRaisesRegex(ValueError, "python_contribution_row_bytes"):
            rt.estimate_vector_sum_materialization_pressure_2d(
                accepted_aggregate_row_count=1,
                fallback_exact_row_count=0,
                source_count=1,
                python_contribution_row_bytes=0,
            )

    def test_docs_and_timing_capture_materialization_boundary(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        timing = json.loads(TIMING.read_text())
        for phrase in [
            "generic_vector_sum_materialization_pressure_2d_v1",
            "materialization_pressure_bucketized_cpu",
            "streamed_or_native_fused",
            "row-materialization boundary explicit",
            "Not public speedup wording",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("materialization_pressure_bucketized_cpu", readme_text)
        records_by_size = {record["body_count"]: record for record in timing["records"]}
        self.assertEqual(records_by_size[2048]["materialization_pressure"]["summary"]["recommended_execution"], "materialized_reference_allowed")
        self.assertEqual(records_by_size[8192]["materialization_pressure"]["summary"]["recommended_execution"], "streamed_or_native_fused")
        self.assertIn("not native timing", timing["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
