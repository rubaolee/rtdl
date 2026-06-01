from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal2855_v2_5_current_canonical_harness_packet_runner as runner


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2972_comparison_toolchain_scope_guard_2026-06-01.md"


class Goal2972ComparisonToolchainScopeGuardTest(unittest.TestCase):
    def test_toolchain_scope_guard_is_machine_readable_and_bounded(self) -> None:
        metadata = runner._toolchain_metadata()
        scope = metadata["comparison_toolchain_scope"]

        self.assertEqual(
            "rtdl.goal2972.comparison_toolchain_scope.v1",
            scope["scope_version"],
        )
        self.assertTrue(scope["same_source_commit_required"])
        self.assertTrue(scope["same_gpu_required"])
        self.assertTrue(scope["same_packet_runner_required"])
        self.assertIn("native_optix_stack_observed", scope)
        self.assertIn("partner_versions_recorded", scope)
        self.assertIn("observed_stack_complete_for_current_packet", scope)
        self.assertFalse(scope["compiler_flag_alignment_proven"])
        self.assertFalse(scope["cross_compiler_fairness_claim_authorized"])
        self.assertFalse(scope["public_speedup_wording_authorized"])
        self.assertFalse(scope["paper_reproduction_claim_authorized"])
        self.assertFalse(scope["release_authorized"])

    def test_packet_summary_indexes_scope_without_authorizing_claims(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal2972_test_") as temp_name:
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

        scope = summary["runner_metadata"]["toolchain"]["comparison_toolchain_scope"]
        self.assertEqual(
            "rtdl.goal2972.comparison_toolchain_scope.v1",
            scope["scope_version"],
        )
        self.assertFalse(scope["cross_compiler_fairness_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])

    def test_report_documents_scope_not_fairness_proof(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2972",
            "comparison-toolchain scope guard",
            "same source commit, same GPU, same packet runner",
            "not a compiler fairness proof",
            "not a second-architecture or multivendor result",
            "not a v2.5 release authorization",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
