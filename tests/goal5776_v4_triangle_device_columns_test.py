from pathlib import Path
import os
import runpy
import threading
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from rtdsl.v4_triangle_reduction_device_runtime import (
    _CompactDeviceColumnStatusSummary,
    _validate_compact_device_column_status,
    VerifiedTriangleDeviceColumnCountExecutor,
)
from rtdsl import v4_triangle_prepared_runtime as triangle_runtime


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
RUNTIME = ROOT / "src/rtdsl/v4_triangle_reduction_device_runtime.py"
CHECKED_REDUCTION = ROOT / "src/rtdsl/v4_checked_u64_device_reduction.py"
APP = ROOT / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py"


class Goal5776V4TriangleDeviceColumnsTest(unittest.TestCase):
    def test_v4_triangle_gas_requires_single_any_hit_delivery(self):
        source = NATIVE.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            source.count("OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL"),
            2,
        )
        self.assertNotIn(
            "uint32_t flags = OPTIX_GEOMETRY_FLAG_NONE;\n"
            "    triangles.flags = &flags;",
            source,
        )

    def test_particle_frontdoor_uses_column_output_without_array_truthiness(self):
        text = (ROOT / "Paper-reproduction-apps" /
                "goal5753-held-out-particle-tracking" /
                "v4_whole_app.py").read_text(encoding="utf-8")
        self.assertIn("queries is None or hasattr(query_values, \"dtype\")", text)
        self.assertNotIn("matched = bool(np.array_equal(", text)

    def test_particle_column_output_returns_scalar_exact_match(self):
        module = runpy.run_path(str(
            ROOT / "Paper-reproduction-apps" /
            "goal5753-held-out-particle-tracking" / "v4_whole_app.py"))
        expected = np.asarray(((1, 2, 3), (4, 5, 6)), dtype=np.uint32)

        class FakeOwner:
            lifecycle_receipt = {"kind": "test"}

            def execute(self, queries, **kwargs):
                self.partner_column_output = kwargs["partner_column_output"]
                return SimpleNamespace(
                    output=expected.copy(), traversal_receipt={"kind": "test"},
                    native_library_sha256="a" * 64,
                    output_sha256="b" * 64)

        owner = FakeOwner()
        prepared = module["PreparedParticleTrackingV4"](
            owner=owner,
            prepared_input={
                "queries": np.ones((2, 7), dtype=np.float32),
                "expected": expected,
            },
            total_prepare_seconds=0.0,
        )
        result = prepared.execute()
        self.assertIs(result["matched"], True)
        self.assertTrue(owner.partner_column_output)

    def test_particle_prepared_defaults_are_owned_read_only_snapshots(self):
        module = runpy.run_path(str(
            ROOT / "Paper-reproduction-apps" /
            "goal5753-held-out-particle-tracking" / "v4_whole_app.py"))
        queries = np.ones((2, 7), dtype=np.float32)
        expected = np.asarray(((1, 2, 3), (4, 5, 6)), dtype=np.uint32)

        class FakeOwner:
            lifecycle_receipt = {"kind": "test"}

            def execute(self, observed_queries, **kwargs):
                self.queries = observed_queries
                self.expected = kwargs["expected_output"]
                return SimpleNamespace(
                    output=np.asarray(kwargs["expected_output"]).copy(),
                    traversal_receipt={"kind": "test"},
                    native_library_sha256="a" * 64,
                    output_sha256="b" * 64,
                )

        owner = FakeOwner()
        prepared = module["PreparedParticleTrackingV4"](
            owner=owner,
            prepared_input={"queries": queries, "expected": expected},
            total_prepare_seconds=0.0,
        )
        queries[:] = 9.0
        expected[:] = 99
        result = prepared.execute()
        self.assertTrue(result["matched"])
        np.testing.assert_array_equal(owner.queries, np.ones((2, 7)))
        np.testing.assert_array_equal(
            owner.expected,
            np.asarray(((1, 2, 3), (4, 5, 6)), dtype=np.uint32),
        )
        self.assertFalse(owner.queries.flags.writeable)
        self.assertFalse(owner.expected.flags.writeable)

    @staticmethod
    def _query_batch_owner():
        owner = triangle_runtime.PreparedBuiltinTriangleOwner.__new__(
            triangle_runtime.PreparedBuiltinTriangleOwner)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._binding_identity = lambda count: ("a" * 64, "b" * 64)
        return owner

    def test_prepared_query_batch_copies_and_freezes_caller_input(self):
        owner = self._query_batch_owner()
        source = np.asarray((
            (0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 2.0),
            (1.0, 1.0, 1.0, 0.0, 1.0, -1.0, 3.0),
        ), dtype=np.float32)
        batch = owner.prepare_query_batch(source)
        source[:] = 9.0
        origins, directions, tmax, count, binding, semantic = (
            owner._prepared_query_batch_columns(batch))
        np.testing.assert_array_equal(
            origins, np.asarray(((0.0, 0.0, 1.0), (1.0, 1.0, 1.0))))
        np.testing.assert_array_equal(
            directions, np.asarray(((0.0, 0.0, -1.0), (0.0, 1.0, -1.0))))
        np.testing.assert_array_equal(tmax, np.asarray((2.0, 3.0)))
        self.assertEqual((count, binding, semantic), (2, "a" * 64, "b" * 64))
        self.assertTrue(all(not value.flags.writeable for value in (
            origins, directions, tmax)))
        with self.assertRaises(ValueError):
            origins.setflags(write=True)

    def test_prepared_query_batch_rejects_foreign_owner(self):
        left = self._query_batch_owner()
        right = self._query_batch_owner()
        batch = left.prepare_query_batch(np.asarray((
            (0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 2.0),
        ), dtype=np.float32))
        with self.assertRaisesRegex(RuntimeError, "identity drifted"):
            right._prepared_query_batch_columns(batch)

    def test_device_resident_query_batch_abi_is_additive_and_complete(self):
        class Symbol:
            argtypes = None
            restype = None

        self.assertEqual(
            triangle_runtime._configure_device_resident_query_batches(
                SimpleNamespace()),
            (None, None, None),
        )
        with self.assertRaisesRegex(RuntimeError, "partial"):
            triangle_runtime._configure_device_resident_query_batches(
                SimpleNamespace(
                    rtdl_optix_v4_prepare_builtin_triangle_query_batch_columns_v1=(
                        Symbol()
                    ),
                )
            )
        prepare, execute, destroy = (Symbol(), Symbol(), Symbol())
        configured = triangle_runtime._configure_device_resident_query_batches(
            SimpleNamespace(
                rtdl_optix_v4_prepare_builtin_triangle_query_batch_columns_v1=(
                    prepare
                ),
                rtdl_optix_v4_execute_prepared_builtin_triangle_callback_batch_columns_v3=(
                    execute
                ),
                rtdl_optix_v4_destroy_prepared_builtin_triangle_query_batch_v1=(
                    destroy
                ),
            )
        )
        self.assertEqual(configured, (prepare, execute, destroy))
        self.assertEqual(len(prepare.argtypes), 8)
        self.assertEqual(len(execute.argtypes), 8)
        self.assertEqual(len(destroy.argtypes), 3)
        self.assertIs(prepare.restype, triangle_runtime.ctypes.c_int)
        self.assertIs(execute.restype, triangle_runtime.ctypes.c_int)
        self.assertIs(destroy.restype, triangle_runtime.ctypes.c_int)

    def test_runtime_validated_execution_is_owner_and_output_bound(self):
        owner = object()
        output = np.zeros((2, 3), dtype=np.uint32)
        receipt = object()
        result = SimpleNamespace(
            output=output,
            output_sha256="a" * 64,
            traversal_receipt=receipt,
        )
        authority = triangle_runtime._ValidatedPreparedTriangleExecution(
            owner=owner,
            output=output,
            output_sha256="a" * 64,
            receipt=receipt,
            query_count=2,
            composed_ptx_sha256="b" * 64,
            native_library_sha256="c" * 64,
            binding_digest="d" * 64,
            token=triangle_runtime._VALIDATED_PREPARED_EXECUTION_TOKEN,
        )
        result._validated_prepared_execution = authority
        self.assertIs(
            triangle_runtime.validate_prepared_triangle_execution(
                result,
                owner=owner,
                query_count=2,
                composed_ptx_sha256="b" * 64,
                native_library_sha256="c" * 64,
                binding_digest="d" * 64,
            ),
            authority,
        )
        result.output = output.copy()
        with self.assertRaisesRegex(RuntimeError, "binding differs"):
            triangle_runtime.validate_prepared_triangle_execution(
                result,
                owner=owner,
                query_count=2,
                composed_ptx_sha256="b" * 64,
                native_library_sha256="c" * 64,
                binding_digest="d" * 64,
            )

    def test_legacy_tuple_execute_returns_without_column_proof(self):
        owner = self._query_batch_owner()
        owner._active = threading.Lock()
        owner._execute_columns = None
        owner._execute_query_batch = None
        owner._token = 17
        owner._library = object()
        owner._audit_sequence = 0
        owner._execution_count = 0
        owner._native_sha = "c" * 64
        owner._ptx_sha = "b" * 64

        def execute(
            _token, _origins, _directions, _tmax, count,
            output_0, output_1, output_2, observed_primitive,
            observed_kind, observed_bx, observed_by, statuses, counters,
            _error, _error_size,
        ):
            self.assertEqual(count, 1)
            output_0[0], output_1[0], output_2[0] = 7, 8, 9
            observed_primitive[0] = 3
            observed_kind[0] = 0xFE
            observed_bx[0] = 0.25
            observed_by[0] = 0.5
            counters[1] = counters[4] = counters[6] = 1
            return 0

        owner._execute = execute

        class Audit:
            def finish(self, **_kwargs):
                return {"physical_executor_classification": "optix_traversal_observed"}

            def abort(self):
                raise AssertionError("successful tuple execution aborted its audit")

        with mock.patch.object(
            triangle_runtime.OptixTraversalAuditSession,
            "open",
            return_value=Audit(),
        ):
            result = owner.execute((
                ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0),
            ))
        self.assertEqual(result.output, ((7, 8, 9),))
        self.assertFalse(hasattr(result, "_validated_prepared_execution"))
        self.assertEqual(result.hit_observations[0]["primitive_index"], 3)

    def test_device_resident_query_batch_native_section_is_app_neutral(self):
        native = NATIVE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_v4_prepare_builtin_triangle_query_batch_columns_v1",
            "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_batch_columns_v3",
            "rtdl_optix_v4_destroy_prepared_builtin_triangle_query_batch_v1",
        ):
            self.assertIn(symbol, api)
        begin = native.index("struct V4PreparedBuiltinTriangleQueryBatch")
        end = native.index("struct V4SphereBuildFacts", begin)
        section = native[begin:end].lower()
        for forbidden in (
            "particle", "tracking", "cell_transition", "neighbor_cell",
            "triangle_counting", "raydb", "rayjoin", "barneshut",
        ):
            self.assertNotIn(forbidden, section)
        self.assertIn("prepared_query_batch->query_columns", section)
        self.assertIn("prepared_query_batch->program.get()", section)

    def test_compact_triangle_summary_is_fail_closed(self):
        summary = triangle_runtime._CompactLifecycleSummary()
        summary.schema_version = 2
        summary.ok = 1
        summary.validated_row_count = 5
        summary.required_invocation_mask = (1 << 1) | (1 << 6)
        summary.terminal_invocation_mask = (1 << 4) | (1 << 5)
        summary.first_invalid_row = (1 << 64) - 1
        summary.role_counters[1] = 5
        summary.role_counters[4] = 3
        summary.role_counters[5] = 2
        summary.role_counters[6] = 5
        summary.success_status_d2h_bytes = triangle_runtime.ctypes.sizeof(
            triangle_runtime._CompactLifecycleSummary)
        self.assertEqual(
            triangle_runtime._validate_compact_lifecycle_summary(summary, 5),
            (0, 5, 0, 0, 3, 2, 5),
        )
        summary.error_code = 17
        with self.assertRaisesRegex(RuntimeError, "summary is invalid"):
            triangle_runtime._validate_compact_lifecycle_summary(summary, 5)

    def test_compact_triangle_native_path_keeps_generic_callback(self):
        native = NATIVE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        helper = (ROOT / "src/native/optix/rtdl_optix_cuda_helpers.cu").read_text(
            encoding="utf-8")
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_columns_v2",
            api,
        )
        self.assertIn("query_count, 0u, 2u", native)
        self.assertIn("mode > 2u", helper)
        self.assertIn(
            "Public result bytes cross the host boundary only after", native)
        compact_begin = native.index("if (compact_column_mode) {")
        compact_end = native.index("} else {", compact_begin)
        compact = native[compact_begin:compact_end]
        self.assertNotIn("observed_primitive_index", compact)
        self.assertNotIn("triangle_counting", compact)
        self.assertNotIn("particle", compact.lower())

    def test_native_route_is_generic_built_in_triangle_optix(self):
        native = NATIVE.read_text(encoding="utf-8")
        begin = native.index(
            "static uint64_t prepare_v4_triangle_reduction_device_columns_program")
        end = native.index(
            "static std::shared_ptr<V4PreparedTriangleReduction>", begin)
        prepare = native[begin:end]
        execute_begin = native.index(
            "static void execute_v4_prepared_triangle_reduction_device_columns_count_callback")
        execute_end = native.index(
            "static void destroy_v4_prepared_triangle_reduction_callback", execute_begin)
        execute = native[execute_begin:execute_end]
        self.assertIn("build_v4_triangle_anyhit_accel_from_device_columns", prepare)
        self.assertIn(
            "v4_rtdlexe_triangle_diagnostic_producer_spec()", prepare)
        self.assertNotIn(
            '"__raygen__rtdl_v4_triangle_reduction",', prepare)
        self.assertIn("V4TriangleReductionParams parameters = {};", execute)
        self.assertNotIn("parameters.fast_control =", execute)
        self.assertIn("optixLaunch", execute)
        self.assertIn("rtdl_optix_bind_traversal_audit_context", execute)
        self.assertNotIn("triangle_counting", prepare + execute)
        self.assertNotIn("RT-1A2", prepare + execute)
        self.assertNotIn("RT-2A1", prepare + execute)

    def test_c_abi_uses_device_pointers_and_keeps_host_route(self):
        api = API.read_text(encoding="utf-8")
        self.assertIn(
            "rtdl_optix_v4_prepare_triangle_reduction_device_columns_count_v1",
            api,
        )
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_device_columns_count_v1",
            api,
        )
        self.assertIn("rtdl_optix_v4_prepare_triangle_reduction_callback_v1", api)
        self.assertIn("rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v1", api)

    def test_segmented_triangle_program_owner_reuses_generic_pipeline(self):
        api = API.read_text(encoding="utf-8")
        native = NATIVE.read_text(encoding="utf-8")
        runtime = (ROOT / "src/rtdsl/v4_triangle_reduction_device_runtime.py").read_text(
            encoding="utf-8")
        self.assertIn(
            "rtdl_optix_v4_prepare_triangle_reduction_device_columns_program_v2",
            api,
        )
        self.assertIn(
            "rtdl_optix_v4_prepare_triangle_reduction_device_columns_count_from_program_v2",
            api,
        )
        self.assertIn(
            "g_v4_triangle_device_column_program_registry", native)
        self.assertIn("prepared->pipeline = std::move(pipeline);", native)
        self.assertIn("self._prepare_from_program(", runtime)
        begin = native.index(
            "prepare_v4_triangle_reduction_device_columns_count_with_pipeline")
        end = native.index(
            "static uint64_t prepare_v4_triangle_reduction_device_columns_count_callback",
            begin,
        )
        generic_segment = native[begin:end]
        self.assertNotIn("triangle_counting", generic_segment)
        self.assertNotIn("RT-2A1", generic_segment)

    def test_fused_column_validation_and_compact_status_are_generic(self):
        api = API.read_text(encoding="utf-8")
        native = NATIVE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn(
            "rtdl_optix_v4_prepare_triangle_reduction_device_columns_count_from_program_v3",
            api,
        )
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_device_columns_count_v2",
            api,
        )
        self.assertIn("ids[i] != i", native)
        self.assertIn(
            "rtdl_cuda_reduce_v4_callback_product_status_precompiled(", native)
        self.assertIn(
            "reinterpret_cast<const uint64_t*>(per_ray), nullptr,\n"
            "            reinterpret_cast<const uint64_t*>(counters.ptr)",
            native,
        )
        self.assertIn("validate_ids=not fused_column_validation", runtime)
        execute_begin = native.index(
            "static void execute_v4_prepared_triangle_reduction_device_columns_count_callback")
        execute_end = native.index(
            "static void destroy_v4_prepared_triangle_reduction_callback", execute_begin)
        fused = native[execute_begin:execute_end]
        self.assertNotIn("triangle_counting", fused)
        self.assertNotIn("RT-2A1", fused)

    def test_compact_device_column_summary_is_fail_closed(self):
        summary = _CompactDeviceColumnStatusSummary()
        summary.schema_version = 2
        summary.ok = 1
        summary.validated_row_count = 5
        summary.required_invocation_mask = (1 << 1) | (1 << 6)
        summary.terminal_invocation_mask = 1 << 5
        summary.first_invalid_row = (1 << 64) - 1
        summary.role_counters[1] = 5
        summary.role_counters[5] = 5
        summary.role_counters[6] = 5
        summary.success_status_d2h_bytes = 112
        self.assertEqual(
            _validate_compact_device_column_status(summary, 5),
            (0, 5, 0, 0, 0, 5, 5),
        )
        summary.invalid_row_count = 1
        with self.assertRaisesRegex(RuntimeError, "summary is invalid"):
            _validate_compact_device_column_status(summary, 5)

    def test_runtime_preserves_device_rows_and_checked_u64_bounds(self):
        source = RUNTIME.read_text(encoding="utf-8")
        reduction_source = CHECKED_REDUCTION.read_text(encoding="utf-8")
        self.assertIn("per_ray_host_materialized\": False", source)
        self.assertIn("checked_u64_weighted_sum_device", source)
        self.assertIn("maximum_value > value_upper_bound", reduction_source)
        self.assertIn("value_upper_bound > U64_MAX // weight_sum", reduction_source)
        self.assertIn("copied_summary.tolist()", reduction_source)
        self.assertIn("checked_summary.summary_copy_sync", reduction_source)
        self.assertIn("OptixTraversalAuditSession.open", source)
        self.assertIn("physical_executor_classification", source)
        self.assertNotIn("paper_algorithm", source)

    def test_executor_close_is_idempotent_and_use_after_close_fails_closed(self):
        executor = VerifiedTriangleDeviceColumnCountExecutor.__new__(
            VerifiedTriangleDeviceColumnCountExecutor)
        executor._closed = False
        executor.close()
        executor.close()
        with self.assertRaisesRegex(RuntimeError, "executor is closed"):
            executor.execute_segment(None, None)

    def test_application_owns_algorithm_and_uses_bounded_segments(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("paper_algorithm=self.paper_algorithm", source)
        self.assertIn("iter_segmented_rt_graph_device_geometry", source)
        self.assertIn("default_selected_between_paper_algorithms\": False", source)
        self.assertIn("global_two_hop_materialized\": False", source)
        self.assertIn("run_v4_segmented_complete", source)


if __name__ == "__main__":
    unittest.main()
