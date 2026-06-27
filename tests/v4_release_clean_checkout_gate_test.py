from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import v4_release_clean_checkout_gate as gate


class V4ReleaseCleanCheckoutGateTest(unittest.TestCase):
    def test_release_artifacts_are_present_and_tracked(self) -> None:
        tracking = gate.check_release_artifact_tracking(ROOT)

        self.assertTrue(tracking["passed"], tracking)
        self.assertEqual([], tracking["missing_artifacts"])
        self.assertEqual([], tracking["untracked_artifacts"])
        self.assertGreaterEqual(tracking["artifact_count"], 20)

    def test_ignored_log_artifacts_are_still_tracked(self) -> None:
        tracking = gate.check_release_artifact_tracking(ROOT)

        self.assertGreaterEqual(len(tracking["ignored_log_artifacts"]), 3)
        self.assertEqual([], tracking["ignored_untracked_log_artifacts"])
        self.assertEqual(
            set(tracking["ignored_log_artifacts"]),
            set(tracking["tracked_ignored_log_artifacts"]),
        )

    def test_gate_script_runs_in_allow_dirty_mode(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/v4_release_clean_checkout_gate.py",
                "--allow-dirty",
                "--non-strict-release",
            ],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn('"status": "passed"', proc.stdout)


if __name__ == "__main__":
    unittest.main()

