from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5322_brats2020_access_conversion_provenance.json"
)


class Goal5322BraTS2020AccessConversionProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["provenance_search_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["pod_execution_claimed"])

    def test_author_log_scope_is_recorded(self) -> None:
        logs = self.payload["author_log_evidence"]
        self.assertEqual(logs["category"], "BraTS2020_ValidationData")
        self.assertEqual(logs["unique_pair_count"], 500)
        self.assertEqual(logs["record_count"], 2500)
        self.assertEqual(logs["point_count_min"], 887_826)
        self.assertEqual(logs["point_count_max"], 1_964_247)
        self.assertEqual(logs["sections"]["rt_gpu"]["unique_pair_count"], 500)
        self.assertEqual(logs["sections"]["auto_tune"]["record_count"], 1000)

    def test_representative_author_pair_paths_are_not_available(self) -> None:
        pair = self.payload["author_log_evidence"]["representative_pair_from_goal5214"]
        self.assertEqual(
            pair["file_name"],
            "BraTS20_Validation_001_flair.nii_BraTS20_Validation_033_flair.nii.json",
        )
        self.assertEqual(pair["hd_result"], 26.645824432373047)
        self.assertEqual(pair["input_point_counts"], [1_589_257, 1_145_851])
        self.assertTrue(all(path.endswith(".nii") for path in pair["input_paths"]))
        self.assertEqual(
            pair["exact_statuses"],
            [
                "author_log_path_known__input_file_not_available",
                "author_log_path_known__input_file_not_available",
            ],
        )

    def test_official_access_and_conversion_blockers_are_explicit(self) -> None:
        sources = self.payload["official_braTS2020_sources_checked"]
        self.assertIn("cbica_data_page", sources)
        self.assertIn("cbica_registration_page", sources)
        registration_facts = "\n".join(sources["cbica_registration_page"]["facts_used"])
        self.assertIn("CBICA Image Processing Portal", registration_facts)
        self.assertIn("Data Request", registration_facts)
        data_facts = "\n".join(sources["cbica_data_page"]["facts_used"])
        self.assertIn("NIfTI", data_facts)
        self.assertIn("T1", data_facts)
        self.assertIn("T2-FLAIR", data_facts)
        conversion = self.payload["conversion_provenance"]
        self.assertFalse(conversion["author_nifti_to_point_pipeline_found"])
        self.assertFalse(conversion["author_converted_point_hashes_found"])
        self.assertFalse(conversion["byte_identical_regeneration_proven"])

    def test_availability_and_exit_label(self) -> None:
        availability = self.payload["availability"]
        self.assertEqual(availability["local_workspace_assets"], "absent")
        self.assertEqual(availability["current_pod_assets"], "absent")
        self.assertFalse(availability["current_pod_hddatasets_root_exists"])
        self.assertEqual(
            self.payload["exit_label"],
            "brats2020_exact_provenance_not_found__access_and_conversion_blocked",
        )
        blockers = "\n".join(self.payload["blocking_gaps"])
        self.assertIn("No authorized BraTS2020 validation NIfTI files", blockers)
        self.assertIn("No deterministic author NIfTI-to-point conversion", blockers)

    def test_no_pod_and_forbidden_claims(self) -> None:
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("BraTS2020 exact paper input recovery", forbidden)
        self.assertIn("Figure-5 reproduction", forbidden)
        self.assertIn("performance ratio", forbidden)
        next_actions = self.payload["recommended_next_actions"]
        self.assertFalse(next_actions[0]["requires_pod"])
        self.assertTrue(next_actions[2]["requires_pod"])


if __name__ == "__main__":
    unittest.main()
