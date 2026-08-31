from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3178_point_group_nearest_witness_typed_producer_metadata_2026-06-03.md"
)


class Goal3178PointGroupNearestWitnessTypedProducerMetadataTest(unittest.TestCase):
    def test_helper_builds_generic_nearest_witness_typed_stream(self) -> None:
        contract = rt.make_v2_8_point_group_nearest_witness_typed_stream_contract(
            4,
            data_ptrs={"query_id": 1000, "neighbor_id": 2000, "distance": 3000},
            device_type="cuda",
            device_id=0,
            source_protocol="cupy_cuda_array_interface",
        )
        metadata = contract.to_metadata()
        validation = rt.validate_typed_result_stream_contract(contract)

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["stream_kind"], "candidate_stream")
        self.assertEqual(metadata["producer_primitive"], "point_group_nearest_witness_2d")
        self.assertEqual(metadata["column_names"], ("query_id", "neighbor_id", "distance"))
        roles = {column["name"]: column["role"] for column in metadata["columns"]}
        self.assertEqual(roles["query_id"], "group_key")
        self.assertEqual(roles["neighbor_id"], "witness")
        self.assertEqual(roles["distance"], "score")
        self.assertEqual(metadata["ordering"], "stable_row_order")
        self.assertEqual(metadata["device_resident_column_count"], 3)
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_producer_metadata_distinguishes_device_columns_from_zero_copy_claims(self) -> None:
        contract = rt.make_v2_8_point_group_nearest_witness_typed_stream_contract(
            2,
            data_ptrs={"query_id": 11, "neighbor_id": 22, "distance": 33},
            device_type="cuda",
            source_protocol="numba_cuda_array_interface",
        )
        metadata = rt.make_v2_8_point_group_nearest_witness_typed_producer_metadata(
            contract,
            backend="optix",
            native_symbol="rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns",
            native_execution_path="prepared_rt_core_point_group_nearest_witness_2d_device_columns",
            query_count=2,
            search_count=8,
            group_count=4,
            radius=1.25,
            transfer_mode="host_query_points_to_device_witness_columns",
            source_protocols=("numba_cuda_array_interface",),
            source_devices=("cuda:0",),
        )

        self.assertEqual(metadata["producer_primitive"], "point_group_nearest_witness_2d")
        self.assertEqual(metadata["producer_output_residency"], "partner_owned_cuda_output_columns")
        self.assertTrue(metadata["device_resident_output_columns_proven"])
        self.assertTrue(metadata["device_resident_output_stream_proven"])
        self.assertFalse(metadata["host_row_materialization_used"])
        self.assertFalse(metadata["end_to_end_true_zero_copy_proven"])
        self.assertFalse(metadata["v2_8_release_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_empty_shortcut_metadata_does_not_claim_device_resident_runtime_proof(self) -> None:
        contract = rt.make_v2_8_point_group_nearest_witness_typed_stream_contract(
            0,
            data_ptrs={"query_id": 11, "neighbor_id": 22, "distance": 33},
        )
        metadata = rt.make_v2_8_point_group_nearest_witness_typed_producer_metadata(
            contract,
            backend="optix",
            native_symbol="rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns",
            native_execution_path="empty_shortcut_no_native_launch",
            query_count=0,
            search_count=8,
            group_count=4,
            radius=1.25,
            transfer_mode="host_query_points_to_device_witness_columns_empty_shortcut",
        )

        self.assertEqual(metadata["producer_output_residency"], "metadata_only_or_empty_output_columns")
        self.assertFalse(metadata["device_resident_output_columns_proven"])
        self.assertFalse(metadata["device_resident_output_stream_proven"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_optix_runtime_attaches_typed_producer_metadata_to_device_column_writer(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        self.assertIn("make_v2_8_point_group_nearest_witness_typed_stream_contract", runtime)
        self.assertIn("make_v2_8_point_group_nearest_witness_typed_producer_metadata", runtime)
        self.assertIn('"typed_result_stream": typed_stream', runtime)
        self.assertIn('"v2_8_typed_producer_metadata": producer_metadata', runtime)
        self.assertIn('"v2_8_release_authorized": False', runtime)

    def test_hausdorff_gap_row_records_metadata_progress_and_remaining_boundary(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        hausdorff = rows["hausdorff_xhd"]

        self.assertIn("nearest-witness stream device-column path now emits reusable typed producer metadata", hausdorff["current_bottleneck"])
        self.assertIn("serious-scale device-resident continuation proof", hausdorff["current_bottleneck"])
        self.assertIn("broader partner conformance", hausdorff["current_bottleneck"])
        self.assertIn("Goal3178", hausdorff["evidence_refs"])
        self.assertFalse(hausdorff["release_authorized"])
        self.assertFalse(hausdorff["true_zero_copy_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "point_group_nearest_witness_2d",
            "partner-owned CUDA output columns",
            "device-resident output columns",
            "does not authorize true-zero-copy",
            "`v2_8_release_authorized: False`",
            "serious-scale device-resident continuation proof",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
