import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3241_rayjoin_overlay_rt_failure_isolation_2026-06-03.md"


class Goal3241RayJoinOverlayRtFailureIsolationTest(unittest.TestCase):
    def test_report_records_overlay_rt_failure_isolation_without_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "polyover_exec -mode=rt -check=true",
            "polyover_exec -mode=rt -check=false",
            "polyover_exec -mode=grid -check=false",
            "cudaSetDevice(0)",
            "pre-sized PIP output buffer",
            "cudaErrorInvalidDevice",
            "PIPRT::Query",
            "same-slice build/query",
            "upstream-RayJoin runtime compatibility blocker",
            "No RTDL native code was changed",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
