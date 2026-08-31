from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3618_segment_pair_count_contract_policy_candidate_2026-06-06.md"


class Goal3618SegmentPairCountContractPolicyCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_contract_is_generic_and_bounded(self):
        self.assertIn("segment_pair_intersection_count", self.report)
        self.assertIn("segment_pair_left_id_dense_count", self.report)
        self.assertIn("must not contain RayJoin, CDB, GIS", self.report)
        self.assertIn("not a public API specification", self.report)
        self.assertIn("not a release packet", self.report)

    def test_policy_records_current_predicate_and_unresolved_cases(self):
        self.assertIn("fabs(denom) < 1.0e-7", self.report)
        self.assertIn("dabsf(denom) < 1.0e-7f", self.report)
        self.assertIn("0.0 <= t <= 1.0", self.report)
        self.assertIn("Collinear overlap is not counted", self.report)
        self.assertIn("not automatically identical for every possible geometry", self.report)

    def test_future_work_requires_conformance_before_public_claim(self):
        self.assertIn("near-parallel, endpoint-touching, tiny-segment", self.report)
        self.assertIn("cross-route conformance tests", self.report)
        self.assertIn("do not use either route for public claims", self.report)


if __name__ == "__main__":
    unittest.main()
