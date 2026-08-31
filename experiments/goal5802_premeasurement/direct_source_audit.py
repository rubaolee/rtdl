"""Independent static guard for the Goal5802 Direct operation call core.

The formal specialization executes no trace mutation.  The untimed observed
specialization instantiates the exact same templated call core and records its
CUDA/OptiX call counts.  This guard closes an added raw-API bypass.
It is deliberately exact-source and fail-closed, not a general C++ parser.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


class DirectSourceAuditError(RuntimeError):
    pass


def _code_only(text: str) -> str:
    """Mask C/C++ comments and quoted literals while preserving positions."""

    output = list(text)
    index = 0
    state = "CODE"
    while index < len(text):
        current = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "CODE":
            if current == "/" and following == "/":
                output[index] = output[index + 1] = " "
                state = "LINE_COMMENT"
                index += 2
                continue
            if current == "/" and following == "*":
                output[index] = output[index + 1] = " "
                state = "BLOCK_COMMENT"
                index += 2
                continue
            if current == '"':
                output[index] = " "
                state = "STRING"
            elif current == "'":
                output[index] = " "
                state = "CHAR"
        elif state == "LINE_COMMENT":
            if current == "\n":
                state = "CODE"
            else:
                output[index] = " "
        elif state == "BLOCK_COMMENT":
            if current == "*" and following == "/":
                output[index] = output[index + 1] = " "
                state = "CODE"
                index += 2
                continue
            if current != "\n":
                output[index] = " "
        else:
            output[index] = " "
            if current == "\\" and following:
                if following != "\n":
                    output[index + 1] = " "
                index += 2
                continue
            if (state == "STRING" and current == '"') \
                    or (state == "CHAR" and current == "'"):
                state = "CODE"
        index += 1
    if state in {"BLOCK_COMMENT", "STRING", "CHAR"}:
        raise DirectSourceAuditError(f"unterminated C++ lexical state: {state}")
    return "".join(output)


def _call_count(code: str, name: str) -> int:
    return len(re.findall(
        rf"\b{re.escape(name)}\s*(?:<[^()<>]+>)?\s*\(", code))


def _function_body(code: str, name: str) -> str:
    """Return the unique balanced function body for an exact-source guard."""

    matches = list(re.finditer(
        rf"\b{re.escape(name)}\s*\([^)]*\)\s*\{{", code))
    if len(matches) != 1:
        raise DirectSourceAuditError(
            f"Direct wrapper definition count differs: {name}={len(matches)}")
    opening = matches[0].end() - 1
    depth = 0
    for index in range(opening, len(code)):
        if code[index] == "{":
            depth += 1
        elif code[index] == "}":
            depth -= 1
            if depth == 0:
                return code[opening + 1:index]
    raise DirectSourceAuditError(f"Direct wrapper body is unbalanced: {name}")


def audit_direct_source(path: Path) -> dict[str, object]:
    path = path.resolve(strict=True)
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    code = _code_only(text)
    expected_calls = {
        # One raw occurrence is allowed only inside each tracing wrapper.
        "cuMemcpyHtoDAsync": 2,
        "cuMemcpyDtoHAsync": 1,
        "cuMemcpyDtoDAsync": 1,
        "cuStreamSynchronize": 1,
        "cuLaunchKernel": 1,
        "optixLaunch": 1,
        # Dynamic-input setup has its own exact wrappers/receipts.  Relation
        # GAS retains the build temporary so this call remains stream-ordered
        # without a hidden setup synchronization.
        "cuMemcpyHtoD": 0,
        "optixAccelBuild": 1,
        "optixDeviceContextSetCacheEnabled": 1,
        # One implementation, one identity reuse wrapper, one fixed-vector KAT
        # call, retained PTX/cubin identities, loaded NVRTC, and the untimed
        # K+1 packed-input identity.
        "sha256_bytes": 7,
        "cuMemsetD8Async": 7,
        # Synchronous/bypass APIs and imported Goal5796 execute helpers are
        # forbidden from the Goal5802-owned source.
        "cuMemcpyDtoH": 0,
        "cuCtxSynchronize": 0,
        "cuEventSynchronize": 0,
        "download_vector": 0,
        "launch": 0,
        "run_relation": 0,
        "run_triangle": 0,
        # Definition plus every templated call site. Both formal<false> and
        # observed<true> specialize these exact same sites.
        "traced_h2d": 2,
        "traced_d2h": 5,
        "traced_sync": 5,
        "traced_launch": 2,
        "enqueue_launch": 3,
        "upload_dynamic_async": 5,
        "build_dynamic_custom_accel": 2,
    }
    observed_calls = {
        name: _call_count(code, name) for name in expected_calls}
    if observed_calls != expected_calls:
        raise DirectSourceAuditError({
            "direct_operation_call_shape_drift": observed_calls,
            "expected": expected_calls,
        })
    # Whole-file counts alone are insufficient: moving the sole launch or
    # synchronization outside its observed/formal shared wrapper preserves the
    # count while breaking the untimed-observer authority.  Pin every raw
    # execute/setup API to the unique helper body that the shared template core
    # calls.  The exact source SHA below then binds these bodies to the formal
    # executable build receipt.
    expected_wrapper_raw_calls = {
        "upload_dynamic_async": {"cuMemcpyHtoDAsync": 1},
        "build_dynamic_custom_accel": {"optixAccelBuild": 1},
        "traced_h2d": {"cuMemcpyHtoDAsync": 1},
        "traced_d2h": {"cuMemcpyDtoHAsync": 1},
        "traced_d2d": {"cuMemcpyDtoDAsync": 1},
        "traced_sync": {"cuStreamSynchronize": 1},
        "traced_launch": {"optixLaunch": 1},
        "enqueue_relation_compaction": {"cuLaunchKernel": 1},
    }
    observed_wrapper_raw_calls: dict[str, dict[str, int]] = {}
    for wrapper, expected in expected_wrapper_raw_calls.items():
        body = _function_body(code, wrapper)
        observed = {name: _call_count(body, name) for name in expected}
        if observed != expected:
            raise DirectSourceAuditError({
                "direct_wrapper_raw_call_shape_drift": wrapper,
                "observed": observed,
                "expected": expected,
            })
        observed_wrapper_raw_calls[wrapper] = observed
    nvrtc_identity_body = _function_body(code, "loaded_nvrtc_identity")
    expected_nvrtc_identity_calls = {
        "nvrtcVersion": 1,
        "dladdr": 1,
        "realpath": 1,
        "lstat": 2,
        "open": 1,
        "fstat": 2,
        "read": 2,
        "sha256_bytes": 1,
    }
    observed_nvrtc_identity_calls = {
        name: _call_count(nvrtc_identity_body, name)
        for name in expected_nvrtc_identity_calls
    }
    if observed_nvrtc_identity_calls != expected_nvrtc_identity_calls:
        raise DirectSourceAuditError({
            "direct_loaded_nvrtc_identity_call_shape_drift":
                observed_nvrtc_identity_calls,
            "expected": expected_nvrtc_identity_calls,
        })
    required_nvrtc_identity_text = (
        "NVRTC_CHECK(nvrtcVersion(&result.version_major, &result.version_minor));",
        "reinterpret_cast<std::uintptr_t>(&nvrtcVersion)",
        "::dladdr(symbol_address, &info)",
        "::realpath(info.dli_fname, nullptr)",
        "S_ISLNK(path_before.st_mode)",
        "!S_ISREG(path_before.st_mode)",
        "O_RDONLY | O_CLOEXEC | O_NOFOLLOW",
        "opened_before.st_dev != path_before.st_dev",
        "opened_before.st_ino != path_before.st_ino",
        "path_after.st_dev != opened_before.st_dev",
        "path_after.st_ino != opened_before.st_ino",
        "result.sha256 = sha256_bytes(exact_bytes);",
    )
    missing_nvrtc_identity = [
        literal for literal in required_nvrtc_identity_text
        if literal not in nvrtc_identity_body
    ]
    if missing_nvrtc_identity:
        raise DirectSourceAuditError({
            "direct_loaded_nvrtc_identity_guard_absent":
                missing_nvrtc_identity})
    forbidden_nvrtc_identity_text = (
        "argv", "std::getenv", "std::cin", "--nvrtc-path",
        "reported_library_path",
    )
    present_forbidden_nvrtc_identity = [
        literal for literal in forbidden_nvrtc_identity_text
        if literal in nvrtc_identity_body
    ]
    if present_forbidden_nvrtc_identity:
        raise DirectSourceAuditError({
            "direct_loaded_nvrtc_identity_accepts_self_reported_input":
                present_forbidden_nvrtc_identity})

    identity_hash_body = _function_body(code, "identity_sha256_bytes")
    if _call_count(identity_hash_body, "sha256_bytes") != 1 \
            or "return sha256_bytes(input);" not in identity_hash_body:
        raise DirectSourceAuditError(
            "Direct identity SHA-256 does not reuse the retained implementation")

    compile_kat_body = _function_body(code, "run_minimal_nvrtc_compile_kat")
    expected_compile_kat_calls = {
        "nvrtcCreateProgram": 1,
        "nvrtcCompileProgram": 1,
        "nvrtcGetProgramLogSize": 1,
        "nvrtcGetProgramLog": 1,
        "nvrtcGetPTXSize": 1,
        "nvrtcGetPTX": 1,
        "nvrtcDestroyProgram": 4,
        "identity_sha256_bytes": 2,
        "cuInit": 0,
        "cuLaunchKernel": 0,
        "optixLaunch": 0,
    }
    observed_compile_kat_calls = {
        name: _call_count(compile_kat_body, name)
        for name in expected_compile_kat_calls
    }
    if observed_compile_kat_calls != expected_compile_kat_calls:
        raise DirectSourceAuditError({
            "direct_nvrtc_compile_kat_call_shape_drift":
                observed_compile_kat_calls,
            "expected": expected_compile_kat_calls,
        })
    required_compile_kat_text = (
        '"extern \\"C\\" __global__ void '
        'goal5802_nvrtc_identity_probe() {}\\n"',
        'result.compile_options = {"--std=c++11"};',
        "if (create_result != NVRTC_SUCCESS || program == nullptr)",
        "nvrtcCompileProgram(program, 1, options);",
        "if (compile_result != NVRTC_SUCCESS)",
        "nvrtcGetPTXSize(program, &product_size);",
        "if (size_result != NVRTC_SUCCESS || product_size == 0)",
        "nvrtcGetPTX(program, product.data());",
        "if (product_result != NVRTC_SUCCESS)",
        "if (destroy_result != NVRTC_SUCCESS || program != nullptr)",
        'result.compile_success = true;',
        'result.program_destroyed = true;',
        'result.product_bytes = static_cast<std::uint64_t>(product.size());',
        'result.product_sha256 = identity_sha256_bytes(product);',
    )
    missing_compile_kat = [
        literal for literal in required_compile_kat_text
        if literal not in text
    ]
    if missing_compile_kat or "Clock::now" in compile_kat_body:
        raise DirectSourceAuditError({
            "direct_nvrtc_compile_kat_guard_absent": missing_compile_kat,
            "clock_read_present": "Clock::now" in compile_kat_body,
        })

    regular_file_body = _function_body(code, "loaded_regular_file_identity")
    expected_regular_file_calls = {
        "realpath": 1,
        "lstat": 2,
        "open": 1,
        "fstat": 2,
        "read": 2,
        "identity_sha256_bytes": 1,
    }
    observed_regular_file_calls = {
        name: _call_count(regular_file_body, name)
        for name in expected_regular_file_calls
    }
    if observed_regular_file_calls != expected_regular_file_calls:
        raise DirectSourceAuditError({
            "direct_builtins_regular_file_call_shape_drift":
                observed_regular_file_calls,
            "expected": expected_regular_file_calls,
        })
    required_regular_file_text = (
        "canonical_path != resolved.get()",
        "S_ISLNK(path_before.st_mode)",
        "!S_ISREG(path_before.st_mode)",
        "O_RDONLY | O_CLOEXEC | O_NOFOLLOW",
        "opened_before.st_dev != path_before.st_dev",
        "opened_before.st_ino != path_before.st_ino",
        "path_after.st_dev != opened_before.st_dev",
        "path_after.st_ino != opened_before.st_ino",
        "result.sha256 = identity_sha256_bytes(exact_bytes);",
    )
    missing_regular_file = [
        literal for literal in required_regular_file_text
        if literal not in regular_file_body
    ]
    if missing_regular_file:
        raise DirectSourceAuditError({
            "direct_builtins_regular_file_guard_absent":
                missing_regular_file})

    builtins_maps_body = _function_body(
        code, "loaded_nvrtc_builtins_identity_from_proc_maps")
    expected_builtins_maps_calls = {
        "getline": 1,
        "realpath": 1,
        "sort": 1,
        "unique": 1,
        "loaded_regular_file_identity": 1,
    }
    observed_builtins_maps_calls = {
        name: _call_count(builtins_maps_body, name)
        for name in expected_builtins_maps_calls
    }
    if observed_builtins_maps_calls != expected_builtins_maps_calls:
        raise DirectSourceAuditError({
            "direct_builtins_maps_call_shape_drift":
                observed_builtins_maps_calls,
            "expected": expected_builtins_maps_calls,
        })
    required_builtins_maps_text = (
        'std::ifstream maps("/proc/self/maps", std::ios::binary);',
        "if (deleted) mapped_path.resize(mapped_path.size() - 10);",
        "if (!is_nvrtc_builtins_basename(mapped_path)) continue;",
        '" (deleted)"',
        "is_nvrtc_builtins_basename(canonical.get())",
        "std::sort(candidates.begin(), candidates.end());",
        "std::unique(candidates.begin(), candidates.end())",
        "if (candidates.size() != 1)",
        'candidates.front(), "loaded NVRTC builtins"',
    )
    missing_builtins_maps = [
        literal for literal in required_builtins_maps_text
        if literal not in text
    ]
    if missing_builtins_maps:
        raise DirectSourceAuditError({
            "direct_builtins_maps_guard_absent": missing_builtins_maps})

    main_body = _function_body(code, "main")
    identity_sequence = (
        "run_minimal_nvrtc_compile_kat",
        "loaded_nvrtc_identity",
        "loaded_nvrtc_builtins_identity_from_proc_maps",
    )
    identity_positions = [main_body.find(name) for name in identity_sequence]
    if any(position < 0 for position in identity_positions) \
            or identity_positions != sorted(identity_positions) \
            or any(_call_count(main_body, name) != 1
                   for name in identity_sequence):
        raise DirectSourceAuditError({
            "direct_identity_compile_then_discovery_order_drift":
                dict(zip(identity_sequence, identity_positions))})
    required_code_patterns = (
        r"for\s*\(\s*unsigned\s+reverse\s*=\s*0\s*;\s*reverse\s*<\s*2\s*;",
        r"kRelationRawCapacity\s*=\s*2\s*\*\s*kRelationSize",
        r"params\.minimum_overlap\s*=\s*minimum_overlap\s*;",
        (r"std::move\s*\(\s*boxes\s*\)\s*,\s*"
         r"std::move\s*\(\s*source_boxes\s*\)\s*,\s*"
         r"kRelationMinimumOverlap\s*\)"),
        (r"relation_k_plus_one_indexed\s*\(\s*\)\s*,\s*"
         r"relation_k_plus_one_sources\s*\(\s*\)\s*,\s*"
         r"kRelationMinimumOverlap\s*\)"),
        (r"box\s*\(\s*0\.0f\s*,\s*0\.0f\s*,\s*4\.0f\s*,\s*"
         r"4\.0f\s*,\s*std::numeric_limits<std::uint32_t>::max\s*"
         r"\(\s*\)\s*\)"),
        (r"box\s*\(\s*0\.125f\s*,\s*2\.0f\s*,\s*1\.125f\s*,\s*"
         r"3\.0f\s*,\s*id\s*\)"),
        (r"box\s*\(\s*0\.125f\s*,\s*2\.0f\s*,\s*0\.625f\s*,\s*"
         r"3\.0f\s*,\s*kRelationSize\s*\+\s*1\s*\)"),
        r"append_f32_le\s*\(\s*output\s*,\s*kRelationMinimumOverlap\s*\)",
        r"append_u32_le\s*\(\s*output\s*,\s*kRelationSize\s*\)",
        r"append_u32_le\s*\(\s*output\s*,\s*kRelationRawCapacity\s*\)",
        r"trace\.async_d2h_bytes\s*!=\s*32784",
        r"trace\.compaction_launch_count\s*!=\s*1",
        r"trace\.async_d2h_bytes\s*!=\s*12",
        r"trace\.host_blocking_boundary_count\s*!=\s*2",
        r"optixDeviceContextSetCacheEnabled\s*\(\s*context->optix\s*,\s*0\s*\)",
        r"validationMode\s*=\s*OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_OFF",
        r"retained_ptx_sha256\s*=\s*sha256_bytes\s*\(\s*ptx\s*\)",
        (r"retained_compaction_cubin_sha256\s*=\s*relation\s*\?\s*"
         r"sha256_bytes\s*\(\s*compaction_cubin\s*\)"),
        (r"compaction_cubin\s*=\s*relation\s*\?\s*"
         r"read_file\s*\(\s*args\.compaction_cubin\s*\)\s*:\s*"
         r"std::string\s*\{\s*\}"),
        r"relation_output\s*=\s*RelationOutput\s*\{\s*\}\s*;",
        r"measurement_evidence_ns\s*\+=\s*elapsed_ns",
    )
    for pattern in required_code_patterns:
        if not re.search(pattern, code):
            raise DirectSourceAuditError(
                f"Direct operation guard absent: {pattern}")
    critical_parameter_assignments = {
        field: len(re.findall(
            rf"\bparams\.{field}\s*=", code))
        for field in (
            "minimum_overlap", "raw_row_capacity",
            "reverse_orientation", "reserved0")
    }
    if any(count != 1 for count in critical_parameter_assignments.values()):
        raise DirectSourceAuditError({
            "Direct critical relation parameter assignment count differs":
                critical_parameter_assignments})
    if "OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_ALL" in code:
        raise DirectSourceAuditError(
            "Direct comparative source enables diagnostic validation ALL")
    if "logCallbackFunction" in code or "logCallbackLevel" in code:
        raise DirectSourceAuditError(
            "Direct comparative source enables an OptiX log callback")
    required_text = (
        'RelationOutput execute() { return execute_core<false>(); }',
        'ObservedRelationOutput execute_observed() { return execute_core<true>(); }',
        'TriangleOutput execute() { return execute_core<false>(); }',
        'ObservedTriangleOutput execute_observed() { return execute_core<true>(); }',
        'if constexpr (Observe)',
        '<< row.dynamic_device_upload_call_count',
        '<< row.dynamic_accel_build_count',
        '<< row.dynamic_explicit_sync_count',
        '<< row.dynamic_blocking_upload_call_count',
        '<< retained_ptx_sha256',
        '<< retained_compaction_cubin_sha256',
        '\\"semantic_compaction_launch_count\\":',
        '\\"total_auxiliary_cuda_kernel_launch_count\\":1',
        '\\"total_auxiliary_cuda_kernel_launch_count\\":0',
        ',\\"measurement_evidence_materialization\\":',
        '\\"optix_log_callback_mode\\":\\"OFF\\"',
        '\\"module_optimization_level\\":\\"DEFAULT\\"',
        '\\"module_debug_level\\":\\"NONE\\"',
        '\\"executed_parameter_projection\\":{',
        'std::string(argv[1]) == "--local-nvrtc-identity"',
        'const MinimalNvrtcCompileKat compile_kat =',
        'run_minimal_nvrtc_compile_kat();',
        'const LoadedNvrtcIdentity identity = loaded_nvrtc_identity();',
        'loaded_nvrtc_builtins_identity_from_proc_maps();',
        '\\"schema\\":\\"rtdl.goal5802.direct_loaded_nvrtc_identity.v2\\"',
        '<< json_escape(identity.resolved_path)',
        '<< json_escape(builtins.resolved_path)',
        '<< identity.version_major',
        '<< identity.version_minor',
        '\\"nvrtc_compile_kat\\":{\\"source_utf8\\":\\"',
        '<< json_escape(compile_kat.source_utf8)',
        '<< compile_kat.product_sha256',
        '\\"clock_read_count\\":0',
        '\\"registered_performance_timing_count\\":0',
        '\\"gpu_kernel_launch_count\\":0',
        '\\"formal_worker_count\\":0',
    )
    missing = [literal for literal in required_text if literal not in text]
    if missing:
        raise DirectSourceAuditError(
            f"Direct JSON ledger is not derived from observed trace: {missing}")
    return {
        "schema": "rtdl.goal5802.direct_source_operation_audit.v2",
        "status": (
            "PASS__FORMAL_TRACE_FREE__UNTIMED_OBSERVER_SAME_TEMPLATE_CORE"),
        "scope": (
            "Goal5802-owned execute call graph; included Goal5796 preparation "
            "helpers remain outside this execute trace and are phase-reported"),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "wrapper_raw_call_shape": observed_wrapper_raw_calls,
        "loaded_nvrtc_identity_guard": {
            "provenance": (
                "MINIMAL_NVRTC_COMPILE_THEN_NVRTCVERSION_SYMBOL_TO_DLADDR_"
                "AND_PROC_SELF_MAPS_UNIQUE_BUILTINS_TO_REALPATH_TO_"
                "NOFOLLOW_REGULAR_FILE_EXACT_BYTES"),
            "accepts_caller_reported_path": False,
            "call_shape": observed_nvrtc_identity_calls,
            "compile_kat_call_shape": observed_compile_kat_calls,
            "builtins_maps_call_shape": observed_builtins_maps_calls,
            "builtins_regular_file_call_shape": observed_regular_file_calls,
            "version_required": True,
            "minimal_compile_before_builtins_discovery_required": True,
            "builtins_current_process_maps_required": True,
            "builtins_unique_canonical_identity_required": True,
            "canonical_regular_file_required": True,
            "symlink_ambiguity_rejected": True,
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
        },
        "relation_raw_capacity_policy": (
            "2_TIMES_SEMANTIC_CAPACITY__RAW_STORAGE_SAFETY_ONLY__"
            "DEVICE_UNIQUE_GATE_REQUIRED"),
        "observed_call_shape": observed_calls,
        "relation_expected_dynamic": {
            "dynamic_device_upload_call_count": 2,
            "dynamic_device_upload_bytes": 212992,
            "dynamic_blocking_upload_call_count": 0,
            "optix_launch_count": 2,
            "semantic_compaction_launch_count": 1,
            "semantic_compaction_key_capacity": 8192,
            "semantic_compaction_scratch_bytes": 98312,
            "total_auxiliary_cuda_kernel_launch_count": 1,
            "async_d2h_call_count": 2,
            "async_d2h_bytes": 32784,
            "status_output_commit_blocking_boundary_count": 2,
        },
        "triangle_expected_dynamic": {
            "dynamic_device_upload_call_count": 2,
            "dynamic_device_upload_bytes": 524288,
            "dynamic_blocking_upload_call_count": 0,
            "optix_launch_count": 1,
            "total_auxiliary_cuda_kernel_launch_count": 0,
            "async_d2h_call_count": 2,
            "async_d2h_bytes": 12,
            "status_output_commit_blocking_boundary_count": 2,
        },
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
