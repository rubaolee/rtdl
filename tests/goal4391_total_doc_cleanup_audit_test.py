from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_total_doc_cleanup_audit.py"
REPORT_MD = ROOT / "docs" / "reports" / "goal4391_total_doc_cleanup_audit_2026-06-15.md"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("rtdl_total_doc_cleanup_audit", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal4391TotalDocCleanupAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = load_audit_module()
        cls.payload = cls.audit.build_payload()

    def test_current_facing_docs_have_no_actionable_issues(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(0, summary["current_documents_with_issues"])
        self.assertEqual(0, summary["current_dead_internal_links"])
        self.assertEqual(0, summary["stale_current_version_hits"])
        self.assertEqual(0, summary["draft_or_pending_hits"])

    def test_current_version_entry_points_are_v2_14(self) -> None:
        for rel in [
            "README.md",
            "docs/README.md",
            "docs/versioning.md",
            "docs/learn/current_claim_boundaries.md",
            "docs/release_reports/v2_14/README.md",
        ]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("v2.14", text, rel)
            self.assertNotIn("current v2.13", text.lower(), rel)
            self.assertNotIn("v2.13 is the current", text.lower(), rel)

    def test_v2_13_docs_are_marked_superseded(self) -> None:
        v213_readme = (ROOT / "docs" / "release_reports" / "v2_13" / "README.md").read_text(encoding="utf-8")
        v213_publication = (ROOT / "docs" / "release_reports" / "v2_13" / "publication.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("previous source-tree release", v213_readme)
        self.assertIn("The current", v213_readme)
        self.assertIn("source-tree release is [v2.14]", v213_readme)
        self.assertIn("previous-release evidence", v213_publication)
        self.assertIn("current release is v2.14", v213_publication)

    def test_report_records_per_document_actions(self) -> None:
        report = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Current-facing documents with issues: `0`", report)
        self.assertIn("Current-facing dead internal links: `0`", report)
        self.assertIn("`README.md`", report)
        self.assertIn("fixed: current source-tree surface", report)
        self.assertIn("Historical/evidence policy", report)


if __name__ == "__main__":
    unittest.main()
