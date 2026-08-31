#!/usr/bin/env python3
"""Untimed two-family hardware smoke for the public ``.rtdlexe`` lifecycle.

``build`` creates unsigned candidates only.  They must be copied to the
offline signer and explicitly frozen before ``run`` can install/load them.
No clock is read and no performance sample is emitted.
"""

from __future__ import annotations

import argparse
import builtins
import ctypes
import hashlib
import importlib.abc
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_create_only(path: Path, value: object) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2).encode() + b"\n")


def _proof(protocol, proof_path: Path):
    from rtdsl.v4 import AnyHitProtocolProof, standard_protocol_physical_plan
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=_sha_file(proof_path),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _relation_minimum_overlap_f32(value: object) -> float:
    """Return one finite, nonnegative, exactly representable f32 threshold."""

    if isinstance(value, bool):
        raise ValueError("relation minimum overlap must be an exact f32")
    try:
        threshold = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError("relation minimum overlap must be an exact f32") from error
    if not math.isfinite(threshold) or threshold < 0.0:
        raise ValueError(
            "relation minimum overlap must be finite and nonnegative")
    try:
        encoded = struct.pack("<f", threshold)
    except (OverflowError, struct.error) as error:
        raise ValueError(
            "relation minimum overlap must be exactly representable as f32") \
            from error
    if struct.unpack("<f", encoded)[0] != threshold:
        raise ValueError(
            "relation minimum overlap must be exactly representable as f32")
    return threshold


def _protocols(args, bounded_relation_protocol, triangle_reduction_mode,
               triangle_reduction_protocol):
    relation_threshold = _relation_minimum_overlap_f32(
        args.relation_minimum_overlap_f32)
    relation = bounded_relation_protocol(
        capacity=4096, minimum_overlap_f32=relation_threshold)
    triangle = triangle_reduction_protocol(
        triangle_reduction_mode.WEIGHTED_HIT_COUNT)
    return (
        ("relation", f"goal5801/lx1/relation/{args.deployment_generation}",
         relation),
        ("triangle", f"goal5801/lx1/triangle/{args.deployment_generation}",
         triangle),
    )


def build(args) -> None:
    output = args.output.resolve()
    if re.fullmatch(r"v[1-9][0-9]*", args.deployment_generation) is None:
        raise ValueError("deployment generation must match v[1-9][0-9]*")
    from rtdsl.v4 import (
        BoundedRelationProtocol, TriangleReductionMode, TriangleReductionProtocol,
        V4Target, V4Toolchain, compile_protocol_program,
        standard_protocol_physical_plan,
    )
    from rtdsl import RTDLExecutableBuildRoots, build_rtdlexe
    import llvmlite

    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    target = V4Target.from_native(
        args.native, optix_sdk=args.optix_sdk,
        compute_capability=tuple(map(int, args.compute_capability.split("."))))
    toolchain = V4Toolchain.current(
        compute_capability=tuple(map(int, args.compute_capability.split("."))),
        optix_include=args.optix_include, cuda_include=args.cuda_include)
    nvcc = subprocess.run(
        ["nvcc", "--version"], check=True, capture_output=True, text=True).stdout.strip()
    roots = RTDLExecutableBuildRoots(
        llvmlite_version=llvmlite.__version__,
        cuda_toolkit_version=nvcc.splitlines()[-1],
        link_options=("max_trace_depth=1", "debug=none"),
    )
    # Goal5802's matched relation task has 4,096 canonical output rows.  The
    # threshold is deliberately a required build input: it is task semantics,
    # not a launcher default.  The resulting protocol is bound into both the
    # artifact identity and the v2 candidate manifest below.
    protocols = _protocols(
        args, BoundedRelationProtocol, TriangleReductionMode,
        TriangleReductionProtocol)
    candidates = {}
    for label, deployment_id, protocol in protocols:
        program = compile_protocol_program(
            protocol, physical_plan=standard_protocol_physical_plan(protocol),
            any_hit_proof=_proof(protocol, args.proof))
        materialized = program.materialize(target=target, toolchain=toolchain)
        authority = output / f"{label}.authority.json"
        built = build_rtdlexe(
            materialized, artifact_directory=output / "artifacts",
            authority_path=authority, build_roots=roots,
            deployment_id=deployment_id)
        candidates[label] = {
            "deployment_id": deployment_id,
            "artifact_path": str(built.artifact_path),
            "artifact_sha256": built.artifact_sha256,
            "authority_path": str(built.authority_path),
            "authority_sha256": built.authority_sha256,
            "executable_identity_sha256": built.executable_identity_sha256,
        }
    relation_protocol = protocols[0][2]
    manifest = {
        "schema": "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
        "status": "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED",
        "registered_timing_count": 0,
        "native_path": str(args.native.resolve()),
        "native_sha256": _sha_file(args.native),
        "proof_path": str(args.proof.resolve()),
        "proof_sha256": _sha_file(args.proof),
        "relation_protocol": {
            "capacity": relation_protocol.capacity,
            "minimum_overlap_boundary": "inclusive",
            "minimum_overlap_f32": relation_protocol.minimum_overlap_f32,
            "minimum_overlap_f32_bits": struct.unpack(
                "<I", struct.pack(
                    "<f", relation_protocol.minimum_overlap_f32))[0],
        },
        "candidates": candidates,
    }
    _write_create_only(output / "candidate_manifest.json", manifest)
    print(json.dumps(manifest, sort_keys=True))


def _fork_boundary(prepared, batch) -> str:
    read_fd, write_fd = os.pipe()
    child = os.fork()
    if child == 0:
        os.close(read_fd)
        try:
            prepared.execute(batch)
            value = "UNEXPECTED_ACCEPT"
        except Exception as error:  # exact code is preserved below
            value = getattr(error, "code", type(error).__name__)
        os.write(write_fd, value.encode("ascii", errors="replace"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    value = os.read(read_fd, 4096).decode("ascii")
    os.close(read_fd)
    waited, status = os.waitpid(child, 0)
    if waited != child or status != 0:
        raise RuntimeError("process-boundary child failed")
    return value


def run(args) -> None:
    forbidden_prefixes = (
        "numba", "llvmlite", "rtdsl.v4_callback_lifecycle",
    )
    def forbidden_module(name: str) -> bool:
        return name.startswith(forbidden_prefixes) or (
            name.startswith("rtdsl.") and any(
                marker in name for marker in (
                    "_compiler", "_codegen", "_composer", "wrapper_codegen")))
    attempted_imports: list[str] = []
    attempted_processes: list[str] = []
    attempted_libraries: list[str] = []

    class _ForbiddenImportFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if forbidden_module(fullname):
                attempted_imports.append(fullname)
                raise ImportError(f"forbidden compiler import on cache hit: {fullname}")
            return None

    sys.meta_path.insert(0, _ForbiddenImportFinder())
    original_import = builtins.__import__
    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and forbidden_module(name):
            attempted_imports.append(name)
            raise ImportError(f"forbidden compiler import on cache hit: {name}")
        return original_import(name, globals, locals, fromlist, level)
    builtins.__import__ = guarded_import

    def forbidden_process(*values, **kwargs):
        attempted_processes.append(repr(values[0] if values else kwargs))
        raise RuntimeError("compiler/process spawn on cache-hit lifecycle")
    for name in ("Popen", "run", "call", "check_call", "check_output"):
        setattr(subprocess, name, forbidden_process)
    for name in ("system", "popen"):
        setattr(os, name, forbidden_process)
    for name in tuple(item for item in dir(os)
                      if item.startswith("spawn") or item.startswith("exec")):
        setattr(os, name, forbidden_process)

    original_cdll = ctypes.CDLL
    exact_native = str(args.native.resolve())
    exact_native_sha256 = _sha_file(Path(exact_native))
    def exact_private_native_alias(label: str) -> bool:
        candidate = Path(label)
        if os.name != "posix" \
                or re.fullmatch(r"image-[0-9a-f]{64}\.so", candidate.name) is None \
                or candidate.name != f"image-{exact_native_sha256}.so" \
                or re.fullmatch(
                    r"rtdl-native-[0-9]+-[a-z0-9_]{8}",
                    candidate.parent.name) is None:
            return False
        try:
            parent_status = os.lstat(candidate.parent)
            return (
                stat.S_ISDIR(parent_status.st_mode)
                and stat.S_IMODE(parent_status.st_mode) == 0o700
                and candidate.is_symlink()
                and re.fullmatch(
                    r"/proc/self/fd/[0-9]+", os.readlink(candidate)) is not None
                and candidate.is_file()
                and _sha_file(candidate) == exact_native_sha256
            )
        except OSError:
            return False

    def guarded_cdll(name, *values, **kwargs):
        label = str(name)
        lowered = label.lower()
        sealed_native_alias = exact_private_native_alias(label)
        allowed = sealed_native_alias or lowered in {
            "libcuda.so.1", "libcuda.so", "nvcuda.dll", "cuda.dll"}
        if not allowed or "nvrtc" in lowered or "compiler" in lowered:
            attempted_libraries.append(label)
            raise RuntimeError(f"forbidden dynamic library on cache hit: {label}")
        return original_cdll(name, *values, **kwargs)
    ctypes.CDLL = guarded_cdll

    if not args.nvrtc_trap_log.is_file() \
            or args.nvrtc_trap_log.stat().st_size != 0:
        raise RuntimeError("NVRTC trap log must be an existing empty file")

    # This branch intentionally imports the public deployment surface, not the
    # V4 compiler/lifecycle module.
    from rtdsl import (
        BoundedRelationBatch, BoundedRelationStaticInput,
        install_rtdlexe_deployment, load_rtdlexe,
        TriangleReductionBatch, TriangleReductionStaticInput,
    )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    loaded = {}
    for label, row in manifest["candidates"].items():
        deployment = install_rtdlexe_deployment(
            trust_root_path=args.trust_root, trust_head_path=args.trust_head,
            trust_package_path=args.trust_package,
            deployment_id=row["deployment_id"])
        loaded[label] = load_rtdlexe(
            row["artifact_path"], authority_path=row["authority_path"],
            deployment=deployment)
    forbidden_loaded_after_load = sorted(
        name for name in sys.modules if forbidden_module(name))
    if forbidden_loaded_after_load:
        raise RuntimeError(
            f"cache-hit imported compiler graph: {forbidden_loaded_after_load}")

    cuda_driver = ctypes.CDLL("libcuda.so.1")
    cu_init = cuda_driver.cuInit
    cu_init.argtypes = [ctypes.c_uint]
    cu_init.restype = ctypes.c_int
    cu_device_get = cuda_driver.cuDeviceGet
    cu_device_get.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cu_device_get.restype = ctypes.c_int
    cu_ctx_get_current = cuda_driver.cuCtxGetCurrent
    cu_ctx_get_current.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    cu_ctx_get_current.restype = ctypes.c_int
    cu_ctx_set_current = cuda_driver.cuCtxSetCurrent
    cu_ctx_set_current.argtypes = [ctypes.c_void_p]
    cu_ctx_set_current.restype = ctypes.c_int
    cu_ctx_create = getattr(cuda_driver, "cuCtxCreate_v2", None)
    if cu_ctx_create is None:
        cu_ctx_create = cuda_driver.cuCtxCreate
    cu_ctx_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint,
                              ctypes.c_int]
    cu_ctx_create.restype = ctypes.c_int
    cu_ctx_destroy = getattr(cuda_driver, "cuCtxDestroy_v2", None)
    if cu_ctx_destroy is None:
        cu_ctx_destroy = cuda_driver.cuCtxDestroy
    cu_ctx_destroy.argtypes = [ctypes.c_void_p]
    cu_ctx_destroy.restype = ctypes.c_int

    def _cu_check(code: int, operation: str) -> None:
        if int(code) != 0:
            raise RuntimeError(f"{operation} failed with CUresult {int(code)}")

    def _current_cuda_context() -> int:
        value = ctypes.c_void_p()
        _cu_check(cu_ctx_get_current(ctypes.byref(value)), "cuCtxGetCurrent")
        return int(value.value or 0)

    def _set_cuda_context(value: int) -> None:
        _cu_check(cu_ctx_set_current(ctypes.c_void_p(value)), "cuCtxSetCurrent")

    _cu_check(cu_init(0), "cuInit")
    cuda_device = ctypes.c_int()
    _cu_check(cu_device_get(ctypes.byref(cuda_device), 0), "cuDeviceGet")
    _set_cuda_context(0)
    if _current_cuda_context() != 0:
        raise RuntimeError("failed to establish null-context KAT precondition")

    class _ProductStatusSummary(ctypes.Structure):
        _fields_ = [
            ("schema_version", ctypes.c_uint32), ("ok", ctypes.c_uint32),
            ("first_error_claimed", ctypes.c_uint32),
            ("error_code", ctypes.c_uint32),
            ("validated_row_count", ctypes.c_uint64),
            ("required_invocation_mask", ctypes.c_uint32),
            ("terminal_invocation_mask", ctypes.c_uint32),
            ("invalid_row_count", ctypes.c_uint32),
            ("first_invalid_row", ctypes.c_uint64),
            ("role_counters", ctypes.c_uint64 * 7),
            ("success_status_d2h_bytes", ctypes.c_uint64),
        ]

    foreign_context = ctypes.c_void_p()
    _cu_check(cu_ctx_create(ctypes.byref(foreign_context), 0,
                            cuda_device.value), "cuCtxCreate")
    foreign_context_value = int(foreign_context.value or 0)
    if foreign_context_value == 0:
        raise RuntimeError("foreign CUDA context creation returned null")
    context_preservation_events: list[str] = []

    def _under_foreign_context(label: str, operation):
        _set_cuda_context(foreign_context_value)
        if _current_cuda_context() != foreign_context_value:
            raise RuntimeError(f"{label}: foreign-context precondition failed")
        value = operation()
        if _current_cuda_context() != foreign_context_value:
            raise RuntimeError(f"{label}: RTDL did not restore foreign context")
        context_preservation_events.append(label)
        return value

    relation_static = BoundedRelationStaticInput((
        (0.0, 0.0, 2.0, 2.0, 100),
        (3.0, 3.0, 4.0, 4.0, 101),
    ))
    relation_batch = BoundedRelationBatch((
        (1.0, 1.0, 1.5, 1.5, 10),
        (10.0, 10.0, 11.0, 11.0, 11),
    ), expected_rows=((10, 100),))
    relation_prepared = _under_foreign_context(
        "relation.prepare",
        lambda: loaded["relation"].prepare(
            relation_static, native_library_path=args.native))
    relation_owner = relation_prepared._owner

    def _executing_dso_observation(owner, label: str):
        library = owner._library
        if getattr(library, "_rtdl_loaded_library_sha256", None) \
                != exact_native_sha256:
            raise RuntimeError(f"{label}: executing DSO SHA-256 drift")
        if int(getattr(library, "_rtdl_native_image_seals", -1)) != 15:
            raise RuntimeError(f"{label}: executing DSO lacks four memfd seals")
        alias = str(getattr(library, "_rtdl_native_loader_alias", ""))
        alias_path = Path(alias)
        if not alias_path.is_absolute() \
                or alias_path.name != f"image-{exact_native_sha256}.so" \
                or re.fullmatch(
                    r"rtdl-native-[0-9]+-[a-z0-9_]{8}",
                    alias_path.parent.name) is None:
            raise RuntimeError(f"{label}: executing DSO alias is malformed")
        counter = getattr(
            library, "rtdl_optix_v4_runtime_compiler_attempt_count_v1")
        counter.argtypes = []
        counter.restype = ctypes.c_uint64
        return library, counter, {
            "label": label,
            "native_sha256": exact_native_sha256,
            "sealed_image_seals": int(library._rtdl_native_image_seals),
            "loader_alias": alias,
        }

    relation_library, relation_compiler_counter, relation_dso = \
        _executing_dso_observation(relation_owner, "relation")
    relation_compiler_attempts_before = int(relation_compiler_counter())

    # Exercise the reducer on the same sealed DSO that executes the public
    # relation lifecycle.  The direct caller path is never loaded by this
    # cache-hit harness.
    _set_cuda_context(0)
    probe = getattr(
        relation_library,
        "rtdl_optix_v4_goal5801_product_status_device_probe_v1")
    probe.argtypes = [ctypes.c_uint32, ctypes.POINTER(_ProductStatusSummary),
                      ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    probe.restype = ctypes.c_int
    reducer_matrix = []
    for case_id in range(12):
        summary = _ProductStatusSummary()
        error = ctypes.create_string_buffer(4096)
        status = int(probe(case_id, ctypes.byref(summary), error, len(error)))
        if status:
            raise RuntimeError(
                f"compiled reducer probe {case_id} failed: " +
                error.value.decode("utf-8", errors="replace"))
        expected_ok = case_id in (0, 9)
        if bool(summary.ok) != expected_ok \
                or int(summary.schema_version) != 2 \
                or int(summary.success_status_d2h_bytes) != ctypes.sizeof(
                    _ProductStatusSummary):
            raise RuntimeError(
                f"compiled reducer hostile verdict mismatch: {case_id}")
        reducer_matrix.append({
            "case_id": case_id, "ok": bool(summary.ok),
            "invalid_row_count": int(summary.invalid_row_count),
            "error_code": int(summary.error_code),
        })
        if _current_cuda_context() != 0:
            raise RuntimeError(
                f"compiled reducer probe {case_id} did not restore null context")
    _set_cuda_context(foreign_context_value)
    relation_result = _under_foreign_context(
        "relation.execute.initial",
        lambda: relation_prepared.execute(
            relation_batch, include_diagnostics=True))
    relation_repeat = _under_foreign_context(
        "relation.execute.repeat",
        lambda: relation_prepared.execute(
            BoundedRelationBatch(tuple(relation_batch.source_boxes),
                                 expected_rows=((10, 100),)),
            include_diagnostics=True))
    # Stronger-than-natural interruption simulation: native has committed B,
    # while Python is forced back to the previously published A key/arrays.
    # Exact native-digest gating must rebuild A despite equal row counts.
    relation_a_key = relation_owner._last_batch_key
    relation_a_arrays = relation_owner._last_source_arrays
    interrupted_b_batch = BoundedRelationBatch((
        (1.0, 1.0, 1.5, 1.5, 14),
        (10.0, 10.0, 11.0, 11.0, 15),
    ), expected_rows=((14, 100),))
    relation_interrupted_b = _under_foreign_context(
        "relation.execute.interrupt_window_commit_b",
        lambda: relation_prepared.execute(
            interrupted_b_batch, include_diagnostics=True))
    relation_owner._last_batch_key = relation_a_key
    relation_owner._last_source_arrays = relation_a_arrays
    relation_interrupt_recovery = _under_foreign_context(
        "relation.execute.interrupt_window_rebuild_a",
        lambda: relation_prepared.execute(
            BoundedRelationBatch(tuple(relation_batch.source_boxes),
                                 expected_rows=((10, 100),)),
            include_diagnostics=True))
    relation_interrupt_recovery_repeat = _under_foreign_context(
        "relation.execute.interrupt_window_repeat_a",
        lambda: relation_prepared.execute(
            BoundedRelationBatch(tuple(relation_batch.source_boxes),
                                 expected_rows=((10, 100),)),
            include_diagnostics=True))
    relation_changed = _under_foreign_context(
        "relation.execute.changed",
        lambda: relation_prepared.execute(
            BoundedRelationBatch(((1.0, 1.0, 1.5, 1.5, 12),),
                                 expected_rows=((12, 100),)),
            include_diagnostics=True))
    failed_predecessor_batch = BoundedRelationBatch(
        ((1.0, 1.0, 1.5, 1.5, 13),),
        expected_rows=((13, 101),),
    )
    try:
        _under_foreign_context(
            "relation.execute.failed_predecessor",
            lambda: relation_prepared.execute(
                failed_predecessor_batch, include_diagnostics=True))
        failed_predecessor_code = "UNEXPECTED_ACCEPT"
    except Exception as error:
        failed_predecessor_code = getattr(error, "code", type(error).__name__)
    relation_recovered = _under_foreign_context(
        "relation.execute.same_bytes_after_failed_predecessor",
        lambda: relation_prepared.execute(
            BoundedRelationBatch(
                tuple(failed_predecessor_batch.source_boxes),
                expected_rows=((13, 100),),
            ),
            include_diagnostics=True,
        ),
    )
    relation_recovered_repeat = _under_foreign_context(
        "relation.execute.same_bytes_committed_repeat",
        lambda: relation_prepared.execute(
            BoundedRelationBatch(
                tuple(failed_predecessor_batch.source_boxes),
                expected_rows=((13, 100),),
            ),
            include_diagnostics=True,
        ),
    )
    _set_cuda_context(0)
    process_boundary = _fork_boundary(relation_prepared, relation_batch)
    _set_cuda_context(foreign_context_value)
    relation_prepared._owner._active.acquire()
    try:
        try:
            relation_prepared.execute(relation_batch)
            reentrant = "UNEXPECTED_ACCEPT"
        except Exception as error:
            reentrant = getattr(error, "code", type(error).__name__)
    finally:
        relation_prepared._owner._active.release()
    relation_compiler_attempts_after = int(relation_compiler_counter())
    _under_foreign_context("relation.close", relation_prepared.close)
    relation_prepared.close()
    try:
        relation_prepared.execute(relation_batch)
        relation_after_close = "UNEXPECTED_ACCEPT"
    except Exception as error:
        relation_after_close = getattr(error, "code", type(error).__name__)

    triangle_static = TriangleReductionStaticInput(
        vertices=((-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (0.0, 1.0, 1.0)),
        triangles=((0, 1, 2),), event_capacity=1)
    triangle_batch = TriangleReductionBatch(
        queries=(((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),),
        query_weights=(7,), expected_reduced_u64=7)
    triangle_prepared = _under_foreign_context(
        "triangle.prepare",
        lambda: loaded["triangle"].prepare(
            triangle_static, native_library_path=args.native))
    triangle_owner = triangle_prepared._owner
    _triangle_library, triangle_compiler_counter, triangle_dso = \
        _executing_dso_observation(triangle_owner, "triangle")
    triangle_compiler_attempts_before = int(triangle_compiler_counter())
    triangle_result = _under_foreign_context(
        "triangle.execute.initial",
        lambda: triangle_prepared.execute(
            triangle_batch, include_diagnostics=True))
    triangle_repeat = _under_foreign_context(
        "triangle.execute.repeat",
        lambda: triangle_prepared.execute(
            TriangleReductionBatch(tuple(triangle_batch.queries),
                                   query_weights=(7,), expected_reduced_u64=7),
            include_diagnostics=True))
    triangle_a_key = triangle_owner._last_batch_key
    triangle_a_arrays = triangle_owner._last_query_arrays
    triangle_changed = _under_foreign_context(
        "triangle.execute.changed",
        lambda: triangle_prepared.execute(
            TriangleReductionBatch(tuple(triangle_batch.queries),
                                   query_weights=(9,), expected_reduced_u64=9),
            include_diagnostics=True))
    # Reproduce the old publication-window state exactly: native has committed
    # B, while an interrupted Python publication still names A.  Native digest
    # mismatch must force a fresh A upload; a same-count B reuse is forbidden.
    triangle_owner._last_batch_key = triangle_a_key
    triangle_owner._last_query_arrays = triangle_a_arrays
    triangle_interrupt_recovery = _under_foreign_context(
        "triangle.execute.interrupt_window_rebuild_a",
        lambda: triangle_prepared.execute(
            TriangleReductionBatch(tuple(triangle_batch.queries),
                                   query_weights=(7,), expected_reduced_u64=7),
            include_diagnostics=True))
    triangle_interrupt_recovery_repeat = _under_foreign_context(
        "triangle.execute.interrupt_window_repeat_a",
        lambda: triangle_prepared.execute(
            TriangleReductionBatch(tuple(triangle_batch.queries),
                                   query_weights=(7,), expected_reduced_u64=7),
            include_diagnostics=True))
    try:
        _under_foreign_context(
            "triangle.execute.oracle_mismatch",
            lambda: triangle_prepared.execute(
                TriangleReductionBatch(
                    tuple(triangle_batch.queries), query_weights=(9,),
                    expected_reduced_u64=8),
                include_diagnostics=True))
        triangle_oracle_failure = "UNEXPECTED_ACCEPT"
    except Exception as error:
        triangle_oracle_failure = getattr(error, "code", type(error).__name__)
    triangle_recovered = _under_foreign_context(
        "triangle.execute.same_bytes_after_oracle_mismatch",
        lambda: triangle_prepared.execute(
            TriangleReductionBatch(
                tuple(triangle_batch.queries), query_weights=(9,),
                expected_reduced_u64=9),
            include_diagnostics=True))
    triangle_compiler_attempts_after = int(triangle_compiler_counter())
    _under_foreign_context("triangle.close", triangle_prepared.close)
    triangle_prepared.close()
    try:
        triangle_prepared.execute(triangle_batch)
        triangle_after_close = "UNEXPECTED_ACCEPT"
    except Exception as error:
        triangle_after_close = getattr(error, "code", type(error).__name__)
    _set_cuda_context(0)
    _cu_check(cu_ctx_destroy(ctypes.c_void_p(foreign_context_value)),
              "cuCtxDestroy")
    if _current_cuda_context() != 0:
        raise RuntimeError("foreign CUDA context cleanup did not restore null")

    if relation_result.output != ((10, 100),) \
            or relation_repeat.output != relation_result.output \
            or relation_interrupted_b.output != ((14, 100),) \
            or relation_interrupt_recovery.output != relation_result.output \
            or relation_interrupt_recovery_repeat.output != relation_result.output \
            or relation_changed.output != ((12, 100),) \
            or relation_recovered.output != ((13, 100),) \
            or relation_recovered_repeat.output != relation_recovered.output \
            or triangle_result.output != 7 \
            or triangle_repeat.output != triangle_result.output \
            or triangle_changed.output != 9 \
            or triangle_interrupt_recovery.output != 7 \
            or triangle_interrupt_recovery_repeat.output != 7 \
            or triangle_recovered.output != 9:
        raise RuntimeError("exact oracle mismatch")
    if relation_result.device_status["prepared_input_reused"] \
            or not relation_repeat.device_status["prepared_input_reused"] \
            or relation_interrupted_b.device_status["prepared_input_reused"] \
            or relation_interrupt_recovery.device_status["prepared_input_reused"] \
            or not relation_interrupt_recovery_repeat.device_status[
                "prepared_input_reused"] \
            or relation_changed.device_status["prepared_input_reused"] \
            or relation_recovered.device_status["prepared_input_reused"] \
            or not relation_recovered_repeat.device_status["prepared_input_reused"] \
            or triangle_result.device_status["prepared_input_reused"] \
            or not triangle_repeat.device_status["prepared_input_reused"] \
            or triangle_changed.device_status["prepared_input_reused"] \
            or triangle_interrupt_recovery.device_status[
                "prepared_input_reused"] \
            or not triangle_interrupt_recovery_repeat.device_status[
                "prepared_input_reused"] \
            or triangle_recovered.device_status["prepared_input_reused"]:
        raise RuntimeError("exact normalized prepared-input reuse contract failed")
    relation_reuse_sequence = (
        (relation_result, 1),
        (relation_repeat, 0),
        (relation_interrupted_b, 1),
        (relation_interrupt_recovery, 1),
        (relation_interrupt_recovery_repeat, 0),
        (relation_changed, 1),
        (relation_recovered, 1),
        (relation_recovered_repeat, 0),
    )
    for observed, expected_delta in relation_reuse_sequence:
        if observed.device_status["native_source_build_count_delta"] != expected_delta:
            raise RuntimeError("native source-cache build delta mismatch")
    if failed_predecessor_code != "RX043_ORACLE_MISMATCH":
        raise RuntimeError(
            "failed-predecessor hostile did not fail at the oracle: "
            + failed_predecessor_code)
    if triangle_oracle_failure != "RX043_ORACLE_MISMATCH":
        raise RuntimeError(
            "triangle in-API oracle hostile did not fail closed: "
            + triangle_oracle_failure)
    if process_boundary != "RX038_PROCESS_BOUNDARY" \
            or reentrant != "RX040_REENTRANT" \
            or relation_after_close != "RX037_USE_AFTER_CLOSE" \
            or triangle_after_close != "RX037_USE_AFTER_CLOSE":
        raise RuntimeError("lifecycle hostile did not fail closed")
    forbidden_loaded_after_close = sorted(
        name for name in sys.modules if forbidden_module(name))
    compiler_attempts_before = (
        relation_compiler_attempts_before + triangle_compiler_attempts_before)
    compiler_attempts_after = (
        relation_compiler_attempts_after + triangle_compiler_attempts_after)
    nvrtc_trap_bytes = args.nvrtc_trap_log.read_bytes()
    if forbidden_loaded_after_close or attempted_imports or attempted_processes \
            or attempted_libraries or compiler_attempts_after != compiler_attempts_before \
            or nvrtc_trap_bytes:
        raise RuntimeError("cache-hit lifecycle reached compiler/codegen path: " +
                           repr({"modules": forbidden_loaded_after_close,
                                 "imports": attempted_imports,
                                 "processes": attempted_processes,
                                 "libraries": attempted_libraries,
                                 "compiler_attempts_before": compiler_attempts_before,
                                 "compiler_attempts_after": compiler_attempts_after,
                                 "nvrtc_trap": nvrtc_trap_bytes.decode(
                                     "ascii", errors="replace")}))
    result = {
        "schema": "rtdl.goal5801.lx1_untimed_functional_result.v1",
        "status": "PASS__TWO_FAMILY_PUBLIC_RTDLEXE_LIFECYCLES",
        "registered_timing_count": 0,
        "performance_claim_authorized": False,
        "rt_core_claim_authorized": False,
        "cache_hit_forbidden_imports_after_load": forbidden_loaded_after_load,
        "cache_hit_forbidden_imports_after_close": forbidden_loaded_after_close,
        "cache_hit_attempted_imports": attempted_imports,
        "cache_hit_attempted_processes": attempted_processes,
        "cache_hit_attempted_libraries": attempted_libraries,
        "native_compiler_attempts_before": compiler_attempts_before,
        "native_compiler_attempts_after": compiler_attempts_after,
        "native_compiler_attempts_by_executing_dso": {
            "relation": {
                **relation_dso,
                "before": relation_compiler_attempts_before,
                "after": relation_compiler_attempts_after,
            },
            "triangle": {
                **triangle_dso,
                "before": triangle_compiler_attempts_before,
                "after": triangle_compiler_attempts_after,
            },
        },
        "nvrtc_preload_trap_bytes": len(nvrtc_trap_bytes),
        "cuda_context_preservation": {
            "null_reducer_probe_cases": len(reducer_matrix),
            "null_preserved_after_all_reducer_probes": True,
            "foreign_boundary_events": context_preservation_events,
            "foreign_boundary_event_count": len(context_preservation_events),
            "foreign_preserved_after_every_boundary": True,
            "final_context_is_null": True,
        },
        "compiled_product_status_reducer_matrix": reducer_matrix,
        "relation": {
            "output": [list(row) for row in relation_result.output],
            "output_sha256": relation_result.output_sha256,
            "device_status": dict(relation_result.device_status),
            "role_counters": list(relation_result.role_counters),
            "repeat_device_status": dict(relation_repeat.device_status),
            "interrupted_publication_hostile": {
                "simulated_native_committed_batch": "B",
                "simulated_python_visible_batch": "A",
                "equal_source_count": True,
                "different_device_input_bytes": True,
                "committed_b_output": [
                    list(row) for row in relation_interrupted_b.output],
                "recovered_a_output": [
                    list(row) for row in relation_interrupt_recovery.output],
                "recovered_a_device_status": dict(
                    relation_interrupt_recovery.device_status),
                "recovered_a_repeat_device_status": dict(
                    relation_interrupt_recovery_repeat.device_status),
                "required_recovery_build_delta": 1,
                "required_repeat_build_delta": 0,
            },
            "changed_device_status": dict(relation_changed.device_status),
            "failed_predecessor_hostile": {
                "failure_code": failed_predecessor_code,
                "same_bytes_recovery_output": [
                    list(row) for row in relation_recovered.output],
                "same_bytes_recovery_device_status": dict(
                    relation_recovered.device_status),
                "committed_repeat_device_status": dict(
                    relation_recovered_repeat.device_status),
                "required_recovery_build_delta": 1,
                "required_committed_repeat_build_delta": 0,
            },
            "traversal_receipt": relation_result.traversal_receipt,
            "process_boundary": process_boundary, "reentrant": reentrant,
            "use_after_close": relation_after_close,
        },
        "triangle": {
            "output": triangle_result.output,
            "output_sha256": triangle_result.output_sha256,
            "device_status": dict(triangle_result.device_status),
            "role_counters": list(triangle_result.role_counters),
            "repeat_device_status": dict(triangle_repeat.device_status),
            "changed_device_status": dict(triangle_changed.device_status),
            "interrupted_publication_hostile": {
                "simulated_native_committed_batch": "B_weight_9",
                "simulated_python_visible_batch": "A_weight_7",
                "equal_query_count": True,
                "different_device_input_bytes": True,
                "committed_b_output": triangle_changed.output,
                "recovered_a_output": triangle_interrupt_recovery.output,
                "recovered_a_device_status": dict(
                    triangle_interrupt_recovery.device_status),
                "recovered_a_repeat_device_status": dict(
                    triangle_interrupt_recovery_repeat.device_status),
                "required_recovery_reused": False,
                "required_repeat_reused": True,
            },
            "oracle_hostile": {
                "failure_code": triangle_oracle_failure,
                "same_bytes_recovery_output": triangle_recovered.output,
                "same_bytes_recovery_device_status": dict(
                    triangle_recovered.device_status),
            },
            "traversal_receipt": triangle_result.traversal_receipt,
            "use_after_close": triangle_after_close,
        },
    }
    _write_create_only(args.output, result)
    print(json.dumps(result, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    builder = sub.add_parser("build")
    builder.add_argument("--native", type=Path, required=True)
    builder.add_argument("--optix-include", type=Path, required=True)
    builder.add_argument("--cuda-include", type=Path, required=True)
    builder.add_argument("--optix-sdk", required=True)
    builder.add_argument("--compute-capability", required=True)
    builder.add_argument("--deployment-generation", required=True)
    builder.add_argument(
        "--relation-minimum-overlap-f32",
        required=True,
        type=_relation_minimum_overlap_f32,
    )
    builder.add_argument("--proof", type=Path, required=True)
    builder.add_argument("--output", type=Path, required=True)
    runner = sub.add_parser("run")
    runner.add_argument("--manifest", type=Path, required=True)
    runner.add_argument("--trust-root", type=Path, required=True)
    runner.add_argument("--trust-head", type=Path, required=True)
    runner.add_argument("--trust-package", type=Path, required=True)
    runner.add_argument("--native", type=Path, required=True)
    runner.add_argument("--nvrtc-trap-log", type=Path, required=True)
    runner.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args) if args.command == "build" else run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
