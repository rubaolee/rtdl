from __future__ import annotations

import ctypes
from dataclasses import replace
import dis
import gc
import hashlib
import os
from pathlib import Path
import select
import signal
import sys
from types import SimpleNamespace
import tempfile
import threading
import unittest
from unittest.mock import patch

from rtdsl import physical_execution_provenance as provenance
import rtdsl.v4_rtdlexe as runtime


class _FakeReadiness:
    def __init__(self, *, fail_close_once: bool = False) -> None:
        self.owner_pid = os.getpid()
        self.released = False
        self.close_calls = 0
        self._fail_close_once = fail_close_once

    def check(self) -> None:
        if self.released:
            runtime._fail("RX037_USE_AFTER_CLOSE", "provider_ready.cuda", "released")
        if self.owner_pid != os.getpid():
            runtime._fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.cuda",
                "different process")

    def close(self) -> None:
        if self.released:
            return
        self.close_calls += 1
        if self._fail_close_once and self.close_calls == 1:
            raise KeyboardInterrupt("injected CUDA retain release interruption")
        self.released = True


class _LeaseOwner:
    def __init__(self, library) -> None:
        self.library = library
        self.closed = False

    def execute(self, _batch, *, diagnostics):
        return (), None, {"ok": True}, (), None

    def close(self) -> None:
        if not self.closed:
            runtime._release_native_library_image(self.library)
            self.closed = True


class _CudaFunction:
    def __init__(self, callback) -> None:
        self.callback = callback
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        return self.callback(*args)


def _fake_cuda_driver(
    *, first_context: int = 0x1111, primary_context: int = 0x2222,
    primary_select_status: int = 0, restore_status: int = 0,
):
    calls = {"set": [], "retain": 0, "release": 0}

    def device_get(device_pointer, _ordinal):
        device_pointer._obj.value = 0
        return 0

    def capability(major_pointer, minor_pointer, _device):
        major_pointer._obj.value = 8
        minor_pointer._obj.value = 9
        return 0

    def get_current(context_pointer):
        context_pointer._obj.value = first_context
        return 0

    def retain(context_pointer, _device):
        calls["retain"] += 1
        context_pointer._obj.value = primary_context
        return 0

    def set_current(context):
        value = int(context.value or 0)
        calls["set"].append(value)
        if value == primary_context:
            return primary_select_status
        return restore_status

    def release(_device):
        calls["release"] += 1
        return 0

    driver = SimpleNamespace(
        cuInit=_CudaFunction(lambda _flags: 0),
        cuDeviceGet=_CudaFunction(device_get),
        cuDeviceComputeCapability=_CudaFunction(capability),
        cuCtxGetCurrent=_CudaFunction(get_current),
        cuCtxSetCurrent=_CudaFunction(set_current),
        cuDevicePrimaryCtxRetain=_CudaFunction(retain),
        cuDevicePrimaryCtxRelease=_CudaFunction(release),
    )
    return driver, calls


class Goal5807ProviderReadyRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self._old_cache = runtime._NATIVE_IMAGE_CACHE
        self._old_next_lease = runtime._NATIVE_IMAGE_CACHE_NEXT_LEASE
        self._old_cache_pid = runtime._NATIVE_IMAGE_CACHE_PID
        self._old_fork_poisoned = runtime._NATIVE_IMAGE_CACHE_FORK_POISONED
        self._old_load_poisoned = runtime._NATIVE_IMAGE_CACHE_LOAD_POISONED
        self._old_load_failure = runtime._NATIVE_IMAGE_CACHE_LOAD_FAILURE
        self._old_touched = runtime._NATIVE_RUNTIME_TOUCHED
        self._old_cuda_ready_lock = runtime._CUDA_PRIMARY_READY_LOCK
        self._old_cuda_ready_pid = runtime._CUDA_PRIMARY_READY_PID
        self._old_cuda_ready_state = runtime._CUDA_PRIMARY_READY_STATE
        runtime._NATIVE_IMAGE_CACHE = {}
        runtime._NATIVE_IMAGE_CACHE_NEXT_LEASE = 0
        runtime._NATIVE_IMAGE_CACHE_PID = os.getpid()
        runtime._NATIVE_IMAGE_CACHE_FORK_POISONED = False
        runtime._NATIVE_IMAGE_CACHE_LOAD_POISONED = False
        runtime._NATIVE_IMAGE_CACHE_LOAD_FAILURE = None
        runtime._NATIVE_RUNTIME_TOUCHED = False
        runtime._CUDA_PRIMARY_READY_LOCK = threading.RLock()
        runtime._CUDA_PRIMARY_READY_PID = os.getpid()
        runtime._CUDA_PRIMARY_READY_STATE = None
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            self._old_provenance = dict(provenance._LOADED_PROVIDER_IDENTITIES)
            self._old_audit = dict(provenance._AUDIT_ABI_REGISTERED)
            provenance._LOADED_PROVIDER_IDENTITIES.clear()
            provenance._AUDIT_ABI_REGISTERED.clear()
        self._descriptors: list[int] = []
        self.seals = patch.object(runtime, "_native_image_seals", return_value=15)
        self.seals.start()

    def tearDown(self) -> None:
        self.seals.stop()
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            provenance._LOADED_PROVIDER_IDENTITIES.clear()
            provenance._LOADED_PROVIDER_IDENTITIES.update(self._old_provenance)
            provenance._AUDIT_ABI_REGISTERED.clear()
            provenance._AUDIT_ABI_REGISTERED.update(self._old_audit)
        runtime._NATIVE_IMAGE_CACHE = self._old_cache
        runtime._NATIVE_IMAGE_CACHE_NEXT_LEASE = self._old_next_lease
        runtime._NATIVE_IMAGE_CACHE_PID = self._old_cache_pid
        runtime._NATIVE_IMAGE_CACHE_FORK_POISONED = self._old_fork_poisoned
        runtime._NATIVE_IMAGE_CACHE_LOAD_POISONED = self._old_load_poisoned
        runtime._NATIVE_IMAGE_CACHE_LOAD_FAILURE = self._old_load_failure
        runtime._NATIVE_RUNTIME_TOUCHED = self._old_touched
        runtime._CUDA_PRIMARY_READY_LOCK = self._old_cuda_ready_lock
        runtime._CUDA_PRIMARY_READY_PID = self._old_cuda_ready_pid
        runtime._CUDA_PRIMARY_READY_STATE = self._old_cuda_ready_state
        for descriptor in self._descriptors:
            try:
                os.close(descriptor)
            except OSError:
                pass
        self.temporary.cleanup()

    def _loaded(self, digest: str):
        descriptor = {"exact": "native-producer-v1"}
        return runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=self.root / "artifact.rtdlexe",
                authority_path=self.root / "authority.json",
                authority_sha256="1" * 64,
                deployment_id="goal5807-test",
                trust_root_sha256="2" * 64,
                trust_package_sha256="3" * 64,
                artifact_sha256="4" * 64,
                executable_identity_sha256="5" * 64,
                family=runtime._BOUNDED,
                composed_ptx="// exact test PTX\n",
                product_projection={
                    "target_toolchain": {
                        "native_library_sha256": digest,
                        "compute_capability": (8, 9),
                    },
                    "runtime": {
                        "native_abi": (
                            "rtdl.v4.prepared_bounded_relation_callback.v7"),
                        "capacity": 8,
                        "minimum_overlap_f32": 0.0,
                    },
                    "execution_schema": {
                        "native_producer_descriptor": descriptor,
                    },
                },
            )), descriptor

    def _distinct_loaded(self, loaded, marker: str):
        """Issue a different exact loader capability for the same provider."""

        marker_sha = hashlib.sha256(marker.encode("utf-8")).hexdigest()
        identity_sha = hashlib.sha256(
            (marker + "-identity").encode("utf-8")).hexdigest()
        return runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=self.root / f"{marker}.rtdlexe",
                authority_path=loaded.authority_path,
                authority_sha256=loaded.authority_sha256,
                deployment_id=f"goal5809-{marker}",
                trust_root_sha256=loaded.trust_root_sha256,
                trust_package_sha256=loaded.trust_package_sha256,
                artifact_sha256=marker_sha,
                executable_identity_sha256=identity_sha,
                family=loaded.family,
                composed_ptx=f"// exact {marker} PTX\n",
                product_projection=runtime._plain(
                    loaded.product_projection),
            ))

    def _binding_lease(self):
        source = self.root / "librtdl_optix.so"
        source.write_bytes(b"goal5807 exact provider bytes")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        sealed_copy = self.root / "sealed-native-image"
        sealed_copy.write_bytes(source.read_bytes())
        descriptor = os.open(sealed_copy, os.O_RDONLY)
        self._descriptors.append(descriptor)
        entry = runtime._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=0x123456),
            sha256=digest,
            source_path=source,
            image_descriptor=descriptor,
            image_seals=15,
            loader_alias="/private/exact-provider.so",
            owner_pid=os.getpid(),
            usable=True,
        )
        runtime._NATIVE_IMAGE_CACHE[digest] = entry
        lease = runtime._acquire_native_image_lease(entry, source_path=source)
        runtime._register_native_image_lease_provenance(
            lease, source_path=source, digest=digest)
        return source, digest, entry, lease

    def _bind(self, *, readiness=None):
        source, digest, entry, lease = self._binding_lease()
        loaded, expected_descriptor = self._loaded(digest)
        readiness = readiness or _FakeReadiness()
        loader = patch.object(
            runtime, "_load_verified_native_file_descriptor",
            return_value=lease)
        query = patch.object(
            runtime, "_query_native_producer_descriptor",
            return_value=expected_descriptor)
        acquire_cuda = patch.object(
            runtime, "_acquire_cuda_primary_context_readiness",
            return_value=readiness)
        with loader as loader_mock, query as query_mock, \
                acquire_cuda as cuda_mock:
            provider = loaded.bind_provider(source)
        return {
            "source": source, "digest": digest, "entry": entry,
            "binding_lease": lease, "loaded": loaded,
            "provider": provider, "readiness": readiness,
            "loader": loader_mock, "query": query_mock,
            "cuda": cuda_mock,
        }

    def _interrupt_before_last_store(
        self, *, code, opname: str, argval: str, operation, message: str,
    ) -> None:
        offsets = [
            instruction.offset
            for instruction in dis.get_instructions(code)
            if instruction.opname == opname and instruction.argval == argval
        ]
        self.assertTrue(offsets, f"no {opname} {argval} in {code.co_name}")
        target_offset = max(offsets)
        fired = False

        def trace(frame, event, _argument):
            nonlocal fired
            if event == "call" and frame.f_code is code:
                frame.f_trace_opcodes = True
                return trace
            if event == "opcode" and frame.f_code is code \
                    and frame.f_lasti == target_offset:
                fired = True
                raise KeyboardInterrupt(message)
            return trace

        sys.settrace(trace)
        try:
            with self.assertRaisesRegex(KeyboardInterrupt, message):
                operation()
        finally:
            sys.settrace(None)
        self.assertTrue(fired, f"opcode interrupt did not fire in {code.co_name}")

    def _interrupt_on_return(
        self, *, code, operation, message: str,
    ) -> None:
        """Raise after callee publication but before the caller stores it."""

        fired = False

        def profile(frame, event, _argument):
            nonlocal fired
            if event == "return" and frame.f_code is code:
                fired = True
                raise KeyboardInterrupt(message)

        sys.setprofile(profile)
        try:
            with self.assertRaisesRegex(KeyboardInterrupt, message):
                operation()
        finally:
            sys.setprofile(None)
        self.assertTrue(fired, f"return interrupt did not fire in {code.co_name}")

    @staticmethod
    def _entry_provenance_count(entry) -> int:
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            return sum(
                getattr(row[0], "_rtdl_native_cache_entry", None) is entry
                for row in provenance._LOADED_PROVIDER_IDENTITIES.values()
            )

    @staticmethod
    def _install_token_tracking_bounded_native(
            entry, *, interrupt_after_prepare: bool = False):
        active_tokens = set()
        destroy_calls = []

        def prepare(*arguments):
            arguments[6]._obj.value = 0x1234
            active_tokens.add(0x1234)
            if interrupt_after_prepare:
                raise KeyboardInterrupt("native token side effect published")
            return 0

        def destroy(*arguments):
            token = int(arguments[0]._obj.value)
            destroy_calls.append(token)
            active_tokens.discard(token)
            arguments[0]._obj.value = 0
            return 0

        callbacks = {
            "rtdl_optix_v4_prepare_bounded_relation_callback_v1": prepare,
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v7": (
                lambda *_arguments: 0),
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v4": (
                lambda *_arguments: 0),
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_build_count_v1": (
                lambda *_arguments: 0),
            "rtdl_optix_v4_commit_prepared_bounded_relation_source_cache_v2": (
                lambda *_arguments: 0),
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_digest_v1": (
                lambda *_arguments: 0),
            "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v2": destroy,
        }
        for name, callback in callbacks.items():
            setattr(entry.library, name, _CudaFunction(callback))
        return active_tokens, destroy_calls

    def test_bind_nested_call_store_interrupt_releases_prepublished_lease(self):
        source, digest, entry, initial = self._binding_lease()
        runtime._release_native_library_image(initial)
        loaded, _descriptor = self._loaded(digest)
        readiness = _FakeReadiness()

        with patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                return_value=readiness):
            self._interrupt_on_return(
                code=runtime._admit_native_image_lease.__code__,
                operation=lambda: loaded.bind_provider(source),
                message="nested native lease CALL to STORE_FAST",
            )

        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())
        self.assertEqual(self._entry_provenance_count(entry), 0)

    def test_provider_lease_call_store_interrupt_releases_owner_lease(self):
        row = self._bind()
        provider = row["provider"]
        entry = row["entry"]
        binding_id = row["binding_lease"]._rtdl_native_cache_lease_id

        self._interrupt_on_return(
            code=runtime._admit_provider_ready_native_image_lease.__code__,
            operation=lambda: provider.prepare(
                runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),))),
            message="provider native lease CALL to STORE_FAST",
        )

        self.assertEqual(entry.active_lease_ids, {binding_id})
        self.assertEqual(self._entry_provenance_count(entry), 1)
        provider.close()
        self.assertEqual(entry.active_lease_ids, set())
        self.assertEqual(self._entry_provenance_count(entry), 0)

    def test_owner_return_interrupt_destroys_prepublished_native_token(self):
        row = self._bind()
        provider = row["provider"]
        entry = row["entry"]
        binding_id = row["binding_lease"]._rtdl_native_cache_lease_id
        active_tokens, destroy_calls = (
            self._install_token_tracking_bounded_native(entry))

        self._interrupt_on_return(
            code=runtime.LoadedRTDLExecutable._build_prepared_owner.__code__,
            operation=lambda: provider.prepare(
                runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),))),
            message="prepared owner CALL to STORE_FAST",
        )

        self.assertEqual(active_tokens, set())
        self.assertEqual(destroy_calls, [0x1234])
        self.assertEqual(entry.active_lease_ids, {binding_id})
        provider.close()
        self.assertEqual(entry.active_lease_ids, set())

    def test_owner_constructor_post_token_interrupt_destroys_exactly_once(self):
        row = self._bind()
        provider = row["provider"]
        entry = row["entry"]
        binding_id = row["binding_lease"]._rtdl_native_cache_lease_id
        active_tokens, destroy_calls = self._install_token_tracking_bounded_native(
            entry, interrupt_after_prepare=True)

        with self.assertRaisesRegex(
                KeyboardInterrupt, "native token side effect published"):
            provider.prepare(
                runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),)))

        self.assertEqual(active_tokens, set())
        self.assertEqual(destroy_calls, [0x1234])
        self.assertEqual(entry.active_lease_ids, {binding_id})
        provider.close()
        self.assertEqual(entry.active_lease_ids, set())

    def test_poisoned_cuda_admission_waiter_rechecks_under_lock(self):
        first_primary_select = threading.Event()
        second_outer_guard = threading.Event()
        calls = {"retain": 0, "release": 0, "primary_select": 0}

        def device_get(device_pointer, _ordinal):
            device_pointer._obj.value = 0
            return 0

        def capability(major_pointer, minor_pointer, _device):
            major_pointer._obj.value = 8
            minor_pointer._obj.value = 9
            return 0

        def get_current(context_pointer):
            context_pointer._obj.value = 0x1111
            return 0

        def retain(context_pointer, _device):
            calls["retain"] += 1
            context_pointer._obj.value = 0x2222
            return 0

        def set_current(context):
            if int(context.value or 0) == 0x2222:
                calls["primary_select"] += 1
                if calls["primary_select"] == 1:
                    first_primary_select.set()
                    if not second_outer_guard.wait(2):
                        raise AssertionError(
                            "second waiter did not pass its outer guard")
                    return 7
            return 0

        def release(_device):
            calls["release"] += 1
            return 9

        driver = SimpleNamespace(
            cuInit=_CudaFunction(lambda _flags: 0),
            cuDeviceGet=_CudaFunction(device_get),
            cuDeviceComputeCapability=_CudaFunction(capability),
            cuCtxGetCurrent=_CudaFunction(get_current),
            cuCtxSetCurrent=_CudaFunction(set_current),
            cuDevicePrimaryCtxRetain=_CudaFunction(retain),
            cuDevicePrimaryCtxRelease=_CudaFunction(release),
        )
        original_guard = runtime._native_image_cache_guard

        def guarded(*, code, identity_path):
            original_guard(code=code, identity_path=identity_path)
            if threading.current_thread().name == "cuda-second-waiter":
                second_outer_guard.set()

        outcomes = {}

        def acquire(label):
            try:
                outcomes[label] = runtime._acquire_cuda_primary_context_readiness(
                    expected_compute_capability=(8, 9))
            except BaseException as error:  # pragma: no cover - relayed below
                outcomes[label] = error

        with patch.object(runtime.ctypes, "CDLL", return_value=driver), \
                patch.object(
                    runtime, "_native_image_cache_guard", side_effect=guarded):
            first = threading.Thread(
                target=acquire, args=("first",), name="cuda-first-waiter")
            first.start()
            self.assertTrue(first_primary_select.wait(2))
            second = threading.Thread(
                target=acquire, args=("second",), name="cuda-second-waiter")
            second.start()
            first.join(3)
            second.join(3)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertIsInstance(outcomes["first"], runtime.RTDLExecutableError)
        self.assertIsInstance(outcomes["second"], runtime.RTDLExecutableError)
        self.assertEqual(outcomes["first"].code, "RX031_CUDA_DRIVER_UNAVAILABLE")
        self.assertEqual(outcomes["second"].code, "RX048_NATIVE_CACHE_QUARANTINED")
        self.assertTrue(runtime._NATIVE_IMAGE_CACHE_LOAD_POISONED)
        self.assertIsNone(runtime._CUDA_PRIMARY_READY_STATE)
        self.assertEqual(calls["retain"], 1)
        self.assertEqual(calls["release"], 1)

    def test_bind_once_prepare_never_rereads_path_and_leases_are_independent(self):
        row = self._bind()
        provider = row["provider"]
        frozen_provenance = provenance._registered_loaded_provider_identity(
            row["binding_lease"])[0]
        # Windows prevents unlink/replace while this test's descriptor is open;
        # overwriting the mutable source spelling still proves that provider
        # prepare neither rereads it nor lets its later bytes relabel provenance.
        row["source"].write_bytes(b"different bytes after the exact bind")

        def owner_factory(*, library, **_kwargs):
            return _LeaseOwner(library)

        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))
        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=owner_factory), patch.object(
                runtime, "_open_regular_readonly",
                side_effect=AssertionError("provider prepare reopened raw path")), \
                patch.object(
                    Path, "resolve",
                    side_effect=AssertionError("provider prepare resolved later path")):
            first = provider.prepare(static_input)
            second = provider.prepare(static_input)

        row["loader"].assert_called_once()
        row["query"].assert_called_once()
        row["cuda"].assert_called_once_with(
            expected_compute_capability=(8, 9))
        self.assertEqual(provider.native_library_path, row["source"])
        self.assertEqual(provider.native_library_sha256, row["digest"])
        self.assertEqual(
            provider.cache_entry_identity,
            f"{os.getpid()}:{row['digest']}")
        leases = (first._owner.library, second._owner.library)
        self.assertNotEqual(
            leases[0]._rtdl_native_cache_lease_id,
            leases[1]._rtdl_native_cache_lease_id)
        self.assertNotEqual(
            leases[0]._rtdl_native_cache_lease_id,
            row["binding_lease"]._rtdl_native_cache_lease_id)
        self.assertEqual(row["entry"].active_lease_ids, {
            row["binding_lease"]._rtdl_native_cache_lease_id,
            leases[0]._rtdl_native_cache_lease_id,
            leases[1]._rtdl_native_cache_lease_id,
        })
        for lease in leases:
            registered = provenance._registered_loaded_provider_identity(lease)
            self.assertEqual(registered, (frozen_provenance, row["digest"]))

        provider.close()
        self.assertTrue(provider.closed)
        self.assertTrue(row["readiness"].released)
        self.assertEqual(len(row["entry"].active_lease_ids), 2)
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            provider.prepare(static_input)
        self.assertEqual(rejected.exception.code, "RX037_USE_AFTER_CLOSE")
        first.close()
        self.assertEqual(len(row["entry"].active_lease_ids), 1)
        second.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_runtime_session_reuses_one_provider_across_loaded_executables(self):
        row = self._bind()
        first_loaded = row["loaded"]
        second_loaded, expected_descriptor = self._loaded(row["digest"])
        second_projection = dict(second_loaded.product_projection)
        second_loaded = runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=self.root / "second-artifact.rtdlexe",
                authority_path=second_loaded.authority_path,
                authority_sha256=second_loaded.authority_sha256,
                deployment_id="goal5808-second-test",
                trust_root_sha256=second_loaded.trust_root_sha256,
                trust_package_sha256=second_loaded.trust_package_sha256,
                artifact_sha256="6" * 64,
                executable_identity_sha256="7" * 64,
                family=second_loaded.family,
                composed_ptx="// distinct exact second test PTX\n",
                product_projection=second_projection,
            ))
        with patch.object(
                runtime.LoadedRTDLExecutable, "bind_provider",
                return_value=row["provider"]) as bind_provider:
            session = first_loaded.open_runtime_session(row["source"])
        bind_provider.assert_called_once_with(row["source"])

        owners = []

        def owner_factory(*, library, artifact_identity, **_kwargs):
            owner = _LeaseOwner(library)
            owner.artifact_identity = artifact_identity
            owners.append(owner)
            return owner

        # Later pathname bytes are untrusted and must not be reopened by either
        # executable.  The producer descriptor is queried from the one live,
        # sealed provider capability for each new executable contract.
        row["source"].write_bytes(b"mutable pathname changed after session open")
        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))
        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=owner_factory), patch.object(
                runtime, "_query_native_producer_descriptor",
                return_value=expected_descriptor) as descriptor_query, \
                patch.object(
                    runtime, "_open_regular_readonly",
                    side_effect=AssertionError("runtime session reopened path")), \
                patch.object(
                    Path, "resolve",
                    side_effect=AssertionError("runtime session resolved path")):
            first = session.prepare(first_loaded, static_input)
            second = session.prepare(second_loaded, static_input)

        self.assertEqual(descriptor_query.call_count, 1)
        self.assertEqual([owner.artifact_identity for owner in owners], [
            first_loaded.executable_identity_sha256,
            second_loaded.executable_identity_sha256,
        ])
        self.assertEqual(session.native_library_sha256, row["digest"])
        self.assertEqual(session.cache_entry_identity,
                         row["provider"].cache_entry_identity)
        self.assertEqual(len(row["entry"].active_lease_ids), 3)
        session.close()
        self.assertTrue(session.closed)
        self.assertEqual(len(row["entry"].active_lease_ids), 2)
        first.close(); second.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_runtime_session_checks_descriptor_once_per_exact_executable(self):
        row = self._bind()
        first_loaded = row["loaded"]
        second_loaded, expected_descriptor = self._loaded(row["digest"])
        second_loaded = runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=self.root / "second-cache-artifact.rtdlexe",
                authority_path=second_loaded.authority_path,
                authority_sha256=second_loaded.authority_sha256,
                deployment_id="goal5809-second-cache-test",
                trust_root_sha256=second_loaded.trust_root_sha256,
                trust_package_sha256=second_loaded.trust_package_sha256,
                artifact_sha256="6" * 64,
                executable_identity_sha256="7" * 64,
                family=second_loaded.family,
                composed_ptx="// distinct descriptor-cache test PTX\n",
                product_projection=runtime._plain(
                    second_loaded.product_projection),
            ))
        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        owners = []

        def owner_factory(*, library, **_kwargs):
            owner = _LeaseOwner(library)
            owners.append(owner)
            return owner

        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))
        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=owner_factory), patch.object(
                runtime, "_query_native_producer_descriptor",
                return_value=expected_descriptor) as descriptor_query:
            # The seed reuses bind-time admission.  First use of the second
            # exact executable is admitted, and later owners of either do not
            # repeat the static FFI.
            prepared = [
                session.prepare(first_loaded, static_input),
                session.prepare(first_loaded, static_input),
                session.prepare(second_loaded, static_input),
                session.prepare(second_loaded, static_input),
            ]

        self.assertEqual(descriptor_query.call_count, 1)
        self.assertEqual(len(session._descriptor_admission_seals), 2)
        session.close()
        for owner in prepared:
            owner.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_runtime_session_serializes_first_descriptor_admission(self):
        row = self._bind()
        loaded = self._distinct_loaded(
            row["loaded"], "concurrent-descriptor-admission")
        expected_descriptor = loaded.product_projection[
            "execution_schema"]["native_producer_descriptor"]
        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))
        start = threading.Barrier(8)
        results = []
        failures = []
        collection_lock = threading.Lock()

        def owner_factory(*, library, **_kwargs):
            return _LeaseOwner(library)

        def worker() -> None:
            try:
                start.wait()
                prepared = session.prepare(loaded, static_input)
                with collection_lock:
                    results.append(prepared)
            except BaseException as error:  # pragma: no cover - assertion path
                with collection_lock:
                    failures.append(error)

        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=owner_factory), patch.object(
                runtime, "_query_native_producer_descriptor",
                return_value=runtime._plain(expected_descriptor)) \
                as descriptor_query:
            threads = [threading.Thread(target=worker) for _ in range(8)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=5.0)

        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(failures, [])
        self.assertEqual(len(results), 8)
        self.assertEqual(descriptor_query.call_count, 1)
        self.assertEqual(len(session._descriptor_admission_seals), 2)
        session.close()
        for prepared in results:
            prepared.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_runtime_session_does_not_cache_failed_descriptor_admission(self):
        row = self._bind()
        loaded = self._distinct_loaded(
            row["loaded"], "failed-descriptor-admission")
        expected_descriptor = runtime._plain(loaded.product_projection[
            "execution_schema"]["native_producer_descriptor"])
        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))

        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=lambda *, library, **_kwargs: _LeaseOwner(library)), \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    side_effect=[{"wrong": "descriptor"}, expected_descriptor]) \
                as descriptor_query:
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                session.prepare(loaded, static_input)
            self.assertEqual(
                rejected.exception.code,
                "RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH")
            self.assertEqual(
                session._descriptor_admission_seals,
                {row["loaded"]._runtime_session_snapshot_seal})
            prepared = session.prepare(loaded, static_input)

        self.assertEqual(descriptor_query.call_count, 2)
        self.assertEqual(len(session._descriptor_admission_seals), 2)
        prepared.close()
        session.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_descriptor_admission_cache_is_not_shared_between_sessions(self):
        row = self._bind()
        loaded = row["loaded"]
        later_loaded = self._distinct_loaded(
            loaded, "cross-session-descriptor-admission")
        expected_descriptor = runtime._plain(loaded.product_projection[
            "execution_schema"]["native_producer_descriptor"])

        second_binding_lease = runtime._acquire_native_image_lease(
            row["entry"], source_path=row["source"])
        runtime._register_native_image_lease_provenance(
            second_binding_lease, source_path=row["source"],
            digest=row["digest"])
        second_provider = runtime.ProviderReadyRTDLExecutable(
            loaded=loaded, binding_library=second_binding_lease,
            bind_source_path=row["source"],
            cuda_readiness=_FakeReadiness())
        sessions = [
            runtime.RTDLRuntimeSession(
                provider=row["provider"],
                expected_native_sha256=row["digest"],
                expected_compute_capability=(8, 9)),
            runtime.RTDLRuntimeSession(
                provider=second_provider,
                expected_native_sha256=row["digest"],
                expected_compute_capability=(8, 9)),
        ]
        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))

        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=lambda *, library, **_kwargs: _LeaseOwner(library)), \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    return_value=expected_descriptor) as descriptor_query:
            prepared = [
                sessions[0].prepare(later_loaded, static_input),
                sessions[1].prepare(later_loaded, static_input),
            ]

        self.assertEqual(descriptor_query.call_count, 2)
        self.assertIsNot(
            sessions[0]._descriptor_admission_seals,
            sessions[1]._descriptor_admission_seals)
        for owner in prepared:
            owner.close()
        for session in sessions:
            session.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_loaded_executable_snapshots_and_deep_freezes_projection(self):
        tuple_child = {"value": "frozen"}
        projection = {
            "target_toolchain": {
                "native_library_sha256": "a" * 64,
                "compute_capability": [8, 9],
            },
            "runtime": {
                "native_abi": "rtdl.v4.prepared_bounded_relation_callback.v7",
                "capacity": 8,
                "minimum_overlap_f32": 0.0,
            },
            "execution_schema": {
                "native_producer_descriptor": {
                    "exact": "native-producer-v1",
                    "tuple_rows": (tuple_child,),
                },
            },
        }
        loaded = runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=self.root / "frozen-artifact.rtdlexe",
                authority_path=self.root / "frozen-authority.json",
                authority_sha256="1" * 64,
                deployment_id="goal5807-frozen-test",
                trust_root_sha256="2" * 64,
                trust_package_sha256="3" * 64,
                artifact_sha256="4" * 64,
                executable_identity_sha256="5" * 64,
                family=runtime._BOUNDED,
                composed_ptx="// exact frozen test PTX\n",
                product_projection=projection,
            ))

        projection["runtime"]["capacity"] = 999
        projection["target_toolchain"]["compute_capability"][0] = 9
        projection["execution_schema"]["native_producer_descriptor"][
            "exact"] = "mutated"
        tuple_child["value"] = "mutated"
        self.assertEqual(loaded.product_projection["runtime"]["capacity"], 8)
        self.assertEqual(
            loaded.product_projection["target_toolchain"][
                "compute_capability"], (8, 9))
        self.assertEqual(
            loaded.product_projection["execution_schema"][
                "native_producer_descriptor"]["exact"],
            "native-producer-v1")
        self.assertEqual(
            loaded.product_projection["execution_schema"][
                "native_producer_descriptor"]["tuple_rows"][0]["value"],
            "frozen")
        with self.assertRaises(TypeError):
            loaded.product_projection["runtime"]["capacity"] = 1000
        with self.assertRaises(TypeError):
            loaded.product_projection["execution_schema"][
                "native_producer_descriptor"]["tuple_rows"][0]["value"] = (
                    "second mutation")

    def test_runtime_session_projection_cannot_change_during_descriptor_query(self):
        row = self._bind()
        loaded = self._distinct_loaded(
            row["loaded"], "projection-query-race")
        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        mutation_rejections = []
        owner_capacities = []

        def query_descriptor(*_args, **_kwargs):
            try:
                loaded.product_projection["runtime"]["capacity"] = 999
            except TypeError as error:
                mutation_rejections.append(error)
            return {"exact": "native-producer-v1"}

        def owner_factory(*, library, runtime, **_kwargs):
            owner_capacities.append(runtime["capacity"])
            return _LeaseOwner(library)

        with patch.object(
                runtime, "_query_native_producer_descriptor",
                side_effect=query_descriptor), patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=owner_factory):
            prepared = session.prepare(
                loaded, runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),)))

        self.assertEqual(len(mutation_rejections), 1)
        self.assertEqual(owner_capacities, [8])
        prepared.close()
        session.close()

    def test_runtime_session_rejects_manually_forged_loaded_capability(self):
        row = self._bind()
        trusted = row["loaded"]
        forged = runtime.LoadedRTDLExecutable(
            artifact_path=self.root / "forged-artifact.rtdlexe",
            authority_path=self.root / "forged-authority.json",
            authority_sha256="a" * 64,
            deployment_id="forged-deployment",
            trust_root_sha256="b" * 64,
            trust_package_sha256="c" * 64,
            artifact_sha256="d" * 64,
            executable_identity_sha256="e" * 64,
            family=trusted.family,
            composed_ptx="// attacker-selected PTX\n",
            product_projection=runtime._plain(trusted.product_projection),
        )

        with patch.object(
                runtime.LoadedRTDLExecutable, "bind_provider",
                side_effect=AssertionError(
                    "forged seed reached native admission")) as bind_provider:
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                forged.open_runtime_session(row["source"])
        self.assertEqual(
            rejected.exception.code, "RX056_LOADED_CAPABILITY_INVALID")
        bind_provider.assert_not_called()

        row["provider"]._loaded = forged
        try:
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                runtime.RTDLRuntimeSession(
                    provider=row["provider"],
                    expected_native_sha256=row["digest"],
                    expected_compute_capability=(8, 9),
                )
            self.assertEqual(
                rejected.exception.code, "RX056_LOADED_CAPABILITY_INVALID")
        finally:
            row["provider"]._loaded = trusted

        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            session.prepare(
                forged, runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),)))
        self.assertEqual(
            rejected.exception.code, "RX056_LOADED_CAPABILITY_INVALID")

        replaced = replace(
            trusted, composed_ptx="// dataclasses.replace forged PTX\n")
        self.assertIs(
            replaced._token, runtime._LOADED_EXECUTABLE_CAPABILITY_TOKEN)
        self.assertEqual(
            replaced._runtime_session_snapshot_seal,
            trusted._runtime_session_snapshot_seal)
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            session.prepare(
                replaced, runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),)))
        self.assertEqual(
            rejected.exception.code, "RX056_LOADED_CAPABILITY_INVALID")
        session.close()

    def test_runtime_session_rejects_valid_seed_substitution_after_bind(self):
        row = self._bind()
        trusted = row["loaded"]
        substituted = self._distinct_loaded(
            trusted, "valid-seed-substitution-after-bind")
        # Both objects are genuine loader capabilities and name the same
        # native SHA/CC.  Only ``trusted`` had its descriptor checked during
        # bind_provider, so the later exact loaded object must not inherit the
        # seed admission merely because its target provider matches.
        row["provider"]._loaded = substituted
        try:
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                runtime.RTDLRuntimeSession(
                    provider=row["provider"],
                    expected_native_sha256=row["digest"],
                    expected_compute_capability=(8, 9),
                )
            self.assertEqual(
                rejected.exception.code, "RX056_LOADED_CAPABILITY_INVALID")
            self.assertEqual(
                rejected.exception.path,
                "runtime_session.seed.native_producer_descriptor")
        finally:
            row["provider"]._loaded = trusted
        row["provider"].close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_runtime_session_return_interrupt_closes_abandoned_provider(self):
        row = self._bind()
        with patch.object(
                runtime.LoadedRTDLExecutable, "bind_provider",
                return_value=row["provider"]) as bind_provider:
            self._interrupt_on_return(
                code=runtime.LoadedRTDLExecutable.open_runtime_session.__code__,
                operation=lambda: row["loaded"].open_runtime_session(
                    row["source"]),
                message="runtime session public return was interrupted",
            )
        gc.collect()

        bind_provider.assert_called_once_with(row["source"])
        self.assertTrue(row["provider"].closed)
        self.assertTrue(row["readiness"].released)
        self.assertEqual(row["entry"].active_lease_ids, set())
        self.assertEqual(self._entry_provenance_count(row["entry"]), 0)

    def test_runtime_session_close_retry_retains_finalizer_until_success(self):
        readiness = _FakeReadiness(fail_close_once=True)
        row = self._bind(readiness=readiness)
        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        with patch.object(
                runtime, "_release_native_library_image",
                wraps=runtime._release_native_library_image) as release:
            with self.assertRaisesRegex(
                    KeyboardInterrupt, "CUDA retain release interruption"):
                session.close()
            self.assertFalse(session.closed)
            self.assertTrue(session._abandon_finalizer.alive)
            session.close()

        self.assertTrue(session.closed)
        self.assertFalse(session._abandon_finalizer.alive)
        self.assertEqual(release.call_count, 1)
        self.assertEqual(readiness.close_calls, 2)
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_runtime_session_rejects_provider_and_descriptor_substitution(self):
        row = self._bind()
        session = runtime.RTDLRuntimeSession(
            provider=row["provider"],
            expected_native_sha256=row["digest"],
            expected_compute_capability=(8, 9),
        )
        static_input = runtime.BoundedRelationStaticInput(
            ((0.0, 0.0, 1.0, 1.0, 1),))

        wrong_native, _ = self._loaded("a" * 64)
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            session.prepare(wrong_native, static_input)
        self.assertEqual(rejected.exception.code, "RX032_NATIVE_IDENTITY_MISMATCH")

        wrong_capability, _ = self._loaded(row["digest"])
        wrong_projection = runtime._plain(wrong_capability.product_projection)
        wrong_projection["target_toolchain"]["compute_capability"] = (9, 0)
        wrong_capability = runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=wrong_capability.artifact_path,
                authority_path=wrong_capability.authority_path,
                authority_sha256=wrong_capability.authority_sha256,
                deployment_id=wrong_capability.deployment_id,
                trust_root_sha256=wrong_capability.trust_root_sha256,
                trust_package_sha256=wrong_capability.trust_package_sha256,
                artifact_sha256=wrong_capability.artifact_sha256,
                executable_identity_sha256=(
                    wrong_capability.executable_identity_sha256),
                family=wrong_capability.family,
                composed_ptx=wrong_capability.composed_ptx,
                product_projection=wrong_projection,
            ))
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            session.prepare(wrong_capability, static_input)
        self.assertEqual(rejected.exception.code, "RX033_DEVICE_SUBSTITUTION")

        matching = self._distinct_loaded(
            row["loaded"], "descriptor-substitution")
        with patch.object(
                runtime, "_query_native_producer_descriptor",
                return_value={"different": "provider"}):
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                session.prepare(matching, static_input)
        self.assertEqual(
            rejected.exception.code, "RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH")
        self.assertEqual(row["entry"].active_lease_ids, {
            row["binding_lease"]._rtdl_native_cache_lease_id,
        })
        session.close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_provider_rejects_cache_entry_handle_seal_and_pid_drift(self):
        mutations = ("cache_entry", "digest", "handle", "seals", "pid")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                row = self._bind()
                provider = row["provider"]
                entry = row["entry"]
                original_entry = runtime._NATIVE_IMAGE_CACHE[row["digest"]]
                original_handle = entry.library._handle
                original_seals = entry.image_seals
                original_pid = entry.owner_pid
                original_digest = entry.sha256
                if mutation == "cache_entry":
                    runtime._NATIVE_IMAGE_CACHE[row["digest"]] = (
                        runtime._NativeImageCacheEntry(
                            library=entry.library, sha256=entry.sha256,
                            source_path=entry.source_path,
                            image_descriptor=entry.image_descriptor,
                            image_seals=entry.image_seals,
                            loader_alias=entry.loader_alias,
                            owner_pid=entry.owner_pid, usable=True))
                elif mutation == "digest":
                    entry.sha256 = "f" * 64
                elif mutation == "handle":
                    entry.library._handle += 1
                elif mutation == "seals":
                    entry.image_seals = 7
                else:
                    entry.owner_pid += 1
                with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                    provider.prepare(runtime.BoundedRelationStaticInput(
                        ((0.0, 0.0, 1.0, 1.0, 1),)))
                self.assertIn(rejected.exception.code, {
                    "RX047_NATIVE_CACHE_FORK_POISONED",
                    "RX048_NATIVE_CACHE_QUARANTINED",
                })
                runtime._NATIVE_IMAGE_CACHE[row["digest"]] = original_entry
                entry.library._handle = original_handle
                entry.image_seals = original_seals
                entry.owner_pid = original_pid
                entry.sha256 = original_digest
                provider.close()

    def test_raw_prepare_keeps_path_loader_and_descriptor_checks_per_call(self):
        source = self.root / "raw-provider.so"
        source.write_bytes(b"raw provider")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        loaded, expected_descriptor = self._loaded(digest)
        fake_library = SimpleNamespace()
        owners = []

        class Owner:
            def close(self):
                pass

        def owner_factory(**_kwargs):
            owner = Owner()
            owners.append(owner)
            return owner

        with patch.object(
                runtime, "_load_native_library",
                return_value=fake_library) as raw_loader, patch.object(
                runtime, "_query_native_producer_descriptor",
                return_value=expected_descriptor) as descriptor_query, patch.object(
                runtime, "_PreparedBoundedOwner", side_effect=owner_factory):
            first = loaded.prepare(
                runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),)),
                native_library_path=source)
            second = loaded.prepare(
                runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 2.0, 2.0, 2),)),
                native_library_path=source)
        self.assertEqual(raw_loader.call_count, 2)
        self.assertEqual(descriptor_query.call_count, 2)
        self.assertEqual(len(owners), 2)
        first.close(); second.close()

    def test_close_retry_does_not_release_binding_lease_twice(self):
        readiness = _FakeReadiness(fail_close_once=True)
        row = self._bind(readiness=readiness)
        provider = row["provider"]
        with patch.object(
                runtime, "_release_native_library_image",
                wraps=runtime._release_native_library_image) as release:
            with self.assertRaisesRegex(
                    KeyboardInterrupt, "CUDA retain release interruption"):
                provider.close()
            self.assertFalse(provider.closed)
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                provider.prepare(runtime.BoundedRelationStaticInput(
                    ((0.0, 0.0, 1.0, 1.0, 1),)))
            self.assertEqual(rejected.exception.code, "RX037_USE_AFTER_CLOSE")
            provider.close()
        self.assertTrue(provider.closed)
        self.assertEqual(release.call_count, 1)
        self.assertEqual(readiness.close_calls, 2)

    def test_close_cannot_race_native_owner_initialization(self):
        row = self._bind()
        provider = row["provider"]
        entered = threading.Event()
        allow_owner = threading.Event()
        close_done = threading.Event()
        result = {}
        failures = []

        def owner_factory(*, library, **_kwargs):
            entered.set()
            if not allow_owner.wait(2):
                raise AssertionError("test did not release owner initialization")
            return _LeaseOwner(library)

        def prepare_worker():
            try:
                result["prepared"] = provider.prepare(
                    runtime.BoundedRelationStaticInput(
                        ((0.0, 0.0, 1.0, 1.0, 1),)))
            except BaseException as error:  # pragma: no cover - assertion relay
                failures.append(error)

        def close_worker():
            try:
                provider.close()
                close_done.set()
            except BaseException as error:  # pragma: no cover - assertion relay
                failures.append(error)

        with patch.object(
                runtime, "_PreparedBoundedOwner",
                side_effect=owner_factory):
            preparing = threading.Thread(target=prepare_worker)
            preparing.start()
            self.assertTrue(entered.wait(2))
            closing = threading.Thread(target=close_worker)
            closing.start()
            self.assertFalse(close_done.wait(0.05))
            allow_owner.set()
            preparing.join(2); closing.join(2)
        self.assertFalse(preparing.is_alive())
        self.assertFalse(closing.is_alive())
        self.assertEqual(failures, [])
        self.assertTrue(provider.closed)
        # Provider close releases only its binding/readiness capabilities; the
        # independently leased prepared owner remains explicitly closable.
        self.assertEqual(len(row["entry"].active_lease_ids), 1)
        result["prepared"].close()
        self.assertEqual(row["entry"].active_lease_ids, set())

    def test_cuda_readiness_is_process_owned_and_reused_without_release(self):
        driver, calls = _fake_cuda_driver()
        with patch.object(runtime.ctypes, "CDLL", return_value=driver), \
                patch.object(runtime, "_NATIVE_RUNTIME_TOUCHED", False):
            first = runtime._acquire_cuda_primary_context_readiness(
                expected_compute_capability=(8, 9))
            second = runtime._acquire_cuda_primary_context_readiness(
                expected_compute_capability=(8, 9))
            self.assertTrue(runtime._NATIVE_RUNTIME_TOUCHED)
        self.assertEqual(calls["retain"], 1)
        self.assertEqual(calls["set"], [0x2222, 0x1111])
        self.assertEqual(first.context_handle, 0x2222)
        self.assertEqual(second.context_handle, 0x2222)
        first.close(); first.close(); second.close()
        # The retain belongs to process lifetime, not either provider lease.
        self.assertEqual(calls["release"], 0)
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            first.check()
        self.assertEqual(rejected.exception.code, "RX037_USE_AFTER_CLOSE")

    def test_cuda_retain_side_effect_then_interrupt_is_cleaned_once(self):
        driver, calls = _fake_cuda_driver()
        original = driver.cuDevicePrimaryCtxRetain.callback

        def interrupted_retain(*args):
            original(*args)
            raise KeyboardInterrupt("after retain side effect")

        driver.cuDevicePrimaryCtxRetain.callback = interrupted_retain
        with patch.object(runtime.ctypes, "CDLL", return_value=driver):
            with self.assertRaisesRegex(KeyboardInterrupt, "after retain"):
                runtime._acquire_cuda_primary_context_readiness(
                    expected_compute_capability=(8, 9))
        self.assertEqual(calls["retain"], 1)
        self.assertEqual(calls["release"], 1)
        self.assertIsNone(runtime._CUDA_PRIMARY_READY_STATE)

    def test_cuda_published_state_survives_lease_construction_interrupt(self):
        driver, calls = _fake_cuda_driver()
        real_lease = runtime._CudaPrimaryContextReadinessLease
        with patch.object(runtime.ctypes, "CDLL", return_value=driver), \
                patch.object(
                    runtime, "_CudaPrimaryContextReadinessLease",
                    side_effect=KeyboardInterrupt("after readiness publication")):
            with self.assertRaisesRegex(KeyboardInterrupt, "publication"):
                runtime._acquire_cuda_primary_context_readiness(
                    expected_compute_capability=(8, 9))
        self.assertIsNotNone(runtime._CUDA_PRIMARY_READY_STATE)
        self.assertEqual(calls["retain"], 1)
        self.assertEqual(calls["release"], 0)
        with patch.object(
                runtime, "_CudaPrimaryContextReadinessLease", real_lease):
            lease = runtime._acquire_cuda_primary_context_readiness(
                expected_compute_capability=(8, 9))
        self.assertEqual(lease.context_handle, 0x2222)
        self.assertEqual(calls["retain"], 1)
        lease.close()

    def test_inherited_provider_rejects_before_orphaned_lock(self):
        row = self._bind()
        provider = row["provider"]
        acquired = threading.Event()
        release_lock = threading.Event()

        def holder():
            with provider._active:
                acquired.set()
                release_lock.wait(2)

        thread = threading.Thread(target=holder)
        thread.start()
        self.assertTrue(acquired.wait(1))
        try:
            with patch.object(runtime.os, "getpid", return_value=os.getpid() + 1):
                with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                    provider.prepare(runtime.BoundedRelationStaticInput(
                        ((0.0, 0.0, 1.0, 1.0, 1),)))
            self.assertEqual(
                rejected.exception.code, "RX047_NATIVE_CACHE_FORK_POISONED")
        finally:
            release_lock.set()
            thread.join(2)
        self.assertFalse(thread.is_alive())
        provider.close()

    @unittest.skipUnless(hasattr(os, "fork"), "requires POSIX fork")
    def test_real_fork_rejects_while_other_thread_holds_provider_lock(self):
        row = self._bind()
        provider = row["provider"]
        acquired = threading.Event()
        release_lock = threading.Event()

        def holder():
            with provider._active:
                acquired.set()
                release_lock.wait(5)

        thread = threading.Thread(target=holder)
        thread.start()
        self.assertTrue(acquired.wait(1))
        read_fd, write_fd = os.pipe()
        child = os.fork()
        if child == 0:  # pragma: no cover - executed only in fork child
            try:
                os.close(read_fd)
                try:
                    provider.prepare(runtime.BoundedRelationStaticInput(
                        ((0.0, 0.0, 1.0, 1.0, 1),)))
                except runtime.RTDLExecutableError as error:
                    payload = error.code.encode("ascii")
                else:
                    payload = b"UNEXPECTED_ACCEPT"
                os.write(write_fd, payload)
            finally:
                os._exit(0)
        os.close(write_fd)
        try:
            readable, _, _ = select.select([read_fd], [], [], 2.0)
            if not readable:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)
                self.fail("fork child deadlocked on inherited provider lock")
            payload = os.read(read_fd, 256)
            _, status = os.waitpid(child, 0)
            self.assertTrue(os.WIFEXITED(status))
            self.assertEqual(
                payload.decode("ascii"), "RX047_NATIVE_CACHE_FORK_POISONED")
        finally:
            os.close(read_fd)
            release_lock.set()
            thread.join(2)
        self.assertFalse(thread.is_alive())
        provider.close()

    def test_cuda_readiness_failure_restores_context_and_drops_retain(self):
        for label, select_status, restore_status in (
                ("select", 7, 0), ("restore", 0, 9)):
            with self.subTest(label=label):
                driver, calls = _fake_cuda_driver(
                    primary_select_status=select_status,
                    restore_status=restore_status)
                with patch.object(runtime.ctypes, "CDLL", return_value=driver):
                    with self.assertRaises(runtime.RTDLExecutableError):
                        runtime._acquire_cuda_primary_context_readiness(
                            expected_compute_capability=(8, 9))
                self.assertEqual(calls["retain"], 1)
                self.assertEqual(calls["release"], 1)
                self.assertIn(0x1111, calls["set"])

    def test_fork_after_cuda_touch_poisoned_before_cache_publication(self):
        with patch.object(runtime, "_NATIVE_IMAGE_CACHE", {}), \
                patch.object(runtime, "_NATIVE_RUNTIME_TOUCHED", True), \
                patch.object(runtime, "_NATIVE_IMAGE_CACHE_FORK_POISONED", False), \
                patch.object(runtime, "_NATIVE_IMAGE_CACHE_PID", os.getpid()):
            runtime._native_image_cache_after_fork_child()
            self.assertTrue(runtime._NATIVE_IMAGE_CACHE_FORK_POISONED)
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                runtime._native_image_cache_guard(
                    code="RX047_NATIVE_CACHE_FORK_POISONED",
                    identity_path="postfork")
            self.assertEqual(
                rejected.exception.code, "RX047_NATIVE_CACHE_FORK_POISONED")


if __name__ == "__main__":
    unittest.main()
