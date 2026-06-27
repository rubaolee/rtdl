from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal516LinuxPublicCommandValidationArtifactTest(unittest.TestCase):
    def test_linux_public_command_artifact_reports_full_backend_pass(self) -> None:
        artifact = REPO_ROOT / "docs" / "reports" / "goal516_linux_tutorial_example_check_2026-04-17.json"
        payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(payload["machine"], "linux-goal516")
        self.assertEqual(payload["system"], "Linux")
        self.assertEqual(payload["summary"], {"passed": 73, "failed": 0, "skipped": 0, "total": 73})
        self.assertEqual(
            payload["backend_status"],
            {
                "cpu_python_reference": True,
                "oracle": True,
                "cpu": True,
                "embree": True,
                "optix": True,
                "vulkan": True,
            },
        )
        self.assertFalse([result for result in payload["results"] if result["status"] != "passed"])


if __name__ == "__main__":
    unittest.main()
