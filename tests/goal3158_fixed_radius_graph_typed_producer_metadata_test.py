from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3158_fixed_radius_graph_typed_producer_metadata_2026-06-03.md"


class _FakeData:
    def __init__(self, ptr: int) -> None:
        self.ptr = ptr


class _FakeColumn:
    def __init__(self, ptr: int) -> None:
        self.data = _FakeData(ptr)


class _FakePreparedLower:
    def close(self) -> None:
        pass


class Goal3158FixedRadiusGraphTypedProducerMetadataTest(unittest.TestCase):
    def test_helper_builds_valid_typed_result_stream_contract(self) -> None:
        contract = rt.make_v2_8_fixed_radius_graph_component_typed_stream_contract(
            4,
            data_ptrs={
                "point_ids": 1000,
                "component_labels": 2000,
                "is_core": 3000,
                "neighbor_counts": 4000,
            },
        )
        metadata = contract.to_metadata()
        validation = rt.validate_typed_result_stream_contract(contract)

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["stream_kind"], "adjacency_stream")
        self.assertEqual(metadata["producer_primitive"], "fixed_radius_graph_component_labels_3d")
        self.assertEqual(metadata["ordering"], "stable_row_order")
        self.assertEqual(metadata["column_names"], ("point_ids", "component_labels", "is_core", "neighbor_counts"))
        roles = {column["name"]: column["role"] for column in metadata["columns"]}
        self.assertEqual(roles["point_ids"], "item_id")
        self.assertEqual(roles["component_labels"], "group_key")
        self.assertEqual(roles["is_core"], "mask")
        self.assertEqual(roles["neighbor_counts"], "payload")
        self.assertEqual(metadata["device_resident_column_count"], 4)
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_describe_and_plan_metadata_include_typed_stream(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=4,
            radius=0.11,
            component_threshold=2,
            backend="optix",
            partner="cupy",
            strategy="grouped_stream",
        )

        for metadata in (description["typed_result_stream_contract"], plan["typed_result_stream"]):
            with self.subTest(stream_id=metadata["stream_id"]):
                self.assertEqual(metadata["stream_kind"], "adjacency_stream")
                self.assertEqual(metadata["producer_primitive"], "fixed_radius_graph_component_labels_3d")
                self.assertEqual(
                    metadata["column_names"],
                    ("point_ids", "component_labels", "is_core", "neighbor_counts"),
                )
                self.assertFalse(metadata["automatic_partner_selection_allowed"])
                self.assertFalse(metadata["release_authorized"])

    def test_runtime_metadata_records_typed_stream_and_device_pointers(self) -> None:
        lower = _FakePreparedLower()
        lower_result = {
            "columns": {
                "point_ids": _FakeColumn(1000),
                "component_labels": _FakeColumn(2000),
                "is_core": _FakeColumn(3000),
                "neighbor_counts": _FakeColumn(4000),
            },
            "metadata": {
                "adapter": "PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run",
                "partner_reference_contract": "generic_prepared_optix_cupy_grouped_stream_component_labels_3d",
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
            },
        }

        with mock.patch(
            "rtdsl.v2_8_fixed_radius_graph_component_front_door.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d",
            return_value=lower,
        ):
            prepared = rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
                ((0.0, 0.0, 0.0), (0.1, 0.0, 0.0), (0.2, 0.0, 0.0), (2.0, 0.0, 0.0)),
                radius=0.11,
                component_threshold=2,
            )

        with mock.patch(
            "rtdsl.v2_8_fixed_radius_graph_component_front_door.radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns",
            return_value=lower_result,
        ):
            result = rt.fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=2,
                return_metadata=True,
            )

        stream = result["metadata"]["typed_result_stream"]
        self.assertEqual(stream["stream_kind"], "adjacency_stream")
        self.assertEqual(stream["device_resident_column_count"], 4)
        observed = {column["name"]: column["buffer"]["data_ptr_observed"] for column in stream["columns"]}
        self.assertTrue(observed["point_ids"])
        self.assertTrue(observed["component_labels"])
        self.assertTrue(observed["is_core"])
        self.assertTrue(observed["neighbor_counts"])
        for column in stream["columns"]:
            self.assertTrue(column["device_resident"])
        self.assertFalse(stream["true_zero_copy_claim_authorized"])
        self.assertFalse(result["metadata"]["true_zero_copy_claim_authorized"])

    def test_report_records_metadata_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3158",
            "typed producer metadata",
            "point_ids",
            "component_labels",
            "adjacency_stream",
            "not a true-zero-copy release claim",
            "does not add automatic partner selection",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
