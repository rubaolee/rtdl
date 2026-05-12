from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"
CLASSIFICATION = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.json"
BASELINE = ROOT / "docs" / "reports" / "goal1668_native_leakage_manifest_baseline_2026-05-10.json"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"


class Goal1672NativeAppLeakageMigrationClassificationTest(unittest.TestCase):
    def _classification(self) -> dict:
        return json.loads(CLASSIFICATION.read_text(encoding="utf-8-sig"))

    def test_classification_matches_goal1668_dirty_baseline(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8-sig"))
        classified = self._classification()
        self.assertEqual(classified["unique_symbol_count"], baseline["unique_symbol_count"])
        self.assertEqual(classified["hit_occurrence_count"], baseline["hit_occurrence_count"])
        self.assertEqual(len(classified["classifications"]), baseline["unique_symbol_count"])
        self.assertIn("not an allowlist", classified["purpose"])

    def test_every_symbol_remains_blocked_until_migrated_or_quarantined(self) -> None:
        classified = self._classification()
        allowed_actions = set(classified["allowed_actions"])
        self.assertEqual(
            allowed_actions,
            {
                "replace_by_generic_packet",
                "rename_or_replace_with_generic_columnar_descriptor",
                "quarantine_legacy_wrapper",
            },
        )
        for entry in classified["classifications"]:
            with self.subTest(symbol=entry["symbol"]):
                self.assertIn(entry["required_action"], allowed_actions)
                self.assertEqual(
                    entry["release_surface_status"],
                    "blocked_until_migrated_or_quarantined",
                )
                self.assertTrue(entry["deletion_or_quarantine_required"])
                self.assertNotEqual(entry["migration_family"], "unknown")
                self.assertIn("generic", entry["generic_replacement"].lower())

    def test_representative_symbols_have_expected_migration_family(self) -> None:
        classified = self._classification()
        by_symbol = {entry["symbol"]: entry for entry in classified["classifications"]}
        expected = {
            "rtdl_optix_prepare_pose_indices_2d": "ray_packet_preparation",
            "rtdl_optix_db_dataset_grouped_sum": "columnar_row_filter_reduce",
            "rtdl_embree_run_directed_hausdorff_2d": "app_level_distance_reduction",
            "rtdl_optix_run_bfs_expand": "frontier_edge_traversal",
            "rtdl_optix_run_knn_rows": "bounded_nearest_candidate_collection",
            "rtdl_oracle_polygon": "legacy_oracle_wrapper",
        }
        for symbol, family in expected.items():
            with self.subTest(symbol=symbol):
                self.assertEqual(by_symbol[symbol]["migration_family"], family)

    def test_report_and_gate_link_the_classification(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        gate_text = GATE.read_text(encoding="utf-8")
        for phrase in (
            "Every listed native symbol remains blocked",
            "`replace_by_generic_packet` | 70",
            "`rename_or_replace_with_generic_columnar_descriptor` | 25",
            "`quarantine_legacy_wrapper` | 1",
            "RTDL native internals are fully app-agnostic.",
            "PyTorch and CuPy partner work must not add partner-specific native backdoors",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal1672_native_app_leakage_migration_classification_2026-05-10.md", gate_text)


if __name__ == "__main__":
    unittest.main()
