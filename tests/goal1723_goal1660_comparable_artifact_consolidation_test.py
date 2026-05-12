import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json"


class Goal1723Goal1660ComparableArtifactConsolidationTest(unittest.TestCase):
    def test_consolidation_counts_all_real_comparable_pairs(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["planned_comparable_rows"], 16)
        self.assertEqual(payload["artifact_pairs_present"], 16)
        self.assertEqual(payload["rows_with_clean_parity_or_companion_evidence"], 16)
        self.assertEqual(payload["rows_with_timing_artifact_boundary_notes"], 3)
        self.assertEqual(payload["rows_with_companion_resolutions"], 3)
        self.assertEqual(payload["rows_with_unresolved_boundaries"], 0)
        self.assertFalse(payload["public_claim_authorized"])
        self.assertFalse(payload["release_authorized"])

    def test_timing_boundary_rows_have_companion_resolutions(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        by_app = {row["app"]: row for row in payload["rows"]}
        self.assertIn(
            "diagnostic_chunk_config_not_public_safe",
            by_app["polygon_set_jaccard"]["timing_artifact_boundary_notes"],
        )
        self.assertEqual(
            by_app["polygon_set_jaccard"]["companion_resolution"]["resolution"],
            "public_safe_chunk_companion_passes_parity",
        )
        self.assertIn(
            "skip_validation_true_in_profiler_payload",
            by_app["facility_knn_assignment"]["timing_artifact_boundary_notes"],
        )
        self.assertEqual(
            by_app["facility_knn_assignment"]["companion_resolution"]["resolution"],
            "validation_companion_matches_oracle",
        )
        self.assertIn(
            "validated_false_in_profiler_payload",
            by_app["robot_collision_screening"]["timing_artifact_boundary_notes"],
        )
        self.assertEqual(
            by_app["robot_collision_screening"]["companion_resolution"]["resolution"],
            "pose_flags_validation_companion_matches_oracle",
        )
        for app in ("polygon_set_jaccard", "facility_knn_assignment", "robot_collision_screening"):
            self.assertTrue(by_app[app]["boundary_resolved_by_companion"])
            self.assertTrue(by_app[app]["evidence_pair_ready_without_public_claim"])

    def test_database_semantic_digest_ignores_timing_metadata(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        db_rows = [
            row for row in payload["rows"]
            if row["app"] == "database_analytics"
        ]
        self.assertEqual(len(db_rows), 2)
        for row in db_rows:
            with self.subTest(engine=row["engine"]):
                self.assertTrue(row["semantic_digest_equal_across_versions"])
                self.assertTrue(row["parity_evidence_clean"])

    def test_report_refuses_speedup_claim_language(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", text)
        self.assertIn("does not authorize release, tagging, or public speedup wording", text)
        self.assertIn("Companion resolutions: `3`", text)
        self.assertIn("Unresolved boundaries: `0`", text)


if __name__ == "__main__":
    unittest.main()
