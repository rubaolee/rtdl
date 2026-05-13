from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1914_v2_pod_artifact_provenance_hardening_2026-05-13.md"
FIXED_RUNNER = ROOT / "scripts" / "goal1878_fixed_radius_app_adapter_perf.py"
SEGMENT_RUNNER = ROOT / "scripts" / "goal1863_segment_polygon_hitcount_v2_partner_perf.py"
BATCH_RUNNER = ROOT / "scripts" / "goal1903_v2_partner_pod_batch_runner.sh"
ACCEPTOR = ROOT / "scripts" / "goal1905_v2_partner_pod_batch_acceptance.py"


class Goal1914V2PodArtifactProvenanceHardeningTest(unittest.TestCase):
    def test_report_documents_fail_closed_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: local-preflight-pass", text)
        self.assertIn("git_commit", text)
        self.assertIn("source_commit_label", text)
        self.assertIn("RTX GPU provenance", text)
        self.assertIn("does not collect pod timings", text)
        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("Goal1905 passes in strict mode", text)

    def test_fixed_and_segment_artifacts_record_source_provenance(self) -> None:
        fixed = FIXED_RUNNER.read_text(encoding="utf-8")
        segment = SEGMENT_RUNNER.read_text(encoding="utf-8")

        self.assertIn('"git_commit": _git_commit()', fixed)
        self.assertIn('"source_commit_label": os.environ.get("RTDL_SOURCE_COMMIT_LABEL", "")', fixed)
        self.assertIn('"gpu": _gpu_name()', fixed)
        self.assertIn('"source_commit_label": os.environ.get("RTDL_SOURCE_COMMIT_LABEL", "")', segment)

    def test_batch_runner_and_acceptor_reject_bad_provenance(self) -> None:
        batch = BATCH_RUNNER.read_text(encoding="utf-8")
        acceptor = ACCEPTOR.read_text(encoding="utf-8")

        for text in (batch, acceptor):
            with self.subTest(file=text[:20]):
                self.assertIn("expected RTX GPU provenance", text)
                self.assertIn("expected git_commit provenance", text)
        self.assertIn("source label mismatch", batch)
        self.assertIn("source_commit_label mismatch", acceptor)


if __name__ == "__main__":
    unittest.main()
