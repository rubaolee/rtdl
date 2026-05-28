import unittest

import rtdsl as rt
from rtdsl.partner import RtdlTensorDescriptor
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


class Goal2658V24PartnerProtocolTest(unittest.TestCase):
    def test_contract_preserves_roadmap_boundaries(self):
        validation = rt.validate_v2_4_partner_protocol_contract()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["scope"], "rtdl_primitive_handoff_only")
        self.assertEqual(validation["native_engine_boundary"], "app_agnostic_native_engine")
        self.assertEqual(validation["memory_manager_boundary"], "not_a_general_purpose_memory_manager")
        self.assertEqual(validation["benchmark_app_count"], 10)
        self.assertEqual(validation["primary_comparison_row_count"], 11)
        self.assertIn("Hausdorff / X-HD-style", validation["low_margin_rows"])
        self.assertIn("Barnes-Hut / RT-BarnesHut-style", validation["low_margin_rows"])
        self.assertIn("Robot collision", validation["low_margin_rows"])

    def test_buffer_descriptor_is_handoff_not_memory_manager(self):
        descriptor = rt.RtdlBufferDescriptor(
            name="query_points",
            dtype="float32",
            shape=(8, 3),
            device_type="cuda",
            device_id=0,
            data_ptr=4096,
            strides_bytes=(12, 4),
            access_mode="read",
            source_protocol="torch",
            capacity_elements=24,
        )
        meta = descriptor.to_metadata()
        self.assertEqual(meta["scope"], "rtdl_primitive_handoff_only")
        self.assertEqual(meta["memory_manager_boundary"], "not_a_general_purpose_memory_manager")
        self.assertEqual(meta["element_count"], 24)
        self.assertEqual(meta["capacity_elements"], 24)
        self.assertTrue(meta["data_ptr_observed"])

    def test_buffer_descriptor_rejects_general_manager_scope_creep(self):
        with self.assertRaisesRegex(ValueError, "stream handles"):
            rt.RtdlBufferDescriptor(
                name="bad_stream",
                dtype="float32",
                shape=(4,),
                device_type="cuda",
                data_ptr=8,
                stream_handle=123,
            )
        with self.assertRaisesRegex(ValueError, "capacity_elements"):
            rt.RtdlBufferDescriptor(
                name="bad_capacity",
                dtype="float32",
                shape=(4,),
                device_type="cpu",
                capacity_elements=3,
            )

    def test_tensor_descriptor_can_be_promoted_to_v2_4_buffer_descriptor(self):
        tensor = RtdlTensorDescriptor(
            data_ptr=8192,
            device_type="cpu",
            device_id=0,
            dtype="float64",
            shape=(2, 2),
            strides=(16, 8),
            access_mode="read",
            source_protocol="numpy",
        )
        descriptor = rt.buffer_descriptor_from_tensor_descriptor("host_table", tensor)
        self.assertEqual(descriptor.name, "host_table")
        self.assertEqual(descriptor.source_protocol, "numpy")
        self.assertEqual(descriptor.device_type, "cpu")
        self.assertEqual(descriptor.strides_bytes, (16, 8))
        self.assertEqual(descriptor.mutability, "immutable")

    def test_prepared_session_rejects_app_specific_native_vocab(self):
        buffer = rt.RtdlBufferDescriptor(
            name="rays",
            dtype="float32",
            shape=(16, 6),
            device_type="cuda",
            data_ptr=4096,
        )
        session = rt.RtdlPreparedSessionDescriptor(
            session_id="generic_session",
            backend="optix",
            primitive="grouped_ray_triangle_reduction",
            input_buffers=(buffer,),
            native_symbols=("rtdl_optix_grouped_ray_triangle_reduction",),
            reusable_scene=True,
            reusable_query_buffers=True,
        )
        meta = session.to_metadata()
        self.assertEqual(meta["native_engine_boundary"], "app_agnostic_native_engine")
        self.assertFalse(meta["app_specific_native_vocab_allowed"])
        self.assertTrue(meta["requires_phase_timing"])

        with self.assertRaisesRegex(ValueError, "app-specific token `raydb`"):
            rt.RtdlPreparedSessionDescriptor(
                session_id="bad_session",
                backend="optix",
                primitive="raydb_grouped_count",
                input_buffers=(buffer,),
            )

    def test_phase_timing_record_requires_split_rt_and_partner_phases(self):
        accepted = rt.validate_phase_timing_record(
            {
                "same_phase_contract_as_basis": True,
                "promoted_performance_path": True,
                "phases_sec": {
                    "query_preparation": 0.001,
                    "rt_traversal": 0.010,
                    "partner_continuation": 0.002,
                    "download": 0.0005,
                },
            }
        )
        self.assertEqual(accepted["status"], "accept")

        rejected = rt.validate_phase_timing_record(
            {
                "same_phase_contract_as_basis": False,
                "promoted_performance_path": True,
                "phases_sec": {"rt_and_partner_combined": 0.012},
            }
        )
        self.assertEqual(rejected["status"], "reject")
        self.assertTrue(any("separate phases" in error for error in rejected["errors"]))
        self.assertTrue(any("same phase contract" in error for error in rejected["errors"]))

    def test_raydb_prepared_path_exposes_generic_v2_4_session_descriptor(self):
        fixture = raydb.make_benchmark_fixture(fixture_kind="repeated", copies=1)
        plan = raydb.make_plan("count")
        workload = raydb._make_paper_rt_encoded_packed_workload(fixture, plan, "count")
        metadata = raydb.describe_paper_rt_v2_4_prepared_session(
            workload,
            backend="embree",
            mode="count",
        )
        self.assertEqual(metadata["v2_4_protocol_version"], rt.V2_4_PARTNER_PROTOCOL_VERSION)
        self.assertEqual(metadata["primitive"], "ray_triangle_grouped_i64_reduction_3d")
        self.assertEqual(metadata["backend"], "embree")
        self.assertEqual(metadata["status"], "protocol_descriptor_only")
        self.assertFalse(metadata["app_specific_native_vocab_allowed"])
        self.assertIn("rays", [item["name"] for item in metadata["input_buffers"]])
        self.assertIn("triangles", [item["name"] for item in metadata["input_buffers"]])
        serialized = repr(metadata).lower()
        self.assertNotIn("raydb_grouped", serialized)
        self.assertNotIn("dbscan", serialized)


if __name__ == "__main__":
    unittest.main()
