from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL4536_V3_COMPLETION_PACKET_2026-06-17.md"


class Goal4537V30CompletionReviewRequestTest(unittest.TestCase):
    def test_review_request_references_completion_evidence(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("Goal4536 V3 Completion Packet", text)
        self.assertIn("goal4534_v3_0_m136_v3_current_app_completion_gate", text)
        self.assertIn("goal4535_v3_0_m137_v3_completion_readiness_audit", text)
        self.assertIn("goal4536_v3_0_m138_v3_internal_completion_packet", text)
        self.assertIn("v3_0_benchmark_implementation_queue.py", text)

    def test_review_request_keeps_claims_blocked(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("No release, public speedup, broad RT-core", text)
        self.assertIn("automatic partner-selection", text)
        self.assertIn("app-specific native-engine claim is authorized", text)
        self.assertIn("request_changes", text)


if __name__ == "__main__":
    unittest.main()
