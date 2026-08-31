"""Adversarial binding and lifecycle regressions for Goal5833."""

from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest import mock

from rtdsl.physical_execution_provenance import (
    _register_loaded_provider_identity,
    _unregister_loaded_provider_identity,
)
from rtdsl import v4_sphere_prepared_runtime as runtime


class Goal5833SphereRuntimeBindingTest(unittest.TestCase):
    def test_authorized_path_must_be_the_provider_actually_loaded(self):
        library = ctypes.pythonapi
        symbol = library.Py_GetVersion
        actual = runtime._mapped_symbol_library_path(symbol)
        digest = hashlib.sha256(actual.read_bytes()).hexdigest()
        _register_loaded_provider_identity(library, actual, digest)
        with tempfile.TemporaryDirectory() as root:
            path_b = Path(root, "b.so")
            path_b.write_bytes(b"provider-b")
            try:
                self.assertEqual(
                    runtime._loaded_native_identity(
                        library, actual, symbol=symbol),
                    (actual, digest),
                )
                with self.assertRaisesRegex(
                        RuntimeError, "differs from the loaded provider"):
                    runtime._loaded_native_identity(
                        library, path_b, symbol=symbol)
            finally:
                _unregister_loaded_provider_identity(library)

    def test_registered_claim_cannot_substitute_a_different_mapped_dso(self):
        library = ctypes.pythonapi
        symbol = library.Py_GetVersion
        actual = runtime._mapped_symbol_library_path(symbol)
        with tempfile.TemporaryDirectory() as root:
            claimed = Path(root, "claimed-provider.so")
            claimed.write_bytes(b"not-the-mapped-python-provider")
            digest = hashlib.sha256(claimed.read_bytes()).hexdigest()
            _register_loaded_provider_identity(library, claimed, digest)
            try:
                with self.assertRaisesRegex(
                        RuntimeError, "OS-mapped ABI owner"):
                    runtime._loaded_native_identity(
                        library, claimed, symbol=symbol)
            finally:
                _unregister_loaded_provider_identity(library)

    def test_loaded_provider_bytes_cannot_change_after_registration(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "provider.so")
            path.write_bytes(b"before")
            library = SimpleNamespace(_name=str(path))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            _register_loaded_provider_identity(library, path, digest)
            try:
                path.write_bytes(b"after")
                with mock.patch.object(
                        runtime, "_mapped_symbol_library_path",
                        return_value=path.resolve()):
                    with self.assertRaisesRegex(RuntimeError, "bytes changed"):
                        runtime._loaded_native_identity(
                            library, path, symbol=object())
            finally:
                _unregister_loaded_provider_identity(library)

    def test_traversal_receipt_must_name_the_same_provider(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "provider.so")
            path.write_bytes(b"provider")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = {
                "provider_library_path": str(path.resolve()),
                "provider_library_sha256": digest,
            }
            runtime._require_traversal_provider_binding(
                receipt, native_path=path.resolve(), native_sha256=digest)
            with self.assertRaisesRegex(RuntimeError, "differs"):
                runtime._require_traversal_provider_binding(
                    {**receipt, "provider_library_sha256": "0" * 64},
                    native_path=path.resolve(), native_sha256=digest)

    def test_host_projection_commitments_are_input_sensitive(self):
        schema = SimpleNamespace(
            center_field_id="centers", radius_field_id="radii",
            application_id_field_id="ids", query_field_id="queries",
            output_field_id="outputs", status_field_id="status",
        )
        authority = SimpleNamespace(schema=schema)
        self.assertNotEqual(
            runtime._field_mapping_commitment(authority),
            runtime._field_mapping_commitment(SimpleNamespace(schema=SimpleNamespace(
                **{**vars(schema), "status_field_id": "different-status"}))),
        )
        self.assertNotEqual(
            runtime._static_input_commitment(((2.0, 0.0, 0.0),), (1.0,), (7,)),
            runtime._static_input_commitment(((2.0, 0.0, 0.0),), (1.5,), (7,)),
        )
        self.assertNotEqual(
            runtime._query_commitment(((0.0, 0.0, 0.0, 4.0, 0.0, 0.0),)),
            runtime._query_commitment(((0.0, 0.0, 0.0, 5.0, 0.0, 0.0),)),
        )

    def test_native_runtime_versions_must_equal_target_authority(self):
        descriptor = {
            "compiled_optix_major": 9,
            "compiled_optix_minor": 0,
            "compiled_optix_patch": 0,
            "cuda_compute_capability_major": 8,
            "cuda_compute_capability_minor": 9,
        }
        target = SimpleNamespace(optix_sdk="9.0.0", compute_capability="8.9")
        runtime._require_native_target_binding(descriptor, target)
        with self.assertRaisesRegex(RuntimeError, "OptiX SDK differs"):
            runtime._require_native_target_binding(
                descriptor,
                SimpleNamespace(optix_sdk="9.1.0", compute_capability="8.9"),
            )
        with self.assertRaisesRegex(RuntimeError, "compute capability differs"):
            runtime._require_native_target_binding(
                descriptor,
                SimpleNamespace(optix_sdk="9.0.0", compute_capability="8.6"),
            )

    def test_descriptor_failure_destroys_successfully_prepared_token(self):
        destroyed: list[int] = []
        native_sha = "a" * 64
        schema = SimpleNamespace(
            center_field_id="centers", radius_field_id="radii",
            application_id_field_id="ids", query_field_id="queries",
            output_field_id="outputs", status_field_id="status",
        )
        fresh = SimpleNamespace(
            target=SimpleNamespace(native_sha256=native_sha),
            authority_nonce="nonce", schema=schema,
        )

        def prepare(_ptx, _centers, _radii, _ids, _count, token, _error, _capacity):
            token._obj.value = 29
            return 0

        def destroy(token, _error, _capacity):
            destroyed.append(int(token))
            return 0

        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "provider.so")
            path.write_bytes(b"provider")
            with mock.patch.object(runtime, "_fresh", return_value=fresh), \
                    mock.patch.object(
                        runtime, "verify_reference_sphere_contents",
                        return_value=(((2.0, 0.0, 0.0),), (1.0,), (7,))), \
                    mock.patch.object(
                        runtime, "consume_verified_sphere_executable",
                        return_value="ptx"), \
                    mock.patch.object(
                        runtime, "_loaded_native_identity",
                        return_value=(path.resolve(), native_sha)), \
                    mock.patch.object(
                        runtime, "_configure",
                        return_value=(prepare, object(), object(), destroy)), \
                    mock.patch.object(
                        runtime, "_read_native_descriptor",
                        side_effect=RuntimeError("bad descriptor")):
                with self.assertRaisesRegex(RuntimeError, "bad descriptor"):
                    runtime.PreparedBuiltinSphereOwner(
                        authority=object(), plan=object(), abi=object(),
                        executable=object(), centers=object(), radii=object(),
                        application_ids=object(), library=object(),
                        native_library_path=path,
                    )
        self.assertEqual(destroyed, [29])

    @staticmethod
    def _guard_only_owner() -> runtime.PreparedBuiltinSphereOwner:
        owner = runtime.PreparedBuiltinSphereOwner.__new__(
            runtime.PreparedBuiltinSphereOwner)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        owner._token = 13
        owner._execution_count = 0
        owner._native_sha = "a" * 64
        owner._ptx_sha = "b" * 64
        owner._physical_receipt = {}
        owner._destroy = lambda _token, _error, _capacity: 0
        return owner

    def test_owner_guards_serialization_reentry_thread_process_and_close(self):
        owner = self._guard_only_owner()
        with self.assertRaisesRegex(RuntimeError, "cannot be serialized"):
            owner.__getstate__()
        owner._active.acquire()
        try:
            with self.assertRaisesRegex(RuntimeError, "during execution"):
                owner.close()
        finally:
            owner._active.release()

        thread_errors: list[str] = []

        def cross_thread():
            try:
                owner.lifecycle_receipt
            except RuntimeError as exc:
                thread_errors.append(str(exc))

        thread = threading.Thread(target=cross_thread)
        thread.start(); thread.join()
        self.assertEqual(thread_errors, [
            "prepared built-in sphere owner crossed thread boundary"])
        with mock.patch.object(runtime.os, "getpid", return_value=owner._pid + 1):
            with self.assertRaisesRegex(RuntimeError, "crossed process boundary"):
                owner.lifecycle_receipt
        owner.close()
        self.assertTrue(owner._closed)
        with self.assertRaisesRegex(RuntimeError, "is closed"):
            owner.close()

    def test_prepared_owner_can_execute_repeatedly(self):
        with tempfile.TemporaryDirectory() as root:
            native_path = Path(root, "provider.so")
            native_path.write_bytes(b"provider")
            native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
            owner = self._guard_only_owner()
            owner._centers = ((2.0, 0.0, 0.0),)
            owner._radii = (0.5,)
            owner._application_ids = (7,)
            owner._fresh = SimpleNamespace(
                authority_nonce="nonce", target=SimpleNamespace())
            owner._plan = SimpleNamespace(plan_sha256="c" * 64)
            owner._abi = SimpleNamespace(abi_sha256="d" * 64)
            owner._library = object()
            owner._describe = object()
            owner._native_descriptor = {}
            owner._native_path = native_path.resolve()
            owner._native_sha = native_sha

            def execute(
                _token, _starts, _ends, count, output_0, output_1, output_2,
                observed_primitive, observed_kind, observed_t, _statuses,
                counters, _error, _capacity,
            ):
                self.assertEqual(count, 1)
                output_0[0] = 1; output_1[0] = 123; output_2[0] = 7
                observed_primitive[0] = 0; observed_kind[0] = 0
                observed_t[0] = ctypes.c_float(0.375).value
                counters[1] = 1
                return 0

            owner._execute = execute
            receipt = {
                "physical_executor_classification": "optix_traversal_observed",
                "provider_library_path": str(native_path.resolve()),
                "provider_library_sha256": native_sha,
            }
            audit = SimpleNamespace(
                finish=mock.Mock(return_value=receipt), abort=mock.Mock())
            with mock.patch.object(
                    runtime.OptixTraversalAuditSession, "open",
                    return_value=audit), mock.patch.object(
                        runtime, "validate_traversal_receipt"), mock.patch.object(
                        runtime, "_read_native_descriptor", return_value={}), \
                    mock.patch.object(runtime, "_require_native_descriptor_transition"), \
                    mock.patch.object(runtime, "_require_native_target_binding"), \
                    mock.patch.object(runtime, "_require_native_execution_fingerprints"):
                first = owner.execute((((0.0, 0.0, 0.0), (4.0, 0.0, 0.0)),))
                second = owner.execute((((0.0, 0.0, 0.0), (4.0, 0.0, 0.0)),))
            self.assertEqual(first.outputs, second.outputs)
            self.assertEqual(owner.lifecycle_receipt["execution_count"], 2)


if __name__ == "__main__":
    unittest.main()
