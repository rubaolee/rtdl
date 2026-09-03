#!/usr/bin/env python3
"""Build or verify the Goal5840 independent-refinement preregistration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5840_independent_lowering_refinement_20260903"
)
OUTPUT_PATH = EVIDENCE_ROOT / "GOAL5840_PREREGISTRATION.json"
SCHEMA = "rtdl.goal5840.independent_lowering_refinement_preregistration.v1"
DOMAIN = b"rtdl.goal5840.independent_lowering_refinement_preregistration.v1\0"
FROZEN_AT_UTC = "2026-09-03T07:31:16Z"
BASELINE_COMMIT = "2f256d5775fd8a522921af48fb8b8fc176a68756"

BASELINE_FILES = {
    "src/rtdsl/v4_protocol_contract.py": (
        "e60f83f5a15df58de2f3f38b681331efb51b797c1b12628ebdaaf1c26a448973"
    ),
    "src/rtdsl/v4_callback_lifecycle.py": (
        "76e35a2b246f125b51136bd6f8354a3133b8c207474f9e9aea31fda9c6b240bd"
    ),
    "src/rtdsl/v4_rtdlexe.py": (
        "ea32830ec3ba273523adf947e4e85c460af2ca50aaa316eeb90e1caa39bda097"
    ),
    "scripts/goal5801_independent_closeout_verifier.py": (
        "d706f755586fece911447608da0cc158d0904239e915d8aa5d4b7f30474f9119"
    ),
    "src/rtdsl/v4_family_schema.py": (
        "2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224"
    ),
    "src/rtdsl/v4_generic_family_lifecycle.py": (
        "7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c"
    ),
    "src/rtdsl/v4_family.py": (
        "d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8"
    ),
}

ROUTES = (
    {
        "route_id": "stable::bounded_relation::canonical_bounded_pair_collection",
        "classification": "stable_fixed_constructor",
        "geometry": "custom_primitive_aabb",
        "result": "canonical_bounded_u32_pair_rows",
        "required_modes": ["capacity_fail_closed_collection"],
    },
    {
        "route_id": "stable::triangle_reduction::checked_u64_reduction",
        "classification": "stable_fixed_constructor",
        "geometry": "builtin_triangle",
        "result": "checked_u64_scalar",
        "required_modes": ["all_hit_count", "weighted_hit_count"],
    },
    {
        "route_id": "prospective::builtin_sphere::any_hit_count_continue_u64_per_query",
        "classification": "goal5838_bounded_prospective_success",
        "geometry": "builtin_sphere",
        "result": "per_query_u64",
        "required_modes": ["accept_every_hit_and_continue"],
    },
)

PROPERTIES = (
    "CP001_ROLE_EFFECT_CLOSURE",
    "CP002_SEMANTIC_ABI_OWNERSHIP",
    "CP003_PHYSICAL_BINDING",
    "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS",
    "CP005_EXECUTABLE_IDENTITY_CHAIN",
)

MUTATION_BY_PROPERTY = {
    "CP001_ROLE_EFFECT_CLOSURE": {
        "mutation": (
            "change one generated role effect or remove one required role symbol while "
            "recomputing every untrusted bundle-local digest"
        ),
        "required_rejection": "TARGET_ROLE_EFFECT_OR_SYMBOL_MISMATCH",
    },
    "CP002_SEMANTIC_ABI_OWNERSHIP": {
        "mutation": (
            "swap one same-width nominal semantic or producer/consumer owner while "
            "preserving machine scalar widths and recomputing bundle-local digests"
        ),
        "required_rejection": "TARGET_NOMINAL_CHANNEL_OWNERSHIP_MISMATCH",
    },
    "CP003_PHYSICAL_BINDING": {
        "mutation": (
            "change one geometry/template, SBT, buffer ordinal/layout, result operator, "
            "or native producer binding and recompute bundle-local digests"
        ),
        "required_rejection": "TARGET_PHYSICAL_BINDING_MISMATCH",
    },
    "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS": {
        "mutation": (
            "remove or reorder a status-before-output guard, or mark overflow/truncation "
            "complete, then recompute bundle-local digests"
        ),
        "required_rejection": "TARGET_STATUS_OR_COMPLETENESS_MISMATCH",
    },
    "CP005_EXECUTABLE_IDENTITY_CHAIN": {
        "mutation": (
            "swap generated source/PTX, native DSO, target, or runtime receipt identity "
            "while recomputing every attacker-controlled bundle-local digest"
        ),
        "required_rejection": "TARGET_EXECUTABLE_IDENTITY_MISMATCH",
    },
}

MUTATION_TARGETS = {
    "stable::bounded_relation::canonical_bounded_pair_collection": {
        "CP001_ROLE_EFFECT_CLOSURE": {
            "target_selector": "callback_abi.roles[any_hit].effects[accept_continue]",
            "replacement": "terminate",
        },
        "CP002_SEMANTIC_ABI_OWNERSHIP": {
            "target_selector": "family_schema.channels[relation_item_id].semantic",
            "replacement": "query.item_id",
        },
        "CP003_PHYSICAL_BINDING": {
            "target_selector": "family_schema.physical.primitive_kind",
            "replacement": "builtin_triangle",
        },
        "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS": {
            "target_selector": "result_operator.contract.capacity",
            "replacement": "return_partial_result",
        },
        "CP005_EXECUTABLE_IDENTITY_CHAIN": {
            "target_selector": "composed_ptx.bytes",
            "replacement": "different_valid_route_ptx_bytes",
        },
    },
    "stable::triangle_reduction::checked_u64_reduction": {
        "CP001_ROLE_EFFECT_CLOSURE": {
            "target_selector": "callback_abi.roles[any_hit].effects[accept_continue]",
            "replacement": "terminate",
        },
        "CP002_SEMANTIC_ABI_OWNERSHIP": {
            "target_selector": "family_schema.channels[triangle_primitive_index].semantic",
            "replacement": "query.index",
        },
        "CP003_PHYSICAL_BINDING": {
            "target_selector": "family_schema.physical.primitive_kind",
            "replacement": "builtin_sphere",
        },
        "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS": {
            "target_selector": "result_operator.contract.overflow",
            "replacement": "wrap_u64_and_report_complete",
        },
        "CP005_EXECUTABLE_IDENTITY_CHAIN": {
            "target_selector": "execution_receipt.native_library_sha256",
            "replacement": "different_well_formed_sha256",
        },
    },
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": {
        "CP001_ROLE_EFFECT_CLOSURE": {
            "target_selector": "callback_abi.roles[any_hit].effects[accept_continue]",
            "replacement": "terminate",
        },
        "CP002_SEMANTIC_ABI_OWNERSHIP": {
            "target_selector": "protocol_instance.nominal_semantics.output",
            "replacement": "query.user_u64",
        },
        "CP003_PHYSICAL_BINDING": {
            "target_selector": "family_schema.physical.sbt.record_count_relation",
            "replacement": "primitive_count",
        },
        "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS": {
            "target_selector": "result_operator.contract.overflow",
            "replacement": "expose_partial_output",
        },
        "CP005_EXECUTABLE_IDENTITY_CHAIN": {
            "target_selector": "execution_receipt.target_sha256",
            "replacement": "different_well_formed_sha256",
        },
    },
}


class Goal5840PreregistrationError(RuntimeError):
    """Fail-closed Goal5840 preregistration error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Goal5840PreregistrationError(message)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _seal(value: dict[str, Any]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return _sha256(DOMAIN + _canonical_bytes(body))


def build_authority() -> dict[str, Any]:
    mutations = []
    for route in ROUTES:
        for property_id in PROPERTIES:
            recipe = MUTATION_BY_PROPERTY[property_id]
            target = MUTATION_TARGETS[route["route_id"]][property_id]
            mutations.append({
                "mutation_id": f"{route['route_id']}::{property_id}",
                "route_id": route["route_id"],
                "property_id": property_id,
                **recipe,
                **target,
                "mutation_time": "after_declaration_admission_before_target_acceptance",
                "recompute_attacker_controlled_digests": True,
                "gpu_launch_required_for_rejection": False,
            })

    authority: dict[str, Any] = {
        "schema": SCHEMA,
        "goal": 5840,
        "stage": "PREREGISTRATION_BEFORE_IMPLEMENTATION",
        "status": (
            "PREREGISTERED_BEFORE_TARGET_EVIDENCE_BUNDLE_OR_"
            "INDEPENDENT_EXTRACTOR_IMPLEMENTATION"
        ),
        "frozen_at_utc": FROZEN_AT_UTC,
        "reviewer_attack": {
            "id": "R3",
            "attack": (
                "The declaration and compiler projections are produced inside the same "
                "implementation and tests do not establish lowering preservation."
            ),
            "current_limitation": (
                "The Goal5801 detached verifier validates stored compiler_projection "
                "identity but does not independently recover that projection from raw "
                "target artifacts."
            ),
        },
        "baseline": {
            "commit": BASELINE_COMMIT,
            "identity_rule": (
                "file SHA-256 values describe blobs at the frozen baseline commit; "
                "later working-tree files are not reinterpreted as the baseline"
            ),
            "pre_freeze_verification": (
                "all listed working-tree files matched these SHA-256 values before this "
                "preregistration was generated"
            ),
            "files": [
                {"path": path, "sha256": digest}
                for path, digest in BASELINE_FILES.items()
            ],
            "roadmap": {
                "path": (
                    "history/internal_docs/goal5838_goal5843_cgo_reviewer_attack_"
                    "remediation_plan_20260902.md"
                ),
                "sha256": (
                    "bf02dfe3833d524c14586d4459adfe7b5063f88cc498a137562f55e087e0b664"
                ),
            },
            "goal5838_final_authority": {
                "path": (
                    "history/internal_docs/goal5838_generic_core_exam_20260902/"
                    "FINAL_AUTHORITY.json"
                ),
                "file_sha256": (
                    "dafea025d8f9583cd186e914f6e2974b6aab2fdd59781a6d2a39087e0def7ce8"
                ),
                "internal_seal": (
                    "c0578a22e006e2bee2dec39e6de98201ce547eca95dc20b6b7f4c1a891479a8e"
                ),
            },
        },
        "supported_scope": {
            "routes": list(ROUTES),
            "route_count": len(ROUTES),
            "properties": list(PROPERTIES),
            "property_count": len(PROPERTIES),
            "claim_unit": "one_route_times_one_property",
            "required_claim_unit_count": len(ROUTES) * len(PROPERTIES),
            "excluded": [
                "arbitrary Callback IR",
                "owner-grouped closed successor route",
                "unselected Goal5838 challenge-table topologies",
                "non-OptiX providers",
                "application correctness",
                "performance or speedup",
                "general compiler soundness",
            ],
        },
        "target_evidence_bundle": {
            "must_preserve_exact_bytes_or_canonical_records": [
                "public protocol declaration",
                "verified Callback IR and role/effect manifest",
                "compiled Callback ABI with nominal semantic types and owners",
                "generated leaf source for every role",
                "trusted wrapper source and role symbols",
                "leaf PTX, wrapper PTX, and composed PTX",
                "family schema and canonical compilation plan",
                "provider key and native producer descriptor",
                "SBT and buffer layout/binding records",
                "target/toolchain/native DSO identities",
                "status/completeness and exact execution receipt",
            ],
            "stored_compiler_projection_is_evidence_source": False,
            "raw_artifact_anchor_rule": (
                "each recovered fact must cite raw generated source or PTX plus its "
                "structural ABI/plan/binding/receipt evidence when that fact has an "
                "executable representation; nominal-only facts must cite both producer "
                "and consumer structural origins"
            ),
            "missing_required_component": "FAIL_CLOSED_UNSUPPORTED_EVIDENCE_BUNDLE",
            "bundle_local_hashes_are_not_external_authority": True,
        },
        "independent_extractor": {
            "implementation_language": "Python standard library only",
            "imports_rtdsl": False,
            "imports_declaration_side_projection_builder": False,
            "imports_existing_compiler_projection_builder": False,
            "reads_stored_compiler_projection_as_target_facts": False,
            "derives": [
                "role effects and required role-symbol topology",
                "nominal channel semantics and producer/consumer ownership",
                "geometry/template/SBT/buffer/result physical bindings",
                "status-before-output and completeness continuation policy",
                "generated source/PTX/native target/runtime receipt identity chain",
            ],
            "must_emit": (
                "property-by-property facts with exact evidence object/path/symbol citations"
            ),
            "unknown_or_unparseable": "FAIL_CLOSED_UNSUPPORTED_RULE",
            "independence_test": (
                "AST import scan plus isolated subprocess with repository package imports blocked"
            ),
        },
        "mutation_matrix": mutations,
        "mutation_count": len(mutations),
        "success_condition": {
            "positive_route_bundles": 3,
            "all_required_modes_present": True,
            "independent_extractor_matches_declaration_for_every_claim_unit": True,
            "all_preregistered_mutations_rejected": True,
            "rejected_before_gpu_launch": True,
            "true_optix_positive_receipt_per_route": True,
            "unsupported_lowering_rule_removed_or_goal_fails_closed": True,
            "frozen_goal5838_core_byte_changes": 0,
            "tcb_and_unproved_obligations_reported": True,
        },
        "failure_condition": {
            "stored_projection_required_to_recover_any_claimed_fact": True,
            "mutation_accepted_for_claimed_property": True,
            "unsupported_rule_retained_in_preservation_statement": True,
            "goal5838_frozen_core_change_required": True,
        },
        "trusted_computing_base_to_report": [
            "public declaration serializer and admission authority",
            "target evidence bundler",
            "standalone independent extractor/checker",
            "SHA-256 and canonical JSON implementation",
            "Numba/NVVM, NVRTC, PTX linker, OptiX runtime and NVIDIA driver",
            "native producer descriptor and execution-receipt producer",
            "GPU hardware for positive execution receipts",
        ],
        "unproved_obligations": [
            "semantic correctness of arbitrary Callback IR",
            "compiler, driver, OptiX, and hardware correctness",
            "geometry intersection arithmetic correctness",
            "application-level correctness",
            "properties outside the three registered routes",
            "performance, usability, and provider portability",
        ],
        "execution_order": [
            "freeze this preregistration",
            "implement target evidence bundle without changing Goal5838 frozen core",
            "implement standalone extractor without rtdsl imports",
            "produce local deterministic positive bundles and run 15 mutations",
            "run exact positive routes and receipts on an NVIDIA OptiX pod",
            "repeat mutations against exact captured bundles",
            "write bounded preservation argument and hostile self-review",
            "seek external review only after travel constraint ends",
        ],
        "claim_boundary": {
            "preregistration_only": True,
            "target_evidence_bundle_implemented": False,
            "independent_extractor_implemented": False,
            "lowering_preservation_established": False,
            "general_soundness_theorem": False,
            "gpu_result": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
            "cgo_claim_authorized": False,
        },
        "authority_sha256": "",
    }
    authority["authority_sha256"] = _seal(authority)
    validate_authority(authority)
    return authority


def validate_authority(authority: dict[str, Any]) -> None:
    _require(authority.get("schema") == SCHEMA, "SCHEMA_MISMATCH")
    _require(authority.get("authority_sha256") == _seal(authority), "SEAL_MISMATCH")
    scope = authority.get("supported_scope")
    _require(isinstance(scope, dict), "SCOPE_MISSING")
    _require(scope.get("route_count") == 3, "ROUTE_COUNT_MISMATCH")
    _require(scope.get("property_count") == 5, "PROPERTY_COUNT_MISMATCH")
    _require(scope.get("required_claim_unit_count") == 15, "CLAIM_UNIT_COUNT_MISMATCH")
    mutations = authority.get("mutation_matrix")
    _require(isinstance(mutations, list) and len(mutations) == 15, "MUTATION_COUNT_MISMATCH")
    _require(len({row["mutation_id"] for row in mutations}) == 15, "MUTATION_ID_DUPLICATE")
    _require(
        {row["route_id"] for row in mutations}
        == {row["route_id"] for row in ROUTES},
        "MUTATION_ROUTE_COVERAGE_MISMATCH",
    )
    _require(
        {row["property_id"] for row in mutations} == set(PROPERTIES),
        "MUTATION_PROPERTY_COVERAGE_MISMATCH",
    )
    _require(
        all(row.get("target_selector") and row.get("replacement") for row in mutations),
        "MUTATION_TARGET_NOT_FROZEN",
    )
    extractor = authority.get("independent_extractor")
    _require(
        isinstance(extractor, dict)
        and extractor.get("imports_rtdsl") is False
        and extractor.get("reads_stored_compiler_projection_as_target_facts") is False,
        "EXTRACTOR_INDEPENDENCE_MISMATCH",
    )
    boundary = authority.get("claim_boundary")
    _require(
        isinstance(boundary, dict)
        and boundary.get("preregistration_only") is True
        and all(
            value is False
            for key, value in boundary.items()
            if key != "preregistration_only"
        ),
        "CLAIM_BOUNDARY_MISMATCH",
    )


def _serialized(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()

    expected = build_authority()
    if args.verify_stored:
        stored = json.loads(args.output.read_text(encoding="ascii"))
        validate_authority(stored)
        _require(_serialized(stored) == _serialized(expected), "STORED_REBUILD_MISMATCH")
        print(json.dumps({
            "authority_sha256": stored["authority_sha256"],
            "file_sha256": _sha256(args.output.read_bytes()),
            "status": "PASS__GOAL5840_PREREGISTRATION_VERIFIED",
        }, sort_keys=True))
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_serialized(expected))
    print(json.dumps({
        "authority_sha256": expected["authority_sha256"],
        "file_sha256": _sha256(args.output.read_bytes()),
        "status": expected["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
