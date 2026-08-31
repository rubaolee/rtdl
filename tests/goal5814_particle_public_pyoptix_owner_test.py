from __future__ import annotations

import ctypes
import inspect
from pathlib import Path
import unittest
from unittest import mock

import numpy as np

from experiments.goal5814_particle import public_pyoptix_owner as owner_module
from experiments.goal5814_particle.public_pyoptix_owner import (
    CLOSEST_HIT_ENTRY,
    CONTROL_DTYPE,
    FORMAL_PARTICLE_SHAPE,
    MISS_ENTRY,
    PARTICLE_PARAM_DTYPE,
    RAYGEN_ENTRY,
    FormalPublicPyOptixParticleOwner,
    ParticleDeviceStatusError,
    PrevalidatedParticleExecutionInput,
    ParticleOracleMismatch,
    ParticleProblemShape,
    PublicPyOptixParticleOwner,
    PublicPyOptixRuntime,
    _prevalidate_particle_execution_input,
    prevalidate_formal_particle_execution_input,
    prepare_formal_particle_owner,
)


ROOT = Path(__file__).resolve().parents[1]
OWNER_SOURCE = (
    ROOT / "experiments" / "goal5814_particle" / "public_pyoptix_owner.py")


class _Object:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _Memory:
    def __init__(self, nbytes: int):
        self.size = int(nbytes)
        self.storage = (ctypes.c_ubyte * self.size)()
        self.ptr = ctypes.addressof(self.storage)

    def copy_from(self, source, nbytes: int) -> None:
        ctypes.memmove(self.ptr, int(source.value), int(nbytes))


class _Stream:
    next_ptr = 1

    def __init__(self, *, non_blocking: bool):
        if not non_blocking:
            raise AssertionError("owner stream must be nonblocking")
        self.ptr = _Stream.next_ptr
        _Stream.next_ptr += 1
        self.synchronize_count = 0

    def synchronize(self) -> None:
        self.synchronize_count += 1


class _CudaRuntime:
    memcpyHostToDevice = 1
    memcpyDeviceToHost = 2

    def __init__(self):
        self.free_calls = []
        self.copy_calls = []

    def free(self, pointer: int) -> None:
        self.free_calls.append(int(pointer))

    def memcpyAsync(
            self, destination: int, source: int, nbytes: int,
            kind: int, stream: int) -> None:
        self.copy_calls.append((int(nbytes), int(kind), int(stream)))
        ctypes.memmove(int(destination), int(source), int(nbytes))


class _Cuda:
    def __init__(self):
        self.runtime = _CudaRuntime()

    @staticmethod
    def alloc(nbytes: int) -> _Memory:
        return _Memory(nbytes)

    @staticmethod
    def alloc_pinned_memory(nbytes: int):
        return (ctypes.c_ubyte * int(nbytes))()

    Stream = _Stream


class _Cupy:
    def __init__(self):
        self.cuda = _Cuda()


class _Pipeline:
    def __init__(self):
        self.stack = None

    def setStackSize(self, *values) -> None:
        self.stack = values


class _Context:
    def __init__(self, owner):
        self.owner = owner
        self.cache_enabled = None
        self.module_ptx = None
        self.program_descriptors = []
        self.build_input = None

    def setCacheEnabled(self, enabled: bool) -> None:
        self.cache_enabled = bool(enabled)

    def moduleCreate(self, module_options, pipeline_options, ptx):
        self.module_ptx = ptx
        return _Object(), ""

    def programGroupCreate(self, descriptors):
        self.program_descriptors.extend(descriptors)
        return [_Object(descriptor=descriptors[0])], ""

    def pipelineCreate(self, options, link, groups, log):
        return _Pipeline()

    def accelComputeMemoryUsage(self, options, build_inputs):
        self.build_input = build_inputs[0]
        return _Object(tempSizeInBytes=64, outputSizeInBytes=128)

    def accelBuild(
            self, stream, options, build_inputs, temporary,
            temporary_bytes, output, output_bytes, emitted):
        self.build_input = build_inputs[0]
        return 0x1234


class _Util:
    @staticmethod
    def accumulateStackSizes(*args):
        return None

    @staticmethod
    def computeStackSizes(stack, trace_depth, cc_depth, dc_depth):
        return 0, 0, 0


class _FakeOptix:
    DEVICE_CONTEXT_VALIDATION_MODE_OFF = 0
    TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS = 1
    EXCEPTION_FLAG_NONE = 0
    PRIMITIVE_TYPE_FLAGS_TRIANGLE = 2
    COMPILE_DEFAULT_MAX_REGISTER_COUNT = 0
    COMPILE_OPTIMIZATION_DEFAULT = 0
    COMPILE_DEBUG_LEVEL_NONE = 0
    SBT_RECORD_HEADER_SIZE = 32
    SBT_RECORD_ALIGNMENT = 16
    VERTEX_FORMAT_FLOAT3 = 1
    INDICES_FORMAT_UNSIGNED_INT3 = 2
    GEOMETRY_FLAG_DISABLE_ANYHIT = 4
    BUILD_FLAG_PREFER_FAST_TRACE = 8
    BUILD_OPERATION_BUILD = 1

    DeviceContextOptions = _Object
    PipelineCompileOptions = _Object
    ModuleCompileOptions = _Object
    ProgramGroupDesc = _Object
    PipelineLinkOptions = _Object
    StackSizes = _Object
    ShaderBindingTable = _Object
    BuildInputTriangleArray = _Object
    AccelBuildOptions = _Object
    util = _Util()

    def __init__(self):
        self.context = None
        self.initialized = False
        self.launch_calls = []
        self.next_control = None
        self.next_output = None

    @staticmethod
    def version():
        return 9, 1, 0

    def init(self) -> None:
        self.initialized = True

    def deviceContextCreate(self, ordinal, options):
        self.context = _Context(self)
        return self.context

    @staticmethod
    def sbtRecordPackHeader(group, record) -> None:
        record["header"].fill(0xA5)

    def launch(
            self, pipeline, stream, params_pointer, params_bytes,
            sbt, width, height, depth) -> None:
        self.launch_calls.append((width, height, depth, params_bytes))
        raw = (ctypes.c_ubyte * PARTICLE_PARAM_DTYPE.itemsize).from_address(
            int(params_pointer))
        params = np.frombuffer(
            raw, dtype=PARTICLE_PARAM_DTYPE, count=1)[0]
        control = self.next_control
        if control is None:
            control = np.array(
                [(width, 0xFFFFFFFF, 0, 0)], dtype=CONTROL_DTYPE)
        ctypes.memmove(
            int(params["control"]), int(control.ctypes.data),
            CONTROL_DTYPE.itemsize)
        if self.next_output is not None:
            for name, column in (
                    ("output_selected", 0),
                    ("output_neighbor", 1),
                    ("output_face", 2)):
                source = np.ascontiguousarray(
                    self.next_output[:, column], dtype=np.uint32)
                ctypes.memmove(
                    int(params[name]), int(source.ctypes.data), source.nbytes)


def _ptx() -> bytes:
    return (
        b".version 8.0\n"
        + b".visible .entry " + RAYGEN_ENTRY.encode() + b"() {}\n"
        + b".visible .entry " + CLOSEST_HIT_ENTRY.encode() + b"() {}\n"
        + b".visible .entry " + MISS_ENTRY.encode() + b"() {}\n")


def _fixture():
    shape = ParticleProblemShape(4, 2, 3)
    vertices = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float32)
    triangles = np.array([[0, 1, 2], [0, 1, 3]], dtype=np.uint32)
    front = np.array([10, 11], dtype=np.uint32)
    back = np.array([20, 21], dtype=np.uint32)
    queries = np.array([
        [0.1, 0.1, -1.0, 0.0, 0.0, 1.0, 3.0],
        [0.2, 0.2, -1.0, 0.0, 0.0, 1.0, 3.0],
        [0.3, 0.1, -1.0, 0.0, 0.0, 1.0, 3.0],
    ], dtype=np.float32)
    expected = np.array([
        [10, 20, 0], [11, 21, 1], [10, 20, 0],
    ], dtype=np.uint32)
    return shape, vertices, triangles, front, back, queries, expected


def _soa_columns(queries: np.ndarray) -> tuple[np.ndarray, ...]:
    return tuple(
        np.array(queries[:, column], dtype=np.float32, copy=True, order="C")
        for column in range(7))


class Goal5814ParticlePublicPyOptixOwnerTest(unittest.TestCase):
    def prepare_owner(self):
        shape, vertices, triangles, front, back, queries, expected = _fixture()
        fake_optix = _FakeOptix()
        runtime = PublicPyOptixRuntime(cp=_Cupy(), optix=fake_optix)
        owner = PublicPyOptixParticleOwner.prepare(
            prebuilt_ptx=_ptx(), vertices=vertices, triangles=triangles,
            front_values=front, back_values=back, shape=shape,
            runtime=runtime)
        return owner, fake_optix, queries, expected

    def test_prepare_uses_public_indexed_triangle_pipeline(self):
        owner, fake_optix, _queries, _expected = self.prepare_owner()
        counts = owner.prepare_operation_counts
        self.assertTrue(fake_optix.initialized)
        self.assertFalse(fake_optix.context.cache_enabled)
        self.assertEqual(fake_optix.context.module_ptx, _ptx())
        self.assertEqual(counts.context_creation_call_count, 1)
        self.assertEqual(counts.module_creation_call_count, 1)
        self.assertEqual(counts.program_group_creation_call_count, 3)
        self.assertEqual(counts.pipeline_creation_call_count, 1)
        self.assertEqual(counts.accel_build_call_count, 1)
        self.assertEqual(counts.stream_creation_call_count, 1)
        self.assertEqual(counts.raw_device_allocation_call_count, 13)
        self.assertEqual(counts.h2d_copy_call_count, 7)
        self.assertEqual(counts.pinned_host_allocation_call_count, 4)
        build = fake_optix.context.build_input
        self.assertEqual(build.vertexFormat, fake_optix.VERTEX_FORMAT_FLOAT3)
        self.assertEqual(build.vertexStrideInBytes, 12)
        self.assertEqual(build.numVertices, 4)
        self.assertEqual(build.indexFormat, fake_optix.INDICES_FORMAT_UNSIGNED_INT3)
        self.assertEqual(build.indexStrideInBytes, 12)
        self.assertEqual(build.numIndexTriplets, 2)
        self.assertEqual(build.flags, [fake_optix.GEOMETRY_FLAG_DISABLE_ANYHIT])
        raygen, miss, hit = fake_optix.context.program_descriptors
        self.assertEqual(raygen.raygenEntryFunctionName, RAYGEN_ENTRY)
        self.assertEqual(miss.missEntryFunctionName, MISS_ENTRY)
        self.assertEqual(hit.hitgroupEntryFunctionNameCH, CLOSEST_HIT_ENTRY)
        self.assertFalse(hasattr(hit, "hitgroupModuleAH"))

    def test_complete_execute_has_frozen_copy_launch_gate_and_oracle_work(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        result = owner.execute_complete_soa(*columns, expected)
        self.assertTrue(np.array_equal(result.output, expected))
        self.assertFalse(result.output.flags.writeable)
        with self.assertRaises(ValueError):
            result.output[0, 0] = np.uint32(99)
        self.assertEqual(result.control, (3, 0xFFFFFFFF, 0, 0))
        counts = result.operation_counts
        self.assertEqual(counts.raw_device_allocation_call_count, 0)
        self.assertEqual(counts.query_h2d_copy_call_count, 7)
        self.assertEqual(
            counts.query_h2d_bytes, sum(column.nbytes for column in columns))
        self.assertEqual(counts.control_reset_h2d_copy_call_count, 1)
        self.assertEqual(counts.control_reset_h2d_bytes, 16)
        self.assertEqual(counts.parameter_h2d_copy_call_count, 1)
        self.assertEqual(counts.parameter_h2d_bytes, 120)
        self.assertEqual(counts.h2d_copy_call_count, 9)
        self.assertEqual(
            counts.h2d_copy_bytes,
            sum(column.nbytes for column in columns) + 16 + 120)
        self.assertEqual(counts.device_memset_call_count, 0)
        self.assertEqual(counts.optix_launch_call_count, 1)
        self.assertEqual(counts.raygen_invocation_count, 3)
        self.assertEqual(counts.control_d2h_copy_call_count, 1)
        self.assertEqual(counts.control_d2h_bytes, 16)
        self.assertEqual(counts.output_d2h_copy_call_count, 1)
        self.assertEqual(counts.output_d2h_bytes, expected.nbytes)
        self.assertTrue(counts.status_before_output)
        self.assertEqual(counts.output_d2h_after_status_failure, 0)
        self.assertEqual(counts.d2h_copy_call_count, 2)
        self.assertEqual(counts.d2h_copy_bytes, 16 + expected.nbytes)
        self.assertEqual(counts.explicit_stream_sync_call_count, 2)
        self.assertEqual(fake_optix.launch_calls, [(3, 1, 1, 120)])

    def test_failed_control_performs_zero_output_d2h(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        fake_optix.next_control = np.array(
            [(2, 1, 1, 1)], dtype=CONTROL_DTYPE)
        with self.assertRaises(ParticleDeviceStatusError) as caught:
            owner.execute_complete_soa(*_soa_columns(queries), expected)
        failure = caught.exception
        self.assertFalse(failure.application_output_exposed)
        self.assertEqual(failure.control, (2, 1, 1, 1))
        counts = failure.operation_counts
        self.assertEqual(counts.query_h2d_copy_call_count, 7)
        self.assertEqual(counts.optix_launch_call_count, 1)
        self.assertEqual(counts.control_d2h_copy_call_count, 1)
        self.assertEqual(counts.output_d2h_copy_call_count, 0)
        self.assertEqual(counts.output_d2h_bytes, 0)
        self.assertTrue(counts.status_before_output)
        self.assertEqual(counts.output_d2h_after_status_failure, 0)
        self.assertEqual(counts.explicit_stream_sync_call_count, 1)

    def test_exact_numpy_oracle_mismatch_is_inside_complete_execute(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected.copy()
        wrong = expected.copy()
        wrong[0, 0] += np.uint32(1)
        with self.assertRaises(ParticleOracleMismatch) as caught:
            owner.execute_complete_soa(*_soa_columns(queries), wrong)
        counts = caught.exception.operation_counts
        self.assertEqual(counts.output_d2h_copy_call_count, 1)
        self.assertEqual(counts.output_d2h_bytes, expected.nbytes)
        self.assertEqual(counts.explicit_stream_sync_call_count, 2)

    def test_prior_borrowed_output_cannot_alias_next_oracle(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        prior = owner.execute_complete_soa(*columns, expected).output
        self.assertTrue(np.shares_memory(prior, owner.host_output))
        aliased_oracle = np.ndarray(
            shape=expected.shape, dtype=np.uint32,
            buffer=owner.host_output, order="C")
        self.assertTrue(aliased_oracle.flags.c_contiguous)
        self.assertTrue(np.shares_memory(prior, aliased_oracle))
        with mock.patch.object(
                np, "array_equal",
                side_effect=AssertionError("aliased oracle must not compare")):
            with self.assertRaisesRegex(ValueError, "must not share memory"):
                owner.execute_complete_soa(*columns, aliased_oracle)
        counts = owner.last_execute_operation_counts
        self.assertEqual(counts.output_d2h_copy_call_count, 1)
        self.assertEqual(counts.explicit_stream_sync_call_count, 2)

    def test_formal_wrapper_cannot_accept_mock_cardinality(self):
        shape, vertices, triangles, front, back, _queries, _expected = _fixture()
        self.assertEqual(shape.query_count, 3)
        self.assertEqual(FORMAL_PARTICLE_SHAPE.query_count, 5000)
        with self.assertRaises(ValueError):
            prepare_formal_particle_owner(
                prebuilt_ptx=_ptx(), vertices=vertices, triangles=triangles,
                front_values=front, back_values=back,
                runtime=PublicPyOptixRuntime(cp=_Cupy(), optix=_FakeOptix()))

    def test_formal_api_is_soa_only_and_rejects_strided_columns(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        expanded = np.empty(columns[0].size * 2, dtype=np.float32)
        expanded[::2] = columns[0]
        with self.assertRaises(ValueError):
            owner.execute_complete_soa(
                expanded[::2], *columns[1:], expected)

        formal_source = inspect.getsource(
            PublicPyOptixParticleOwner.execute_complete_soa)
        self.assertNotIn("queries.T", formal_source)
        self.assertNotIn("transpose", formal_source.lower())
        self.assertNotIn("ascontiguousarray", formal_source)
        core_source = inspect.getsource(
            PublicPyOptixParticleOwner._execute_exact_core_locked)
        self.assertIn("np.copyto(", core_source)
        self.assertFalse(hasattr(
            FormalPublicPyOptixParticleOwner,
            "execute_complete_matrix_convenience"))

    def test_prevalidated_core_scans_once_and_materializes_after_oracle(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        for item in (*columns, expected):
            item.setflags(write=False)
        with mock.patch.object(np, "isfinite", wraps=np.isfinite) as finite:
            admitted = _prevalidate_particle_execution_input(
                *columns, expected, query_count=queries.shape[0])
        self.assertEqual(finite.call_count, 7)
        self.assertTrue(all(isinstance(item.base, bytes)
                            for item in (*admitted.columns, admitted.expected)))
        self.assertTrue(all(not item.flags.writeable
                            for item in (*admitted.columns, admitted.expected)))
        with mock.patch.object(
                np, "isfinite", side_effect=AssertionError("core rescanned")):
            completion = owner.execute_exact_core_prevalidated(admitted)
        self.assertIsNone(owner.last_execute_operation_counts)
        result = owner.materialize_exact_core_completion(completion)
        self.assertEqual(result.operation_counts.query_h2d_copy_call_count, 7)
        self.assertTrue(np.array_equal(result.output, expected))

    def test_prevalidated_capability_rejects_forgery_and_storage_drift(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        for item in (*columns, expected):
            item.setflags(write=False)
        admitted = _prevalidate_particle_execution_input(
            *columns, expected, query_count=queries.shape[0])
        with self.assertRaises(TypeError):
            PrevalidatedParticleExecutionInput()
        forged = object.__new__(PrevalidatedParticleExecutionInput)
        with self.assertRaises(TypeError):
            owner.execute_exact_core_prevalidated(forged)
        object.__setattr__(
            admitted, "_PrevalidatedParticleExecutionInput__columns",
            tuple(item.copy() for item in admitted.columns))
        with self.assertRaisesRegex(ValueError, "storage drifted"):
            owner.execute_exact_core_prevalidated(admitted)

    def test_exact_core_completion_rejects_stale_generation(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        for item in (*columns, expected):
            item.setflags(write=False)
        admitted = _prevalidate_particle_execution_input(
            *columns, expected, query_count=queries.shape[0])
        stale = owner.execute_exact_core_prevalidated(admitted)
        current = owner.execute_exact_core_prevalidated(admitted)
        with self.assertRaisesRegex(ValueError, "stale or foreign"):
            owner.materialize_exact_core_completion(stale)
        owner.materialize_exact_core_completion(current)

    def test_exact_core_completion_is_opaque_and_rejects_all_drift(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        foreign_owner, _foreign_optix, _queries, _expected = \
            self.prepare_owner()
        fake_optix.next_output = expected
        columns = _soa_columns(queries)
        for item in (*columns, expected):
            item.setflags(write=False)
        admitted = _prevalidate_particle_execution_input(
            *columns, expected, query_count=queries.shape[0])

        completion = owner.execute_exact_core_prevalidated(admitted)
        self.assertFalse(hasattr(completion, "output"))
        self.assertFalse(hasattr(completion, "control"))
        with self.assertRaises(AttributeError):
            object.__setattr__(completion, "output", expected)
        forged = object.__new__(owner_module.ParticleExactCoreCompletion)
        with self.assertRaisesRegex(ValueError, "stale or foreign"):
            owner.materialize_exact_core_completion(forged)
        with self.assertRaisesRegex(ValueError, "stale or foreign"):
            foreign_owner.materialize_exact_core_completion(completion)

        state = owner_module._PARTICLE_EXACT_CORE_COMPLETIONS[completion]
        state.operation_counts.query_h2d_bytes += 1
        with self.assertRaisesRegex(ValueError, "mutated after return"):
            owner.materialize_exact_core_completion(completion)

        completion = owner.execute_exact_core_prevalidated(admitted)
        state = owner_module._PARTICLE_EXACT_CORE_COMPLETIONS[completion]
        state.output.setflags(write=True)
        with self.assertRaisesRegex(ValueError, "mutated after return"):
            owner.materialize_exact_core_completion(completion)

        completion = owner.execute_exact_core_prevalidated(admitted)
        owner.host_output[0, 0] ^= np.uint32(1)
        with self.assertRaisesRegex(ValueError, "mutated after return"):
            owner.materialize_exact_core_completion(completion)

    def test_formal_admission_fixes_5000_and_rejects_mutable_sources(self):
        columns = tuple(
            np.zeros(FORMAL_PARTICLE_SHAPE.query_count, dtype=np.float32)
            for _ in range(7))
        columns[3].fill(np.float32(1.0))
        columns[6].fill(np.float32(1.0))
        expected = np.zeros(
            (FORMAL_PARTICLE_SHAPE.query_count, 3), dtype=np.uint32)
        with self.assertRaisesRegex(ValueError, "read-only"):
            prevalidate_formal_particle_execution_input(*columns, expected)
        for item in (*columns, expected):
            item.setflags(write=False)
        # A durable np.load/layout adapter may expose a read-only C-contiguous
        # view rather than an OWNDATA array.  Admission copies it into bytes,
        # so ownership is irrelevant once mutability/layout are checked.
        nonowning_expected = expected.view()
        self.assertFalse(nonowning_expected.flags.owndata)
        admitted = prevalidate_formal_particle_execution_input(
            *columns, nonowning_expected)
        self.assertEqual(admitted.query_count, 5000)

    def test_matrix_adapter_is_explicitly_nonformal(self):
        owner, fake_optix, queries, expected = self.prepare_owner()
        fake_optix.next_output = expected
        result = owner.execute_complete_matrix_convenience(queries, expected)
        self.assertTrue(np.array_equal(result.output, expected))
        self.assertEqual(result.operation_counts.query_h2d_copy_call_count, 7)

    def test_prebuilt_ptx_and_array_contracts_fail_closed(self):
        shape, vertices, triangles, front, back, _queries, _expected = _fixture()
        runtime = PublicPyOptixRuntime(cp=_Cupy(), optix=_FakeOptix())
        with self.assertRaises(ValueError):
            PublicPyOptixParticleOwner.prepare(
                prebuilt_ptx=b".version 8.0\n", vertices=vertices,
                triangles=triangles, front_values=front, back_values=back,
                shape=shape, runtime=runtime)
        with self.assertRaisesRegex(ValueError, "embedded NUL"):
            PublicPyOptixParticleOwner.prepare(
                prebuilt_ptx=_ptx() + b"\0unconsumed-tail",
                vertices=vertices, triangles=triangles,
                front_values=front, back_values=back,
                shape=shape, runtime=runtime)
        with self.assertRaisesRegex(ValueError, "entrypoint set differs"):
            PublicPyOptixParticleOwner.prepare(
                prebuilt_ptx=(
                    _ptx()
                    + b".visible .entry __anyhit__attacker() {}\n"),
                vertices=vertices, triangles=triangles,
                front_values=front, back_values=back,
                shape=shape, runtime=runtime)
        with self.assertRaises(ValueError):
            PublicPyOptixParticleOwner.prepare(
                prebuilt_ptx=_ptx(), vertices=vertices[:, ::-1],
                triangles=triangles, front_values=front, back_values=back,
                shape=shape, runtime=runtime)

    def test_source_boundary_has_no_rtdl_loader_compiler_timer_or_receipt(self):
        source = OWNER_SOURCE.read_text(encoding="utf-8")
        required = (
            "context.moduleCreate(", "context.programGroupCreate(",
            "context.pipelineCreate(", "optix.BuildInputTriangleArray()",
            "context.accelBuild(", "self.runtime.optix.launch(",
            "np.array_equal(output, expected)",
            "def execute_complete_soa(",
            "def execute_complete_matrix_convenience(",
        )
        for token in required:
            self.assertIn(token, source)
        forbidden = (
            "ctypes.CDLL", "rtdl_optix_v4_prepare",
            "rtdl_optix_v4_execute", "rtdl_optix_v4_destroy",
            "src.rtdsl", "import rtdsl", "cuda.bindings.nvrtc",
            "import time", "perf_counter", "import json", "import hashlib",
            "receipt",
        )
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
