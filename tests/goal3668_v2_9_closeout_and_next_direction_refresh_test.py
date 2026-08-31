from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3668_v2_9_closeout_and_next_direction_refresh_2026-06-06.md"
STATUS = ROOT / "docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md"
FUTURE = ROOT / "docs/research/future_version_to_do_list.md"


class Goal3668V29CloseoutAndNextDirectionRefreshTest(unittest.TestCase):
    def test_refresh_records_post_goal3665_rayjoin_pip_reading(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin PIP is no longer accurately summarized as a CuPy-owned route",
            "0.283574ms",
            "0.034225ms/request",
            "0.051139ms/request",
            "47264 != 47262",
            "validated-domain evidence only",
            "No single whole-RayJoin performance claim is authorized",
        ):
            self.assertIn(phrase, text)

    def test_closeout_stop_rule_and_next_targets_are_explicit(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Stop the current v2.9 tuning loop",
            "fixes a correctness mismatch",
            "large material end-to-end gain",
            "reusable generic primitive/runtime capability",
            "segment_pair_*",
            "topology-aware closed-shape membership",
            "typed resident primitive output columns",
            "deterministic grouped reductions / witness contracts",
        ):
            self.assertIn(phrase, text)

    def test_consensus_and_claim_boundaries_remain_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "not final 3-AI roadmap consensus",
            "Gemini: pending fresh review",
            "Claude: still required",
            "public v2.9 speedup claims",
            "RayJoin paper reproduction wording",
            "RTDL-beats-RayJoin wording",
            "true zero-copy wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_status_and_future_notes_are_consistent_with_refresh(self) -> None:
        status = STATUS.read_text(encoding="utf-8")
        future = FUTURE.read_text(encoding="utf-8")

        self.assertIn("Goal3665", status)
        self.assertIn("topology-aware closed-shape", status)
        self.assertIn("47264 != 47262", status)
        self.assertIn("Goals3658, 3660, and 3663", future)
        self.assertIn("Goal3665", future)
        self.assertIn("not as a performance tuning problem", future)


if __name__ == "__main__":
    unittest.main()
