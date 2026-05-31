from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2795_v2_5_tier_label_reconciliation_2026-05-31.md"
REVIEW = REPO_ROOT / "docs" / "reviews" / "goal2795_gemini_review_tier_label_reconciliation_2026-05-31.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal2795_v2_5_tier_label_reconciliation_consensus_2026-05-31.md"


class Goal2795V25TierLabelReconciliationTest(unittest.TestCase):
    def test_manifest_reconciles_claude_tier_drift_findings(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        validation = rt.validate_v2_5_tiered_benchmark_manifest()
        rows = {row["app_id"]: row for row in manifest["apps"]}

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(manifest["tier_counts"], {"A": 3, "B": 4, "C": 3})

        librts = rows["librts_spatial_index"]
        self.assertEqual(librts["tier"], "C")
        self.assertEqual(librts["required_partner_operations"], ())
        self.assertIn("no-regression", librts["parity_target"])
        self.assertIn("no_partner_parity", librts["benchmark_track"])

        spatial = rows["spatial_rayjoin"]
        self.assertEqual(spatial["tier"], "A")
        self.assertIn("Tier A count/parity", spatial["parity_target"])
        self.assertIn("deferred Tier B", spatial["parity_target"])
        self.assertIn("deferred Tier B", spatial["next_action"])
        self.assertIn("segmented_count_i64", spatial["required_partner_operations"])

    def test_manifest_rejects_regressed_librts_or_spatial_labels(self) -> None:
        source = Path(rt.__file__).with_name("v2_5_triton_app_migration.py").read_text(encoding="utf-8")

        self.assertIn('app_id="librts_spatial_index"', source)
        self.assertIn('tier="C"', source)
        self.assertIn("RT AABB count no-regression only", source)
        self.assertIn("row/overlay modes are deferred Tier B continuation work", source)

    def test_report_review_and_consensus_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2795", report)
        self.assertIn("librts_spatial_index", report)
        self.assertIn("spatial_rayjoin", report)
        self.assertIn("## verdict", review.lower())
        self.assertIn("accept", review.lower())
        self.assertIn("accept-with-boundary", consensus.lower())
        self.assertIn(str(REVIEW.relative_to(REPO_ROOT)).replace("\\", "/"), consensus)


if __name__ == "__main__":
    unittest.main()
