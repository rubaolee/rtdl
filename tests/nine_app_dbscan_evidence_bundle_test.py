from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "history"
    / "internal_docs"
    / "nine_app_dbscan_formal_20260909"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


class NineAppDbscanEvidenceBundleTest(unittest.TestCase):
    def test_manifest_binds_both_complete_transactions(self):
        manifest = json.loads(
            (EVIDENCE / "MANIFEST.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest["schema"],
            "rtdl.nine_app.dbscan.complete_evidence_manifest.v1",
        )
        self.assertFalse(manifest["paper_claim_authorized"])
        self.assertEqual(
            set(manifest["artifacts"]),
            {
                "adverse_predecessor_complete_bundle",
                "successor_complete_bundle",
            },
        )
        for record in manifest["artifacts"].values():
            path = EVIDENCE / record["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(sha256(path), record["sha256"])

    def test_report_retains_both_verdicts_and_claim_boundary(self):
        report = (EVIDENCE / "REPORT.md").read_text(encoding="utf-8")
        self.assertIn("2.3386578819653017x", report)
        self.assertIn("1.0703272608056769x", report)
        self.assertIn("1.0830616336924297x", report)
        self.assertIn("14.175927359894695x", report)
        self.assertIn("paper_claim_authorized", report)
        self.assertIn("external_review_completed", report)
        self.assertIn("no independent external acceptance", report.lower())


if __name__ == "__main__":
    unittest.main()
