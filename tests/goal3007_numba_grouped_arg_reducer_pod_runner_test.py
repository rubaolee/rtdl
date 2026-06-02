from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "goal3007_numba_grouped_arg_reducer_pod_runner.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3007_numba_grouped_arg_reducer_pod_runner_2026-06-01.md"


class Goal3007NumbaGroupedArgReducerPodRunnerTest(unittest.TestCase):
    def test_runner_records_clean_source_and_claim_boundaries(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")

        for phrase in (
            "_numba_cuda_redirector",
            "run_numba_grouped_argmin_f64",
            "grouped_argmax_f64_partner_columns",
            "all_cases_match_cpu_reference",
            "source_commit",
            "source_dirty",
            "uses_legacy_torch_carrier",
            "uses_torch_conversion",
            "release_authorized",
            "numba_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            self.assertIn(phrase, source)

    def test_runner_prints_progress_and_uses_large_stream(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")

        for phrase in (
            "[goal3007] running",
            "[goal3007] wrote",
            "large_stream",
            "tie_fixture",
            "--rows",
            "--groups",
            "1_000_000",
            "4096",
        ):
            self.assertIn(phrase, source)

    def test_report_is_conformance_only(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "conformance infrastructure only",
            "equal-score tie fixture",
            "large generic grouped score-row stream",
            "public `grouped_argmax_f64_partner_columns",
            "_numba_cuda_redirector",
            "does not authorize",
            "v2.6 release",
            "public speedup wording",
            "Numba speedup wording",
            "true-zero-copy wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
