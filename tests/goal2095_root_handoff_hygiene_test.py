import subprocess
import unittest
from pathlib import Path


class RootHandoffHygieneTest(unittest.TestCase):
    def test_no_tracked_root_handoff_files(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["git", "ls-files", "HANDOFF_*.md"],
            cwd=repo,
            check=True,
            text=True,
            capture_output=True,
        )
        tracked_root_handoffs = [
            line for line in result.stdout.splitlines() if line.startswith("HANDOFF_")
        ]
        self.assertEqual([], tracked_root_handoffs)


if __name__ == "__main__":
    unittest.main()
