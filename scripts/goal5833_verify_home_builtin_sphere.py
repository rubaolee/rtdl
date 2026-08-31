#!/usr/bin/env python3
"""Independent stdlib-only recount of Goal5833 Home evidence."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import struct


U32_MAX = 0xFFFFFFFF

# Independent copy of the exact values from the pinned OptiX 9
# ``optix_types.h`` authority.  The recount must reject a receipt that carries
# the right symbolic labels but different native enum/flag numbers.
EXPECTED_OPTIX9_SPHERE_FACTS = {
    "build_input_type": 0x2146,
    "primitive_type": 0x2506,
    "primitive_type_flags": 1 << 6,
    "builtin_is_build_flags": 1 << 2,
    "build_flags": 1 << 2,
    "geometry_flags": 1 << 1,
    "traversable_graph_flags": 1 << 0,
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _field_mapping_commitment() -> str:
    return _canonical_digest({
        "schema": "rtdl.v4.sphere_field_mapping_commitment.v1",
        "centers": "sphere_centers",
        "radii": "sphere_radii",
        "application_ids": "application_ids",
        "queries": "motion_segments",
        "outputs": "first_contacts",
        "status": "device_status",
    })


def _static_input_commitment(centers, radii, application_ids) -> str:
    return _canonical_digest({
        "schema": "rtdl.v4.sphere_static_host_ffi_projection.v1",
        "centers_f32_bits": [[_f32_bits(value) for value in row]
                             for row in centers],
        "radii_f32_bits": [_f32_bits(value) for value in radii],
        "application_ids_u32": [int(value) for value in application_ids],
    })


def _query_commitment(queries) -> str:
    return _canonical_digest({
        "schema": "rtdl.v4.sphere_query_host_ffi_projection.v1",
        "segments_f32_bits": [
            [_f32_bits(value) for value in (*start, *end)]
            for start, end in queries
        ],
    })


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", _f32(value)))[0]


def _native_fingerprint(domain: str, columns) -> str:
    states = [
        14695981039346656037,
        1099511628211 ^ 0x9E3779B97F4A7C15,
        0x6A09E667F3BCC909,
        0xBB67AE8584CAA73B,
    ]
    primes = [1099511628211, 1099511627791, 1099511627689, 1099511627609]
    mask = (1 << 64) - 1

    def add_byte(value):
        for index in range(4):
            states[index] ^= int(value) + index * 17
            states[index] = (states[index] * primes[index]) & mask

    def add(value, width):
        for shift in range(0, width, 8):
            add_byte((int(value) >> shift) & 0xFF)

    encoded = domain.encode("ascii")
    add(len(encoded), 64)
    for value in encoded:
        add_byte(value)
    for kind, value in columns:
        if kind == "f32":
            add(_f32_bits(value), 32)
        elif kind == "u32":
            add(value, 32)
        elif kind == "u64":
            add(value, 64)
        else:
            raise RuntimeError(f"unknown native fingerprint type: {kind}")
    return "".join(f"{value:016x}" for value in states)


def _native_static_fingerprint(centers, radii, application_ids):
    columns = [("u64", len(centers))]
    for center, radius, application_id in zip(centers, radii, application_ids):
        columns.extend(("f32", value) for value in center)
        columns.extend((("f32", radius), ("u32", application_id)))
    return _native_fingerprint("rtdl.v4.native_sphere_static_input.v1", columns)


def _native_query_fingerprint(queries):
    columns = [("u64", len(queries))]
    for start, end in queries:
        columns.extend(("f32", value) for value in (*start, *end))
    return _native_fingerprint("rtdl.v4.native_sphere_query.v1", columns)


def _native_output_fingerprint(result):
    outputs = result["observed"]
    primitives = result["observed_primitive_indices_raw"]
    kinds = result["observed_hit_kinds_raw"]
    times = result["observed_t_values_raw"]
    time_bits = result["observed_t_f32_bits_raw"]
    _require(
        len(outputs) == len(primitives) == len(kinds) == len(times)
        == len(time_bits),
             "native output evidence cardinality differs")
    columns = [("u64", len(outputs))]
    for index, output in enumerate(outputs):
        bits = time_bits[index]
        _require(
            isinstance(bits, int) and not isinstance(bits, bool)
            and 0 <= bits <= U32_MAX,
            "raw observed t bits are not u32",
        )
        decoded = struct.unpack("<f", struct.pack("<I", bits))[0]
        if times[index] is None:
            _require(math.isnan(decoded),
                     "null observed t does not bind a NaN f32 payload")
        else:
            _require(_f32_bits(times[index]) == bits,
                     "finite observed t differs from its f32 bits")
        columns.extend(("u32", value) for value in output)
        columns.extend((
            ("u32", primitives[index]), ("u32", kinds[index]),
            ("u32", bits),
        ))
    return _native_fingerprint("rtdl.v4.native_sphere_output.v1", columns)


def _native_status_fingerprint(rows):
    order = (
        "first_error_claimed", "error_code", "stage", "role",
        "launch_index", "error_site", "effect_tag", "nonce_word",
        "invocation_mask",
    )
    columns = [("u64", len(rows))]
    for row in rows:
        columns.extend(
            ("u64" if name == "launch_index" else "u32", row[name])
            for name in order)
    return _native_fingerprint("rtdl.v4.native_sphere_status.v1", columns)


def _native_counter_fingerprint(values):
    return _native_fingerprint(
        "rtdl.v4.native_sphere_counters.v1",
        [("u64", len(values)), *(("u64", value) for value in values)],
    )


def _verify_artifact_set(
    artifact_root: Path, record: dict[str, object],
) -> dict[str, str]:
    subdirectory = record.get("subdirectory")
    _require(isinstance(subdirectory, str) and subdirectory in (
        "accepted", "hostile_zero_tmax"), "artifact subdirectory differs")
    root = (artifact_root / subdirectory).resolve()
    _require(root.parent == artifact_root.resolve() and root.is_dir(),
             "artifact root differs")
    manifest_path = root / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    _require(hashlib.sha256(manifest_bytes).hexdigest()
             == record["manifest_sha256"], "artifact manifest identity differs")
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") == \
            "rtdl.goal5833.generated_executable_artifacts.v2":
        _require(
            manifest.get("compiler_identity") == record.get("compiler_identity"),
            "artifact compiler identity projection differs",
        )
    _require(manifest["executable_sha256"] == record["executable_sha256"],
             "artifact executable identity differs")
    _require(manifest["member_count"] == record["member_count"]
             == len(manifest["members"]), "artifact member count differs")
    _require(manifest["members"] == record["members"],
             "artifact manifest/receipt members differ")
    expected_names = {
        "callback_source.py", "wrapper.cu", "wrapper.ptx", "composed.ptx",
        "nvrtc.log",
        "compiler_options.json",
        "leaf_0_make_ray.py", "leaf_1_closest_hit.py", "leaf_2_miss.py",
        "leaf_3_finalize.py", "leaf_0_make_ray.ptx",
        "leaf_1_closest_hit.ptx", "leaf_2_miss.ptx",
        "leaf_3_finalize.ptx",
    }
    _require({item["path"] for item in manifest["members"]} == expected_names,
             "artifact member names differ")
    member_sha256: dict[str, str] = {}
    for item in manifest["members"]:
        name = item["path"]
        _require(Path(name).name == name, "unsafe artifact member path")
        body = (root / name).read_bytes()
        observed_sha256 = hashlib.sha256(body).hexdigest()
        _require(len(body) == item["size"] and
                 observed_sha256 == item["sha256"],
                 f"artifact member identity differs: {name}")
        member_sha256[name] = observed_sha256
    return member_sha256


def _verify_execution_native_binding(
    execution_path: object,
    traversal: dict[str, object],
    physical: dict[str, object],
    *,
    label: str,
) -> None:
    """Check original-run path consistency without binding preservation path.

    Evidence may be copied to another directory or host.  The preserved native
    is therefore bound by SHA-256 in :func:`verify`; absolute paths remain
    evidence about the original execution and need only agree with each other.
    """

    _require(isinstance(execution_path, str) and bool(execution_path),
             f"{label} original native path is malformed")
    _require(
        traversal.get("provider_library_path") == execution_path
        and physical.get("authorized_native_library_path") == execution_path
        and physical.get("loaded_native_library_path") == execution_path,
        f"{label} original execution native paths differ",
    )


def _verify_artifact_bridges(
    result: dict[str, object],
    hostile: dict[str, object],
    accepted_members: dict[str, str],
    hostile_members: dict[str, str],
) -> None:
    """Bridge preserved source/PTX bytes to the result's scientific ids."""

    _require(
        accepted_members["callback_source.py"] == result["source_sha256"]
        and hostile_members["callback_source.py"] == hostile["source_sha256"],
        "accepted/hostile Callback DSL source bytes differ from result identity",
    )
    _require(
        accepted_members["wrapper.cu"] == result["wrapper_source_sha256"]
        and hostile_members["wrapper.cu"] == hostile["wrapper_source_sha256"],
        "accepted/hostile wrapper source bytes differ from result identity",
    )
    _require(
        accepted_members["composed.ptx"] == result["composed_ptx_sha256"]
        and hostile_members["composed.ptx"] == hostile["composed_ptx_sha256"],
        "accepted/hostile composed PTX bytes differ from result identity",
    )


def _statement_effects(statements: list[dict[str, object]]) -> set[str]:
    effects: set[str] = set()
    for statement in statements:
        kind = statement.get("kind")
        if kind == "return_effect":
            effect = statement.get("effect")
            _require(isinstance(effect, dict) and isinstance(effect.get("kind"), str),
                     "callback effect projection is malformed")
            effects.add(effect["kind"])
        for key in ("body", "then", "else"):
            nested = statement.get(key)
            if nested is not None:
                _require(isinstance(nested, list),
                         "callback statement projection is malformed")
                effects.update(_statement_effects(nested))
    return effects


def _verify_compiler_identity(
    artifact_root: Path,
    record: dict[str, object],
    scientific: dict[str, object],
    member_sha256: dict[str, str],
) -> None:
    """Rebuild the canonical compiler/executable identity from preserved bytes.

    This is intentionally stdlib-only.  It does not import RTDL's compiler or
    trust the top-level identity fields as the source of the recomputation.
    """

    identity = record.get("compiler_identity")
    _require(isinstance(identity, dict) and identity.get("schema") ==
             "rtdl.goal5833.sphere_compiler_identity_projection.v1",
             "compiler identity projection is absent or malformed")
    program = identity["callback_program"]
    verified = identity["verified_callback"]
    schema = identity["physical_schema"]
    target = identity["target"]
    plan = identity["canonical_plan"]
    abi = identity["callback_abi"]
    authority = identity["authority"]
    executable = identity["executable_record"]
    for name, value in (
        ("callback program", program), ("verified callback", verified),
        ("physical schema", schema), ("target", target),
        ("canonical plan", plan), ("callback ABI", abi),
        ("authority", authority), ("executable record", executable),
    ):
        _require(isinstance(value, dict), f"{name} projection is malformed")

    normalized_source = program.get("normalized_source")
    _require(isinstance(normalized_source, str) and
             hashlib.sha256(normalized_source.encode("utf-8")).hexdigest()
             == program.get("source_sha256"),
             "normalized Callback program source identity does not rederive")
    _require(member_sha256["callback_source.py"] == scientific["source_sha256"]
             == identity.get("public_source_sha256"),
             "public Callback DSL source identity does not rederive")
    ir_projection = dict(program)
    ir_projection.pop("normalized_source", None)
    ir_projection.pop("source_sha256", None)
    ir_sha = _canonical_digest(ir_projection)
    _require(ir_sha == verified.get("ir_sha256")
             == scientific["callback_ir_sha256"],
             "Callback IR identity does not rederive")

    functions = program.get("functions")
    _require(isinstance(functions, list), "Callback function projection is malformed")
    effect_projection = []
    for function in functions:
        _require(isinstance(function, dict) and isinstance(function.get("name"), str)
                 and isinstance(function.get("body"), list),
                 "Callback function projection is malformed")
        effect_projection.append([
            function["name"], sorted(_statement_effects(function["body"]))])
    effect_digest = _canonical_digest(effect_projection)
    _require(effect_digest == verified.get("effect_digest")
             == scientific["callback_effect_digest"],
             "Callback effect identity does not rederive")

    schema_sha = _canonical_digest(schema)
    target_sha = _canonical_digest(target)
    _require(schema_sha == scientific["physical_schema_sha256"],
             "physical schema identity does not rederive")
    _require(target_sha == scientific["target_sha256"],
             "target identity does not rederive")
    nonce = _canonical_digest({
        "kind": "builtin_sphere_physical_authority_v1",
        "callback": ir_sha,
        "effect": effect_digest,
        "schema": schema_sha,
        "target": target_sha,
    })
    _require(plan.get("callback_ir_sha256") == ir_sha
             and plan.get("effect_digest") == effect_digest
             and plan.get("schema_sha256") == schema_sha
             and plan.get("target_sha256") == target_sha
             and plan.get("authority_nonce") == nonce
             and _canonical_digest(plan) == scientific["canonical_plan_sha256"],
             "canonical plan identity does not rederive")
    abi_projection = dict(abi)
    abi_sha = abi_projection.pop("abi_sha256", None)
    _require(_canonical_digest(abi_projection) == abi_sha
             == scientific["callback_abi_sha256"],
             "callback ABI identity does not rederive")
    authority_projection = {
        "callback_ir_sha256": ir_sha,
        "callback_effect_digest": effect_digest,
        "schema_sha256": schema_sha,
        "target_sha256": target_sha,
        "authority_nonce": nonce,
    }
    authority_sha = _canonical_digest(authority_projection)
    _require(authority == authority_projection
             and identity.get("authority_sha256") == authority_sha
             == scientific["authority_sha256"],
             "sphere authority identity does not rederive")

    root = artifact_root / str(record["subdirectory"])
    compiler_options = json.loads((root / "compiler_options.json").read_text(
        encoding="utf-8"))
    leaf_roles = ("make_ray", "closest_hit", "miss", "finalize")
    rebuilt_executable = {
        "schema": "rtdl.v4.verified_sphere_executable.v1",
        "authority_sha256": authority_sha,
        "plan_sha256": scientific["canonical_plan_sha256"],
        "abi_sha256": scientific["callback_abi_sha256"],
        "wrapper_source_sha256": member_sha256["wrapper.cu"],
        "wrapper_ptx_sha256": member_sha256["wrapper.ptx"],
        "generated_leaf_sha256": [
            member_sha256[f"leaf_{index}_{role}.py"]
            for index, role in enumerate(leaf_roles)],
        "compiled_leaf_sha256": [
            member_sha256[f"leaf_{index}_{role}.ptx"]
            for index, role in enumerate(leaf_roles)],
        "composed_ptx_sha256": member_sha256["composed.ptx"],
        "compiler_options": compiler_options,
        "nvrtc_log_sha256": member_sha256["nvrtc.log"],
    }
    _require(executable == rebuilt_executable,
             "executable record differs from preserved compiler bytes")
    _require(_canonical_digest(rebuilt_executable)
             == record["executable_sha256"] == scientific["executable_sha256"],
             "executable identity does not rederive")


def _ordered_f32(value: float) -> int:
    bits = _f32_bits(value)
    return (~bits & U32_MAX) if bits & 0x80000000 else bits ^ 0x80000000


def _compare_value_to_root(value, a, half_b, discriminant, branch):
    y = a * value + half_b
    if branch == 0:
        return (y > 0) - (y < 0)
    if branch == -1:
        if y >= 0:
            return 1
        delta = discriminant - y * y
        return (delta > 0) - (delta < 0)
    if branch == 1:
        if y <= 0:
            return -1
        delta = y * y - discriminant
        return (delta > 0) - (delta < 0)
    raise RuntimeError("invalid symbolic root branch")


def _float_from_bits(bits):
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def _round_symbolic_unit_root(a, half_b, discriminant, branch):
    low_bits, high_bits = 0, _f32_bits(1.0)
    while low_bits < high_bits:
        middle = (low_bits + high_bits + 1) // 2
        value = Fraction.from_float(_float_from_bits(middle))
        if _compare_value_to_root(
                value, a, half_b, discriminant, branch) <= 0:
            low_bits = middle
        else:
            high_bits = middle - 1
    lower = Fraction.from_float(_float_from_bits(low_bits))
    if _compare_value_to_root(
            lower, a, half_b, discriminant, branch) == 0:
        return _float_from_bits(low_bits)
    upper_bits = low_bits + 1
    upper = Fraction.from_float(_float_from_bits(upper_bits))
    midpoint_order = _compare_value_to_root(
        (lower + upper) / 2, a, half_b, discriminant, branch)
    if midpoint_order < 0:
        return _float_from_bits(upper_bits)
    if midpoint_order > 0:
        return _float_from_bits(low_bits)
    return _float_from_bits(low_bits if low_bits % 2 == 0 else upper_bits)


def _first_contact(start, end, centers, radii, application_ids):
    projected_start = tuple(_f32(value) for value in start)
    projected_end = tuple(_f32(value) for value in end)
    direction = tuple(_f32(projected_end[i] - projected_start[i])
                      for i in range(3))
    exact_direction = tuple(Fraction.from_float(value) for value in direction)
    a = sum((value * value for value in exact_direction), Fraction(0))
    _require(a > 0, "invalid query segment")
    candidates = []
    for center, radius, app_id in zip(centers, radii, application_ids):
        projected_center = tuple(_f32(value) for value in center)
        projected_radius = _f32(radius)
        _require(projected_radius > 0.0, "invalid sphere radius")
        offset = tuple(
            Fraction.from_float(projected_start[i])
            - Fraction.from_float(projected_center[i])
            for i in range(3))
        exact_radius = Fraction.from_float(projected_radius)
        c = sum((value * value for value in offset), Fraction(0)) \
            - exact_radius * exact_radius
        _require(c > 0, "query does not start strictly outside sphere")
        half_b = sum(
            (offset[i] * exact_direction[i] for i in range(3)), Fraction(0))
        discriminant = half_b * half_b - a * c
        if discriminant < 0:
            continue
        for branch in ((0,) if discriminant == 0 else (-1, 1)):
            if _compare_value_to_root(
                    Fraction(0), a, half_b, discriminant, branch) <= 0 \
                    and _compare_value_to_root(
                        Fraction(1), a, half_b, discriminant, branch) >= 0:
                t = _round_symbolic_unit_root(
                    a, half_b, discriminant, branch)
                # The normative stable winner key is only
                # (ordered-f32(t), application_id).  Primitive index is
                # physical provenance and must not participate in the oracle.
                candidates.append((_ordered_f32(t), int(app_id), t))
                break
    if not candidates:
        return [0, _f32_bits(1.0), U32_MAX]
    _, app_id, t = min(candidates)
    return [1, _f32_bits(t), app_id]


def _verify_policy_aware_rows(observed, expected, policies):
    _require(len(observed) == len(expected) == len(policies),
             "expected-output policy cardinality differs")
    exact_rows = []
    ulp_rows = []
    for index, (actual, gold, policy) in enumerate(
            zip(observed, expected, policies)):
        _require(actual[0] == gold[0] and actual[2] == gold[2],
                 f"row {index} hit/application identity differs")
        if policy in ("miss_exact_bits", "exact_root_bits"):
            _require(actual == gold, f"row {index} exact bits differ")
            exact_rows.append(index)
        elif policy == "nonexact_t_ulp_le_4":
            distance = abs(int(actual[1]) - int(gold[1]))
            _require(distance <= 4, f"row {index} exceeds four binary32 ULP")
            ulp_rows.append({"index": index, "ulp_distance": distance})
        else:
            raise RuntimeError(f"unknown expected-output policy at row {index}: {policy}")
    return exact_rows, ulp_rows


def verify(
    result_path: Path, native_path: Path, oracle_path: Path,
    artifact_root: Path,
) -> dict[str, object]:
    raw = result_path.read_bytes()
    result = json.loads(raw)
    _require(result["schema"] == "rtdl.goal5833.home_builtin_sphere_validation.v1",
             "wrong result schema")
    _require(result["status"] == "PASS", "functional run did not pass")
    _require(result["registered_performance_timing_count"] == 0,
             "functional result contains timing")
    for key in (
        "performance_claimed", "prospective_generalization_claimed",
        "paper_app_claimed",
    ):
        _require(result[key] is False, f"forbidden claim enabled: {key}")
    _require(_sha256(native_path) == result["native_sha256"],
             "native identity mismatch")
    _require(_sha256(oracle_path) == result["oracle_sha256"],
             "oracle identity mismatch")
    centers = result["centers"]
    radii = result["radii"]
    application_ids = result["application_ids"]
    recomputed = [
        _first_contact(start, end, centers, radii, application_ids)
        for start, end in result["queries"]
    ]
    _require(recomputed == result["expected"],
             "independent CPU oracle mismatch")
    exact_rows, ulp_rows = _verify_policy_aware_rows(
        result["observed"], result["expected"],
        result["expected_comparison_policies"])
    _require(result["fixture_names"] == [
        "equal_time_stable_application_id",
        "transverse_miss",
        "nearer_time_precedes_application_id",
        "grazing_front_face_entry",
        "beyond_tmax_miss",
    ], "fixture set differs")
    _require(all(
        row["first_error_claimed"] == 0 and row["error_code"] == 0
        for row in result["device_status"]), "device status failed")
    _require(result["role_counters"] == [0, 5, 0, 0, 3, 2, 5],
             "role counters differ")
    _require(result["use_after_close_rejected"] is True,
             "use after close was not rejected")
    _require(result["double_close_rejected"] is True and
             result["serialization_rejected"] is True and
             result["thread_boundary_rejected"] is True,
             "prepared lifecycle guard evidence differs")
    _require(result["lifecycle_before"]["execution_count"] == 0 and
             result["lifecycle_after_first"]["execution_count"] == 1 and
             result["lifecycle_after"]["execution_count"] == 2,
             "lifecycle count differs")
    tangent = result["exact_tangent_boundary"]
    tangent_expected = [
        _first_contact(start, end, centers, radii, application_ids)
        for start, end in tangent["queries"]
    ]
    _require(
        tangent_expected == tangent["independent_closed_sphere_expected"]
        and len(tangent_expected) == 1
        and tangent_expected[0][0] == 1,
        "exact-tangent closed-sphere oracle evidence differs",
    )
    _require(
        "exact_tangent_unsupported_by_optix9_front_face_contract"
        in tangent["error"]
        and tangent["execution_count_before"] == 2
        and tangent["execution_count_after"] == 2
        and tangent["native_launch_occurred"] is False,
        "exact tangent was not rejected before native execution",
    )
    endpoint = result["trace_endpoint_boundary"]
    endpoint_expected = [
        _first_contact(start, end, centers, radii, application_ids)
        for start, end in endpoint["queries"]
    ]
    _require(
        endpoint_expected == endpoint["independent_closed_segment_expected"]
        and len(endpoint_expected) == 1
        and endpoint_expected[0]
        == [0, _f32_bits(1.0), U32_MAX],
        "trace-endpoint closed-segment oracle evidence differs",
    )
    _require(
        "front_entry_near_closed_trace_interval_boundary"
        in endpoint["error"]
        and endpoint["execution_count_before"] == 2
        and endpoint["execution_count_after"] == 2
        and endpoint["native_launch_occurred"] is False,
        "trace-endpoint ambiguity was not rejected before native execution",
    )
    exact_tmax = result["exact_tmax_boundary"]
    exact_tmax_expected = [
        _first_contact(start, end, centers, radii, application_ids)
        for start, end in exact_tmax["queries"]
    ]
    _require(
        exact_tmax_expected == exact_tmax["independent_closed_segment_expected"]
        and exact_tmax_expected == [[1, _f32_bits(1.0), 2]],
        "exact-tmax closed-segment oracle evidence differs",
    )
    _require(
        "front_entry_near_closed_trace_interval_boundary"
        in exact_tmax["error"]
        and exact_tmax["execution_count_before"] == 2
        and exact_tmax["execution_count_after"] == 2
        and exact_tmax["native_launch_occurred"] is False,
        "exact-tmax contact was not rejected before native execution",
    )
    cleanup = result["expected_mismatch_cleanup"]
    _require(
        cleanup["owner_closed_after_exception"] is True
        and "expected_output" in cleanup["error"],
        "post-launch expected-output exception did not close its owner",
    )
    physical = result["physical_receipt"]
    descriptor = physical["native_descriptor"]
    _require(descriptor["schema"] ==
             "rtdl.v4.native_builtin_sphere_descriptor.v2",
             "native descriptor schema differs")
    _require(descriptor["builtin_is_module"] is True and
             descriptor["user_intersection_program"] is False and
             descriptor["uses_motion_blur"] is False,
             "native built-in sphere facts differ")
    _require(descriptor["primitive_count"] == len(centers) and
             descriptor["center_stride_bytes"] == 12 and
             descriptor["radius_stride_bytes"] == 4 and
             descriptor["single_radius"] is False and
             descriptor["primitive_index_offset"] == 0 and
             descriptor["gas_count"] == 1 and
             descriptor["sbt_record_count"] == 1 and
             descriptor["motion_key_count"] == 0 and
             descriptor["builtin_is_build_flags"]
             == descriptor["build_flags"] and
             descriptor["max_payload_values"] == 8 and
             descriptor["max_attribute_values"] == 0 and
             descriptor["max_trace_depth"] == 1 and
             descriptor["program_group_count"] == 3 and
             descriptor["traversable_graph_flags"] > 0,
             "native geometry facts differ")
    _require(all(descriptor[key] == expected for key, expected in
                 EXPECTED_OPTIX9_SPHERE_FACTS.items()),
             "native OptiX 9 sphere enum/flag facts differ")
    expected_optix = tuple(int(item) for item in result["optix_sdk"].split("."))
    expected_compute = tuple(
        int(item) for item in result["compute_capability"].split("."))
    _require(len(expected_optix) == 3 and len(expected_compute) == 2,
             "target version shape differs")
    _require(
        tuple(descriptor[key] for key in (
            "compiled_optix_major", "compiled_optix_minor",
            "compiled_optix_patch")) == expected_optix,
        "compiled OptiX SDK differs from target authority",
    )
    _require(
        tuple(descriptor[key] for key in (
            "cuda_compute_capability_major",
            "cuda_compute_capability_minor")) == expected_compute,
        "live CUDA compute capability differs from target authority",
    )
    _require(
        descriptor["compiled_optix_version"]
        == expected_optix[0] * 10000 + expected_optix[1] * 100
        + expected_optix[2]
        and descriptor["cuda_driver_version"] > 0,
        "native runtime version identity differs",
    )
    expected_native_static = _native_static_fingerprint(
        centers, radii, application_ids)
    _require(
        descriptor["static_input_fingerprint"] == expected_native_static
        and descriptor["device_static_input_fingerprint"]
        == expected_native_static,
        "native host/device static content fingerprint differs",
    )
    _require(all(descriptor[key] > 0 for key in (
        "center_device_pointer", "radius_device_pointer",
        "application_id_device_pointer", "traversable_identity")),
        "native static device identity is zero")
    _require(
        descriptor["last_execution_present"] is True
        and descriptor["last_status_failed"] is False
        and descriptor["last_query_count"] == len(result["queries"])
        and descriptor["last_status_d2h_call_count"] == 1
        and descriptor["last_application_output_d2h_call_count"] == 6
        and descriptor["last_output_after_status_failure_count"] == 0
        and descriptor["last_query_device_pointer_nonzero_count"] == 6
        and descriptor["last_output_device_pointer_nonzero_count"] == 8,
        "native execution identity/transfer telemetry differs",
    )
    _require(
        descriptor["last_query_fingerprint"]
        == _native_query_fingerprint(result["queries"])
        and descriptor["last_device_query_fingerprint"]
        == _native_query_fingerprint(result["queries"])
        and descriptor["last_output_fingerprint"]
        == _native_output_fingerprint(result)
        and descriptor["last_status_fingerprint"]
        == _native_status_fingerprint(result["device_status"])
        and descriptor["last_counter_fingerprint"]
        == _native_counter_fingerprint(result["role_counters"]),
        "native execution content fingerprint differs",
    )
    for key in (
        "last_query_device_pointer_fingerprint",
        "last_output_device_pointer_fingerprint",
    ):
        value = descriptor[key]
        _require(isinstance(value, str) and len(value) == 64 and all(
            char in "0123456789abcdef" for char in value)
            and value != "0" * 64,
            f"native pointer fingerprint is malformed: {key}")
    traversal = result["traversal_receipt"]
    execution_native_path = result.get("native_path")
    _verify_execution_native_binding(
        execution_native_path, traversal, physical, label="primary")
    _require(
        traversal["provider_library_sha256"] == result["native_sha256"],
        "traversal provider bytes differ from preserved native",
    )
    _require(
        physical["native_library_sha256"] == result["native_sha256"]
        and physical["loaded_native_library_sha256"] == result["native_sha256"],
        "authorized/loaded native bytes differ from preserved native",
    )
    _require(
        physical["commitment_scope"]
        == "canonical_host_ffi_projection_plus_native_content_and_device_identity",
        "physical commitment scope differs",
    )
    for key in (
        "field_mapping_commitment_sha256",
        "static_input_commitment_sha256",
        "query_commitment_sha256",
        "output_commitment_sha256",
        "status_commitment_sha256",
        "counter_commitment_sha256",
    ):
        value = physical.get(key)
        _require(
            isinstance(value, str)
            and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            f"malformed physical commitment: {key}",
        )
    _require(
        physical["output_commitment_sha256"]
        == _canonical_digest(result["observed"]),
        "physical output commitment differs from observed rows",
    )
    _require(
        physical["field_mapping_commitment_sha256"]
        == _field_mapping_commitment(),
        "physical field-mapping commitment differs",
    )
    _require(
        physical["static_input_commitment_sha256"]
        == _static_input_commitment(centers, radii, application_ids),
        "physical static-input commitment differs",
    )
    _require(
        physical["query_commitment_sha256"] == _query_commitment(result["queries"]),
        "physical query commitment differs",
    )
    _require(
        physical["status_commitment_sha256"] == _canonical_digest({
            "schema": "rtdl.v4.sphere_status_host_projection.v1",
            "rows": result["device_status"],
        }),
        "physical status commitment differs",
    )
    _require(
        physical["counter_commitment_sha256"] == _canonical_digest({
            "schema": "rtdl.v4.sphere_counter_host_projection.v1",
            "values": result["role_counters"],
        }),
        "physical counter commitment differs",
    )
    _require(physical["status_before_output"] is True,
             "status-before-output commitment differs")
    _require(
        physical["composed_ptx_sha256"] == result["composed_ptx_sha256"],
        "physical composed-PTX identity differs",
    )
    expected_output_digest = _canonical_digest(result["observed"])
    _require(traversal["output_digest"] == expected_output_digest,
             "traversal output digest differs from observed rows")
    _require(
        traversal["semantic_digest"] == _canonical_digest({
            "authority": physical["authority_nonce"],
            "plan": result["canonical_plan_sha256"],
            "abi": result["callback_abi_sha256"],
            "ptx": result["composed_ptx_sha256"],
            "native": result["native_sha256"],
            "physical": physical,
        }),
        "traversal semantic digest does not bind the physical receipt",
    )
    body = dict(traversal)
    seal = body.pop("receipt_sha256")
    _require(_canonical_digest(body) == seal, "traversal receipt seal differs")
    snapshot = traversal["native_snapshot"]
    _require(traversal["physical_executor_classification"] ==
             "optix_traversal_observed" and
             traversal["expected_program_observed_at_receipt_edge"] is True,
             "expected true OptiX route not observed")
    _require(snapshot["attempted_launch_count"] == 1 and
             snapshot["successful_launch_count"] == 1 and
             snapshot["failed_launch_count"] == 0 and
             snapshot["complete_context_launch_count"] == 1 and
             snapshot["incomplete_context_launch_count"] == 0 and
             snapshot["raygen_invocation_count"] == len(result["queries"]),
             "native traversal snapshot differs")

    repeat = result["repeat_execution"]
    repeat_recomputed = [
        _first_contact(start, end, centers, radii, application_ids)
        for start, end in repeat["queries"]
    ]
    _require(repeat_recomputed == repeat["expected"],
             "repeat independent CPU oracle mismatch")
    _verify_policy_aware_rows(
        repeat["observed"], repeat["expected"],
        repeat["expected_comparison_policies"])
    repeat_physical = repeat["physical_receipt"]
    repeat_descriptor = repeat_physical["native_descriptor"]
    stable_keys = {key for key in descriptor if not key.startswith("last_")}
    _require(all(repeat_descriptor[key] == descriptor[key]
                 for key in stable_keys),
             "repeat native static descriptor identity changed")
    _require(
        repeat_descriptor["last_execution_present"] is True
        and repeat_descriptor["last_status_failed"] is False
        and repeat_descriptor["last_query_count"] == len(repeat["queries"])
        and repeat_descriptor["last_status_d2h_call_count"] == 1
        and repeat_descriptor["last_application_output_d2h_call_count"] == 6
        and repeat_descriptor["last_output_after_status_failure_count"] == 0
        and repeat_descriptor["last_query_device_pointer_nonzero_count"] == 6
        and repeat_descriptor["last_output_device_pointer_nonzero_count"] == 8
        and repeat_descriptor["last_query_fingerprint"]
        == _native_query_fingerprint(repeat["queries"])
        and repeat_descriptor["last_device_query_fingerprint"]
        == _native_query_fingerprint(repeat["queries"])
        and repeat_descriptor["last_output_fingerprint"]
        == _native_output_fingerprint(repeat)
        and repeat_descriptor["last_status_fingerprint"]
        == _native_status_fingerprint(repeat["device_status"])
        and repeat_descriptor["last_counter_fingerprint"]
        == _native_counter_fingerprint(repeat["role_counters"])
        and all(repeat_descriptor[key] != "0" * 64 for key in (
            "last_query_device_pointer_fingerprint",
            "last_output_device_pointer_fingerprint")),
        "repeat native execution fingerprint differs",
    )
    repeat_traversal = repeat["traversal_receipt"]
    _verify_execution_native_binding(
        execution_native_path, repeat_traversal, repeat_physical,
        label="repeat")
    _require(
        repeat_traversal["provider_library_sha256"]
        == result["native_sha256"],
        "repeat traversal provider differs",
    )
    repeat_body = dict(repeat_traversal)
    repeat_seal = repeat_body.pop("receipt_sha256")
    _require(_canonical_digest(repeat_body) == repeat_seal,
             "repeat traversal seal differs")
    repeat_snapshot = repeat_traversal["native_snapshot"]
    _require(
        repeat_snapshot["successful_launch_count"] == 1
        and repeat_snapshot["failed_launch_count"] == 0
        and repeat_snapshot["complete_context_launch_count"] == 1
        and repeat_snapshot["raygen_invocation_count"] == len(repeat["queries"]),
        "repeat traversal snapshot differs",
    )
    _require(
        repeat_traversal["semantic_digest"] == _canonical_digest({
            "authority": repeat_physical["authority_nonce"],
            "plan": result["canonical_plan_sha256"],
            "abi": result["callback_abi_sha256"],
            "ptx": result["composed_ptx_sha256"],
            "native": result["native_sha256"],
            "physical": repeat_physical,
        }),
        "repeat traversal semantic binding differs",
    )

    hostile = result["hostile_zero_tmax"]
    failure = hostile["failure_receipt"]
    failure_physical = failure["physical_receipt"]
    failure_descriptor = failure_physical["native_descriptor"]
    _require(
        failure_descriptor["last_status_failed"] is True
        and failure_descriptor["last_execution_present"] is True
        and failure_descriptor["last_query_count"] == len(hostile["queries"])
        and failure_descriptor["last_status_d2h_call_count"] == 1
        and failure_descriptor["last_application_output_d2h_call_count"] == 0
        and failure_descriptor["last_output_after_status_failure_count"] == 0
        and failure_descriptor["last_query_device_pointer_nonzero_count"] == 6
        and failure_descriptor["last_output_device_pointer_nonzero_count"] == 8
        and failure_descriptor["last_output_fingerprint"] == ""
        and all(failure_descriptor[key] != "0" * 64 for key in (
            "last_query_device_pointer_fingerprint",
            "last_output_device_pointer_fingerprint"))
        and failure_physical["application_output_d2h_after_status_failure"] == 0
        and failure_physical["device_failure_observed"] is True,
        "hostile status-before-output telemetry differs",
    )
    _require(any(row["first_error_claimed"] or row["error_code"]
                 for row in failure_physical["device_status_rows"]),
             "hostile device status did not fail")
    _require(
        failure_descriptor["last_query_fingerprint"]
        == _native_query_fingerprint(hostile["queries"])
        and failure_descriptor["last_device_query_fingerprint"]
        == _native_query_fingerprint(hostile["queries"])
        and failure_descriptor["last_status_fingerprint"]
        == _native_status_fingerprint(failure_physical["device_status_rows"])
        and failure_descriptor["last_counter_fingerprint"]
        == _native_counter_fingerprint(failure_physical["role_counters"]),
        "hostile native failure fingerprint differs",
    )
    expected_failure_digest = _canonical_digest({
        "schema": "rtdl.v4.sphere_device_failure.v1",
        "status": failure_physical["device_status_rows"],
        "counters": failure_physical["role_counters"],
    })
    _require(failure["failure_digest"] == expected_failure_digest,
             "hostile failure digest differs")
    failure_traversal = failure["traversal_receipt"]
    _verify_execution_native_binding(
        execution_native_path, failure_traversal, failure_physical,
        label="hostile")
    failure_body = dict(failure_traversal)
    failure_seal = failure_body.pop("receipt_sha256")
    _require(_canonical_digest(failure_body) == failure_seal,
             "hostile traversal seal differs")
    _require(
        failure_traversal["provider_library_sha256"]
        == result["native_sha256"]
        and failure_traversal["output_digest"] == expected_failure_digest
        and failure_traversal["native_snapshot"]["successful_launch_count"] == 1
        and failure_traversal["native_snapshot"]["raygen_invocation_count"]
        == len(hostile["queries"]),
        "hostile traversal identity differs",
    )
    _require(
        failure_traversal["semantic_digest"] == _canonical_digest({
            "authority": failure_physical["authority_nonce"],
            "plan": hostile["canonical_plan_sha256"],
            "abi": hostile["callback_abi_sha256"],
            "ptx": hostile["composed_ptx_sha256"],
            "native": result["native_sha256"],
            "physical": failure_physical,
        }),
        "hostile traversal semantic binding differs",
    )
    accepted_members = _verify_artifact_set(
        artifact_root.resolve(strict=True), result["accepted_artifacts"])
    hostile_members = _verify_artifact_set(
        artifact_root.resolve(strict=True), hostile["artifacts"])
    _verify_artifact_bridges(
        result, hostile, accepted_members, hostile_members)
    _verify_compiler_identity(
        artifact_root.resolve(strict=True), result["accepted_artifacts"],
        result, accepted_members)
    _verify_compiler_identity(
        artifact_root.resolve(strict=True), hostile["artifacts"],
        hostile, hostile_members)
    _require(result["accepted_artifacts"]["executable_sha256"]
             == result["executable_sha256"] and
             hostile["artifacts"]["executable_sha256"]
             == hostile["executable_sha256"],
             "artifact set is bound to the wrong executable")
    return {
        "schema": "rtdl.goal5833.home_builtin_sphere_recount.v1",
        "status": "PASS",
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "native_sha256": result["native_sha256"],
        "oracle_sha256": result["oracle_sha256"],
        "observed": result["observed"],
        "exact_policy_rows": exact_rows,
        "ulp_policy_rows": ulp_rows,
        "native_descriptor": descriptor,
        "traversal_receipt_sha256": seal,
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("native", type=Path)
    parser.add_argument("oracle", type=Path)
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    recount = verify(
        args.result.resolve(strict=True), args.native.resolve(strict=True),
        args.oracle.resolve(strict=True), args.artifact_dir.resolve(strict=True))
    text = json.dumps(recount, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
