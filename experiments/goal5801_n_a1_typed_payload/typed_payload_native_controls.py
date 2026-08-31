#!/usr/bin/env python3
"""Untimed native OptiX typed-payload survival controls for Goal5801-N-A1.

The experiment mechanically lifts the five frozen Goal5797 device variants
onto ``OPTIX_PAYLOAD_TYPE_ID_0``.  It then asks native OptiX, with validation
enabled and an actual ``OptixPayloadType`` supplied at module creation, whether
each counterexample is rejected or executes.  Every outcome is retained.

This is not a performance worker and imports no RTDL module.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback
from typing import Any


PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
UNTYPED_SOURCE_SHA256 = "dcfb335a2a63ab609d21ce0361d0d530f148d157bd98b122989df0dab51f17a8"
SEMANTIC_SPEC_SHA256 = "88bc8468c78302ed18cb3176e70a6c1dea65bc8306bf5e747bc18dea1e3fac4b"
UNTYPED_VARIANT_SHA256 = {
    "valid_a": "dcfb335a2a63ab609d21ce0361d0d530f148d157bd98b122989df0dab51f17a8",
    "role_effect_closure": "5c92882c642019e83f0b4336ca980ceec0e32681a0b4e50bd3c22a049ce3255e",
    "payload_attribute_abi_ownership": "a361b95773b6ed7111725a8d85160b20e2cda8673febd42f08ea30deaf604176",
    "physical_geometry_binding": "1668e822432eb008bedcd4e9d95443806d199be137d0f0533faf4ee2a5a22f74",
    "checked_program_executable_identity": "6114f10806e289941238f41e1e35e31e58c5bc3c1cf62fc82944a0c6d47cea44",
}
ATTACKS = (
    "role_effect_closure",
    "payload_attribute_abi_ownership",
    "physical_geometry_binding",
    "device_status_continuation",
    "checked_program_executable_identity",
)
NATIVE_NEGATIVE_IDENTITY_CONTROL_CASES = frozenset({
    "nearby_valid_triangle",
    "native_negative_missing_anyhit_rights",
})
NATIVE_NEGATIVE_IDENTITY_CONTROL_SOURCE_NAME = (
    "goal5801_n_a1_valid_a_identity_control.cu")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    value = path.read_bytes()
    return {"path": str(path), "bytes": len(value), "sha256": sha_bytes(value)}


def untyped_variant_sources(base_source: bytes) -> dict[str, bytes]:
    """Exact independent transcription of Goal5797's frozen transforms."""
    if sha_bytes(base_source) != UNTYPED_SOURCE_SHA256:
        raise RuntimeError("Goal5797 base device source identity drift")
    text = base_source.decode("utf-8")
    variants = {"valid_a": text}

    effects_old = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixIgnoreIntersection();\n"
        "}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}"
    )
    effects_new = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixTerminateRay();\n"
        "}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}"
    )
    if text.count(effects_old) != 1:
        raise RuntimeError("role-effect anchor is not unique")
    variants["role_effect_closure"] = text.replace(
        effects_old, effects_new, 1)

    abi_old = "optixReportIntersection(0.0f, 0u, item.item_id);"
    abi_new = "optixReportIntersection(0.0f, 0u, primitive_index);"
    if text.count(abi_old) != 1:
        raise RuntimeError("attribute-ABI anchor is not unique")
    variants["payload_attribute_abi_ownership"] = text.replace(
        abi_old, abi_new, 1)

    physical_anchor = (
        "extern \"C\" __global__ void __raygen__goal5796_relation() {"
    )
    physical_helper = r'''static __forceinline__ __device__ Box goal5797_swap_xy(Box value) {
    const float lower_x = value.lower_x;
    const float upper_x = value.upper_x;
    value.lower_x = value.lower_y;
    value.lower_y = lower_x;
    value.upper_x = value.upper_y;
    value.upper_y = upper_x;
    return value;
}

extern "C" __global__ void __raygen__goal5796_relation() {'''
    if text.count(physical_anchor) != 1:
        raise RuntimeError("physical-binding helper anchor is not unique")
    physical = text.replace(physical_anchor, physical_helper, 1)
    query_anchor = "const Box query = params.queries[query_index];"
    if physical.count(query_anchor) != 2:
        raise RuntimeError("physical-binding query anchors are not exactly two")
    physical = physical.replace(
        query_anchor,
        "const Box query = goal5797_swap_xy(params.queries[query_index]);",
    )
    variants["physical_geometry_binding"] = physical

    identity_old = "set_payload_u64(before + 1ull);"
    identity_new = "set_payload_u64(before + 2ull);"
    if text.count(identity_old) != 1:
        raise RuntimeError("executable-identity anchor is not unique")
    variants["checked_program_executable_identity"] = text.replace(
        identity_old, identity_new, 1)

    encoded = {key: value.encode("utf-8") for key, value in variants.items()}
    observed = {key: sha_bytes(value) for key, value in encoded.items()}
    if observed != UNTYPED_VARIANT_SHA256:
        raise RuntimeError({"Goal5797_variant_regeneration_drift": observed})
    return encoded


def typed_source(untyped_source: bytes) -> bytes:
    """Add only the explicit native payload-type ID to both trace calls."""
    text = untyped_source.decode("utf-8")
    anchor = "    optixTrace(\n"
    if text.count(anchor) != 2:
        raise RuntimeError("expected exactly two optixTrace call sites")
    typed = text.replace(
        anchor,
        "    optixTrace(\n        OPTIX_PAYLOAD_TYPE_ID_0,\n",
    )
    if typed.count("OPTIX_PAYLOAD_TYPE_ID_0") != 2:
        raise RuntimeError("typed trace-site transform failed")
    return typed.encode("utf-8")


def generated_sources(base_source: bytes) -> dict[str, bytes]:
    return {
        name: typed_source(value)
        for name, value in untyped_variant_sources(base_source).items()
    }


def static_check(base_source_path: Path) -> dict[str, Any]:
    generated = generated_sources(base_source_path.read_bytes())
    return {
        "status": "PASS__STATIC_ONLY__NO_GPU_IMPORT",
        "base_source_sha256": sha_bytes(base_source_path.read_bytes()),
        "untyped_variant_sha256": UNTYPED_VARIANT_SHA256,
        "typed_variant_sha256": {
            key: sha_bytes(value) for key, value in generated.items()
        },
        "typed_trace_site_count_each": {
            key: value.count(b"OPTIX_PAYLOAD_TYPE_ID_0")
            for key, value in generated.items()
        },
        "registered_performance_timing_count": 0,
    }


def exception_record(exc: BaseException) -> dict[str, Any]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "repr": repr(exc),
        "traceback": traceback.format_exc(),
    }


def nvrtc_compile(base: Any, source: bytes, source_name: str,
                  optix_include: Path, cuda_include: Path) -> tuple[bytes, str]:
    nvrtc = base.nvrtc
    program = base.check_nvrtc(nvrtc.nvrtcCreateProgram(
        source, source_name.encode(), 0, [], []))
    options = [
        b"--std=c++17", b"--device-as-default-execution-space",
        b"--relocatable-device-code=true",
        f"-I{optix_include}".encode(), f"-I{cuda_include}".encode(),
    ]
    base.check_nvrtc(
        nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    log_size = base.check_nvrtc(nvrtc.nvrtcGetProgramLogSize(program))
    log_bytes = b" " * log_size
    base.check_nvrtc(nvrtc.nvrtcGetProgramLog(program, log_bytes))
    ptx_size = base.check_nvrtc(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * ptx_size
    base.check_nvrtc(nvrtc.nvrtcGetPTX(program, ptx))
    return ptx, log_bytes.rstrip(b"\0 ").decode("utf-8", errors="replace")


def native_semantics(optix: Any, *, allow_anyhit_write: bool) -> int:
    value = int(optix.PAYLOAD_SEMANTICS_TRACE_CALLER_READ_WRITE)
    if allow_anyhit_write:
        value |= int(optix.PAYLOAD_SEMANTICS_AH_READ_WRITE)
    else:
        # The device code both reads and writes in triangle any-hit.  Omitting
        # all AH rights is the deliberately invalid native-negative control.
        value |= int(optix.PAYLOAD_SEMANTICS_AH_NONE)
    return value


def typed_pipeline_options(base: Any, *, custom: bool) -> Any:
    optix = base.optix
    kwargs = dict(
        usesMotionBlur=False,
        traversableGraphFlags=int(optix.TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS),
        numPayloadValues=0,
        numAttributeValues=1 if custom else 2,
        exceptionFlags=int(optix.EXCEPTION_FLAG_NONE),
        pipelineLaunchParamsVariableName="params",
    )
    if optix.version()[1] >= 2:
        kwargs["usesPrimitiveTypeFlags"] = (
            optix.PRIMITIVE_TYPE_FLAGS_CUSTOM if custom
            else optix.PRIMITIVE_TYPE_FLAGS_TRIANGLE)
    return optix.PipelineCompileOptions(**kwargs)


def build_typed_pipeline(base: Any, context: Any, ptx: bytes, *, task: str,
                         allow_anyhit_write: bool,
                         phase: dict[str, Any]) -> tuple[Any, Any, Any]:
    optix = base.optix
    custom = task == "relation"
    pipeline_options = typed_pipeline_options(base, custom=custom)
    semantics = native_semantics(
        optix, allow_anyhit_write=allow_anyhit_write)
    payload_type = optix.PayloadType([semantics, semantics])
    module_options = optix.ModuleCompileOptions(
        maxRegisterCount=optix.COMPILE_DEFAULT_MAX_REGISTER_COUNT,
        optLevel=optix.COMPILE_OPTIMIZATION_DEFAULT,
        debugLevel=optix.COMPILE_DEBUG_LEVEL_DEFAULT,
    )
    module_options.payloadTypes = [payload_type]
    module, module_log = context.moduleCreate(
        module_options, pipeline_options, ptx)
    phase["module"] = {
        "verdict": "PASS", "log": str(module_log),
        "num_payload_types": 1, "num_payload_values_per_type": 2,
        "payload_semantics_u32_each": semantics,
        "pipeline_num_payload_values": 0,
    }

    descriptions = []
    raygen = optix.ProgramGroupDesc()
    raygen.raygenModule = module
    raygen.raygenEntryFunctionName = (
        "__raygen__goal5796_relation" if custom
        else "__raygen__goal5796_triangle")
    descriptions.append(("raygen", raygen))
    miss = optix.ProgramGroupDesc()
    miss.missModule = module
    miss.missEntryFunctionName = (
        "__miss__goal5796_relation" if custom
        else "__miss__goal5796_triangle")
    descriptions.append(("miss", miss))
    hit = optix.ProgramGroupDesc()
    hit.hitgroupModuleAH = module
    hit.hitgroupEntryFunctionNameAH = (
        "__anyhit__goal5796_relation" if custom
        else "__anyhit__goal5796_triangle")
    if custom:
        hit.hitgroupModuleIS = module
        hit.hitgroupEntryFunctionNameIS = "__intersection__goal5796_relation"
    descriptions.append(("hitgroup", hit))

    groups = []
    program_logs = {}
    # Pin the exact same native payload type at every program-group boundary.
    # The diagnostic binding repair synchronizes this PayloadType instance in
    # its constructor, so ProgramGroupOptions receives a populated native
    # OptixPayloadType rather than an empty wrapper.
    program_group_options = optix.ProgramGroupOptions(payload_type)
    for name, desc in descriptions:
        group, log = context.programGroupCreate([desc], program_group_options)
        groups.append(group[0])
        program_logs[name] = str(log)
    phase["program_groups"] = {
        "verdict": "PASS", "logs": program_logs,
        "payload_type_selection": "EXPLICIT_SAME_PAYLOAD_TYPE_AT_EVERY_PROGRAM_GROUP",
    }

    link = optix.PipelineLinkOptions()
    link.maxTraceDepth = 1
    pipeline = context.pipelineCreate(pipeline_options, link, groups, "")
    stack = optix.StackSizes()
    for group in groups:
        if optix.version()[:2] >= (7, 7):
            optix.util.accumulateStackSizes(group, stack, pipeline)
        else:
            optix.util.accumulateStackSizes(group, stack)
    dc_trav, dc_state, cc = optix.util.computeStackSizes(stack, 1, 0, 0)
    pipeline.setStackSize(dc_trav, dc_state, cc, 1)
    phase["pipeline_link"] = {"verdict": "PASS", "max_trace_depth": 1}
    sbt, sbt_keepalive = base.make_sbt(groups)
    return pipeline, sbt, (module, payload_type, groups, sbt_keepalive)


def run_relation_forward(base: Any, context: Any, pipeline: Any, sbt: Any,
                         fixture: dict[str, Any]) -> dict[str, Any]:
    cp = base.cp
    np = base.np
    indexed = base.boxes_array(fixture["indexed"])
    sources = base.boxes_array(fixture["sources"])
    d_indexed = base.to_device(indexed)
    d_sources = base.to_device(sources)
    raw_capacity = max(1, 2 * len(indexed) * len(sources))
    d_rows = cp.zeros(raw_capacity * 2, dtype=np.uint32)
    d_count = cp.zeros(1, dtype=np.uint32)
    d_overflow = cp.zeros(1, dtype=np.uint32)
    d_status = cp.zeros(1, dtype=np.uint32)
    handle, gas_keepalive = base.build_custom_gas(context, indexed)
    params = np.zeros(1, dtype=base.PARAM_DTYPE)
    params[0] = (
        handle, d_indexed.ptr, d_sources.ptr, d_rows.data.ptr,
        d_count.data.ptr, d_overflow.data.ptr,
        len(indexed), len(sources), raw_capacity, 0,
        np.float32(fixture["minimum_overlap"]), np.float32(0.0),
        np.float32(1.0), 0, 0, 0, 0, 0, d_status.data.ptr,
    )
    device_params = base.launch(pipeline, sbt, params, len(sources))
    keepalive = [d_indexed, d_sources, d_rows, d_count, d_overflow,
                 d_status, *gas_keepalive, device_params]
    raw_count = int(cp.asnumpy(d_count)[0])
    overflow = int(cp.asnumpy(d_overflow)[0])
    status = int(cp.asnumpy(d_status)[0])
    raw = cp.asnumpy(d_rows[:raw_count * 2]).reshape((-1, 2))
    rows = sorted({(int(row[0]), int(row[1])) for row in raw})
    del keepalive
    return {
        "output": [list(row) for row in rows],
        "raw_event_count": raw_count,
        "device_overflow": overflow,
        "device_status": status,
    }


def run_real_overflow_bypass(base: Any, context: Any, pipeline: Any, sbt: Any,
                             fixture: dict[str, Any]) -> dict[str, Any]:
    """Deliberately violate status-before-output after a real device overflow."""
    cp = base.cp
    np = base.np
    indexed = base.boxes_array(fixture["indexed"])
    sources = base.boxes_array(fixture["sources"])
    d_indexed = base.to_device(indexed)
    d_sources = base.to_device(sources)
    raw_capacity = 7
    d_rows = cp.zeros(raw_capacity * 2, dtype=np.uint32)
    d_count = cp.zeros(1, dtype=np.uint32)
    d_overflow = cp.zeros(1, dtype=np.uint32)
    d_status = cp.zeros(1, dtype=np.uint32)
    handle, gas_keepalive = base.build_custom_gas(context, indexed)
    params = np.zeros(1, dtype=base.PARAM_DTYPE)
    params[0] = (
        handle, d_indexed.ptr, d_sources.ptr, d_rows.data.ptr,
        d_count.data.ptr, d_overflow.data.ptr,
        len(indexed), len(sources), raw_capacity, 0,
        np.float32(fixture["minimum_overlap"]), np.float32(0.0),
        np.float32(1.0), 0, 0, 0, 0, 0, d_status.data.ptr,
    )
    device_params = base.launch(pipeline, sbt, params, len(sources))
    keepalive = [d_indexed, d_sources, d_rows, d_count, d_overflow,
                 d_status, *gas_keepalive, device_params]
    raw_count = int(cp.asnumpy(d_count)[0])
    overflow = int(cp.asnumpy(d_overflow)[0])
    status = int(cp.asnumpy(d_status)[0])
    # This D2H is intentionally after observing failure.  It is the exact
    # application-continuation defect under test, never the RTDL good path.
    raw = cp.asnumpy(d_rows).reshape((-1, 2))
    rows = sorted({(int(row[0]), int(row[1])) for row in raw})
    del keepalive
    return {
        "status_observed_before_application_output_copy": True,
        "application_output_copied_despite_failure": True,
        "application_result_consumed": True,
        "raw_capacity": raw_capacity,
        "raw_event_count": raw_count,
        "device_overflow": overflow,
        "device_status": status,
        "returned_row_count": len(rows),
        "returned_rows": [list(row) for row in rows],
    }


def run_case(base: Any, *, name: str, source: bytes, task: str,
             fixture: dict[str, Any], optix_include: Path, cuda_include: Path,
             evidence_dir: Path, allow_anyhit_write: bool) -> dict[str, Any]:
    source_path = evidence_dir / "device_sources" / f"{name}.cu"
    ptx_path = evidence_dir / "ptx" / f"{name}.ptx"
    nvrtc_source_name = (
        NATIVE_NEGATIVE_IDENTITY_CONTROL_SOURCE_NAME
        if name in NATIVE_NEGATIVE_IDENTITY_CONTROL_CASES
        else source_path.name
    )
    source_path.write_bytes(source)
    row: dict[str, Any] = {
        "id": name, "task": task,
        "allow_anyhit_write": allow_anyhit_write,
        "nvrtc_source_name": nvrtc_source_name,
        "source": file_identity(source_path), "phases": {},
    }
    logger = None
    keepalive = None
    current_phase = "nvrtc"
    try:
        ptx, nvrtc_log = nvrtc_compile(
            base, source, nvrtc_source_name, optix_include, cuda_include)
        ptx_path.write_bytes(ptx)
        row["ptx"] = file_identity(ptx_path)
        row["phases"]["nvrtc"] = {"verdict": "PASS", "log": nvrtc_log}

        current_phase = "context"
        context, logger = base.make_context()
        row["phases"]["context"] = {
            "verdict": "PASS", "validation_mode": "ALL"}
        current_phase = "module_or_pipeline"
        pipeline, sbt, keepalive = build_typed_pipeline(
            base, context, ptx, task=task,
            allow_anyhit_write=allow_anyhit_write,
            phase=row["phases"])
        current_phase = "launch"
        if name == "nearby_valid_relation":
            observation = run_relation_forward(
                base, context, pipeline, sbt, fixture)
        elif name in {
                "payload_attribute_abi_ownership",
                "physical_geometry_binding"}:
            observation = run_relation_forward(
                base, context, pipeline, sbt, fixture)
        elif name == "device_status_continuation":
            observation = run_real_overflow_bypass(
                base, context, pipeline, sbt, fixture)
        else:
            per_ray, weighted = base.run_triangle(
                context, pipeline, sbt, fixture)
            observation = {"per_ray": per_ray, "weighted_sum": weighted}
        row["observation"] = observation
        row["phases"]["launch"] = {"verdict": "PASS"}
        row["terminal_phase"] = "launch_completed"
    except BaseException as exc:  # preserve every native/infra outcome
        failure_phase = current_phase
        if current_phase == "module_or_pipeline":
            if row["phases"].get("module", {}).get("verdict") != "PASS":
                failure_phase = "module"
            elif row["phases"].get("program_groups", {}).get("verdict") != "PASS":
                failure_phase = "program_groups"
            elif row["phases"].get("pipeline_link", {}).get("verdict") != "PASS":
                failure_phase = "pipeline_link"
            else:
                failure_phase = "native_build_unknown"
        row["phases"].setdefault(failure_phase, {})
        row["phases"][failure_phase].update({
            "verdict": "REJECT_OR_ERROR", "exception": exception_record(exc)})
        row["terminal_phase"] = failure_phase
    row["optix_validation_messages"] = (
        list(logger.messages) if logger is not None else [])
    row["optix_validation_error_or_fatal_message_count"] = sum(
        1 for item in row["optix_validation_messages"]
        if int(item["level"]) <= 2)
    del keepalive
    return row


def classify(row: dict[str, Any]) -> str:
    name = row["id"]
    launched = row.get("terminal_phase") == "launch_completed"
    native_payload_rejection = native_payload_specific_rejection(row)
    if name == "native_negative_missing_anyhit_rights":
        if launched:
            return "INVALID__NATIVE_NEGATIVE_WAS_NOT_REJECTED"
        return (
            "PASS__NATIVE_TYPED_SEMANTICS_REJECTED_NEGATIVE"
            if native_payload_rejection else
            "INVALID__INFRA_OR_TRANSCRIPTION_FAILURE")
    if name == "nearby_valid_relation":
        return (
            "PASS__NEARBY_VALID"
            if launched and row.get("observation") == {
                "output": [[100, 10], [101, 20]],
                "raw_event_count": 2,
                "device_overflow": 0,
                "device_status": 0,
            } else "INVALID__NEARBY_VALID_RELATION_FAILED")
    if name == "nearby_valid_triangle":
        return (
            "PASS__NEARBY_VALID"
            if launched and row.get("observation") == {
                "per_ray": [3, 2, 0, 1], "weighted_sum": 16}
            else "INVALID__NEARBY_VALID_TRIANGLE_FAILED")
    if not launched:
        return (
            "NATIVE_TYPED_SEMANTICS_REJECTED_ATTACK__RTDL_CLAIM_MUST_NARROW"
            if native_payload_rejection else
            "INVALID__INFRA_OR_TRANSCRIPTION_FAILURE")
    observation = row.get("observation")
    exact = {
        "role_effect_closure": {
            "per_ray": [1, 1, 0, 1], "weighted_sum": 11},
        "payload_attribute_abi_ownership": {
            "output": [[100, 0], [101, 1]], "raw_event_count": 2,
            "device_overflow": 0, "device_status": 0},
        "physical_geometry_binding": {
            "output": [[100, 20], [101, 10]], "raw_event_count": 2,
            "device_overflow": 0, "device_status": 0},
        "checked_program_executable_identity": {
            "per_ray": [6, 4, 0, 2], "weighted_sum": 32},
    }
    if name == "device_status_continuation":
        good = (
            observation.get("status_observed_before_application_output_copy") is True
            and observation.get("application_output_copied_despite_failure") is True
            and observation.get("application_result_consumed") is True
            and observation.get("raw_capacity") == 7
            and observation.get("raw_event_count") == 8
            and observation.get("device_overflow") == 1
            and observation.get("device_status") == 0
            and observation.get("returned_row_count") == 7)
    else:
        good = observation == exact[name]
    return (
        "NATIVE_ACCEPTED_AND_EXECUTED_EXACT_COUNTEREXAMPLE__RESIDUAL_SURVIVES"
        if good else "INVALID__ATTACK_OUTCOME_DRIFT")


def native_payload_specific_rejection(row: dict[str, Any]) -> bool:
    """Reject infra failures; require a native build-stage payload diagnosis."""
    phases = row.get("phases", {})
    if phases.get("nvrtc", {}).get("verdict") != "PASS" \
            or phases.get("context", {}).get("verdict") != "PASS":
        return False
    failing_phase = first_failing_native_phase(row)
    if failing_phase is None:
        return False
    failing = phases[failing_phase]
    evidence_values = []
    if isinstance(failing.get("log"), str):
        evidence_values.append(failing["log"])
    exception = failing.get("exception", {})
    if isinstance(exception, dict):
        # Exclude traceback and JSON key names: the runner filename and
        # successful metadata contain the word "payload" by construction.
        for key in ("message", "repr"):
            if isinstance(exception.get(key), str):
                evidence_values.append(exception[key])
    for message in row.get("optix_validation_messages", []):
        if isinstance(message, dict):
            for key in ("tag", "message"):
                if isinstance(message.get(key), str):
                    evidence_values.append(message[key])
    evidence = "\n".join(evidence_values).lower()
    payload_markers = (
        "optix_error_payload_type_mismatch",
        "optix_error_payload_type_resolution_failed",
        "payload type mismatch",
        "payload type resolution",
        "payload semantics",
        "payload access",
        "payload register",
        "payload value",
    )
    return any(marker in evidence for marker in payload_markers)


def first_failing_native_phase(row: dict[str, Any]) -> str | None:
    phases = row.get("phases", {})
    order = ("module", "program_groups", "pipeline_link")
    for name in order:
        verdict = phases.get(name, {}).get("verdict")
        if verdict == "REJECT_OR_ERROR":
            return name
        if verdict != "PASS":
            return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-check", action="store_true")
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--base-device-source", type=Path, required=True)
    parser.add_argument("--base-host-source", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--binding-receipt", type=Path)
    parser.add_argument("--expected-optix-api-version", default="9.0.0")
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.static_check:
        print(json.dumps(static_check(args.base_device_source),
                         indent=2, sort_keys=True))
        return 0
    required = (
        args.spec, args.base_host_source, args.optix_include,
        args.cuda_include, args.binding_receipt, args.evidence_dir, args.output)
    if any(value is None for value in required):
        raise SystemExit("GPU execution requires every non-static argument")
    if args.evidence_dir.exists() or args.output.exists():
        raise FileExistsError("Goal5801-N-A1 outputs are create-only")
    spec_bytes = args.spec.read_bytes()
    if sha_bytes(spec_bytes) != SEMANTIC_SPEC_SHA256:
        raise RuntimeError("semantic spec identity drift")
    spec = json.loads(spec_bytes)
    binding_receipt_bytes = args.binding_receipt.read_bytes()
    binding_receipt = json.loads(binding_receipt_bytes)
    if binding_receipt.get("status") \
            != "PASS__TWO_LINE_FFI_PAYLOAD_TYPE_REPAIR__UNTIMED":
        raise RuntimeError("patched PyOptiX receipt is not controlling")

    sys.path.insert(0, str(args.base_host_source.resolve().parent))
    import pyoptix_baseline as base  # type: ignore  # noqa: E402
    version = tuple(int(value) for value in base.optix.version())
    expected_version = tuple(
        int(value) for value in args.expected_optix_api_version.split("."))
    if version != expected_version:
        raise RuntimeError(f"OptiX API mismatch: {version} != {expected_version}")
    loaded_optix_package = Path(base.optix.__file__).resolve(strict=True)
    loaded_optix_extension = Path(
        importlib.import_module("optix._optix").__file__).resolve(strict=True)
    installed_extension = binding_receipt["installed_extension"]
    if sha_bytes(loaded_optix_extension.read_bytes()) \
            != installed_extension["sha256"]:
        raise RuntimeError("loaded OptiX extension is not repaired receipt bytes")

    sources = generated_sources(args.base_device_source.read_bytes())
    args.evidence_dir.mkdir(parents=True)
    (args.evidence_dir / "device_sources").mkdir()
    (args.evidence_dir / "ptx").mkdir()
    relation = spec["tasks"]["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"]
    diagnostic = next(
        row for row in relation["fixtures"] if row["id"] == "diagnostic_cross")
    broad = next(
        row for row in relation["fixtures"] if row["id"] == "librts_tiny_broad")
    triangle = spec["tasks"]["BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"]

    definitions = [
        ("nearby_valid_relation", "valid_a", "relation", diagnostic, True),
        ("nearby_valid_triangle", "valid_a", "triangle", triangle, True),
        ("role_effect_closure", "role_effect_closure", "triangle", triangle, True),
        ("payload_attribute_abi_ownership", "payload_attribute_abi_ownership",
         "relation", diagnostic, True),
        ("physical_geometry_binding", "physical_geometry_binding",
         "relation", diagnostic, True),
        ("device_status_continuation", "valid_a", "relation", broad, True),
        ("checked_program_executable_identity",
         "checked_program_executable_identity", "triangle", triangle, True),
        ("native_negative_missing_anyhit_rights", "valid_a", "triangle",
         triangle, False),
    ]
    rows = []
    for name, source_name, task, fixture, allow_ah in definitions:
        row = run_case(
            base, name=name, source=sources[source_name], task=task,
            fixture=fixture, optix_include=args.optix_include,
            cuda_include=args.cuda_include, evidence_dir=args.evidence_dir,
            allow_anyhit_write=allow_ah)
        row["source_variant"] = source_name
        row["classification"] = classify(row)
        rows.append(row)

    by_id = {row["id"]: row for row in rows}
    nearby_triangle = by_id["nearby_valid_triangle"]
    native_negative = by_id["native_negative_missing_anyhit_rights"]
    negative_identity_same = (
        nearby_triangle["source"]["sha256"] == native_negative["source"]["sha256"]
        and nearby_triangle["source"]["bytes"] == native_negative["source"]["bytes"]
        and nearby_triangle.get("ptx", {}).get("sha256")
        == native_negative.get("ptx", {}).get("sha256")
        and nearby_triangle.get("ptx", {}).get("bytes")
        == native_negative.get("ptx", {}).get("bytes"))
    if not negative_identity_same:
        native_negative["classification"] = (
            "INVALID__NEGATIVE_SOURCE_OR_PTX_DIFFERS_FROM_NEARBY_VALID")

    collision = [row["id"] for row in rows if row["id"] in ATTACKS and
                 row["classification"].startswith("NATIVE_TYPED")]
    residual = [row["id"] for row in rows if row["id"] in ATTACKS and
                row["classification"].startswith("NATIVE_ACCEPTED")]
    invalid = [row["id"] for row in rows if
               row["classification"].startswith("INVALID")]
    required_control_classifications = {
        "nearby_valid_relation": "PASS__NEARBY_VALID",
        "nearby_valid_triangle": "PASS__NEARBY_VALID",
        "native_negative_missing_anyhit_rights": (
            "PASS__NATIVE_TYPED_SEMANTICS_REJECTED_NEGATIVE"),
    }
    controls_pass = all(
        by_id[name]["classification"] == expected
        for name, expected in required_control_classifications.items())
    status = (
        "PASS__UNCONDITIONAL_NATIVE_TYPED_PAYLOAD_SURVIVAL_RESULT"
        if controls_pass and not invalid
        and sorted(collision + residual) == sorted(ATTACKS)
        else "INVALID__CONTROL_OR_ATTACK_OUTCOME_DRIFT")
    result = {
        "schema": "rtdl.goal5801_n_a1.native_typed_payload_survival.v1",
        "status": status,
        "scope": {
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0, "pod_count": 0,
            "wsl_used": False, "performance_claimed": False,
            "rtdl_imported": False,
        },
        "machine": {
            "hostname": platform.node(),
            "kernel": platform.platform(),
            "nvidia_smi": subprocess.run([
                "nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap",
                "--format=csv,noheader"], check=True, capture_output=True,
                text=True).stdout.strip(),
        },
        "optix": {
            "api_version": ".".join(map(str, version)),
            "validation_mode": "ALL",
            "native_payload_type_enabled": True,
            "payload_type_id": "OPTIX_PAYLOAD_TYPE_ID_0",
            "payload_words": 2,
            "loaded_package_init": file_identity(loaded_optix_package),
            "loaded_extension": file_identity(loaded_optix_extension),
        },
        "pyoptix": {
            "upstream_commit": PYOPTIX_COMMIT,
            "distribution_version": importlib.metadata.version("pyoptix"),
            "stock_or_unmodified_binding_claimed": False,
            "two_line_ffi_payload_type_repair_used": True,
            "binding_receipt": {
                "bytes": len(binding_receipt_bytes),
                "sha256": sha_bytes(binding_receipt_bytes),
            },
        },
        "inputs": {
            "semantic_spec": file_identity(args.spec),
            "base_device_source": file_identity(args.base_device_source),
            "base_host_source": file_identity(args.base_host_source),
            "runner": file_identity(Path(__file__).resolve()),
        },
        "cases": rows,
        "native_negative_identity_control": {
            "source_byte_identical_to_nearby_valid_triangle": (
                nearby_triangle["source"]["sha256"]
                == native_negative["source"]["sha256"]),
            "ptx_byte_identical_to_nearby_valid_triangle": (
                nearby_triangle.get("ptx", {}).get("sha256")
                == native_negative.get("ptx", {}).get("sha256")),
            "only_runtime_configuration_difference": (
                "payload semantics omit AH rights"),
            "pass": negative_identity_same,
        },
        "native_collision_mechanisms": collision,
        "residual_surviving_mechanisms": residual,
        "invalid_cases": invalid,
        "required_validity_controls_pass": controls_pass,
        "claim_rule": {
            "native_rejected_attack": "DELETE_OR_NARROW_THAT_RTDL_RESIDUAL",
            "native_accepted_exact_counterexample": "RESIDUAL_SURVIVES_THIS_CONTROL",
            "all_outcomes_accepted": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": status, "native_collision_mechanisms": collision,
        "residual_surviving_mechanisms": residual, "invalid_cases": invalid,
    }, sort_keys=True))
    return 0 if not invalid else 2


if __name__ == "__main__":
    raise SystemExit(main())
