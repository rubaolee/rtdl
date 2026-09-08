from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from rtdsl.v4 import TriangleReductionMode, TriangleReductionProtocol
from scripts import v4_long_workload_build_triangle_rtdlexe as builder


class TriangleRTDLExecutableBuilderTest(unittest.TestCase):
    def test_parser_requires_exact_target_deployment_and_output(self):
        arguments = builder._parser().parse_args([
            "--source-root", "/source",
            "--native", "/native.so",
            "--nvcc", "/nvcc",
            "--optix-include", "/optix/include",
            "--cuda-include", "/cuda/include",
            "--compute-capability", "8.6",
            "--optix-sdk", "8.0.0",
            "--deployment-id", "successor/triangle/a4500",
            "--output-root", "/product",
            "--manifest", "/manifest.json",
        ])
        self.assertEqual(arguments.compute_capability, "8.6")
        self.assertEqual(arguments.deployment_id, "successor/triangle/a4500")

    def test_graph_proof_binds_both_app_sources_and_generic_callback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / builder.APP).parent.mkdir(parents=True)
            (root / builder.BENCHMARK).parent.mkdir(parents=True)
            (root / builder.APP).write_text("app source\n", encoding="ascii")
            (root / builder.BENCHMARK).write_text(
                "benchmark source\n", encoding="ascii")
            protocol = TriangleReductionProtocol(
                TriangleReductionMode.WEIGHTED_HIT_COUNT)
            proof = builder._graph_proof(protocol, root)
            expected = builder._digest({
                "kind": "triangle_counting_paper_mapping_order_independence_v1",
                "callback": proof.callback_ir_sha256,
                "app_source": builder._sha256(root / builder.APP),
                "benchmark_source": builder._sha256(root / builder.BENCHMARK),
                "paper_algorithms": ("RT-1A2", "RT-2A1"),
            })
            self.assertEqual(proof.proof_sha256, expected)
            self.assertEqual(proof.proof_kind, builder.PROOF_KIND)

    def test_manifest_is_create_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            builder._write_create(path, {"status": "PASS"})
            with self.assertRaises(FileExistsError):
                builder._write_create(path, {"status": "PASS"})
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"status": "PASS"},
            )


if __name__ == "__main__":
    unittest.main()
