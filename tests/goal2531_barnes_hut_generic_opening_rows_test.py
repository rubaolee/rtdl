from pathlib import Path
import json
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2531_barnes_hut_generic_opening_rows_2026-05-23.md"
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


class Goal2531BarnesHutGenericOpeningRowsTest(unittest.TestCase):
    def test_generic_opening_rows_match_existing_app_opening_decision(self) -> None:
        bodies = app.make_bodies()
        nodes = app.build_one_level_quadtree(bodies)
        candidate_rows = app._run_node_candidates("cpu_python_reference", bodies, nodes)
        opening = rt.evaluate_aggregate_opening_rows_2d(
            bodies,
            nodes,
            theta=app.THETA,
            candidate_rows=candidate_rows,
        )
        self.assertEqual(opening["metadata"]["contract"], rt.AGGREGATE_OPENING_ROWS_2D_CONTRACT)
        self.assertEqual(opening["summary"]["accepted_aggregate_row_count"], 5)
        self.assertEqual(opening["summary"]["fallback_exact_row_count"], 22)

        accepted_by_source: dict[int, list[int]] = {body.id: [] for body in bodies}
        for row in opening["accepted_aggregate_rows"]:
            accepted_by_source[int(row["source_id"])].append(int(row["aggregate_id"]))
        fallback_by_source: dict[int, list[int]] = {body.id: [] for body in bodies}
        for row in opening["fallback_exact_rows"]:
            fallback_by_source[int(row["source_id"])].append(int(row["target_id"]))

        old_rows = app.approximate_forces_from_candidates(bodies, nodes, candidate_rows, theta=app.THETA)
        for row in old_rows:
            body_id = int(row["body_id"])
            self.assertEqual(accepted_by_source[body_id], row["accepted_node_ids"])
            self.assertEqual(sorted(fallback_by_source[body_id]), row["exact_body_ids"])

    def test_generic_opening_rows_reject_invalid_inputs(self) -> None:
        bodies = app.make_bodies()
        nodes = app.build_one_level_quadtree(bodies)
        with self.assertRaisesRegex(ValueError, "theta must be positive"):
            rt.evaluate_aggregate_opening_rows_2d(bodies, nodes, theta=0)
        with self.assertRaisesRegex(ValueError, "candidate aggregate node id"):
            rt.evaluate_aggregate_opening_rows_2d(
                bodies,
                nodes,
                theta=app.THETA,
                candidate_rows=({"query_id": bodies[0].id, "neighbor_id": 999},),
            )

    def test_benchmark_opening_rows_mode_records_boundary(self) -> None:
        payload = bench.run_benchmark("opening_rows_cpu")
        metadata = payload["benchmark_metadata"]
        self.assertEqual(metadata["contract"], rt.AGGREGATE_OPENING_ROWS_2D_CONTRACT)
        self.assertFalse(metadata["rt_core_accelerated"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertEqual(payload["opening_rows"]["summary"]["accepted_aggregate_row_count"], 5)
        self.assertIn("force-vector accumulation", payload["app_boundary"])

    def test_cli_opening_rows_mode_outputs_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--mode", "opening_rows_cpu"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["benchmark_metadata"]["mode"], "opening_rows_cpu")
        self.assertEqual(payload["opening_rows"]["metadata"]["contract"], rt.AGGREGATE_OPENING_ROWS_2D_CONTRACT)

    def test_docs_record_goal2531_boundary(self) -> None:
        report_text = REPORT.read_text()
        report_normalized = " ".join(report_text.split())
        readme_text = README.read_text()
        for phrase in [
            "generic_aggregate_opening_rows_2d_v1",
            "accepted aggregate-node rows",
            "fallback exact-body rows",
            "not authorize performance wording",
            "native Barnes-Hut ABI",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_normalized)
        self.assertIn("Goal2531 adds the first generic reconstruction", readme_text)
        self.assertIn("opening_rows_cpu", readme_text)


if __name__ == "__main__":
    unittest.main()
