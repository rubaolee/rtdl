from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "handoff" / "GOAL3920_SAFE_NEXT_POD_RTDBSCAN_BLOCKED_NUMBA_RUNBOOK_2026-06-08.md"


class Goal3920SafeNextPodRtDbscanBlockedNumbaRunbookTest(unittest.TestCase):
    def test_runbook_has_safe_workspace_and_two_numba_modes(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn('mktemp -d /root/goal3920_rtdbscan.XXXXXX', text)
        self.assertIn('test "$workdir" != "/root"', text)
        self.assertIn("PowerShell double-quoted SSH command", text)
        self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d", text)
        self.assertIn("optix_rt_core_grouped_stream_blocked_numba_column_signature_3d", text)
        self.assertIn("--grouped-union-query-block-size 4096", text)
        self.assertIn("partner: numba", text)
        self.assertIn("Do not promote the blocked Numba route unless it wins timing", text)


if __name__ == "__main__":
    unittest.main()
