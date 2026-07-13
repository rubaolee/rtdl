import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5319_graphics_exact_provenance_search.json"
)


class Goal5319GraphicsExactProvenanceSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_search_keeps_exact_and_figure_claims_false(self):
        boundary = self.data["claim_boundary"]
        self.assertTrue(boundary["provenance_search_complete"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_complete"])
        self.assertFalse(boundary["figure5_reproduction_complete"])
        self.assertFalse(boundary["full_paper_reproduction_complete"])
        self.assertFalse(boundary["author_vs_rtdl_performance_ratio_authorized"])
        self.assertFalse(boundary["new_author_or_rtdl_performance_run"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])

        decision = self.data["decision"]
        self.assertEqual(
            decision["exit_label"],
            "graphics_exact_provenance_not_found_keep_level_b",
        )
        self.assertTrue(decision["graphics_remains_level_b_same_source"])
        self.assertFalse(decision["graphics_exact_paper_dataset_reproduction_claimed"])

    def test_public_asset_hashes_are_present_but_not_author_hashes(self):
        assets = self.data["public_stanford_assets"]
        self.assertEqual(
            assets["dragon_vrip"]["sha256"],
            "fea87ff48f2aba22fb53e7b67c3ff3f7b8c2a3b3a0653af62c48bba67c6d5744",
        )
        self.assertEqual(
            assets["happy_vrip"]["sha256"],
            "2283371216d748a08376a3c88698e283cc8f18d10ced348d6d133051bcf217ab",
        )
        self.assertEqual(assets["asian_dragon"]["vertices"], 3_609_600)
        self.assertEqual(assets["thai_statuette"]["vertices"], 4_999_996)

        for item in assets.values():
            self.assertEqual(item["status"], "public_same_source_asset_not_author_hash")
            self.assertEqual(item["archive_head"]["status"], 200)
            self.assertIsNotNone(item["archive_head"]["last_modified"])

        findings = self.data["provenance_findings"]
        self.assertFalse(findings["author_graphics_files_found"])
        self.assertFalse(findings["author_graphics_hashes_found"])
        self.assertFalse(findings["byte_identical_regeneration_proven"])
        self.assertFalse(findings["public_stanford_archives_exact_equivalence_proven"])

    def test_scaled_assets_remain_app_owned_not_author_preprocessing_proof(self):
        scaled = self.data["app_owned_scaled_assets"]
        self.assertTrue(scaled["asian_dragon_scaled_1e-3"]["app_owned_conversion"])
        self.assertEqual(scaled["asian_dragon_scaled_1e-3"]["scale"], 0.001)
        self.assertTrue(scaled["thai_statuette_scaled_1e-3"]["app_owned_conversion"])
        self.assertEqual(scaled["thai_statuette_scaled_1e-3"]["scale"], 0.001)
        for item in scaled.values():
            self.assertEqual(
                item["status"],
                "app_owned_scaled_level_b_candidate_not_author_preprocessing_proof",
            )

        findings = self.data["provenance_findings"]
        self.assertFalse(findings["author_scaling_or_preprocessing_proven"])

    def test_pair_status_has_three_matches_and_one_dragon_asian_no_go(self):
        rows = {row["case_id"]: row for row in self.data["pair_status"]}
        self.assertEqual(len(rows), 4)
        matched = [row for row in rows.values() if row["matched_paper_log_value"]]
        self.assertEqual(len(matched), 3)

        self.assertTrue(rows["dragon_happy"]["matched_paper_log_value"])
        self.assertTrue(rows["thai_happy_scaled"]["matched_paper_log_value"])
        self.assertTrue(rows["thai_asian_scaled"]["matched_paper_log_value"])
        self.assertFalse(rows["dragon_asian_scaled"]["matched_paper_log_value"])
        self.assertEqual(
            rows["dragon_asian_scaled"]["status"],
            "author_value_no_go_current_mapping",
        )
        self.assertAlmostEqual(
            rows["dragon_asian_scaled"]["abs_diff_vs_paper_log"],
            8.715689182281494e-05,
        )

    def test_author_log_paths_are_only_paths_and_counts(self):
        log = self.data["author_log_path_evidence"]
        self.assertEqual(
            log["status"], "basenames_and_point_counts_known__author_bytes_hashes_absent"
        )
        self.assertEqual(log["known_point_counts"]["dragon.ply"], 437_645)
        self.assertEqual(log["known_point_counts"]["happy_buddha.ply"], 543_652)
        self.assertEqual(log["known_point_counts"]["asian_dragon.ply"], 3_609_600)
        self.assertEqual(log["known_point_counts"]["thai_statuette.ply"], 4_999_996)
        self.assertFalse(log["author_hashes_found"])
        self.assertFalse(log["author_preprocessing_script_found"])

    def test_strongest_rows_are_level_b_not_exact_or_ratio_claims(self):
        strongest = self.data["strongest_graphics_level_b_rows"]
        self.assertEqual(
            strongest["dragon_happy"]["status"],
            "strongest_current_graphics_level_b_scalar_match_not_exact",
        )
        self.assertFalse(strongest["dragon_happy"]["per_source_witness_exact"])
        self.assertTrue(strongest["dragon_happy"]["global_bound_early_break"])
        self.assertEqual(
            strongest["dragon_asian_scaled"]["status"],
            "author_value_no_go_current_mapping",
        )

        forbidden = "\n".join(self.data["decision"]["forbidden_summaries"])
        self.assertIn("byte-identical", forbidden)
        self.assertIn("All four Figure-5 graphics pairs", forbidden)
        self.assertIn("performance ratio", forbidden)


if __name__ == "__main__":
    unittest.main()
