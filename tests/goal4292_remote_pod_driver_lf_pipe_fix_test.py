from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_remote_pod_validation_driver.py"
REPORT = ROOT / "docs" / "reports" / "goal4292_remote_pod_driver_lf_pipe_fix_2026-06-11.md"


class Goal4292RemotePodDriverLfPipeFixTest(unittest.TestCase):
    def test_execute_path_uses_binary_stdin_and_decodes_stdout(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('process.stdin.write(payload["remote_script"].encode("utf-8"))', source)
        self.assertIn('line.decode("utf-8", errors="replace")', source)
        self.assertIn("bufsize=0", source)
        self.assertNotIn("text=True", source)

    def test_report_records_windows_crlf_failure(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("pipefail", text)
        self.assertIn("CRLF", text)
        self.assertIn("does not run hardware", text)


if __name__ == "__main__":
    unittest.main()
