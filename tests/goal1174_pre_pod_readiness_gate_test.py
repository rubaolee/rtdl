from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1174_pre_pod_readiness_gate_2026-04-30.md"


class Goal1174PrePodReadinessGateTest(unittest.TestCase):
    def test_gate_blocks_dirty_source_claim_grade_pod_runs(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("POD EXECUTION IS READY ONLY AFTER SOURCE CLEANLINESS IS RESOLVED", text)
        self.assertIn("do not copy this local tree to a pod for claim-grade work", text)
        self.assertIn("No dirty local rsync/tar copy to pod for claim-grade evidence", text)

    def test_gate_names_allowed_source_modes(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Mode 1: clean pushed git commit.", text)
        self.assertIn("Mode 2: staged source archive.", text)
        self.assertIn("goal1175_rtdl_staged_source_2026-04-30.tar.gz", text)
        self.assertIn("e6978ed37cdab26737df80efbcb1d34411900a66f9ce1c79063620d128bcce37", text)
        self.assertIn("Use Mode 1 if possible", text)


if __name__ == "__main__":
    unittest.main()
