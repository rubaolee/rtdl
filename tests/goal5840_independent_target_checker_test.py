from __future__ import annotations

import ast
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import tempfile
import unittest

from rtdsl.v4_callback_lifecycle import (
    AnyHitProtocolProof,
    BoundedRelationProtocol,
    TriangleReductionMode,
    TriangleReductionProtocol,
    standard_protocol_physical_plan,
)
from rtdsl.v4_family_route_adapters import (
    bounded_relation_family_route,
    triangle_reduction_family_route,
)
from rtdsl.v4_sphere_any_hit_count_family_route import (
    sphere_any_hit_count_family_route,
)
from rtdsl.v4_target_evidence_bundle import (
    TARGET_EVIDENCE_BUNDLE_DOMAIN,
    build_family_target_declaration,
    build_target_evidence_bundle,
    make_blob_record,
    registered_operator_contracts,
)
from rtdsl.v4_target_control_flow_evidence import (
    capture_target_control_flow_evidence,
)
from scripts import goal5840_independent_target_checker as checker
from scripts import goal5840_mutation_suite as mutation_suite


ROUTES = tuple(checker.ROUTE_RULES)
FAMILY_PLAN_DOMAIN = b"rtdl.family_compilation_plan.v1\0"
FAMILY_SHAPE_DOMAIN = b"rtdl.family_shape.v1\0"
PROTOCOL_INSTANCE_DOMAIN = b"rtdl.protocol_instance.v1\0"
PREREGISTRATION_PATH = Path(
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "GOAL5840_PREREGISTRATION.json"
)
FROZEN_MUTATIONS = {
    (row["route_id"], row["property_id"]): row
    for row in json.loads(PREREGISTRATION_PATH.read_text(encoding="ascii"))[
        "mutation_matrix"
    ]
}


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _proof(protocol: object, label: str) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        plan.callback_ir_sha256,
        plan.effect_digest,
        _sha(label),
        "external_machine_checked_order_independence_v1",
    )


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sealed(value: dict[str, object], field: str) -> dict[str, object]:
    value[field] = _digest({key: item for key, item in value.items() if key != field})
    return value


def _role_effects(route_id: str) -> dict[str, tuple[str, ...]]:
    if route_id.startswith("stable::bounded_relation"):
        return {
            "any_hit": ("accept_continue",),
            "bounds": ("aabb",),
            "closest_hit": ("payload",),
            "finalize": ("output",),
            "intersection": ("hit", "no_hit"),
            "make_ray": ("trace_request",),
            "miss": ("payload",),
        }
    return {
        "any_hit": ("accept_continue",),
        "finalize": ("output",),
        "make_ray": ("trace_request",),
        "miss": ("payload",),
    }


def _buffers(route_id: str) -> list[dict[str, object]]:
    primitive = checker.ROUTE_RULES[route_id]["primitive_kind"]
    result = checker.ROUTE_RULES[route_id]["nominal_output"]
    return [
        {
            "ordinal": 0,
            "semantic": f"primitive.{primitive}",
            "value_type": "u32",
        },
        {
            "ordinal": 1,
            "semantic": result,
            "value_type": "u64",
        },
    ]


def _channels(route_id: str) -> list[dict[str, object]]:
    channel = checker.ROUTE_RULES[route_id]["channel"]
    if channel is None:
        return []
    return [{
        "semantic": channel[0],
        "ownership": channel[1],
        "producer": {"kind": "callback"},
    }]


def _plan(
    route_id: str,
    abi_sha: str,
    callback_ir_sha: str,
    *,
    mode: str | None = None,
) -> SimpleNamespace:
    rule = checker.ROUTE_RULES[route_id]
    contract = registered_operator_contracts(route_id)[0]
    record_count = (
        "constant_one"
        if rule["sbt_record_count_relation"] == "constant_one"
        else "primitive_count"
    )
    roles = [
        {
            "role": role,
            "allowed_effects": list(effects),
            "required_effects": list(effects),
            "cardinality": "exactly_one",
        }
        for role, effects in sorted(_role_effects(route_id).items())
    ]
    family_shape = {
            "callback": {"roles": roles},
            "graph_nodes": [{
                "kind": "trace",
                "primitive_kind": rule["primitive_kind"],
            }],
            "buffers": _buffers(route_id),
            "channels": _channels(route_id),
            "events": [],
            "capabilities": [],
            "physical": {"sbt": {
                "record_stride": 1,
                "record_count_relation": record_count,
            }},
            "continuation": {
                "initial_state": "synthetic_prepared",
                "states": [
                    {"state_id": "synthetic_prepared", "kind": "prepared"},
                    {"state_id": "synthetic_launched", "kind": "launched"},
                    {"state_id": "synthetic_ok", "kind": "status_ok"},
                    {"state_id": "synthetic_failed", "kind": "status_failed"},
                    {"state_id": "synthetic_committed", "kind": "committed"},
                ],
                "transitions": [
                    {
                        "from_state": "synthetic_prepared",
                        "event": "launch",
                        "to_state": "synthetic_launched",
                    },
                    {
                        "from_state": "synthetic_launched",
                        "event": "observe_status_ok",
                        "to_state": "synthetic_ok",
                    },
                    {
                        "from_state": "synthetic_launched",
                        "event": "observe_status_failure",
                        "to_state": "synthetic_failed",
                    },
                    {
                        "from_state": "synthetic_ok",
                        "event": "copy_output",
                        "to_state": "synthetic_committed",
                    },
                ],
                "terminal_states": ["synthetic_failed", "synthetic_committed"],
                "invariants": [
                    "copy_output_requires_status_ok",
                    "status_failure_forbids_output_copy",
                ],
            },
            "result_pipeline": [{
                "operator": "provider_operator",
                "operator_id": contract["operator_id"],
                "operator_contract_sha256": _digest(contract),
            }],
        }
    effect_digest = _sha(route_id + ":effects")
    sphere = route_id == checker.SPHERE_ROUTE_ID
    physical_schema_sha = _sha(route_id + ":physical-schema")
    if sphere:
        behavior_schema = {
            "schema": checker.SPHERE_BEHAVIOR_SCHEMA,
            "callback_ir_sha256": callback_ir_sha,
            "effect_digest": effect_digest,
            "physical_schema_sha256": physical_schema_sha,
            "event_semantics": "intersected_primitive_once",
            "continuation": "accept_every_hit_and_continue",
            "result_operator": "rtdl.result.per_query_u64.v1",
            "output_count_relation": "query_count",
            "overflow": "impossible_under_u32_primitive_count_bound",
        }
    else:
        behavior_schema = {"schema_sha256": _sha(route_id + ":behavior")}
    protocol_instance = {
        "nominal_semantics": {"output": rule["nominal_output"]},
        "parameter_values": ([{
            "parameter_ref": "p0",
            "value_type": "namespaced_identifier",
            "value": (
                "checked_u64_product_sum"
                if mode == "weighted_hit_count"
                else "checked_u64_sum"
            ),
        }] if route_id.startswith("stable::triangle_reduction") else []),
    }
    if sphere:
        protocol_instance["authorities"] = [{
            "authority_kind": "physical_schema",
            "authority_sha256": physical_schema_sha,
        }]
    family_shape_sha = hashlib.sha256(
        FAMILY_SHAPE_DOMAIN + _canonical(family_shape)
    ).hexdigest()
    protocol_instance_sha = hashlib.sha256(
        PROTOCOL_INSTANCE_DOMAIN + _canonical(protocol_instance)
    ).hexdigest()
    document = {
        "schema": "rtdl.family_compilation_plan.v1",
        "family_shape_sha256": family_shape_sha,
        "protocol_instance_sha256": protocol_instance_sha,
        "callback_source_sha256": _sha(route_id + ":callback-source"),
        "callback_ir_sha256": callback_ir_sha,
        "effect_digest": effect_digest,
        "abi_sha256": abi_sha,
        "behavior_schema_sha256": (
            _digest(behavior_schema)
            if sphere
            else _sha(route_id + ":behavior")
        ),
        "canonical_template_id": (
            checker.SPHERE_PHYSICAL_TEMPLATE
            if sphere
            else "goal5840.synthetic.template.v1"
        ),
        "family_shape": family_shape,
        "protocol_instance": protocol_instance,
    }
    plan_sha = hashlib.sha256(FAMILY_PLAN_DOMAIN + _canonical(document)).hexdigest()
    return SimpleNamespace(
        to_dict=lambda: document,
        plan_sha256=plan_sha,
        behavior_schema=behavior_schema,
        physical_schema_sha256=physical_schema_sha,
    )


def _effect_fields(route_id: str, role: str, effect: str) -> list[dict[str, object]]:
    if route_id.startswith("stable::bounded_relation") \
            and role == "intersection" and effect == "hit":
        return [{
            "path": "out.hit.attributes.0",
            "scalar": "u32",
            "semantic_type": '{"kind":"scalar","scalar":"u32"}',
        }]
    if route_id.endswith("any_hit_count_continue_u64_per_query") \
            and role == "finalize" and effect == "output":
        return [{
            "path": "out.output.value.count",
            "scalar": "u64",
            "semantic_type": '{"kind":"scalar","scalar":"u64"}',
        }]
    return []


def _abi(route_id: str, abi_sha: str, callback_ir_sha: str) -> dict[str, object]:
    rows = []
    for role, effects in sorted(_role_effects(route_id).items()):
        inputs = []
        if route_id.startswith("stable::triangle_reduction") and role == "any_hit":
            inputs.append({
                "path": "in.hit.primitive_index",
                "scalar": "u32",
                "semantic_type": '{"kind":"scalar","scalar":"u32"}',
            })
        rows.append({
            "role": role,
            "symbol": f"goal5840_{role}",
            "inputs": inputs,
            "effects": [{
                "kind": effect,
                "tag": next(tag for tag, name in checker.EFFECT_TAGS.items() if name == effect),
                "fields": _effect_fields(route_id, role, effect),
            } for effect in effects],
        })
    return {
        "schema_id": "https://rtdl.dev/schemas/v4-callback-abi-v1.json",
        "schema_version": "v1",
        "abi_sha256": abi_sha,
        "callback_ir_sha256": callback_ir_sha,
        "roles": rows,
    }


def _leaf_source(symbol: str, effects: tuple[str, ...]) -> str:
    lines = [f"def {symbol}(out_effect_tag, branch):"]
    for index, effect in enumerate(effects):
        tag = next(tag for tag, name in checker.EFFECT_TAGS.items() if name == effect)
        prefix = "if" if index == 0 else "elif"
        lines.append(f"    {prefix} branch == {index}:")
        lines.append(f"        out_effect_tag[0] = {tag}")
    lines.append("    return")
    return "\n".join(lines) + "\n"


def _inline_definition(symbol: str, effects: tuple[str, ...]) -> str:
    lines = [
        'extern "C" __forceinline__ __device__ unsigned long long '
        f"{symbol}(unsigned int* out_effect_tag) {{",
        "    out_effect_tag[0] = 0;",
    ]
    for effect in effects:
        tag = next(
            tag for tag, name in checker.EFFECT_TAGS.items() if name == effect
        )
        lines.append(f"    out_effect_tag[0] = {tag};")
    lines.extend(("    return 0ull;", "}"))
    return "\n".join(lines) + "\n"


def _wrapper_source(
    route_id: str,
    symbols: list[str],
    inline_definitions: list[str],
) -> str:
    declarations = "\n".join(f'extern "C" void {symbol}();' for symbol in symbols)
    if route_id.startswith("stable::bounded_relation"):
        body = declarations + "\n\n" + "\n".join(inline_definitions) + """
extern "C" __global__ void __raygen__rtdl_v4_bounded_relation() {
    atomicOr(&params.status[query].invocation_mask, 1u << 1u);
    origin = make_float3(0.0f, 0.0f, 0.0f);
    direction = make_float3(1.0f, 1.0f, 0.0f);
    optixTrace(params.traversable, origin, direction);
    params.output_hit_count[query] = payload_count;
    params.output_minimum_id[query] = payload_minimum;
    params.output_intersection_count[query] = intersection_count;
    atomicOr(&params.status[query].invocation_mask, 1u << 6u);
    if (latent_error || lifecycle_invalid || evidence_invalid) return;
    atomicAdd(&params.fast_control->validated_row_count, 1u);
}
extern "C" __global__ void __intersection__rtdl_v4_bounded_relation() {
    const bool closed =
        params.primitives[primitive_index].lower_x <= source_max_x &&
        params.primitives[primitive_index].lower_y <= source_max_y &&
        params.primitives[primitive_index].upper_x >= source_min_x &&
        params.primitives[primitive_index].upper_y >= source_min_y;
    atomicOr(&params.status[query].invocation_mask,
             (1u << 0u) | (1u << 2u));
    if (closed && overlap_x * overlap_y >= params.minimum_overlap)
        optixReportIntersection(0.0f, 0u,
                                params.primitives[primitive_index].item_id, 0u);
}
extern "C" __global__ void __anyhit__rtdl_v4_bounded_relation() {
    if (prior_count == 0xffffffffu) {
        optixTerminateRay(); return;
    }
    const unsigned int updated_count = prior_count + 1u;
    const unsigned int updated_minimum = hit_kind;
    const unsigned long long slot = v4_relation_reserve_row();
    if (slot < params.event_capacity) {
        row.item_id = optixGetAttribute_0();
        params.rows[slot] = row;
    } else {
        atomicExch(params.overflowed, 1u);
    }
    optixSetPayload_0(updated_count);
    optixSetPayload_1(updated_minimum);
    atomicOr(&params.status[query].invocation_mask, 1u << 3u);
}
extern "C" __global__ void __closesthit__rtdl_v4_bounded_relation() {
    atomicOr(&params.status[query].invocation_mask, 1u << 4u);
}
extern "C" __global__ void __miss__rtdl_v4_bounded_relation() {
    atomicOr(&params.status[query].invocation_mask, 1u << 5u);
}
"""
        return body
    elif route_id.startswith("stable::triangle_reduction"):
        body = """
const unsigned int primitive = optixGetPrimitiveIndex();
extern "C" __global__ void __raygen__rtdl_v4_triangle_reduction() {
    optixTrace(params.traversable);
    if (params.fast_control->error_code != 0u) return;
    const unsigned long long final_value = 1u;
    params.per_ray_u64[query] = final_value;
}
extern "C" __global__ void __raygen__rtdl_v4_triangle_reduction_diagnostic() {
    if (params.fast_control != nullptr) {
        optixTrace(params.traversable);
        if (params.fast_control->error_code != 0u) return;
        const unsigned long long final_value = 1u;
        params.per_ray_u64[query] = final_value;
        return;
    }
    optixTrace(params.traversable);
    if (params.fast_control != nullptr) {
        if (params.fast_control->error_code != 0u) return;
    } else if (params.status[query].first_error_claimed != 0u) return;
    (void)rtdl_v4_finalize_goal5840(query);
    if (!v4_commit_leaf_status(query, fin_status_ok)) { return; }
    if (fin_out_effect_tag != 9u) return;
    const unsigned long long final_value = 1u;
    params.per_ray_u64[query] = final_value;
}
"""
    else:
        body = """
const unsigned int primitive = optixGetPrimitiveIndex();
extern "C" __global__ void __raygen__rtdl_v4_sphere() {
    optixTrace(params.traversable);
    if (params.status[query].first_error_claimed != 0u) return;
    (void)rtdl_v4_finalize_goal5840(query);
    if (!v4_commit_leaf_status(query, fin_status_ok)) { return; }
    const unsigned long long result = 1u;
    params.output_0[query] = v4_u64_low(result);
    params.output_1[query] = v4_u64_high(result);
}
"""
    return declarations + body


def _make_bundle(
    route_id: str,
    *,
    mode: str | None = None,
) -> tuple[dict[str, object], str, str, str]:
    abi_sha = _sha(route_id + ":abi")
    callback_ir_sha = _sha(route_id + ":ir")
    plan = _plan(route_id, abi_sha, callback_ir_sha, mode=mode)
    declaration = build_family_target_declaration(route_id, plan)
    abi = _abi(route_id, abi_sha, callback_ir_sha)
    target_sha = _sha(route_id + ":target")
    native_sha = _sha(route_id + ":native")
    leaves = []
    symbols = []
    ptx_header = ".version 8.0\n.target sm_89\n.address_size 64\n"
    ptx_bodies = []
    role_symbols = []
    inline_definitions = []
    for role, effects in sorted(_role_effects(route_id).items()):
        symbol = f"goal5840_{role}"
        symbols.append(symbol)
        role_symbols.append([role, symbol])
        source = _leaf_source(symbol, effects)
        ptx_body = f".visible .func {symbol}() {{ ret; }}\n"
        ptx = ptx_header + ptx_body
        ptx_bodies.append(ptx_body)
        if route_id.startswith("stable::bounded_relation"):
            inline_definitions.append(_inline_definition(symbol, effects))
        leaves.append({
            "role": role,
            "generated_metadata": {
                "role": role,
                "abi_name": symbol,
                "generated_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "callback_ir_sha256": callback_ir_sha,
                "callback_effect_digest": plan.to_dict()["effect_digest"],
                "callback_abi_sha256": abi_sha,
            },
            "generated_source": make_blob_record(source),
            "compiled_metadata": {
                "role": role,
                "abi_name": symbol,
                "generated_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "ir_sha256": callback_ir_sha,
                "ptx_sha256": hashlib.sha256(ptx.encode()).hexdigest(),
            },
            "compiled_ptx": make_blob_record(ptx),
        })
    wrapper_source = _wrapper_source(
        route_id, symbols, inline_definitions
    )
    wrapper_body = ".visible .entry __raygen__goal5840() { ret; }\n"
    if route_id.startswith("stable::bounded_relation"):
        # NVRTC may erase every forced-inline leaf symbol. The identity proof
        # must use the raw source definitions, not final-PTX byte presence.
        wrapper_ptx = ptx_header + wrapper_body
        composed_ptx = wrapper_ptx
    else:
        wrapper_ptx = ptx_header + wrapper_body
        composed_ptx = ptx_header + "".join(ptx_bodies) + wrapper_body
    composed_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
    wrapper_source_sha = hashlib.sha256(wrapper_source.encode()).hexdigest()
    wrapper_ptx_sha = hashlib.sha256(wrapper_ptx.encode()).hexdigest()
    generated_hashes = [
        row["generated_metadata"]["generated_source_sha256"] for row in leaves
    ]
    compiled_hashes = [
        row["compiled_metadata"]["ptx_sha256"] for row in leaves
    ]
    executable_schema = checker.ROUTE_RULES[route_id]["executable_schema"]
    if route_id.startswith("stable::bounded_relation"):
        identity_preimage = {
            "schema": executable_schema,
            "authority": _sha(route_id + ":authority"),
            "contract": _sha(route_id + ":contract"),
            "abi": abi_sha,
            "wrapper_source": wrapper_source_sha,
            "wrapper_ptx": wrapper_ptx_sha,
            "generated": generated_hashes,
            "compiled": compiled_hashes,
            "inline_cuda": hashlib.sha256(
                "\n".join(inline_definitions).encode()
            ).hexdigest(),
            "inline_cuda_leaves": [
                [role, hashlib.sha256(definition.encode()).hexdigest()]
                for (role, _symbol), definition in zip(
                    role_symbols, inline_definitions, strict=True
                )
            ],
            "composed": composed_sha,
            "options": ["--gpu-architecture=compute_89"],
            "nvrtc_log": _sha(route_id + ":nvrtc-log"),
        }
    elif route_id.startswith("stable::triangle_reduction"):
        identity_preimage = {
            "schema": executable_schema,
            "authority": _sha(route_id + ":authority"),
            "contract": _sha(route_id + ":contract"),
            "abi": abi_sha,
            "wrapper_source": wrapper_source_sha,
            "wrapper_ptx": wrapper_ptx_sha,
            "generated": generated_hashes,
            "compiled": compiled_hashes,
            "composed": composed_sha,
            "options": ["--gpu-architecture=compute_89"],
            "nvrtc_log": _sha(route_id + ":nvrtc-log"),
        }
    else:
        authority_nonce = _digest({
            "kind": "builtin_sphere_any_hit_count_physical_authority_v1",
            "callback": callback_ir_sha,
            "effect": plan.to_dict()["effect_digest"],
            "schema": plan.physical_schema_sha256,
            "target": target_sha,
        })
        physical_authority_sha = _digest({
            "callback_ir_sha256": callback_ir_sha,
            "callback_effect_digest": plan.to_dict()["effect_digest"],
            "schema_sha256": plan.physical_schema_sha256,
            "target_sha256": target_sha,
            "authority_nonce": authority_nonce,
        })
        physical_plan_sha = _digest({
            "schema_sha256": plan.physical_schema_sha256,
            "callback_ir_sha256": callback_ir_sha,
            "effect_digest": plan.to_dict()["effect_digest"],
            "target_sha256": target_sha,
            "authority_nonce": authority_nonce,
            "template_id": checker.SPHERE_PHYSICAL_TEMPLATE,
            "executable": False,
        })
        identity_preimage = {
            "schema": executable_schema,
            "authority_sha256": physical_authority_sha,
            "plan_sha256": physical_plan_sha,
            "abi_sha256": abi_sha,
            "wrapper_source_sha256": wrapper_source_sha,
            "wrapper_ptx_sha256": wrapper_ptx_sha,
            "generated_leaf_sha256": generated_hashes,
            "compiled_leaf_sha256": compiled_hashes,
            "composed_ptx_sha256": composed_sha,
            "compiler_options": ["--gpu-architecture=compute_89"],
            "nvrtc_log_sha256": _sha(route_id + ":nvrtc-log"),
        }
    executable_sha = _digest(identity_preimage)
    generated = {
        "wrapper": {
            "metadata": {
                "source_sha256": wrapper_source_sha,
                "callback_ir_sha256": callback_ir_sha,
                "callback_abi_sha256": abi_sha,
                "role_symbols": role_symbols,
                "linked_role_symbols": not route_id.startswith(
                    "stable::bounded_relation"
                ),
            },
            "source": make_blob_record(wrapper_source),
            "ptx": make_blob_record(wrapper_ptx),
        },
        "leaves": leaves,
        "composed_ptx": make_blob_record(composed_ptx),
        "executable_metadata": {
            "schema": executable_schema,
            "executable_sha256": executable_sha,
            "composed_ptx_sha256": composed_sha,
            "composition": {
                "schema": "rtdl.v4.composed_callback_ptx_evidence.v1",
                "mode": checker.ROUTE_RULES[route_id]["composition_mode"],
                "ptx_version": "8.0",
                "ptx_target": "sm_89",
                "address_size": "64",
                "wrapper_ptx_sha256": wrapper_ptx_sha,
                "leaf_order": [role for role, _symbol in role_symbols],
                "leaf_bindings": [
                    {"role": role, "symbol": symbol}
                    for role, symbol in role_symbols
                ],
                "stripped_wrapper_externs": symbols,
                "stripped_numba_environments": [],
            },
            "identity_preimage": identity_preimage,
        },
    }
    operator_contracts = [{
        "operator_id": row["operator_id"],
        "operator_contract_sha256": _digest(row),
    } for row in declaration["operator_contracts"]]
    program_artifacts = [
        {
            "artifact_id": "rtdl.callback.abi",
            "format_id": "rtdl.callback_abi.canonical_json.v1",
            "payload": make_blob_record(_canonical(abi)),
        },
        {
            "artifact_id": "rtdl.callback.program",
            "format_id": "rtdl.callback_program.canonical_json.v1",
            "payload": make_blob_record(
                _canonical({"callback_ir_sha256": callback_ir_sha})
            ),
        },
        {
            "artifact_id": "rtdl.behavior.schema",
            "format_id": "rtdl.behavior_schema.canonical_json.v1",
            "payload": make_blob_record(
                _canonical(plan.behavior_schema)
            ),
        },
    ]
    artifact_rows = sorted(({
        "artifact_id": row["artifact_id"],
        "format_id": row["format_id"],
        "payload_bytes": row["payload"]["bytes"],
        "payload_sha256": row["payload"]["sha256"],
    } for row in program_artifacts), key=lambda row: row["artifact_id"])
    artifact_bundle_sha = _digest({
        "schema": "rtdl.family_program_artifacts.v1",
        "plan_sha256": plan.plan_sha256,
        "callback_source_sha256": plan.to_dict()["callback_source_sha256"],
        "callback_ir_sha256": plan.to_dict()["callback_ir_sha256"],
        "effect_digest": plan.to_dict()["effect_digest"],
        "abi_sha256": plan.to_dict()["abi_sha256"],
        "behavior_schema_sha256": plan.to_dict()["behavior_schema_sha256"],
        "artifacts": artifact_rows,
    })
    requirements_body = {
        "schema": "rtdl.family_plan_requirements.v1",
        "graph_kinds": ["trace"],
        "primitive_kinds": [checker.ROUTE_RULES[route_id]["primitive_kind"]],
        "callback_roles": sorted(_role_effects(route_id)),
        "provider_builtins": [],
        "operator_contracts": operator_contracts,
        "capabilities": [],
    }
    descriptor = _sealed({
        "schema": "rtdl.family_provider_descriptor.v1",
        "provider_id": "goal5840.synthetic",
        "graph_kinds": ["trace"],
        "primitive_kinds": [checker.ROUTE_RULES[route_id]["primitive_kind"]],
        "callback_roles": sorted(_role_effects(route_id)),
        "provider_builtins": [],
        "artifact_formats": [
            {"artifact_id": row["artifact_id"], "format_id": row["format_id"]}
            for row in artifact_rows
        ],
        "operator_contracts": operator_contracts,
        "capabilities": [],
    }, "descriptor_sha256")
    projection = _sealed({
        "schema": "rtdl.family_provider_projection.v1",
        "provider_descriptor_sha256": descriptor["descriptor_sha256"],
        "plan_sha256": plan.plan_sha256,
        "family_shape_sha256": plan.to_dict()["family_shape_sha256"],
        "protocol_instance_sha256": plan.to_dict()["protocol_instance_sha256"],
        "callback_source_sha256": plan.to_dict()["callback_source_sha256"],
        "callback_ir_sha256": plan.to_dict()["callback_ir_sha256"],
        "effect_digest": plan.to_dict()["effect_digest"],
        "abi_sha256": plan.to_dict()["abi_sha256"],
        "behavior_schema_sha256": plan.to_dict()["behavior_schema_sha256"],
        "canonical_template_id": plan.to_dict()["canonical_template_id"],
        "requirements_sha256": _digest(requirements_body),
        "artifact_bundle_sha256": artifact_bundle_sha,
    }, "projection_sha256")
    identity = _sealed({
        "schema": "rtdl.family_executable_identity.v1",
        "provider_descriptor_sha256": descriptor["descriptor_sha256"],
        "provider_projection_sha256": projection["projection_sha256"],
        "plan_sha256": plan.plan_sha256,
        "target_sha256": target_sha,
        "executable_sha256": executable_sha,
        "provider_artifact_sha256": native_sha,
        "generated_artifact_sha256": composed_sha,
    }, "identity_sha256")
    rule = checker.ROUTE_RULES[route_id]
    record_count = (
        "constant_one"
        if rule["sbt_record_count_relation"] == "constant_one"
        else "primitive_count"
    )
    control_flow = capture_target_control_flow_evidence(route_id)
    execution_mode = mode or (
        "capacity_fail_closed_collection"
        if route_id.startswith("stable::bounded_relation")
        else "all_hit_count"
        if route_id.startswith("stable::triangle_reduction")
        else "accept_every_hit_and_continue"
    )
    output_sha = _sha(route_id + ":output")
    bundle = build_target_evidence_bundle(
        route_id=route_id,
        declaration=declaration,
        declaration_authority_sha256=_sha(route_id + ":declaration-authority"),
        program_artifacts=program_artifacts,
        generated_target_artifacts=generated,
        provider_descriptor=descriptor,
        provider_projection=projection,
        executable_identity=identity,
        target_binding={
            "target_sha256": target_sha,
            "native_library_sha256": native_sha,
        },
        native_producer_descriptor={
            "build_input_type_name": rule["native_names"][1],
        } | ({
            "runtime_physical_receipt": {
                "authority_nonce": authority_nonce,
            },
        } if route_id == checker.SPHERE_ROUTE_ID else {}),
        sbt_buffer_bindings={
            "schema": "rtdl.v4.target_sbt_buffer_bindings.v1",
            "primitive_kind": rule["primitive_kind"],
            "record_stride": 1,
            "record_count_relation": record_count,
            "buffers": _buffers(route_id),
        },
        target_control_flow_evidence=control_flow,
        execution_receipt={
            "schema": "rtdl.v4.goal5840_execution_receipt.v1",
            "route_id": route_id,
            "mode": execution_mode,
            "plan_sha256": plan.plan_sha256,
            "executable_identity_sha256": identity["identity_sha256"],
            "target_sha256": target_sha,
            "native_library_sha256": native_sha,
            "output_sha256": output_sha,
            "status": "OK",
            "status_code": 0,
            "status_before_output": True,
            "complete": True,
            "partial_result_exposed": False,
            "control_flow_manifest_sha256": control_flow["manifest_sha256"],
            "traversal_receipt": {
                "physical_executor_classification": "optix_traversal_observed",
                "provider_library_sha256": native_sha,
                "output_digest": output_sha,
            } | ({
                "physical_receipt": {
                    "authority_nonce": authority_nonce,
                },
            } if route_id == checker.SPHERE_ROUTE_ID else {}),
        },
    )
    return (
        bundle,
        declaration["declaration_sha256"],
        identity["identity_sha256"],
        str(control_flow["manifest_sha256"]),
    )


def _reseal_bundle(bundle: dict[str, object]) -> None:
    body = dict(bundle)
    body["bundle_sha256"] = ""
    bundle["bundle_sha256"] = hashlib.sha256(
        TARGET_EVIDENCE_BUNDLE_DOMAIN + _canonical(body)
    ).hexdigest()


def _replace_wrapper_source(
    bundle: dict[str, object], old: str, new: str
) -> None:
    generated = bundle["generated_target_artifacts"]
    assert isinstance(generated, dict)
    wrapper = generated["wrapper"]
    assert isinstance(wrapper, dict)
    source_record = wrapper["source"]
    assert isinstance(source_record, dict)
    source = base64.b64decode(str(source_record["base64"])).decode("utf-8")
    if source.count(old) != 1:
        raise AssertionError(f"wrapper replacement cardinality differs: {old!r}")
    source = source.replace(old, new, 1)
    wrapper["source"] = make_blob_record(source)
    metadata = wrapper["metadata"]
    assert isinstance(metadata, dict)
    metadata["source_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    _reseal_bundle(bundle)


class Goal5840IndependentTargetCheckerTest(unittest.TestCase):
    def test_cp004_accepts_all_four_real_wrapper_shapes(self) -> None:
        from rtdsl.v4_bounded_relation_optix_wrapper_codegen import (
            generate_trusted_bounded_relation_wrapper_v1,
        )
        from rtdsl.v4_sphere_any_hit_count_contract import (
            build_sphere_any_hit_count_authority,
        )
        from rtdsl.v4_sphere_any_hit_count_wrapper_codegen import (
            generate_trusted_optix_sphere_any_hit_count_wrapper_v1,
        )
        from rtdsl.v4_triangle_reduction_optix_wrapper_codegen import (
            generate_trusted_optix_triangle_reduction_wrapper_v1,
        )
        from scripts.goal5758_m1_consumer_fixtures import (
            all_hit_schema,
            compile_count_callback,
            weighted_schema,
        )
        from tests.goal5759_v4_triangle_reduction_target_test import (
            _compiled as compiled_triangle,
        )
        from tests.goal5760_v4_bounded_relation_test import (
            _compiled as compiled_bounded,
        )
        from tests.goal5838_selected_sphere_any_hit_count_test import (
            _target as sphere_target,
        )

        bounded_authority, bounded_proof, bounded_abi, bounded_contract = (
            compiled_bounded()
        )
        bounded = generate_trusted_bounded_relation_wrapper_v1(
            bounded_authority,
            bounded_contract,
            bounded_abi,
            any_hit_proof_authority=bounded_proof,
        )
        bounded_flow = checker._check_wrapper_status_flow(ROUTES[0], bounded.source)
        self.assertEqual(bounded_flow["kind"], "bounded_fail_closed_collection")

        count_callback = compile_count_callback()
        for mode, schema in (
            ("all_hit_count", all_hit_schema(count_callback)),
            ("weighted_hit_count", weighted_schema(count_callback)),
        ):
            with self.subTest(mode=mode):
                authority, proof, abi, contract = compiled_triangle(
                    count_callback, schema
                )
                triangle = generate_trusted_optix_triangle_reduction_wrapper_v1(
                    authority,
                    contract,
                    abi,
                    any_hit_proof_authority=proof,
                )
                flow = checker._check_wrapper_status_flow(
                    ROUTES[1], triangle.source
                )
                self.assertEqual(
                    flow["kind"], "triangle_dual_path_status_gated_reduction"
                )

        sphere_authority, _proof, sphere_abi, _behavior = (
            build_sphere_any_hit_count_authority(sphere_target())
        )
        sphere = generate_trusted_optix_sphere_any_hit_count_wrapper_v1(
            sphere_authority,
            sphere_authority.canonical_plan,
            sphere_abi,
        )
        sphere_flow = checker._check_wrapper_status_flow(ROUTES[2], sphere.source)
        self.assertEqual(sphere_flow["kind"], "sphere_status_gated_count")

    def test_checker_imports_only_python_standard_library(self) -> None:
        path = Path(checker.__file__)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertEqual(
            imported_roots,
            {
                "__future__", "argparse", "ast", "base64", "collections",
                "hashlib", "json", "pathlib", "re", "typing",
            },
        )

    def test_checker_runs_isolated_without_repository_package_path(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        with tempfile.TemporaryDirectory() as name:
            bundle_path = Path(name) / "bundle.json"
            bundle_path.write_text(
                json.dumps(bundle, sort_keys=True), encoding="ascii"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(Path(checker.__file__).resolve()),
                    str(bundle_path),
                    "--trusted-declaration-sha256",
                    declaration_sha,
                    "--trusted-executable-identity-sha256",
                    identity_sha,
                    "--trusted-control-flow-manifest-sha256",
                    control_flow_sha,
                ],
                cwd=name,
                env={"PATH": str(Path(sys.executable).parent)},
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["verdict"], "ACCEPT")

    def test_all_three_bounded_route_fixtures_pass_all_five_properties(self) -> None:
        for route_id in ROUTES:
            with self.subTest(route_id=route_id):
                bundle, declaration_sha, identity_sha, control_flow_sha = (
                    _make_bundle(route_id)
                )
                report = checker.check_target_evidence(
                    bundle,
                    trusted_declaration_sha256=declaration_sha,
                    trusted_executable_identity_sha256=identity_sha,
                    trusted_control_flow_manifest_sha256=control_flow_sha,
                )
                self.assertEqual(report["verdict"], "ACCEPT", report)
                self.assertEqual(report["pass_count"], 5)
                self.assertEqual(report["reject_count"], 0)

    def test_inline_route_accepts_optimized_ptx_without_leaf_symbols(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        generated = bundle["generated_target_artifacts"]
        assert isinstance(generated, dict)
        composed = generated["composed_ptx"]
        assert isinstance(composed, dict)
        ptx = base64.b64decode(str(composed["base64"])).decode("utf-8")
        wrapper = generated["wrapper"]
        assert isinstance(wrapper, dict)
        metadata = wrapper["metadata"]
        assert isinstance(metadata, dict)
        for _role, symbol in metadata["role_symbols"]:
            self.assertNotIn(symbol, ptx)
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        self.assertEqual(report["verdict"], "ACCEPT", report)

    def test_inline_effect_drift_rejects_cp001_itself(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        _replace_wrapper_source(
            bundle,
            "    out_effect_tag[0] = 5;\n",
            "    out_effect_tag[0] = 7;\n",
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp001 = report["property_checks"][0]
        self.assertEqual(cp001["property_id"], "CP001_ROLE_EFFECT_CLOSURE")
        self.assertEqual(cp001["verdict"], "REJECT")
        self.assertEqual(
            cp001["reason_id"], "TC001_INLINE_OR_PARTIAL_EFFECT_MISMATCH"
        )

    def test_partial_evaluation_drift_rejects_cp001_itself(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        _replace_wrapper_source(
            bundle,
            "    optixSetPayload_0(updated_count);\n",
            "    /* removed accept-continue payload update */\n",
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp001 = report["property_checks"][0]
        self.assertEqual(cp001["verdict"], "REJECT")
        self.assertEqual(
            cp001["reason_id"], "TC001_PARTIAL_EVAL_ANY_HIT_MISMATCH"
        )

    def test_partial_evaluation_comment_spoof_rejects_cp001_itself(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        _replace_wrapper_source(
            bundle,
            "    optixSetPayload_0(updated_count);\n",
            "    /* optixSetPayload_0(updated_count); */\n",
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp001 = report["property_checks"][0]
        self.assertEqual(cp001["verdict"], "REJECT")
        self.assertEqual(
            cp001["reason_id"], "TC001_PARTIAL_EVAL_ANY_HIT_MISMATCH"
        )

    def test_inline_preimage_drift_rejects_cp005_recomputation(self) -> None:
        for field, reason in (
            ("inline_cuda", "TC005_INLINE_SOURCE_PREIMAGE_MISMATCH"),
            ("inline_cuda_leaves", "TC005_INLINE_LEAF_PREIMAGE_MISMATCH"),
        ):
            with self.subTest(field=field):
                bundle, _declaration_sha, _identity_sha, _control_flow_sha = (
                    _make_bundle(ROUTES[0])
                )
                generated = bundle["generated_target_artifacts"]
                assert isinstance(generated, dict)
                executable = generated["executable_metadata"]
                assert isinstance(executable, dict)
                preimage = executable["identity_preimage"]
                assert isinstance(preimage, dict)
                if field == "inline_cuda":
                    preimage[field] = "0" * 64
                else:
                    rows = preimage[field]
                    assert isinstance(rows, list)
                    rows[0][1] = "0" * 64
                plan = bundle["declaration"]
                assert isinstance(plan, dict)
                with self.assertRaises(checker.IndependentTargetCheckError) as caught:
                    checker._generated_identity_facts(
                        bundle,
                        plan["family_plan"],
                        target_sha256=bundle["physical_evidence"][
                            "executable_identity"
                        ]["target_sha256"],
                    )
                self.assertEqual(caught.exception.reason_id, reason)

    def test_sphere_inner_plan_is_independently_derived_from_outer_bindings(
        self,
    ) -> None:
        route_id = checker.SPHERE_ROUTE_ID
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        declaration = bundle["declaration"]
        physical = bundle["physical_evidence"]
        generated = bundle["generated_target_artifacts"]
        assert isinstance(declaration, dict)
        assert isinstance(physical, dict)
        assert isinstance(generated, dict)
        plan = declaration["family_plan"]
        identity = physical["executable_identity"]
        executable = generated["executable_metadata"]
        assert isinstance(plan, dict)
        assert isinstance(identity, dict)
        assert isinstance(executable, dict)
        preimage = executable["identity_preimage"]
        assert isinstance(preimage, dict)

        self.assertNotEqual(declaration["plan_sha256"], preimage["plan_sha256"])
        generated_facts = checker._generated_identity_facts(
            bundle,
            plan,
            target_sha256=identity["target_sha256"],
        )
        refinement = generated_facts["physical_plan_refinement"]
        assert isinstance(refinement, dict)
        self.assertEqual(
            refinement["physical_plan_sha256"], preimage["plan_sha256"]
        )
        self.assertEqual(
            refinement["authority_sha256"], preimage["authority_sha256"]
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        self.assertEqual(report["verdict"], "ACCEPT", report)
        self.assertEqual(report["pass_count"], 5)

    def test_sphere_plan_refinement_rejects_each_untrusted_bridge_drift(
        self,
    ) -> None:
        route_id = checker.SPHERE_ROUTE_ID
        cases = (
            (
                "inner_plan",
                "TC005_EXECUTABLE_PREIMAGE_PLAN_MISMATCH",
            ),
            (
                "physical_authority",
                "TC005_EXECUTABLE_PREIMAGE_AUTHORITY_MISMATCH",
            ),
            (
                "native_runtime_nonce",
                "TC005_SPHERE_RUNTIME_AUTHORITY_NONCE_MISMATCH",
            ),
            (
                "traversal_runtime_nonce",
                "TC005_SPHERE_RUNTIME_AUTHORITY_NONCE_MISMATCH",
            ),
            (
                "behavior_physical_schema",
                "TC005_SPHERE_BEHAVIOR_PLAN_BINDING_MISMATCH",
            ),
            (
                "protocol_physical_authority",
                "TC005_SPHERE_PHYSICAL_AUTHORITY_BINDING_MISMATCH",
            ),
            (
                "outer_callback",
                "TC005_WRAPPER_PLAN_IDENTITY_MISMATCH",
            ),
            (
                "outer_effect",
                "TC005_LEAF_IDENTITY_MISMATCH",
            ),
            (
                "target",
                "TC005_SPHERE_RUNTIME_AUTHORITY_NONCE_MISMATCH",
            ),
            (
                "physical_template",
                "TC005_SPHERE_PHYSICAL_TEMPLATE_MISMATCH",
            ),
            (
                "behavior_contract",
                "TC005_SPHERE_BEHAVIOR_CONTRACT_MISMATCH",
            ),
        )
        for mutation, reason in cases:
            with self.subTest(mutation=mutation):
                bundle, _declaration_sha, _identity_sha, _control_flow_sha = (
                    _make_bundle(route_id)
                )
                declaration = bundle["declaration"]
                physical = bundle["physical_evidence"]
                generated = bundle["generated_target_artifacts"]
                receipt = bundle["execution_receipt"]
                assert isinstance(declaration, dict)
                assert isinstance(physical, dict)
                assert isinstance(generated, dict)
                assert isinstance(receipt, dict)
                plan = declaration["family_plan"]
                identity = physical["executable_identity"]
                executable = generated["executable_metadata"]
                assert isinstance(plan, dict)
                assert isinstance(identity, dict)
                assert isinstance(executable, dict)
                preimage = executable["identity_preimage"]
                assert isinstance(preimage, dict)
                if mutation == "inner_plan":
                    preimage["plan_sha256"] = "0" * 64
                elif mutation == "physical_authority":
                    preimage["authority_sha256"] = "0" * 64
                elif mutation == "native_runtime_nonce":
                    native = physical["native_producer_descriptor"]
                    assert isinstance(native, dict)
                    runtime = native["runtime_physical_receipt"]
                    assert isinstance(runtime, dict)
                    runtime["authority_nonce"] = "0" * 64
                elif mutation == "traversal_runtime_nonce":
                    traversal = receipt["traversal_receipt"]
                    assert isinstance(traversal, dict)
                    runtime = traversal["physical_receipt"]
                    assert isinstance(runtime, dict)
                    runtime["authority_nonce"] = "0" * 64
                elif mutation == "behavior_physical_schema":
                    artifacts = bundle["program_artifacts"]
                    assert isinstance(artifacts, list)
                    row = next(
                        item
                        for item in artifacts
                        if item["artifact_id"] == "rtdl.behavior.schema"
                    )
                    payload = row["payload"]
                    assert isinstance(payload, dict)
                    behavior = json.loads(
                        base64.b64decode(payload["base64"]).decode("ascii")
                    )
                    behavior["physical_schema_sha256"] = "0" * 64
                    row["payload"] = make_blob_record(_canonical(behavior))
                elif mutation == "protocol_physical_authority":
                    instance = plan["protocol_instance"]
                    assert isinstance(instance, dict)
                    authorities = instance["authorities"]
                    assert isinstance(authorities, list)
                    authorities[0]["authority_sha256"] = "0" * 64
                elif mutation == "outer_callback":
                    plan["callback_ir_sha256"] = "0" * 64
                elif mutation == "outer_effect":
                    plan["effect_digest"] = "0" * 64
                elif mutation == "target":
                    identity["target_sha256"] = "0" * 64
                elif mutation == "physical_template":
                    plan["canonical_template_id"] = "attacker.template"
                else:
                    artifacts = bundle["program_artifacts"]
                    assert isinstance(artifacts, list)
                    row = next(
                        item
                        for item in artifacts
                        if item["artifact_id"] == "rtdl.behavior.schema"
                    )
                    payload = row["payload"]
                    assert isinstance(payload, dict)
                    behavior = json.loads(
                        base64.b64decode(payload["base64"]).decode("ascii")
                    )
                    behavior["continuation"] = "terminate_on_first_hit"
                    row["payload"] = make_blob_record(_canonical(behavior))
                with self.assertRaises(
                    checker.IndependentTargetCheckError
                ) as caught:
                    checker._generated_identity_facts(
                        bundle,
                        plan,
                        target_sha256=identity["target_sha256"],
                    )
                self.assertEqual(caught.exception.reason_id, reason)

    def test_sphere_self_consistent_inner_rewrite_cannot_replace_trusted_identity(
        self,
    ) -> None:
        route_id = checker.SPHERE_ROUTE_ID
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        declaration = bundle["declaration"]
        generated = bundle["generated_target_artifacts"]
        physical = bundle["physical_evidence"]
        receipt = bundle["execution_receipt"]
        assert isinstance(declaration, dict)
        assert isinstance(generated, dict)
        assert isinstance(physical, dict)
        assert isinstance(receipt, dict)
        plan = declaration["family_plan"]
        executable = generated["executable_metadata"]
        identity = physical["executable_identity"]
        target = physical["target_binding"]
        native_descriptor = physical["native_producer_descriptor"]
        traversal = receipt["traversal_receipt"]
        assert isinstance(plan, dict)
        assert isinstance(executable, dict)
        assert isinstance(identity, dict)
        assert isinstance(target, dict)
        assert isinstance(native_descriptor, dict)
        assert isinstance(traversal, dict)
        preimage = executable["identity_preimage"]
        runtime_receipt = native_descriptor["runtime_physical_receipt"]
        traversal_physical = traversal["physical_receipt"]
        assert isinstance(preimage, dict)
        assert isinstance(runtime_receipt, dict)
        assert isinstance(traversal_physical, dict)

        physical_schema_sha = next(
            row["authority_sha256"]
            for row in plan["protocol_instance"]["authorities"]
            if row["authority_kind"] == "physical_schema"
        )
        attacker_target_sha = _sha("attacker:replacement-target")
        attacker_nonce = _digest({
            "kind": "builtin_sphere_any_hit_count_physical_authority_v1",
            "callback": plan["callback_ir_sha256"],
            "effect": plan["effect_digest"],
            "schema": physical_schema_sha,
            "target": attacker_target_sha,
        })
        preimage["authority_sha256"] = _digest({
            "callback_ir_sha256": plan["callback_ir_sha256"],
            "callback_effect_digest": plan["effect_digest"],
            "schema_sha256": physical_schema_sha,
            "target_sha256": attacker_target_sha,
            "authority_nonce": attacker_nonce,
        })
        preimage["plan_sha256"] = _digest({
            "schema_sha256": physical_schema_sha,
            "callback_ir_sha256": plan["callback_ir_sha256"],
            "effect_digest": plan["effect_digest"],
            "target_sha256": attacker_target_sha,
            "authority_nonce": attacker_nonce,
            "template_id": checker.SPHERE_PHYSICAL_TEMPLATE,
            "executable": False,
        })
        executable["executable_sha256"] = _digest(preimage)
        identity["target_sha256"] = attacker_target_sha
        identity["executable_sha256"] = executable["executable_sha256"]
        _sealed(identity, "identity_sha256")
        target["target_sha256"] = attacker_target_sha
        receipt["target_sha256"] = attacker_target_sha
        receipt["executable_identity_sha256"] = identity["identity_sha256"]
        runtime_receipt["authority_nonce"] = attacker_nonce
        traversal_physical["authority_nonce"] = attacker_nonce
        _reseal_bundle(bundle)

        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp005 = next(
            row
            for row in report["property_checks"]
            if row["property_id"] == "CP005_EXECUTABLE_IDENTITY_CHAIN"
        )
        self.assertEqual(cp005["verdict"], "REJECT")
        self.assertEqual(
            cp005["reason_id"], "TC005_EXECUTABLE_IDENTITY_TRUST_MISMATCH"
        )

    def test_real_route_plans_and_sources_satisfy_control_flow_extractors(self) -> None:
        bounded_protocol = BoundedRelationProtocol(16, 0.25)
        triangle_all = TriangleReductionProtocol(
            TriangleReductionMode.ALL_HIT_COUNT
        )
        triangle_weighted = TriangleReductionProtocol(
            TriangleReductionMode.WEIGHTED_HIT_COUNT
        )
        rows = (
            (
                ROUTES[0],
                bounded_relation_family_route(
                    bounded_protocol, _proof(bounded_protocol, "real-bounded")
                ),
            ),
            (
                ROUTES[1],
                triangle_reduction_family_route(
                    triangle_all, _proof(triangle_all, "real-triangle-all")
                ),
            ),
            (
                ROUTES[1],
                triangle_reduction_family_route(
                    triangle_weighted,
                    _proof(triangle_weighted, "real-triangle-weighted"),
                ),
            ),
            (ROUTES[2], sphere_any_hit_count_family_route()),
        )
        for route_id, route in rows:
            with self.subTest(route_id=route_id, plan=route.plan.plan_sha256):
                control = capture_target_control_flow_evidence(route_id)
                sources = {
                    row["repository_path"]: base64.b64decode(
                        row["payload"]["base64"]
                    ).decode("utf-8")
                    for row in control["sources"]
                }
                checker._check_declared_continuation(
                    route.plan.to_dict()["family_shape"], route_id
                )
                native = checker._check_native_producer_source(route_id, sources)
                self.assertEqual(
                    native["build_input_type"],
                    checker.ROUTE_RULES[route_id]["native_names"][1],
                )
                checker._check_host_status_flow(route_id, sources)

    def test_all_fifteen_preregistered_mutation_units_reject_target_property(self) -> None:
        for route_id in ROUTES:
            for property_id in checker.PROPERTIES:
                with self.subTest(route_id=route_id, property_id=property_id):
                    bundle, declaration_sha, identity_sha, control_flow_sha = (
                        _make_bundle(route_id)
                    )
                    mutated, selector, replacement = (
                        mutation_suite.apply_frozen_mutation(
                            bundle, route_id, property_id
                        )
                    )
                    frozen = FROZEN_MUTATIONS[(route_id, property_id)]
                    self.assertEqual(selector, frozen["target_selector"])
                    self.assertEqual(replacement, frozen["replacement"])
                    report = checker.check_target_evidence(
                        mutated,
                        trusted_declaration_sha256=declaration_sha,
                        trusted_executable_identity_sha256=identity_sha,
                        trusted_control_flow_manifest_sha256=control_flow_sha,
                    )
                    row = next(
                        item for item in report["property_checks"]
                        if item["property_id"] == property_id
                    )
                    self.assertEqual(report["verdict"], "REJECT")
                    self.assertEqual(row["verdict"], "REJECT", report)
                    self.assertTrue(row["reason_id"].startswith("TC"), report)

    def test_exact_bundle_suite_runs_twenty_mode_replications(self) -> None:
        fixtures = [
            _make_bundle(ROUTES[0]),
            _make_bundle(ROUTES[1], mode="all_hit_count"),
            _make_bundle(ROUTES[1], mode="weighted_hit_count"),
            _make_bundle(ROUTES[2]),
        ]
        bundles = []
        trust_roots = {}
        for bundle, declaration_sha, identity_sha, control_flow_sha in fixtures:
            bundles.append(bundle)
            route_id = str(bundle["route_id"])
            mode = str(bundle["execution_receipt"]["mode"])
            trust_roots[f"{route_id}::{mode}"] = {
                "declaration_sha256": declaration_sha,
                "executable_identity_sha256": identity_sha,
                "control_flow_manifest_sha256": control_flow_sha,
            }
        report = mutation_suite.run_exact_bundle_mutations(
            bundles, trust_roots
        )
        self.assertEqual(report["preregistered_claim_unit_count"], 15)
        self.assertEqual(report["mode_replication_application_count"], 20)
        self.assertEqual(report["rejected_application_count"], 20)
        self.assertTrue(report["all_rejected_before_gpu_launch"])

    def test_wrong_external_trust_roots_fail_cp005(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        for trusted_declaration, trusted_identity, trusted_control in (
            (_sha("wrong-declaration"), identity_sha, control_flow_sha),
            (declaration_sha, _sha("wrong-identity"), control_flow_sha),
            (declaration_sha, identity_sha, _sha("wrong-control-flow")),
        ):
            report = checker.check_target_evidence(
                bundle,
                trusted_declaration_sha256=trusted_declaration,
                trusted_executable_identity_sha256=trusted_identity,
                trusted_control_flow_manifest_sha256=trusted_control,
            )
            self.assertEqual(report["verdict"], "REJECT" if trusted_control == control_flow_sha else "UNRESOLVED")
            if trusted_control == control_flow_sha:
                cp005 = report["property_checks"][-1]
                self.assertEqual(cp005["verdict"], "REJECT")

    def test_forged_triangle_mode_rejects_cp004(self) -> None:
        route_id = ROUTES[1]
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        bundle["execution_receipt"]["mode"] = "weighted_hit_count"
        _reseal_bundle(bundle)
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp004 = next(
            row for row in report["property_checks"]
            if row["property_id"]
            == "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS"
        )
        self.assertEqual(cp004["verdict"], "REJECT")
        self.assertEqual(cp004["reason_id"], "TC004_MODE_PLAN_MISMATCH")

    def test_triangle_fast_status_after_output_rejects_cp004(self) -> None:
        route_id = ROUTES[1]
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        _replace_wrapper_source(
            bundle,
            """extern \"C\" __global__ void __raygen__rtdl_v4_triangle_reduction() {
    optixTrace(params.traversable);
    if (params.fast_control->error_code != 0u) return;
    const unsigned long long final_value = 1u;
    params.per_ray_u64[query] = final_value;
}""",
            """extern \"C\" __global__ void __raygen__rtdl_v4_triangle_reduction() {
    optixTrace(params.traversable);
    const unsigned long long final_value = 1u;
    params.per_ray_u64[query] = final_value;
    if (params.fast_control->error_code != 0u) return;
}""",
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp004 = next(
            row for row in report["property_checks"]
            if row["property_id"]
            == "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS"
        )
        self.assertEqual(cp004["verdict"], "REJECT")
        self.assertEqual(cp004["reason_id"], "TC004_STATUS_AFTER_OUTPUT")

    def test_triangle_diagnostic_status_comment_spoof_rejects_cp004(self) -> None:
        route_id = ROUTES[1]
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        _replace_wrapper_source(
            bundle,
            "    } else if (params.status[query].first_error_claimed != 0u) return;\n",
            (
                "    } /* else if "
                "(params.status[query].first_error_claimed != 0u) return; */\n"
            ),
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp004 = next(
            row for row in report["property_checks"]
            if row["property_id"]
            == "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS"
        )
        self.assertEqual(cp004["verdict"], "REJECT")
        self.assertEqual(
            cp004["reason_id"], "TC004_STATUS_SOURCE_ANCHOR_MISSING"
        )

    def test_triangle_diagnostic_status_string_spoof_rejects_cp004(self) -> None:
        route_id = ROUTES[1]
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        _replace_wrapper_source(
            bundle,
            "    } else if (params.status[query].first_error_claimed != 0u) return;\n",
            (
                "    } const char* fake_status_gate = \"else if "
                "(params.status[query].first_error_claimed != 0u) return;\";\n"
            ),
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp004 = next(
            row for row in report["property_checks"]
            if row["property_id"]
            == "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS"
        )
        self.assertEqual(cp004["verdict"], "REJECT")
        self.assertEqual(
            cp004["reason_id"], "TC004_STATUS_SOURCE_ANCHOR_MISSING"
        )

    def test_triangle_finalizer_status_commit_removal_rejects_cp004(self) -> None:
        route_id = ROUTES[1]
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            route_id
        )
        _replace_wrapper_source(
            bundle,
            "    if (!v4_commit_leaf_status(query, fin_status_ok)) { return; }\n",
            "    /* finalizer status commit removed */\n",
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        cp004 = next(
            row for row in report["property_checks"]
            if row["property_id"]
            == "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS"
        )
        self.assertEqual(cp004["verdict"], "REJECT")
        self.assertEqual(
            cp004["reason_id"], "TC004_STATUS_SOURCE_ANCHOR_MISSING"
        )

    def test_report_never_issues_capability_or_broad_claim(self) -> None:
        bundle, declaration_sha, identity_sha, control_flow_sha = _make_bundle(
            ROUTES[0]
        )
        report = checker.check_target_evidence(
            bundle,
            trusted_declaration_sha256=declaration_sha,
            trusted_executable_identity_sha256=identity_sha,
            trusted_control_flow_manifest_sha256=control_flow_sha,
        )
        boundary = report["claim_boundary"]
        self.assertFalse(boundary["executable_capability_issued"])
        self.assertFalse(boundary["general_compiler_soundness"])
        self.assertFalse(boundary["external_review_or_consensus"])


if __name__ == "__main__":
    unittest.main()
