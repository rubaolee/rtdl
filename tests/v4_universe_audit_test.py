from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from v4_universe_audit import run_audit


class V4UniverseAuditTest(unittest.TestCase):
    def test_public_surface_has_no_internal_or_old_current_leaks(self) -> None:
        result = run_audit()

        self.assertEqual([], result["public_findings"])
        self.assertEqual([], result["tracked_docs_reviews"])
        self.assertEqual([], result["missing_required_public_files"])
        self.assertEqual([], result["missing_required_history_dirs"])

    def test_untracked_workspace_debris_is_classified(self) -> None:
        result = run_audit()

        self.assertEqual(0, result["unknown_untracked_count"])
        self.assertIn(result["status"], {"pass", "pass_with_known_local_debris"})


if __name__ == "__main__":
    unittest.main()
