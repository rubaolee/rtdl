from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.goal5848_render_direct_worker import (
    INCLUDE_DEPENDENCY,
    INCLUDE_DEPENDENCY_SHA256,
    PARENT,
    render,
)


class Goal5848DirectDerivationTest(unittest.TestCase):
    def test_derivation_changes_only_frozen_timing_counts(self):
        parent = PARENT.read_bytes()
        derived, dependency, receipt = render()
        expected = parent.replace(
            b"constexpr int kSteadyWarmups = 8;",
            b"constexpr int kSteadyWarmups = 16;",
        ).replace(
            b"constexpr int kSteadyRepetitions = 64;",
            b"constexpr int kSteadyRepetitions = 128;",
        )
        self.assertEqual(derived, expected)
        self.assertEqual(dependency, INCLUDE_DEPENDENCY.read_bytes())
        self.assertEqual(
            receipt["derived_sha256"], hashlib.sha256(derived).hexdigest()
        )
        self.assertEqual(
            receipt["include_dependency"]["sha256"],
            INCLUDE_DEPENDENCY_SHA256,
        )
        self.assertFalse(receipt["optix_cuda_or_output_logic_changed"])

    def test_parent_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "direct.cpp"
            mutated.write_bytes(PARENT.read_bytes() + b"\n")
            with self.assertRaisesRegex(RuntimeError, "identity"):
                render(mutated)

    def test_include_dependency_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "direct_optix.cpp"
            mutated.write_bytes(INCLUDE_DEPENDENCY.read_bytes() + b"\n")
            with self.assertRaisesRegex(RuntimeError, "dependency identity"):
                render(include_dependency=mutated)

    def test_cli_writes_compile_ready_relative_include_bundle(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "direct"
            source = (
                output_root / "source/goal5802_premeasurement/direct_worker.cpp"
            )
            dependency = (
                output_root / "source/goal5796_matched/direct_optix.cpp"
            )
            source.parent.mkdir(parents=True)
            dependency.parent.mkdir(parents=True)
            receipt = output_root / "derivation_receipt.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts/goal5848_render_direct_worker.py"),
                    "--output",
                    str(source),
                    "--include-dependency-output",
                    str(dependency),
                    "--receipt",
                    str(receipt),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=root,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                (
                    source.parent / "../goal5796_matched/direct_optix.cpp"
                ).resolve(strict=True),
                dependency.resolve(strict=True),
            )
            self.assertEqual(dependency.read_bytes(), INCLUDE_DEPENDENCY.read_bytes())
            value = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(
                value["status"],
                "PASS__PINNED_INCLUDE_BUNDLE_AND_EXACT_TWO_CONSTANT_DERIVATION",
            )


if __name__ == "__main__":
    unittest.main()
