from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4384_v3_0_preflight_3ai_consensus_gate_2026-06-14.md"
CLAUDE = ROOT / "docs/handoff/HANDOFF_CLAUDE_GOAL4384_V3_0_PREFLIGHT_3AI_CONSENSUS_2026-06-14.md"
GEMINI = ROOT / "docs/handoff/HANDOFF_GEMINI_GOAL4384_V3_0_PREFLIGHT_3AI_CONSENSUS_2026-06-14.md"
CONSENSUS = ROOT / "docs/reports/goal4384_v3_0_preflight_3ai_consensus_2026-06-14.md"
V214_INSTRUCTIONS = ROOT / "docs/reports/goal4385_v2_14_closeout_instructions_before_v3_0_2026-06-14.md"


class Goal4384V30PreflightConsensusGateTest(unittest.TestCase):
    def test_gate_blocks_v3_implementation_until_three_ai_consensus(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("V3.0 must not start", text)
        self.assertIn("Codex", text)
        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        self.assertIn("blocked_preflight", text)
        self.assertIn("final consensus document records three acceptable verdicts", text)

    def test_architecture_boundary_rejects_app_specific_native_engines(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("app-agnostic primitives", text)
        self.assertIn("Application semantics stay in Python or explicit partner continuation code", text)
        self.assertIn("No native RayJoin engine", text)
        self.assertIn("No native DBSCAN engine", text)
        self.assertIn("No native Barnes-Hut force-law engine", text)
        self.assertIn("No native contact-manifold physics engine", text)
        self.assertIn("No app-specific public Python API names", text)

    def test_handoff_packets_request_independent_reviews(self) -> None:
        for path, reviewer in ((CLAUDE, "Claude"), (GEMINI, "Gemini")):
            text = path.read_text(encoding="utf-8")
            self.assertIn(reviewer, text)
            self.assertIn("goal4384_v3_0_preflight_3ai_consensus_gate_2026-06-14.md", text)
            self.assertIn("accept-with-boundary", text)
            self.assertIn("needs-more-evidence", text)
            self.assertIn("must not authorize public speedup claims", text)
            self.assertIn("app-specific native engine semantics", text)

    def test_consensus_records_external_accept_with_boundary_and_blocks_implementation(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", text)
        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        self.assertIn("blocked_until_v2_14_closeout", text)
        self.assertIn("does not authorize V3.0 implementation", text)
        self.assertIn("v2.14 closeout is a hard precondition", text)

    def test_v214_closeout_instructions_are_explicit(self) -> None:
        text = V214_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertIn("Do not start V3.0 implementation", text)
        self.assertIn("Run final local gates", text)
        self.assertIn("Run final pod gates", text)
        self.assertIn("RayJoin Overlay", text)
        self.assertIn("AABB broadphase/contact-witness primitive only", text)


if __name__ == "__main__":
    unittest.main()
