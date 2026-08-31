from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.json"


class Goal3037PointGroupNearestNumbaArgmaxA4000PodTest(unittest.TestCase):
    def _artifact(self) -> dict[str, object]:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_report_records_clean_a4000_composition(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3037",
            "NVIDIA RTX A4000, driver 580.159.03",
            "Source dirty state: `[]`",
            "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns",
            "global_argmax_u32_f64",
            "multi_stage_block_reduce_no_global_atomics",
            "consumer_source_protocols=[\"cupy\", \"cupy\"]",
            "does not authorize",
            "true-zero-copy wording remains blocked",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_clean_source_and_boundaries(self) -> None:
        data = self._artifact()

        self.assertEqual(data["source_commit"], "5aebe6e5a80aa8b6783e98bf66a84ec8a58cd468")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA RTX A4000, 580.159.03")
        self.assertEqual(data["cuda_home"], "/usr/local/cuda-12.8")
        self.assertEqual(data["optix_prefix"], "/root/vendor/optix-sdk")
        self.assertEqual(data["cuda_python_package"], "cuda-python>=12,<13")
        self.assertTrue(data["numba_cuda_use_nvidia_binding"])
        self.assertFalse(data["numba_cuda_minor_version_compatibility"])
        self.assertFalse(data["v2_6_release_authorized"])
        self.assertFalse(data["true_zero_copy_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])

    def test_device_columns_and_numba_argmax_match_raw_rows(self) -> None:
        data = self._artifact()

        self.assertEqual(data["producer_native_symbol"], "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns")
        self.assertEqual(data["producer_native_execution_path"], "prepared_rt_core_point_group_nearest_witness_2d_device_columns")
        self.assertTrue(data["producer_rt_core_accelerated"])
        self.assertFalse(data["producer_materializes_neighbor_rows"])
        self.assertTrue(data["producer_output_columns_true_zero_copy_authorized"])
        self.assertFalse(data["producer_true_zero_copy_authorized"])
        self.assertFalse(data["producer_rt_core_speedup_claim_authorized"])

        self.assertEqual(data["consumer_operation"], "global_argmax_u32_f64")
        self.assertEqual(data["consumer_contract"], "generic_global_argmax_u32_f64")
        self.assertEqual(data["consumer_partner"], "numba")
        self.assertEqual(data["consumer_reduction_strategy"], "multi_stage_block_reduce_no_global_atomics")
        self.assertEqual(data["consumer_neutral_handoff_status"], "accept")
        self.assertEqual(data["consumer_source_protocols"], ["cupy", "cupy"])
        self.assertTrue(data["consumer_direct_device_handoff_authorized"])
        self.assertFalse(data["consumer_true_zero_copy_claim_authorized"])

        for key in (
            "query_ids_match_raw_rows",
            "neighbor_ids_match_raw_rows",
            "distances_match_raw_rows",
            "argmax_item_matches_raw_rows",
            "argmax_row_matches_raw_rows",
            "argmax_score_matches_raw_rows",
            "argmax_neighbor_matches_raw_rows",
        ):
            self.assertTrue(data[key], key)

    def test_roadmap_indexes_clean_composition_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["point_group_nearest_numba_argmax_pod_goal"], "Goal3037")
        self.assertIn("clean_a4000", roadmap["point_group_nearest_numba_argmax_pod_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["true_zero_copy_claim_authorized"])
        self.assertFalse(roadmap["rt_core_speedup_claim_authorized"])
        self.assertEqual(validation["status"], "accept")


if __name__ == "__main__":
    unittest.main()
