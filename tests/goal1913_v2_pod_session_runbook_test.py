from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1913_v2_pod_session_runbook.sh"
REPORT = ROOT / "docs" / "reports" / "goal1913_v2_pod_session_runbook_2026-05-13.md"


class Goal1913V2PodSessionRunbookTest(unittest.TestCase):
    def test_runbook_sequences_current_v2_pod_steps(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal1908_v2_local_preflight.py", text)
        self.assertIn("goal1903_v2_partner_pod_batch_runner.sh", text)
        self.assertIn("goal1905_v2_partner_pod_batch_acceptance.py", text)
        self.assertIn("goal1916_v2_post_pod_artifact_manifest.py", text)
        self.assertIn("goal1911_v2_readiness_aggregator.py", text)
        self.assertIn("GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE", text)

    def test_runbook_prints_progress_and_preserves_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("BEGIN", text)
        self.assertIn("END", text)
        self.assertIn("nvidia-smi", text)
        self.assertIn("OPTIX_PREFIX", text)
        self.assertIn("RUN_BATCH", text)
        self.assertIn("RUN_ACCEPTANCE", text)
        self.assertIn("RUN_MANIFEST", text)

    def test_report_documents_command_progress_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: runbook-ready-waiting-for-pod", text)
        self.assertIn("scripts/goal1913_v2_pod_session_runbook.sh", text)
        self.assertIn("BEGIN ...", text)
        self.assertIn("avoids silent multi-minute", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("final 3-AI release consensus", text)


if __name__ == "__main__":
    unittest.main()
