from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from scripts.goal1911_v2_readiness_aggregator import REQUIRED_POD_ARTIFACTS
from scripts.goal1911_v2_readiness_aggregator import SUPPORTING_REQUIRED
from scripts.goal1911_v2_readiness_aggregator import aggregate
from scripts.goal1911_v2_readiness_aggregator import main


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1911_v2_readiness_aggregator_2026-05-13.md"


class Goal1911V2ReadinessAggregatorTest(unittest.TestCase):
    def test_current_repo_reports_blocked_on_missing_pod_artifacts(self) -> None:
        payload = aggregate(ROOT)

        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["missing_supporting_files"])
        for artifact in REQUIRED_POD_ARTIFACTS:
            self.assertIn(artifact, payload["missing_pod_artifacts"])
        self.assertIn("RTX pod batch artifacts missing", payload["blockers"])
        self.assertIn("fresh Claude or Pro-class review", " ".join(payload["blockers"]))
        self.assertIn("docs/handoff/GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE_2026-05-13.md", SUPPORTING_REQUIRED)
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["pod_evidence_collected"])

    def test_complete_supporting_and_pod_fixture_still_blocks_on_consensus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in (*SUPPORTING_REQUIRED, *REQUIRED_POD_ARTIFACTS):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")
            payload = aggregate(root)

            self.assertEqual(payload["status"], "blocked")
            self.assertFalse(payload["missing_supporting_files"])
            self.assertFalse(payload["missing_pod_artifacts"])
            self.assertIn("final v2.0 release consensus missing", payload["blockers"])
            self.assertIn("explicit user-requested release action missing", payload["blockers"])

    def test_main_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            rc = main(["--root", str(root), "--output", "out/readiness.json"])
            self.assertEqual(rc, 0)
            payload = json.loads((root / "out/readiness.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["goal"], "Goal1911")
            self.assertEqual(payload["status"], "blocked")

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: active-local-gate", text)
        self.assertIn("machine-readable readiness aggregator", text)
        self.assertIn("expected status is `blocked`", text)
        self.assertIn("does not replace Goal1903 pod", text)
        self.assertIn("user-requested release action", text)


if __name__ == "__main__":
    unittest.main()
