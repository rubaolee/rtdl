import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md"
CALL_FOR_REVIEW = ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m35_focused_gap_ledger_2026-06-23.md"


class V3PhoenixM35FocusedGapLedgerTest(unittest.TestCase):
    def test_report_preserves_structural_vs_material_boundary(self):
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Status: `m35_focused_gap_ledger_not_release`",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "broad_v3_faster_than_v2_claim_authorized: false",
            "all_app_pod_spend_authorized: false",
            "Structural ready",
            "Material ready",
            "RTDBSCAN component signature",
            "0.997557675600175",
            "runner vs Embree `2.927729x` is control context",
            "RayJoin point-location topology stream",
            "0.973754x",
            "Grouped reduction device-column",
            "3.5985x",
            "73.586x",
            "no generic `run_grouped_vector_sum_2d_prepared_session` helper",
            "Component union / component signature",
            "1.077x",
            "M36: add a generic grouped vector-sum/reduction prepared-session helper",
            "M3.4 recommended AABB runner generalization",
            "The M30-M34 bundle review supersedes that sub-milestone direction",
            "M37: split component-union and component-signature accounting",
            "Non-Authorization",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("all_app_pod_spend_authorized: true", text)
        rtdbscan_rows = [
            line for line in text.splitlines() if line.startswith("| RTDBSCAN component signature |")
        ]
        rayjoin_rows = [
            line for line in text.splitlines() if line.startswith("| RayJoin point-location topology stream |")
        ]
        self.assertTrue(rtdbscan_rows)
        self.assertTrue(rayjoin_rows)
        for line in rtdbscan_rows + rayjoin_rows:
            self.assertNotRegex(line, re.compile(r"material win", re.IGNORECASE))

    def test_call_for_review_keeps_external_review_request_bounded(self):
        text = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "Status: `request_m35_focused_gap_ledger_review_not_release`",
            "accept_m35_gap_ledger_continue_m36",
            "accept_with_amendments",
            "blocked_needs_gap_reclassification",
            "reject_wrong_next_work",
            "explicit non-authorization block",
            "Does this review authorize release",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("release_authorized: true", text)
        self.assertNotIn("v4_work_authorized: true", text)

    def test_referenced_paths_exist(self):
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            paths = sorted(set(re.findall(r"`([^`]+\.(?:md|json|txt|py))`", text)))
            missing = [item for item in paths if not (ROOT / item).exists()]
            self.assertEqual(missing, [], path.name)


if __name__ == "__main__":
    unittest.main()
