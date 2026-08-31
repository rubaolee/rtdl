from __future__ import annotations

import ctypes
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
import threading
import unittest
from unittest import mock

import numpy as np

from experiments.goal5814_particle_tracking import particle_product_owner as owner_api


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_HEADER = ROOT / "src/native/optix/rtdl_optix_v4_particle_template.h"
REAL_DESCRIPTOR = (
    ROOT / "history/internal_docs/goal5814_particle_executable_v2_20260828"
    / "4bf983fdc07f5f6e48b8fcd32482ea23dc14a50a3083cdaa4fe0923142acba63.particle_descriptor.json"
)


def _exact_exported_source() -> bytes:
    match = re.search(
        rb'kRtdlV4ParticleStrictInteriorSource\s*=\s*R"RTDLCUDA\((.*?)\)RTDLCUDA";',
        TEMPLATE_HEADER.read_bytes(),
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("unable to extract exact Particle template source")
    source = match.group(1)
    if hashlib.sha256(source).hexdigest() != owner_api.EXPECTED_SOURCE_SHA256:
        raise AssertionError("live native source is not the adapter's frozen source")
    return source


def _descriptor_bytes(source: bytes, mutate: bool = False) -> bytes:
    descriptor = owner_api._expected_descriptor(source)
    if mutate:
        descriptor = dict(descriptor)
        descriptor["unreviewed_extension"] = True
    return json.dumps(
        descriptor, ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8")


def _prebuilt(source: bytes, descriptor: bytes) -> owner_api.ParticlePrebuiltPTX:
    ptx = (
        b".version 7.0\n.target sm_70\n.address_size 64\n"
        b".visible .entry __raygen__rtdl_particle_strict_interior() {}\n"
        b".visible .entry __closesthit__rtdl_particle_strict_interior() {}\n"
        b".visible .entry __miss__rtdl_particle_strict_interior() {}\n"
    )
    return owner_api.ParticlePrebuiltPTX(
        ptx=ptx,
        source_sha256=hashlib.sha256(source).hexdigest(),
        descriptor_sha256=hashlib.sha256(descriptor).hexdigest(),
        semantic_sha256=owner_api.EXPECTED_SEMANTIC_SHA256,
        ptx_sha256=hashlib.sha256(ptx).hexdigest(),
    )


def _int(value: object) -> int:
    return int(value.value) if hasattr(value, "value") else int(value)


class _FakeCFunction:
    def __init__(self, callback):
        self.callback = callback
        self.argtypes = None
        self.restype = None
        self.calls = 0

    def __call__(self, *args):
        self.calls += 1
        return self.callback(*args)


class _FakeLibrary:
    def __init__(
        self,
        source: bytes,
        descriptor: bytes,
        expected: np.ndarray,
        mode: str = "success",
    ) -> None:
        self.source = source
        self.descriptor = descriptor
        self.expected = expected
        self.mode = mode
        self.accessed: list[str] = []
        self.prepared = False
        self.destroyed = False
        self.borrowed_output_soa = np.empty(
            (3, owner_api.QUERY_COUNT), dtype=np.uint32
        )
        self._symbols = {
            owner_api.SOURCE_SYMBOL: _FakeCFunction(
                lambda *args: self._query(self.source, *args)
            ),
            owner_api.DESCRIPTOR_SYMBOL: _FakeCFunction(
                lambda *args: self._query(self.descriptor, *args)
            ),
            owner_api.PREPARE_SYMBOL: _FakeCFunction(self._prepare),
            owner_api.EXECUTE_SYMBOL: _FakeCFunction(self._execute),
            owner_api.DESTROY_SYMBOL: _FakeCFunction(self._destroy),
        }

    def __getattr__(self, name: str):
        symbols = object.__getattribute__(self, "_symbols")
        if name not in symbols:
            raise AttributeError(name)
        self.accessed.append(name)
        return symbols[name]

    @staticmethod
    def _query(payload, output, capacity, byte_count_out, error, error_size):
        del error, error_size
        ctypes.cast(
            byte_count_out, ctypes.POINTER(ctypes.c_size_t)
        )[0] = len(payload)
        if output is None:
            if _int(capacity) != 0:
                return 1
            return 0
        if _int(capacity) <= len(payload):
            return 1
        ctypes.memmove(output, payload, len(payload))
        ctypes.memset(ctypes.addressof(output) + len(payload), 0, 1)
        return 0

    def _prepare(
        self,
        ptx,
        vertices,
        vertex_count,
        triangles,
        triangle_count,
        front_values,
        back_values,
        token_out,
        error,
        error_size,
    ):
        del error, error_size
        if (
            not ptx
            or not vertices
            or not triangles
            or not front_values
            or not back_values
            or _int(vertex_count) != owner_api.VERTEX_COUNT
            or _int(triangle_count) != owner_api.TRIANGLE_COUNT
        ):
            return 1
        ctypes.cast(token_out, ctypes.POINTER(ctypes.c_uint64))[0] = 0x5814
        self.prepared = True
        return 0

    @staticmethod
    def _fill_structure(pointer, structure_type, values):
        structure = ctypes.cast(pointer, ctypes.POINTER(structure_type)).contents
        for key, value in values.items():
            setattr(structure, key, value)

    def _execute(
        self,
        token,
        query_ox,
        query_oy,
        query_oz,
        query_dx,
        query_dy,
        query_dz,
        query_tmax,
        query_count,
        output_columns_soa_out,
        output_row_count_out,
        control_out,
        receipt_out,
        error,
        error_size,
    ):
        del error, error_size
        if _int(token) != 0x5814 or _int(query_count) != owner_api.QUERY_COUNT:
            return 1
        if not all(
            (
                query_ox,
                query_oy,
                query_oz,
                query_dx,
                query_dy,
                query_dz,
                query_tmax,
            )
        ):
            return 1
        borrowed_pointer_out = ctypes.cast(
            output_columns_soa_out, ctypes.POINTER(owner_api._U32_PTR)
        )
        borrowed_row_count_out = ctypes.cast(
            output_row_count_out, ctypes.POINTER(ctypes.c_size_t)
        )
        borrowed_pointer_out[0] = owner_api._U32_PTR()
        borrowed_row_count_out[0] = 0

        receipt = {
            "schema_version": 1,
            "optix_launch_count": 1,
            "query_count": 5_000,
            "query_h2d_copy_call_count": 7,
            "control_reset_h2d_copy_call_count": 1,
            "parameter_h2d_copy_call_count": 1,
            "control_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1,
            "host_blocking_boundary_count": 2,
            "status_before_output": 1,
            "query_h2d_bytes": 140_000,
            "control_reset_h2d_bytes": 16,
            "parameter_h2d_bytes": 120,
            "control_d2h_bytes": 16,
            "output_d2h_bytes": 60_000,
            "output_d2h_after_status_failure": 0,
            "boundary_owner_table_bytes": 0,
        }
        if self.mode.startswith("status_failure"):
            control = {
                "validated_row_count": 4_999,
                "first_error": 17,
                "error_code": 2,
                "status": 1,
            }
            receipt.update(
                output_d2h_copy_call_count=0,
                host_blocking_boundary_count=1,
                output_d2h_bytes=0,
            )
            if self.mode == "status_failure_pointer_leak":
                borrowed_pointer_out[0] = self.borrowed_output_soa.ctypes.data_as(
                    owner_api._U32_PTR
                )
                borrowed_row_count_out[0] = owner_api.QUERY_COUNT
        else:
            control = {
                "validated_row_count": 5_000,
                "first_error": owner_api.UINT32_MAX,
                "error_code": 0,
                "status": 0,
            }
            for column in range(3):
                self.borrowed_output_soa[column, :] = self.expected[:, column]
            borrowed_pointer_out[0] = self.borrowed_output_soa.ctypes.data_as(
                owner_api._U32_PTR
            )
            borrowed_row_count_out[0] = owner_api.QUERY_COUNT
        if self.mode == "receipt_mismatch":
            receipt["query_h2d_copy_call_count"] = 6
        self._fill_structure(control_out, owner_api._ParticleControl, control)
        self._fill_structure(
            receipt_out, owner_api._ParticleFastReceipt, receipt
        )
        return 0

    def _destroy(self, token_inout, error, error_size):
        del error, error_size
        token = ctypes.cast(token_inout, ctypes.POINTER(ctypes.c_uint64))
        if token[0] != 0x5814:
            return 1
        token[0] = 0
        self.destroyed = True
        return 0


class _NoPythonRows(np.ndarray):
    def __iter__(self):
        raise AssertionError("Python row iteration is forbidden")

    def tolist(self):
        raise AssertionError("tolist is forbidden")


class ParticleProductOwnerAdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = _exact_exported_source()
        cls.descriptor = _descriptor_bytes(cls.source)
        cls.prebuilt = _prebuilt(cls.source, cls.descriptor)
        cls.vertices = np.zeros(
            (owner_api.VERTEX_COUNT, 3), dtype=np.float32
        )
        cls.triangles = np.zeros(
            (owner_api.TRIANGLE_COUNT, 3), dtype=np.uint32
        )
        cls.front = np.zeros(owner_api.TRIANGLE_COUNT, dtype=np.uint32)
        cls.back = np.ones(owner_api.TRIANGLE_COUNT, dtype=np.uint32)
        cls.static_input = owner_api.ParticleStaticInput(
            cls.vertices, cls.triangles, cls.front, cls.back
        )
        cls.query_columns = owner_api.ParticleQueryColumns(
            *(np.full(owner_api.QUERY_COUNT, index + 1, dtype=np.float32)
              for index in range(7))
        )
        cls.expected = np.empty(
            (owner_api.QUERY_COUNT, 3), dtype=np.uint32
        )
        indices = np.arange(owner_api.QUERY_COUNT, dtype=np.uint32)
        cls.expected[:, 0] = indices
        cls.expected[:, 1] = indices + np.uint32(1)
        cls.expected[:, 2] = indices * np.uint32(2)

    def _owner(self, mode="success", source=None, descriptor=None, prebuilt=None):
        library = _FakeLibrary(
            self.source if source is None else source,
            self.descriptor if descriptor is None else descriptor,
            self.expected,
            mode=mode,
        )
        owner = owner_api.prepare_particle_product_owner(
            library,
            self.prebuilt if prebuilt is None else prebuilt,
            self.static_input,
        )
        return library, owner

    def test_success_exact_output_and_only_product_symbols(self):
        library, owner = self._owner()
        self.assertEqual(library.accessed, list(owner_api.PRODUCT_SYMBOLS))
        output = owner.execute_complete(self.query_columns, self.expected)
        self.assertIs(type(output), np.ndarray)
        self.assertEqual(output.dtype, np.dtype(np.uint32))
        self.assertEqual(output.shape, (5_000, 3))
        self.assertTrue(output.flags.f_contiguous)
        self.assertFalse(output.flags.writeable)
        self.assertEqual(
            output.__array_interface__["data"][0],
            library.borrowed_output_soa.__array_interface__["data"][0],
        )
        self.assertTrue(np.array_equal(output, self.expected))
        self.assertEqual(owner.last_receipt["query_h2d_copy_call_count"], 7)
        self.assertEqual(owner.last_receipt["query_h2d_bytes"], 140_000)
        self.assertEqual(owner.last_receipt["output_d2h_bytes"], 60_000)
        owner.close()
        self.assertTrue(owner.closed)
        self.assertTrue(library.destroyed)

    def test_adapter_descriptor_is_exact_downloaded_v2_authority(self):
        self.assertEqual(self.descriptor, REAL_DESCRIPTOR.read_bytes())
        self.assertEqual(
            json.loads(self.descriptor)["native_abi"],
            "rtdl.v4.prepared_particle_strict_interior.v2",
        )

    def test_previous_borrowed_output_cannot_become_next_oracle(self):
        _, owner = self._owner()
        previous = owner.execute_complete(self.query_columns, self.expected)
        with self.assertRaisesRegex(
                owner_api.ParticleInputError, "must not share memory"):
            owner.execute_complete(self.query_columns, previous)
        owner.close()

    def test_oracle_comparison_holds_owner_lock(self):
        _, owner = self._owner()
        comparison_entered = threading.Event()
        release_comparison = threading.Event()
        failures = []
        completed = []
        real_array_equal = np.array_equal

        def blocked_array_equal(left, right):
            comparison_entered.set()
            if not release_comparison.wait(timeout=5):
                raise AssertionError("test did not release oracle comparison")
            return real_array_equal(left, right)

        def worker_body():
            try:
                completed.append(owner.execute_complete(
                    self.query_columns, self.expected))
            except BaseException as exc:  # pragma: no cover - diagnostic
                failures.append(exc)

        with mock.patch.object(
                owner_api.np, "array_equal", side_effect=blocked_array_equal):
            worker = threading.Thread(target=worker_body)
            worker.start()
            self.assertTrue(comparison_entered.wait(timeout=5))
            with self.assertRaisesRegex(
                    owner_api.ParticleNativeError, "active operation"):
                owner.execute_complete(self.query_columns, self.expected)
            release_comparison.set()
            worker.join(timeout=5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(failures, [])
        self.assertEqual(len(completed), 1)
        owner.close()

    def test_status_failure_proves_zero_output_d2h_before_raising(self):
        library, owner = self._owner(mode="status_failure")
        with mock.patch.object(
            owner_api.np,
            "array_equal",
            side_effect=AssertionError("oracle must not inspect failed output"),
        ):
            with self.assertRaises(owner_api.ParticleDeviceStatusError) as caught:
                owner.execute_complete(self.query_columns, self.expected)
        self.assertEqual(caught.exception.receipt["output_d2h_copy_call_count"], 0)
        self.assertEqual(caught.exception.receipt["output_d2h_bytes"], 0)
        self.assertEqual(
            caught.exception.receipt["output_d2h_after_status_failure"], 0
        )
        self.assertEqual(caught.exception.receipt["host_blocking_boundary_count"], 1)
        owner.close()
        self.assertTrue(library.destroyed)

    def test_status_failure_must_withhold_borrowed_output(self):
        _, owner = self._owner(mode="status_failure_pointer_leak")
        with self.assertRaisesRegex(
            owner_api.ParticleReceiptError, "non-null borrowed output"
        ):
            owner.execute_complete(self.query_columns, self.expected)
        owner.close()

    def test_full_receipt_mismatch_rejects(self):
        _, owner = self._owner(mode="receipt_mismatch")
        with self.assertRaisesRegex(
            owner_api.ParticleReceiptError, "query_h2d_copy_call_count"
        ):
            owner.execute_complete(self.query_columns, self.expected)
        owner.close()

    def test_every_receipt_field_is_decision_bearing(self):
        for success in (False, True):
            baseline = dict(owner_api._RECEIPT_COMMON)
            baseline.update(
                output_d2h_copy_call_count=1 if success else 0,
                host_blocking_boundary_count=2 if success else 1,
                output_d2h_bytes=60_000 if success else 0,
            )
            owner_api._validate_receipt(baseline, success)
            for field in baseline:
                mutated = dict(baseline)
                mutated[field] ^= 1
                with self.subTest(success=success, field=field):
                    with self.assertRaises(owner_api.ParticleReceiptError):
                        owner_api._validate_receipt(mutated, success)

    def test_source_and_descriptor_mismatch_reject_before_prepare(self):
        bad_source_library = _FakeLibrary(
            self.source + b" ", self.descriptor, self.expected
        )
        with self.assertRaisesRegex(owner_api.ParticleAuthorityError, "source"):
            owner_api.prepare_particle_product_owner(
                bad_source_library, self.prebuilt, self.static_input
            )
        self.assertFalse(bad_source_library.prepared)

        bad_descriptor = self.descriptor + b" "
        bad_descriptor_library = _FakeLibrary(
            self.source, bad_descriptor, self.expected
        )
        with self.assertRaisesRegex(owner_api.ParticleAuthorityError, "descriptor"):
            owner_api.prepare_particle_product_owner(
                bad_descriptor_library, self.prebuilt, self.static_input
            )
        self.assertFalse(bad_descriptor_library.prepared)

        structurally_bad = _descriptor_bytes(self.source, mutate=True)
        rebound = replace(
            self.prebuilt,
            descriptor_sha256=hashlib.sha256(structurally_bad).hexdigest(),
        )
        structurally_bad_library = _FakeLibrary(
            self.source, structurally_bad, self.expected
        )
        with self.assertRaisesRegex(
            owner_api.ParticleAuthorityError, "exact frozen descriptor"
        ):
            owner_api.prepare_particle_product_owner(
                structurally_bad_library, rebound, self.static_input
            )
        self.assertFalse(structurally_bad_library.prepared)

    def test_exact_dtype_shape_and_contiguity_are_required(self):
        with self.assertRaisesRegex(owner_api.ParticleInputError, "vertices dtype"):
            owner_api.ParticleStaticInput(
                self.vertices.astype(np.float64),
                self.triangles,
                self.front,
                self.back,
            )
        with self.assertRaisesRegex(owner_api.ParticleInputError, "triangles shape"):
            owner_api.ParticleStaticInput(
                self.vertices,
                self.triangles[:-1],
                self.front,
                self.back,
            )
        with self.assertRaisesRegex(
            owner_api.ParticleInputError, "triangles must be C-contiguous"
        ):
            owner_api.ParticleStaticInput(
                self.vertices,
                self.triangles[:, ::-1],
                self.front,
                self.back,
            )

        _, owner = self._owner()
        with self.assertRaisesRegex(owner_api.ParticleInputError, "ox dtype"):
            owner_api.ParticleQueryColumns(
                self.query_columns.ox.astype(np.float64),
                *self.query_columns.native_order()[1:],
            )
        with self.assertRaisesRegex(owner_api.ParticleInputError, "ox shape"):
            owner_api.ParticleQueryColumns(
                self.query_columns.ox[:-1],
                *self.query_columns.native_order()[1:],
            )
        with self.assertRaisesRegex(
            owner_api.ParticleInputError, "ox must be C-contiguous"
        ):
            doubled = np.ones(owner_api.QUERY_COUNT * 2, dtype=np.float32)
            owner_api.ParticleQueryColumns(
                doubled[::2], *self.query_columns.native_order()[1:]
            )
        with self.assertRaisesRegex(
            owner_api.ParticleInputError, "seven contiguous ParticleQueryColumns"
        ):
            owner.execute_complete(
                np.ones((owner_api.QUERY_COUNT, 7), dtype=np.float32),
                self.expected,
            )
        with self.assertRaisesRegex(
            owner_api.ParticleInputError, "expected_output dtype"
        ):
            owner.execute_complete(
                self.query_columns, self.expected.astype(np.int64)
            )
        with self.assertRaisesRegex(
            owner_api.ParticleInputError, "expected_output shape"
        ):
            owner.execute_complete(self.query_columns, self.expected[:-1])
        owner.close()

    def test_no_tolist_or_python_row_iteration(self):
        guarded_static = owner_api.ParticleStaticInput(
            self.vertices.view(_NoPythonRows),
            self.triangles.view(_NoPythonRows),
            self.front.view(_NoPythonRows),
            self.back.view(_NoPythonRows),
        )
        library = _FakeLibrary(
            self.source, self.descriptor, self.expected
        )
        owner = owner_api.prepare_particle_product_owner(
            library, self.prebuilt, guarded_static
        )
        guarded_queries = owner_api.ParticleQueryColumns(
            *(column.view(_NoPythonRows)
              for column in self.query_columns.native_order())
        )
        output = owner.execute_complete(
            guarded_queries, self.expected.view(_NoPythonRows)
        )
        self.assertTrue(np.array_equal(output, self.expected))
        module_source = Path(owner_api.__file__).read_text(encoding="utf-8")
        self.assertNotIn(".tolist(", module_source)
        execute_source = module_source[
            module_source.index("    def execute_complete("):
            module_source.index("    def close(", module_source.index("    def execute_complete("))
        ]
        self.assertNotIn("ascontiguousarray", execute_source)
        self.assertNotIn("queries.T", execute_source)
        self.assertNotIn("np.empty", execute_source)
        owner.close()

    def test_oracle_mismatch_is_inside_complete_execute(self):
        _, owner = self._owner()
        wrong = self.expected.copy()
        wrong[0, 2] ^= np.uint32(1)
        with self.assertRaises(owner_api.ParticleOracleMismatch):
            owner.execute_complete(self.query_columns, wrong)
        owner.close()

    def test_ctypes_layout_matches_live_native_abi(self):
        self.assertEqual(ctypes.sizeof(owner_api._ParticleControl), 16)
        self.assertEqual(ctypes.sizeof(owner_api._ParticleFastReceipt), 96)
        self.assertEqual(
            [name for name, _ in owner_api._ParticleFastReceipt._fields_],
            [
                "schema_version",
                "optix_launch_count",
                "query_count",
                "query_h2d_copy_call_count",
                "control_reset_h2d_copy_call_count",
                "parameter_h2d_copy_call_count",
                "control_d2h_copy_call_count",
                "output_d2h_copy_call_count",
                "host_blocking_boundary_count",
                "status_before_output",
                "query_h2d_bytes",
                "control_reset_h2d_bytes",
                "parameter_h2d_bytes",
                "control_d2h_bytes",
                "output_d2h_bytes",
                "output_d2h_after_status_failure",
                "boundary_owner_table_bytes",
            ],
        )


if __name__ == "__main__":
    unittest.main()
