from __future__ import annotations

import ctypes
import dataclasses
import json
from pathlib import Path
import pickle
import tempfile
import unittest
from unittest import mock

import numpy as np

from rtdsl.v4_callback_abi import CallbackAbiError, derive_compiler_recognized_any_hit_proof
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_ir import CallbackVerificationError
from rtdsl.v4_callback_partner_runtime import (
    UINT32_MAX,
    V4PartnerContractError,
    V4PreparedCallbackSession,
    _FormalStatus,
    describe_cuda_array,
)
from tests.goal5750_v4_callback_ir_test import manifest
from tests.goal5751_v4_optix_wrapper_codegen_test import FORMAL_SOURCE


class _Symbol:
    def __init__(self, function):
        self.function = function
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        return self.function(*args)


def _integer(value) -> int:
    return int(value.value) if hasattr(value, "value") else int(value)


class _FakeLibrary:
    def __init__(self, native_path: Path):
        self._name = str(native_path)
        self.destroyed = []
        self.executions = 0
        self.rtdl_optix_v4_prepare_formal_callback_v1 = _Symbol(self._prepare)
        self.rtdl_optix_v4_execute_prepared_formal_callback_device_v1 = _Symbol(self._execute)
        self.rtdl_optix_v4_destroy_prepared_formal_callback_v1 = _Symbol(self._destroy)

    @staticmethod
    def _prepare(_ptx, _spheres, _count, token_out, _error, _size):
        ctypes.cast(token_out, ctypes.POINTER(ctypes.c_uint64))[0] = 71
        return 0

    def _execute(
        self, _token, _qx, _qy, _qz, _qt, count, ids_ptr, distance_ptr,
        status_ptr, counter_ptr, _stream, _error, _size,
    ):
        self.executions += 1
        count = _integer(count)
        ids = (ctypes.c_uint32 * count).from_address(_integer(ids_ptr))
        distances = (ctypes.c_float * count).from_address(_integer(distance_ptr))
        statuses = (_FormalStatus * count).from_address(_integer(status_ptr))
        counters = (ctypes.c_uint64 * 7).from_address(_integer(counter_ptr))
        for index in range(count):
            ids[index] = 3 if index == 0 else UINT32_MAX
            distances[index] = 4.0 if index == 0 else 100.0
            statuses[index] = _FormalStatus()
        for index, value in enumerate((3, 2, 3, 2, 1, 1, 2)):
            counters[index] = value
        return 0

    def _destroy(self, token, _error, _size):
        self.destroyed.append(_integer(token))
        return 0


class _Device:
    id = 0


class _FakeCudaArray:
    def __init__(self, array: np.ndarray, *, read_only: bool = False):
        self.array = np.ascontiguousarray(array)
        self.device = _Device()
        self.size = self.array.size
        self.__cuda_array_interface__ = {
            "version": 3,
            "shape": self.array.shape,
            "strides": self.array.strides,
            "typestr": self.array.dtype.str,
            "data": (int(self.array.ctypes.data), bool(read_only)),
        }


class _Stream:
    ptr = 0x12340

    @staticmethod
    def synchronize():
        return None


class _Audit:
    def __init__(self):
        self.aborted = False

    def abort(self):
        self.aborted = True

    def finish(self, **kwargs):
        return {
            "physical_executor_classification": "optix_traversal_observed",
            "successful_launch_count": 1,
            "complete_context_launch_count": 1,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "semantic_digest": kwargs["semantic_digest"],
            "output_digest": kwargs["output_digest"],
        }


class Goal5752PartnerLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        native = Path(self.temp.name) / "librtdl_optix.so"
        native.write_bytes(b"fake-goal5752-native")
        self.library = _FakeLibrary(native)
        self.session = V4PreparedCallbackSession(
            library=self.library, token=71, semantic_digest="1" * 64,
            provider_identity="rtdl.v4.generated_provider." + "2" * 64,
            provider_key_sha256="2" * 64, composed_ptx_sha256="3" * 64,
            native_sha256="4" * 64, geometry_sha256="5" * 64,
            sphere_count=3,
        )

    def tearDown(self):
        if not self.session.closed:
            self.session.close()
        self.temp.cleanup()

    def _arrays(self):
        return (
            _FakeCudaArray(np.array([0.0, 0.0], dtype=np.float32)),
            _FakeCudaArray(np.array([0.0, 4.0], dtype=np.float32)),
            _FakeCudaArray(np.array([0.0, 0.0], dtype=np.float32)),
            _FakeCudaArray(np.array([100.0, 100.0], dtype=np.float32)),
            _FakeCudaArray(np.empty(2, dtype=np.uint32)),
            _FakeCudaArray(np.empty(2, dtype=np.float32)),
            _FakeCudaArray(np.empty(2 * ctypes.sizeof(_FormalStatus), dtype=np.uint8)),
            _FakeCudaArray(np.empty(7, dtype=np.uint64)),
            _FakeCudaArray(np.empty(2, dtype=np.bool_)),
            _FakeCudaArray(np.empty(2, dtype=np.float32)),
        )

    def test_typed_same_stream_device_handoff_and_continuation(self):
        arrays = self._arrays()

        def continuation():
            arrays[8].array[:] = arrays[4].array != UINT32_MAX
            arrays[9].array[:] = np.where(
                arrays[8].array, arrays[5].array, np.float32(0.0))

        with mock.patch(
            "rtdsl.v4_callback_partner_runtime.OptixTraversalAuditSession.open",
            return_value=_Audit(),
        ):
            result = self.session._execute_with_enqueued_continuation(
                enqueue_continuation=continuation,
                partner="cupy", stream=_Stream(), arrays=arrays,
                synchronize=_Stream.synchronize,
                to_host=lambda value: value.array,
                expected_output=((3, 4.0), (UINT32_MAX, 100.0)),
            )
        self.assertEqual(result.output_ids, (3, UINT32_MAX))
        self.assertEqual(result.valid_hit_mask, (True, False))
        self.assertEqual(result.masked_distance, (4.0, 0.0))
        self.assertEqual(result.valid_hit_count, 1)
        self.assertTrue(result.buffer_receipt["native_boundary_host_staging"] is False)
        self.assertTrue(result.buffer_receipt["single_explicit_nondefault_stream"])
        self.assertEqual(result.execution_index, 1)
        self.assertEqual(self.library.executions, 1)

    def test_buffer_contract_rejects_dtype_shape_stride_readonly_and_default_stream(self):
        good = _FakeCudaArray(np.empty(2, dtype=np.float32))
        view = describe_cuda_array(
            "query_x", good, dtype=np.dtype(np.float32), length=2, writable=False)
        self.assertGreater(view.device_pointer, 0)

        for value, code in (
            (_FakeCudaArray(np.empty(2, dtype=np.float64)), "buffer_dtype"),
            (_FakeCudaArray(np.empty(3, dtype=np.float32)), "buffer_shape"),
            (_FakeCudaArray(np.empty(2, dtype=np.float32), read_only=True), "buffer_read_only"),
        ):
            with self.assertRaises(V4PartnerContractError) as caught:
                describe_cuda_array(
                    "output", value, dtype=np.dtype(np.float32), length=2, writable=True)
            self.assertEqual(caught.exception.code, code)

        arrays = self._arrays()
        default_stream = _Stream()
        default_stream.ptr = 0
        with self.assertRaises(V4PartnerContractError) as caught, mock.patch(
            "rtdsl.v4_callback_partner_runtime.OptixTraversalAuditSession.open",
            return_value=_Audit(),
        ):
            self.session._execute_with_enqueued_continuation(
                enqueue_continuation=lambda: None,
                partner="cupy", stream=default_stream, arrays=arrays,
                synchronize=lambda: None, to_host=lambda value: value.array,
                expected_output=None,
            )
        self.assertEqual(caught.exception.code, "stream")
        self.assertEqual(self.library.executions, 0)

    def test_prepared_owner_is_nonserializable_and_use_after_close_fails(self):
        with self.assertRaises(V4PartnerContractError) as caught:
            pickle.dumps(self.session)
        self.assertEqual(caught.exception.code, "session_serialization")
        self.session.close()
        self.assertEqual(self.library.destroyed, [71])
        with self.assertRaises(V4PartnerContractError) as closed:
            self.session._check_owner()
        self.assertEqual(closed.exception.code, "session_closed")

    def test_goal5751_p2_decode_errors_are_uniformly_coded(self):
        verified = compile_callback_source(FORMAL_SOURCE, manifest())
        payload = json.loads(json.dumps(verified.program.to_dict()))
        mutations = []
        unknown_enum = json.loads(json.dumps(payload))
        unknown_enum["manifest"]["geometry"]["admission"] = "unknown"
        mutations.append(unknown_enum)
        malformed_type = json.loads(json.dumps(payload))
        malformed_type["records"][0]["fields"][0]["type"]["kind"] = "unknown"
        mutations.append(malformed_type)
        from rtdsl.v4_callback_ir import callback_program_from_dict
        for mutation in mutations:
            with self.assertRaises(CallbackVerificationError) as caught:
                callback_program_from_dict(mutation)
            self.assertEqual(caught.exception.code, "decode_error")

    def test_partner_cannot_coerce_a_different_any_hit_reduction(self):
        baseline = compile_callback_source(FORMAL_SOURCE, manifest())
        derive_compiler_recognized_any_hit_proof(baseline)
        hostile_source = FORMAL_SOURCE.replace(
            "hit.hit_kind < payload.best_id",
            "hit.hit_kind > payload.best_id",
        )
        self.assertNotEqual(hostile_source, FORMAL_SOURCE)
        hostile = compile_callback_source(hostile_source, manifest())
        with self.assertRaises(CallbackAbiError) as caught:
            derive_compiler_recognized_any_hit_proof(hostile)
        self.assertEqual(caught.exception.code, "any_hit_compiler_proof_shape")

    def test_native_prepared_boundary_has_token_registry_and_no_host_staging(self):
        source = Path("src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text()
        api = Path("src/native/optix/rtdl_optix_api.cpp").read_text()
        self.assertIn("g_v4_prepared_formal_registry", source)
        self.assertIn("unknown or closed", source)
        self.assertIn("cuMemsetD8Async", source)
        self.assertIn("cuEventRecord", source)
        self.assertNotIn("download(output_ids", source[source.index(
            "static void execute_v4_prepared_formal_callback_device"):source.index(
            "static void destroy_v4_prepared_formal_callback")])
        self.assertIn("rtdl_optix_v4_execute_prepared_formal_callback_device_v1", api)


if __name__ == "__main__":
    unittest.main()
