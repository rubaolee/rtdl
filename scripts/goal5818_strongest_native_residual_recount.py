#!/usr/bin/env python3
"""Offline recount for Goal5818's strongest-native residual boundary.

This verifier imports neither RTDL, PyOptiX, OWL, CUDA, nor OptiX.  It binds
the already executed Goal5801-N-A1 native-typed-payload result, reconstructs
the exact CP002 attribute dataflow from preserved CUDA bytes, inspects the
pinned Goal5800 OWL public source bytes, and separately scans pinned OptiX 9
public headers.  It performs no GPU work and no
performance measurement.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"

TYPED_RESULT = (
    DOCS
    / "goal5801_n_a1_home_evidence_20260824"
    / "v3_native_typed_result.json"
)
TYPED_RESULT_SHA256 = (
    "8699fff641d5ef998b31507360fb05ba3b704873af13df1862bd11dad59b9fe7"
)
VALID_RELATION = (
    DOCS
    / "goal5801_n_a1_home_evidence_20260824"
    / "v3_gpu_evidence"
    / "device_sources"
    / "nearby_valid_relation.cu"
)
VALID_RELATION_SHA256 = (
    "fef3042b8cd676e5a5d83f5c69e4eaab600ca819c9ffb957b89855f9ab4b0ab5"
)
CP002_ATTACK = (
    DOCS
    / "goal5801_n_a1_home_evidence_20260824"
    / "v3_gpu_evidence"
    / "device_sources"
    / "payload_attribute_abi_ownership.cu"
)
CP002_ATTACK_SHA256 = (
    "a0a559ec384e5762d8f3ff6a0351e4684a30d2dc773f15576e47e5a2a2a072af"
)
OWL_BUNDLE = DOCS / "goal5800_owl_untimed_functional_bundle_v5_20260824.tar.gz"
OWL_BUNDLE_SHA256 = (
    "2840ae5fff2200c76c18664176b46f6b179c1be20f0216bd7237e28181d16993"
)
OWL_CORRECTION = DOCS / "goal5800_owl_repository_locator_correction_result_20260824.json"
OWL_CORRECTION_SHA256 = (
    "29e174b77a4b6c47692baae8b7f8175462f77a97266a99ec5e9c575431a69f4d"
)
OPTIX9_HEADERS = DOCS / "goal5818_optix9_public_header_evidence_20260829"
OPTIX9_HEADER = OPTIX9_HEADERS / "optix.h"
OPTIX9_TYPES = OPTIX9_HEADERS / "optix_types.h"
OPTIX9_DEVICE = OPTIX9_HEADERS / "optix_device.h"
OPTIX9_SOURCE_RECEIPT = OPTIX9_HEADERS / "source_receipt.json"
OPTIX9_BUNDLE = OPTIX9_HEADERS / "optix_headers_fff65c2a.bundle"
OPTIX9_SHA256 = {
    "optix.h": "85a13f5966e98e23b00cb6be0fa25ad6580bbbea94bc9fce9d0bf00d16827b8f",
    "optix_types.h": "fbd1aca6096daee765233f6be5a3680c7017ec678fd35c9a5000ed7d6b6ff48c",
    "optix_device.h": "3a5c1f784b64161479546462f35f953ab0f9e14058356c45ab1422313e79676f",
    "source_receipt.json": "b2b54365b1620ca2a587c617539efa6dbd27254f968f08130843512c5eee26a2",
    "optix_headers_fff65c2a.bundle": "bf52d3b089eb2b215d9071340ec5c809cfbf919cd87a8f3fdb07f0c59ed80745",
}

MECHANISMS = (
    "role_effect_closure",
    "payload_attribute_abi_ownership",
    "physical_geometry_binding",
    "device_status_continuation",
    "checked_program_executable_identity",
)

EXPECTED_OUTPUTS = {
    "role_effect_closure": {"per_ray": [1, 1, 0, 1], "weighted_sum": 11},
    "payload_attribute_abi_ownership": {
        "device_overflow": 0,
        "device_status": 0,
        "output": [[100, 0], [101, 1]],
        "raw_event_count": 2,
    },
    "physical_geometry_binding": {
        "device_overflow": 0,
        "device_status": 0,
        "output": [[100, 20], [101, 10]],
        "raw_event_count": 2,
    },
    "device_status_continuation": {
        "application_output_copied_despite_failure": True,
        "application_result_consumed": True,
        "device_overflow": 1,
        "device_status": 0,
        "raw_capacity": 7,
        "raw_event_count": 8,
        "returned_row_count": 7,
        "returned_rows": [
            [0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [3, 2], [4, 3],
        ],
        "status_observed_before_application_output_copy": True,
    },
    "checked_program_executable_identity": {
        "per_ray": [6, 4, 0, 2],
        "weighted_sum": 32,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def section(text: str, start: str, end: str) -> str:
    require(text.count(start) == 1, f"non-unique start anchor: {start}")
    tail = text.split(start, 1)[1]
    require(end in tail, f"missing end anchor after: {start}")
    return tail.split(end, 1)[0]


def line_of(text: str, literal: str) -> int:
    require(text.count(literal) == 1, f"non-unique line literal: {literal}")
    return text[: text.index(literal)].count("\n") + 1


def member_text(archive: tarfile.TarFile, name: str) -> str:
    member = archive.getmember(name)
    require(member.isfile(), f"not a regular file: {name}")
    stream = archive.extractfile(member)
    require(stream is not None, f"cannot extract: {name}")
    return stream.read().decode("utf-8")


def main() -> None:
    require(sha256(TYPED_RESULT) == TYPED_RESULT_SHA256, "typed result hash drift")
    require(sha256(VALID_RELATION) == VALID_RELATION_SHA256, "valid source hash drift")
    require(sha256(CP002_ATTACK) == CP002_ATTACK_SHA256, "CP002 source hash drift")
    require(sha256(OWL_BUNDLE) == OWL_BUNDLE_SHA256, "OWL bundle hash drift")
    require(sha256(OWL_CORRECTION) == OWL_CORRECTION_SHA256, "OWL correction hash drift")

    typed = json.loads(TYPED_RESULT.read_text(encoding="utf-8"))
    require(
        typed["status"] == "PASS__UNCONDITIONAL_NATIVE_TYPED_PAYLOAD_SURVIVAL_RESULT",
        "typed result status drift",
    )
    require(typed["required_validity_controls_pass"] is True, "valid controls failed")
    require(typed["native_collision_mechanisms"] == [], "native collision set drift")
    require(
        typed["residual_surviving_mechanisms"] == list(MECHANISMS),
        "surviving mechanism set/order drift",
    )
    require(typed["optix"]["api_version"] == "9.0.0", "OptiX version drift")
    require(typed["optix"]["validation_mode"] == "ALL", "validation not ALL")
    require(typed["optix"]["native_payload_type_enabled"] is True, "payload type inactive")

    cases = {row["id"]: row for row in typed["cases"]}
    for mechanism in MECHANISMS:
        row = cases[mechanism]
        require(
            row["classification"]
            == "NATIVE_ACCEPTED_AND_EXECUTED_EXACT_COUNTEREXAMPLE__RESIDUAL_SURVIVES",
            f"classification drift: {mechanism}",
        )
        require(row["terminal_phase"] == "launch_completed", f"no launch: {mechanism}")
        require(
            row["optix_validation_error_or_fatal_message_count"] == 0,
            f"native diagnostic collision: {mechanism}",
        )
        require(row["observation"] == EXPECTED_OUTPUTS[mechanism], f"output drift: {mechanism}")

    negative = cases["native_negative_missing_anyhit_rights"]
    nearby = cases["nearby_valid_triangle"]
    require(
        negative["classification"] == "PASS__NATIVE_TYPED_SEMANTICS_REJECTED_NEGATIVE",
        "native negative did not reject",
    )
    require(negative["terminal_phase"] == "module", "native negative phase drift")
    require(negative["source"]["sha256"] == nearby["source"]["sha256"], "negative source differs")
    require(negative["ptx"]["sha256"] == nearby["ptx"]["sha256"], "negative PTX differs")

    valid_text = VALID_RELATION.read_text(encoding="utf-8")
    attack_text = CP002_ATTACK.read_text(encoding="utf-8")
    valid_is = section(
        valid_text,
        'extern "C" __global__ void __intersection__goal5796_relation()',
        'extern "C" __global__ void __anyhit__goal5796_relation()',
    )
    attack_is = section(
        attack_text,
        'extern "C" __global__ void __intersection__goal5796_relation()',
        'extern "C" __global__ void __anyhit__goal5796_relation()',
    )
    attack_ah = section(
        attack_text,
        'extern "C" __global__ void __anyhit__goal5796_relation()',
        'extern "C" __global__ void __miss__goal5796_relation()',
    )
    require("optixReportIntersection(0.0f, 0u, item.item_id);" in valid_is, "valid producer drift")
    require("optixReportIntersection(0.0f, 0u, primitive_index);" in attack_is, "attack producer drift")
    require("row.item_id = optixGetAttribute_0();" in attack_ah, "attribute consumer drift")
    require("params.rows[slot] = row;" in attack_ah, "output sink drift")
    require("optixGetPayload" not in attack_is + attack_ah, "unexpected payload read in CP002 path")
    require("optixSetPayload" not in attack_is + attack_ah, "unexpected payload write in CP002 path")
    require("__closesthit__goal5796_relation" not in attack_text, "unexpected CH in CP002 path")

    correction = json.loads(OWL_CORRECTION.read_text(encoding="utf-8"))
    bridge = correction["official_source_bridge"]
    require(bridge["commit"] == "df7390b16bce5244b7352ca6d3e320f838297072", "OWL commit drift")
    require(bridge["tree"] == "c31d2c7510050fc3d57a4c4e0a4d4d84bc7b03ff", "OWL tree drift")
    require(bridge["origin"] == "https://github.com/NVIDIA/OWL.git", "OWL origin drift")

    with tarfile.open(OWL_BUNDLE, "r:gz") as archive:
        names = archive.getnames()
        public_names = [
            name for name in names
            if name.startswith((
                "goal5800_owl_source/include/",
                "goal5800_owl_source/owl/",
                "goal5800_owl_source/prime/",
            ))
        ]
        public_text = "\n".join(member_text(archive, name) for name in public_names)
        owl_header = member_text(archive, "goal5800_owl_source/include/owl/owl_host.h")
        owl_device = member_text(archive, "goal5800_owl_source/owl/DeviceContext.cpp")
        owl_vendored_optix_header = member_text(
            archive, "goal5800_owl_source/3rdParty/optix/include/optix.h"
        )

    forbidden_public_tokens = (
        "OptixPayloadType",
        "OptixPayloadSemantics",
        "payloadTypes",
        "payloadSemantics",
    )
    for token in forbidden_public_tokens:
        require(token not in public_text, f"OWL public payload-type token appeared: {token}")
    require("owlContextSetNumPayloadValues" in owl_header, "OWL payload count API missing")
    require("owlContextSetNumAttributeValues" in owl_header, "OWL attribute count API missing")
    require("pipelineCompileOptions.numPayloadValues" in owl_device, "OWL payload count plumbing missing")
    require("pipelineCompileOptions.numAttributeValues" in owl_device, "OWL attribute count plumbing missing")
    require("OptixProgramGroupOptions pgOptions = {};" in owl_device, "OWL PG options path drift")
    require("pgOptions.payloadType" not in owl_device, "OWL now assigns PG payload type")

    require("#define OPTIX_VERSION 80000" in owl_vendored_optix_header,
            "OWL vendored OptiX header version drift")
    for path, expected in (
        (OPTIX9_HEADER, OPTIX9_SHA256["optix.h"]),
        (OPTIX9_TYPES, OPTIX9_SHA256["optix_types.h"]),
        (OPTIX9_DEVICE, OPTIX9_SHA256["optix_device.h"]),
        (OPTIX9_SOURCE_RECEIPT, OPTIX9_SHA256["source_receipt.json"]),
        (OPTIX9_BUNDLE, OPTIX9_SHA256["optix_headers_fff65c2a.bundle"]),
    ):
        require(sha256(path) == expected, f"OptiX 9 evidence drift: {path.name}")
    optix_header = OPTIX9_HEADER.read_text(encoding="utf-8")
    optix_types = OPTIX9_TYPES.read_text(encoding="utf-8")
    optix_device = OPTIX9_DEVICE.read_text(encoding="utf-8")
    optix9_receipt = json.loads(OPTIX9_SOURCE_RECEIPT.read_text(encoding="utf-8"))
    materialized = optix9_receipt["materialized_headers"]
    require("#define OPTIX_VERSION 90000" in optix_header, "OptiX 9 version marker missing")
    require(materialized["commit"] == "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
            "OptiX 9 header commit drift")
    require(materialized["tree"] == "c30f1b41cb64f6cba6290d7ad82686cc84922267",
            "OptiX 9 header tree drift")

    require("typedef enum OptixPayloadSemantics" in optix_types, "native semantics enum missing")
    for stage in ("TRACE_CALLER", "CH", "MS", "AH", "IS"):
        require(
            f"OPTIX_PAYLOAD_SEMANTICS_{stage}_READ_WRITE" in optix_types,
            f"native stage semantics missing: {stage}",
        )
    require("const unsigned int *payloadSemantics;" in optix_types, "payload word semantics field missing")
    require("int numAttributeValues;" in optix_types, "attribute count field missing")
    for slot in range(8):
        require(f"optixGetAttribute_{slot}();" in optix_device, f"attribute getter missing: {slot}")
    require("AttributeSemantics" not in optix_types + optix_device, "attribute semantics API appeared")

    output = {
        "schema": "rtdl.goal5818.strongest_native_residual_recount.v1",
        "status": "PASS__BRANCH_A_SELECTED_FROM_EXISTING_EXECUTED_EVIDENCE",
        "repository": {
            "resolved_path": str(ROOT),
            "git_head_ref_value": "1af120d187228035db733ce690de3a3bf5b54ee5",
            "commit_object_available": False,
            "git_branch": "codex/v4-restricted-python-callback-design",
            "git_object_status": "UNAVAILABLE__BAD_OBJECT_HEAD",
        },
        "existing_native_execution": {
            "result_sha256": TYPED_RESULT_SHA256,
            "optix_api_version": "9.0.0",
            "validation_mode": "ALL",
            "native_typed_payload_live_negative_control": True,
            "native_collision_count": 0,
            "residual_survival_count": 5,
            "mechanisms": list(MECHANISMS),
            "designed_task_count": 2,
            "environment_count": 1,
            "stock_pyoptix_or_owl_claimed": False,
        },
        "cp002_exact_dataflow": {
            "producer_role": "intersection",
            "producer_valid": "optixReportIntersection(..., item.item_id)",
            "producer_attack": "optixReportIntersection(..., primitive_index)",
            "transport": "attribute_slot_0",
            "consumer_role": "any_hit",
            "consumer": "optixGetAttribute_0()",
            "sink": "RelationRow.item_id -> params.rows[slot]",
            "closest_hit_in_path": False,
            "payload_read_or_write_in_is_ah_path": False,
            "valid_source_sha256": VALID_RELATION_SHA256,
            "attack_source_sha256": CP002_ATTACK_SHA256,
            "producer_line": line_of(
                attack_text, "optixReportIntersection(0.0f, 0u, primitive_index);"
            ),
            "consumer_line": line_of(attack_text, "row.item_id = optixGetAttribute_0();"),
            "sink_line": line_of(attack_text, "params.rows[slot] = row;"),
        },
        "pinned_optix_9_0_public_header_boundary": {
            "source_commit": materialized["commit"],
            "source_tree": materialized["tree"],
            "source_bundle_sha256": optix9_receipt["headers_bundle"]["sha256"],
            "header_sha256": dict(OPTIX9_SHA256),
            "optix_version_macro": 90000,
            "payload_semantics_granularity": "per_32b_word_per_shader_role_read_write",
            "attribute_declaration_found": "pipeline_numAttributeValues_plus_slot_getters",
            "per_attribute_slot_nominal_semantics_declaration_found": False,
            "negative_scan_scope": "pinned OptiX 9.0 optix_types.h and optix_device.h only",
        },
        "pinned_owl_public_api_boundary": {
            "origin": bridge["origin"],
            "commit": bridge["commit"],
            "tree": bridge["tree"],
            "bundle_sha256": OWL_BUNDLE_SHA256,
            "vendored_optix_version_macro": 80000,
            "public_payload_and_attribute_count_setters": True,
            "public_payload_type_or_semantics_surface_found": False,
            "program_group_payload_type_assignment_found": False,
            "bounded_meaning": (
                "The examined public API does not expose the native payload-type declaration; "
                "obtaining it requires leaving that abstraction or modifying its implementation."
            ),
        },
        "selected_claim_branch": "A__NATIVE_TYPED_PAYLOAD_ACTIVE__ZERO_OF_FIVE_CAPTURED",
        "registered_performance_timing_count": 0,
        "gpu_execution_performed_by_goal5818": 0,
        "rtdl_core_changed": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
