from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import hashlib
import inspect
import os
import tempfile
import unittest
from unittest import mock

from experiments.goal5802_premeasurement import rtdlexe_arm
from experiments.goal5802_premeasurement import pyoptix_scalar_arm
from experiments.goal5802_premeasurement.workload import RELATION_TASK
from scripts import goal5807_provider_ready_pilot as pilot


class _Clock:
    def __init__(self) -> None:
        self.value = 0

    def __call__(self) -> int:
        return self.value

    def advance(self, value: int) -> None:
        self.value += value


class _CudaDriver:
    def __init__(
        self, current: int = 0, *, primary: int = 0xD00D,
        capability: tuple[int, int] = (8, 6), retain_status: int = 0,
        release_status: int = 0,
        set_fail_values: frozenset[int] = frozenset(),
        current_device: int = 0,
    ) -> None:
        self.current = current
        self.primary = primary
        self.capability = capability
        self.retain_status = retain_status
        self.release_status = release_status
        self.set_fail_values = set_fail_values
        self.current_device = current_device
        self.set_calls: list[int] = []
        self.retain_calls: list[int] = []
        self.release_calls: list[int] = []
        self.events: list[str] = []
        self.get_current_call_count = 0
        self.get_device_call_count = 0

    def cuCtxGetCurrent(self, output: object) -> int:
        self.get_current_call_count += 1
        output._obj.value = self.current
        return 0

    def cuCtxSetCurrent(self, value: object) -> int:
        target = int(value.value or 0)
        self.set_calls.append(target)
        self.events.append(f"set:{target}")
        if target in self.set_fail_values:
            return 1
        self.current = target
        return 0

    def cuCtxGetDevice(self, output: object) -> int:
        self.get_device_call_count += 1
        output._obj.value = self.current_device
        return 0

    def cuDeviceGet(self, output: object, ordinal: int) -> int:
        output._obj.value = 0
        self.events.append(f"device:{ordinal}")
        return 0

    def cuDeviceComputeCapability(
        self, major: object, minor: object, _device: int,
    ) -> int:
        major._obj.value, minor._obj.value = self.capability
        return 0

    def cuDevicePrimaryCtxRetain(self, output: object, device: int) -> int:
        self.retain_calls.append(device)
        self.events.append("retain")
        if self.retain_status == 0:
            output._obj.value = self.primary
        return self.retain_status

    def cuDevicePrimaryCtxRelease(self, device: int) -> int:
        self.release_calls.append(device)
        self.events.append("release")
        return self.release_status


class _CudaRuntime:
    def __init__(
        self, driver: _CudaDriver, *, fail_after_change: bool = False,
    ) -> None:
        self.driver = driver
        self.fail_after_change = fail_after_change
        self.free_calls: list[int] = []

    def free(self, value: int) -> None:
        self.free_calls.append(value)
        self.driver.current = 0xCAFE
        if self.fail_after_change:
            raise RuntimeError("synthetic free failure")


class _Prepared:
    def __init__(self, order: list[str], *, close_error: bool = False) -> None:
        self.order = order
        self.close_error = close_error

    def close(self) -> None:
        self.order.append("prepared.close")
        if self.close_error:
            raise RuntimeError("prepared close failed")


class _Provider:
    def __init__(self, order: list[str], prepared: _Prepared) -> None:
        self.order = order
        self.prepared = prepared
        self.closed = False
        self.prepare_calls: list[object] = []

    def prepare(self, static: object) -> _Prepared:
        self.order.append("provider.prepare")
        self.prepare_calls.append(static)
        return self.prepared

    def close(self) -> None:
        self.order.append("provider.close")
        self.closed = True


class _Loaded:
    def __init__(
        self, order: list[str], provider: _Provider, prepared: _Prepared,
    ) -> None:
        self.order = order
        self.provider = provider
        self.prepared = prepared
        self.bind_paths: list[Path] = []
        self.raw_prepare_calls: list[tuple[object, Path]] = []

    def bind_provider(self, *, native_library_path: Path) -> _Provider:
        self.order.append("loaded.bind_provider")
        self.bind_paths.append(native_library_path)
        return self.provider

    def prepare(
        self, static: object, *, native_library_path: Path,
    ) -> _Prepared:
        self.order.append("loaded.prepare_raw")
        self.raw_prepare_calls.append((static, native_library_path))
        return self.prepared


def _adapter_fixture(
    *, prepared_close_error: bool = False,
) -> tuple[rtdlexe_arm.RTDLExecutableAdapter, _Loaded, _Provider, list[str]]:
    order: list[str] = []
    prepared = _Prepared(order, close_error=prepared_close_error)
    provider = _Provider(order, prepared)
    loaded = _Loaded(order, provider, prepared)
    module = SimpleNamespace(
        __name__=rtdlexe_arm.RTDL_ROOT_MODULE,
        __file__=rtdlexe_arm.__file__,
        install_rtdlexe_deployment=lambda **kwargs: object(),
        load_rtdlexe=lambda **kwargs: loaded,
        BoundedRelationBufferStaticInput=lambda **kwargs: ("static", kwargs),
        BoundedRelationBufferBatch=lambda **kwargs: ("batch", kwargs),
    )
    implementation = SimpleNamespace(
        __name__=rtdlexe_arm.RTDL_IMPLEMENTATION_MODULE)
    paths = rtdlexe_arm.RTDLDeploymentPaths(
        artifact=Path("artifact.rtdlexe"), authority=Path("authority.json"),
        trust_root=Path("root.json"), trust_head=Path("head.json"),
        trust_package=Path("package.json"), native_library=Path("native.so"),
        deployment_id="deployment-test")
    workload = {
        "indexed": [[0.0, 0.0, 1.0, 1.0, 7]],
        "sources": [[0.0, 0.0, 1.0, 1.0, 7]],
        "expected_rows": [[7, 7]],
        "minimum_overlap_f32": 1.0,
        "semantic_capacity": 1,
    }
    adapter = rtdlexe_arm.RTDLExecutableAdapter(
        RELATION_TASK, workload, paths,
        preloaded_runtime=module,
        preloaded_implementation=implementation,
        runtime_preload_receipt={"status": "fake"})
    return adapter, loaded, provider, order


class ProviderReadyPilotTest(unittest.TestCase):
    def test_pyoptix_primary_readiness_restores_exact_current_context(self) \
            -> None:
        driver = _CudaDriver(current=0x1234)
        runtime = _CudaRuntime(driver)
        evidence = pilot._pyoptix_primary_ready_preserving_current(
            runtime, driver=driver)
        self.assertEqual(runtime.free_calls, [0])
        self.assertEqual(driver.current, 0x1234)
        self.assertEqual(driver.set_calls, [0x1234])
        self.assertTrue(evidence["exact_current_context_restored"])
        self.assertEqual(evidence["cuCtxGetCurrent_before"], 0x1234)
        self.assertEqual(evidence["cuCtxGetCurrent_after_restore"], 0x1234)

    def test_pyoptix_primary_readiness_restores_context_on_failure(self) -> None:
        driver = _CudaDriver(current=0x5678)
        runtime = _CudaRuntime(driver, fail_after_change=True)
        with self.assertRaisesRegex(RuntimeError, "synthetic free failure"):
            pilot._pyoptix_primary_ready_preserving_current(
                runtime, driver=driver)
        self.assertEqual(driver.current, 0x5678)
        self.assertEqual(driver.set_calls, [0x5678])

    def test_rtdl_bind_guard_rejects_current_context_side_effect(self) -> None:
        driver = _CudaDriver(current=0)

        def operation() -> object:
            driver.current = 0x9999
            return object()

        with self.assertRaisesRegex(RuntimeError, "bind_changed_current_context"):
            pilot._call_requiring_current_unchanged(
                operation, driver=driver)

    def test_device0_primary_lease_spans_lifecycle_and_balances(self) -> None:
        driver = _CudaDriver(current=0xABCD)
        with pilot._Device0PrimaryCurrentLease(
                driver, expected_preexisting_primary_handle=driver.primary,
                persistent_owner="RTDL_PROCESS_LIFETIME_RETAIN") as lease:
            self.assertEqual(driver.current, driver.primary)
            self.assertEqual(driver.retain_calls, [0])
            self.assertEqual(driver.release_calls, [])
            lease.verify_current("AFTER_APP_PREPARE")
            lease.verify_current("AFTER_FIRST_EXACT_OUTPUT")
            lease.verify_current("AFTER_STEADY")
        self.assertEqual(driver.current, 0xABCD)
        self.assertEqual(driver.release_calls, [0])
        self.assertTrue(lease.evidence["temporary_primary_retain_balanced"])
        self.assertTrue(
            lease.evidence["temporary_primary_retain_live_through_close"])
        self.assertTrue(lease.evidence["exact_prior_current_restored"])
        self.assertLess(
            driver.events.index("set:43981"),
            driver.events.index("release"))

    def test_device0_primary_lease_rejects_wrong_target_capability(self) -> None:
        driver = _CudaDriver(capability=(8, 9))
        with self.assertRaisesRegex(
                RuntimeError, "target_compute_capability_mismatch"):
            with pilot._Device0PrimaryCurrentLease(
                    driver, persistent_owner="synthetic"):
                pass
        self.assertEqual(driver.retain_calls, [])

    def test_device0_primary_lease_rejects_wrong_current_device(self) -> None:
        driver = _CudaDriver(current_device=1)
        with self.assertRaisesRegex(RuntimeError, "primary_current_drift"):
            with pilot._Device0PrimaryCurrentLease(
                    driver, persistent_owner="synthetic"):
                pass
        self.assertEqual(driver.release_calls, [0])

    def test_device0_primary_lease_pid_thread_guard_precedes_cuda_calls(
            self) -> None:
        driver = _CudaDriver()
        with pilot._Device0PrimaryCurrentLease(
                driver, persistent_owner="synthetic") as lease:
            get_current_before = driver.get_current_call_count
            get_device_before = driver.get_device_call_count
            original_pid = lease.owner_pid
            lease.owner_pid = original_pid + 1
            try:
                with self.assertRaisesRegex(
                        RuntimeError, "primary_lease_owner_drift"):
                    lease.verify_current("HOSTILE_PID_DRIFT")
            finally:
                lease.owner_pid = original_pid
            self.assertEqual(
                driver.get_current_call_count, get_current_before)
            self.assertEqual(
                driver.get_device_call_count, get_device_before)
            original_thread = lease.owner_thread_ident
            lease.owner_thread_ident = original_thread + 1
            try:
                with self.assertRaisesRegex(
                        RuntimeError, "primary_lease_owner_drift"):
                    lease.verify_current("HOSTILE_THREAD_DRIFT")
            finally:
                lease.owner_thread_ident = original_thread
            self.assertEqual(
                driver.get_current_call_count, get_current_before)
            self.assertEqual(
                driver.get_device_call_count, get_device_before)

    def test_device0_primary_lease_retain_failure_has_no_release(self) -> None:
        driver = _CudaDriver(retain_status=7)
        with self.assertRaisesRegex(
                RuntimeError, "cuDevicePrimaryCtxRetain_status"):
            with pilot._Device0PrimaryCurrentLease(
                    driver, persistent_owner="synthetic"):
                pass
        self.assertEqual(driver.release_calls, [])

    def test_device0_primary_lease_set_failure_restores_and_releases(self) \
            -> None:
        driver = _CudaDriver(current=0xABCD, set_fail_values=frozenset({
            0xD00D,
        }))
        with self.assertRaisesRegex(RuntimeError, "cuCtxSetCurrent_status"):
            with pilot._Device0PrimaryCurrentLease(
                    driver, persistent_owner="synthetic"):
                pass
        self.assertEqual(driver.current, 0xABCD)
        self.assertEqual(driver.release_calls, [0])

    def test_device0_primary_lease_restore_failure_still_releases(self) -> None:
        driver = _CudaDriver(
            current=0xABCD, set_fail_values=frozenset({0xABCD}))
        with self.assertRaisesRegex(
                RuntimeError, "primary_current_cleanup_failed"):
            with pilot._Device0PrimaryCurrentLease(
                    driver, persistent_owner="synthetic"):
                pass
        self.assertEqual(driver.release_calls, [0])

    def test_device0_primary_lease_release_failure_is_terminal(self) -> None:
        driver = _CudaDriver(current=0xABCD, release_status=9)
        with self.assertRaisesRegex(
                RuntimeError, "primary_current_cleanup_failed"):
            with pilot._Device0PrimaryCurrentLease(
                    driver, persistent_owner="synthetic"):
                pass
        self.assertEqual(driver.release_calls, [0])

    def test_pilot_no_longer_claims_primary_ready_in_preload(self) -> None:
        source = inspect.getsource(pilot)
        self.assertNotIn("PYOPTIX_EXTENSION_PRIMARY_READY_IN_PRELOAD", source)
        self.assertNotIn("provider_ready_boundary_symmetric", source)
        self.assertIn("timer_entry_state_mechanically_matched", source)
        self.assertIn(
            "cuda_current_context_is_device0_primary_at_app_timer_entry",
            source)
        for field in (
                '"paper_claim_authorized": False',
                '"inferential_claim_authorized": False',
                '"threshold_claim_authorized": False',
                '"formal_design_input_only": True'):
            self.assertIn(field, source)

    def test_two_prefix_timers_are_positive_and_contiguous(self) -> None:
        rows = pilot._contiguous_prefix_boundaries(
            harness_run_entry_ns=10,
            post_runtime_preload_entry_ns=30,
            first_exact_output_validated_ns=130)
        self.assertEqual(set(rows), {
            "HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT",
            "POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT",
        })
        self.assertEqual(
            rows["HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT"]["duration_ns"],
            120)
        self.assertEqual(
            rows["POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT"]["duration_ns"],
            100)
        self.assertGreater(
            rows["HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT"]["duration_ns"],
            rows["POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT"]["duration_ns"])
        self.assertEqual(
            rows["HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT"]["duration_ns"]
            - rows["POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT"]["duration_ns"],
            20)
        for row in rows.values():
            self.assertGreater(row["duration_ns"], 0)
            self.assertTrue(row["single_contiguous_timer"])
            self.assertEqual(
                row["stop_event"], "FIRST_EXACT_OUTPUT_VALIDATED")

    def test_prefix_timer_instrumentation_is_adjacent_to_boundaries(self) \
            -> None:
        wrapper = inspect.getsource(pilot._run)
        self.assertLess(
            wrapper.index("harness_run_entry_ns = time.perf_counter_ns()"),
            wrapper.index("primary_stack = ExitStack()"))
        implementation = inspect.getsource(pilot._run_impl)
        preload_return = implementation.index(
            "post_runtime_preload_entry_ns = time.perf_counter_ns()")
        adapter_construct = implementation.index(
            'with ledger.phase("adapter_construct")')
        self.assertLess(preload_return, adapter_construct)
        execute = implementation.index("first_result = execute()")
        stop = implementation.index(
            "first_exact_output_validated_ns = time.perf_counter_ns()")
        post_assertion = implementation.index(
            '"IMMEDIATELY_AFTER_FIRST_EXACT_OUTPUT_CLOCK"')
        self.assertLess(execute, stop)
        self.assertLess(stop, post_assertion)

    def test_provider_ready_context_factory_skips_only_redundant_free(self) \
            -> None:
        provider_ready = inspect.getsource(
            pilot._make_provider_ready_validation_off_context)
        raw_default = inspect.getsource(
            pyoptix_scalar_arm._make_validation_off_context)
        self.assertNotIn(".free(0)", provider_ready)
        self.assertIn(".free(0)", raw_default)
        for required in (
                "optix.init", "DeviceContextOptions", "validationMode",
                "deviceContextCreate"):
            self.assertIn(required, provider_ready)

    def test_provider_ready_context_factory_dynamically_avoids_free(self) \
            -> None:
        calls: list[str] = []

        class Runtime:
            def free(self, _value: int) -> None:
                raise AssertionError("provider-ready factory called free(0)")

        class Options:
            validationMode: object | None = None

        class Optix:
            DEVICE_CONTEXT_VALIDATION_MODE_OFF = object()

            def init(self) -> None:
                calls.append("init")

            def DeviceContextOptions(self) -> Options:
                calls.append("options")
                return Options()

            def deviceContextCreate(
                self, ordinal: int, options: Options,
            ) -> object:
                self.assertions = (
                    ordinal == 0
                    and options.validationMode
                    is self.DEVICE_CONTEXT_VALIDATION_MODE_OFF)
                calls.append("create")
                return object()

        optix = Optix()
        baseline = SimpleNamespace(
            cp=SimpleNamespace(cuda=SimpleNamespace(runtime=Runtime())),
            optix=optix)
        context, logger = \
            pilot._make_provider_ready_validation_off_context(baseline)
        self.assertIsNotNone(context)
        self.assertIsNone(logger)
        self.assertTrue(optix.assertions)
        self.assertEqual(calls, ["init", "options", "create"])

    def test_pyoptix_partial_close_is_labeled_without_claim_inflation(self) \
            -> None:
        source = inspect.getsource(pilot._run_impl)
        self.assertIn(
            "PARTIAL_OWNER_CLOSE__PROCESS_TEARDOWN_RETAINS_CONTEXT_PIPELINE_SBT",
            source)
        for key in (
                '"context_retained"', '"pipeline_retained"',
                '"sbt_retained"'):
            self.assertIn(key, source)

    @unittest.skipUnless(
        os.name == "posix" and hasattr(os, "memfd_create"),
        "Linux write-sealed memfd required",
    )
    def test_relation_cubin_memfd_is_write_sealed_and_rehashes(self) -> None:
        data = b"\x7fELF" + bytes(range(64))
        identity = pyoptix_scalar_arm._create_write_sealed_memfd(data)
        try:
            pyoptix_scalar_arm._validate_write_sealed_memfd(identity)
            self.assertTrue(identity["write_sealed"])
            self.assertEqual(
                identity["sha256"],
                hashlib.sha256(data).hexdigest())
            with self.assertRaises(OSError):
                os.write(identity["fd"], b"x")
        finally:
            os.close(identity["fd"])

    def test_relation_prepare_uses_held_proc_fd_not_original_path(self) -> None:
        source = inspect.getsource(
            pyoptix_scalar_arm.PyOptixScalarAdapter.prepare)
        self.assertIn(
            'path=self._compaction_cubin_memfd["proc_fd_path"]', source)
        self.assertNotIn("compaction_cubin_path.resolve", source)

    def test_relation_prepare_passes_exact_sealed_proc_fd_to_rawmodule(self) \
            -> None:
        observed_paths: list[str] = []

        class RawModule:
            def __init__(self, *, path: str) -> None:
                observed_paths.append(path)

            def get_function(self, _name: str) -> object:
                return object()

        class Context:
            def setCacheEnabled(self, value: bool) -> None:
                self.cache_enabled = value

        class Owner:
            def __init__(self, *_args: object, **_kwargs: object) -> None:
                pass

            def execute(self) -> object:
                return object()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ptx = root / "matched.ptx"
            cubin = root / "relation.cubin"
            ptx.write_bytes(b".version 8.0\n")
            cubin_bytes = b"\x7fELFsealed-cubin"
            cubin.write_bytes(cubin_bytes)
            baseline = SimpleNamespace(
                __name__=pyoptix_scalar_arm.PYOPTIX_BASELINE_MODULE,
                cp=SimpleNamespace(RawModule=RawModule),
                make_sbt=lambda _keepalive: (object(), object()),
            )
            workload = {
                "indexed": [], "sources": [], "minimum_overlap_f32": 1.0,
                "semantic_capacity": 1, "expected_rows": [],
            }
            adapter = pyoptix_scalar_arm.PyOptixScalarAdapter(
                RELATION_TASK, workload, ptx_path=ptx,
                compaction_cubin_path=cubin,
                preloaded_runtime=baseline,
                runtime_preload_receipt={"status": "synthetic"})
            identity = {
                "fd": 99, "proc_fd_path": "/proc/self/fd/99",
                "bytes": len(cubin_bytes),
                "sha256": hashlib.sha256(cubin_bytes).hexdigest(),
                "seal_mask": 15, "observed_seals": 15,
                "stat_device": 1, "stat_inode": 2, "write_sealed": True,
            }
            with mock.patch.object(
                    pyoptix_scalar_arm, "_create_write_sealed_memfd",
                    return_value=identity), mock.patch.object(
                    pyoptix_scalar_arm, "_validate_write_sealed_memfd"), \
                    mock.patch.object(
                        pyoptix_scalar_arm, "_make_validation_off_context",
                        return_value=(Context(), None)), mock.patch.object(
                        pyoptix_scalar_arm, "_build_comparative_pipeline",
                        return_value=(object(), object(), {})), \
                    mock.patch.object(
                        pyoptix_scalar_arm, "DeferredRelationPrepared", Owner):
                adapter.load()
                adapter.prepare()
        self.assertEqual(observed_paths, ["/proc/self/fd/99"])
        self.assertEqual(
            adapter._compaction_cubin_source_sha256,
            hashlib.sha256(cubin_bytes).hexdigest())

    def test_relation_runtime_identity_does_not_reopen_cubin_path(self) -> None:
        source = inspect.getsource(
            pyoptix_scalar_arm.PyOptixScalarAdapter.runtime_identity)
        self.assertNotIn("compaction_cubin_path.read_bytes", source)
        self.assertNotIn("compaction_cubin_path.resolve", source)

    def test_relation_fd_closes_after_owner_and_module_release(self) -> None:
        order: list[str] = []

        class Owner:
            compaction_kernel = object()

            def close(self) -> None:
                order.append("owner.close")

        adapter = object.__new__(pyoptix_scalar_arm.PyOptixScalarAdapter)
        adapter.task = RELATION_TASK
        adapter.owner = Owner()
        adapter._measurement_execute = object()
        adapter.compaction_kernel = object()
        adapter.compaction_module = object()
        adapter._compaction_cubin_memfd = {"fd": 41}
        adapter._compaction_cubin_memfd_closed = False

        def close_fd(value: int) -> None:
            self.assertIsNone(adapter.owner)
            self.assertIsNone(adapter.compaction_module)
            self.assertIsNone(adapter.compaction_kernel)
            order.append(f"fd.close:{value}")

        with mock.patch.object(pyoptix_scalar_arm.os, "close", close_fd):
            adapter.close()
        self.assertEqual(order, ["owner.close", "fd.close:41"])
        self.assertTrue(adapter.compaction_cubin_loader_closed)

    def test_relation_fd_closes_even_when_owner_close_fails(self) -> None:
        order: list[str] = []

        class Owner:
            compaction_kernel = object()

            def close(self) -> None:
                order.append("owner.close")
                raise RuntimeError("synthetic owner close failure")

        adapter = object.__new__(pyoptix_scalar_arm.PyOptixScalarAdapter)
        adapter.task = RELATION_TASK
        adapter.owner = Owner()
        adapter._measurement_execute = object()
        adapter.compaction_kernel = object()
        adapter.compaction_module = object()
        adapter._compaction_cubin_memfd = {"fd": 42}
        adapter._compaction_cubin_memfd_closed = False

        def close_fd(value: int) -> None:
            order.append(f"fd.close:{value}")

        with mock.patch.object(pyoptix_scalar_arm.os, "close", close_fd):
            with self.assertRaisesRegex(
                    RuntimeError, "synthetic owner close failure"):
                adapter.close()
        self.assertEqual(order, ["owner.close", "fd.close:42"])
        self.assertTrue(adapter.compaction_cubin_loader_closed)

    def test_phase_ledger_closes_without_dropping_between_phase_cost(self) -> None:
        clock = _Clock()
        ledger = pilot._PhaseLedger(process_entry_ns=0, clock_ns=clock)
        clock.advance(5)
        observed_sum = 0
        for index, name in enumerate(pilot.PHASES):
            if name == "provider_session_close":
                ledger.unavailable(name, reason="synthetic missing state")
                clock.advance(2)
                continue
            with ledger.phase(name):
                duration = index + 1
                clock.advance(duration)
                observed_sum += duration
            clock.advance(2)
        result = ledger.finalize(process_stop_ns=clock())
        self.assertEqual(result["observed_phase_sum_ns_additive"], observed_sum)
        self.assertEqual(
            result["observed_phase_sum_ns_additive"]
            + result["between_phase_unclassified_ns_additive"],
            result["total_profiled_full_process_ns"])
        self.assertEqual(
            result["additive_closure_ns"],
            result["total_profiled_full_process_ns"])
        self.assertIsNone(
            result["phases"]["provider_session_close"]["duration_ns"])
        self.assertFalse(result["nonobserved_phase_zero_imputed"])

    def test_phase_ledger_rejects_missing_or_duplicate_phase(self) -> None:
        clock = _Clock()
        ledger = pilot._PhaseLedger(process_entry_ns=0, clock_ns=clock)
        with ledger.phase("input_admission"):
            clock.advance(1)
        with self.assertRaisesRegex(RuntimeError, "phase repeated"):
            with ledger.phase("input_admission"):
                pass
        with self.assertRaisesRegex(RuntimeError, "missing_phases"):
            ledger.finalize(process_stop_ns=clock())

    def test_phase_ledger_rejects_out_of_order_phase(self) -> None:
        clock = _Clock()
        ledger = pilot._PhaseLedger(process_entry_ns=0, clock_ns=clock)
        with self.assertRaisesRegex(RuntimeError, "phase_order_drift"):
            with ledger.phase("runtime_preload"):
                pass

    def test_comparable_boundary_excludes_delayed_prepared_close(self) -> None:
        phase_ledger = {
            "phases": {
                "app_prepare": {
                    "status": "OBSERVED", "duration_ns": 700,
                },
                "first_exact_execute": {
                    "status": "OBSERVED", "duration_ns": 300,
                },
                "prepared_close": {
                    "status": "OBSERVED", "duration_ns": 9_000_000,
                },
            }
        }
        self.assertEqual(
            pilot._comparable_app_boundary_ns(phase_ledger), 1_000)

    def test_raw_prepare_default_is_byte_shape_compatible_and_unbound(self) -> None:
        adapter, loaded, provider, order = _adapter_fixture()
        adapter.load()
        adapter.prepare()
        self.assertIsNone(adapter.provider)
        self.assertEqual(len(loaded.raw_prepare_calls), 1)
        self.assertEqual(provider.prepare_calls, [])
        self.assertEqual(
            loaded.raw_prepare_calls[0][1], adapter.paths.native_library)
        adapter.close()
        self.assertEqual(order, ["loaded.prepare_raw", "prepared.close"])
        self.assertFalse(provider.closed)

    def test_explicit_bind_uses_capability_and_closes_prepared_then_provider(self) \
            -> None:
        adapter, loaded, provider, order = _adapter_fixture()
        adapter.load()
        self.assertIs(adapter.bind_provider(), provider)
        adapter.prepare()
        self.assertEqual(loaded.raw_prepare_calls, [])
        self.assertEqual(len(provider.prepare_calls), 1)
        adapter.close()
        self.assertEqual(order, [
            "loaded.bind_provider", "provider.prepare",
            "prepared.close", "provider.close",
        ])
        self.assertTrue(provider.closed)

    def test_provider_closes_even_when_prepared_close_fails(self) -> None:
        adapter, _loaded, provider, order = _adapter_fixture(
            prepared_close_error=True)
        adapter.load()
        adapter.bind_provider()
        adapter.prepare()
        with self.assertRaisesRegex(RuntimeError, "prepared close failed"):
            adapter.close()
        self.assertEqual(order[-2:], ["prepared.close", "provider.close"])
        self.assertTrue(provider.closed)

    def test_separate_provider_close_requires_prepared_close_first(self) -> None:
        adapter, _loaded, provider, order = _adapter_fixture()
        adapter.load()
        adapter.bind_provider()
        adapter.prepare()
        with self.assertRaisesRegex(RuntimeError, "precedes prepared close"):
            adapter.close_provider()
        adapter.close_prepared()
        adapter.close_provider()
        self.assertEqual(order[-2:], ["prepared.close", "provider.close"])
        self.assertTrue(provider.closed)

    def test_provider_bind_state_machine_fails_closed(self) -> None:
        adapter, _loaded, _provider, _order = _adapter_fixture()
        with self.assertRaisesRegex(RuntimeError, "precedes load"):
            adapter.bind_provider()
        adapter.load()
        adapter.bind_provider()
        with self.assertRaisesRegex(RuntimeError, "called twice"):
            adapter.bind_provider()
        adapter.prepare()
        with self.assertRaisesRegex(RuntimeError, "follows prepare"):
            # Force only the ordering branch; the public method would normally
            # reject the already-bound state first if tested in reverse order.
            adapter.provider = None
            adapter.bind_provider()


if __name__ == "__main__":
    unittest.main()
