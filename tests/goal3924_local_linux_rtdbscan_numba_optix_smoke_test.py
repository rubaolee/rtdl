from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3924_local_linux_rtdbscan_numba_optix_smoke_2026-06-08.md"


class Goal3924LocalLinuxRtdbscanNumbaOptixSmokeTest(unittest.TestCase):
    def test_report_records_local_rebuild_and_both_numba_modes(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev", text)
        self.assertIn("RTDL_OPTIX_LIBRARY=/home/lestat/work/rtdl_codex_local_check/build/librtdl_optix.so", text)
        self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d", text)
        self.assertIn("optix_rt_core_grouped_stream_blocked_numba_column_signature_3d", text)
        self.assertIn("grouped_union_query_block_count = 4", text)

    def test_report_keeps_local_linux_evidence_non_authorizing(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("functional readiness evidence only", text)
        self.assertIn("GTX 1070", text)
        self.assertIn("not release performance evidence", text)
        self.assertIn("does not create release performance evidence", text)
        self.assertIn("does not create release performance evidence", text)
        self.assertIn("Goal3923 combined next-pod queue", text)
        self.assertIn("Goal3920 RTDBSCAN unblocked versus blocked Numba timing", text)


if __name__ == "__main__":
    unittest.main()
