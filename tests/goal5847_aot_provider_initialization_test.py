from __future__ import annotations

import gc
import hashlib
import os
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import rtdsl.v4_rtdlexe as runtime
from rtdsl import physical_execution_provenance as provenance


class Goal5847AotProviderInitializationTest(unittest.TestCase):
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
            provenance._LOADED_PROVIDER_IDENTITIES.clear()
        self._descriptors: list[int] = []
        self.seals = patch.object(runtime, "_native_image_seals", return_value=15)
        self.seals.start()

    def tearDown(self) -> None:
        self.seals.stop()
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            provenance._LOADED_PROVIDER_IDENTITIES.clear()
            provenance._LOADED_PROVIDER_IDENTITIES.update(self._old_provenance)
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

    def _resources(self):
        source = self.root / "librtdl_optix.so"
        source.write_bytes(b"goal5847 exact provider bytes")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        sealed = self.root / "sealed-provider"
        sealed.write_bytes(source.read_bytes())
        descriptor = os.open(sealed, os.O_RDONLY)
        self._descriptors.append(descriptor)
        compiler_attempt_count = Mock(return_value=0)
        entry = runtime._NativeImageCacheEntry(
            library=SimpleNamespace(
                _handle=0x5847,
                rtdl_optix_v4_runtime_compiler_attempt_count_v1=(
                    compiler_attempt_count
                ),
            ),
            sha256=digest,
            source_path=source,
            image_descriptor=descriptor,
            image_seals=15,
            loader_alias="/private/goal5847-provider.so",
            owner_pid=os.getpid(),
            usable=True,
        )
        runtime._NATIVE_IMAGE_CACHE[digest] = entry
        lease = runtime._acquire_native_image_lease(
            entry, source_path=source)
        runtime._register_native_image_lease_provenance(
            lease, source_path=source, digest=digest)
        readiness_state = runtime._CudaPrimaryContextReadinessState(
            driver=SimpleNamespace(),
            device=0,
            context=0x5847,
            compute_capability=(8, 9),
            owner_pid=os.getpid(),
        )
        runtime._CUDA_PRIMARY_READY_STATE = readiness_state
        readiness = runtime._CudaPrimaryContextReadinessLease(
            state=readiness_state)
        return source, digest, entry, lease, readiness

    def _deployment_and_loaded(self, digest: str):
        values = {
            "authority": "1" * 64,
            "root": "2" * 64,
            "package": "3" * 64,
            "artifact": "4" * 64,
            "executable": "5" * 64,
            "target": "6" * 64,
            "task": "7" * 64,
        }
        deployment_id = "goal5847/aot/provider"
        entry = {
            "deployment_id": deployment_id,
            "family": runtime._BOUNDED,
            "task_semantics_sha256": values["task"],
            "authority_sha256": values["authority"],
            "artifact_sha256": values["artifact"],
            "executable_identity_sha256": values["executable"],
            "target_sha256": values["target"],
            "native_library_sha256": digest,
            "compute_capability": (8, 9),
        }
        deployment = runtime.InstalledRTDLDeployment(
            _token=runtime._DEPLOYMENT_CAPABILITY_TOKEN,
            trust_root_path=self.root / "root.json",
            trust_root_sha256=values["root"],
            trust_head_path=self.root / "head.json",
            trust_head_sha256="8" * 64,
            trust_package_path=self.root / "package.json",
            trust_package_sha256=values["package"],
            deployment_id=deployment_id,
            entry=entry,
        )
        descriptor = {"exact": "goal5847-native-descriptor"}
        loaded = runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=self.root / "artifact.rtdlexe",
                authority_path=self.root / "authority.json",
                authority_sha256=values["authority"],
                deployment_id=deployment_id,
                trust_root_sha256=values["root"],
                trust_package_sha256=values["package"],
                artifact_sha256=values["artifact"],
                executable_identity_sha256=values["executable"],
                family=runtime._BOUNDED,
                composed_ptx="// exact Goal5847 PTX\n",
                product_projection={
                    "target_toolchain": {
                        "native_library_sha256": digest,
                        "compute_capability": (8, 9),
                    },
                    "runtime": {
                        "native_abi": (
                            "rtdl.v4.prepared_bounded_relation_callback.v7"),
                    },
                    "execution_schema": {
                        "native_producer_descriptor": descriptor,
                    },
                },
            ))
        return deployment, loaded, descriptor

    def _patches(self, lease, readiness, descriptor):
        return (
            patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                return_value=readiness),
            patch.object(
                runtime, "_load_verified_native_file_descriptor",
                return_value=lease),
            patch.object(runtime, "_warm_native_provider_runtime"),
            patch.object(
                runtime, "_query_native_producer_descriptor",
                return_value=descriptor),
        )

    def test_initialization_overlaps_then_binds_exact_loaded_slot_once(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        admitted = threading.Event()
        release = threading.Event()

        def delayed_readiness(**_kwargs):
            admitted.set()
            self.assertTrue(release.wait(timeout=2.0))
            return readiness

        with patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                side_effect=delayed_readiness), \
                patch.object(
                    runtime, "_load_verified_native_file_descriptor",
                    return_value=lease) as loader, \
                patch.object(runtime, "_warm_native_provider_runtime") as warm, \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    return_value=descriptor) as query:
            initializing = deployment.begin_provider_initialization(
                source, collect_phase_timings=True)
            self.assertTrue(admitted.wait(timeout=2.0))
            self.assertEqual(initializing.state, "INITIALIZING")
            release.set()
            provider = initializing.bind(loaded)

        self.assertEqual(initializing.state, "BOUND")
        self.assertEqual(provider.native_library_sha256, digest)
        self.assertEqual(provider.runtime_compiler_attempt_count, 0)
        self.assertEqual(
            entry.library.rtdl_optix_v4_runtime_compiler_attempt_count_v1
                .call_count,
            1,
        )
        self.assertEqual(loader.call_count, 1)
        self.assertEqual(warm.call_count, 1)
        self.assertEqual(query.call_count, 1)
        self.assertEqual(set(initializing.phase_timings_ns), {
            "cuda_primary_context", "sealed_native_image",
            "parallel_admission_wall", "parallel_overlap_saved",
            "native_runtime_warm", "total",
        })
        self.assertGreaterEqual(
            initializing.phase_timings_ns["parallel_overlap_saved"], 0)
        with self.assertRaises(runtime.RTDLExecutableError) as repeated:
            initializing.bind(loaded)
        self.assertEqual(
            repeated.exception.code, "RX057_PROVIDER_INITIALIZATION_INVALID")
        provider.close()
        with self.assertRaises(runtime.RTDLExecutableError) as closed_counter:
            _ = provider.runtime_compiler_attempt_count
        self.assertEqual(closed_counter.exception.code, "RX037_USE_AFTER_CLOSE")
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_native_warm_precedes_python_cuda_readiness_retain(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        readiness_started = threading.Event()
        sealed_loaded = threading.Event()
        release_readiness = threading.Event()
        order = []

        def delayed_readiness(**_kwargs):
            order.append("readiness")
            readiness_started.set()
            self.assertTrue(release_readiness.wait(timeout=2.0))
            return readiness

        def observed_load(*_args, **_kwargs):
            order.append("load")
            sealed_loaded.set()
            return lease

        def observed_warm(_library):
            order.append("warm")

        with patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                side_effect=delayed_readiness), \
                patch.object(
                    runtime, "_load_verified_native_file_descriptor",
                    side_effect=observed_load), \
                patch.object(
                    runtime, "_warm_native_provider_runtime",
                    side_effect=observed_warm), \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    return_value=descriptor):
            initializing = deployment.begin_provider_initialization(
                source, collect_phase_timings=True)
            self.assertTrue(readiness_started.wait(timeout=2.0))
            self.assertTrue(sealed_loaded.wait(timeout=2.0))
            self.assertEqual(order, ["load", "warm", "readiness"])
            release_readiness.set()
            provider = initializing.bind(loaded)

        provider.close()
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_phase_timing_is_explicitly_opt_in(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], patches[2], patches[3]:
            initializing = deployment.begin_provider_initialization(source)
            provider = initializing.bind(loaded)
        self.assertEqual(dict(initializing.phase_timings_ns), {})
        provider.close()
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_phase_timing_rejects_non_bool_switch(self):
        source, digest, _entry, _lease, _readiness = self._resources()
        deployment, _loaded, _descriptor = self._deployment_and_loaded(digest)
        with self.assertRaises(runtime.RTDLExecutableError) as rejected:
            deployment.begin_provider_initialization(
                source, collect_phase_timings=1)
        self.assertEqual(rejected.exception.code, "RX006_INPUT_INVALID")

    def test_mismatched_loaded_slot_fails_closed_and_releases_resources(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        mismatched = runtime._issue_loaded_runtime_session_capability(
            runtime.LoadedRTDLExecutable(
                artifact_path=loaded.artifact_path,
                authority_path=loaded.authority_path,
                authority_sha256=loaded.authority_sha256,
                deployment_id=loaded.deployment_id,
                trust_root_sha256=loaded.trust_root_sha256,
                trust_package_sha256=loaded.trust_package_sha256,
                artifact_sha256=loaded.artifact_sha256,
                executable_identity_sha256="9" * 64,
                family=loaded.family,
                composed_ptx=loaded.composed_ptx,
                product_projection=loaded.product_projection,
            ))
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], patches[2], patches[3]:
            initializing = runtime.begin_rtdlexe_provider_initialization(
                deployment=deployment, native_library_path=source)
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                initializing.bind(mismatched)
        self.assertEqual(rejected.exception.code, "RX050_DEPLOYMENT_INTENT_MISMATCH")
        self.assertEqual(initializing.state, "CLOSED")
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_public_compiler_counter_fails_closed_when_abi_is_absent(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        delattr(
            entry.library,
            "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
        )
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], patches[2], patches[3]:
            provider = deployment.begin_provider_initialization(source).bind(loaded)
            try:
                with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                    _ = provider.runtime_compiler_attempt_count
            finally:
                provider.close()
        self.assertEqual(rejected.exception.code, "RX036_NATIVE_ABI_MISSING")
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_background_failure_and_unbound_close_do_not_leak(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], \
                patch.object(
                    runtime, "_warm_native_provider_runtime",
                    side_effect=RuntimeError("injected warm failure")), \
                patches[3]:
            initializing = deployment.begin_provider_initialization(source)
            with self.assertRaisesRegex(RuntimeError, "injected warm failure"):
                initializing.bind(loaded)
        self.assertEqual(initializing.state, "CLOSED")
        # Native warm failed before the readiness lease was acquired.
        self.assertFalse(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_unbound_close_is_idempotent_and_releases_resources(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, _loaded, descriptor = self._deployment_and_loaded(digest)
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], patches[2], patches[3]:
            initializing = deployment.begin_provider_initialization(source)
            initializing.close()
            initializing.close()
        self.assertEqual(initializing.state, "CLOSED")
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_post_warm_readiness_failure_releases_loaded_native_image(self):
        source, digest, entry, lease, _readiness = self._resources()
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        with patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                side_effect=RuntimeError("injected readiness failure")), \
                patch.object(
                    runtime, "_load_verified_native_file_descriptor",
                    return_value=lease), \
                patch.object(runtime, "_warm_native_provider_runtime") as warm, \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    return_value=descriptor):
            initializing = deployment.begin_provider_initialization(source)
            with self.assertRaisesRegex(
                    RuntimeError, "injected readiness failure"):
                initializing.bind(loaded)
        self.assertEqual(warm.call_count, 1)
        self.assertEqual(initializing.state, "CLOSED")
        self.assertEqual(entry.active_lease_ids, set())

    def test_native_load_failure_prevents_readiness_acquisition(self):
        source, digest, entry, unused_lease, readiness = self._resources()
        runtime._release_native_library_image(unused_lease)
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        with patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                return_value=readiness), \
                patch.object(
                    runtime, "_load_verified_native_file_descriptor",
                    side_effect=RuntimeError("injected native load failure")), \
                patch.object(runtime, "_warm_native_provider_runtime") as warm, \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    return_value=descriptor):
            initializing = deployment.begin_provider_initialization(source)
            with self.assertRaisesRegex(
                    RuntimeError, "injected native load failure"):
                initializing.bind(loaded)
        self.assertEqual(warm.call_count, 0)
        self.assertEqual(initializing.state, "CLOSED")
        self.assertFalse(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_native_load_failure_precedes_unreached_readiness_failure(self):
        source, digest, entry, unused_lease, _readiness = self._resources()
        runtime._release_native_library_image(unused_lease)
        deployment, loaded, descriptor = self._deployment_and_loaded(digest)
        with patch.object(
                runtime, "_acquire_cuda_primary_context_readiness",
                side_effect=RuntimeError("injected readiness failure")) as acquire, \
                patch.object(
                    runtime, "_load_verified_native_file_descriptor",
                    side_effect=RuntimeError("injected native load failure")), \
                patch.object(runtime, "_warm_native_provider_runtime") as warm, \
                patch.object(
                    runtime, "_query_native_producer_descriptor",
                    return_value=descriptor):
            initializing = deployment.begin_provider_initialization(source)
            with self.assertRaisesRegex(
                    RuntimeError, "injected native load failure") as rejected:
                initializing.bind(loaded)
        self.assertEqual(warm.call_count, 0)
        self.assertEqual(acquire.call_count, 0)
        self.assertEqual(initializing.state, "CLOSED")
        self.assertEqual(getattr(rejected.exception, "__notes__", ()), ())
        self.assertEqual(entry.active_lease_ids, set())

    def test_forked_or_directly_constructed_capability_is_rejected(self):
        with self.assertRaises(runtime.RTDLExecutableError) as direct:
            runtime.InitializingRTDLProvider(
                deployment=object(), native_library_path=self.root / "x",
                _token=object())
        self.assertEqual(
            direct.exception.code, "RX057_PROVIDER_INITIALIZATION_INVALID")

        source, digest, _entry, lease, readiness = self._resources()
        deployment, _loaded, descriptor = self._deployment_and_loaded(digest)
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], patches[2], patches[3]:
            initializing = deployment.begin_provider_initialization(source)
            initializing._thread.join()
            initializing._pid += 1
            with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                _ = initializing.state
            initializing._pid -= 1
            initializing.close()
        self.assertEqual(
            rejected.exception.code, "RX047_NATIVE_CACHE_FORK_POISONED")

    def test_abandoned_unbound_capability_releases_after_worker_finishes(self):
        source, digest, entry, lease, readiness = self._resources()
        deployment, _loaded, descriptor = self._deployment_and_loaded(digest)
        patches = self._patches(lease, readiness, descriptor)
        with patches[0], patches[1], patches[2], patches[3]:
            initializing = deployment.begin_provider_initialization(source)
            worker = initializing._thread
            del initializing
            worker.join(timeout=2.0)
            self.assertFalse(worker.is_alive())
            gc.collect()
        self.assertTrue(readiness.released)
        self.assertEqual(entry.active_lease_ids, set())


if __name__ == "__main__":
    unittest.main()
