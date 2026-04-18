from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal518V08FinalLocalReleaseAuditTest(unittest.TestCase):
    def test_goal518_audit_artifact_is_valid(self) -> None:
        artifact = REPO_ROOT / "docs" / "reports" / "goal518_v0_8_final_local_release_audit_2026-04-17.json"
        payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertTrue(payload["valid"], payload["checks"])
        self.assertTrue(payload["checks"]["forbidden_public_strings"]["valid"])
        self.assertTrue(payload["checks"]["targeted_release_tests"]["valid"])
        self.assertTrue(payload["checks"]["public_command_truth"]["valid"])
        self.assertTrue(payload["checks"]["complete_history_map"]["valid"])
        self.assertTrue(payload["checks"]["py_compile"]["valid"])


if __name__ == "__main__":
    unittest.main()
