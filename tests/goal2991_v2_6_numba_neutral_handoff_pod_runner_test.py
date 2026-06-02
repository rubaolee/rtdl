from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2991_v2_6_numba_neutral_handoff_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2991_v2_6_numba_neutral_handoff_pod_runner_2026-06-01.md"


class Goal2991V26NumbaNeutralHandoffPodRunnerTest(unittest.TestCase):
    def test_runner_uses_goal2990_neutral_handoff_before_numba_execution(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_v2_6_neutral_partner_handoff", source)
        self.assertIn("validate_v2_6_neutral_partner_handoff", source)
        self.assertIn("partner=\"numba\"", source)
        self.assertIn("run_numba_segmented_count_i64", source)
        self.assertIn("run_numba_segmented_sum_f64", source)
        self.assertIn("counts_match_cpu", source)
        self.assertIn("sums_match_cpu", source)
        self.assertIn("print(\"[goal2991]", source)
        self.assertNotIn("import torch", source)
        self.assertNotIn("torch.", source)

    def test_runner_claim_boundary_blocks_release_and_speedup(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            '"release_authorized": False',
            '"public_speedup_claim_authorized": False',
            '"true_zero_copy_claim_authorized": False',
            '"numba_speedup_claim_authorized": False',
        ):
            self.assertIn(phrase, source)

    def test_report_records_pod_requirement_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2991",
            "pod runner",
            "Goal2990 neutral handoff packet",
            "Numba segmented count/sum",
            "CPU parity",
            "not a release authorization",
            "not a Numba speedup claim",
        ):
            self.assertIn(phrase, text)

    def test_readiness_points_to_goal2991_as_next_pod_action(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertIn("run_goal2991_numba_neutral_handoff_on_cuda_pod", packet["allowed_next_actions"])
        self.assertEqual("accept", packet["core_validations"]["v2_6_roadmap"]["status"])

    def test_runner_smoke_executes_only_when_numba_cuda_is_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available on this host")
        output = ROOT / "docs" / "reports" / "goal2991_v2_6_numba_neutral_handoff_pod" / "local_smoke.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--rows",
                "1024",
                "--groups",
                "32",
                "--output",
                str(output),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertIn("[goal2991] status=pass", completed.stdout)
        self.assertTrue(output.exists())


def _numba_cuda_available() -> bool:
    try:
        from numba import cuda
    except Exception:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:
        return False


if __name__ == "__main__":
    unittest.main()
