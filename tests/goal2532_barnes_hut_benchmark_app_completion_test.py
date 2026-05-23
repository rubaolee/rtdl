from pathlib import Path
import json
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2532_barnes_hut_benchmark_app_completion_2026-05-23.md"
BASELINE_2048 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2532_barnes_hut_multithreaded_cpu_baseline_local_2026-05-23.json"
)
BASELINE_8192 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2532_barnes_hut_multithreaded_cpu_baseline_local_8192_2026-05-23.json"
)
RTDL_TIMING_8192 = (
    REPO_ROOT / "docs" / "reports" / "goal2532_barnes_hut_rtdl_local_timing_8192_2026-05-23.json"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
BASELINE_SCRIPT = REPO_ROOT / "scripts" / "goal2532_barnes_hut_multithreaded_cpu_baseline.py"
BENCH_SCRIPT = (
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


class Goal2532BarnesHutBenchmarkAppCompletionTest(unittest.TestCase):
    def test_bucketized_tree_contract_adopts_portable_paper_layout(self) -> None:
        bodies = app.make_generated_bodies(64)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=8, max_depth=16)
        self.assertEqual(tree["metadata"]["contract"], rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT)
        self.assertTrue(tree["metadata"]["morton_ordered"])
        self.assertTrue(tree["metadata"]["dfs_ordered"])
        self.assertTrue(tree["metadata"]["resume_index_metadata"])
        self.assertFalse(tree["metadata"]["native_engine_app_specific"])
        self.assertEqual(tree["summary"]["source_count"], 64)
        self.assertLessEqual(tree["summary"]["max_leaf_member_count"], 8)

        nodes = tree["nodes"]
        self.assertEqual([node.dfs_index for node in nodes], list(range(len(nodes))))
        for node in nodes:
            if node.resume_index is not None:
                self.assertGreater(node.resume_index, node.dfs_index)
            for child_id in node.child_ids:
                child = next(candidate for candidate in nodes if candidate.id == child_id)
                self.assertGreater(child.dfs_index, node.dfs_index)
                self.assertEqual(child.depth, node.depth + 1)

    def test_hierarchical_frontier_emits_nonduplicated_rows(self) -> None:
        bodies = app.make_generated_bodies(64)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=8, max_depth=16)
        opening = rt.evaluate_aggregate_tree_opening_frontier_2d(bodies, tree["nodes"], theta=app.THETA)
        self.assertEqual(opening["metadata"]["contract"], rt.AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT)
        self.assertTrue(opening["metadata"]["hierarchical_frontier"])
        self.assertEqual(opening["summary"]["source_count"], 64)
        self.assertEqual(opening["summary"]["sources_with_any_output"], 64)
        self.assertGreater(opening["summary"]["accepted_aggregate_row_count"], 0)
        fallback_pairs = [
            (int(row["source_id"]), int(row["target_id"]))
            for row in opening["fallback_exact_rows"]
        ]
        self.assertEqual(len(fallback_pairs), len(set(fallback_pairs)))

    def test_benchmark_modes_expose_completed_local_app_surface(self) -> None:
        tree_payload = bench.run_benchmark("bucketized_tree_cpu", body_count=64, bucket_size=8)
        frontier_payload = bench.run_benchmark(
            "opening_frontier_bucketized_cpu",
            body_count=64,
            bucket_size=8,
        )
        force_payload = bench.run_benchmark("bucketized_force_cpu", body_count=64, bucket_size=8)
        self.assertEqual(
            tree_payload["benchmark_metadata"]["contract"],
            rt.AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT,
        )
        self.assertEqual(
            frontier_payload["benchmark_metadata"]["contract"],
            rt.AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT,
        )
        self.assertIn("python_force_interpretation", force_payload["benchmark_metadata"]["contract"])
        self.assertEqual(force_payload["force_row_count"], 64)
        self.assertIn("Python-level Barnes-Hut force interpretation", force_payload["boundary"])

    def test_cli_bucketized_frontier_mode_outputs_guarded_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(BENCH_SCRIPT),
                "--mode",
                "opening_frontier_bucketized_cpu",
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
        self.assertEqual(payload["benchmark_metadata"]["mode"], "opening_frontier_bucketized_cpu")
        self.assertFalse(payload["benchmark_metadata"]["public_speedup_claim_authorized"])
        self.assertIn("opening_frontier", payload)

    def test_local_baseline_and_timing_artifacts_record_claim_boundaries(self) -> None:
        baseline_text = BASELINE_SCRIPT.read_text()
        self.assertIn("std::thread", baseline_text)
        self.assertIn("std_thread_exact_pairwise_force_2d", baseline_text)

        for path in (BASELINE_2048, BASELINE_8192):
            payload = json.loads(path.read_text())
            self.assertEqual(payload["baseline"], "std_thread_exact_pairwise_force_2d")
            self.assertFalse(payload["metadata"]["authors_code_comparison"])
            self.assertFalse(payload["metadata"]["public_speedup_claim_authorized"])
            self.assertGreaterEqual(len(payload["runs"]), 2)

        timing = json.loads(RTDL_TIMING_8192.read_text())
        modes = {run["mode"] for run in timing["runs"]}
        self.assertEqual(
            modes,
            {"bucketized_tree_cpu", "opening_frontier_bucketized_cpu", "bucketized_force_cpu"},
        )
        self.assertIn("not paper-code comparison", timing["claim_boundary"])

    def test_docs_record_artifact_intake_and_remaining_pod_work(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        for phrase in [
            "2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7",
            "samples/cmdline/s01-rtbarneshut",
            "Bucketized leaves with default bucket size 32",
            "Morton/Z-order sorting",
            "DFS-preorder node layout",
            "Resume-index metadata",
            "OptiX triangle encoding",
            "No public speedup claim",
            "C++ exact all-pairs CPU baseline",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("generic_bucketized_aggregate_tree_2d_v1", readme_text)
        self.assertIn("opening_frontier_bucketized_cpu", readme_text)
        self.assertIn("github.com/vani-nag/OWLRayTracing", readme_text)


if __name__ == "__main__":
    unittest.main()
