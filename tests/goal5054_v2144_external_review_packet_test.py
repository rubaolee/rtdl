from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "history" / "internal_docs" / "goal5054_v2_14_4_external_review_packet_2026-07-06.md"
CALL = ROOT / "history" / "internal_docs" / "call_for_review_goal5054_v2_14_4_external_review_packet_2026-07-06.md"
PREFLIGHT_SCRIPT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"


class Goal5054V2144ExternalReviewPacketTest(unittest.TestCase):
    def test_packet_indexes_all_open_review_debt(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        for goal in ("Goal5048", "Goal5049", "Goal5050", "Goal5051", "Goal5052", "Goal5053", "Goal5055", "Goal5056", "Goal5057", "Goal5058"):
            self.assertIn(goal, text)
        self.assertIn("completed_external_review_packet_ready__review_debt_not_retired", text)
        self.assertIn("review_debt_retired", text)
        authorized_section = text.split("Not authorized:", 1)[0]
        self.assertNotIn("review_debt_retired", authorized_section)

    def test_call_for_review_preserves_boundaries(self) -> None:
        text = CALL.read_text(encoding="utf-8")
        self.assertIn("approve_goal5054_external_review_packet_ready_but_review_debt_not_retired", text)
        self.assertIn("no v2.14.4 speedup claim", text)
        self.assertIn("no true-zero-copy claim", text)
        self.assertIn("no author parity claim", text)
        self.assertIn("no public `device_group_by` claim", text)

    def test_preflight_review_debt_can_be_retired_by_consolidated_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preflight.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PREFLIGHT_SCRIPT),
                    "--allow-blocked",
                    "--output-json",
                    str(output),
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
        review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
        self.assertEqual("pass", review_check["status"])
        self.assertEqual([], review_check["open"])
        for goal in ("Goal5053", "Goal5055", "Goal5056", "Goal5057", "Goal5058"):
            self.assertIn("review_v2_14_4_all_open_review_debt_2026-07-06.md", review_check["found"][goal])


if __name__ == "__main__":
    unittest.main()
