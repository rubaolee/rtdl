"""Create the non-self-referential Goal5789-A2 CFR and exact entrypoint."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESULT_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_result_20260821.json"
REPORT_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_technical_report_20260821.md"
SCIENCE_REVIEW_REL = "history/internal_docs/self_review_goal5789_a2_callback_ir_authority_binding_science_20260821.md"
ARTIFACT_REVIEW_REL = "history/internal_docs/self_review_goal5789_a2_callback_ir_authority_binding_artifact_governance_20260821.md"
DELIVERY_REL = "history/internal_docs/goal5789_a2_delivery_manifest_20260821.json"
PACKET_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
TWIN_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_twin_20260821.tar.gz"
PACKET_MANIFEST_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_manifest_20260821.json"
PACKET_AUDIT_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_audit_20260821.json"
CFR_REL = "history/internal_docs/call_for_review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md"
ENTRYPOINT_REL = "history/internal_docs/GOAL5789_A2_EXTERNAL_REVIEW_ENTRYPOINT_20260821.json"
CFR = ROOT / CFR_REL
ENTRYPOINT = ROOT / ENTRYPOINT_REL

EXPECTED_RESEARCH_INTEGRITY = {
    "goal5793_generalization_exam_count": 0,
    "generalization_claimed": False,
    "false_rejection_rate_claimed": False,
    "third_geometry_family_claimed": False,
    "all_v4_paths_semantically_gated_claimed": False,
    "user_usability_study_count": 0,
    "programming_task_time_comparison_count": 0,
    "easy_or_better_than_direct_cuda_optix_claimed": False,
    "production_tool_claimed": False,
}
EXPECTED_RESULT_AUTHORIZATION = {
    "authorizes_owner_selected_external_review_packet_preparation": True,
    "authorizes_external_reviewer_contact_by_this_result": False,
    "authorizes_goal5793": False,
    "authorizes_entropy_or_candidate_selection": False,
    "authorizes_implementation_or_execution": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_worker_or_timing": False,
    "authorizes_product_change": False,
    "authorizes_publication_or_submission": False,
}
EXPECTED_DELIVERY_AUTHORIZATION = {
    "authorizes_owner_selected_external_review_packet_preparation": True,
    "authorizes_external_reviewer_contact_by_this_manifest": False,
    "authorizes_goal5793": False,
    "authorizes_entropy_or_candidate_selection": False,
    "authorizes_implementation_or_execution": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_worker_or_timing": False,
    "authorizes_product_change": False,
    "authorizes_publication_or_submission": False,
}
EXPECTED_PACKET_CLAIM_BOUNDARY = {
    "callback_authority_bound_inventory_rows": 6,
    "callback_authority_unbound_inventory_rows": 9,
    "goal5793_generalization_evidence_count": 0,
    "user_usability_study_count": 0,
    "authority_producer_is_tcb": True,
    "jointly_wrong_authorities_detected": False,
    "semantic_soundness_claimed": False,
    "completeness_claimed": False,
    "generalization_claimed": False,
    "easy_or_better_than_cuda_optix_claimed": False,
}
EXPECTED_PACKET_AUTHORIZATION = {
    "authorizes_goal5793": False,
    "authorizes_entropy_or_candidate_selection": False,
    "authorizes_execution": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_worker_or_timing": False,
    "authorizes_product_change": False,
    "authorizes_publication_or_submission": False,
}
EXPECTED_PACKET_AUDIT_AUTHORIZATION = {
    "authorizes_goal5793": False,
    "authorizes_execution": False,
    "authorizes_gpu_home_pod_or_ssh": False,
    "authorizes_worker_or_timing": False,
    "authorizes_product_change": False,
    "authorizes_publication_or_submission": False,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _pretty(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"expected regular file: {relative}")
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "file_sha256": _sha(data)}


def _load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_bytes())
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {relative}")
    return value


def _assert_seal(value: Mapping[str, object], field: str, label: str) -> None:
    body = {key: item for key, item in value.items() if key != field}
    if value.get(field) != _sha(_canonical(body)):
        raise RuntimeError(f"{label} internal seal mismatch")


def _table_row(identity: Mapping[str, object]) -> str:
    return f"| `{identity['path']}` | `{identity['file_sha256']}` | {identity['bytes']:,} |"


def build_outputs() -> tuple[bytes, dict[str, object]]:
    result = _load(RESULT_REL)
    delivery = _load(DELIVERY_REL)
    packet_manifest = _load(PACKET_MANIFEST_REL)
    packet_audit = _load(PACKET_AUDIT_REL)
    _assert_seal(result, "result_sha256", "Goal5789-A2 result")
    _assert_seal(delivery, "delivery_manifest_sha256", "Goal5789-A2 delivery manifest")
    _assert_seal(packet_audit, "audit_sha256", "Goal5789-A2 packet audit")
    if (
        result.get("status")
        != "COMPLETE_LOCAL_CALLBACK_IR_AUTHORITY_BINDING_EVIDENCE__EXTERNAL_REVIEW_REQUIRED__GOAL5793_BLOCKED"
        or packet_audit.get("status")
        != "PASS__EXACT_DETERMINISTIC_PACKET_TWIN_MANIFEST_AND_DELIVERY_CROSSBIND"
    ):
        raise RuntimeError("Goal5789-A2 local completion or packet audit status mismatch")
    if (
        result.get("research_integrity") != EXPECTED_RESEARCH_INTEGRITY
        or result.get("authorization") != EXPECTED_RESULT_AUTHORIZATION
        or delivery.get("claim_boundary") != EXPECTED_RESEARCH_INTEGRITY
        or delivery.get("authorization") != EXPECTED_DELIVERY_AUTHORIZATION
        or packet_manifest.get("claim_boundary") != EXPECTED_PACKET_CLAIM_BOUNDARY
        or packet_manifest.get("authorization") != EXPECTED_PACKET_AUTHORIZATION
        or packet_audit.get("authorization") != EXPECTED_PACKET_AUDIT_AUTHORIZATION
    ):
        raise RuntimeError("Goal5789-A2 result/delivery/packet claim or authorization drift")

    identities = [
        _identity(RESULT_REL),
        _identity(REPORT_REL),
        _identity(SCIENCE_REVIEW_REL),
        _identity(ARTIFACT_REVIEW_REL),
        _identity(DELIVERY_REL),
        _identity(PACKET_REL),
        _identity(TWIN_REL),
        _identity(PACKET_MANIFEST_REL),
        _identity(PACKET_AUDIT_REL),
    ]
    by_path = {row["path"]: row for row in identities}
    if (ROOT / PACKET_REL).read_bytes() != (ROOT / TWIN_REL).read_bytes():
        raise RuntimeError("review packet twin differs before CFR generation")
    packet_root = packet_manifest.get("root_delivery_manifest")
    if not isinstance(packet_root, Mapping) or (
        packet_root.get("path") != DELIVERY_REL
        or packet_root.get("bytes") != by_path[DELIVERY_REL]["bytes"]
        or packet_root.get("file_sha256") != by_path[DELIVERY_REL]["file_sha256"]
        or packet_root.get("delivery_manifest_sha256")
        != delivery.get("delivery_manifest_sha256")
    ):
        raise RuntimeError("packet manifest does not crossbind the current delivery root")
    expected_checks = {
        "exact_member_set": True,
        "embedded_manifest_byte_identical": True,
        "delivery_manifest_crossbound": True,
        "regular_file_only": True,
        "canonical_metadata": True,
        "unsafe_member_count": 0,
    }
    if packet_audit.get("checks") != expected_checks:
        raise RuntimeError("packet audit checks are not exact")
    audit_archive = packet_audit.get("archive")
    audit_twin = packet_audit.get("twin")
    audit_manifest = packet_audit.get("manifest")
    if not isinstance(audit_archive, Mapping) or not isinstance(audit_twin, Mapping) or not isinstance(audit_manifest, Mapping):
        raise RuntimeError("packet audit identity rows missing")
    if audit_archive != by_path[PACKET_REL]:
        raise RuntimeError("stale packet audit archive identity")
    if audit_twin != (by_path[TWIN_REL] | {"byte_identical": True}):
        raise RuntimeError("stale packet audit twin identity")
    expected_manifest_audit = by_path[PACKET_MANIFEST_REL] | {
        "payload_count": packet_manifest["payload_count"],
        "payload_bytes": packet_manifest["payload_bytes"],
        "payload_set_sha256": packet_manifest["payload_set_sha256"],
    }
    if audit_manifest != expected_manifest_audit:
        raise RuntimeError("stale packet audit manifest identity")

    cfr = f"""# Call for review — Goal5789-A2 Callback-IR authority binding and Goal5793 entry

Date: 2026-08-21  
Requested reviewer: owner-selected external reviewer  
Status: exact-byte external-review request; this file does not claim review  
Scope: bounded local evidence repair for the Goal5789 independent compatibility
checker; Goal5793 remains blocked pending a returned P0=0/P1=0 review and an
append-only owner absorption/closure

## Requested verdict

Please independently reproduce the packet and return P0/P1/P2/P3. The strongest
verdict requested is:

```text
APPROVE_GOAL5789_A2_AT_BOUNDED_LOCAL_CALLBACK_IR_AUTHORITY_BINDING_SCOPE
__FIVE_FROZEN_PROGRAMS_AND_26_EXECUTED_LEAVES_RECONSTRUCTED
__FOUR_SEMANTIC_PHYSICAL_PAIR_TO_PROGRAM_BINDINGS_EXACT
__ORIGINAL_EMPTY_EFFECT_AND_REAL_PROGRAM_SUBSTITUTION_ATTACKS_REJECTED
__PREDECESSOR_AND_SUCCESSOR_INVENTORY_BOTH_6_COMPATIBLE_9_UNKNOWN_0_INCOMPATIBLE
__ONLY_6_OF_15_INVENTORY_ROWS_CALLBACK_BOUND_AND_9_OF_15_EXPLICITLY_UNBOUND
__RTXRMQ_IS_LEGACY_NO_SPECIAL_CASE_REPLAY_NOT_CHECKER_HELD_OUT_GENERALIZATION
__AUTHORITY_PRODUCER_AND_EXTERNAL_ROOTS_REMAIN_TCB
__NO_SOUNDNESS_COMPLETENESS_FALSE_REJECTION_RATE_GENERALIZATION_USABILITY_OR_ALL_PATH_GATE_CLAIM
__GOAL5793_S0_REQUIRES_SEPARATE_POSTREVIEW_ABSORPTION_AND_PREREGISTRATION
```

Any broader verdict should be refused.

## Exact review roots

| Artifact | SHA-256 | Bytes |
|---|---:|---:|
{chr(10).join(_table_row(row) for row in identities)}

The packet manifest reports {packet_manifest['payload_count']} payloads totaling
{packet_manifest['payload_bytes']:,} bytes with payload-set digest
`{packet_manifest['payload_set_sha256']}`. The archive and twin are byte-identical.
The independent packet audit is `{packet_audit['status']}`.

The review request is intentionally outside the packet to avoid a hash cycle.
Rehash this CFR separately using the owner-supplied hash.

## Why A2 exists

The owner-returned Goal5789-A1 review approved the bounded registered
assume-guarantee framing, but a later hostile audit found that Callback role
effects, digest identities, exact role sets, and resource summaries were partly
self-reported by the certificate/builder. Clearing allowed effects and re-signing
the certificate could still return `COMPATIBLE_FOR_DECLARED_DOMAIN`. The prior
Goal5793 S0 entry was therefore terminalized rather than quietly reinterpreted.

A2 is a technical evidence repair. It independently materializes five complete
Callback-IR programs from the exact Goal5785 execution source, cross-binds 26
executed leaf artifacts from the frozen evidence archive, fixes four reviewed
semantic/physical-pair-to-program mappings, and makes each bound certificate an
exact type-sensitive projection of that authority. It does not change product,
native, app, GPU, or scientific execution bytes.

## Required independent checks

1. **Roots and materialization.** Rehash the Goal5785 result, exact execution
   source and evidence archives. Reconstruct all five programs, all 26 unique
   leaf identities, their PTX/IR/effect/role links, and the four exact bindings.
2. **Original failure and repair.** Reproduce that the predecessor accepts the
   empty-allowed-effect certificate after re-signing, while A2 rejects it under
   the fixed Callback authority and pin.
3. **Hostile matrix.** Re-run all 159 cases. In particular, coordinate re-sign
   Triangle count→keyed, Particle adjacency→count, LibRTS box→spatial, an
   invented RTXRMQ pair, resource/type aliases, producer metadata, leaf-manifest
   identities, and claim-overreach. Each must fail at the documented boundary.
   Independently verify that the finalizer/recount reject predecessor-manifest,
   terminal, and work-authority root drift.
4. **TCB ceiling.** Confirm that a mutually consistent but jointly wrong semantic
   and physical authority can still pass. This is an explicit ceiling, not a
   target for a false tamper-proof claim.
5. **Inventory.** Rebuild the predecessor and successor vectors. Both must be
   6 compatible / 9 unknown / 0 incompatible. Exactly 6/15 inventory rows are
   Callback-bound; 9/15 are unbound and carry no Callback-integrity claim.
6. **RTXRMQ.** Confirm the exact adjacency binding and compatible replay, while
   rejecting any claim that it was held out from the Goal5789 checker/calculus.
7. **Generalization red line.** A2 contributes zero Goal5793 exams. It does not
   establish false-rejection rate, a third family, arbitrary-candidate support,
   or frozen-after-selection generalization.
8. **Usability red line.** A2 contains no user study, task-time comparison,
   API-friction measurement, or evidence that V4 is easier than direct
   CUDA/OptiX. It may not support such a claim.
9. **Entry decision.** Goal5793 may proceed only after a returned review with
   P0=0/P1=0, exact owner absorption, and a separate S0 preregistration. This
   packet alone authorizes no entropy draw, selection, implementation, or run.

## Claim boundary to preserve

- Contribution under review: source-backed, identity-bound compatibility
  checking over a bounded two-geometry-family registered catalog.
- Not claimed: proof-carrying code, translation validation, abstract-
  interpretation soundness, refinement proof, soundness, completeness, or
  universal V4 gating.
- Authority producers and all external roots remain trusted computing base.
- Consumer linkage is an exact source-hash plus token witness, not a complete
  call-graph proof.
- The nine UNKNOWN rows remain unresolved and unbound; A2 does not hide them or
  upgrade them.
- No product usability, production readiness, performance, GPU/POD, public,
  publication, or submission claim is authorized.

## Requested output

Please save the returned review as:

`history/internal_docs/review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md`

Include the exact packet, manifest, audit, result, delivery-manifest, and this
CFR hashes; report P0/P1/P2/P3; and state explicitly whether Goal5793 S0 may be
considered after owner absorption.
""".encode("utf-8")

    entrypoint: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.external_review_entrypoint.v1",
        "entrypoint_sha256": "",
        "goal": "5789-A2",
        "date": "2026-08-21",
        "status": "READY_FOR_OWNER_SELECTED_EXTERNAL_REVIEW__GOAL5793_BLOCKED",
        "review_roots": identities
        + [
            {
                "path": CFR_REL,
                "bytes": len(cfr),
                "file_sha256": _sha(cfr),
            }
        ],
        "result_sha256": result["result_sha256"],
        "delivery_manifest_sha256": delivery["delivery_manifest_sha256"],
        "packet_audit_sha256": packet_audit["audit_sha256"],
        "requested_review_output": "history/internal_docs/review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md",
        "entry_gate": {
            "external_review_required": True,
            "returned_review_must_have_p0_0_p1_0": True,
            "owner_absorption_and_closure_required": True,
            "separate_goal5793_s0_preregistration_required": True,
            "goal5793_generalization_evidence_count": 0,
            "user_usability_study_count": 0,
        },
        "authorization": {
            "authorizes_external_reviewer_contact_by_this_file": False,
            "authorizes_goal5793": False,
            "authorizes_entropy_or_candidate_selection": False,
            "authorizes_implementation_or_execution": False,
            "authorizes_gpu_home_pod_or_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_product_change": False,
            "authorizes_publication_or_submission": False,
        },
    }
    entrypoint["entrypoint_sha256"] = _sha(
        _canonical({key: value for key, value in entrypoint.items() if key != "entrypoint_sha256"})
    )
    return cfr, entrypoint


def main() -> int:
    if CFR.exists() or ENTRYPOINT.exists():
        raise RuntimeError("Goal5789-A2 CFR/entrypoint outputs are create-only")
    cfr, entrypoint = build_outputs()
    CFR.parent.mkdir(parents=True, exist_ok=True)
    with CFR.open("xb") as handle:
        handle.write(cfr)
    try:
        with ENTRYPOINT.open("xb") as handle:
            handle.write(_pretty(entrypoint))
    except Exception:
        CFR.unlink(missing_ok=True)
        ENTRYPOINT.unlink(missing_ok=True)
        raise
    print(
        json.dumps(
            {
                "cfr_sha256": _sha(cfr),
                "cfr_bytes": len(cfr),
                "entrypoint_file_sha256": _sha(ENTRYPOINT.read_bytes()),
                "entrypoint_sha256": entrypoint["entrypoint_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
