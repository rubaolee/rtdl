#!/usr/bin/env python3
"""Independently verify one Goal5838 selected-topology GPU exam artifact.

This verifier deliberately imports no RTDL module.  It checks the prospective
selection, frozen-core identities, Git source custody, oracle outputs, generic
family identities, and the complete native OptiX traversal-receipt envelope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import struct
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_ROOT = (
    "history/internal_docs/goal5838_generic_core_exam_20260902"
)
SELECTION_PATH = f"{AUTHORITY_ROOT}/CHALLENGE_SELECTION_RESULT.json"
SEAL_PATH = f"{AUTHORITY_ROOT}/GENERIC_CORE_SEAL.json"
TABLE_PATH = f"{AUTHORITY_ROOT}/CHALLENGE_TABLE.json"
SELECTED_CANDIDATE_ID = (
    "builtin_sphere::any_hit_count_continue_u64_per_query"
)
SELECTION_RESULT_SHA256 = (
    "9f543f52cd9453e0410766aa79c3f302a6a0e39314487279842fa5ad5e57ed61"
)
SELECTION_FILE_SHA256 = (
    "f12461047e234901b799d5fadeb1ce9bf58172a34a21138a09ceeac51ae772f9"
)
GENERIC_CORE_SEAL_SHA256 = (
    "c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae"
)
CHALLENGE_TABLE_SHA256 = (
    "0a2b2c01aed75ad08fad44f7fbc2509ef632d786545e0202b9a4b27425a30345"
)
TARGET_LOCAL_RANDOM_VALUE = (
    "aa62c239c5079ed89cf0ad70c1b44245552bf2dd519d6d4871518746fac2efca"
    "5a64bb5a21956e897e36a5bc7cc0f0bd53d1f9ae585045a3c762656f852eefa7"
)
PLAN_SHA256 = (
    "5a8f15a3941f10560ffecc6021cd4689c068f5ed39903014b1d5e99e98b3d669"
)
PROVIDER_DESCRIPTOR_SHA256 = (
    "a92be4d2defc87fd7dcf2e1edd143cf6afb63035a7048a7560d486b4bdf7463a"
)
PROVIDER_PROJECTION_SHA256 = (
    "fe26dc5417f644c7c649dfbe9827404ed9c914d82334d16e878872cc11f68ec1"
)
FIXTURE_SHA256 = (
    "69e38e95e8d3a2e14cb428f18e4d8bb27a87da1c21688b6ddad672406a94977a"
)
ORACLE_SHA256 = (
    "b43839793ea426528053adc4ff1cd66d090ac6f2b05b6b774fa7c290bb91fa63"
)
EXPECTED_COUNTS = (4, 1, 1, 0, 4, 0)
EXPECTED_CASE_NAMES = (
    "four_hits_with_overlapping_centers",
    "one_offset_hit",
    "one_negative_offset_hit",
    "all_miss",
    "reverse_direction_four_hits",
    "parallel_plane_miss",
)
OBSERVED_T_SENTINEL_BITS = 0x7FFFFFFF
FIXTURE_CENTERS = (
    (3.0, 0.0, 0.0),
    (3.0, 0.0, 0.0),
    (5.0, 0.0, 0.0),
    (5.0, 2.0, 0.0),
    (7.0, -2.0, 0.0),
    (9.0, 0.0, 0.0),
)
FIXTURE_RADII = (1.0, 0.5, 1.25, 0.75, 0.5, 1.0)
FIXTURE_QUERIES = (
    ((0.0, 0.0, 0.0), (12.0, 0.0, 0.0)),
    ((0.0, 2.0, 0.0), (12.0, 2.0, 0.0)),
    ((0.0, -2.0, 0.0), (12.0, -2.0, 0.0)),
    ((0.0, 4.0, 0.0), (12.0, 4.0, 0.0)),
    ((12.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    ((0.0, 0.0, 3.0), (12.0, 0.0, 3.0)),
)
CALLBACK_IR_SHA256 = (
    "72e1a9fafd54d8d4ae72e5d48ae6a91ce53e53c7c08bc1860308b516d3f6ef08"
)
CALLBACK_EFFECT_SHA256 = (
    "49c63a2ed9e1cfa8beb47dc7595ce82d5eee63523b3efbb619ff50de0453bf5c"
)
CALLBACK_ABI_SHA256 = (
    "833d9555602a54f234ed2cdd57e51ef1e087019e43a24481767eddff468402ea"
)
PHYSICAL_SCHEMA_SHA256 = (
    "b76c99505b1156a8eb7c23021c4fa9d86b64af84e365bcf9afbc85c8af109bb8"
)
PHYSICAL_TEMPLATE_ID = "builtin_sphere_any_hit_count_u64_per_query_v1"
PROGRAM_BUNDLE = "v4_builtin_sphere_callback_ir_four_role_composed"
ROUTE_IDENTITY = "v4_builtin_sphere_any_hit_count:four_role_composed_v1"
CORE_ROWS = (
    (
        "src/rtdsl/v4_family_schema.py",
        58007,
        "2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224",
    ),
    (
        "src/rtdsl/v4_generic_family_lifecycle.py",
        41675,
        "7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c",
    ),
    (
        "src/rtdsl/v4_family.py",
        2792,
        "d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8",
    ),
)
EXAM_SOURCE_PATHS = (
    "case_studies/goal5838_selected_sphere_any_hit_count/README.md",
    "case_studies/goal5838_selected_sphere_any_hit_count/fixture.py",
    (
        "case_studies/goal5838_selected_sphere_any_hit_count/"
        "sphere_any_hit_count_oracle.py"
    ),
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "scripts/goal5838_run_selected_sphere_gpu_exam.py",
    "scripts/goal5838_verify_selected_sphere_gpu_exam.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/rtdsl/physical_execution_provenance.py",
    "src/rtdsl/v4_family_route_adapters.py",
    "src/rtdsl/v4_public_sphere_any_hit_count.py",
    "src/rtdsl/v4_sphere_any_hit_count.py",
    "src/rtdsl/v4_sphere_any_hit_count_contract.py",
    "src/rtdsl/v4_sphere_any_hit_count_family_route.py",
    "src/rtdsl/v4_sphere_any_hit_count_numba_codegen.py",
    "src/rtdsl/v4_sphere_any_hit_count_optix_compiler.py",
    "src/rtdsl/v4_sphere_any_hit_count_prepared_runtime.py",
    "src/rtdsl/v4_sphere_any_hit_count_wrapper_codegen.py",
    "src/rtdsl/v4_sphere_physical_schema.py",
    "src/rtdsl/v4_sphere_prepared_runtime.py",
    "tests/goal5838_selected_sphere_any_hit_count_test.py",
)
NATIVE_BUILD_RESULT_DOMAIN = (
    "rtdl.goal5838.selected_sphere_optix_provider_build.v1"
)
NATIVE_BUILD_SOURCE_PATHS = (
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)
NATIVE_BUILD_TRANSLATION_UNITS = (
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)
NATIVE_BUILD_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
    "rtdl_optix_v4_rtdlexe_producer_descriptor_v1",
    "rtdl_optix_traversal_audit_begin",
    "rtdl_optix_traversal_audit_finish",
    "rtdl_optix_traversal_audit_abort",
    "rtdl_optix_v4_prepare_builtin_sphere_callback_v1",
    "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1",
)
SNAPSHOT_FIELDS = {
    "nonce_hi",
    "nonce_lo",
    "attempted_launch_count",
    "successful_launch_count",
    "failed_launch_count",
    "complete_context_launch_count",
    "incomplete_context_launch_count",
    "context_bind_count",
    "raygen_invocation_count",
    "program_bundle_mix",
    "traversable_mix",
    "pipeline_mix",
    "sbt_mix",
    "stream_mix",
    "params_mix",
    "callsite_mix",
    "first_program_bundle_id",
    "last_program_bundle_id",
    "first_traversable",
    "last_traversable",
    "pending_context_at_finish",
    "session_error",
    "incomplete_callsite_record_count",
    "incomplete_callsite_lines",
}
PHYSICAL_RECEIPT_FIELDS = {
    "schema",
    "native_descriptor",
    "build_input_type_name",
    "primitive_type_name",
    "builtin_is_api_name",
    "geometry_flags_name",
    "continuation_name",
    "result_semantics",
    "provider_private_primitive_ids",
    "metadata_channels",
    "native_library_sha256",
    "loaded_native_library_path",
    "composed_ptx_sha256",
    "authority_nonce",
    "field_mapping_commitment_sha256",
    "static_input_commitment_sha256",
    "status_before_output",
    "numeric_policy",
    "discriminant_guard_binary32_unit_roundoffs",
    "nonexact_toi_ulp_bound",
    "query_commitment_sha256",
    "output_commitment_sha256",
    "raw_output_commitment_sha256",
    "role_counters",
}
NATIVE_DESCRIPTOR_FIELDS = {
    "schema",
    "build_input_type",
    "primitive_type",
    "primitive_type_flags",
    "builtin_is_build_flags",
    "builtin_is_module",
    "user_intersection_program",
    "uses_motion_blur",
    "build_flags",
    "geometry_flags",
    "center_stride_bytes",
    "radius_stride_bytes",
    "single_radius",
    "primitive_index_offset",
    "sbt_record_count",
    "gas_count",
    "primitive_count",
    "motion_key_count",
    "traversable_graph_flags",
    "max_payload_values",
    "max_attribute_values",
    "max_trace_depth",
    "program_group_count",
    "compiled_optix_version",
    "compiled_optix_major",
    "compiled_optix_minor",
    "compiled_optix_patch",
    "cuda_device_ordinal",
    "cuda_compute_capability_major",
    "cuda_compute_capability_minor",
    "cuda_driver_version",
    "static_input_fingerprint",
    "device_static_input_fingerprint",
    "center_device_pointer",
    "radius_device_pointer",
    "application_id_device_pointer",
    "traversable_identity",
    "last_execution_present",
    "last_status_failed",
    "last_query_count",
    "last_status_d2h_call_count",
    "last_application_output_d2h_call_count",
    "last_output_after_status_failure_count",
    "last_query_device_pointer_nonzero_count",
    "last_output_device_pointer_nonzero_count",
    "last_query_fingerprint",
    "last_device_query_fingerprint",
    "last_output_fingerprint",
    "last_status_fingerprint",
    "last_counter_fingerprint",
    "last_query_device_pointer_fingerprint",
    "last_output_device_pointer_fingerprint",
}


class Goal5838ExamVerificationError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise Goal5838ExamVerificationError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_external_output(path: Path, *, artifact_path: Path) -> Path:
    output = path.expanduser().resolve()
    root = ROOT.resolve()
    if output == root or root in output.parents:
        raise ValueError(f"verification output must be outside Git tree: {output}")
    if output == artifact_path.resolve():
        raise ValueError("verification output must differ from the exam artifact")
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def _write_json_exclusive(path: Path, value: object) -> None:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(path) from None
    finally:
        temporary.unlink(missing_ok=True)


def _f32(value: object) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _f32_bits(value: object) -> int:
    return struct.unpack("<I", struct.pack("<f", float(value)))[0]


def _f32_from_bits(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


def _normalized_query_rows(queries) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(_f32(value) for point in query for value in point)
        for query in queries
    )


def _native_fingerprint(
    domain: str, columns: tuple[tuple[str, object], ...]
) -> str:
    states = [
        14695981039346656037,
        1099511628211 ^ 0x9E3779B97F4A7C15,
        0x6A09E667F3BCC909,
        0xBB67AE8584CAA73B,
    ]
    primes = [1099511628211, 1099511627791, 1099511627689, 1099511627609]
    mask = (1 << 64) - 1

    def add_byte(byte: int) -> None:
        for index in range(4):
            states[index] ^= byte + index * 17
            states[index] = (states[index] * primes[index]) & mask

    def add_integer(value: int, bits: int) -> None:
        for shift in range(0, bits, 8):
            add_byte((value >> shift) & 0xFF)

    encoded_domain = domain.encode("ascii")
    add_integer(len(encoded_domain), 64)
    for byte in encoded_domain:
        add_byte(byte)
    for kind, value in columns:
        if kind == "u32":
            add_integer(int(value), 32)
        elif kind == "u64":
            add_integer(int(value), 64)
        elif kind == "f32":
            add_integer(_f32_bits(value), 32)
        else:
            _fail(f"unknown native fingerprint kind: {kind}")
    return "".join(f"{value:016x}" for value in states)


def _static_commitment() -> str:
    return _digest(
        {
            "schema": "rtdl.v4.sphere_static_host_ffi_projection.v1",
            "centers_f32_bits": [
                [_f32_bits(value) for value in center]
                for center in FIXTURE_CENTERS
            ],
            "radii_f32_bits": [_f32_bits(value) for value in FIXTURE_RADII],
            "application_ids_u32": list(range(len(FIXTURE_CENTERS))),
        }
    )


def _query_commitment(queries) -> str:
    return _digest(
        {
            "schema": "rtdl.v4.sphere_query_host_ffi_projection.v1",
            "segments_f32_bits": [
                [_f32_bits(value) for value in row]
                for row in _normalized_query_rows(queries)
            ],
        }
    )


def _static_native_fingerprint() -> str:
    columns: list[tuple[str, object]] = [("u64", len(FIXTURE_CENTERS))]
    for index, (center, radius) in enumerate(
        zip(FIXTURE_CENTERS, FIXTURE_RADII, strict=True)
    ):
        columns.extend(("f32", value) for value in center)
        columns.append(("f32", radius))
        columns.append(("u32", index))
    return _native_fingerprint(
        "rtdl.v4.native_sphere_static_input.v1", tuple(columns)
    )


def _execution_native_fingerprints(
    counts: tuple[int, ...], queries
) -> dict[str, str]:
    normalized = _normalized_query_rows(queries)
    query_columns: list[tuple[str, object]] = [("u64", len(normalized))]
    for row in normalized:
        query_columns.extend(("f32", value) for value in row)
    raw_outputs = tuple(
        (count & 0xFFFFFFFF, (count >> 32) & 0xFFFFFFFF, 0)
        for count in counts
    )
    output_columns: list[tuple[str, object]] = [("u64", len(raw_outputs))]
    status_columns: list[tuple[str, object]] = [("u64", len(counts))]
    for index, (count, output) in enumerate(
        zip(counts, raw_outputs, strict=True)
    ):
        output_columns.extend(("u32", value) for value in output)
        output_columns.extend(
            (
                ("u32", 0xFFFFFFFF),
                ("u32", 0xFFFFFFFF),
                ("f32", _f32_from_bits(OBSERVED_T_SENTINEL_BITS)),
            )
        )
        invocation_mask = 106 if count else 98
        status_columns.extend(
            (
                ("u32", 0),
                ("u32", 0),
                ("u32", 0),
                ("u32", 0),
                ("u64", index),
                ("u32", 0),
                ("u32", 0),
                ("u32", 0),
                ("u32", invocation_mask),
            )
        )
    counters = (0, len(counts), 0, sum(counts), 0, len(counts), len(counts))
    counter_columns = (("u64", len(counters)),) + tuple(
        ("u64", value) for value in counters
    )
    return {
        "query": _native_fingerprint(
            "rtdl.v4.native_sphere_query.v1", tuple(query_columns)
        ),
        "output": _native_fingerprint(
            "rtdl.v4.native_sphere_output.v1", tuple(output_columns)
        ),
        "status": _native_fingerprint(
            "rtdl.v4.native_sphere_status.v1", tuple(status_columns)
        ),
        "counter": _native_fingerprint(
            "rtdl.v4.native_sphere_counters.v1", counter_columns
        ),
        "raw_output_commitment": _digest(raw_outputs),
    }


def _field_mapping_commitment() -> str:
    return _digest(
        {
            "schema": "rtdl.v4.sphere_any_hit_count_field_mapping.v1",
            "centers": "sphere_centers",
            "radii": "sphere_radii",
            "provider_primitive_ids": "provider_primitive_ids",
            "queries": "motion_segments",
            "outputs": "per_query_counts",
            "status": "device_status",
        }
    )


def _physical_authority(target_sha256: str) -> tuple[str, str]:
    authority_nonce = _digest(
        {
            "kind": "builtin_sphere_any_hit_count_physical_authority_v1",
            "callback": CALLBACK_IR_SHA256,
            "effect": CALLBACK_EFFECT_SHA256,
            "schema": PHYSICAL_SCHEMA_SHA256,
            "target": target_sha256,
        }
    )
    plan_sha256 = _digest(
        {
            "schema_sha256": PHYSICAL_SCHEMA_SHA256,
            "callback_ir_sha256": CALLBACK_IR_SHA256,
            "effect_digest": CALLBACK_EFFECT_SHA256,
            "target_sha256": target_sha256,
            "authority_nonce": authority_nonce,
            "template_id": PHYSICAL_TEMPLATE_ID,
            "executable": False,
        }
    )
    return authority_nonce, plan_sha256


def _sha(value: object, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        _fail(f"{label} is not lowercase SHA-256")
    return value


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail(f"{label} is not a mapping")
    return value


def _integer(value: object, label: str, *, bits: int = 64) -> int:
    if type(value) is not int or not 0 <= value < 1 << bits:
        _fail(f"{label} is not u{bits}")
    return value


def _sealed_document_sha256(
    document: Mapping[str, object], field: str, domain: str
) -> str:
    payload = dict(document)
    payload[field] = ""
    return hashlib.sha256(
        domain.encode("ascii") + b"\0" + _canonical_bytes(payload)
    ).hexdigest()


def _native_build_seal(document: Mapping[str, object]) -> str:
    payload = dict(document)
    payload["result_sha256"] = ""
    return hashlib.sha256(
        NATIVE_BUILD_RESULT_DOMAIN.encode("ascii")
        + b"\0"
        + _canonical_bytes(payload)
    ).hexdigest()


def _git_blob(commit: str, relative: str, *, root: Path) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        _fail(
            f"cannot read {relative} from {commit}: "
            f"{completed.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return completed.stdout


def _json_git_blob(commit: str, relative: str, *, root: Path) -> dict[str, object]:
    try:
        value = json.loads(_git_blob(commit, relative, root=root))
    except json.JSONDecodeError as exc:
        raise Goal5838ExamVerificationError(
            f"invalid JSON at {commit}:{relative}"
        ) from exc
    if not isinstance(value, dict):
        _fail(f"JSON root at {commit}:{relative} is not an object")
    return value


def _physical_program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _native_audit_mix_u64(state: int, value: int) -> int:
    mask = (1 << 64) - 1
    state &= mask
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value ^= value >> 31
    value &= mask
    return (
        state
        ^ (
            value
            + 0x9E3779B97F4A7C15
            + ((state << 6) & mask)
            + (state >> 2)
        )
    ) & mask


def _verify_authorities(commit: str, artifact: Mapping[str, object], *, root: Path) -> None:
    selection_bytes = _git_blob(commit, SELECTION_PATH, root=root)
    if _sha256_bytes(selection_bytes) != SELECTION_FILE_SHA256:
        _fail("selection file bytes differ from the independently selected record")
    selection = _json_git_blob(commit, SELECTION_PATH, root=root)
    if (
        selection.get("selection_result_sha256") != SELECTION_RESULT_SHA256
        or _sealed_document_sha256(
            selection,
            "selection_result_sha256",
            "rtdl.goal5838.challenge_selection_result.v1",
        )
        != SELECTION_RESULT_SHA256
    ):
        _fail("selection result seal differs")
    table = _json_git_blob(commit, TABLE_PATH, root=root)
    if (
        table.get("challenge_table_sha256") != CHALLENGE_TABLE_SHA256
        or _sealed_document_sha256(
            table,
            "challenge_table_sha256",
            "rtdl.goal5838.prospective_challenge_table.v1",
        )
        != CHALLENGE_TABLE_SHA256
    ):
        _fail("challenge table seal differs")
    candidates = table.get("eligible_candidates")
    if not isinstance(candidates, list) or len(candidates) != 10:
        _fail("challenge table candidate cardinality differs")
    if selection.get("selected_candidate") != candidates[3]:
        _fail("selection is not exact challenge-table row 3")
    selected = _mapping(selection.get("selected_candidate"), "selected candidate")
    target_pulse = _mapping(selection.get("target_pulse"), "target pulse")
    if (
        selected.get("candidate_id") != SELECTED_CANDIDATE_ID
        or selected.get("metadata_channels") != []
        or selected.get("true_gpu_receipt_required") is not True
        or target_pulse.get("local_random_value") != TARGET_LOCAL_RANDOM_VALUE
        or target_pulse.get("signature_verified") is not True
        or selection.get("activity_at_selection")
        != {
            "candidate_execution_count": 0,
            "candidate_implementation_count": 0,
            "gpu_receipt_count": 0,
            "prospective_success_count": 0,
        }
    ):
        _fail("selected challenge contract differs")
    seal = _json_git_blob(commit, SEAL_PATH, root=root)
    if (
        seal.get("seal_sha256") != GENERIC_CORE_SEAL_SHA256
        or _sealed_document_sha256(
            seal,
            "seal_sha256",
            "rtdl.goal5838.generic_core_seal.v1",
        )
        != GENERIC_CORE_SEAL_SHA256
    ):
        _fail("generic-core seal differs")
    expected_core = [
        {"path": path, "bytes": size, "sha256": digest}
        for path, size, digest in CORE_ROWS
    ]
    if seal.get("frozen_core_files") != expected_core:
        _fail("generic-core sealed file inventory differs")
    frozen = _mapping(artifact.get("frozen_core"), "artifact frozen_core")
    if (
        frozen.get("generic_core_seal_sha256") != GENERIC_CORE_SEAL_SHA256
        or frozen.get("changed_file_count") != 0
        or frozen.get("files") != expected_core
    ):
        _fail("artifact frozen-core record differs")
    for path, size, digest in CORE_ROWS:
        payload = _git_blob(commit, path, root=root)
        if len(payload) != size or _sha256_bytes(payload) != digest:
            _fail(f"frozen core differs at committed path {path}")


def _verify_repository(artifact: Mapping[str, object], *, root: Path) -> str:
    repository = _mapping(artifact.get("repository"), "repository")
    expected_keys = {
        "expected_commit",
        "head_commit",
        "branch",
        "origin_url",
        "clean_before_execution",
        "tracked_source_files",
        "head_after_execution",
        "clean_after_execution",
    }
    if set(repository) != expected_keys:
        _fail("repository custody field set differs")
    commit = repository.get("head_commit")
    _sha(commit, "repository commit")
    if (
        repository.get("expected_commit") != commit
        or repository.get("clean_before_execution") is not True
        or repository.get("head_after_execution") != commit
        or repository.get("clean_after_execution") is not True
        or not isinstance(repository.get("branch"), str)
        or not repository.get("branch")
        or not isinstance(repository.get("origin_url"), str)
        or not repository.get("origin_url")
    ):
        _fail("repository custody values differ")
    rows = repository.get("tracked_source_files")
    if not isinstance(rows, list) or len(rows) != len(EXAM_SOURCE_PATHS):
        _fail("tracked source inventory cardinality differs")
    if [row.get("path") for row in rows if isinstance(row, dict)] != list(
        EXAM_SOURCE_PATHS
    ):
        _fail("tracked source inventory path order differs")
    for row, relative in zip(rows, EXAM_SOURCE_PATHS, strict=True):
        row = _mapping(row, f"source row {relative}")
        if set(row) != {"path", "bytes", "sha256"}:
            _fail(f"source row field set differs: {relative}")
        payload = _git_blob(commit, relative, root=root)
        if (
            row.get("path") != relative
            or row.get("bytes") != len(payload)
            or row.get("sha256") != _sha256_bytes(payload)
        ):
            _fail(f"source row differs from committed bytes: {relative}")
    return commit


def _verify_executable_identity(
    generic: Mapping[str, object], target: Mapping[str, object]
) -> Mapping[str, object]:
    if (
        generic.get("classification") != "prospective_selected_extension"
        or generic.get("plan_sha256") != PLAN_SHA256
        or generic.get("provider_descriptor_sha256")
        != PROVIDER_DESCRIPTOR_SHA256
        or generic.get("provider_projection_sha256")
        != PROVIDER_PROJECTION_SHA256
    ):
        _fail("generic family identity differs")
    identity = _mapping(
        generic.get("executable_identity"), "generic executable identity"
    )
    expected_keys = {
        "schema",
        "provider_descriptor_sha256",
        "provider_projection_sha256",
        "plan_sha256",
        "target_sha256",
        "executable_sha256",
        "provider_artifact_sha256",
        "generated_artifact_sha256",
        "identity_sha256",
    }
    if set(identity) != expected_keys:
        _fail("generic executable identity field set differs")
    body = dict(identity)
    claimed = body.pop("identity_sha256", None)
    for key in expected_keys - {"schema"}:
        _sha(identity.get(key), f"executable identity {key}")
    if (
        identity.get("schema") != "rtdl.family_executable_identity.v1"
        or claimed != _digest(body)
        or identity.get("provider_descriptor_sha256")
        != PROVIDER_DESCRIPTOR_SHA256
        or identity.get("provider_projection_sha256")
        != PROVIDER_PROJECTION_SHA256
        or identity.get("plan_sha256") != PLAN_SHA256
        or identity.get("target_sha256") != target.get("profile_sha256")
        or identity.get("provider_artifact_sha256")
        != target.get("native_library_sha256")
    ):
        _fail("generic executable identity does not rederive")
    return identity


def _verify_traversal_receipt(
    receipt_value: object,
    *,
    counts: tuple[int, ...],
    queries,
    output_sha256: str,
    target: Mapping[str, object],
    identity: Mapping[str, object],
) -> None:
    receipt = dict(_mapping(receipt_value, "traversal receipt"))
    expected_counters = [0, len(counts), 0, sum(counts), 0, len(counts), len(counts)]
    if (
        receipt.pop("selected_topology", None) != SELECTED_CANDIDATE_ID
        or receipt.pop("role_counters", None) != expected_counters
    ):
        _fail("selected topology or role counters differ")
    physical = _mapping(
        receipt.pop("physical_receipt", None), "physical receipt"
    )
    if set(physical) != PHYSICAL_RECEIPT_FIELDS:
        _fail("physical receipt field set differs")
    expected_receipt_keys = {
        "schema",
        "provider_library",
        "provider_library_path",
        "provider_library_sha256",
        "route_identity",
        "semantic_digest",
        "output_digest",
        "nonce",
        "physical_executor_classification",
        "expected_program_bundles",
        "expected_program_bundle_ids",
        "expected_program_observed_at_receipt_edge",
        "native_snapshot",
        "claim_rules",
        "receipt_sha256",
    }
    if set(receipt) != expected_receipt_keys:
        _fail("base traversal receipt field set differs")
    receipt_body = dict(receipt)
    receipt_sha256 = receipt_body.pop("receipt_sha256", None)
    bundle_id = _physical_program_bundle_id(PROGRAM_BUNDLE)
    nonce = _mapping(receipt.get("nonce"), "traversal nonce")
    snapshot = _mapping(receipt.get("native_snapshot"), "native snapshot")
    rules = {
        "provider_name_alone_proves_traversal": False,
        "selected_template_alone_proves_traversal": False,
        "successful_optix_launch_required": True,
        "nonzero_traversable_binding_required": True,
        "program_bundle_binding_required": True,
        "output_digest_bound": True,
    }
    if (
        receipt.get("schema")
        != "rtdl.physical_execution.traversal_receipt.v1"
        or receipt.get("provider_library") != "librtdl_optix"
        or receipt.get("provider_library_path")
        != target.get("native_library_path")
        or receipt.get("provider_library_sha256")
        != target.get("native_library_sha256")
        or receipt.get("route_identity") != ROUTE_IDENTITY
        or _sha(receipt.get("semantic_digest"), "semantic digest")
        != receipt.get("semantic_digest")
        or receipt.get("output_digest") != output_sha256
        or receipt.get("physical_executor_classification")
        != "optix_traversal_observed"
        or receipt.get("expected_program_bundles") != [PROGRAM_BUNDLE]
        or receipt.get("expected_program_bundle_ids") != [bundle_id]
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
        or receipt.get("claim_rules") != rules
        or receipt_sha256 != _digest(receipt_body)
    ):
        _fail("traversal receipt envelope differs")
    if set(nonce) != {"hi", "lo"}:
        _fail("traversal nonce field set differs")
    nonce_hi = _integer(nonce.get("hi"), "nonce.hi")
    nonce_lo = _integer(nonce.get("lo"), "nonce.lo")
    if (nonce_hi, nonce_lo) == (0, 0) or set(snapshot) != SNAPSHOT_FIELDS:
        _fail("native snapshot identity differs")
    for key, value in snapshot.items():
        if key == "incomplete_callsite_lines":
            if (
                not isinstance(value, list)
                or len(value) != 32
                or any(_integer(item, f"{key} item", bits=32) for item in value)
            ):
                _fail("native incomplete callsite lines differ")
        else:
            _integer(value, f"native snapshot {key}")
    if (
        snapshot.get("nonce_hi") != nonce_hi
        or snapshot.get("nonce_lo") != nonce_lo
        or snapshot.get("attempted_launch_count") != 1
        or snapshot.get("successful_launch_count") != 1
        or snapshot.get("failed_launch_count") != 0
        or snapshot.get("complete_context_launch_count") != 1
        or snapshot.get("incomplete_context_launch_count") != 0
        or snapshot.get("context_bind_count") != 1
        or snapshot.get("raygen_invocation_count") != len(counts)
        or snapshot.get("pending_context_at_finish") != 0
        or snapshot.get("session_error") != 0
        or snapshot.get("incomplete_callsite_record_count") != 0
        or any(snapshot.get("incomplete_callsite_lines", []))
        or snapshot.get("first_program_bundle_id") != bundle_id
        or snapshot.get("last_program_bundle_id") != bundle_id
        or snapshot.get("first_traversable") == 0
        or snapshot.get("first_traversable") != snapshot.get("last_traversable")
        or snapshot.get("program_bundle_mix")
        != _native_audit_mix_u64(0, bundle_id)
        or snapshot.get("traversable_mix")
        != _native_audit_mix_u64(0, snapshot["first_traversable"])
        or any(
            snapshot.get(key) == 0
            for key in ("pipeline_mix", "sbt_mix", "stream_mix", "params_mix", "callsite_mix")
        )
    ):
        _fail("native traversal observation differs")
    descriptor = _mapping(physical.get("native_descriptor"), "native descriptor")
    if set(descriptor) != NATIVE_DESCRIPTOR_FIELDS:
        _fail("native built-in-sphere descriptor field set differs")
    target_sha256 = _sha(target.get("profile_sha256"), "target profile")
    authority_nonce, physical_plan_sha256 = _physical_authority(target_sha256)
    query_commitment = _query_commitment(queries)
    fingerprints = _execution_native_fingerprints(counts, queries)
    expected_physical = {
        "schema": "rtdl.v4.sphere_any_hit_count_physical_receipt.v1",
        "build_input_type_name": "OPTIX_BUILD_INPUT_TYPE_SPHERES",
        "primitive_type_name": "OPTIX_PRIMITIVE_TYPE_SPHERE",
        "builtin_is_api_name": "optixBuiltinISModuleGet",
        "geometry_flags_name": "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL",
        "continuation_name": "optixIgnoreIntersection",
        "result_semantics": "per_query_u64_intersected_primitive_count",
        "provider_private_primitive_ids": True,
        "metadata_channels": [],
        "native_library_sha256": target.get("native_library_sha256"),
        "loaded_native_library_path": target.get("native_library_path"),
        "composed_ptx_sha256": identity.get("generated_artifact_sha256"),
        "authority_nonce": authority_nonce,
        "field_mapping_commitment_sha256": _field_mapping_commitment(),
        "static_input_commitment_sha256": _static_commitment(),
        "status_before_output": True,
        "numeric_policy": (
            "binary32_projection__disc_ratio_ge_2^-12__"
            "exact_tangent_prelaunch_reject__front_entry_endpoint_margin_2^-12__"
            "nonexact_toi_ulp_le_4_v3"
        ),
        "discriminant_guard_binary32_unit_roundoffs": 4096,
        "nonexact_toi_ulp_bound": 4,
        "query_commitment_sha256": query_commitment,
        "output_commitment_sha256": output_sha256,
        "raw_output_commitment_sha256": fingerprints[
            "raw_output_commitment"
        ],
        "role_counters": expected_counters,
    }
    for key, expected in expected_physical.items():
        if physical.get(key) != expected:
            _fail(f"physical receipt differs at {key}")
    expected_semantic_digest = _digest(
        {
            "authority": authority_nonce,
            "plan": physical_plan_sha256,
            "abi": CALLBACK_ABI_SHA256,
            "ptx": identity.get("generated_artifact_sha256"),
            "native": target.get("native_library_sha256"),
            "descriptor": descriptor,
            "query": query_commitment,
        }
    )
    if receipt.get("semantic_digest") != expected_semantic_digest:
        _fail("traversal semantic digest does not rederive")
    compute = str(target.get("compute_capability")).split(".")
    if len(compute) != 2 or any(not item.isdecimal() for item in compute):
        _fail("target compute capability differs")
    compute_major, compute_minor = (int(item) for item in compute)
    static_fingerprint = _static_native_fingerprint()
    if (
        descriptor.get("schema")
        != "rtdl.v4.native_builtin_sphere_descriptor.v2"
        or descriptor.get("build_input_type") != 0x2146
        or descriptor.get("primitive_type") != 0x2506
        or descriptor.get("primitive_type_flags") != 1 << 6
        or descriptor.get("builtin_is_build_flags") != 1 << 2
        or descriptor.get("build_flags") != 1 << 2
        or descriptor.get("geometry_flags") != 1 << 1
        or descriptor.get("builtin_is_module") is not True
        or descriptor.get("user_intersection_program") is not False
        or descriptor.get("uses_motion_blur") is not False
        or descriptor.get("center_stride_bytes") != 12
        or descriptor.get("radius_stride_bytes") != 4
        or descriptor.get("single_radius") is not False
        or descriptor.get("primitive_index_offset") != 0
        or descriptor.get("sbt_record_count") != 1
        or descriptor.get("gas_count") != 1
        or descriptor.get("primitive_count") != 6
        or descriptor.get("motion_key_count") != 0
        or descriptor.get("traversable_graph_flags") != 1
        or descriptor.get("max_payload_values") != 8
        or descriptor.get("max_attribute_values") != 0
        or descriptor.get("max_trace_depth") != 1
        or descriptor.get("program_group_count") != 3
        or descriptor.get("compiled_optix_version") != 90000
        or descriptor.get("compiled_optix_major") != 9
        or descriptor.get("compiled_optix_minor") != 0
        or descriptor.get("compiled_optix_patch") != 0
        or type(descriptor.get("cuda_device_ordinal")) is not int
        or descriptor.get("cuda_device_ordinal") < 0
        or descriptor.get("cuda_compute_capability_major") != compute_major
        or descriptor.get("cuda_compute_capability_minor") != compute_minor
        or type(descriptor.get("cuda_driver_version")) is not int
        or descriptor.get("cuda_driver_version") <= 0
        or descriptor.get("static_input_fingerprint") != static_fingerprint
        or descriptor.get("device_static_input_fingerprint")
        != static_fingerprint
        or any(
            type(descriptor.get(key)) is not int or descriptor.get(key) <= 0
            for key in (
                "center_device_pointer",
                "radius_device_pointer",
                "application_id_device_pointer",
            )
        )
        or descriptor.get("last_execution_present") is not True
        or descriptor.get("last_status_failed") is not False
        or descriptor.get("last_query_count") != len(counts)
        or descriptor.get("last_status_d2h_call_count") != 1
        or descriptor.get("last_application_output_d2h_call_count") != 6
        or descriptor.get("last_output_after_status_failure_count") != 0
        or descriptor.get("last_query_device_pointer_nonzero_count") != 6
        or descriptor.get("last_output_device_pointer_nonzero_count") != 8
        or descriptor.get("traversable_identity")
        != snapshot.get("first_traversable")
        or descriptor.get("last_query_fingerprint") != fingerprints["query"]
        or descriptor.get("last_device_query_fingerprint")
        != fingerprints["query"]
        or descriptor.get("last_output_fingerprint")
        != fingerprints["output"]
        or descriptor.get("last_status_fingerprint")
        != fingerprints["status"]
        or descriptor.get("last_counter_fingerprint")
        != fingerprints["counter"]
    ):
        _fail("native built-in-sphere descriptor differs")
    for key in (
        "last_query_device_pointer_fingerprint",
        "last_output_device_pointer_fingerprint",
    ):
        value = _sha(descriptor.get(key), f"native descriptor {key}")
        if value == "0" * 64:
            _fail(f"native descriptor {key} is zero")


def _verify_native_build(
    value: object,
    *,
    commit: str,
    target: Mapping[str, object],
    root: Path,
) -> None:
    manifest = _mapping(value, "native build manifest")
    expected_manifest_keys = {
        "schema",
        "status",
        "repository",
        "build_input",
        "build_input_sha256",
        "executed_command",
        "executed_command_display",
        "reproduction_command",
        "reproduction_command_display",
        "build_log",
        "native_output",
        "required_symbols",
        "required_symbol_check",
        "all_required_symbols_exported",
        "dynamic_dependencies",
        "result_sha256",
    }
    if set(manifest) != expected_manifest_keys:
        _fail("native build manifest field set differs")
    if (
        manifest.get("schema") != NATIVE_BUILD_RESULT_DOMAIN
        or manifest.get("status")
        != "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        or manifest.get("result_sha256") != _native_build_seal(manifest)
        or manifest.get("required_symbols")
        != list(NATIVE_BUILD_REQUIRED_SYMBOLS)
        or manifest.get("required_symbol_check")
        != "exact_nm_dynamic_defined_name"
        or manifest.get("all_required_symbols_exported") is not True
        or not isinstance(manifest.get("dynamic_dependencies"), str)
    ):
        _fail("native build manifest envelope differs")

    repository = _mapping(
        manifest.get("repository"), "native build repository"
    )
    if set(repository) != {
        "expected_commit",
        "head_before",
        "branch",
        "origin_url",
        "clean_before",
        "source_files",
        "head_after",
        "clean_after",
    }:
        _fail("native build repository field set differs")
    if (
        repository.get("expected_commit") != commit
        or repository.get("head_before") != commit
        or repository.get("head_after") != commit
        or repository.get("clean_before") is not True
        or repository.get("clean_after") is not True
        or not isinstance(repository.get("branch"), str)
        or not repository.get("branch")
        or not isinstance(repository.get("origin_url"), str)
        or not repository.get("origin_url")
    ):
        _fail("native build repository identity differs")
    source_rows = repository.get("source_files")
    if (
        not isinstance(source_rows, list)
        or len(source_rows) != len(NATIVE_BUILD_SOURCE_PATHS)
    ):
        _fail("native build source inventory cardinality differs")
    for row_value, relative in zip(
        source_rows, NATIVE_BUILD_SOURCE_PATHS, strict=True
    ):
        row = _mapping(row_value, f"native build source {relative}")
        payload = _git_blob(commit, relative, root=root)
        if (
            set(row) != {"path", "bytes", "sha256"}
            or row.get("path") != relative
            or row.get("bytes") != len(payload)
            or row.get("sha256") != _sha256_bytes(payload)
        ):
            _fail(f"native build source identity differs: {relative}")

    build_input = _mapping(manifest.get("build_input"), "native build input")
    expected_input_keys = {
        "schema",
        "translation_units",
        "builder_path",
        "builder_sha256",
        "cuda_prefix",
        "cuda_include",
        "cuda_system_include",
        "nvcc_path",
        "nvcc_sha256",
        "nvcc_version",
        "host_compiler_path",
        "host_compiler_sha256",
        "host_compiler_version",
        "optix_prefix",
        "optix_include",
        "optix_version",
        "expected_optix_sdk",
        "key_headers",
        "compute_capability",
        "gpu",
        "language_standard",
        "optimization",
        "position_independent_code",
        "geos_mode",
        "geos_cflags",
        "geos_libraries",
        "library_dirs",
    }
    if set(build_input) != expected_input_keys:
        _fail("native build input field set differs")
    build_input_sha256 = _sha(
        manifest.get("build_input_sha256"), "native build input"
    )
    first_source = _mapping(source_rows[0], "native builder source")
    if (
        build_input_sha256 != _digest(build_input)
        or build_input.get("schema")
        != "rtdl.goal5838.selected_sphere_optix_build_input.v1"
        or build_input.get("translation_units")
        != list(NATIVE_BUILD_TRANSLATION_UNITS)
        or build_input.get("builder_path") != NATIVE_BUILD_SOURCE_PATHS[0]
        or build_input.get("builder_sha256") != first_source.get("sha256")
        or build_input.get("optix_version") != 90000
        or build_input.get("expected_optix_sdk") != "9.0.0"
        or build_input.get("compute_capability")
        != target.get("compute_capability")
        or build_input.get("language_standard") != "c++17"
        or build_input.get("optimization") != "O3"
        or build_input.get("position_independent_code") is not True
    ):
        _fail("native build input identity differs")
    required_strings = (
        "cuda_prefix",
        "cuda_include",
        "nvcc_path",
        "nvcc_version",
        "host_compiler_path",
        "host_compiler_version",
        "optix_prefix",
        "optix_include",
        "geos_mode",
    )
    if any(
        not isinstance(build_input.get(key), str) or not build_input.get(key)
        for key in required_strings
    ):
        _fail("native build path or tool version is absent")
    _sha(build_input.get("nvcc_sha256"), "native build nvcc")
    _sha(build_input.get("host_compiler_sha256"), "native build host compiler")
    if not isinstance(build_input.get("cuda_system_include"), str):
        _fail("native build CUDA system include differs")
    for key in ("geos_cflags", "geos_libraries", "library_dirs"):
        values = build_input.get(key)
        if (
            not isinstance(values, list)
            or any(not isinstance(item, str) or not item for item in values)
        ):
            _fail(f"native build {key} differs")
    headers = build_input.get("key_headers")
    expected_header_names = (
        "optix.h",
        "optix_device.h",
        "optix_function_table_definition.h",
        "optix_stack_size.h",
        "optix_stubs.h",
        "cuda.h",
        "cuda_runtime.h",
        "nvrtc.h",
    )
    if not isinstance(headers, list) or len(headers) != len(expected_header_names):
        _fail("native build key-header inventory differs")
    for row_value, name in zip(headers, expected_header_names, strict=True):
        row = _mapping(row_value, f"native build header {name}")
        if (
            set(row) != {"name", "path", "bytes", "sha256"}
            or row.get("name") != name
            or not isinstance(row.get("path"), str)
            or not row.get("path")
            or type(row.get("bytes")) is not int
            or row.get("bytes") <= 0
        ):
            _fail(f"native build header identity differs: {name}")
        _sha(row.get("sha256"), f"native build header {name}")
    build_gpu = _mapping(build_input.get("gpu"), "native build GPU")
    target_gpu = _mapping(target.get("gpu"), "target GPU")
    if (
        set(build_gpu)
        != {"name", "uuid", "driver_version", "compute_capability"}
        or any(
            build_gpu.get(key) != target_gpu.get(key)
            for key in build_gpu
        )
    ):
        _fail("native build and execution GPU identities differ")

    native_output = _mapping(
        manifest.get("native_output"), "native build output"
    )
    if (
        set(native_output) != {"path", "bytes", "sha256"}
        or native_output.get("path") != target.get("native_library_path")
        or native_output.get("bytes") != target.get("native_library_bytes")
        or native_output.get("sha256") != target.get("native_library_sha256")
    ):
        _fail("native build output differs from executed provider")
    build_log = _mapping(manifest.get("build_log"), "native build log")
    if (
        set(build_log) != {"path", "bytes", "sha256"}
        or not isinstance(build_log.get("path"), str)
        or not build_log.get("path")
        or type(build_log.get("bytes")) is not int
        or build_log.get("bytes") < 0
    ):
        _fail("native build log identity differs")
    _sha(build_log.get("sha256"), "native build log")

    command = manifest.get("executed_command")
    reproduction = manifest.get("reproduction_command")
    if (
        not isinstance(command, list)
        or not isinstance(reproduction, list)
        or any(not isinstance(item, str) or not item for item in command)
        or any(not isinstance(item, str) or not item for item in reproduction)
        or len(command) < 20
        or len(command) != len(reproduction)
        or command[-2] != "-o"
        or reproduction[-2] != "-o"
    ):
        _fail("native build command shape differs")
    first_unit = NATIVE_BUILD_TRANSLATION_UNITS[0]
    unit_matches = [
        item for item in command if item.endswith("/" + first_unit)
    ]
    if len(unit_matches) != 1:
        _fail("native build source root cannot be recovered")
    source_root = unit_matches[0][: -len(first_unit)].rstrip("/")
    expected_command = [
        str(build_input["nvcc_path"]),
        "-ccbin",
        str(build_input["host_compiler_path"]),
        "-std=c++17",
        "-O3",
        "-shared",
        f"-I{build_input['optix_include']}",
        f"-I{build_input['cuda_include']}",
        *build_input["geos_cflags"],
        f'-DRTDL_OPTIX_INCLUDE_DIR="{build_input["optix_include"]}"',
        f'-DRTDL_CUDA_INCLUDE_DIR="{build_input["cuda_include"]}"',
        (
            '-DRTDL_CUDA_SYSTEM_INCLUDE_DIR="'
            + str(build_input["cuda_system_include"])
            + '"'
        ),
        f'-DRTDL_OPTIX_BUILD_ID="{build_input_sha256}"',
        "-arch=sm_"
        + str(build_input["compute_capability"]).replace(".", ""),
        "-Xcompiler",
        "-fPIC",
        *(
            str(Path(source_root) / relative)
            for relative in NATIVE_BUILD_TRANSLATION_UNITS
        ),
        *(f"-L{path}" for path in build_input["library_dirs"]),
        "-lcuda",
        "-lnvrtc",
        *build_input["geos_libraries"],
        "-o",
        command[-1],
    ]
    expected_reproduction = [*expected_command[:-1], str(native_output["path"])]
    if (
        command != expected_command
        or reproduction != expected_reproduction
        or manifest.get("executed_command_display") != shlex.join(command)
        or manifest.get("reproduction_command_display")
        != shlex.join(reproduction)
    ):
        _fail("native build command does not rederive")


def verify_artifact(
    artifact: Mapping[str, object],
    *,
    root: Path = ROOT,
    native_path: Path | None = None,
) -> dict[str, object]:
    expected_top_level = {
        "schema",
        "status",
        "claim_boundary",
        "selection",
        "repository",
        "frozen_core",
        "native_build",
        "target",
        "toolchain",
        "generic_family",
        "fixture",
        "executions",
        "lifecycle",
        "summary",
        "result_sha256",
    }
    if set(artifact) != expected_top_level:
        _fail("artifact top-level field set differs")
    body = dict(artifact)
    claimed_result_sha256 = body.pop("result_sha256", None)
    if claimed_result_sha256 != _digest(body):
        _fail("artifact result seal differs")
    if (
        artifact.get("schema")
        != "rtdl.goal5838.selected_sphere_gpu_exam.v1"
        or artifact.get("status")
        != "PASS__BOUNDED_PROSPECTIVE_FROZEN_CORE_TOPOLOGY"
        or artifact.get("claim_boundary")
        != {
            "one_bounded_prospective_result": True,
            "arbitrary_callback_ir_gpu_execution": False,
            "universal_provider_portability": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        }
    ):
        _fail("artifact claim boundary differs")
    commit = _verify_repository(artifact, root=root)
    _verify_authorities(commit, artifact, root=root)
    selection = _mapping(artifact.get("selection"), "artifact selection")
    if (
        selection.get("candidate_id") != SELECTED_CANDIDATE_ID
        or selection.get("selection_result_sha256")
        != SELECTION_RESULT_SHA256
        or selection.get("selection_file_sha256") != SELECTION_FILE_SHA256
        or selection.get("selected_index") != 3
        or selection.get("target_pulse_index") != 1_924_176
        or selection.get("target_local_random_value")
        != TARGET_LOCAL_RANDOM_VALUE
    ):
        _fail("artifact selection binding differs")
    target = _mapping(artifact.get("target"), "target")
    if set(target) != {
        "profile_sha256",
        "native_library_path",
        "native_library_sha256",
        "native_library_bytes",
        "optix_sdk",
        "compute_capability",
        "gpu",
    }:
        _fail("target field set differs")
    native_sha256 = _sha(
        target.get("native_library_sha256"), "target native library"
    )
    if (
        not isinstance(target.get("native_library_path"), str)
        or not target.get("native_library_path")
        or type(target.get("native_library_bytes")) is not int
        or target.get("native_library_bytes") <= 0
        or target.get("optix_sdk") != "9.0.0"
        or not isinstance(target.get("compute_capability"), str)
        or not isinstance(target.get("gpu"), dict)
    ):
        _fail("target identity differs")
    expected_target_sha256 = _digest(
        {
            "provider": "optix",
            "optix_sdk": target.get("optix_sdk"),
            "compute_capability": target.get("compute_capability"),
            "native_sha256": native_sha256,
            "supports_builtin_sphere": True,
            "max_graph_depth": 1,
        }
    )
    if target.get("profile_sha256") != expected_target_sha256:
        _fail("target profile identity does not rederive")
    gpu = _mapping(target.get("gpu"), "target GPU")
    if (
        set(gpu)
        != {
            "name",
            "uuid",
            "driver_version",
            "pci_bus_id",
            "compute_capability",
            "memory_mib",
        }
        or gpu.get("compute_capability") != target.get("compute_capability")
        or any(not isinstance(gpu.get(key), str) or not gpu.get(key) for key in gpu)
    ):
        _fail("GPU identity differs from target authority")
    native_verified = False
    candidate_native = native_path
    if candidate_native is None:
        recorded = Path(str(target["native_library_path"]))
        if recorded.is_file():
            candidate_native = recorded
    if candidate_native is not None:
        native_bytes = candidate_native.resolve(strict=True).read_bytes()
        if (
            len(native_bytes) != target.get("native_library_bytes")
            or _sha256_bytes(native_bytes) != native_sha256
        ):
            _fail("provided native library differs from executed bytes")
        native_verified = True
    _verify_native_build(
        artifact.get("native_build"), commit=commit, target=target, root=root
    )
    generic = _mapping(artifact.get("generic_family"), "generic family")
    if set(generic) != {
        "classification",
        "plan_sha256",
        "provider_descriptor_sha256",
        "provider_projection_sha256",
        "executable_identity",
    }:
        _fail("generic family field set differs")
    identity = _verify_executable_identity(generic, target)
    toolchain = _mapping(artifact.get("toolchain"), "toolchain")
    if (
        set(toolchain)
        != {
            "python",
            "python_executable",
            "numba",
            "numpy",
            "optix_include",
            "cuda_include",
        }
        or any(not isinstance(value, str) or not value for value in toolchain.values())
    ):
        _fail("toolchain identity differs")
    fixture = _mapping(artifact.get("fixture"), "fixture")
    independently_fixed_fixture_sha256 = _digest(
        {
            "centers": FIXTURE_CENTERS,
            "radii": FIXTURE_RADII,
            "queries": FIXTURE_QUERIES,
            "case_names": EXPECTED_CASE_NAMES,
        }
    )
    if fixture != {
        "case_names": list(EXPECTED_CASE_NAMES),
        "primitive_count": 6,
        "query_count": 6,
        "expected_counts": list(EXPECTED_COUNTS),
        "fixture_sha256": independently_fixed_fixture_sha256,
        "oracle_sha256": ORACLE_SHA256,
    } or independently_fixed_fixture_sha256 != FIXTURE_SHA256:
        _fail("fixture or independent-oracle identity differs")
    executions = artifact.get("executions")
    expected_rows = (
        ("primary", EXPECTED_COUNTS, FIXTURE_QUERIES),
        (
            "reverse_query_order",
            tuple(reversed(EXPECTED_COUNTS)),
            tuple(reversed(FIXTURE_QUERIES)),
        ),
    )
    if not isinstance(executions, list) or len(executions) != 2:
        _fail("execution cardinality differs")
    for row_value, (label, counts, queries) in zip(
        executions, expected_rows, strict=True
    ):
        row = _mapping(row_value, f"execution {label}")
        if set(row) != {
            "label",
            "observed_counts",
            "output_sha256",
            "oracle_exact_match",
            "traversal_receipt",
        }:
            _fail(f"execution field set differs: {label}")
        output = {
            "schema": "rtdl.v4.sphere_any_hit_count_output.v1",
            "counts": list(counts),
        }
        output_sha256 = _digest(output)
        if (
            row.get("label") != label
            or row.get("observed_counts") != list(counts)
            or row.get("output_sha256") != output_sha256
            or row.get("oracle_exact_match") is not True
        ):
            _fail(f"execution output differs: {label}")
        _verify_traversal_receipt(
            row.get("traversal_receipt"),
            counts=counts,
            queries=queries,
            output_sha256=output_sha256,
            target=target,
            identity=identity,
        )
    lifecycle = _mapping(artifact.get("lifecycle"), "lifecycle")
    if set(lifecycle) != {
        "before",
        "after_primary",
        "after_reverse",
        "execution_count",
        "closed_idempotently",
    }:
        _fail("lifecycle field set differs")
    lifecycle_rows = (
        ("before", 0),
        ("after_primary", 1),
        ("after_reverse", 2),
    )
    physical_receipt_sha256 = None
    for label, execution_count in lifecycle_rows:
        row = _mapping(lifecycle.get(label), f"lifecycle.{label}")
        if (
            set(row)
            != {
                "schema",
                "process_bound",
                "thread_bound",
                "nonserializable",
                "nonreentrant",
                "execution_count",
                "native_library_sha256",
                "composed_ptx_sha256",
                "physical_receipt_sha256",
            }
            or row.get("schema")
            != "rtdl.v4.prepared_sphere_any_hit_count_owner.v1"
            or row.get("process_bound") is not True
            or row.get("thread_bound") is not True
            or row.get("nonserializable") is not True
            or row.get("nonreentrant") is not True
            or row.get("execution_count") != execution_count
            or row.get("native_library_sha256") != native_sha256
            or row.get("composed_ptx_sha256")
            != identity.get("generated_artifact_sha256")
        ):
            _fail(f"prepared lifecycle receipt differs: {label}")
        _sha(row.get("physical_receipt_sha256"), "physical receipt identity")
        if physical_receipt_sha256 is None:
            physical_receipt_sha256 = row["physical_receipt_sha256"]
        elif row.get("physical_receipt_sha256") != physical_receipt_sha256:
            _fail("prepared physical identity changed across executions")
    if (
        lifecycle.get("execution_count") != 2
        or lifecycle.get("closed_idempotently") is not True
    ):
        _fail("prepared lifecycle progression differs")
    if artifact.get("summary") != {
        "true_optix_launch_count": 2,
        "oracle_case_count": 12,
        "oracle_exact_match_count": 12,
        "frozen_core_changed_file_count": 0,
    }:
        _fail("artifact summary differs")
    return {
        "schema": "rtdl.goal5838.selected_sphere_gpu_exam_verification.v1",
        "status": "PASS__INDEPENDENT_ARTIFACT_REDERIVATION",
        "artifact_result_sha256": claimed_result_sha256,
        "repository_commit": commit,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "source_file_count": len(EXAM_SOURCE_PATHS),
        "frozen_core_changed_file_count": 0,
        "true_optix_launch_count": 2,
        "oracle_exact_match_count": 12,
        "native_library_bytes_reverified": native_verified,
        "performance_claim_authorized": False,
        "external_review_or_consensus_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    artifact_path = args.artifact.resolve(strict=True)
    artifact = json.loads(artifact_path.read_text("utf-8"))
    result = verify_artifact(artifact, native_path=args.native)
    result["artifact_file_sha256"] = _sha256_bytes(artifact_path.read_bytes())
    result["verification_sha256"] = _digest(result)
    if args.output is not None:
        output = _require_external_output(
            args.output, artifact_path=artifact_path
        )
        _write_json_exclusive(output, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
