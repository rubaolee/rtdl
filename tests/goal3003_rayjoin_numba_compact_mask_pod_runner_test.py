from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "goal3003_rayjoin_numba_compact_mask_pod_runner.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3003_rayjoin_numba_compact_mask_pod_runner_2026-06-01.md"


class Goal3003RayjoinNumbaCompactMaskPodRunnerTest(unittest.TestCase):
    def test_runner_covers_all_rayjoin_workloads_and_boundaries(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            'WORKLOADS = ("pip", "lsi", "overlay_seed")',
            "run_rayjoin_v2_6_numba_compact_mask_preview",
            "partner_mask_indices",
            "import _numba_cuda_redirector",
            "all_workloads_match_cpu",
            "source_commit",
            "source_dirty",
            '"rayjoin_paper_reproduction_claim_authorized": False',
            '"rtdl_beats_rayjoin_claim_authorized": False',
        ):
            self.assertIn(phrase, source)

    def test_report_keeps_pod_runner_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3003",
            "RayJoin-style",
            "pip",
            "lsi",
            "overlay_seed",
            "compact_mask_i64",
            "not a RayJoin paper reproduction",
            "not a performance claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
