#!/usr/bin/env python3
"""Goal5802 Python-arm worker with symmetric phase boundaries.

The executable path is dormant until the controller supplies a separately
sealed two-key execution authority.  Unit tests exercise ``run_adapter`` with
fake adapters and a fake clock; no local test records a performance sample.
"""

from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Mapping

from .contract import (
    ARMS,
    REGIMES,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    validate_freeze,
)
from .controller import (
    consume_formal_worker_live_capability,
    validate_execution_authority,
    validate_formal_worker_preflight_gate,
)
from .pyoptix_scalar_arm import (
    ARM as PYOPTIX_ARM,
    PyOptixScalarAdapter,
    preload_pyoptix_runtime,
)
from .rtdlexe_arm import (
    ARM as RTDL_ARM,
    RTDLDeploymentPaths,
    RTDLExecutableAdapter,
    preload_rtdl_runtime,
)
from .runtime_manifest import validate_runtime_manifest_document
from .workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    relation_workload,
    triangle_workload,
)


Clock = Callable[[], int]
PRIMARY_TIMER_NEW_MODULE_LOAD_POLICY = "REJECT_ALL_NOT_PRELOADED"


def _matches_forbidden_primary_import(fullname: str) -> bool:
    # ``sys.meta_path`` is consulted only for a module that is not already in
    # ``sys.modules``.  Rejecting every such request makes the boundary
    # symmetric for RTDL, PyOptiX, CuPy, NumPy, OptiX and ordinary lazy Python
    # dependencies; no arm gets an unreported first import inside a 1--2% gate.
    return isinstance(fullname, str) and bool(fullname)


def validate_warm_process_import_source_boundary(
        source_overrides: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Prove adapters contain no cached-import escape into primary phases."""

    paths = {
        "worker": Path(__file__).resolve(),
        "pyoptix": Path(__file__).with_name("pyoptix_scalar_arm.py").resolve(),
        "rtdl": Path(__file__).with_name("rtdlexe_arm.py").resolve(),
        "baseline": (
            Path(__file__).resolve().parents[1]
            / "goal5796_matched" / "pyoptix_baseline.py"),
    }
    texts = {
        role: (
            source_overrides[role]
            if source_overrides is not None and role in source_overrides
            else path.read_text(encoding="utf-8"))
        for role, path in paths.items()
    }
    trees = {role: ast.parse(text, filename=str(paths[role]))
             for role, text in texts.items()}

    forbidden_calls = {
        "importlib.import_module", "builtins.__import__", "__import__",
    }

    def dotted(node: ast.AST) -> str | None:
        parts: list[str] = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if not isinstance(node, ast.Name):
            return None
        parts.append(node.id)
        return ".".join(reversed(parts))

    method_rows: list[dict[str, str]] = []
    violations: list[str] = []
    for role, class_name in (
            ("pyoptix", "PyOptixScalarAdapter"),
            ("rtdl", "RTDLExecutableAdapter")):
        classes = [node for node in trees[role].body
                   if isinstance(node, ast.ClassDef)
                   and node.name == class_name]
        if len(classes) != 1:
            violations.append(f"{role}:{class_name}:class_count={len(classes)}")
            continue
        methods = {node.name: node for node in classes[0].body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for method_name in ("load", "prepare", "execute"):
            method = methods.get(method_name)
            if method is None:
                violations.append(f"{role}:{class_name}.{method_name}:absent")
                continue
            for node in ast.walk(method):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    violations.append(
                        f"{role}:{class_name}.{method_name}:import@{node.lineno}")
                elif isinstance(node, ast.Call) \
                        and dotted(node.func) in forbidden_calls:
                    violations.append(
                        f"{role}:{class_name}.{method_name}:"
                        f"{dotted(node.func)}@{node.lineno}")
            method_rows.append({"role": role, "class": class_name,
                                "method": method_name})

    # The runtime methods call module-level and owner helpers.  Reject cached
    # import escapes anywhere in either adapter module, not only in the three
    # immediately visible facade methods.  The only allowed dynamic-import
    # sites are the explicit preloader and the post-execution PyOptiX identity
    # query; neither is inside the comparative primary boundary.
    allowed_dynamic_import_functions = {
        "pyoptix": {
            ("preload_pyoptix_runtime", "importlib.import_module"),
            ("runtime_identity", "__import__"),
        },
        "rtdl": {
            ("preload_rtdl_runtime", "importlib.import_module"),
        },
    }
    for role in ("pyoptix", "rtdl"):
        for function in (
                node for node in ast.walk(trees[role])
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            for node in ast.walk(function):
                if node is function:
                    continue
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    violations.append(
                        f"{role}:{function.name}:nested_import@{node.lineno}")
                elif isinstance(node, ast.Call) \
                        and dotted(node.func) in forbidden_calls \
                        and (function.name, dotted(node.func)) \
                        not in allowed_dynamic_import_functions[role]:
                    violations.append(
                        f"{role}:{function.name}:"
                        f"{dotted(node.func)}@{node.lineno}")

    baseline_top_imports = []
    for node in trees["baseline"].body:
        if isinstance(node, ast.Import):
            baseline_top_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            baseline_top_imports.append(node.module or "")
    if any(name == "cuda.bindings" or name.startswith("cuda.bindings.nvrtc")
           for name in baseline_top_imports):
        violations.append("baseline:top_level_nvrtc_import")
    unexpected_cli_imports = sorted(set(baseline_top_imports).intersection({
        "argparse", "hashlib", "importlib.metadata", "json", "pathlib",
        "platform", "subprocess",
    }))
    if unexpected_cli_imports:
        violations.append(
            f"baseline:top_level_cli_imports={unexpected_cli_imports}")
    compile_functions = {
        node.name: node for node in trees["baseline"].body
        if isinstance(node, ast.FunctionDef)
        and node.name in {"compile_ptx", "check_nvrtc"}
    }
    if set(compile_functions) != {"compile_ptx", "check_nvrtc"}:
        violations.append("baseline:compiler_functions_absent")
    else:
        for name, function in compile_functions.items():
            if not any(
                    isinstance(node, ast.ImportFrom)
                    and node.module == "cuda.bindings"
                    and any(alias.name == "nvrtc" for alias in node.names)
                    for node in ast.walk(function)):
                violations.append(f"baseline:{name}:lazy_nvrtc_import_absent")

    allowed_baseline_function_imports = {
        "check_nvrtc": {"from cuda.bindings import nvrtc"},
        "compile_ptx": {"from cuda.bindings import nvrtc"},
        "machine_record": {"import platform", "import subprocess"},
        "main": {
            "import argparse", "import hashlib", "import importlib.metadata",
            "import json", "from pathlib import Path",
        },
    }
    for function in (
            node for node in trees["baseline"].body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
        observed_imports: set[str] = set()
        for node in ast.walk(function):
            if isinstance(node, ast.Import):
                observed_imports.update(
                    f"import {alias.name}" for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                observed_imports.update(
                    f"from {node.module or ''} import {alias.name}"
                    for alias in node.names)
        expected_imports = allowed_baseline_function_imports.get(
            function.name, set())
        if observed_imports != expected_imports:
            violations.append(
                f"baseline:{function.name}:nested_imports="
                f"{sorted(observed_imports)}:expected={sorted(expected_imports)}")

    main_functions = [node for node in trees["worker"].body
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "main"]
    if len(main_functions) != 1:
        violations.append(f"worker:main_count={len(main_functions)}")
    else:
        calls = [node for node in ast.walk(main_functions[0])
                 if isinstance(node, ast.Call)]
        preload_lines = {
            name: [node.lineno for node in calls if dotted(node.func) == name]
            for name in ("preload_pyoptix_runtime", "preload_rtdl_runtime")
        }
        run_lines = [node.lineno for node in calls
                     if dotted(node.func) == "run_adapter"]
        if any(len(lines) != 1 for lines in preload_lines.values()) \
                or len(run_lines) != 1 \
                or any(lines[0] >= run_lines[0]
                       for lines in preload_lines.values() if lines):
            violations.append({
                "worker_preload_lines": preload_lines,
                "worker_run_adapter_lines": run_lines,
            }.__repr__())

    if violations:
        raise RuntimeError({"warm_process_import_source_violations": violations})
    return {
        "schema": "rtdl.goal5802.warm_process_import_source_boundary.v1",
        "status": "PASS__SOURCE_ONLY__ZERO_TIMINGS",
        "primary_methods_checked": method_rows,
        "baseline_top_level_nvrtc_import": False,
        "baseline_top_level_cli_or_metadata_import": False,
        "compiler_only_nvrtc_lazy_import_functions": [
            "check_nvrtc", "compile_ptx"],
        "worker_preloads_selected_runtime_before_run_adapter": True,
        "registered_performance_timing_count": 0,
    }


class _RejectNewPrimaryTimerModuleLoad:
    """Fail before a forbidden not-yet-loaded module can enter the timer."""

    @staticmethod
    def find_spec(fullname, path=None, target=None):  # noqa: ANN001
        del path, target
        if _matches_forbidden_primary_import(str(fullname)):
            raise RuntimeError(
                f"Goal5802 forbidden new module load inside primary timer: "
                f"{fullname}")
        return None


@contextmanager
def _primary_timer_import_boundary(contract: dict[str, Any] | None):
    """Require arm runtimes preloaded and compiler-only modules absent.

    Python returns already-loaded modules without consulting ``sys.meta_path``.
    Consequently this boundary rejects *new module loads* at runtime, while a
    source audit separately rejects cached import calls in adapter primary
    methods.  Together they cover both executable and source-level paths.
    """

    if contract is None:
        contract = {
            "required_preloaded_modules": [],
            "forbidden_absent_modules": [],
        }
    if set(contract) != {
            "required_preloaded_modules", "forbidden_absent_modules"}:
        raise RuntimeError("Goal5802 primary import contract keys differ")
    required = contract["required_preloaded_modules"]
    forbidden_absent = contract["forbidden_absent_modules"]
    if not isinstance(required, list) or not isinstance(forbidden_absent, list) \
            or any(not isinstance(name, str) or not name for name in required) \
            or any(not isinstance(name, str) or not name
                   for name in forbidden_absent):
        raise RuntimeError("Goal5802 primary import contract values differ")
    missing = sorted(name for name in required if name not in sys.modules)
    forbidden_present = sorted(
        name for name in forbidden_absent if name in sys.modules)
    if missing or forbidden_present:
        raise RuntimeError({
            "required_runtime_modules_not_preloaded": missing,
            "forbidden_modules_present_before_primary_timer":
                forbidden_present,
        })
    blocker = _RejectNewPrimaryTimerModuleLoad()
    sys.meta_path.insert(0, blocker)
    try:
        yield
    finally:
        if blocker not in sys.meta_path:
            raise RuntimeError("Goal5802 primary import blocker was removed")
        sys.meta_path.remove(blocker)
        forbidden_after = sorted(
            name for name in forbidden_absent if name in sys.modules)
        if forbidden_after:
            raise RuntimeError({
                "forbidden_modules_present_after_primary_timer":
                    forbidden_after,
            })


def run_adapter(
        adapter: Any, regime: str, *, clock: Clock = time.perf_counter_ns,
        local_untimed: bool = False,
        input_materialization_ns: int | None = None,
        process_startup_and_admission_ns: int | None = None) -> dict[str, Any]:
    """Run one arm without putting serialization or close in the main timer."""

    if regime not in REGIMES and not local_untimed:
        raise ValueError(f"unsupported Goal5802 regime: {regime}")
    durations: list[int] = []
    phases: dict[str, int | None] = {
        "process_startup_and_admission": None,
        "input_materialization": None,
        "load_or_deploy": None,
        "prepare": None,
        "steady_warmups": None,
        "complete_execute": None,
        "measurement_evidence_materialization": None,
        "close": None,
        "post_execution_identity_validation": None,
    }
    lifecycle_receipts: list[dict[str, Any]] = []
    measurement_evidence_ns = 0

    def retain_lifecycle(execution: Any) -> None:
        nonlocal measurement_evidence_ns
        evidence_start = None if local_untimed else clock()
        extractor = getattr(adapter, "measurement_lifecycle_receipt", None)
        receipt = (
            extractor(execution) if callable(extractor)
            else execution.get("dynamic_input_receipt")
            if isinstance(execution, dict) else None)
        if not isinstance(receipt, dict):
            raise RuntimeError("Goal5802 execution lacks dynamic-input receipt")
        lifecycle_receipts.append(dict(receipt))
        if evidence_start is not None:
            evidence_end = clock()
            if evidence_end <= evidence_start:
                raise RuntimeError(
                    "Goal5802 lifecycle-evidence duration is nonpositive")
            measurement_evidence_ns += evidence_end - evidence_start

    def finalize(execution: Any) -> dict[str, Any]:
        materializer = getattr(adapter, "finalize_measurement_evidence", None)
        value = materializer(execution) if callable(materializer) else execution
        if not isinstance(value, dict):
            raise RuntimeError("Goal5802 measurement evidence is not an object")
        return value

    def bind_measurement_execution() -> Any:
        selector = getattr(adapter, "measurement_execution_callable", None)
        execute = selector() if callable(selector) else adapter.execute
        if not callable(execute):
            raise RuntimeError("Goal5802 measurement execution is not callable")
        return execute

    if not local_untimed:
        if isinstance(process_startup_and_admission_ns, bool) \
                or not isinstance(process_startup_and_admission_ns, int) \
                or process_startup_and_admission_ns <= 0:
            raise RuntimeError("formal startup/admission duration absent")
        phases["process_startup_and_admission"] = (
            process_startup_and_admission_ns)
        if isinstance(input_materialization_ns, bool) \
                or not isinstance(input_materialization_ns, int) \
                or input_materialization_ns <= 0:
            raise RuntimeError("formal input-materialization duration absent")
        phases["input_materialization"] = input_materialization_ns
    preload_evidence_extractor = getattr(
        adapter, "constructor_runtime_preload_receipt", None)
    primary_import_contract_extractor = getattr(
        adapter, "primary_timer_import_contract", None)
    constructor_runtime_preload = (
        preload_evidence_extractor()
        if callable(preload_evidence_extractor) else {
            "schema": "rtdl.goal5802.test_double_runtime_preload.v1",
            "status": "NOT_APPLICABLE__UNIT_TEST_DOUBLE",
        })
    if not isinstance(constructor_runtime_preload, dict):
        raise RuntimeError("Goal5802 constructor preload evidence differs")
    primary_import_contract = (
        primary_import_contract_extractor()
        if callable(primary_import_contract_extractor) else None)

    raw_result: Any | None = None
    with _primary_timer_import_boundary(primary_import_contract):
        if local_untimed:
            adapter.load()
            adapter.prepare()
            execute = bind_measurement_execution()
            raw_result = execute()
            retain_lifecycle(raw_result)
        else:
            total_start = clock()
            adapter.load()
            load_end = clock()
            phases["load_or_deploy"] = load_end - total_start
            adapter.prepare()
            prepare_end = clock()
            phases["prepare"] = prepare_end - load_end
            phases["steady_warmups"] = 0
            execute = bind_measurement_execution()
        if not local_untimed and regime == "DEPLOYMENT_COLD":
            phase_start = prepare_end
            raw_result = execute()
            phase_end = clock()
            retain_lifecycle(raw_result)
            phases["complete_execute"] = phase_end - phase_start
            durations.append(phase_end - total_start)
        elif not local_untimed and regime == "PREPARE":
            durations.append(phases["prepare"])
            phase_start = clock()
            raw_result = execute()
            phase_end = clock()
            retain_lifecycle(raw_result)
            phases["complete_execute"] = phase_end - phase_start
        elif not local_untimed:
            warmup_ns = 0
            for _ in range(STEADY_WARMUPS):
                phase_start = clock()
                warmup_result = execute()
                phase_end = clock()
                retain_lifecycle(warmup_result)
                warmup_ns += phase_end - phase_start
                release_start = clock()
                del warmup_result
                release_end = clock()
                if release_end <= release_start:
                    raise RuntimeError(
                        "Goal5802 warmup release duration is nonpositive")
                measurement_evidence_ns += release_end - release_start
            phases["steady_warmups"] = warmup_ns
            for repetition in range(STEADY_REPETITIONS):
                phase_start = clock()
                current_result = execute()
                phase_end = clock()
                retain_lifecycle(current_result)
                durations.append(phase_end - phase_start)
                if repetition + 1 == STEADY_REPETITIONS:
                    raw_result = current_result
                else:
                    release_start = clock()
                    del current_result
                    release_end = clock()
                    if release_end <= release_start:
                        raise RuntimeError(
                            "Goal5802 repetition release duration is nonpositive")
                    measurement_evidence_ns += release_end - release_start
            phases["complete_execute"] = sum(durations)
    if raw_result is None:
        raise RuntimeError("Goal5802 adapter returned no exact result")
    if local_untimed:
        result = finalize(raw_result)
    else:
        evidence_start = clock()
        result = finalize(raw_result)
        evidence_end = clock()
        if evidence_end <= evidence_start:
            raise RuntimeError(
                "Goal5802 final-evidence duration is nonpositive")
        measurement_evidence_ns += evidence_end - evidence_start
        phases["measurement_evidence_materialization"] = measurement_evidence_ns
    close_start = None if local_untimed else clock()
    adapter.close()
    if close_start is not None:
        phases["close"] = clock() - close_start
    if any(value <= 0 for value in durations):
        raise RuntimeError("Goal5802 timer produced a nonpositive duration")
    return {
        "schema": "rtdl.goal5802.python_arm_worker_result.v1",
        "status": "PASS__LOCAL_UNTIMED" if local_untimed else "PASS",
        "regime": "LOCAL_UNTIMED" if local_untimed else regime,
        "execute_or_regime_durations_ns": durations,
        "phase_durations_ns": phases,
        "result": result,
        "execution_lifecycle_receipts": lifecycle_receipts,
        "constructor_runtime_preload_receipt": constructor_runtime_preload,
        "primary_estimator_name": (
            "LOCAL_UNTIMED"
            if local_untimed else
            "WARM_PROCESS_DEPLOYMENT_COLD"
            if regime == "DEPLOYMENT_COLD" else regime),
        "primary_estimator_scope": (
            "LOAD_OR_DEPLOY_PLUS_PREPARE_PLUS_COMPLETE_EXECUTE__EXCLUDES_"
            "PROCESS_STARTUP_ADMISSION_AND_ARM_RUNTIME_MODULE_PRELOAD"
            if regime == "DEPLOYMENT_COLD" and not local_untimed else
            "REGIME_DEFINED_BY_GOAL5802_FREEZE"),
        "new_forbidden_module_load_inside_primary_timer": False,
        "primary_timer_new_module_load_policy":
            PRIMARY_TIMER_NEW_MODULE_LOAD_POLICY,
        "constructor_evidence_inside_primary_timer": False,
        "registered_performance_timing_count": 0 if local_untimed else len(durations),
        "receipt_serialization_inside_timer": False,
        "close_inside_primary_timer": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=(PYOPTIX_ARM, RTDL_ARM), required=True)
    parser.add_argument("--task", choices=(RELATION_TASK, TRIANGLE_TASK), required=True)
    parser.add_argument("--regime", choices=REGIMES, default="STEADY_E2E")
    parser.add_argument("--local-untimed", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--execution-authority", type=Path)
    parser.add_argument("--runtime-manifest", type=Path)
    parser.add_argument("--worker-id")
    parser.add_argument("--ptx", type=Path)
    parser.add_argument("--compaction-cubin", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--authority", type=Path)
    parser.add_argument("--trust-root", type=Path)
    parser.add_argument("--trust-head", type=Path)
    parser.add_argument("--trust-package", type=Path)
    parser.add_argument("--native-library", type=Path)
    parser.add_argument("--deployment-id")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    admission_ns: int | None = None
    controller_start_ns: int | None = None
    if not args.local_untimed:
        if args.freeze is None or args.execution_authority is None \
                or args.runtime_manifest is None or not args.worker_id:
            raise RuntimeError("formal Goal5802 worker lacks frozen authority inputs")
        freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
        authority = json.loads(args.execution_authority.read_text(encoding="utf-8"))
        if not isinstance(freeze, dict) or not isinstance(authority, dict):
            raise RuntimeError("formal Goal5802 authority roots must be objects")
        validate_freeze(freeze, args.root.resolve())
        freeze_file_sha = hashlib.sha256(args.freeze.read_bytes()).hexdigest()
        runtime_manifest = json.loads(
            args.runtime_manifest.read_text(encoding="utf-8"))
        if not isinstance(runtime_manifest, dict):
            raise RuntimeError("Goal5802 runtime manifest root is not an object")
        # Exact file/tree bytes were verified once by the controller and the
        # common all-arm file union was re-read immediately before this
        # process.  Rehashing target paths here would warm Python/RTDL inputs
        # asymmetrically.  The worker validates only the sealed document.
        validate_runtime_manifest_document(runtime_manifest)
        runtime_manifest_sha = hashlib.sha256(
            args.runtime_manifest.read_bytes()).hexdigest()
        validate_execution_authority(
            authority, freeze_sha256=freeze_file_sha,
            runtime_manifest_sha256=runtime_manifest_sha)
        authority_file_sha = hashlib.sha256(
            args.execution_authority.read_bytes()).hexdigest()
        if os.environ.get("GOAL5802_FORMAL_CONTROLLER_PID") != str(os.getppid()) \
                or os.environ.get("GOAL5802_EXECUTION_AUTHORITY_SHA256") \
                != authority_file_sha \
                or os.environ.get("GOAL5802_RUNTIME_MANIFEST_SHA256") \
                != runtime_manifest_sha:
            raise RuntimeError("formal Goal5802 worker was not born under controller")
        matches = [row for row in freeze["schedule"]
                   if row["worker_id"] == args.worker_id]
        if len(matches) != 1 or matches[0]["arm"] != args.arm \
                or matches[0]["task"] != args.task \
                or matches[0]["regime"] != args.regime:
            raise RuntimeError("formal Goal5802 worker/schedule row mismatch")
        # This must precede either arm's runtime preload and every GPU/timer
        # action.  It prevents accidental or direct entry around controller
        # preflight; it is not malicious-owner authentication.
        validate_formal_worker_preflight_gate(
            runtime_manifest_sha256=runtime_manifest_sha)
        consume_formal_worker_live_capability(
            worker_id=args.worker_id,
            runtime_manifest_sha256=runtime_manifest_sha)
        controller_start_text = os.environ.get(
            "GOAL5802_CONTROLLER_ENVELOPE_START_NS")
        if controller_start_text is None or not controller_start_text.isdigit():
            raise RuntimeError("formal Goal5802 controller start clock absent")
        controller_start_ns = int(controller_start_text)
    else:
        freeze = None
        runtime_manifest = None

    # Validate arm arguments and preload the selected Python/runtime graph
    # before closing the controller-to-worker admission phase.  Neither the
    # baseline module nor RTDL's lazy public implementation may first enter
    # the process after ``run_adapter`` starts its primary clock.
    if args.arm == PYOPTIX_ARM:
        if args.ptx is None:
            raise ValueError("PyOptiX worker requires --ptx")
        if args.task == RELATION_TASK and args.compaction_cubin is None:
            raise ValueError("PyOptiX relation requires --compaction-cubin")
        if args.task == TRIANGLE_TASK and args.compaction_cubin is not None:
            raise ValueError("PyOptiX triangle forbids relation-only cubin")
        pyoptix_runtime, runtime_preload_receipt = \
            preload_pyoptix_runtime()
        rtdl_runtime = None
        rtdl_implementation = None
    else:
        for name in (
                "artifact", "authority", "trust_root", "trust_head",
                "trust_package", "native_library", "deployment_id"):
            if getattr(args, name) is None:
                raise ValueError(
                    f"RTDL worker requires --{name.replace('_', '-')}")
        rtdl_runtime, rtdl_implementation, runtime_preload_receipt = \
            preload_rtdl_runtime()
        pyoptix_runtime = None

    if controller_start_ns is not None:
        admission_ns = time.perf_counter_ns() - controller_start_ns
        if admission_ns <= 0:
            raise RuntimeError("formal Goal5802 admission duration invalid")

    input_start = None if args.local_untimed else time.perf_counter_ns()
    workload = (
        relation_workload() if args.task == RELATION_TASK else triangle_workload())
    if args.arm == PYOPTIX_ARM:
        if pyoptix_runtime is None:
            raise RuntimeError("PyOptiX admission runtime is absent")
        adapter = PyOptixScalarAdapter(
            args.task, workload, ptx_path=args.ptx,
            compaction_cubin_path=args.compaction_cubin,
            preloaded_runtime=pyoptix_runtime,
            runtime_preload_receipt=runtime_preload_receipt)
    else:
        if rtdl_runtime is None or rtdl_implementation is None:
            raise RuntimeError("RTDL admission runtime is absent")
        adapter = RTDLExecutableAdapter(
            args.task, workload,
            RTDLDeploymentPaths(
                artifact=args.artifact,
                authority=args.authority,
                trust_root=args.trust_root,
                trust_head=args.trust_head,
                trust_package=args.trust_package,
                native_library=args.native_library,
                deployment_id=args.deployment_id,
            ),
            preloaded_runtime=rtdl_runtime,
            preloaded_implementation=rtdl_implementation,
            runtime_preload_receipt=runtime_preload_receipt,
        )
    input_materialization_ns = (
        None if input_start is None else time.perf_counter_ns() - input_start)
    receipt = run_adapter(
        adapter, args.regime, local_untimed=args.local_untimed,
        input_materialization_ns=input_materialization_ns,
        process_startup_and_admission_ns=admission_ns)
    if runtime_manifest is not None:
        identity_start = time.perf_counter_ns()
        runtime_identity = adapter.runtime_identity()
        files = runtime_manifest["files"]
        if args.arm == PYOPTIX_ARM:
            expected = {
                "distribution_version": runtime_manifest["pyoptix"][
                    "distribution_version"],
                "initializer_path": files["pyoptix_initializer"]["path"],
                "initializer_sha256": files["pyoptix_initializer"]["sha256"],
                "extension_path": files["pyoptix_extension"]["path"],
                "extension_sha256": files["pyoptix_extension"]["sha256"],
                "optix_api_version": runtime_manifest["pyoptix"][
                    "optix_api_version"],
                "matched_ptx_path": files["matched_ptx"]["path"],
                "matched_ptx_sha256": files["matched_ptx"]["sha256"],
                "retained_matched_ptx_sha256": files["matched_ptx"]["sha256"],
            }
            if args.task == RELATION_TASK:
                expected.update({
                    "compaction_cubin_path": files["compaction_cubin"]["path"],
                    "compaction_cubin_sha256": files["compaction_cubin"][
                        "sha256"],
                    "retained_compaction_cubin_sha256": files[
                        "compaction_cubin"]["sha256"],
                })
        else:
            prefix = "relation" if args.task == RELATION_TASK else "triangle"
            expected = {
                "rtdsl_init_path": files["rtdsl_init"]["path"],
                "rtdsl_init_sha256": files["rtdsl_init"]["sha256"],
                "rtdlexe_module_path": files["rtdlexe_module"]["path"],
                "rtdlexe_module_sha256": files["rtdlexe_module"]["sha256"],
                "executed_executable_identity_sha256": freeze[
                    "product_binding"][
                        f"{prefix}_executable_identity_sha256"],
            }
        if runtime_identity != expected:
            raise RuntimeError("loaded Python arm identity differs from runtime manifest")
        identity_ns = time.perf_counter_ns() - identity_start
        if identity_ns <= 0:
            raise RuntimeError("post-execution identity-validation duration invalid")
        receipt["phase_durations_ns"][
            "post_execution_identity_validation"] = identity_ns
        receipt["loaded_runtime_identity"] = runtime_identity
    receipt["arm"] = args.arm
    receipt["task"] = args.task
    receipt["worker_id"] = args.worker_id or "LOCAL_UNTIMED"
    receipt["freeze_file_sha256"] = (
        hashlib.sha256(args.freeze.read_bytes()).hexdigest()
        if args.freeze is not None else None)
    receipt["execution_authority_sha256"] = (
        hashlib.sha256(args.execution_authority.read_bytes()).hexdigest()
        if args.execution_authority is not None else None)
    receipt["runtime_manifest_sha256"] = (
        hashlib.sha256(args.runtime_manifest.read_bytes()).hexdigest()
        if args.runtime_manifest is not None else None)
    encoded = json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
