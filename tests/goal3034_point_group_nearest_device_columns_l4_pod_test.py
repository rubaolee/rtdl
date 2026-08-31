from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3034_point_group_nearest_device_columns_l4_pod_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3034_point_group_nearest_device_columns_l4_pod_2026-06-02.json"


class Goal3034PointGroupNearestDeviceColumnsL4PodTest(unittest.TestCase):
    def _artifact(self) -> dict[str, object]:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_report_records_clean_l4_validation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3034",
            "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns",
            "NVIDIA L4, driver 565.57.01",
            "Source dirty state: `[]`",
            "caller-owned CuPy output columns",
            "Query ids match raw rows",
            "does not authorize",
            "true_zero_copy_authorized=false",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_device_column_contract_and_boundaries(self) -> None:
        data = self._artifact()

        self.assertEqual(data["source_commit"], "a4f867d833edea0b30e4a8e7650243bb371eb60e")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertEqual(data["cuda_home"], "/usr/local/cuda-12.6")
        self.assertEqual(data["optix_prefix"], "/root/vendor/optix-sdk")
        self.assertEqual(data["native_symbol"], "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns")
        self.assertEqual(data["native_execution_path"], "prepared_rt_core_point_group_nearest_witness_2d_device_columns")
        self.assertEqual(data["query_count"], 2048)
        self.assertEqual(data["search_count"], 3072)
        self.assertEqual(data["group_count"], 16)
        self.assertTrue(data["rt_core_accelerated"])
        self.assertFalse(data["materializes_neighbor_rows"])
        self.assertFalse(data["true_zero_copy_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["v2_6_release_authorized"])

    def test_device_columns_match_existing_raw_row_contract(self) -> None:
        data = self._artifact()

        self.assertTrue(data["query_ids_match_raw_rows"])
        self.assertTrue(data["neighbor_ids_match_raw_rows"])
        self.assertTrue(data["distances_match_raw_rows"])

        metadata = data["metadata"]
        self.assertEqual(metadata["source_protocols"], ["cupy"])
        self.assertEqual(metadata["source_devices"], ["cuda:0"])
        self.assertFalse(metadata["materializes_neighbor_rows"])
        self.assertTrue(metadata["output_columns_true_zero_copy_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_roadmap_indexes_goal3033_and_goal3034_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["point_group_nearest_device_columns_goal"], "Goal3033")
        self.assertEqual(roadmap["point_group_nearest_device_columns_pod_goal"], "Goal3034")
        self.assertIn("device_columns", roadmap["point_group_nearest_device_columns_status"])
        self.assertIn("not_speedup_evidence", roadmap["point_group_nearest_device_columns_pod_status"])
        self.assertFalse(roadmap["rt_core_speedup_claim_authorized"])
        self.assertFalse(roadmap["true_zero_copy_claim_authorized"])
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
