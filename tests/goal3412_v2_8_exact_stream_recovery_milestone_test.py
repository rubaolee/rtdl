from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3412_v2_8_exact_stream_recovery_milestone_2026-06-04.md"


class Goal3412V28ExactStreamRecoveryMilestoneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_report_summarizes_delivered_chain(self):
        for phrase in (
            "successful streams now report allocated exact-row capacity",
            "overflowed streams fail closed and expose required capacity",
            "callers can explicitly retry with that capacity",
            "recovered exact streams feed generic grouped-count continuation",
            "full `br_county.cdb` evidence exists",
        ):
            self.assertIn(phrase, self.report)

    def test_report_records_full_cdb_and_windowed_evidence(self):
        for phrase in (
            "Single recovered stream | 47262 | 16476 | true",
            "Windowed recovered stream | 47262 | 16476 | true",
            "overflowed windows: 9",
            "retried windows: 9",
            "key-based addition",
            "not concatenation under a disjoint-key assumption",
        ):
            self.assertIn(phrase, self.report)

    def test_report_keeps_future_native_target_and_boundaries(self):
        for phrase in (
            "real paged pair-column stream contract",
            "page ownership/lifetime rules",
            "grouped continuations that consume or merge page summaries",
            "does not implement native paged streams",
            "device-only exact",
            "predicates",
            "automatic retry",
            "true zero-copy",
            "release",
            "authorization",
        ):
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
