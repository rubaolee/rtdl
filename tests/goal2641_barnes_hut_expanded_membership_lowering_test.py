from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2641_barnes_hut_expanded_membership_lowering_2026-05-27.md"

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

import rtdsl as rt
from examples.v2_0.research_benchmarks.barnes_hut import rtdl_barnes_hut_benchmark_app as bench


class Goal2641BarnesHutExpandedMembershipLoweringTest(unittest.TestCase):
    def test_cpu_lowering_matches_aggregate_frontier_contract(self) -> None:
        payload = bench.run_benchmark(
            "aggregate_frontier_expanded_membership_cpu",
            body_count=128,
            bucket_size=8,
        )

        self.assertEqual(
            payload["benchmark_metadata"]["contract"],
            (
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                f"{rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT}+"
                "python_opening_and_force_interpretation"
            ),
        )
        self.assertTrue(payload["baseline_validation"]["matches_collect_aggregate_frontier_2d"])
        self.assertEqual(
            payload["membership_primitive"]["contract"],
            rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT,
        )
        self.assertEqual(payload["membership_primitive"]["backend"], "cpu")
        self.assertFalse(payload["membership_primitive"]["rt_core_accelerated"])
        self.assertFalse(payload["frontier_collection"]["metadata"]["native_engine_app_specific"])
        self.assertFalse(payload["frontier_collection"]["metadata"]["force_law_embedded_in_engine"])
        self.assertEqual(payload["force_summary"]["force_row_count"], 128)
        self.assertGreater(payload["frontier_collection"]["summary"]["safe_far_accept_count"], 0)
        self.assertGreater(payload["frontier_collection"]["summary"]["exact_opening_test_count"], 0)
        self.assertIn("native engine only sees points, boxes", payload["boundary"])

    def test_modes_are_registered_with_correct_rt_boundary(self) -> None:
        self.assertIn("aggregate_frontier_expanded_membership_cpu", bench.MODES)
        self.assertIn("aggregate_frontier_expanded_membership_embree", bench.MODES)
        self.assertIn("aggregate_frontier_expanded_membership_optix", bench.MODES)

        optix_payload = bench._promotion_metadata(
            mode="aggregate_frontier_expanded_membership_optix",
            contract=(
                f"{rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT}+"
                f"{rt.EXPANDED_AABB_POINT_MEMBERSHIP_2D_CONTRACT}+"
                "python_opening_and_force_interpretation"
            ),
            rt_core_accelerated=True,
        )
        self.assertTrue(optix_payload["rt_core_accelerated"])
        self.assertFalse(optix_payload["native_engine_app_specific"])
        self.assertFalse(optix_payload["public_speedup_claim_authorized"])

    def test_cli_outputs_lowering_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "aggregate_frontier_expanded_membership_cpu",
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
        self.assertEqual(
            payload["benchmark_metadata"]["mode"],
            "aggregate_frontier_expanded_membership_cpu",
        )
        self.assertTrue(payload["baseline_validation"]["matches_collect_aggregate_frontier_2d"])

    def test_docs_record_goal2641_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "aggregate_frontier_expanded_membership_optix",
            "EXPANDED_AABB_POINT_MEMBERSHIP_2D",
            "near-zone candidate rows",
            "force math remains app or partner code",
            "not a whole Barnes-Hut speedup claim",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, readme + report)


if __name__ == "__main__":
    unittest.main()
