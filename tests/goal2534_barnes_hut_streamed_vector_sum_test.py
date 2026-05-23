from pathlib import Path
import json
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2534_barnes_hut_streamed_vector_sum_2026-05-23.md"
TIMING = REPO_ROOT / "docs" / "reports" / "goal2534_barnes_hut_streamed_vector_sum_local_2026-05-23.json"
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
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app
from examples.v2_0.research_benchmarks.barnes_hut import rtdl_barnes_hut_benchmark_app as bench


class Goal2534BarnesHutStreamedVectorSumTest(unittest.TestCase):
    def test_streamed_vector_sum_matches_materialized_contribution_sum(self) -> None:
        bodies = app.make_generated_bodies(64)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=8, max_depth=16)
        opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )
        contributions = rt.evaluate_weighted_inverse_square_contribution_rows_2d(
            bodies,
            bodies,
            accepted_aggregate_rows=opening["accepted_aggregate_rows"],
            fallback_exact_rows=opening["fallback_exact_rows"],
            aggregate_nodes=tree["nodes"],
            softening=app.SOFTENING,
        )
        materialized = rt.sum_vector_contribution_rows_2d(
            contributions["contribution_rows"],
            source_ids=[body.id for body in bodies],
        )
        streamed = rt.sum_weighted_inverse_square_contributions_2d(
            bodies,
            bodies,
            accepted_aggregate_rows=opening["accepted_aggregate_rows"],
            fallback_exact_rows=opening["fallback_exact_rows"],
            aggregate_nodes=tree["nodes"],
            softening=app.SOFTENING,
        )
        self.assertEqual(
            streamed["metadata"]["contract"],
            rt.WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT,
        )
        self.assertFalse(streamed["metadata"]["intermediate_contribution_rows_materialized"])
        materialized_by_source = {
            int(row["source_id"]): row for row in materialized["vector_sum_rows"]
        }
        for row in streamed["vector_sum_rows"]:
            other = materialized_by_source[int(row["source_id"])]
            self.assertAlmostEqual(float(row["vector_x"]), float(other["vector_x"]), places=12)
            self.assertAlmostEqual(float(row["vector_y"]), float(other["vector_y"]), places=12)

    def test_streamed_benchmark_mode_outputs_guarded_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "streamed_force_sum_bucketized_cpu",
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
        self.assertEqual(payload["benchmark_metadata"]["mode"], "streamed_force_sum_bucketized_cpu")
        self.assertIn(rt.WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT, payload["benchmark_metadata"]["contract"])
        self.assertEqual(payload["vector_sum_contract"], rt.WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT)
        self.assertFalse(payload["benchmark_metadata"]["public_speedup_claim_authorized"])

    def test_streamed_and_materialized_benchmark_checksums_match(self) -> None:
        materialized = bench.run_benchmark("bucketized_force_cpu", body_count=64, bucket_size=8)
        streamed = bench.run_benchmark("streamed_force_sum_bucketized_cpu", body_count=64, bucket_size=8)
        materialized_x = sum(float(row["force_x"]) for row in materialized["force_rows"])
        materialized_y = sum(float(row["force_y"]) for row in materialized["force_rows"])
        streamed_x = sum(float(row["force_x"]) for row in streamed["force_rows"])
        streamed_y = sum(float(row["force_y"]) for row in streamed["force_rows"])
        self.assertAlmostEqual(materialized_x, streamed_x, places=12)
        self.assertAlmostEqual(materialized_y, streamed_y, places=12)
        self.assertEqual(
            materialized["contribution_summary"]["contribution_row_count"],
            streamed["vector_sum_summary"]["contribution_row_count"],
        )

    def test_docs_and_timing_capture_streaming_result(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        timing = json.loads(TIMING.read_text())
        for phrase in [
            "generic_weighted_inverse_square_vector_sum_2d_v1",
            "streamed_force_sum_bucketized_cpu",
            "checksum delta vs materialized: 0.0",
            "fused frontier-to-vector-sum",
            "Not public speedup wording",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("streamed_force_sum_bucketized_cpu", readme_text)
        streamed_records = [
            record for record in timing["records"] if record["mode"] == "streamed_force_sum_bucketized_cpu"
        ]
        self.assertEqual({record["body_count"] for record in streamed_records}, {2048, 8192})
        for record in streamed_records:
            self.assertEqual(record["checksum_delta_x_vs_materialized"], 0.0)
            self.assertEqual(record["checksum_delta_y_vs_materialized"], 0.0)
            self.assertLess(record["elapsed_ratio_vs_materialized"], 1.0)


if __name__ == "__main__":
    unittest.main()
