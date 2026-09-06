from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments.goal5848_strong_baseline import controller


class Goal5848PodRunbookTest(unittest.TestCase):
    def test_direct_recipe_canonicalizes_aliased_cuda_library_directories(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            canonical = temporary_root / "targets" / "x86_64-linux" / "lib"
            canonical.mkdir(parents=True)
            alias = temporary_root / "lib64"
            alias.symlink_to(canonical, target_is_directory=True)
            output = temporary_root / "recipe.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts/goal5802_build_direct_recipe.py"),
                    "--library-directory",
                    str(alias),
                    "--library-directory",
                    str(canonical),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            recipe = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                recipe["argv_template"].count(f"-L{canonical.resolve()}"),
                1,
            )

    def test_single_generation_runbook_is_syntax_valid_and_fail_closed(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts/goal5848_pod_prepare_and_run.sh"
        completed = subprocess.run(
            ["bash", "-n", str(script)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(os.access(script, os.X_OK))
        text = script.read_text(encoding="utf-8")
        self.assertIn("set -euo pipefail", text)
        self.assertIn('export CUDA_CACHE_DISABLE=1', text)
        self.assertIn(
            'export RTDL_OPTIX_DISK_CACHE_POLICY=disabled', text
        )
        self.assertIn("-name 'libnvrtc.so.*'", text)
        self.assertIn("! -path '*/stubs/*'", text)
        self.assertIn("selected NVRTC image is a link-time stub", text)
        self.assertNotIn("-name 'libnvrtc.so*' 2>/dev/null", text)
        self.assertIn('stage "run_single_attempt_eighty_cell_formal_transaction"', text)
        self.assertEqual(
            text.count(
                '"$PYTHON" -m experiments.goal5848_strong_baseline.controller'
            ),
            1,
        )
        self.assertEqual(
            text.count(
                '"$PYTHON" "$REPO_ROOT/scripts/'
                'goal5848_build_transaction_authority.py"'
            ),
            2,
        )
        self.assertIn(
            'cmp -s "$SINGLE_AUTHORITY" "$SINGLE_AUTHORITY_RECOUNT"',
            text,
        )
        self.assertIn("--device-artifact-build-receipt", text)
        self.assertIn("--aot-cache-authority", text)
        self.assertIn("--include-dependency-output", text)
        self.assertIn("source/goal5796_matched/direct_optix.cpp", text)
        self.assertIn("--unlink-signing-private-after-build", text)
        self.assertIn("--require-cold-first", text)
        self.assertIn("retry_count=0", text)
        self.assertIn("discard_count=0", text)
        self.assertNotIn("--allow-dirty", text)
        self.assertNotIn("formal_retry", text.lower())
        self.assertIn("OUTPUT_ROOT must be outside the Git checkout", text)
        for name in controller._FORMAL_SANITIZED_ENVIRONMENT:
            with self.subTest(sanitized_environment=name):
                self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
