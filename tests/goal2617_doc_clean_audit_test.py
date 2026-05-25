from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC_AUDIT_JSON = ROOT / "docs" / "reports" / "goal2617_doc_audit_current_surface_2026-05-25.json"
POD_SMOKE_JSON = ROOT / "docs" / "reports" / "goal2617_pod_surface_smoke_2026-05-25.json"


class Goal2617DocCleanAuditTest(unittest.TestCase):
    def test_current_public_docs_have_no_stale_versions_or_dead_links(self) -> None:
        payload = json.loads(DOC_AUDIT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v2.3")
        self.assertEqual(payload["counts"]["current_needs_fix"], 0)
        bad_rows = [
            row
            for row in payload["rows"]
            if row["category"] == "current_public"
            and (row["stale_version_hits"] or row["dead_local_links"])
        ]
        self.assertEqual(bad_rows, [])

    def test_historical_and_support_docs_are_classified_not_rewritten(self) -> None:
        payload = json.loads(DOC_AUDIT_JSON.read_text(encoding="utf-8"))
        categories = {row["category"] for row in payload["rows"]}
        self.assertIn("historical_audit", categories)
        self.assertIn("historical_release_package", categories)
        self.assertIn("support_artifact", categories)
        self.assertGreater(payload["counts"]["dead_local_link_files"], 0)

    def test_pod_runnable_surface_smoke_passes_all_current_entrypoints(self) -> None:
        payload = json.loads(POD_SMOKE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v2.3")
        self.assertEqual(payload["total_cases"], 54)
        self.assertEqual(payload["passed"], 54)
        self.assertEqual(payload["failed"], 0)
        self.assertEqual(payload["missing_manifest_entries"], [])
        self.assertTrue(all(row["status"] == "ok" for row in payload["results"]))


if __name__ == "__main__":
    unittest.main()
