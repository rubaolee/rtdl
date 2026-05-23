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
    / "goal2539_barnes_hut_same_contract_cpp_baseline_2026-05-23.md"
)
SCRIPT = REPO_ROOT / "scripts" / "goal2539_barnes_hut_same_contract_cpp_baseline.py"
LOCAL_CPP = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2539_barnes_hut_same_contract_cpp_baseline_local_8192_2026-05-23.json"
)
POD_CPP = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2539_barnes_hut_same_contract_cpp_baseline_pod_8192_2026-05-23.json"
)
FUSED_TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2538_barnes_hut_fused_frontier_vector_sum_local_2026-05-23.json"
)
POD_FUSED_TIMING = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2538_barnes_hut_fused_frontier_vector_sum_pod_2026-05-23.json"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"


class Goal2539BarnesHutSameContractCppBaselineTest(unittest.TestCase):
    def test_cpp_baseline_smoke_matches_expected_metadata(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--body-count",
                "64",
                "--thread-counts",
                "1,2",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["baseline"], "std_thread_same_contract_barnes_hut_2d")
        self.assertTrue(payload["metadata"]["same_contract_as_rtdl_fused_reference"])
        self.assertFalse(payload["metadata"]["authors_code_comparison"])
        self.assertFalse(payload["metadata"]["public_speedup_claim_authorized"])
        self.assertEqual({run["threads"] for run in payload["runs"]}, {1, 2})
        self.assertEqual(
            payload["runs"][0]["contribution_row_count"],
            payload["runs"][1]["contribution_row_count"],
        )

    def test_local_and_pod_artifacts_match_fused_contract_counts(self) -> None:
        local_cpp = json.loads(LOCAL_CPP.read_text())
        pod_cpp = json.loads(POD_CPP.read_text())
        local_fused = json.loads(FUSED_TIMING.read_text())
        pod_fused = json.loads(POD_FUSED_TIMING.read_text())
        local_fused_8192 = {
            record["mode"]: record for record in local_fused["records"] if record["body_count"] == 8192
        }["fused_frontier_force_sum_bucketized_cpu"]
        pod_fused_8192 = {
            record["mode"]: record for record in pod_fused["records"] if record["body_count"] == 8192
        }["fused_frontier_force_sum_bucketized_cpu"]

        for label, cpp, fused in (
            ("local", local_cpp, local_fused_8192),
            ("pod", pod_cpp, pod_fused_8192),
        ):
            with self.subTest(label=label):
                first_run = cpp["runs"][0]
                self.assertTrue(cpp["metadata"]["same_contract_as_rtdl_fused_reference"])
                self.assertFalse(cpp["metadata"]["public_speedup_claim_authorized"])
                self.assertEqual(
                    first_run["contribution_row_count"],
                    fused["vector_sum_summary"]["contribution_row_count"],
                )
                self.assertEqual(
                    first_run["aggregate_contribution_row_count"],
                    fused["vector_sum_summary"]["aggregate_contribution_row_count"],
                )
                self.assertEqual(
                    first_run["exact_contribution_row_count"],
                    fused["vector_sum_summary"]["exact_contribution_row_count"],
                )
                self.assertEqual(first_run["visited_node_total"], fused["vector_sum_summary"]["visited_node_total"])
                self.assertAlmostEqual(first_run["checksum_force_x"], fused["checksum_force_x"], places=6)
                self.assertAlmostEqual(first_run["checksum_force_y"], fused["checksum_force_y"], places=6)

    def test_report_and_readme_capture_claim_boundary(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        for phrase in [
            "std_thread_same_contract_barnes_hut_2d",
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
            "not public speedup wording",
            "not authors' code",
            "same-contract multithreaded C++ CPU baseline",
            "native/partner lowering",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal2539_barnes_hut_same_contract_cpp_baseline.py", readme_text)


if __name__ == "__main__":
    unittest.main()
