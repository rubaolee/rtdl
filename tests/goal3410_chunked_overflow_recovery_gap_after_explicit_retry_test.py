from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3410_chunked_overflow_recovery_gap_after_explicit_retry_2026-06-04.md"


class Goal3410ChunkedOverflowRecoveryGapAfterExplicitRetryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_report_distinguishes_explicit_retry_from_chunked_streaming(self):
        self.assertIn("explicit retry path", self.report)
        self.assertIn("it is not chunked streaming recovery", self.report)
        self.assertIn("`required_capacity` itself is too large", self.report)
        self.assertIn("Retrying with `required_capacity` still requires one allocation", self.report)

    def test_report_lists_future_contract_and_first_slice(self):
        for phrase in (
            "Paged exact relation streams",
            "page-token or cursor ABI",
            "Python-level explicit windowed recovery",
            "left-id windows are disjoint",
            "bounded Python orchestration bridge",
            "generic paged pair-column stream",
        ):
            self.assertIn(phrase.lower(), self.report.lower())

    def test_report_keeps_release_boundaries_closed(self):
        for phrase in (
            "does not implement chunked overflow recovery",
            "does not authorize release",
            "public speedup",
            "RT-core speedup",
            "true zero-copy",
            "hidden dispatch",
            "automatic retry",
            "app-specific native-engine behavior",
        ):
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
