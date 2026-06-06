import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DummyPairColumnOwner:
    handle_value = 123


class Goal3675ClosedShapeCandidateRelationStatusColumnsTest(unittest.TestCase):
    def test_native_candidate_kernel_emits_generic_relation_status_column(self) -> None:
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        self.assertIn("point_closed_shape_membership_status", core)
        self.assertIn("return 2u;", core)
        self.assertIn("optixSetPayload_3(relation_status)", core)
        self.assertIn("unsigned long long* relation_status_out;", workloads)
        self.assertIn("unsigned long long* relation_boundary_ordinals_out;", workloads)
        self.assertIn("params.relation_status_out[slot]", workloads)
        self.assertIn("params.relation_boundary_ordinals_out[slot]", workloads)
        self.assertIn("columns_out->relation_status_device_ptr", workloads)
        self.assertIn("columns_out->relation_boundary_ordinals_device_ptr", workloads)
        new_terms = "\n".join(
            line
            for line in (core + "\n" + workloads).splitlines()
            if "relation_status" in line
            or "relation_boundary" in line
            or "point_closed_shape_membership_status" in line
        ).lower()
        self.assertNotIn("rayjoin", new_terms)
        self.assertNotIn("cdb", new_terms)

    def test_ctypes_pair_column_abi_append_and_metadata(self) -> None:
        from rtdsl.optix_runtime import (
            OptixNativeDevicePairColumnOutput,
            _RtdlNativeDevicePairColumns,
        )

        field_names = [name for name, _ in _RtdlNativeDevicePairColumns._fields_]
        self.assertEqual(field_names[-2], "relation_status_device_ptr")
        self.assertEqual(field_names[-3], "right_ordinals_device_ptr")
        self.assertIn("left_ordinals_device_ptr", field_names)
        self.assertIn("right_ordinals_device_ptr", field_names)
        self.assertEqual(field_names[-1], "relation_boundary_ordinals_device_ptr")

        output = OptixNativeDevicePairColumnOutput(
            library=object(),
            owner=DummyPairColumnOwner(),
            left_ids_device_ptr=1000,
            right_ids_device_ptr=2000,
            row_count=3,
            capacity=3,
            candidate_event_count=3,
            overflow=False,
            device_ordinal=0,
            traversal_seconds=0.01,
            native_symbol="rtdl_optix_prepared_point_closed_shape_membership_candidate_device_columns_2d",
            field_names=("point_id", "shape_id"),
            left_ordinals_device_ptr=3000,
            right_ordinals_device_ptr=4000,
            ordinal_field_names=("point_ordinal", "shape_ordinal"),
            relation_status_device_ptr=5000,
            relation_status_field_name="relation_status",
            relation_boundary_ordinals_device_ptr=6000,
            relation_boundary_ordinal_field_name="relation_boundary_ordinal",
        )
        self.assertTrue(output.has_relation_status_column)
        self.assertTrue(output.has_relation_boundary_ordinal_column)
        metadata = output.to_metadata()
        relation_status = metadata["runtime"]["relation_status_column"]
        self.assertEqual(relation_status["field_name"], "relation_status")
        self.assertEqual(relation_status["data_ptr"], 5000)
        self.assertEqual(
            relation_status["value_contract"]["2"],
            "accepted_by_closed_shape_boundary_predicate",
        )
        self.assertFalse(relation_status["release_authorized"])
        boundary_ordinal = metadata["runtime"]["relation_boundary_ordinal_column"]
        self.assertEqual(boundary_ordinal["field_name"], "relation_boundary_ordinal")
        self.assertEqual(boundary_ordinal["data_ptr"], 6000)
        self.assertEqual(boundary_ordinal["sentinel_value"], 0xFFFFFFFF)
        self.assertFalse(boundary_ordinal["release_authorized"])

    def test_cupy_refiner_exposes_boundary_contact_fast_path(self) -> None:
        source = (ROOT / "src/rtdsl/closed_shape_topology.py").read_text(encoding="utf-8")
        self.assertIn("boundary_contact_closed_shape_candidate_refine", source)
        self.assertIn("def refine_boundary_contacts(", source)
        self.assertIn("validate_columns: bool = True", source)
        self.assertIn("relation_boundary_ordinal", source)
        self.assertIn("full_simple_ring_scan_used", source)
        self.assertIn("boundary_contact_single_element_closed_shape_membership", source)
        self.assertIn('"trusted_native_stream_fast_path": not bool(validate_columns)', source)
        self.assertIn("def count_boundary_contacts_numba(", source)
        self.assertIn("boundary_contact_count_closed_shape_membership", source)
        self.assertIn("row_stream_materialized", source)
        self.assertIn("_numba_boundary_contact_closed_shape_count_kernel", source)


if __name__ == "__main__":
    unittest.main()
