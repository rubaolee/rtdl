from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "goal3000_triangle_counting_numba_compact_mask_pod_runner.py"
NUMBA_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal3000_triangle_counting_numba_compact_mask_pod_runner_2026-06-01.md"
)


class Goal3000TriangleCountingNumbaCompactMaskPodRunnerTest(unittest.TestCase):
    def test_runner_invokes_app_wrapper_and_records_cpu_parity(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            "run_triangle_counting_v2_6_numba_compact_mask_preview",
            "partner_mask_indices",
            "candidate_row_ids",
            "valid_triangle_mask",
            "candidates_match_cpu",
            "indices_match_cpu",
            "partner_indices_match_cpu",
            "import _numba_cuda_redirector",
            "source_commit",
            "source_dirty",
            '"triangle_counting_whole_app_speedup_claim_authorized": False',
        ):
            self.assertIn(phrase, source)

    def test_numba_import_helper_activates_target_install_redirector(self) -> None:
        source = NUMBA_CONTINUATION.read_text(encoding="utf-8")
        self.assertIn("_activate_numba_cuda_redirector", source)
        self.assertIn("import _numba_cuda_redirector", source)
        self.assertIn("from numba import cuda", source)

    def test_report_keeps_pod_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3000",
            "pod runner",
            "compact_mask_i64",
            "app-level witness-row compaction proof",
            "does not claim",
            "CUDA pod runtime evidence is still required",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
