from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"


class Goal5471LibrtsFullTargetAvailabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(
            (RESULTS / "librts_goal5471_full_paper_target_availability.json").read_text(
                encoding="utf-8"
            )
        )

    def test_author_provenance_logs_and_dataset_boundary_are_pinned(self):
        self.assertEqual(
            self.payload["provenance"]["ae_commit"],
            "d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b",
        )
        self.assertEqual(self.payload["author_evidence"]["paper_log_count"], 264)
        self.assertTrue(
            self.payload["author_evidence"]["all_paper_figure_targets_have_author_logs"]
        )
        self.assertFalse(self.payload["decision"]["exact_paper_inputs_available"])
        self.assertFalse(self.payload["decision"]["pod_required_next"])
        self.assertEqual(
            {entry["name"]: entry["md5"] for entry in self.payload["dataset_acquisition"]["archives"]},
            {
                "polygons": "d5c2a8053fd0b7359a5b83391f7d0b82",
                "queries": "64b560c3d067262b7ef7d7422c64225a",
                "synthetic": "ebe7dcf4001132d297a8022c110cedeb",
            },
        )

    def test_final_paper_numbers_are_not_mechanically_equal_to_ae_output_numbers(self):
        self.assertFalse(
            self.payload["numbering_warning"]["mechanical_numeric_matching_is_valid"]
        )
        self.assertEqual(
            self.payload["numbering_warning"]["paper_to_ae_output"],
            {
                "6": "fig7.pdf",
                "7": "fig8.pdf",
                "8": "fig9.pdf",
                "9": "fig10.pdf",
                "10": "fig12.pdf",
                "11": "fig11.pdf",
                "12": "fig13.pdf",
            },
        )


class Goal5472LibrtsAuthorLogDenominatorMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(
            (RESULTS / "librts_goal5472_author_paper_log_denominators.json").read_text(
                encoding="utf-8"
            )
        )

    def test_all_264_logs_are_classified_under_paper_figures_6_through_12(self):
        self.assertEqual(self.payload["source"]["record_count"], 264)
        self.assertEqual(
            self.payload["source"]["figure_record_counts"],
            {"6": 60, "7": 40, "8": 88, "9": 6, "10": 28, "11": 30, "12": 12},
        )
        self.assertEqual(
            [entry["paper_figure"] for entry in self.payload["figure_summaries"]],
            list(range(6, 13)),
        )

    def test_denominators_distinguish_query_build_mixed_and_pip_end_to_end(self):
        contracts = {
            entry["paper_figure"]: entry["denominator_contract"]
            for entry in self.payload["figure_summaries"]
        }
        self.assertIn("Loading Time excluded", contracts[6])
        self.assertIn("incoming-query BVH construction included", contracts[8])
        self.assertIn("mixed", contracts[10])
        self.assertIn("Loading Time + Query Time", contracts[12])
        self.assertFalse(self.payload["decision"]["performance_ratio_authorized"])

    def test_ray_multicast_log_indices_are_normalized_to_actual_power_of_two_k(self):
        census = next(
            entry
            for entry in self.payload["ray_multicast_author_targets"]
            if entry["dataset"] == "USACensusBlockGroupBoundaries.wkt.log"
        )
        self.assertEqual(census["predicted_partition_count"], 32)
        self.assertEqual(set(census["k_query_time_ms"]), {str(1 << value) for value in range(10)})
        self.assertAlmostEqual(census["k_query_time_ms"]["1"], 24.26)
        self.assertAlmostEqual(census["k_query_time_ms"]["16"], 3.101)
        self.assertTrue(self.payload["claim_boundary"]["author_logs_are_reference_targets_only"])


class Goal5473LibrtsDatasetAcquisitionDecisionTest(unittest.TestCase):
    def test_current_host_download_is_deferred_without_claiming_sources_are_gone(self):
        payload = json.loads(
            (RESULTS / "librts_goal5473_dataset_acquisition_decision.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["official_sources"]["zenodo_size_bytes"], 23062425365)
        self.assertEqual(
            payload["official_sources"]["zenodo_md5"],
            "89e589f086038f1cd3af9e3ed67da8c8",
        )
        self.assertGreater(payload["current_host"]["estimated_full_download_hours"], 12.0)
        self.assertFalse(payload["current_host"]["meets_paper_hardware_guidance"])
        self.assertFalse(payload["decision"]["download_on_current_host"])
        self.assertTrue(payload["decision"]["pod_required_for_exact_dataset_execution"])
        self.assertFalse(payload["claim_boundary"]["sharepoint_permanently_unavailable_claimed"])
        self.assertFalse(payload["claim_boundary"]["exact_inputs_acquired"])


if __name__ == "__main__":
    unittest.main()
