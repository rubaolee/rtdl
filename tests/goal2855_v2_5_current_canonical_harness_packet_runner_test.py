from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal2855_v2_5_current_canonical_harness_packet_runner as runner


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2855_v2_5_current_canonical_harness_packet_runner_2026-05-31.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2855_current_canonical_harness_runner_pod" / "goal2855_summary.json"
REVIEW = ROOT / "docs" / "reviews" / "goal2856_gemini_review_goal2855_v2_5_canonical_packet_runner_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2856_goal2855_v2_5_canonical_packet_runner_consensus_2026-05-31.md"


class Goal2855V25CurrentCanonicalHarnessPacketRunnerTest(unittest.TestCase):
    def test_packet_plan_names_all_seven_canonical_harnesses(self) -> None:
        output_dir = Path("/tmp/goal2855_out")
        plan = runner.packet_plan(
            python_exe="python3",
            output_dir=output_dir,
            work_dir=Path("/tmp/goal2855_work"),
            raw_output_dir=Path("/tmp/goal2855_raw"),
            fail_fast=True,
        )

        self.assertEqual(7, len(plan))
        self.assertEqual(
            [
                "Goal2797",
                "Goal2798",
                "Goal2799",
                "Goal2800",
                "Goal2801",
                "Goal2802",
                "Goal2803",
            ],
            [item["goal"] for item in plan],
        )
        self.assertEqual(
            {
                "goal2797_triangle_counting.json",
                "goal2798_librts.json",
                "goal2799_spatial_rayjoin.json",
                "goal2800_rtnn.json",
                "goal2801_hausdorff_xhd.json",
                "goal2802_rt_dbscan.json",
                "goal2803_barnes_hut.json",
            },
            {item["artifact_name"] for item in plan},
        )
        self.assertTrue(any("--fail-fast" in item["command"] for item in plan))
        self.assertTrue(any("--raw-output-dir" in item["command"] for item in plan))
        self.assertTrue(all(str(output_dir) in " ".join(item["command"]) for item in plan))

    def test_summarize_packet_fails_closed_on_dirty_artifact_or_claim_violation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal2855_test_") as temp_name:
            output_dir = Path(temp_name)
            for spec in runner.HARNESS_SPECS:
                payload = {
                    "status": "pass",
                    "source_commit": "abc123",
                    "source_dirty": [],
                    "gpu": "NVIDIA RTX A5000, 570.211.01",
                    "claim_boundary": {
                        "public_speedup_claim_authorized": False,
                        "whole_app_speedup_claim_authorized": False,
                        "paper_reproduction_claim_authorized": False,
                        "native_engine_customization": False,
                    },
                }
                if spec.goal == "Goal2801":
                    payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"] = True
                if spec.goal == "Goal2803":
                    payload["source_dirty"] = [" M scripts/goal2803_barnes_hut_v25_consolidated_harness.py"]
                (output_dir / spec.artifact_name).write_text(
                    json.dumps(payload),
                    encoding="utf-8",
                )

            executions = [
                {
                    "goal": spec.goal,
                    "app": spec.app,
                    "artifact_name": spec.artifact_name,
                    "returncode": 0,
                    "timed_out": False,
                    "elapsed_sec": 0.01,
                }
                for spec in runner.HARNESS_SPECS
            ]
            summary = runner.summarize_packet(
                output_dir=output_dir,
                executions=executions,
                elapsed_sec=1.0,
            )

        self.assertEqual("fail", summary["status"])
        self.assertFalse(summary["all_pass"])
        self.assertIn("goal2801_hausdorff_xhd.json", summary["claim_boundary_violations"])
        self.assertIn("goal2803_barnes_hut.json", summary["dirty_artifacts"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])

    def test_summarize_packet_accepts_clean_pass_packet(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal2855_test_") as temp_name:
            output_dir = Path(temp_name)
            for spec in runner.HARNESS_SPECS:
                payload = {
                    "status": "pass",
                    "source_commit": "abc123",
                    "source_dirty": [],
                    "gpu": "NVIDIA RTX A5000, 570.211.01",
                    "claim_boundary": {
                        "public_speedup_claim_authorized": False,
                        "whole_app_speedup_claim_authorized": False,
                        "paper_reproduction_claim_authorized": False,
                        "native_engine_customization": False,
                    },
                }
                (output_dir / spec.artifact_name).write_text(
                    json.dumps(payload),
                    encoding="utf-8",
                )
            executions = [
                {
                    "goal": spec.goal,
                    "app": spec.app,
                    "artifact_name": spec.artifact_name,
                    "returncode": 0,
                    "timed_out": False,
                    "elapsed_sec": 0.01,
                }
                for spec in runner.HARNESS_SPECS
            ]
            summary = runner.summarize_packet(
                output_dir=output_dir,
                executions=executions,
                elapsed_sec=1.0,
            )

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual("abc123", summary["source_commit"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual({}, summary["dirty_artifacts"])

    def test_report_documents_operational_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2855",
            "seven-harness packet runner",
            "not a v2.5 release authorization",
            "--list",
            "source_dirty: []",
            "public speedup",
            "Goal2803",
        ):
            self.assertIn(phrase, text)

    def test_pod_summary_records_clean_successful_packet(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("Goal2855", summary["goal"])
        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual(7, summary["expected_artifact_count"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual([], summary["runner_metadata"]["source_dirty"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])

    def test_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Independent Gemini Review",
            "distinct from Codex authoring",
            "`accept-with-boundary`",
            "operational readiness tracking only",
        ):
            self.assertIn(phrase, review)

        for phrase in (
            "Consensus verdict: **accept-with-boundary**",
            "Codex",
            "Gemini",
            "not final v2.5 release consensus",
            "source_commit: e8b95e9e4cbdc0893747be949d5c7b587e8dbe35",
        ):
            self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
