from __future__ import annotations

import hashlib
from types import SimpleNamespace
import unittest

from scripts import goal5807_symmetric_prepare_profiler as profiler


class _Clock:
    def __init__(self) -> None:
        self.value = 0

    def __call__(self) -> int:
        return self.value

    def advance(self, value: int) -> None:
        self.value += value


def _declare_absent(
    recorder: profiler._TraceRecorder, phase: str, *observed: str,
) -> None:
    for category in profiler.REQUIRED_CATEGORIES:
        if category not in observed:
            recorder.declare_coverage(
                phase=phase, category=category, status="NOT_APPLICABLE",
                reason="synthetic test has no such event")


class SymmetricPrepareProfilerTest(unittest.TestCase):
    def test_nested_exclusive_accounting_closes_without_double_counting(self) -> None:
        clock = _Clock()
        recorder = profiler._TraceRecorder(clock_ns=clock)
        with recorder.phase("prepare"):
            clock.advance(10)
            with recorder.span(
                    phase="prepare", category="owner_remainder",
                    label="owner"):
                clock.advance(10)
                with recorder.span(
                        phase="prepare", category="native_prepare_abi",
                        label="native"):
                    clock.advance(30)
                clock.advance(20)
            clock.advance(10)
        recorder.declare_coverage(
            phase="prepare", category="owner_remainder", status="OBSERVED",
            reason="synthetic owner")
        recorder.declare_coverage(
            phase="prepare", category="native_prepare_abi", status="OBSERVED",
            reason="synthetic native ABI")
        _declare_absent(
            recorder, "prepare", "owner_remainder", "native_prepare_abi")

        trace = recorder.finalize()
        phase = trace["phases"]["prepare"]
        self.assertEqual(phase["wall_ns"], 80)
        self.assertEqual(
            phase["categories"]["owner_remainder"]
            ["inclusive_sum_ns_nonadditive"], 60)
        self.assertEqual(
            phase["categories"]["owner_remainder"]
            ["exclusive_sum_ns_additive"], 30)
        self.assertEqual(
            phase["categories"]["native_prepare_abi"]
            ["exclusive_sum_ns_additive"], 30)
        self.assertEqual(phase["unclassified_exclusive_ns_additive"], 20)
        self.assertEqual(phase["additive_closure_ns"], 80)

    def test_folded_category_is_null_not_zero(self) -> None:
        clock = _Clock()
        recorder = profiler._TraceRecorder(clock_ns=clock)
        with recorder.phase("prepare"):
            clock.advance(17)
        for category in profiler.REQUIRED_CATEGORIES:
            recorder.declare_coverage(
                phase="prepare", category=category,
                status="FOLDED_INTO_NATIVE_PREPARE_ABI",
                reason="synthetic unobservable native phase",
                folded_into="native_prepare_abi")

        row = recorder.finalize()["phases"]["prepare"]["categories"]["gas"]
        self.assertEqual(row["event_count"], 0)
        self.assertIsNone(row["inclusive_sum_ns_nonadditive"])
        self.assertIsNone(row["exclusive_sum_ns_additive"])
        self.assertEqual(row["folded_into"], "native_prepare_abi")

    def test_missing_observed_hook_fails_closed(self) -> None:
        clock = _Clock()
        recorder = profiler._TraceRecorder(clock_ns=clock)
        with recorder.phase("prepare"):
            clock.advance(1)
        for category in profiler.REQUIRED_CATEGORIES:
            recorder.declare_coverage(
                phase="prepare", category=category,
                status=("OBSERVED" if category == "gas" else "NOT_APPLICABLE"),
                reason="synthetic declaration")
        with self.assertRaisesRegex(RuntimeError, "observed hook is absent"):
            recorder.finalize()

    def test_event_contradicting_not_applicable_declaration_fails(self) -> None:
        clock = _Clock()
        recorder = profiler._TraceRecorder(clock_ns=clock)
        with recorder.phase("prepare"):
            with recorder.span(
                    phase="prepare", category="gas", label="unexpected"):
                clock.advance(1)
        for category in profiler.REQUIRED_CATEGORIES:
            recorder.declare_coverage(
                phase="prepare", category=category, status="NOT_APPLICABLE",
                reason="synthetic declaration")
        with self.assertRaisesRegex(RuntimeError, "declared unobservable"):
            recorder.finalize()

    def test_rtdl_load_allows_observed_dependency_cdll_provider_event(self) -> None:
        clock = _Clock()
        recorder = profiler._TraceRecorder(clock_ns=clock)
        with recorder.phase("load"):
            with recorder.span(
                    phase="load", category="artifact_verification",
                    label="rtdl_load"):
                clock.advance(2)
                with recorder.span(
                        phase="load", category="provider_native_acquisition",
                        label="dependency_cdll"):
                    clock.advance(3)
                clock.advance(5)
        profiler._declare_primary_coverage(recorder, arm="RTDL")

        rows = recorder.finalize()["phases"]["load"]["categories"]
        self.assertEqual(
            rows["provider_native_acquisition"]["event_count"], 1)
        self.assertEqual(
            rows["provider_native_acquisition"]["status"],
            "OPTIONAL_OBSERVED__LOAD_DEPENDENCY_CDLL_BOUNDARY")
        self.assertEqual(
            rows["provider_native_acquisition"]
            ["exclusive_sum_ns_additive"], 3)

    def test_ctypes_proxy_forwards_interface_and_times_exact_call(self) -> None:
        clock = _Clock()

        class Function:
            argtypes = None
            restype = None

            def __call__(self, value: int) -> int:
                clock.advance(19)
                return value + 1

        function = Function()
        recorder = profiler._TraceRecorder(clock_ns=clock)
        proxy = profiler._CTypesFunctionProxy(
            function, recorder, label="native_prepare")
        proxy.argtypes = [int]
        proxy.restype = int
        with recorder.phase("prepare"):
            self.assertEqual(proxy(6), 7)
        self.assertEqual(function.argtypes, [int])
        self.assertIs(function.restype, int)
        recorder.declare_coverage(
            phase="prepare", category="native_prepare_abi", status="OBSERVED",
            reason="synthetic native call")
        _declare_absent(recorder, "prepare", "native_prepare_abi")
        row = recorder.finalize()["phases"]["prepare"]["categories"] \
            ["native_prepare_abi"]
        self.assertEqual(row["inclusive_sum_ns_nonadditive"], 19)
        self.assertEqual(row["exclusive_sum_ns_additive"], 19)

    def test_rtdl_hook_attaches_proxy_to_exact_prepare_export(self) -> None:
        clock = _Clock()

        class NativePrepare:
            argtypes = None
            restype = None

            def __call__(self, value: int) -> int:
                clock.advance(23)
                return value

        native_prepare = NativePrepare()
        lease = SimpleNamespace(
            rtdl_optix_v4_prepare_bounded_relation_callback_v1=native_prepare)

        class Loaded:
            def prepare(self) -> None:
                return None

        implementation = SimpleNamespace(
            _initialize_cuda_and_get_capability=lambda: (8, 6),
            _read_descriptor_bytes=lambda *args, **kwargs: b"native",
            _sealed_native_image_descriptor=lambda *args, **kwargs: 1,
            _create_unique_native_loader_alias=lambda *args, **kwargs: "alias",
            _validate_cached_native_image=lambda *args, **kwargs: None,
            _load_verified_native_file_descriptor=lambda *args, **kwargs: lease,
            _load_native_library=lambda *args, **kwargs: lease,
            _query_native_producer_descriptor=lambda *args, **kwargs: {},
            _sha_bytes=lambda value: hashlib.sha256(value).hexdigest(),
            _PreparedBoundedOwner=lambda *args, **kwargs: object(),
            _PreparedTriangleOwner=lambda *args, **kwargs: object(),
            LoadedRTDLExecutable=Loaded,
            ctypes=SimpleNamespace(CDLL=lambda *args, **kwargs: object()),
        )
        runtime = SimpleNamespace(
            install_rtdlexe_deployment=lambda *args, **kwargs: object(),
            load_rtdlexe=lambda *args, **kwargs: object(),
        )
        recorder = profiler._TraceRecorder(clock_ns=clock)
        with profiler._Patches() as patches:
            profiler._install_rtdl_hooks(
                patches, recorder, runtime, implementation, "relation")
            with recorder.phase("prepare"):
                observed_lease = implementation._load_native_library()
                observed_prepare = getattr(
                    observed_lease,
                    "rtdl_optix_v4_prepare_bounded_relation_callback_v1")
                observed_prepare.argtypes = [int]
                observed_prepare.restype = int
                self.assertEqual(observed_prepare(4), 4)
        self.assertEqual(native_prepare.argtypes, [int])
        self.assertIs(native_prepare.restype, int)
        observed = {"provider_native_acquisition", "native_prepare_abi"}
        for category in observed:
            recorder.declare_coverage(
                phase="prepare", category=category, status="OBSERVED",
                reason="synthetic RTDL hook")
        _declare_absent(recorder, "prepare", *observed)
        rows = recorder.finalize()["phases"]["prepare"]["categories"]
        self.assertEqual(
            rows["native_prepare_abi"]["exclusive_sum_ns_additive"], 23)

    def test_context_proxy_splits_module_program_group_and_pipeline(self) -> None:
        clock = _Clock()

        class Context:
            def moduleCreate(self) -> str:
                clock.advance(2)
                return "module"

            def programGroupCreate(self) -> str:
                clock.advance(3)
                return "group"

            def pipelineCreate(self) -> str:
                clock.advance(5)
                return "pipeline"

            def setCacheEnabled(self, value: bool) -> bool:
                clock.advance(7)
                return value

        recorder = profiler._TraceRecorder(clock_ns=clock)
        context = profiler._PyOptixContextProxy(Context(), recorder)
        with recorder.phase("prepare"):
            self.assertEqual(context.moduleCreate(), "module")
            self.assertEqual(context.programGroupCreate(), "group")
            self.assertEqual(context.pipelineCreate(), "pipeline")
            self.assertFalse(context.setCacheEnabled(False))
        observed = {
            "driver_context", "module_create", "program_groups",
            "pipeline_link_stack",
        }
        for category in observed:
            recorder.declare_coverage(
                phase="prepare", category=category, status="OBSERVED",
                reason="synthetic context call")
        _declare_absent(recorder, "prepare", *observed)
        rows = recorder.finalize()["phases"]["prepare"]["categories"]
        self.assertEqual(rows["module_create"]["exclusive_sum_ns_additive"], 2)
        self.assertEqual(rows["program_groups"]["exclusive_sum_ns_additive"], 3)
        self.assertEqual(
            rows["pipeline_link_stack"]["exclusive_sum_ns_additive"], 5)
        self.assertEqual(rows["driver_context"]["exclusive_sum_ns_additive"], 7)

    def test_missing_pyoptix_init_is_explicit_and_nonfatal(self) -> None:
        function = lambda *args, **kwargs: object()
        runtime = SimpleNamespace(free=function)
        cuda = SimpleNamespace(
            runtime=runtime, alloc=function, alloc_pinned_memory=function,
            Stream=function)
        cp = SimpleNamespace(
            cuda=cuda, zeros=function, empty=function, asarray=function,
            RawModule=function)
        optix = SimpleNamespace(deviceContextCreate=function)
        baseline = SimpleNamespace(
            cp=cp, optix=optix, make_sbt=function,
            build_custom_gas=function, build_triangle_gas=function,
            to_device=function)
        arm = SimpleNamespace(
            _make_validation_off_context=function,
            _build_comparative_pipeline=function,
            DeferredRelationPrepared=function,
            ScalarTrianglePrepared=function)
        recorder = profiler._TraceRecorder()
        with profiler._Patches() as patches:
            profiler._install_pyoptix_hooks(
                patches, recorder, arm, baseline, "relation")

        availability = recorder.finalize()["hook_availability"]
        self.assertEqual(
            availability["pyoptix_optix_init"]["status"],
            "NOT_EXPOSED_BY_INSTALLED_BINDING")

    def test_patch_set_is_restored_after_exception(self) -> None:
        class Owner:
            value = "before"

        owner = Owner()
        with self.assertRaisesRegex(RuntimeError, "stop"):
            with profiler._Patches() as patches:
                patches.set(owner, "value", "during")
                self.assertEqual(owner.value, "during")
                raise RuntimeError("stop")
        self.assertEqual(owner.value, "before")

    def test_canonical_json_and_digest_are_deterministic(self) -> None:
        value = {"z": [2, 1], "a": {"b": True}}
        expected = b'{"a":{"b":true},"z":[2,1]}'
        self.assertEqual(profiler._canonical(value), expected)
        self.assertEqual(
            profiler._digest(value), hashlib.sha256(expected).hexdigest())


if __name__ == "__main__":
    unittest.main()
