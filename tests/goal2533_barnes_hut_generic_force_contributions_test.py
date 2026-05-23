from pathlib import Path
import json
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2533_barnes_hut_generic_force_contributions_2026-05-23.md"
TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2533_barnes_hut_generic_force_contributions_local_2026-05-23.json"
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
from examples.v2_0.research_benchmarks.barnes_hut import rtdl_barnes_hut_benchmark_app as bench


class Goal2533BarnesHutGenericForceContributionsTest(unittest.TestCase):
    def _small_frontier(self):
        bodies = app.make_generated_bodies(64)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=8, max_depth=16)
        opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )
        return bodies, tree, opening

    def test_generic_contribution_and_vector_sum_contracts(self) -> None:
        bodies, tree, opening = self._small_frontier()
        contributions = rt.evaluate_weighted_inverse_square_contribution_rows_2d(
            bodies,
            bodies,
            accepted_aggregate_rows=opening["accepted_aggregate_rows"],
            fallback_exact_rows=opening["fallback_exact_rows"],
            aggregate_nodes=tree["nodes"],
            softening=app.SOFTENING,
        )
        vector_sums = rt.sum_vector_contribution_rows_2d(
            contributions["contribution_rows"],
            source_ids=[body.id for body in bodies],
        )

        self.assertEqual(
            contributions["metadata"]["contract"],
            rt.WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT,
        )
        self.assertEqual(vector_sums["metadata"]["contract"], rt.GROUPED_VECTOR_SUM_ROWS_2D_CONTRACT)
        self.assertEqual(
            contributions["summary"]["contribution_row_count"],
            opening["summary"]["accepted_aggregate_row_count"]
            + opening["summary"]["fallback_exact_row_count"],
        )
        self.assertEqual(vector_sums["summary"]["source_count"], len(bodies))
        self.assertEqual(vector_sums["summary"]["sources_with_contributions"], len(bodies))

    def test_bucketized_force_uses_generic_contribution_contracts(self) -> None:
        payload = bench.run_benchmark("bucketized_force_cpu", body_count=64, bucket_size=8)
        self.assertEqual(payload["force_row_count"], 64)
        self.assertEqual(
            payload["contribution_contract"],
            rt.WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT,
        )
        self.assertEqual(payload["vector_sum_contract"], rt.GROUPED_VECTOR_SUM_ROWS_2D_CONTRACT)
        self.assertEqual(
            payload["contribution_summary"]["contribution_row_count"],
            payload["vector_sum_summary"]["contribution_row_count"],
        )
        self.assertIn("tree/frontier/contribution/vector-sum", payload["boundary"])

    def test_contribution_mode_cli_outputs_guarded_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "force_contributions_bucketized_cpu",
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
        self.assertEqual(payload["benchmark_metadata"]["mode"], "force_contributions_bucketized_cpu")
        self.assertEqual(
            payload["benchmark_metadata"]["contract"],
            rt.WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT,
        )
        self.assertFalse(payload["benchmark_metadata"]["public_speedup_claim_authorized"])

    def test_contribution_contract_rejects_invalid_inputs(self) -> None:
        bodies, tree, opening = self._small_frontier()
        with self.assertRaisesRegex(ValueError, "softening must be non-negative"):
            rt.evaluate_weighted_inverse_square_contribution_rows_2d(
                bodies,
                bodies,
                accepted_aggregate_rows=opening["accepted_aggregate_rows"],
                fallback_exact_rows=opening["fallback_exact_rows"],
                aggregate_nodes=tree["nodes"],
                softening=-1,
            )
        with self.assertRaisesRegex(ValueError, "fallback target_id"):
            rt.evaluate_weighted_inverse_square_contribution_rows_2d(
                bodies,
                bodies[:1],
                fallback_exact_rows=({"source_id": bodies[0].id, "target_id": bodies[-1].id},),
                softening=app.SOFTENING,
            )

    def test_docs_and_timing_capture_boundary(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        timing = json.loads(TIMING.read_text())
        for phrase in [
            "generic_weighted_inverse_square_contribution_rows_2d_v1",
            "generic_grouped_vector_sum_rows_2d_v1",
            "force_contributions_bucketized_cpu",
            "not public speedup evidence",
            "fuse steps 2-4",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("force_contributions_bucketized_cpu", readme_text)
        self.assertIn("generic_grouped_vector_sum_rows_2d_v1", readme_text)
        self.assertIn("not authors-code timing", timing["claim_boundary"])
        self.assertEqual({record["body_count"] for record in timing["records"]}, {2048, 8192})


if __name__ == "__main__":
    unittest.main()
