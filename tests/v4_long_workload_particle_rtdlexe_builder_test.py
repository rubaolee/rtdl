from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from scripts import v4_long_workload_build_particle_rtdlexe as builder


class ParticleRTDLExecutableBuilderTest(unittest.TestCase):
    def test_parser_requires_explicit_target_and_output_identities(self) -> None:
        arguments = builder._parser().parse_args([
            "--source-root", "/source",
            "--data-root", "/data",
            "--native", "/native.so",
            "--nvcc", "/nvcc",
            "--optix-include", "/optix/include",
            "--cuda-include", "/cuda/include",
            "--compute-capability", "8.6",
            "--optix-sdk", "8.0.0",
            "--deployment-id", "successor/particle/a4500",
            "--build-directory", "/build",
            "--artifact-directory", "/artifacts",
            "--manifest", "/manifest.json",
        ])
        self.assertEqual(arguments.compute_capability, "8.6")
        self.assertEqual(arguments.deployment_id, "successor/particle/a4500")

    def test_create_only_manifest_rejects_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            builder._write_create(path, {"value": 1})
            with self.assertRaises(FileExistsError):
                builder._write_create(path, {"value": 1})
            self.assertEqual(path.read_text(encoding="utf-8"), '{\n  "value": 1\n}\n')
            self.assertTrue(os.path.isfile(path))


if __name__ == "__main__":
    unittest.main()
