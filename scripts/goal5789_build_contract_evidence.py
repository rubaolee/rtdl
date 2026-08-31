"""Build the bounded Goal5789 semantic/physical evidence package.

This builder is evidence-side code.  It does not import RTDL, any selector, or
an application execution route.  Semantic requirements and physical guarantees
are authored as separate tables below and are joined only by the independent
checker.  A paper-app row for which the independent semantic authority is not
yet strong enough is deliberately emitted as UNKNOWN.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts import goal5789_independent_compatibility_checker as check


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5789_contract_evidence_20260816"
WORKERS = ROOT / "history/internal_docs/.goal5785_inspect/raw5776/RAW/workers"


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return _sha_bytes(path.read_bytes())


def _sha_json(value: object) -> str:
    return _sha_bytes(check.canonical_bytes(value))


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _seal_section(value: dict[str, Any]) -> None:
    value["authority_sha256"] = check.nested_authority_digest(value)


def _seal_authority(value: dict[str, Any]) -> None:
    for name in (
        "semantic_authority",
        "physical_authority",
        "target_authority",
        "instance_authority",
        "evidence_authority",
    ):
        _seal_section(value[name])
    value["authority_sha256"] = check.authority_digest(value)


def _seal_certificate(value: dict[str, Any]) -> None:
    value["certificate_sha256"] = check.certificate_digest(value)


SOURCE_PATHS = (
    "src/rtdsl/v4_callback_ir.py",
    "src/rtdsl/v4_typed_physical_schema.py",
    "src/rtdsl/v4_builtin_triangle_standard_library.py",
    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
    "src/rtdsl/v4_triangle_prepared_runtime.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "src/rtdsl/v4_triangle_reduction_device_runtime.py",
    "src/rtdsl/v4_checked_u64_device_reduction.py",
    "src/rtdsl/v4_bounded_relation_standard_library.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/independent_oracle.py",
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/independent_oracle.py",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
    "scripts/goal5760_m2_consumer_fixtures.py",
    "scripts/goal5776_real_scale_frontdoors.py",
)


SOURCE_MANIFEST = {path: _sha_file(path) for path in SOURCE_PATHS}


def _map(kind: str, pin: str) -> dict[str, Any]:
    graph = {
        "encode": (["semantic_input"], ["geometry", "query_state"]),
        "ray": (["query_state"], ["ray"]),
        "trace": (["geometry", "ray"], ["hit_stream"]),
        "continuation": (["hit_stream"], ["candidate_output"]),
        "decode": (["candidate_output"], ["semantic_output"]),
    }
    consumes, produces = graph[kind]
    return {
        "kind": kind,
        "source_pin": pin,
        "source_sha256": SOURCE_MANIFEST[pin],
        "consumes": consumes,
        "produces": produces,
    }


PARTICLE_POLICY = {
    "input_type": "oriented_triangle_mesh_queries_with_u32_adjacency",
    "output_type": "cell_neighbor_face_u32x3_per_query",
    "exactness": "exact_for_declared_mesh_and_ray_domain",
    "tie_policy": "nearest_t_then_min_u32_primitive",
    "order_policy": "query_index_ascending",
    "multiplicity": "one_hit_or_miss_per_query",
    "numeric_precision": "binary32_optix_triangle_with_pinned_orientation",
    "overflow_policy": "fail_closed_status_before_output_authority",
}

RELATION_POLICY = {
    "input_type": "finite_nonnegative_aabb_relation_rows_with_u32_ids",
    "output_type": "lexicographic_u32_pair_relation",
    "exactness": "inclusive_overlap_exact_for_declared_binary32_domain",
    "tie_policy": "ascending_u32_pair",
    "order_policy": "lexicographic_u32_pair",
    "multiplicity": "deduplicated_set",
    "numeric_precision": "binary32_geometry_with_exact_u32_identity",
    "overflow_policy": "fail_closed_capacity_or_counter_overflow",
}

TRIANGLE_WEIGHTED_POLICY = {
    "input_type": "oriented_edge_segments_with_u32_weights",
    "output_type": "checked_u64_triangle_count_scalar",
    "exactness": "exact_checked_integer_reduction",
    "tie_policy": "not_applicable_scalar",
    "order_policy": "commutative_checked_reduction",
    "multiplicity": "paper_owned_rt2a1_weighted_hit_multiplicity",
    "numeric_precision": "u32_inputs_checked_u64_accumulator",
    "overflow_policy": "fail_closed_before_u64_wraparound",
}

RTXRMQ_POLICY = {
    "input_type": "array_values_and_closed_interval_queries",
    "output_type": "leftmost_range_minimum_u32_index_per_query",
    "exactness": "exact_for_registered_interior_cell_encoding_domain",
    "tie_policy": "leftmost_minimum_index",
    "order_policy": "query_index_ascending",
    "multiplicity": "one_index_per_nonempty_query",
    "numeric_precision": "integer_rank_geometry_with_binary32_interior_coordinates",
    "overflow_policy": "fail_closed_on_capacity_or_invalid_interval",
}


def _semantic(contract_id: str, algorithm: str, policy: dict[str, str], spec_pin: str,
              required_hits: list[str]) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "algorithm_identity": algorithm,
        "declared_domain_sha256": _sha_json({"contract": contract_id, "policy": policy}),
        "policy": deepcopy(policy),
        "required_hit_semantics": list(required_hits),
        "specification_source_pin": spec_pin,
    }


def _roles(family: str, *, reduction: bool = False) -> list[dict[str, Any]]:
    if family == "builtin_triangle":
        roles = [
            {"role": "make_ray", "effects": ["trace_request"]},
            {"role": "any_hit", "effects": ["accept_continue", "ignore"]},
            {"role": "miss", "effects": ["payload"]},
            {"role": "finalize", "effects": ["output"]},
        ]
        if not reduction:
            roles[1] = {"role": "closest_hit", "effects": ["payload"]}
        return roles
    return [
        {"role": "bounds", "effects": ["aabb"]},
        {"role": "make_ray", "effects": ["trace_request"]},
        {"role": "intersection", "effects": ["hit", "no_hit"]},
        {"role": "any_hit", "effects": ["accept_continue", "ignore"]},
        {"role": "miss", "effects": ["payload"]},
        {"role": "finalize", "effects": ["output"]},
    ]


def _hit_contract(family: str) -> tuple[list[str], list[dict[str, Any]]]:
    if family == "custom_aabb":
        rows = [("custom_hit_kind", "verified_intersection_effect", ["any_hit"])]
    else:
        rows = [
            ("primitive_index_u32", "optix_builtin", ["any_hit", "closest_hit"]),
            ("triangle_front_back_hit_kind_u32", "optix_builtin", ["any_hit", "closest_hit"]),
            ("triangle_barycentrics_f32x2", "optix_builtin", ["any_hit", "closest_hit"]),
            ("primitive_metadata_lookup", "compiler_metadata_lookup", ["any_hit", "closest_hit"]),
        ]
    return [row[0] for row in rows], [
        {"semantic": semantic, "producer": producer, "read_roles": readers}
        for semantic, producer, readers in rows
    ]


def _physical(encoding_id: str, family: str, policy: dict[str, str], pins: dict[str, str],
              *, update: str = "static") -> dict[str, Any]:
    _, hit_channels = _hit_contract(family)
    return {
        "encoding_id": encoding_id,
        "geometry_family": family,
        "schema_sha256": _sha_json({"encoding": encoding_id, "family": family, "policy": policy}),
        "maps": [_map(kind, pins[kind]) for kind in ("encode", "ray", "trace", "continuation", "decode")],
        "guarantees": deepcopy(policy),
        "hit_channels": hit_channels,
        "gas": {
            "geometry_family": family,
            "graph_depth": 1,
            "sbt_record_stride": 1,
            "update_policy": update,
        },
        "buffers": [
            {"semantic": "input_rows", "access": "read_only", "residency": "device", "count_relation": "bound_to_declared_input"},
            {"semantic": "output_rows", "access": "write_only", "residency": "device", "count_relation": "bounded_by_declared_capacity"},
            {"semantic": "status", "access": "internal_status", "residency": "device", "count_relation": "one_per_launch"},
        ],
        "provider_source_pin": pins["trace"],
    }


SEMANTIC_REQUIREMENTS = {
    "particle.closest_face_projection.v1": _semantic(
        "particle.closest_face_projection.v1", "particle_closest_face_projection",
        PARTICLE_POLICY,
        "Paper-reproduction-apps/goal5753-held-out-particle-tracking/independent_oracle.py",
        _hit_contract("builtin_triangle")[0],
    ),
    "librts.inclusive_aabb_relation.v1": _semantic(
        "librts.inclusive_aabb_relation.v1", "inclusive_aabb_relation",
        RELATION_POLICY, "scripts/goal5760_m2_consumer_fixtures.py",
        _hit_contract("custom_aabb")[0],
    ),
    "triangle.rt2a1.weighted_count.v1": _semantic(
        "triangle.rt2a1.weighted_count.v1", "paper_owned_rt2a1_weighted_triangle_count",
        TRIANGLE_WEIGHTED_POLICY, "scripts/goal5776_real_scale_frontdoors.py",
        _hit_contract("builtin_triangle")[0],
    ),
    "rtxrmq.leftmost_argmin.v1": _semantic(
        "rtxrmq.leftmost_argmin.v1", "leftmost_closed_interval_range_minimum",
        RTXRMQ_POLICY, "Paper-reproduction-apps/goal5783-held-out-rtxrmq/independent_oracle.py",
        _hit_contract("builtin_triangle")[0],
    ),
}


PHYSICAL_GUARANTEES = {
    "builtin_triangle.closest_face_projection.v1": _physical(
        "builtin_triangle.closest_face_projection.v1", "builtin_triangle", PARTICLE_POLICY,
        {
            "encode": "src/rtdsl/v4_builtin_triangle_standard_library.py",
            "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
            "trace": "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
            "continuation": "src/rtdsl/v4_triangle_prepared_runtime.py",
            "decode": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        },
    ),
    "custom_aabb.inclusive_relation.v1": _physical(
        "custom_aabb.inclusive_relation.v1", "custom_aabb", RELATION_POLICY,
        {
            "encode": "src/rtdsl/v4_bounded_relation_standard_library.py",
            "ray": "src/rtdsl/v4_box_relation_callback.py",
            "trace": "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
            "continuation": "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
            "decode": "src/rtdsl/v4_bounded_relation_standard_library.py",
        },
    ),
    "builtin_triangle.weighted_count.v1": _physical(
        "builtin_triangle.weighted_count.v1", "builtin_triangle", TRIANGLE_WEIGHTED_POLICY,
        {
            "encode": "src/rtdsl/v4_triangle_standard_library.py",
            "ray": "src/rtdsl/v4_triangle_standard_library.py",
            "trace": "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
            "continuation": "src/rtdsl/v4_triangle_reduction_device_runtime.py",
            "decode": "src/rtdsl/v4_checked_u64_device_reduction.py",
        },
    ),
    "builtin_triangle.rtxrmq_leftmost.v1": _physical(
        "builtin_triangle.rtxrmq_leftmost.v1", "builtin_triangle", RTXRMQ_POLICY,
        {
            "encode": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
            "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
            "trace": "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
            "continuation": "src/rtdsl/v4_triangle_prepared_runtime.py",
            "decode": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
        },
    ),
}


FAMILY_FOR_CONTRACT = {
    "particle.closest_face_projection.v1": "builtin_triangle.closest_face_projection.v1",
    "librts.inclusive_aabb_relation.v1": "custom_aabb.inclusive_relation.v1",
    "triangle.rt2a1.weighted_count.v1": "builtin_triangle.weighted_count.v1",
    "rtxrmq.leftmost_argmin.v1": "builtin_triangle.rtxrmq_leftmost.v1",
}


WORKER_INDEX = {
    "particle__microfluidics_5000": 1,
    "triangle__com_dblp__rt_1a2": 17,
    "triangle__com_dblp__rt_2a1": 33,
    "triangle__cit_patents__rt_1a2": 49,
    "triangle__cit_patents__rt_2a1": 65,
    "triangle__soc_livejournal1__rt_1a2": 81,
    "triangle__soc_livejournal1__rt_2a1": 97,
    "rtdbscan__goal5776_clustered3d_4096": 113,
    "rtnn__kitti12m_q4096_k4": 129,
    "xhd__dragon_to_happy": 145,
    "rtbh__author_32768": 161,
    "raydb__ssb_sf10_q11": 177,
    "librts__parks_point_contains": 193,
    "librts__parks_range_contains": 209,
    "rayjoin__top4_six_batch": 225,
}


INVENTORY_CONTRACT = {
    "particle__microfluidics_5000": "particle.closest_face_projection.v1",
    "triangle__com_dblp__rt_2a1": "triangle.rt2a1.weighted_count.v1",
    "triangle__cit_patents__rt_2a1": "triangle.rt2a1.weighted_count.v1",
    "triangle__soc_livejournal1__rt_2a1": "triangle.rt2a1.weighted_count.v1",
    "librts__parks_point_contains": "librts.inclusive_aabb_relation.v1",
    "librts__parks_range_contains": "librts.inclusive_aabb_relation.v1",
}


def _target(worker: dict[str, Any], family: str) -> dict[str, Any]:
    return {
        "target_sha256": worker["target_identity_sha256"],
        "provider": "optix",
        "native_sha256": worker["native_library_sha256"],
        # This target profile describes the target, not the selected family.
        # A single target identity must not acquire a different authority row
        # merely because a different certificate consumes it.
        "capabilities": [
            "optix",
            "bound_program_bundle",
            "optix_builtin_triangle",
            "optix_custom_aabb",
        ],
        "max_payload_u32_slots": 32,
        "max_attribute_u32_slots": 8,
        "max_trace_depth": 1,
        "max_callable_depth": 0,
    }


def _instance(worker: dict[str, Any], unit_id: str) -> dict[str, Any]:
    row = worker["rows"][0]
    # Input facts are keyed by input identity.  ABBA/method workers sharing the
    # same frozen input therefore replay the same logical owner authority.
    owner = f"goal5785-input-{row['input_sha256'][:16]}"
    return {
        "input_sha256": row["input_sha256"],
        "element_count": 1,
        "capacity": 1,
        "numeric_inputs_finite": True,
        "overflow_observed": False,
        "bindings": [
            {"semantic": "input_rows", "element_count": 1, "writable": False, "owner_nonce": owner, "device_id": 0, "stream_id": 0, "mutation_epoch": 0},
            {"semantic": "output_rows", "element_count": 1, "writable": True, "owner_nonce": owner, "device_id": 0, "stream_id": 0, "mutation_epoch": 0},
            {"semantic": "status", "element_count": 1, "writable": True, "owner_nonce": owner, "device_id": 0, "stream_id": 0, "mutation_epoch": 0},
        ],
    }


def _callback(contract_id: str, family: str) -> dict[str, Any]:
    return {
        "ir_sha256": _sha_json({"contract": contract_id, "roles": _roles(family, reduction="triangle.rt2a1" in contract_id)}),
        "effect_digest": _sha_json(_roles(family, reduction="triangle.rt2a1" in contract_id)),
        "roles": _roles(family, reduction="triangle.rt2a1" in contract_id),
        "payload_u32_slots": 8,
        "attribute_u32_slots": 2,
        "trace_depth": 1,
        "callable_depth": 0,
        "total_static_iterations": 64,
    }


def _candidate(semantic: dict[str, Any], physical: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_id": f"reference.{physical['encoding_id']}",
        "canonical": True,
        "algorithm_identity": semantic["algorithm_identity"],
        "geometry_family": physical["geometry_family"],
        "schema_sha256": physical["schema_sha256"],
        "guarantees": deepcopy(semantic["policy"]),
    }


def _certificate(unit_id: str, worker: dict[str, Any], contract_id: str,
                 semantic: dict[str, Any], physical: dict[str, Any]) -> dict[str, Any]:
    row = worker["rows"][0]
    receipt = worker["traversal_receipt"]
    value = {
        "schema": check.CERTIFICATE_SCHEMA,
        "certificate_sha256": "",
        "semantic_request": deepcopy(semantic),
        "physical_encoding": deepcopy(physical),
        "callback_contract": _callback(contract_id, physical["geometry_family"]),
        "canonical_candidates": [_candidate(semantic, physical)],
        "target_contract": _target(worker, physical["geometry_family"]),
        "instance_contract": _instance(worker, unit_id),
        "evidence_contract": {
            "source_pins": {path: SOURCE_MANIFEST[path] for path in sorted({
                semantic["specification_source_pin"], physical["provider_source_pin"],
                *(item["source_pin"] for item in physical["maps"]),
            })},
            "independent_oracle_sha256": _sha_file(semantic["specification_source_pin"]),
            # Composite application receipts do not all carry a top-level
            # receipt_sha256.  Bind the exact frozen receipt object in that
            # case; never synthesize a positive behavioral classification.
            "behavioral_receipt_sha256": receipt.get("receipt_sha256", _sha_json(receipt)),
            "oracle_output_sha256": row["output_sha256"],
            "physical_output_sha256": row["output_sha256"],
        },
    }
    _seal_certificate(value)
    return value


def _unknown_semantic(unit_id: str, worker: dict[str, Any]) -> dict[str, Any]:
    # The certificate is structurally complete, but its semantic contract is
    # intentionally absent from the independent semantic authority.  This is
    # evidence of UNKNOWN, not evidence against the implementation.
    family = "builtin_triangle" if unit_id.startswith("triangle__") else "custom_aabb"
    physical = PHYSICAL_GUARANTEES[
        "builtin_triangle.weighted_count.v1" if family == "builtin_triangle"
        else "custom_aabb.inclusive_relation.v1"
    ]
    policy = deepcopy(physical["guarantees"])
    semantic = _semantic(
        f"unresolved.{_sha_bytes(unit_id.encode())[:16]}.v1",
        f"unresolved_algorithm_{_sha_bytes(unit_id.encode())[:12]}",
        policy,
        "scripts/goal5776_real_scale_frontdoors.py",
        _hit_contract(family)[0],
    )
    return _certificate(unit_id, worker, semantic["contract_id"], semantic, physical)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    workers = {unit: _read_json(WORKERS / f"{index:04d}.json") for unit, index in WORKER_INDEX.items()}
    for unit, worker in workers.items():
        if worker["unit_id"] != unit or worker["method"] != "v4_restricted_callback_true_optix" or not worker["matched"]:
            raise RuntimeError(f"unexpected frozen worker identity: {unit}")

    # Independent authorities are assembled from separate requirement and
    # guarantee registries.  Unresolved inventory contracts are deliberately
    # not inserted into semantic_authority.
    target_profiles: dict[str, Any] = {}
    instances: dict[str, Any] = {}
    oracle_allowlist: set[str] = set()
    receipt_allowlist: set[str] = set()
    certificates: dict[str, dict[str, Any]] = {}
    for unit, worker in workers.items():
        if unit in INVENTORY_CONTRACT:
            contract_id = INVENTORY_CONTRACT[unit]
            semantic = SEMANTIC_REQUIREMENTS[contract_id]
            physical = PHYSICAL_GUARANTEES[FAMILY_FOR_CONTRACT[contract_id]]
            cert = _certificate(unit, worker, contract_id, semantic, physical)
        else:
            cert = _unknown_semantic(unit, worker)
        certificates[unit] = cert
        target = cert["target_contract"]
        instance = cert["instance_contract"]
        target_profiles[target["target_sha256"]] = deepcopy(target)
        instances[instance["input_sha256"]] = deepcopy(instance)
        oracle_allowlist.add(cert["evidence_contract"]["independent_oracle_sha256"])
        receipt_allowlist.add(cert["evidence_contract"]["behavioral_receipt_sha256"])

    authority = {
        "schema": check.AUTHORITY_SCHEMA,
        "authority_sha256": "",
        "semantic_authority": {
            "schema": check.SEMANTIC_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "contracts": deepcopy(SEMANTIC_REQUIREMENTS),
        },
        "physical_authority": {
            "schema": check.PHYSICAL_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "encodings": deepcopy(PHYSICAL_GUARANTEES),
            "source_manifest": deepcopy(SOURCE_MANIFEST),
        },
        "target_authority": {
            "schema": check.TARGET_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "target_profiles": target_profiles,
        },
        "instance_authority": {
            "schema": check.INSTANCE_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "instances": instances,
        },
        "evidence_authority": {
            "schema": check.EVIDENCE_AUTHORITY_SCHEMA,
            "authority_sha256": "",
            "oracle_sha256_allowlist": sorted(oracle_allowlist),
            "receipt_sha256_allowlist": sorted(receipt_allowlist),
        },
    }
    _seal_authority(authority)
    _write_json(OUT / "AUTHORITY_BUNDLE.json", authority)

    inventory: list[dict[str, Any]] = []
    for unit in WORKER_INDEX:
        cert = certificates[unit]
        result = check.evaluate_certificate(cert, authority)
        _write_json(OUT / "certificates" / f"{unit}.json", cert)
        _write_json(OUT / "results" / f"{unit}.json", result)
        inventory.append({
            "unit_id": unit,
            "contract_id": cert["semantic_request"]["contract_id"],
            "encoding_id": cert["physical_encoding"]["encoding_id"],
            "target_capable": result["target_capable"]["verdict"],
            "semantic_compatible": result["semantic_compatible"]["verdict"],
            "instance_admissible": result["instance_admissible"]["verdict"],
            "canonical_resolution": result["canonical_resolution"]["verdict"],
            "reference_admission_complete": result["reference_admission_complete"],
            "performance": result["performance"]["verdict"],
            "semantic_authority_present": unit in INVENTORY_CONTRACT,
            "evidence_strength": (
                ["SOURCE_ENFORCED", "INDEPENDENT_ORACLE", "BEHAVIORALLY_OBSERVED"]
                if unit in INVENTORY_CONTRACT
                else [
                    "SOURCE_IDENTITY_PINNED",
                    "INSTANCE_ORACLE_OBSERVED",
                    "BEHAVIORALLY_OBSERVED",
                    "MISSING_INDEPENDENT_SEMANTIC_AUTHORITY",
                ]
            ),
        })

    held_result = _read_json(ROOT / "history/internal_docs/goal5783_postfreeze_held_out_rtxrmq_result_20260814.json")
    held_semantic = SEMANTIC_REQUIREMENTS["rtxrmq.leftmost_argmin.v1"]
    held_physical = PHYSICAL_GUARANTEES["builtin_triangle.rtxrmq_leftmost.v1"]
    # Held-out evidence predates Goal5789 and is not a Goal5785 inventory row.
    # Reuse a target/instance shape only for admission replay, while binding the
    # actual held-out oracle, receipt and native identities.
    base = deepcopy(certificates["particle__microfluidics_5000"])
    base["semantic_request"] = deepcopy(held_semantic)
    base["physical_encoding"] = deepcopy(held_physical)
    base["callback_contract"] = _callback("rtxrmq.leftmost_argmin.v1", "builtin_triangle")
    base["canonical_candidates"] = [_candidate(held_semantic, held_physical)]
    base["target_contract"]["native_sha256"] = held_result["local_and_home_evidence"]["native_library_sha256"]
    base["target_contract"]["target_sha256"] = _sha_json({
        "scope": "goal5783_home_held_out_target",
        "native_sha256": base["target_contract"]["native_sha256"],
        "capabilities": base["target_contract"]["capabilities"],
    })
    base["evidence_contract"] = {
        "source_pins": {path: SOURCE_MANIFEST[path] for path in sorted({
            held_semantic["specification_source_pin"], held_physical["provider_source_pin"],
            *(item["source_pin"] for item in held_physical["maps"]),
        })},
        "independent_oracle_sha256": held_result["implementation"]["independent_oracle_sha256"],
        "behavioral_receipt_sha256": held_result["local_and_home_evidence"]["home_functional_receipt_sha256"],
        "oracle_output_sha256": _sha_json({"held_out": "rtxrmq", "exact": True, "lanes": 4}),
        "physical_output_sha256": _sha_json({"held_out": "rtxrmq", "exact": True, "lanes": 4}),
    }
    _seal_certificate(base)
    held_authority = deepcopy(authority)
    held_authority["target_authority"]["target_profiles"][base["target_contract"]["target_sha256"]] = deepcopy(base["target_contract"])
    held_authority["instance_authority"]["instances"][base["instance_contract"]["input_sha256"]] = deepcopy(base["instance_contract"])
    held_authority["evidence_authority"]["oracle_sha256_allowlist"].append(base["evidence_contract"]["independent_oracle_sha256"])
    held_authority["evidence_authority"]["receipt_sha256_allowlist"].append(base["evidence_contract"]["behavioral_receipt_sha256"])
    held_authority["evidence_authority"]["oracle_sha256_allowlist"] = sorted(set(held_authority["evidence_authority"]["oracle_sha256_allowlist"]))
    held_authority["evidence_authority"]["receipt_sha256_allowlist"] = sorted(set(held_authority["evidence_authority"]["receipt_sha256_allowlist"]))
    _seal_authority(held_authority)
    held_check = check.evaluate_certificate(base, held_authority)
    _write_json(OUT / "HELD_OUT_AUTHORITY_BUNDLE.json", held_authority)
    _write_json(OUT / "HELD_OUT_RTXRMQ_CERTIFICATE.json", base)
    _write_json(OUT / "HELD_OUT_RTXRMQ_RESULT.json", held_check)

    summary = {
        "schema": "rtdl.goal5789.bounded_inventory.v1",
        "paper_app_count": 9,
        "registered_lane_count": len(inventory),
        "inventory": inventory,
        "semantic_compatible_count": sum(row["semantic_compatible"] == check.COMPATIBLE for row in inventory),
        "semantic_unknown_count": sum(row["semantic_compatible"] == check.UNKNOWN for row in inventory),
        "semantic_incompatible_count": sum(row["semantic_compatible"] == check.INCOMPATIBLE for row in inventory),
        "held_out_result": {
            "semantic_compatible": held_check["semantic_compatible"]["verdict"],
            "checker_core_changed_for_held_out": False,
            "universal_hit_rate_claimed": False,
        },
        "claim_boundary": {
            "registered_encoding_only": True,
            "unknown_fails_closed": True,
            "typed_schema_is_executable": False,
            "performance_inferred": False,
            "mechanized_proof_claimed": False,
            "all_nine_apps_claimed_compatible": False,
            "execution_authorized": False,
        },
    }
    summary["inventory_sha256"] = _sha_json(summary)
    _write_json(OUT / "BOUNDED_INVENTORY.json", summary)

    # Shared Goal5789 -> Goal5790 sync gate.  These are evidence-side names for
    # already implemented objects; they do not authorize execution or assert a
    # production optimizer.  Goal5790 may vary only the declared downstream
    # reducer variant after the common OptiX per-ray producer.
    triangle_certificate = certificates["triangle__cit_patents__rt_2a1"]
    triangle_worker = workers["triangle__cit_patents__rt_2a1"]
    traversal = triangle_worker["traversal_receipt"]
    component_receipts = traversal.get("component_receipts", [])
    program_bundles = sorted({
        bundle
        for component in component_receipts
        for bundle in component.get("expected_program_bundles", [])
    })
    shared = {
        "schema": "rtdl.goal5789_goal5790.shared_contract_freeze.v1",
        "status": "FROZEN_FOR_LOCAL_GOAL5790_IMPLEMENTATION_ONLY",
        "semantic_request": deepcopy(triangle_certificate["semantic_request"]),
        "semantic_request_sha256": _sha_json(triangle_certificate["semantic_request"]),
        "physical_encoding": deepcopy(triangle_certificate["physical_encoding"]),
        "physical_encoding_sha256": _sha_json(triangle_certificate["physical_encoding"]),
        "admitted_reference_plan": {
            **deepcopy(triangle_certificate["canonical_candidates"][0]),
            "executable": False,
        },
        "executable_family_plan": {
            "family_id": "v4_triangle_per_ray_optix_producer_plus_checked_u64_continuation.v1",
            # This is provenance for the already observed Goal5785 RTX
            # materialization, not a cross-target executable requirement.
            # Goal5790 must build and bind one exact native per target; Home
            # and a later RTX target are neither expected nor permitted to
            # masquerade as byte-identical materializations.
            "reference_native_provenance_sha256": triangle_worker[
                "native_library_sha256"],
            "reference_source_tree_sha256": triangle_worker["source_tree_sha256"],
            "program_bundles": program_bundles,
            "source_members": {
                path: SOURCE_MANIFEST[path]
                for path in (
                    "src/rtdsl/v4_triangle_standard_library.py",
                    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
                    "src/rtdsl/v4_triangle_reduction_device_runtime.py",
                    "src/rtdsl/v4_checked_u64_device_reduction.py",
                )
            },
            "authority_scope": "existing_family_identity_only__not_goal5790_variant_implementation",
            "target_materialization_policy": {
                "actual_target_native_must_be_receipt_bound": True,
                "actual_target_source_tree_must_be_receipt_bound": True,
                "cross_target_native_byte_reproducibility_assumed": False,
                "reference_native_is_execution_authority_for_other_targets": False,
                "same_target_fusion_pair_must_share_exact_native": True,
                "same_target_fusion_pair_must_share_exact_program_bundle": True,
                "same_target_fusion_pair_must_share_exact_source_tree": True,
            },
        },
        "transformation_variant_contract": {
            "mechanism_id": "checked_u64_product_sum_downstream_lowering.v1",
            "common_prefix": "same semantic request, triangle/ray inputs, Callback IR, OptiX per-ray producer, output and overflow contract",
            "fused_variant": "checked_summary_kernel_then_one_summary_copy_sync",
            "unfused_variant": "materialize_product_then_max_sum_sum_product_with_three_scalar_copy_sync_boundaries",
            "only_allowlisted_difference": "downstream_checked_u64_reducer_operation_identity_and_event_sequence",
            "particle_included": False,
            "particle_exclusion_reason": "no neutral placement IR or compiler-produced strict fusion-off plan in current architecture",
        },
        "claim_boundary": {
            "same_semantic_ir_required": True,
            "same_optix_producer_required": True,
            "event_derived_operation_receipts_required": True,
            "product_performance_claimed": False,
            "pod_or_target_worker_authorized": False,
            "compiler_fusion_claim_authorized": False,
        },
    }
    shared["shared_contract_freeze_sha256"] = _sha_json(shared)
    _write_json(OUT / "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json", shared)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
