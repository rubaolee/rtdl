from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_13_credibility_roadmap import (
    markdown_v2_13_credibility_roadmap,
    v2_13_credibility_roadmap,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_13_credibility_roadmap.py"
REPORT_MD = ROOT / "docs" / "reports" / "goal4366_v2_13_credibility_roadmap_2026-06-13.md"
REPORT_JSON = ROOT / "docs" / "reports" / "goal4366_v2_13_credibility_roadmap_2026-06-13.json"


class Goal4366V213CredibilityRoadmapTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = v2_13_credibility_roadmap()

    def test_roadmap_accepts_current_baseline_but_not_new_claims(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        self.assertEqual("accepted_plan_not_release_packet", self.payload["status"])
        self.assertEqual(
            "rtdl.v2_13.credibility_roadmap.goal4366.v1",
            self.payload["version"],
        )
        self.assertEqual(11, self.payload["current_baseline"]["v2_12_summary"]["release_table_row_count"])

    def test_rayjoin_baseline_keeps_lsi_and_pip_truth_visible(self) -> None:
        rayjoin = self.payload["current_baseline"]["rayjoin_same_stream"]
        self.assertGreater(rayjoin["lsi"]["embree_divided_by_optix"], 40.0)
        self.assertGreater(rayjoin["lsi"]["rayjoin_rt_over_rtdl_optix"], 1.0)
        self.assertLess(rayjoin["pip"]["embree_divided_by_optix"], 1.3)
        self.assertGreater(rayjoin["pip"]["rayjoin_rt_faster_than_rtdl_optix"], 10.0)
        self.assertGreater(rayjoin["pip"]["phase_ms"]["exact_refine_median_ms"], 4.0)
        self.assertIn("optimization debt", rayjoin["pip"]["readout"])

    def test_each_release_row_has_reasonability_analysis(self) -> None:
        reviews = self.payload["current_baseline"]["row_review"]
        self.assertEqual(11, len(reviews))
        self.assertTrue(all(row["reasonable"] for row in reviews))
        by_contract = {row["contract"]: row for row in reviews}
        self.assertEqual(
            "reasonable_but_v2_13_optimization_debt",
            by_contract["pip_same_stream_scalar_count"]["classification"],
        )
        self.assertEqual(
            "reasonable_embree_faster_tiny_row",
            by_contract["native_collect_k_bounded_witness_rows"]["classification"],
        )
        self.assertIn(
            "not an RT-core",
            by_contract["prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows"]["analysis"],
        )

    def test_goals_include_public_wording_and_amd_defer_gates(self) -> None:
        goals = {goal["id"]: goal for goal in self.payload["roadmap_goals"]}
        self.assertIn("rayjoin_authors_code_comparison_packet", goals)
        self.assertIn("pip_exact_membership_optimization", goals)
        self.assertIn("embree_cpu_fairness_hardening", goals)
        self.assertIn("human_scale_timing_packet", goals)
        self.assertIn("public_wording_packet", goals)
        self.assertIn("amd_gpu_defer_gate", goals)
        self.assertFalse(self.payload["amd_gpu_decision"]["prepare_amd_gpu_now"])
        self.assertIn("zero unexplained rows", self.payload["amd_gpu_decision"]["recommended_timing"])

    def test_markdown_contains_public_completion_contract(self) -> None:
        markdown = markdown_v2_13_credibility_roadmap(self.payload)
        self.assertIn("RTDL v2.13 Credibility Roadmap", markdown)
        self.assertIn("Row Reasonability Review", markdown)
        self.assertIn("PIP Phase Debt", markdown)
        self.assertIn("A row with an unexplained speedup is a failed row", markdown)
        self.assertIn("Prepare AMD GPU now: `False`", markdown)
        self.assertIn("Validation status: `accept`", markdown)

    def test_script_writes_report_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "roadmap.json"
            out_md = Path(tmp) / "roadmap.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            markdown = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("RTDL v2.13 Credibility Roadmap", markdown)

    def test_committed_report_artifacts_are_current(self) -> None:
        expected = self.payload
        committed = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(expected["version"], committed["version"])
        self.assertEqual("accept", committed["validation"]["status"])

        report = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("RTDL v2.13 Credibility Roadmap", report)
        self.assertIn("RayJoin PIP same stream", report)
        self.assertIn("amd_gpu_defer_gate", report)
        self.assertIn("Validation status: `accept`", report)


if __name__ == "__main__":
    unittest.main()
