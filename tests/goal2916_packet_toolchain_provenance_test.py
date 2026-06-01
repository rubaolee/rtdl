from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal2855_v2_5_current_canonical_harness_packet_runner as runner


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2916_packet_toolchain_provenance_metadata_2026-06-01.md"


class Goal2916PacketToolchainProvenanceTest(unittest.TestCase):
    def test_toolchain_metadata_has_release_bounded_keys(self) -> None:
        metadata = runner._toolchain_metadata()

        self.assertEqual(
            "rtdl.goal2916.toolchain_provenance.v1",
            metadata["metadata_version"],
        )
        for key in (
            "python_version",
            "cuda_home",
            "optix_prefix",
            "optix_header_exists",
            "rtdl_optix_library_exists",
            "rtdl_optix_ptx_arch",
            "rtdl_optix_ptx_compiler",
            "nvcc_probe_path",
            "nvcc_version",
            "cxx_version",
            "triton_version",
            "torch_version",
            "cupy_version",
            "numba_version",
        ):
            self.assertIn(key, metadata)
        self.assertFalse(metadata["claim_boundary"]["compiler_fairness_claim_authorized"])
        self.assertFalse(metadata["claim_boundary"]["multivendor_claim_authorized"])
        self.assertFalse(metadata["claim_boundary"]["v2_5_release_authorized"])

    def test_packet_summary_indexes_toolchain_without_changing_pass_semantics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal2916_test_") as temp_name:
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
        toolchain = summary["runner_metadata"]["toolchain"]
        self.assertEqual("rtdl.goal2916.toolchain_provenance.v1", toolchain["metadata_version"])
        self.assertFalse(toolchain["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_documents_compiler_alignment_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2916",
            "toolchain provenance",
            "compiler flag alignment",
            "not a compiler fairness proof",
            "not a multivendor result",
            "not a v2.5 release authorization",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
