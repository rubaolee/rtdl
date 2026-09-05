from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from experiments.goal5848_strong_baseline import controller


class Goal5848PodRunbookTest(unittest.TestCase):
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
