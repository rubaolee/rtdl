import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1710_windows_toolchain_validation_after_source_recovery_2026-05-11.md"
)


class Goal1710WindowsToolchainValidationAfterSourceRecoveryTest(unittest.TestCase):
    def test_report_records_vcvars_fix_and_graph_validation(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RTDL_VCVARS64", text)
        self.assertIn(
            r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
            text,
        )
        self.assertIn("tests.goal903_embree_graph_ray_traversal_test", text)
        self.assertIn("Ran 8 tests", text)
        self.assertIn("Ran 28 tests", text)
        self.assertIn("OK", text)

    def test_report_does_not_overclaim_pod_or_release_readiness(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not provide pod or hardware execution evidence", text)
        self.assertIn("needs-more-evidence", text)
        self.assertIn("The next blocker is pod/hardware validation", text)


if __name__ == "__main__":
    unittest.main()
