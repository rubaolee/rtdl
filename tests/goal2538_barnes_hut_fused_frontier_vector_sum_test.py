from pathlib import Path
import json
import os
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2538_barnes_hut_fused_frontier_vector_sum_reference_2026-05-23.md"
)
TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2538_barnes_hut_fused_frontier_vector_sum_local_2026-05-23.json"
)
POD_TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2538_barnes_hut_fused_frontier_vector_sum_pod_2026-05-23.json"
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
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app


class Goal2538BarnesHutFusedFrontierVectorSumTest(unittest.TestCase):
    def test_fused_reference_matches_streamed_row_composition(self) -> None:
        bodies = app.make_generated_bodies(128)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=8)
        opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )
        streamed = rt.sum_weighted_inverse_square_contributions_2d(
            bodies,
            bodies,
            accepted_aggregate_rows=opening["accepted_aggregate_rows"],
            fallback_exact_rows=opening["fallback_exact_rows"],
            aggregate_nodes=tree["nodes"],
            softening=app.SOFTENING,
        )
        fused = rt.sum_aggregate_frontier_weighted_vectors_2d(
            bodies,
            bodies,
            tree["nodes"],
            theta=app.THETA,
            softening=app.SOFTENING,
        )
        self.assertEqual(
            fused["metadata"]["contract"],
            rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
        )
        self.assertFalse(fused["summary"]["materialized_frontier_rows"])
        self.assertFalse(fused["summary"]["materialized_contribution_rows"])
        self.assertEqual(
            streamed["summary"]["contribution_row_count"],
            fused["summary"]["contribution_row_count"],
        )
        streamed_rows = {int(row["source_id"]): row for row in streamed["vector_sum_rows"]}
        for row in fused["vector_sum_rows"]:
            source_id = int(row["source_id"])
            with self.subTest(source_id=source_id):
                self.assertAlmostEqual(float(row["vector_x"]), float(streamed_rows[source_id]["vector_x"]))
                self.assertAlmostEqual(float(row["vector_y"]), float(streamed_rows[source_id]["vector_y"]))
                self.assertEqual(
                    int(row["contribution_count"]),
                    int(streamed_rows[source_id]["contribution_count"]),
                )

    def test_fused_cli_mode_reports_app_agnostic_boundary(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "fused_frontier_force_sum_bucketized_cpu",
                "--body-count",
                "64",
                "--bucket-size",
                "8",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["benchmark_metadata"]["mode"], "fused_frontier_force_sum_bucketized_cpu")
        self.assertIn(
            rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            payload["benchmark_metadata"]["contract"],
        )
        self.assertFalse(payload["benchmark_metadata"]["native_engine_app_specific"])
        self.assertFalse(payload["benchmark_metadata"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["vector_sum_summary"]["materialized_frontier_rows"])
        self.assertFalse(payload["vector_sum_summary"]["materialized_contribution_rows"])
        self.assertIn("checksum_force_x", payload)
        self.assertIn("checksum_force_y", payload)

    def test_invalid_fused_inputs_fail_closed(self) -> None:
        bodies = app.make_generated_bodies(16)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=4)
        with self.assertRaisesRegex(ValueError, "theta"):
            rt.sum_aggregate_frontier_weighted_vectors_2d(
                bodies,
                bodies,
                tree["nodes"],
                theta=0.0,
            )
        with self.assertRaisesRegex(ValueError, "softening"):
            rt.sum_aggregate_frontier_weighted_vectors_2d(
                bodies,
                bodies,
                tree["nodes"],
                theta=app.THETA,
                softening=-1.0,
            )

    def test_docs_and_timing_capture_fused_boundary(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        timing = json.loads(TIMING.read_text())
        for phrase in [
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
            "fused_frontier_force_sum_bucketized_cpu",
            "intermediate_frontier_rows_materialized=false",
            "intermediate_contribution_rows_materialized=false",
            "44 tests OK",
            "not public speedup evidence",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("fused_frontier_force_sum_bucketized_cpu", readme_text)
        records = {(record["body_count"], record["mode"]): record for record in timing["records"]}
        streamed = records[(8192, "streamed_force_sum_bucketized_cpu")]
        fused = records[(8192, "fused_frontier_force_sum_bucketized_cpu")]
        self.assertFalse(fused["vector_sum_summary"]["materialized_frontier_rows"])
        self.assertFalse(fused["vector_sum_summary"]["materialized_contribution_rows"])
        self.assertEqual(
            streamed["vector_sum_summary"]["contribution_row_count"],
            fused["vector_sum_summary"]["contribution_row_count"],
        )
        self.assertAlmostEqual(streamed["checksum_force_x"], fused["checksum_force_x"])
        self.assertAlmostEqual(streamed["checksum_force_y"], fused["checksum_force_y"])
        pod_timing = json.loads(POD_TIMING.read_text())
        self.assertIn("not OptiX timing", pod_timing["claim_boundary"])
        pod_records = {(record["body_count"], record["mode"]): record for record in pod_timing["records"]}
        pod_streamed = pod_records[(8192, "streamed_force_sum_bucketized_cpu")]
        pod_fused = pod_records[(8192, "fused_frontier_force_sum_bucketized_cpu")]
        self.assertFalse(pod_fused["vector_sum_summary"]["materialized_frontier_rows"])
        self.assertFalse(pod_fused["vector_sum_summary"]["materialized_contribution_rows"])
        self.assertAlmostEqual(pod_streamed["checksum_force_x"], pod_fused["checksum_force_x"])
        self.assertAlmostEqual(pod_streamed["checksum_force_y"], pod_fused["checksum_force_y"])


if __name__ == "__main__":
    unittest.main()
