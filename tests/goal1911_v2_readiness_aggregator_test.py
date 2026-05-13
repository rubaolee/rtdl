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
    def test_current_repo_reports_post_pod_review_but_still_blocks_release(self) -> None:
        payload = aggregate(ROOT)

        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["missing_supporting_files"])
        self.assertFalse(payload["missing_pod_artifacts"])
        self.assertEqual(payload["goal1905_acceptance_status"], "pass")
        self.assertEqual(payload["goal1916_manifest_status"], "pass")
        self.assertNotIn("RTX pod batch artifacts missing", payload["blockers"])
        self.assertNotIn("fresh Claude or Pro-class review", " ".join(payload["blockers"]))
        self.assertIn(
            "docs/reviews/goal1912_gemini_review_goal1903_post_pod_artifacts_2026-05-13.md",
            payload["post_pod_review_files"],
        )
        self.assertIn(
            "docs/reviews/goal1912_claude_review_goal1903_post_pod_artifacts_2026-05-13.md",
            payload["decisive_post_pod_review_files"],
        )
        self.assertIn("final v2.0 release consensus missing", payload["blockers"])
        self.assertIn("explicit user-requested release action missing", payload["blockers"])
        self.assertIn("docs/handoff/GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE_2026-05-13.md", SUPPORTING_REQUIRED)
        self.assertIn("scripts/goal1913_v2_pod_session_runbook.sh", SUPPORTING_REQUIRED)
        self.assertIn(
            "docs/reviews/goal1935_gemini_review_goal1933_1934_large_scale_perf_2026-05-13.md",
            SUPPORTING_REQUIRED,
        )
        self.assertIn("goal1932_all_app_v2_pod_batch_runner.sh", payload["next_hardware_command"])
        self.assertIn("timeout --preserve-status", payload["next_hardware_command"])
        self.assertIn("goal1913_v2_pod_session_runbook.sh", payload["pod_session_runbook_command"])
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertTrue(payload["claim_boundary"]["pod_evidence_collected"])

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
            self.assertFalse(payload["claim_boundary"]["pod_evidence_collected"])
            self.assertIn("final v2.0 release consensus missing", payload["blockers"])
            self.assertIn("explicit user-requested release action missing", payload["blockers"])

    def test_acceptance_manifest_and_review_clear_their_specific_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for relative in (*SUPPORTING_REQUIRED, *REQUIRED_POD_ARTIFACTS):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")
            for relative in (
                "docs/reports/goal1905_v2_partner_pod_batch_acceptance.json",
                "docs/reports/goal1916_v2_post_pod_artifact_manifest.json",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
            review = root / "docs/reviews/goal1912_gemini_review_goal1903_post_pod_artifacts_2026-05-13.md"
            review.parent.mkdir(parents=True, exist_ok=True)
            review.write_text("Verdict: accept-with-boundary\n", encoding="utf-8")

            payload = aggregate(root)

            self.assertEqual(payload["goal1905_acceptance_status"], "pass")
            self.assertEqual(payload["goal1916_manifest_status"], "pass")
            self.assertTrue(payload["claim_boundary"]["pod_evidence_collected"])
            self.assertNotIn("strict Goal1905 post-pod acceptance not passed on pod artifacts", payload["blockers"])
            self.assertNotIn("Goal1916 post-pod artifact manifest not passed on pod artifacts", payload["blockers"])
            self.assertIn("fresh Claude or Pro-class review of actual pod artifacts missing", payload["blockers"])
            self.assertIn(str(review.relative_to(root)).replace("\\", "/"), payload["post_pod_review_files"])
            self.assertFalse(payload["decisive_post_pod_review_files"])

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
