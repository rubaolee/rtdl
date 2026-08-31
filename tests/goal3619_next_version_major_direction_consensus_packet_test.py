from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3619_next_version_major_direction_consensus_packet_2026-06-06.md"


class Goal3619NextVersionMajorDirectionConsensusPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_report_is_bounded_and_non_authorizing(self):
        self.assertIn("authorizes nothing", self.report)
        self.assertIn("not public claims", self.report)
        self.assertIn("not complete consensus", self.report)
        self.assertIn("independent Claude and Gemini reviews", self.report)

    def test_direction_is_contract_and_residency_first(self):
        self.assertIn("contract-and-residency first", self.report)
        self.assertIn("Formal Primitive Contracts", self.report)
        self.assertIn("Device-Resident Typed Primitive Outputs", self.report)
        self.assertIn("Benchmark-Driven Runtime Extensions", self.report)
        self.assertIn("Partner Freedom, Not Partner Defaulting", self.report)

    def test_perf_stop_continue_rule_is_explicit(self):
        self.assertIn("Stop/Continue Rule For Performance Work", self.report)
        self.assertIn("fixes a correctness mismatch", self.report)
        self.assertIn("large material end-to-end improvement", self.report)
        self.assertIn("reusable generic primitive/runtime capability", self.report)
        self.assertIn("missing same-contract evidence", self.report)

    def test_segment_pair_contract_is_first_target(self):
        self.assertIn("segment_pair_intersection_count", self.report)
        self.assertIn("segment_pair_left_id_dense_count", self.report)
        self.assertIn("segment_pair_intersection_rows", self.report)
        self.assertIn("collinear-overlap decision", self.report)
        self.assertIn("cross-route conformance", self.report)

    def test_partner_policy_keeps_user_choice(self):
        self.assertIn("The user chooses the partner", self.report)
        self.assertIn("no automatic public default", self.report)
        self.assertIn("Benchmark reference implementations may recommend a partner", self.report)


if __name__ == "__main__":
    unittest.main()
