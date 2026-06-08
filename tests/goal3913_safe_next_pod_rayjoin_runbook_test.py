from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "handoff" / "GOAL3913_SAFE_NEXT_POD_RAYJOIN_RUNBOOK_2026-06-08.md"


class Goal3913SafeNextPodRayJoinRunbookTest(unittest.TestCase):
    def test_runbook_contains_remote_workspace_and_claim_boundary_guards(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn('mktemp -d /root/goal3913_rayjoin.XXXXXX', text)
        self.assertIn('test "$workdir" != "/root"', text)
        self.assertIn("PowerShell double-quoted SSH command", text)
        self.assertIn("--data-dir /root/rtdl/data/rayjoin_public_cdb", text)
        self.assertIn("subprobe_wrapper_phase_timing_sec", text)
        self.assertIn("loaded_case_reuse_enabled: true", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
