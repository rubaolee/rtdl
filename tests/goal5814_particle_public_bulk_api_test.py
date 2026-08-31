from __future__ import annotations

import types
import unittest
from unittest import mock

import numpy as np

from rtdsl import v4
from rtdsl import v4_public_builtin_triangle as public_triangle
from rtdsl import v4_triangle_prepared_runtime as triangle_runtime


class _NoElementIteration(np.ndarray):
    """Array witness that fails if the public API manufactures Python rows."""

    def __iter__(self):  # pragma: no cover - a call is the test failure
        raise AssertionError("bulk input was expanded through Python iteration")

    def tolist(self):  # pragma: no cover - a call is the test failure
        raise AssertionError("bulk input was expanded through ndarray.tolist")


def _no_iter(shape, dtype):
    return np.empty(shape, dtype=dtype).view(_NoElementIteration)


class Goal5814ParticlePublicBulkApiTest(unittest.TestCase):
    def test_particle_scale_columns_are_retained_without_element_iteration(self):
        # Exact Goal5814 Particle dimensions.  np.empty reserves only the raw
        # ABI storage; the no-iteration subclass proves the constructor does
        # not manufacture ~14 million Python rows/scalars from it.
        vertices = _no_iter((314_587, 3), "<f4")
        triangles = _no_iter((3_392_530, 3), "<u4")
        front = _no_iter((3_392_530,), "<u4")
        back = _no_iter((3_392_530,), "<u4")
        queries = _no_iter((5_000, 7), "<f4")

        static_input = v4.BuiltinTriangleCallbackStaticInput(
            vertices=vertices,
            triangles=triangles,
            first_primitive_values=front,
            second_primitive_values=back,
        )
        batch = v4.BuiltinTriangleCallbackBatch(queries=queries)

        self.assertTrue(static_input.uses_contiguous_columns)
        self.assertTrue(batch.uses_contiguous_columns)
        for retained, original in (
            (static_input.vertices, vertices),
            (static_input.triangles, triangles),
            (static_input.first_primitive_values, front),
            (static_input.second_primitive_values, back),
            (batch.queries, queries),
        ):
            self.assertIsInstance(retained, np.ndarray)
            self.assertTrue(np.shares_memory(retained, original))

    def test_shaped_memoryviews_are_zero_copy_public_bulk_inputs(self):
        vertices = np.empty((4, 3), dtype="<f4")
        triangles = np.empty((2, 3), dtype="<u4")
        front = np.empty((2,), dtype="<u4")
        back = np.empty((2,), dtype="<u4")
        queries = np.empty((3, 7), dtype="<f4")

        static_input = v4.BuiltinTriangleCallbackStaticInput(
            vertices=memoryview(vertices),
            triangles=memoryview(triangles),
            first_primitive_values=memoryview(front),
            second_primitive_values=memoryview(back),
        )
        batch = v4.BuiltinTriangleCallbackBatch(memoryview(queries))

        self.assertTrue(np.shares_memory(static_input.vertices, vertices))
        self.assertTrue(np.shares_memory(static_input.triangles, triangles))
        self.assertTrue(np.shares_memory(
            static_input.first_primitive_values, front))
        self.assertTrue(np.shares_memory(
            static_input.second_primitive_values, back))
        self.assertTrue(np.shares_memory(batch.queries, queries))

    def test_small_python_sequence_api_is_unchanged(self):
        static_input = v4.BuiltinTriangleCallbackStaticInput(
            vertices=[(0, 0, 0), (1, 0, 0), (0, 1, 0)],
            triangles=[[0, 1, 2]],
            first_primitive_values=[7],
            second_primitive_values=[8],
        )
        batch = v4.BuiltinTriangleCallbackBatch(
            queries=[((0, 0, 1), (0, 0, -1), 2)],
        )
        self.assertEqual(
            static_input.vertices,
            ((0, 0, 0), (1, 0, 0), (0, 1, 0)),
        )
        self.assertEqual(static_input.triangles, ((0, 1, 2),))
        self.assertEqual(static_input.first_primitive_values, (7,))
        self.assertEqual(static_input.second_primitive_values, (8,))
        self.assertEqual(
            batch.queries, (((0, 0, 1), (0, 0, -1), 2),))
        self.assertFalse(static_input.uses_contiguous_columns)
        self.assertFalse(batch.uses_contiguous_columns)

    def test_bulk_static_input_rejects_dtype_shape_endian_stride_and_mixing(self):
        valid = {
            "vertices": np.empty((4, 3), dtype="<f4"),
            "triangles": np.empty((2, 3), dtype="<u4"),
            "first_primitive_values": np.empty((2,), dtype="<u4"),
            "second_primitive_values": np.empty((2,), dtype="<u4"),
        }

        mutations = {
            "vertex_dtype": {"vertices": np.empty((4, 3), dtype="<f8")},
            "vertex_endian": {"vertices": np.empty((4, 3), dtype=">f4")},
            "vertex_shape": {"vertices": np.empty((4, 4), dtype="<f4")},
            "vertex_stride": {
                "vertices": np.empty((4, 6), dtype="<f4")[:, ::2]},
            "triangle_dtype": {
                "triangles": np.empty((2, 3), dtype="<i4")},
            "triangle_shape": {
                "triangles": np.empty((2, 4), dtype="<u4")},
            "metadata_dtype": {
                "first_primitive_values": np.empty((2,), dtype="<i4")},
            "metadata_shape": {
                "first_primitive_values": np.empty((2, 1), dtype="<u4")},
            "metadata_count": {
                "first_primitive_values": np.empty((1,), dtype="<u4")},
            "mixed_bulk_tuple": {"second_primitive_values": (1, 2)},
        }
        for label, mutation in mutations.items():
            with self.subTest(label=label):
                arguments = {**valid, **mutation}
                with self.assertRaises(
                    v4.PublicCallbackLifecycleError,
                ) as rejected:
                    v4.BuiltinTriangleCallbackStaticInput(**arguments)
                self.assertEqual(
                    rejected.exception.code, "GC031_BULK_INPUT_INVALID")

    def test_bulk_batch_rejects_dtype_shape_endian_stride_and_empty(self):
        invalid = {
            "dtype": np.empty((2, 7), dtype="<f8"),
            "endian": np.empty((2, 7), dtype=">f4"),
            "shape": np.empty((2, 6), dtype="<f4"),
            "stride": np.empty((2, 14), dtype="<f4")[:, ::2],
            "empty": np.empty((0, 7), dtype="<f4"),
        }
        for label, queries in invalid.items():
            with self.subTest(label=label):
                with self.assertRaises(
                    v4.PublicCallbackLifecycleError,
                ) as rejected:
                    v4.BuiltinTriangleCallbackBatch(queries)
                self.assertEqual(
                    rejected.exception.code, "GC031_BULK_INPUT_INVALID")

    def test_bulk_batch_requests_runtime_numpy_column_output(self):
        class _Owner:
            def __init__(self):
                self.queries = None
                self.partner_column_output = None

            def execute(self, queries, *, partner_column_output=False):
                self.queries = queries
                self.partner_column_output = partner_column_output
                output = np.asarray(
                    ((1, 2, 3), (4, 5, 6)), dtype="<u4",
                ).view(_NoElementIteration)
                return types.SimpleNamespace(
                    output=output,
                    hit_observations=(),
                    role_counters=(2, 2, 2, 2, 2, 0, 2),
                    launch_status=({
                        "validated_row_count": 2,
                        "first_error_claimed": 0,
                        "error_code": 0,
                    },),
                    traversal_receipt={},
                    output_sha256=public_triangle._bulk_u32x3_digest(output),
                    composed_ptx_sha256="b" * 64,
                    native_library_sha256="c" * 64,
                )

        owner = _Owner()
        prepared = v4.PreparedBuiltinTriangleCallbackProgram(
            owner=owner,
            identity=v4.BuiltinTriangleCallbackExecutableIdentity(
                program_identity_sha256="a" * 64,
                physical_schema_sha256="a" * 64,
                canonical_plan_sha256="a" * 64,
                callback_abi_sha256="a" * 64,
                wrapper_source_sha256="a" * 64,
                generated_executable_sha256="a" * 64,
                composed_ptx_sha256="b" * 64,
                native_library_sha256="c" * 64,
            ),
            decision=types.SimpleNamespace(verdict="ACCEPT"),
            _construction_token=public_triangle._CONSTRUCTION_TOKEN,
        )
        queries = _no_iter((2, 7), "<f4")
        batch = v4.BuiltinTriangleCallbackBatch(queries)
        with mock.patch(
            "rtdsl.physical_execution_provenance.validate_traversal_receipt",
        ) as validate:
            result = prepared.execute(batch)
        self.assertTrue(owner.partner_column_output)
        self.assertTrue(np.shares_memory(owner.queries, queries))
        self.assertIsInstance(result.output, np.ndarray)
        np.testing.assert_array_equal(
            result.output, np.asarray(((1, 2, 3), (4, 5, 6)), dtype="<u4"))
        validate.assert_called_once()

    def test_bulk_output_digest_is_independent_and_never_materializes_rows(self):
        output = np.arange(15_000, dtype="<u4").reshape(5_000, 3).view(
            _NoElementIteration)
        self.assertEqual(
            public_triangle._bulk_u32x3_digest(output),
            triangle_runtime._bulk_u32x3_digest(output),
        )

    def test_small_batch_does_not_force_bulk_runtime_keyword(self):
        class _ReachedRuntime(RuntimeError):
            pass

        class _TinyOwner:
            def execute(self, queries):
                raise _ReachedRuntime

        prepared = v4.PreparedBuiltinTriangleCallbackProgram(
            owner=_TinyOwner(),
            identity=object(),
            decision=types.SimpleNamespace(verdict="ACCEPT"),
            _construction_token=public_triangle._CONSTRUCTION_TOKEN,
        )
        batch = v4.BuiltinTriangleCallbackBatch(
            (((0, 0, 1), (0, 0, -1), 2),))
        with self.assertRaises(_ReachedRuntime):
            prepared.execute(batch)


if __name__ == "__main__":
    unittest.main()
