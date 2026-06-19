from __future__ import annotations

import ctypes
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np
import rtdsl
from rtdsl import optix_runtime as optix
from rtdsl import v4_0_device_array_operator as v4


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json"
PARITY_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_parity_matrix_2026-06-19.json"
NO_HOST_STAGE_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json"
)
BENCHMARK_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_benchmark_probe_2026-06-19.json"
STREAM_ORDERING_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_cupy_stream_ordering_probe_2026-06-19.json"
)
NUMBA_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_numba_cuda_array_interface_smoke_2026-06-19.json"
NUMBA_PARTNER_SURFACE_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_numba_partner_surface_probe_2026-06-19.json"
)
DLPACK_REPORT = ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_dlpack_bridge_smoke_2026-06-19.json"
DLPACK_CAPSULE_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_dlpack_capsule_probe_2026-06-19.json"
)
PYTORCH_REPORT = (
    ROOT / "docs" / "reports" / "v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe_2026-06-19.json"
)
SMOKE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_stream_smoke.py"
PARITY_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_parity_matrix.py"
NO_HOST_STAGE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_no_host_stage_probe.py"
BENCHMARK_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_benchmark_probe.py"
STREAM_ORDERING_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_cupy_stream_ordering_probe.py"
NUMBA_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_numba_cuda_array_interface_smoke.py"
NUMBA_PARTNER_SURFACE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_numba_partner_surface_probe.py"
DLPACK_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_dlpack_bridge_smoke.py"
DLPACK_CAPSULE_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_dlpack_capsule_probe.py"
PYTORCH_SCRIPT = ROOT / "scripts" / "v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe.py"
CLAIM_REVIEW = ROOT / "docs" / "reviews" / "codex_v4_m1_true_zero_copy_claim_review_2026-06-19.md"
WORDING_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_m1_true_zero_copy_wording_consensus_2026-06-19.md"
)
NUMBA_SURFACE_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_v4_m1_numba_surface_2ai_consensus_2026-06-19.md"
)
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class _FakeCudaColumn:
    def __init__(
        self,
        ptr: int,
        *,
        dtype: str,
        shape: tuple[int, ...],
        strides: tuple[int, ...] | None = None,
        stream: int = 0,
    ) -> None:
        self._ptr = int(ptr)
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self.__cuda_array_interface__ = {
            "version": 3,
            "shape": shape,
            "typestr": dtype,
            "data": (self._ptr, False),
            "strides": strides,
            "stream": stream,
        }


class _FakeGradTorchTensorWithExplodingCudaArrayInterface:
    __module__ = "torch.fake"

    def __init__(
        self,
        ptr: int,
        *,
        dtype: str,
        shape: tuple[int, ...],
        strides: tuple[int, ...] | None = None,
    ) -> None:
        self._ptr = int(ptr)
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self.requires_grad = True
        self.cuda_array_interface_reads = 0

    def data_ptr(self) -> int:
        return self._ptr

    def __dlpack_device__(self) -> tuple[int, int]:
        return (2, 0)

    def __dlpack__(self):
        raise AssertionError("grad-enabled torch tensors must be rejected before __dlpack__ export")

    @property
    def __cuda_array_interface__(self):
        self.cuda_array_interface_reads += 1
        raise RuntimeError("grad-enabled torch tensors should not be probed through CAI")


class _FakeTorchCudaColumn:
    __module__ = "torch.fake"

    def __init__(
        self,
        ptr: int,
        *,
        dtype: str,
        shape: tuple[int, ...],
        stride: tuple[int, ...],
        requires_grad: bool = False,
    ) -> None:
        self._ptr = int(ptr)
        self.dtype = dtype
        self.shape = shape
        self._stride = stride
        self.requires_grad = requires_grad

    def data_ptr(self) -> int:
        return self._ptr

    def stride(self) -> tuple[int, ...]:
        return self._stride

    def __dlpack_device__(self) -> tuple[int, int]:
        return (2, 0)

    def __dlpack__(self):
        raise AssertionError("torch data_ptr path should not need __dlpack__")


class _FakeTorchStream:
    def __init__(self, cuda_stream: int) -> None:
        self.cuda_stream = int(cuda_stream)


class _TestDLDevice(ctypes.Structure):
    _fields_ = [("device_type", ctypes.c_int), ("device_id", ctypes.c_int)]


class _TestDLDataType(ctypes.Structure):
    _fields_ = [("code", ctypes.c_uint8), ("bits", ctypes.c_uint8), ("lanes", ctypes.c_uint16)]


class _TestDLTensor(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.c_void_p),
        ("device", _TestDLDevice),
        ("ndim", ctypes.c_int32),
        ("dtype", _TestDLDataType),
        ("shape", ctypes.POINTER(ctypes.c_int64)),
        ("strides", ctypes.POINTER(ctypes.c_int64)),
        ("byte_offset", ctypes.c_uint64),
    ]


class _TestDLManagedTensor(ctypes.Structure):
    pass


_TestDLManagedTensor._fields_ = [
    ("dl_tensor", _TestDLTensor),
    ("manager_ctx", ctypes.c_void_p),
    ("deleter", ctypes.c_void_p),
]


_TEST_DLPACK_DELETER = ctypes.CFUNCTYPE(None, ctypes.POINTER(_TestDLManagedTensor))
_TEST_PY_CAPSULE_NEW = ctypes.pythonapi.PyCapsule_New
_TEST_PY_CAPSULE_NEW.restype = ctypes.py_object
_TEST_PY_CAPSULE_NEW.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
_NO_DLPACK_STREAM_ARGUMENT = object()


class _FakeDLPackCapsuleColumn:
    """A capsule-only CUDA column for V4 DLPack lifetime tests."""

    def __init__(
        self,
        ptr: int,
        *,
        dtype: str,
        shape: tuple[int, ...],
        strides: tuple[int, ...] | None = None,
        declared_device: tuple[int, int] = (2, 0),
        capsule_device: tuple[int, int] | None = None,
        return_same_capsule: bool = False,
        no_deleter: bool = False,
        dtype_lanes: int = 1,
    ) -> None:
        self._ptr = int(ptr)
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self.declared_device = declared_device
        self.capsule_device = declared_device if capsule_device is None else capsule_device
        self.return_same_capsule = return_same_capsule
        self.no_deleter = no_deleter
        self.dtype_lanes = int(dtype_lanes)
        self.requested_streams: list[int | str] = []
        self.deleter_calls = 0
        self._records: list[object] = []
        self._shared_capsule = None

    def __dlpack_device__(self):
        return self.declared_device

    def __dlpack__(self, stream=_NO_DLPACK_STREAM_ARGUMENT):
        if stream is _NO_DLPACK_STREAM_ARGUMENT:
            self.requested_streams.append("no_arg")
        else:
            self.requested_streams.append(int(stream) if stream is not None else "none")
        if self.return_same_capsule and self._shared_capsule is not None:
            return self._shared_capsule
        capsule = self._new_capsule()
        if self.return_same_capsule:
            self._shared_capsule = capsule
        return capsule

    def _new_capsule(self):
        shape_array = (ctypes.c_int64 * len(self.shape))(*[int(dim) for dim in self.shape])
        strides_array = None
        if self.strides is not None:
            strides_array = (ctypes.c_int64 * len(self.strides))(*[int(stride) for stride in self.strides])
        managed = _TestDLManagedTensor()
        managed.dl_tensor.data = ctypes.c_void_p(self._ptr)
        managed.dl_tensor.device = _TestDLDevice(int(self.capsule_device[0]), int(self.capsule_device[1]))
        managed.dl_tensor.ndim = len(self.shape)
        managed.dl_tensor.dtype = self._dtype()
        managed.dl_tensor.shape = ctypes.cast(shape_array, ctypes.POINTER(ctypes.c_int64))
        managed.dl_tensor.strides = (
            ctypes.cast(strides_array, ctypes.POINTER(ctypes.c_int64))
            if strides_array is not None
            else ctypes.POINTER(ctypes.c_int64)()
        )
        managed.dl_tensor.byte_offset = 0

        def _deleter(_managed):
            self.deleter_calls += 1

        callback = _TEST_DLPACK_DELETER(_deleter)
        managed.deleter = None if self.no_deleter else ctypes.cast(callback, ctypes.c_void_p).value
        managed_ptr = ctypes.pointer(managed)
        capsule = _TEST_PY_CAPSULE_NEW(
            ctypes.cast(managed_ptr, ctypes.c_void_p),
            b"dltensor",
            None,
        )
        self._records.append(
            SimpleNamespace(
                shape_array=shape_array,
                strides_array=strides_array,
                managed=managed,
                managed_ptr=managed_ptr,
                callback=callback,
                capsule=capsule,
            )
        )
        return capsule

    def _dtype(self) -> _TestDLDataType:
        if self.dtype.startswith("uint"):
            return _TestDLDataType(1, int(self.dtype.removeprefix("uint")), self.dtype_lanes)
        if self.dtype.startswith("int"):
            return _TestDLDataType(0, int(self.dtype.removeprefix("int")), self.dtype_lanes)
        if self.dtype.startswith("float"):
            return _TestDLDataType(2, int(self.dtype.removeprefix("float")), self.dtype_lanes)
        if self.dtype == "double":
            return _TestDLDataType(2, 64, self.dtype_lanes)
        raise ValueError(f"unsupported fake DLPack dtype {self.dtype!r}")


class _FakePrepared:
    def __init__(self, *, prepare_stream_ptr: int = 0) -> None:
        self.closed = False
        self.on_stream_call = None
        self.prepare_stream_ptr = int(prepare_stream_ptr)

    def close(self) -> None:
        self.closed = True

    def write_device_count_threshold_columns_on_stream(self, query_point_columns, **kwargs):
        self.on_stream_call = {"query_point_columns": query_point_columns, **kwargs}
        query_stream_ptr = int(kwargs["cuda_stream_ptr"])
        prepare_query_streams_differ = self.prepare_stream_ptr != query_stream_ptr
        pointer_echo = {f"query.{name}": int(column._ptr) for name, column in query_point_columns.items()}
        pointer_echo.update(
            {
                "output.query_ids": int(kwargs["query_ids_out"]._ptr),
                "output.neighbor_counts": int(kwargs["neighbor_counts_out"]._ptr),
                "output.threshold_flags": int(kwargs["threshold_flags_out"]._ptr),
            }
        )
        return {
            "metadata": {
                "native_symbol": "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream",
                "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy_on_stream",
                "cuda_stream_ptr": int(kwargs["cuda_stream_ptr"]),
                "native_call_device_pointer_echo": pointer_echo,
                "native_call_device_pointer_echo_complete": True,
                "prepare_stream_ptr": self.prepare_stream_ptr,
                "prepare_query_streams_differ": prepare_query_streams_differ,
                "native_prepare_ready_event_recorded": True,
                "native_prepare_ready_event_wait_ready": True,
                "native_prepare_ready_event_wait_used": prepare_query_streams_differ,
                "named_cuda_columns_no_host_stage_authorized": True,
                "named_cuda_columns_no_host_stage_ready": True,
                "internal_device_staging_disclosed": True,
                "internal_device_staging_scope": "device-resident AABB/BVH staging may occur inside the native route",
                "native_synchronized_before_return": True,
                "native_async_ready": False,
                "true_zero_copy_authorized": True,
            }
        }


def _point_columns(base: int, *, count: int = 3, x_dtype: str = "float64"):
    return {
        "ids": _FakeCudaColumn(base + 0x10, dtype="uint32", shape=(count,), strides=(4,)),
        "x": _FakeCudaColumn(base + 0x20, dtype=x_dtype, shape=(count,), strides=(8,)),
        "y": _FakeCudaColumn(base + 0x30, dtype="float64", shape=(count,), strides=(8,)),
    }


def _dlpack_point_columns(
    base: int,
    *,
    count: int = 3,
    x_dtype: str = "float64",
    x_shape: tuple[int, ...] | None = None,
    x_strides: tuple[int, ...] | None = (1,),
    y_device: tuple[int, int] = (2, 0),
):
    return {
        "ids": _FakeDLPackCapsuleColumn(base + 0x10, dtype="uint32", shape=(count,), strides=(1,)),
        "x": _FakeDLPackCapsuleColumn(
            base + 0x20,
            dtype=x_dtype,
            shape=(count,) if x_shape is None else x_shape,
            strides=x_strides,
        ),
        "y": _FakeDLPackCapsuleColumn(
            base + 0x30,
            dtype="float64",
            shape=(count,),
            strides=(1,),
            declared_device=y_device,
        ),
    }


def _output_columns(base: int, *, count: int = 3):
    return {
        "query_ids": _FakeCudaColumn(base + 0x10, dtype="uint32", shape=(count,), strides=(4,)),
        "neighbor_counts": _FakeCudaColumn(base + 0x20, dtype="uint32", shape=(count,), strides=(4,)),
        "threshold_flags": _FakeCudaColumn(base + 0x30, dtype="uint32", shape=(count,), strides=(4,)),
    }


def _dlpack_output_columns(base: int, *, count: int = 3):
    return {
        "query_ids": _FakeDLPackCapsuleColumn(base + 0x10, dtype="uint32", shape=(count,), strides=(1,)),
        "neighbor_counts": _FakeDLPackCapsuleColumn(base + 0x20, dtype="uint32", shape=(count,), strides=(1,)),
        "threshold_flags": _FakeDLPackCapsuleColumn(base + 0x30, dtype="uint32", shape=(count,), strides=(1,)),
    }


def _host_point_columns(count: int = 3):
    return {
        "ids": np.arange(count, dtype=np.uint32),
        "x": np.arange(count, dtype=np.float64),
        "y": np.arange(count, dtype=np.float64),
    }


def _clone_handoff(handoff, **overrides):
    values = {
        "data_ptr": handoff.data_ptr,
        "dtype": handoff.dtype,
        "shape": handoff.shape,
        "strides": handoff.strides,
        "device_type": handoff.device_type,
        "device_id": handoff.device_id,
        "access_mode": handoff.access_mode,
        "source_protocol": handoff.source_protocol,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class V40M1FixedRadiusRouteTest(unittest.TestCase):
    def test_route_descriptor_freezes_fixed_radius_count_threshold_2d(self) -> None:
        route = rtdsl.describe_v4_fixed_radius_count_threshold_2d_route()

        self.assertEqual(route["scope"], "python_gpu_rt_core_operator")
        self.assertEqual(route["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(route["backend"], "optix")
        self.assertEqual(route["output_shape"], "fixed one row per query, no variable neighbor rows")
        self.assertEqual(route["supported_input_protocols"], ("cuda_array_interface", "cupy"))
        self.assertEqual(route["evidence_backed_frameworks"], ("cupy", "numba", "pytorch"))
        self.assertEqual(route["experimental_input_protocols"], ("dlpack_bridge_wrapper", "legacy_dlpack_capsule"))
        self.assertIn("dlpack", route["target_input_protocols"])
        self.assertIn("pytorch", route["target_frameworks"])
        self.assertIn("full_dlpack_capsule", route["blocked_input_protocols_without_full_route_evidence"])
        self.assertNotIn("pytorch", route["blocked_frameworks_without_route_evidence"])
        self.assertIn("jax", route["blocked_frameworks_without_route_evidence"])
        self.assertTrue(route["native_stream_propagation_ready"])
        self.assertTrue(route["native_prepare_stream_propagation_ready"])
        self.assertTrue(route["cross_stream_event_wait_ready"])
        self.assertEqual(route["cross_stream_status"], "fixed_radius_m1_prepare_ready_event_wait_supported_synchronous")
        self.assertEqual(
            route["cross_stream_prepare_query_policy"],
            "fixed_radius_m1_prepare_ready_event_wait_when_prepare_and_query_streams_differ",
        )
        self.assertEqual(route["cross_stream_event_wait_scope"], "fixed_radius_m1_prepare_query_only")
        self.assertFalse(route["native_async_ready"])
        self.assertFalse(route["v4_true_zero_copy_claim_authorized"])
        self.assertIn("variable_length_neighbor_rows", route["blocked_generalizations"])
        self.assertIn("ray_triangle_any_hit", route["blocked_generalizations"])
        self.assertIn("full_pytorch_partner_surface", route["blocked_generalizations"])
        self.assertIn("dlpack_route_support", route["blocked_generalizations"])
        self.assertIn("general_cross_stream_event_wait", route["blocked_generalizations"])
        self.assertIn("full_external_stream_ownership", route["blocked_generalizations"])

    def test_plan_captures_borrowed_pointers_and_producer_streams(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        query["x"] = _FakeCudaColumn(0x2020, dtype="float64", shape=(3,), strides=(8,), stream=77)

        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            output_columns=outputs,
        )
        metadata = plan.to_metadata()

        self.assertEqual(metadata["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(metadata["query_count"], 3)
        self.assertEqual(metadata["search_count"], 3)
        self.assertEqual(metadata["borrowed_device_pointers"]["search.x"], 0x1020)
        self.assertEqual(metadata["borrowed_device_pointers"]["query.x"], 0x2020)
        self.assertEqual(metadata["descriptors"]["query.x"]["producer_stream_handle"], 77)
        self.assertEqual(metadata["output_contract"], "caller_owned_cuda_output_columns")

    def test_plan_accepts_torch_cuda_stream_objects(self) -> None:
        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            _point_columns(0x2000),
            _point_columns(0x1000),
            output_columns=_output_columns(0x3000),
            stream=_FakeTorchStream(456),
            prepare_stream=_FakeTorchStream(123),
        )

        metadata = plan.to_metadata()
        self.assertEqual(metadata["caller_stream_handle"], 456)
        self.assertEqual(metadata["prepare_stream_handle"], 123)
        self.assertTrue(metadata["native_prepare_ready_event_wait_required"])

    def test_dlpack_capsule_lease_consumes_capsule_and_calls_deleter_once(self) -> None:
        column = _FakeDLPackCapsuleColumn(
            0xCAFE,
            dtype="uint32",
            shape=(4,),
            strides=(1,),
            return_same_capsule=True,
        )

        lease = rtdsl.acquire_dlpack_capsule_lease(column, stream=99)
        self.assertIsInstance(lease, rtdsl.RtdlDLPackCapsuleLease)
        self.assertEqual(lease.data_ptr, 0xCAFE)
        self.assertEqual(lease.device_type, "cuda")
        self.assertEqual(lease.device_id, 0)
        self.assertEqual(lease.dtype, "uint32")
        self.assertEqual(lease.shape, (4,))
        self.assertEqual(lease.strides, (1,))
        self.assertEqual(lease.requested_stream, 99)
        self.assertEqual(column.requested_streams, [99])

        with self.assertRaisesRegex(ValueError, "already been consumed"):
            rtdsl.acquire_dlpack_capsule_lease(column, stream=99)
        lease.release()
        lease.release()
        self.assertEqual(column.deleter_calls, 1)

    def test_dlpack_handoff_rejects_non_cuda_mismatched_device_and_bad_deleter(self) -> None:
        cpu_column = _FakeDLPackCapsuleColumn(0x1000, dtype="uint32", shape=(1,), declared_device=(1, 0))
        with self.assertRaisesRegex(ValueError, "requires a CUDA capsule"):
            rtdsl.prepare_dlpack_device_pointer_handoff(cpu_column)
        self.assertEqual(cpu_column.deleter_calls, 1)

        mismatched = _FakeDLPackCapsuleColumn(
            0x2000,
            dtype="uint32",
            shape=(1,),
            declared_device=(2, 0),
            capsule_device=(2, 1),
        )
        with self.assertRaisesRegex(ValueError, "must match __dlpack_device__"):
            rtdsl.acquire_dlpack_capsule_lease(mismatched)

        no_deleter = _FakeDLPackCapsuleColumn(0x3000, dtype="uint32", shape=(1,), no_deleter=True)
        with self.assertRaisesRegex(ValueError, "deleter must not be null"):
            rtdsl.acquire_dlpack_capsule_lease(no_deleter)

    def test_plan_uses_real_dlpack_capsule_path_and_retains_lease_owners(self) -> None:
        search = _dlpack_point_columns(0x1000)
        query = _dlpack_point_columns(0x2000)
        outputs = _dlpack_output_columns(0x3000)

        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            output_columns=outputs,
            stream=456,
            prepare_stream=123,
        )
        metadata = plan.to_metadata()

        self.assertEqual(metadata["source_protocols"], ("dlpack",))
        self.assertEqual(metadata["borrowed_device_pointers"]["search.x"], 0x1020)
        self.assertEqual(metadata["borrowed_device_pointers"]["query.x"], 0x2020)
        self.assertEqual(metadata["borrowed_device_pointers"]["output.neighbor_counts"], 0x3020)
        self.assertIsInstance(plan.search_columns["ids"].owner, rtdsl.RtdlDLPackCapsuleLease)
        self.assertIsInstance(plan.query_columns["x"].owner, rtdsl.RtdlDLPackCapsuleLease)
        self.assertIsInstance(plan.output_columns["threshold_flags"].owner, rtdsl.RtdlDLPackCapsuleLease)
        self.assertEqual([column.requested_streams for column in search.values()], [[123], [123], [123]])
        self.assertEqual([column.requested_streams for column in query.values()], [[456], [456], [456]])
        self.assertEqual([column.requested_streams for column in outputs.values()], [[456], [456], [456]])

        for descriptor in (
            *plan.search_columns.values(),
            *plan.query_columns.values(),
            *plan.output_columns.values(),
        ):
            descriptor.owner.release()

    def test_pytorch_grad_tensor_rejection_does_not_probe_cuda_array_interface(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        grad_column = _FakeGradTorchTensorWithExplodingCudaArrayInterface(
            0x2020,
            dtype="float64",
            shape=(3,),
            strides=(8,),
        )
        query["x"] = grad_column

        with self.assertRaisesRegex(ValueError, "grad-enabled PyTorch tensors"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=outputs)

        self.assertEqual(grad_column.cuda_array_interface_reads, 0)

    def test_pytorch_stride_method_rejects_noncontiguous_views(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        query["x"] = _FakeTorchCudaColumn(
            0x2020,
            dtype="float64",
            shape=(3,),
            stride=(2,),
        )

        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must be contiguous"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=outputs)

    def test_dlpack_capsule_route_fails_closed_for_dtype_rank_stride_and_device(self) -> None:
        cases = (
            (
                "dtype",
                _dlpack_point_columns(0x2000, x_dtype="float32"),
                "V4 query column 'x' must use dtype",
            ),
            (
                "rank",
                _dlpack_point_columns(0x2000, x_shape=(3, 1), x_strides=(1, 1)),
                "V4 query column 'x' must be one-dimensional",
            ),
            (
                "stride",
                _dlpack_point_columns(0x2000, x_strides=(2,)),
                "V4 query column 'x' must be contiguous",
            ),
            (
                "device",
                _dlpack_point_columns(0x2000, y_device=(2, 1)),
                "V4 query columns must live on the same CUDA device",
            ),
        )
        for name, query, message in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, message):
                    rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                        query,
                        _dlpack_point_columns(0x1000),
                        output_columns=_dlpack_output_columns(0x3000),
                        stream=456,
                        prepare_stream=123,
                    )

    def test_optix_fixed_radius_packer_accepts_capsule_only_dlpack_columns_on_stream(self) -> None:
        columns = _dlpack_point_columns(0x4000)

        packet = optix.pack_optix_fixed_radius_count_threshold_2d_device_point_inputs(
            columns,
            label="query",
            native_symbol="test_symbol",
            dlpack_stream=777,
        )

        self.assertEqual(packet["metadata"]["source_protocols"], ("dlpack",))
        self.assertEqual(packet["metadata"]["point_count"], 3)
        self.assertEqual(packet["points"]["x"].data_ptr, 0x4020)
        self.assertEqual([column.requested_streams for column in columns.values()], [[777], [777], [777]])
        for handoff in packet["points"].values():
            handoff.descriptor.owner.release()

    def test_plan_fails_closed_for_wrong_dtype_and_captures_caller_stream(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000, x_dtype="float32")
        outputs = _output_columns(0x3000)

        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must use dtype"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=outputs)

        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            _point_columns(0x2000),
            search,
            output_columns=outputs,
            stream=123,
        )
        self.assertEqual(plan.to_metadata()["caller_stream_handle"], 123)
        self.assertEqual(plan.to_metadata()["prepare_stream_handle"], 123)
        self.assertTrue(plan.to_metadata()["caller_stream_native_propagation_ready"])
        self.assertTrue(plan.to_metadata()["native_prepare_stream_propagation_ready"])
        self.assertTrue(plan.to_metadata()["cross_stream_event_wait_ready"])
        self.assertFalse(plan.to_metadata()["native_prepare_ready_event_wait_required"])

    def test_plan_fails_closed_for_host_arrays_bad_rank_and_noncontiguous_stride(self) -> None:
        search = _point_columns(0x1000)
        outputs = _output_columns(0x3000)

        with self.assertRaisesRegex(ValueError, "requires a CUDA"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                _host_point_columns(),
                search,
                output_columns=outputs,
            )

        bad_rank = _point_columns(0x2000)
        bad_rank["x"] = _FakeCudaColumn(0x2020, dtype="float64", shape=(3, 1), strides=(8, 8))
        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must be one-dimensional"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(bad_rank, search, output_columns=outputs)

        noncontiguous = _point_columns(0x2000)
        noncontiguous["x"] = _FakeCudaColumn(0x2020, dtype="float64", shape=(3,), strides=(16,))
        with self.assertRaisesRegex(ValueError, "V4 query column 'x' must be contiguous"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(noncontiguous, search, output_columns=outputs)

    def test_plan_fails_closed_for_bad_output_contracts(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)

        wrong_count = _output_columns(0x3000, count=2)
        with self.assertRaisesRegex(ValueError, "V4 output columns must have matching lengths"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=wrong_count)

        wrong_dtype = _output_columns(0x3000)
        wrong_dtype["neighbor_counts"] = _FakeCudaColumn(0x3020, dtype="int32", shape=(3,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "V4 output column 'neighbor_counts' must use dtype"):
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=wrong_dtype)

    def test_plan_records_cross_stream_prepare_query_event_wait_requirement(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)

        plan = rtdsl.plan_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            output_columns=outputs,
            stream=456,
            prepare_stream=123,
        )
        metadata = plan.to_metadata()

        self.assertEqual(metadata["caller_stream_handle"], 456)
        self.assertEqual(metadata["prepare_stream_handle"], 123)
        self.assertTrue(metadata["prepare_query_streams_differ"])
        self.assertTrue(metadata["native_prepare_ready_event_wait_required"])
        self.assertTrue(metadata["cross_stream_event_wait_ready"])
        self.assertEqual(
            metadata["cross_stream_prepare_query_policy"],
            "fixed_radius_m1_prepare_ready_event_wait_when_prepare_and_query_streams_differ",
        )

    def test_native_fixed_radius_prepare_handle_owns_event_wait_contract(self) -> None:
        native = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        for token in (
            "CUevent prepare_ready_event",
            "CUstream prepare_stream",
            "cuEventCreate(&prepare_ready_event, CU_EVENT_DISABLE_TIMING)",
            "cuEventRecord(prepare_ready_event, stream)",
            "cuStreamWaitEvent(stream, prepared->prepare_ready_event, 0)",
            "cuEventDestroy(prepare_ready_event)",
        ):
            self.assertIn(token, native)

    def test_plan_fails_closed_for_mixed_devices(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        original = v4._partner.prepare_direct_device_pointer_handoff

        def fake_handoff(obj, *, access="read"):
            handoff = original(obj, access=access)
            if obj is query["y"]:
                return _clone_handoff(handoff, device_id=1)
            return handoff

        with mock.patch.object(v4._partner, "prepare_direct_device_pointer_handoff", side_effect=fake_handoff):
            with self.assertRaisesRegex(ValueError, "V4 query columns must live on the same CUDA device"):
                rtdsl.plan_v4_fixed_radius_count_threshold_2d(query, search, output_columns=outputs)

    def test_operator_wraps_existing_prepared_optix_device_column_route(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        prepared = _FakePrepared()
        native_result = {
            "columns": outputs,
            "metadata": {
                "adapter": "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns",
                "true_zero_copy_authorized": True,
                "native_metadata": {
                    "native_symbol": "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns",
                    "true_zero_copy_authorized": True,
                },
            },
        }

        with mock.patch.object(v4, "_prepare_scene", return_value=prepared) as prepare_scene, mock.patch.object(
            v4,
            "_run_prepared",
            return_value=native_result,
        ) as run_prepared:
            with rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
                search,
                max_radius=2.0,
                partner="cupy",
            ) as operator:
                result = operator.run(
                    query,
                    radius=1.5,
                    threshold=2,
                    output_columns=outputs,
                    return_metadata=True,
                )

        prepare_scene.assert_called_once()
        run_prepared.assert_called_once()
        self.assertTrue(prepared.closed)
        self.assertIs(result["columns"], outputs)
        metadata = result["metadata"]
        self.assertEqual(metadata["v4_route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(metadata["v4_backend"], "optix")
        self.assertTrue(metadata["native_true_zero_copy_authorized"])
        self.assertFalse(metadata["v4_true_zero_copy_claim_authorized"])
        self.assertEqual(
            metadata["v4_true_zero_copy_claim_blocker"],
            "public_true_zero_copy_wording_blocked_by_internal_device_staging_and_sync_contract",
        )

    def test_cupy_stream_smoke_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(EVIDENCE_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertRegex(report["code_commit"], r"^[0-9a-f]{9}$")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["build_optix"], "pass")
        self.assertEqual(report["validation"]["cupy_stream_smoke"], "pass")
        self.assertIn(
            "PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py",
            report["commands"],
        )
        self.assertEqual(report["cupy_stream_smoke_observed"]["neighbor_counts"], [1, 1, 0])
        self.assertTrue(all(report["pointer_identity"].values()))
        self.assertTrue(all(report["pointer_echo_identity"].values()))
        self.assertTrue(all(report["source_audit"].values()))
        self.assertTrue(all(report["promotion_blockers"].values()))
        self.assertFalse(report["route"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_parity_matrix_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(PARITY_REPORT.read_text(encoding="utf-8"))
        script = PARITY_SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertRegex(report["code_commit"], r"^[0-9a-f]{9}$")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["cupy_parity_matrix"], "pass")
        self.assertEqual(report["parity_matrix"]["case_count"], 5)
        self.assertEqual(report["parity_matrix"]["pass_count"], 5)
        self.assertEqual(report["fail_closed_matrix"]["case_count"], 1)
        self.assertEqual(report["fail_closed_matrix"]["pass_count"], 1)
        self.assertTrue(all(row["passed"] for row in report["parity_matrix"]["cases"]))
        self.assertTrue(all(row["passed"] for row in report["fail_closed_matrix"]["cases"]))
        self.assertIn("boundary_inclusive", {row["name"] for row in report["parity_matrix"]["cases"]})
        self.assertIn("random_seed_7", {row["name"] for row in report["parity_matrix"]["cases"]})
        self.assertIn("empty_query_zero_length_cupy_columns_fail_closed", script)
        self.assertFalse(report["claim_boundaries"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_no_host_stage_report_preserves_claim_boundaries(self) -> None:
        report = json.loads(NO_HOST_STAGE_REPORT.read_text(encoding="utf-8"))
        script = NO_HOST_STAGE_SCRIPT.read_text(encoding="utf-8")
        classification = report["transfer_counter_classification"]

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertRegex(report["code_commit"], r"^[0-9a-f]{9}$")
        self.assertEqual(report["route"]["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["validation"]["cupy_no_host_stage_probe"], "pass")
        self.assertTrue(classification["transfer_counter_observed"])
        self.assertTrue(classification["no_host_stage_ready"])
        self.assertFalse(classification["host_stage_observed"])
        self.assertEqual(classification["observed_device_to_host_calls"], 0)
        self.assertEqual(classification["observed_unknown_calls"], 0)
        self.assertLess(
            classification["observed_host_to_device_bytes"],
            classification["min_named_column_bytes"],
        )
        self.assertTrue(classification["internal_device_to_device_copy_allowed"])
        self.assertFalse(classification["v4_true_zero_copy_claim_authorized"])
        self.assertTrue(report["metadata_subset"]["named_cuda_columns_no_host_stage_authorized"])
        self.assertTrue(report["metadata_subset"]["internal_device_staging_disclosed"])
        self.assertIn("LD_PRELOAD", script)
        self.assertIn("v4_m1_fixed_radius_prepare_plus_query_after_warmup", script)
        self.assertFalse(report["claim_boundaries"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])

    def test_cupy_stream_smoke_script_is_reproducible_route_gate(self) -> None:
        script = SMOKE_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "run_v4_fixed_radius_count_threshold_2d",
            "cp.cuda.Stream(non_blocking=True)",
            "pointer_identity",
            "pointer_echo_identity",
            "native_call_device_pointer_echo",
            "named_cuda_columns_no_host_stage_authorized",
            "internal_device_staging_disclosed",
            "source_audit",
            "promotion_blockers",
            "prepare_on_stream_symbol_present",
            "if not all(result[\"source_audit\"].values())",
            "native_async_ready",
            "v4_true_zero_copy_claim_authorized",
        ):
            self.assertIn(token, script)

    def test_cupy_benchmark_probe_keeps_speed_claims_blocked(self) -> None:
        script = BENCHMARK_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "v4_one_shot_prepare_plus_query",
            "v4_prepared_query_only",
            "cupy_bruteforce_cuda_core_baseline",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "False",
            "baseline_limitations",
            "not authorize public speedup wording",
        ):
            self.assertIn(token, script)

    def test_cupy_benchmark_report_records_raw_timings_without_speed_claims(self) -> None:
        report = json.loads(BENCHMARK_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["remote_validation"]["v4_active"]["test_count"], 31)
        self.assertTrue(report["validation"]["output_match"])
        self.assertIn("v4_one_shot_prepare_plus_query", report["median_seconds"])
        self.assertIn("v4_prepared_query_only", report["median_seconds"])
        self.assertIn("cupy_bruteforce_cuda_core_baseline", report["median_seconds"])
        self.assertIn("baseline_over_v4_prepared_query", report["raw_ratios"])
        self.assertFalse(report["hardware"]["rt_core_hardware"])
        self.assertEqual(report["rtx_pod_access"]["result"], "blocked")
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["async_claim_authorized"])
        self.assertIn("not a best-known tuned", report["claim_boundaries"]["baseline_limitations"])
        self.assertIn("raw timing", report["claim_boundaries"]["allowed_wording"])
        self.assertIn("RT-core speedup", report["claim_boundaries"]["forbidden_wording"])

    def test_cupy_stream_ordering_probe_is_same_stream_only_and_claim_bounded(self) -> None:
        script = STREAM_ORDERING_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "same_nondefault_cupy_stream_producer_rtdl_consumer",
            "cross_stream_prepare_query_contract",
            "prepare_stream = cp.cuda.Stream",
            "query_stream = cp.cuda.Stream",
            "producer_event.record(stream)",
            "consumer_event.record(stream)",
            "prepare_input_event.record(prepare_stream)",
            "cross_consumer_event.record(query_stream)",
            "native_prepare_ready_event_wait_used",
            "producer_rtdl_consumer_order_validated",
            "cross_stream_event_wait_validated",
            "cross_stream_event_wait_claim_authorized",
            "general_cross_stream_event_wait_claim_authorized",
            "full_external_stream_ownership_claim_authorized",
            "async_claim_authorized",
            "public_speedup_claim_authorized",
            "v4_true_zero_copy_claim_authorized",
            "False",
            "not authorize async, full external stream ownership",
        ):
            self.assertIn(token, script)

    def test_cupy_stream_ordering_report_allows_same_stream_only(self) -> None:
        report = json.loads(STREAM_ORDERING_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertTrue(report["remote_validation"]["build_optix"]["ok"])
        self.assertTrue(report["remote_validation"]["source_tree_doctor"]["ok"])
        self.assertTrue(report["remote_validation"]["source_tree_doctor"]["include_v4_active"])
        self.assertTrue(report["remote_validation"]["v4_active"]["ok"])
        self.assertEqual(report["remote_validation"]["v4_active"]["test_count"], 53)
        self.assertTrue(report["remote_validation"]["stream_ordering_probe"]["ok"])
        self.assertTrue(report["remote_validation"]["claim_boundary_scan"]["ok"])
        self.assertTrue(report["remote_validation"]["git_diff_check"]["ok"])
        self.assertTrue(report["remote_validation"]["worktree_clean"]["ok"])
        self.assertEqual(report["ordering_scope"], "same_stream_and_cross_stream_prepare_query_event_wait")
        contract = report["same_stream_contract"]
        self.assertEqual(contract["producer_stream_ptr"], contract["rtdl_prepare_stream_ptr"])
        self.assertEqual(contract["producer_stream_ptr"], contract["rtdl_query_stream_ptr"])
        self.assertEqual(contract["producer_stream_ptr"], contract["consumer_stream_ptr"])
        self.assertTrue(contract["producer_rtdl_consumer_order_validated"])
        self.assertFalse(contract["cross_stream_event_wait_validated"])
        self.assertFalse(contract["native_prepare_ready_event_wait_used"])
        cross_contract = report["cross_stream_prepare_query_contract"]
        self.assertNotEqual(cross_contract["prepare_stream_ptr"], cross_contract["query_stream_ptr"])
        self.assertTrue(cross_contract["streams_distinct"])
        self.assertTrue(cross_contract["prepare_query_streams_differ"])
        self.assertTrue(cross_contract["native_prepare_ready_event_recorded"])
        self.assertTrue(cross_contract["native_prepare_ready_event_wait_required"])
        self.assertTrue(cross_contract["native_prepare_ready_event_wait_used"])
        self.assertTrue(cross_contract["native_synchronized_before_return"])
        self.assertTrue(cross_contract["cross_stream_event_wait_validated"])
        self.assertTrue(report["validation"]["output_match"])
        self.assertTrue(report["validation"]["device_consumer_checksum_match"])
        self.assertTrue(report["validation"]["cross_stream_output_match"])
        self.assertTrue(report["validation"]["cross_stream_device_consumer_checksum_match"])
        self.assertEqual(report["validation"]["observed_checksum"], report["validation"]["expected_checksum"])
        self.assertEqual(
            report["validation"]["cross_stream_observed_checksum"],
            report["validation"]["cross_stream_expected_checksum"],
        )
        self.assertFalse(report["metadata_subset"]["native_async_ready"])
        self.assertTrue(report["metadata_subset"]["cross_stream_event_wait_ready"])
        self.assertTrue(report["metadata_subset"]["cross_stream_prepare_query_wait_used"])
        self.assertTrue(report["metadata_subset"]["native_synchronized_before_return"])
        self.assertTrue(report["claim_boundaries"]["same_stream_ordering_claim_authorized"])
        self.assertTrue(
            report["claim_boundaries"]["fixed_radius_m1_cross_stream_prepare_query_event_wait_claim_authorized"]
        )
        self.assertFalse(report["claim_boundaries"]["cross_stream_event_wait_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["general_cross_stream_event_wait_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["full_external_stream_ownership_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["async_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["v4_true_zero_copy_claim_authorized"])
        self.assertIn("full external stream ownership", report["claim_boundaries"]["forbidden_wording"])

    def test_numba_cuda_array_interface_smoke_is_claim_bounded(self) -> None:
        script = NUMBA_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "from numba import cuda",
            "__cuda_array_interface__",
            "source_protocols",
            "cuda_array_interface",
            "numba_device_array_route_claim_authorized",
            "numba_full_partner_surface_claim_authorized",
            "pytorch_route_claim_authorized",
            "dlpack_route_claim_authorized",
            "async_claim_authorized",
            "public_speedup_claim_authorized",
            "v4_true_zero_copy_claim_authorized",
            "False",
            "does not validate a full Numba partner surface",
        ):
            self.assertIn(token, script)

    def test_numba_cuda_array_interface_report_keeps_scope_narrow(self) -> None:
        report = json.loads(NUMBA_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["framework"], "numba")
        self.assertEqual(report["protocol"], "cuda_array_interface")
        self.assertEqual(report["remote_validation"]["v4_active"]["test_count"], 37)
        self.assertTrue(report["validation"]["output_match"])
        self.assertEqual(report["metadata_subset"]["source_protocols"], ["cuda_array_interface"])
        self.assertTrue(report["metadata_subset"]["caller_stream_handle_nonzero"])
        self.assertTrue(report["metadata_subset"]["prepare_stream_handle_nonzero"])
        self.assertFalse(report["metadata_subset"]["native_async_ready"])
        self.assertFalse(report["metadata_subset"]["v4_true_zero_copy_claim_authorized"])
        boundaries = report["claim_boundaries"]
        self.assertTrue(boundaries["numba_device_array_route_claim_authorized"])
        self.assertTrue(boundaries["numba_cuda_array_interface_claim_authorized"])
        self.assertFalse(boundaries["numba_full_partner_surface_claim_authorized"])
        self.assertFalse(boundaries["pytorch_route_claim_authorized"])
        self.assertFalse(boundaries["dlpack_route_claim_authorized"])
        self.assertFalse(boundaries["async_claim_authorized"])
        self.assertFalse(boundaries["public_speedup_claim_authorized"])
        self.assertFalse(boundaries["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundaries["v4_true_zero_copy_claim_authorized"])
        self.assertIn("PyTorch route support", boundaries["forbidden_wording"])
        self.assertIn("DLPack route support", boundaries["forbidden_wording"])

    def test_numba_partner_surface_probe_script_covers_m1_contract(self) -> None:
        script = NUMBA_PARTNER_SURFACE_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "same_nondefault_numba_stream_producer_rtdl_consumer",
            "checksum_kernel[1, 1, stream]",
            "_plan_pointer_matches",
            "_native_pointer_matches",
            "prepare_v4_fixed_radius_count_threshold_2d",
            "caller_kept_search_columns_alive_until_operator_close",
            "Numba search columns are caller-owned borrowed device arrays",
            "numba_m1_devicearray_partner_surface_claim_authorized",
            "numba_full_partner_surface_claim_authorized",
            "all Numba programs are accelerated",
            "cross-stream event wait support",
            "False",
        ):
            self.assertIn(token, script)

    def test_numba_partner_surface_report_is_bounded_and_validated(self) -> None:
        report = json.loads(NUMBA_PARTNER_SURFACE_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["framework"], "numba")
        self.assertEqual(report["protocol"], "cuda_array_interface")
        self.assertEqual(report["remote_validation"]["validated_commit"], report["evidence_code_commit"])
        self.assertTrue(report["remote_validation"]["v4_active"]["ok"])
        self.assertEqual(report["remote_validation"]["v4_active"]["test_count"], 50)
        self.assertTrue(report["remote_validation"]["claim_boundary_scan"]["ok"])
        self.assertTrue(report["remote_validation"]["diff_check"]["ok"])
        self.assertTrue(report["remote_validation"]["worktree_clean"])
        self.assertEqual(report["case_count"], 4)
        self.assertEqual(report["pass_count"], 4)
        self.assertTrue(all(case["passed"] for case in report["cases"]))
        self.assertTrue(all(case["plan_pointer_match_complete"] for case in report["cases"]))
        self.assertTrue(all(case["native_pointer_echo_match_complete"] for case in report["cases"]))
        self.assertTrue(all(case["same_stream_consumer_kernel_checksum_passed"] for case in report["cases"]))
        self.assertTrue(report["pointer_identity"]["plan_pointer_match_complete"])
        self.assertTrue(report["pointer_identity"]["native_pointer_echo_match_complete"])
        self.assertEqual(
            report["same_stream_contract"]["ordering_scope"],
            "same_nondefault_numba_stream_producer_rtdl_consumer",
        )
        self.assertTrue(report["same_stream_contract"]["consumer_checksum_validated"])
        self.assertFalse(report["same_stream_contract"]["cross_stream_event_wait_validated"])
        lifetime = report["prepared_handle_lifetime_contract"]
        self.assertEqual(lifetime["prepared_reuse_run_count"], 2)
        self.assertTrue(lifetime["caller_kept_search_columns_alive_until_operator_close"])
        self.assertTrue(lifetime["search_column_borrowed_pointers_stable_across_runs"])
        self.assertIn("must outlive", lifetime["required_user_rule"])
        boundaries = report["claim_boundaries"]
        self.assertTrue(boundaries["numba_m1_devicearray_partner_surface_claim_authorized"])
        self.assertTrue(boundaries["numba_prepared_reuse_claim_authorized"])
        self.assertFalse(boundaries["numba_full_partner_surface_claim_authorized"])
        self.assertFalse(boundaries["cross_stream_event_wait_claim_authorized"])
        self.assertFalse(boundaries["pytorch_route_claim_authorized"])
        self.assertFalse(boundaries["dlpack_route_claim_authorized"])
        self.assertFalse(boundaries["async_claim_authorized"])
        self.assertFalse(boundaries["v4_true_zero_copy_claim_authorized"])
        self.assertIn("all Numba programs are accelerated", boundaries["forbidden_wording"])
        self.assertIn("full arbitrary Numba partner surface", boundaries["forbidden_wording"])

    def test_numba_surface_consensus_keeps_broad_claim_blocked(self) -> None:
        consensus = NUMBA_SURFACE_CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Keep `full_numba_partner_surface.closed = false`", consensus)
        self.assertIn("Numba `DeviceNDArray` fixed-radius route", consensus)
        self.assertIn("does not authorize broad", consensus)
        self.assertIn("arbitrary Numba program acceleration", consensus)
        self.assertIn("Tighten the blocker manifest", consensus)

    def test_dlpack_bridge_smoke_is_claim_bounded(self) -> None:
        script = DLPACK_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "class DLPackOnlyColumn",
            "__dlpack__",
            "__dlpack_device__",
            "all_wrappers_hide_cuda_array_interface",
            "source_protocols",
            "dlpack_bridge_wrapper_claim_authorized",
            "full_dlpack_capsule_route_claim_authorized",
            "dlpack_route_claim_authorized",
            "pytorch_route_claim_authorized",
            "async_claim_authorized",
            "public_speedup_claim_authorized",
            "v4_true_zero_copy_claim_authorized",
            "False",
            "does not validate arbitrary DLPack capsule",
        ):
            self.assertIn(token, script)

    def test_dlpack_bridge_report_keeps_full_dlpack_and_pytorch_blocked(self) -> None:
        report = json.loads(DLPACK_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["framework"], "cupy_backed_dlpack_only_wrapper")
        self.assertEqual(report["protocol"], "dlpack_bridge_wrapper")
        self.assertTrue(report["validation"]["output_match"])
        self.assertTrue(report["validation"]["all_wrappers_hide_cuda_array_interface"])
        self.assertEqual(report["metadata_subset"]["source_protocols"], ["dlpack"])
        self.assertTrue(report["metadata_subset"]["caller_stream_handle_nonzero"])
        self.assertTrue(report["metadata_subset"]["prepare_stream_handle_nonzero"])
        self.assertFalse(report["metadata_subset"]["native_async_ready"])
        self.assertFalse(report["metadata_subset"]["v4_true_zero_copy_claim_authorized"])
        self.assertTrue(all(report["pointer_identity"].values()))
        self.assertTrue(all(report["pointer_echo_identity"].values()))
        boundaries = report["claim_boundaries"]
        self.assertTrue(boundaries["dlpack_bridge_wrapper_claim_authorized"])
        self.assertFalse(boundaries["full_dlpack_capsule_route_claim_authorized"])
        self.assertFalse(boundaries["dlpack_route_claim_authorized"])
        self.assertFalse(boundaries["pytorch_route_claim_authorized"])
        self.assertFalse(boundaries["async_claim_authorized"])
        self.assertFalse(boundaries["public_speedup_claim_authorized"])
        self.assertFalse(boundaries["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundaries["v4_true_zero_copy_claim_authorized"])
        self.assertIn("does not validate arbitrary DLPack capsule", boundaries["reason"])

    def test_dlpack_capsule_probe_script_uses_real_capsule_path(self) -> None:
        script = DLPACK_CAPSULE_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "class DLPackCapsuleOnlyColumn",
            "__dlpack__",
            "__dlpack_device__",
            "all_wrappers_hide_cuda_array_interface",
            "all_wrappers_hide_data_ptr",
            "real_dlpack_capsule_intake",
            "legacy_dltensor_capsule_policy",
            "producer_accepted_stream_argument",
            "fixed_radius_m1_dlpack_capsule_route_claim_authorized",
            "full_dlpack_capsule_route_claim_authorized",
            "framework_neutral_dlpack_route_claim_authorized",
            "pytorch_route_claim_authorized",
            "async_claim_authorized",
            "public_speedup_claim_authorized",
            "v4_true_zero_copy_claim_authorized",
            "False",
            "does not validate arbitrary",
            "framework-neutral DLPack",
        ):
            self.assertIn(token, script)

    def test_dlpack_capsule_report_validates_lifetime_stream_and_blocks_broad_claims(self) -> None:
        report = json.loads(DLPACK_CAPSULE_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["framework"], "cupy_backed_dlpack_capsule_only_wrapper")
        self.assertEqual(report["protocol"], "legacy_dlpack_capsule")
        self.assertEqual(report["remote_validation"]["host"], "192.168.1.20")
        self.assertTrue(report["remote_validation"]["build_optix"]["ok"])
        self.assertTrue(report["remote_validation"]["v4_active"]["ok"])
        self.assertEqual(report["remote_validation"]["v4_active"]["test_count"], 61)
        self.assertTrue(report["remote_validation"]["dlpack_capsule_probe"]["ok"])
        self.assertTrue(report["remote_validation"]["claim_boundary_scan"]["ok"])
        self.assertTrue(report["remote_validation"]["git_diff_check"]["ok"])
        self.assertTrue(report["remote_validation"]["worktree_clean"]["ok"])
        self.assertTrue(report["validation"]["output_match"])
        self.assertTrue(report["validation"]["all_wrappers_hide_cuda_array_interface"])
        self.assertTrue(report["validation"]["all_wrappers_hide_data_ptr"])
        self.assertTrue(report["validation"]["real_dlpack_capsule_intake"])
        self.assertTrue(report["validation"]["legacy_dltensor_capsule_policy"])
        self.assertEqual(report["metadata_subset"]["source_protocols"], ["dlpack"])
        self.assertTrue(report["metadata_subset"]["caller_stream_handle_nonzero"])
        self.assertTrue(report["metadata_subset"]["prepare_stream_handle_nonzero"])
        self.assertFalse(report["metadata_subset"]["native_async_ready"])
        self.assertFalse(report["metadata_subset"]["v4_true_zero_copy_claim_authorized"])
        self.assertTrue(all(report["pointer_identity"].values()))
        self.assertTrue(all(report["pointer_echo_identity"].values()))
        self.assertTrue(report["dlpack_stream_contract"]["all_requested_streams_match_caller_stream"])
        self.assertFalse(report["dlpack_stream_contract"]["async_completion_authorized"])
        lifetime = report["lifetime_contract"]
        self.assertEqual(lifetime["capsule_policy"], "legacy_dltensor_only")
        self.assertIn("used_dltensor", lifetime["consume_policy"])
        self.assertIn("deleter exactly once", lifetime["deleter_policy"])
        self.assertFalse(lifetime["full_framework_neutral_lifetime_matrix_complete"])
        boundaries = report["claim_boundaries"]
        self.assertTrue(boundaries["fixed_radius_m1_dlpack_capsule_route_claim_authorized"])
        self.assertFalse(boundaries["full_dlpack_capsule_route_claim_authorized"])
        self.assertFalse(boundaries["framework_neutral_dlpack_route_claim_authorized"])
        self.assertFalse(boundaries["dlpack_route_claim_authorized"])
        self.assertFalse(boundaries["pytorch_route_claim_authorized"])
        self.assertFalse(boundaries["async_claim_authorized"])
        self.assertFalse(boundaries["public_speedup_claim_authorized"])
        self.assertFalse(boundaries["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundaries["v4_true_zero_copy_claim_authorized"])
        self.assertIn("does not validate arbitrary framework-neutral DLPack", boundaries["reason"])

    def test_pytorch_cuda_tensor_probe_script_covers_exact_m1_route(self) -> None:
        script = PYTORCH_SCRIPT.read_text(encoding="utf-8")

        for token in (
            "import torch",
            "torch.cuda.Stream",
            "requires_grad=True",
            "partner=\"torch\"",
            "output_columns=outputs",
            "source_protocols",
            "torch_cuda_tensor_data_ptr",
            "pytorch_fixed_radius_m1_cuda_tensor_route_claim_authorized",
            "pytorch_full_partner_surface_claim_authorized",
            "framework_neutral_dlpack_route_claim_authorized",
            "async_claim_authorized",
            "public_speedup_claim_authorized",
            "v4_true_zero_copy_claim_authorized",
            "False",
            "not validate a full PyTorch",
            "partner surface, framework-neutral DLPack",
        ):
            self.assertIn(token, script)

    def test_pytorch_cuda_tensor_report_authorizes_only_exact_m1_route(self) -> None:
        report = json.loads(PYTORCH_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass-with-boundary")
        self.assertEqual(report["route_id"], "fixed_radius_count_threshold_2d")
        self.assertEqual(report["framework"], "pytorch")
        self.assertEqual(report["protocol"], "torch_cuda_tensor_data_ptr")
        self.assertEqual(report["remote_validation"]["validated_commit"], report["evidence_code_commit"])
        self.assertTrue(report["remote_validation"]["build_optix"]["ok"])
        self.assertTrue(report["remote_validation"]["v4_active"]["ok"])
        self.assertEqual(report["remote_validation"]["v4_active"]["test_count"], 64)
        self.assertTrue(report["remote_validation"]["dlpack_capsule_probe"]["ok"])
        self.assertTrue(report["remote_validation"]["source_tree_doctor"]["ok"])
        self.assertTrue(report["remote_validation"]["claim_boundary_scan"]["ok"])
        self.assertTrue(report["remote_validation"]["git_diff_check"]["ok"])
        self.assertTrue(report["remote_validation"]["worktree_clean"]["ok"])
        self.assertTrue(report["torch"]["cuda_available"])
        self.assertIn("+cu", report["torch"]["version"])
        self.assertEqual(report["hardware"]["gpu"], "NVIDIA GeForce GTX 1070")
        self.assertFalse(report["hardware"]["rt_core_hardware"])
        self.assertTrue(report["validation"]["output_match"])
        self.assertTrue(report["validation"]["same_stream_consumer_checksum_match"])
        self.assertTrue(report["validation"]["grad_enabled_tensor_rejected"])
        self.assertEqual(report["validation"]["observed"], report["validation"]["expected"])
        self.assertEqual(report["validation"]["observed_checksum"], report["validation"]["expected_checksum"])
        self.assertEqual(report["metadata_subset"]["source_protocols"], ["torch"])
        self.assertTrue(report["metadata_subset"]["caller_stream_handle_nonzero"])
        self.assertTrue(report["metadata_subset"]["prepare_stream_handle_nonzero"])
        self.assertTrue(report["metadata_subset"]["caller_stream_native_propagation_ready"])
        self.assertTrue(report["metadata_subset"]["native_prepare_stream_propagation_ready"])
        self.assertTrue(report["metadata_subset"]["native_synchronized_before_return"])
        self.assertTrue(report["metadata_subset"]["native_call_device_pointer_echo_complete"])
        self.assertFalse(report["metadata_subset"]["native_async_ready"])
        self.assertFalse(report["metadata_subset"]["v4_true_zero_copy_claim_authorized"])
        self.assertTrue(all(report["pointer_identity"].values()))
        self.assertTrue(all(report["pointer_echo_identity"].values()))
        self.assertTrue(report["stream_contract"]["same_stream_consumer_checksum_validated"])
        self.assertFalse(report["stream_contract"]["cross_stream_event_wait_validated"])
        self.assertFalse(report["stream_contract"]["async_completion_authorized"])
        lifetime = report["lifetime_contract"]
        self.assertTrue(lifetime["caller_owned_tensors_retained_until_stream_synchronized"])
        self.assertTrue(lifetime["grad_enabled_tensors_must_be_detached"])
        self.assertFalse(lifetime["full_pytorch_partner_surface_complete"])
        boundaries = report["claim_boundaries"]
        self.assertTrue(boundaries["pytorch_fixed_radius_m1_cuda_tensor_route_claim_authorized"])
        self.assertTrue(boundaries["pytorch_route_claim_authorized"])
        self.assertFalse(boundaries["pytorch_full_partner_surface_claim_authorized"])
        self.assertFalse(boundaries["framework_neutral_dlpack_route_claim_authorized"])
        self.assertFalse(boundaries["async_claim_authorized"])
        self.assertFalse(boundaries["public_speedup_claim_authorized"])
        self.assertFalse(boundaries["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundaries["v4_true_zero_copy_claim_authorized"])
        self.assertIn("does not validate a full PyTorch partner surface", boundaries["reason"])

    def test_claim_review_keeps_v4_true_zero_copy_claim_blocked(self) -> None:
        review = CLAIM_REVIEW.read_text(encoding="utf-8")

        for token in (
            "Verdict: keep `v4_true_zero_copy_claim_authorized` false",
            "Prepare caller-stream support has now landed",
            "transfer-counter or equivalent no-host-stage evidence",
            "fail-closed matrix",
            "Do not promote",
        ):
            self.assertIn(token, review)

    def test_wording_consensus_keeps_public_true_zero_copy_blocked(self) -> None:
        consensus = WORDING_CONSENSUS.read_text(encoding="utf-8")

        for token in (
            "Keep `v4_true_zero_copy_claim_authorized` false",
            "zero-copy device-column handoff with no observed host staging of named columns",
            "not end-to-end true zero-copy",
            "named_cuda_columns_no_host_stage_authorized",
            "internal device-to-device AABB/BVH staging",
            "Async remains blocked",
        ):
            self.assertIn(token, consensus)

    def test_operator_uses_on_stream_route_for_nonzero_caller_stream(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        prepared = _FakePrepared(prepare_stream_ptr=456)

        with mock.patch.object(v4, "_prepare_scene") as prepare_scene, mock.patch.object(
            v4,
            "_prepare_scene_on_stream",
            return_value=prepared,
        ) as prepare_on_stream, mock.patch.object(
            v4,
            "_run_prepared",
        ) as run_prepared:
            result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
                query,
                search,
                radius=1.0,
                threshold=1,
                partner="cupy",
                output_columns=outputs,
                stream=456,
                return_metadata=True,
            )

        prepare_scene.assert_not_called()
        prepare_on_stream.assert_called_once()
        self.assertEqual(prepare_on_stream.call_args.kwargs["cuda_stream_ptr"], 456)
        run_prepared.assert_not_called()
        self.assertEqual(prepared.on_stream_call["cuda_stream_ptr"], 456)
        self.assertIs(prepared.on_stream_call["query_ids_out"], outputs["query_ids"])
        metadata = result["metadata"]
        self.assertEqual(metadata["caller_stream_handle"], 456)
        self.assertEqual(metadata["prepare_stream_handle"], 456)
        self.assertTrue(metadata["caller_stream_native_propagation_ready"])
        self.assertTrue(metadata["native_prepare_stream_propagation_ready"])
        self.assertTrue(metadata["cross_stream_event_wait_ready"])
        self.assertFalse(metadata["prepare_query_streams_differ"])
        self.assertFalse(metadata["native_prepare_ready_event_wait_required"])
        self.assertTrue(metadata["native_prepare_ready_event_recorded"])
        self.assertTrue(metadata["native_prepare_ready_event_wait_ready"])
        self.assertFalse(metadata["native_prepare_ready_event_wait_used"])
        self.assertTrue(metadata["native_synchronized_before_return"])
        self.assertFalse(metadata["native_async_ready"])
        self.assertTrue(metadata["native_true_zero_copy_authorized"])
        self.assertTrue(metadata["native_call_device_pointer_echo_complete"])
        self.assertEqual(metadata["native_call_device_pointer_echo"]["query.x"], 0x2020)
        self.assertEqual(metadata["native_call_device_pointer_echo"]["output.neighbor_counts"], 0x3020)
        self.assertTrue(metadata["named_cuda_columns_no_host_stage_authorized"])
        self.assertTrue(metadata["named_cuda_columns_no_host_stage_ready"])
        self.assertTrue(metadata["internal_device_staging_disclosed"])
        self.assertIn("AABB/BVH", metadata["internal_device_staging_scope"])
        self.assertEqual(
            metadata["v4_true_zero_copy_claim_blocker"],
            "public_true_zero_copy_wording_blocked_by_internal_device_staging_and_sync_contract",
        )
        self.assertFalse(metadata["v4_true_zero_copy_claim_authorized"])

    def test_operator_uses_prepare_ready_event_wait_for_different_prepare_and_query_streams(self) -> None:
        search = _point_columns(0x1000)
        query = _point_columns(0x2000)
        outputs = _output_columns(0x3000)
        prepared = _FakePrepared(prepare_stream_ptr=123)

        with mock.patch.object(v4, "_prepare_scene_on_stream", return_value=prepared):
            with rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
                search,
                max_radius=2.0,
                partner="cupy",
                stream=123,
            ) as operator:
                result = operator.run(
                    query,
                    radius=1.0,
                    threshold=1,
                    output_columns=outputs,
                    stream=456,
                    return_metadata=True,
                )

        metadata = result["metadata"]
        self.assertEqual(prepared.on_stream_call["cuda_stream_ptr"], 456)
        self.assertEqual(metadata["caller_stream_handle"], 456)
        self.assertEqual(metadata["prepare_stream_handle"], 123)
        self.assertTrue(metadata["prepare_query_streams_differ"])
        self.assertTrue(metadata["native_prepare_ready_event_wait_required"])
        self.assertTrue(metadata["native_prepare_ready_event_recorded"])
        self.assertTrue(metadata["native_prepare_ready_event_wait_ready"])
        self.assertTrue(metadata["native_prepare_ready_event_wait_used"])
        self.assertTrue(metadata["native_synchronized_before_return"])
        self.assertFalse(metadata["native_async_ready"])
        self.assertFalse(metadata["v4_true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
