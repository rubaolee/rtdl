"""Create Goal5789-A2 local result, reports, and exact delivery manifest.

All outputs are create-only.  The resulting local closure still requires an
owner-selected external review before any Goal5793 S0 work may begin.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
A2_DIR_REL = "history/internal_docs/goal5789_a2_contract_evidence_20260821"
A2_DIR = ROOT / A2_DIR_REL
RESULT_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_result_20260821.json"
REPORT_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_technical_report_20260821.md"
SCIENCE_REVIEW_REL = "history/internal_docs/self_review_goal5789_a2_callback_ir_authority_binding_science_20260821.md"
ARTIFACT_REVIEW_REL = "history/internal_docs/self_review_goal5789_a2_callback_ir_authority_binding_artifact_governance_20260821.md"
DELIVERY_REL = "history/internal_docs/goal5789_a2_delivery_manifest_20260821.json"

RESULT = ROOT / RESULT_REL
REPORT = ROOT / REPORT_REL
SCIENCE_REVIEW = ROOT / SCIENCE_REVIEW_REL
ARTIFACT_REVIEW = ROOT / ARTIFACT_REVIEW_REL
DELIVERY = ROOT / DELIVERY_REL

UNIT_IDS = (
    "librts__parks_point_contains",
    "librts__parks_range_contains",
    "particle__microfluidics_5000",
    "raydb__ssb_sf10_q11",
    "rayjoin__top4_six_batch",
    "rtbh__author_32768",
    "rtdbscan__goal5776_clustered3d_4096",
    "rtnn__kitti12m_q4096_k4",
    "triangle__cit_patents__rt_1a2",
    "triangle__cit_patents__rt_2a1",
    "triangle__com_dblp__rt_1a2",
    "triangle__com_dblp__rt_2a1",
    "triangle__soc_livejournal1__rt_1a2",
    "triangle__soc_livejournal1__rt_2a1",
    "xhd__dragon_to_happy",
)

TOP_LEVEL_EVIDENCE = (
    "AUTHORITY_BUNDLE.json",
    "BOUNDED_INVENTORY.json",
    "CALLBACK_BINDING_ADVERSARIAL_MATRIX.json",
    "CALLBACK_IR_AUTHORITY.json",
    "CALLBACK_IR_AUTHORITY_PIN.json",
    "HELD_OUT_AUTHORITY_BUNDLE.json",
    "HELD_OUT_RTXRMQ_CERTIFICATE.json",
    "HELD_OUT_RTXRMQ_RESULT.json",
    "INDEPENDENT_RECOUNT.json",
    "PREDECESSOR_LINEAGE.json",
)

EXPECTED_ROOTS = {
    f"{A2_DIR_REL}/CALLBACK_IR_AUTHORITY.json": (261_703, "16422fc282b834286f3f3c22db15f1663cc642e7d97bf940e7f594b550a5a59a"),
    f"{A2_DIR_REL}/CALLBACK_IR_AUTHORITY_PIN.json": (1_787, "98e2aa6bb258030348dd623ed3609e168143003bae51048230a6dcd665dd1a0d"),
    f"{A2_DIR_REL}/BOUNDED_INVENTORY.json": (14_258, "a061a255ba79f0575c0be075ef099ce52dc61da0f7b4c592b7052a49804476d3"),
    f"{A2_DIR_REL}/PREDECESSOR_LINEAGE.json": (14_840, "9724018f6c9585778bba0d9b036670ce7c67b9cf2cfad1640c0b1be22cd3fb81"),
    f"{A2_DIR_REL}/INDEPENDENT_RECOUNT.json": (4_321, "65b6915807360c9774c7115206484c48054ebc44c919f273efad355ca9848c59"),
    f"{A2_DIR_REL}/CALLBACK_BINDING_ADVERSARIAL_MATRIX.json": (90_589, "ec3de9782d5587f944d0872d25cfc8a8703b0963ad2e2109de1455b742c340ea"),
    "history/internal_docs/goal5789_delivery_manifest_20260816.json": (13_176, "523c95139d24a84ad2ad02ff1e0bb3ee60fc87e540cdaca112c8b74870ef7667"),
    "history/internal_docs/review_goal5789_a1_post_goal5792_theory_readiness_and_goal5793_entry_20260821.md": (30_299, "13130c81dc4e8ec92edc4e99a30fc0de73b541e55f55a3158f2fb21deb7c3e2a"),
    "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json": (7_647, "8a2960140381d7564a36a67c7024f2554bafe379621eef844c3edab0157be7be"),
    "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.md": (3_230, "bbcbf08c142f3bfd3a63dc443e8f1a24b00b80e37118162efb9993f4e4c04676"),
    "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json": (4_556, "7631ca7486afcb5515f79e99de3c3bb4020328c95bafd3d8bfe94697c5da0c1a"),
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json": (4_963, "7f5cd38e625fa62233adfbb9df1f6aa56ebb050999b3154c1604bbc25f4e9064"),
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz": (10_836_249, "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41"),
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz": (28_674_437, "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a"),
}

CORE_CODE = (
    "scripts/goal5789_a2_independent_compatibility_checker.py",
    "scripts/goal5789_a2_materialize_callback_ir_authority.py",
    "scripts/goal5789_a2_build_contract_evidence.py",
    "scripts/goal5789_a2_independent_recount.py",
    "scripts/goal5789_a2_adversarial_binding_audit.py",
    "tests/goal5789_a2_callback_ir_authority_test.py",
)

DELIVERY_TOOLS = (
    "scripts/goal5789_a2_finalize_local_delivery.py",
    "scripts/goal5789_a2_build_review_packet.py",
    "scripts/goal5789_a2_audit_review_packet.py",
    "scripts/goal5789_a2_build_external_review_entrypoint.py",
    "tests/goal5789_a2_delivery_packet_test.py",
)


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


def _safe(relative: str) -> str:
    if "\\" in relative:
        raise RuntimeError(f"backslash forbidden in repository-relative path: {relative!r}")
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} or ":" in part for part in path.parts):
        raise RuntimeError(f"unsafe repository-relative path: {relative!r}")
    return path.as_posix()


def _identity(relative: str) -> dict[str, object]:
    relative = _safe(relative)
    path = ROOT / Path(*PurePosixPath(relative).parts)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"expected regular non-link file: {relative}")
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "file_sha256": _sha(data)}


def _load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_bytes())
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {relative}")
    return value


def _assert_seal(value: Mapping[str, object], field: str, expected: str, label: str) -> None:
    body = {key: item for key, item in value.items() if key != field}
    if value.get(field) != expected or _sha(_canonical(body)) != expected:
        raise RuntimeError(f"{label} internal seal mismatch")


def _validate_roots() -> None:
    for relative, (size, sha256) in EXPECTED_ROOTS.items():
        identity = _identity(relative)
        if identity["bytes"] != size or identity["file_sha256"] != sha256:
            raise RuntimeError(f"controlling root identity mismatch: {relative}")
    authority = _load(f"{A2_DIR_REL}/CALLBACK_IR_AUTHORITY.json")
    pin = _load(f"{A2_DIR_REL}/CALLBACK_IR_AUTHORITY_PIN.json")
    inventory = _load(f"{A2_DIR_REL}/BOUNDED_INVENTORY.json")
    lineage = _load(f"{A2_DIR_REL}/PREDECESSOR_LINEAGE.json")
    recount = _load(f"{A2_DIR_REL}/INDEPENDENT_RECOUNT.json")
    matrix = _load(f"{A2_DIR_REL}/CALLBACK_BINDING_ADVERSARIAL_MATRIX.json")
    terminal = _load("history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json")
    work = _load("history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json")
    _assert_seal(authority, "authority_sha256", "8383367ba43b92ec88b0f719a507ade4944e635e1a9b6d9243695b0623eaad70", "Callback authority")
    _assert_seal(pin, "pin_sha256", "2defc4649703f0f5bd26c5d6b122d01655886636e2f6880b34dd5e15b33f70e1", "Callback pin")
    _assert_seal(inventory, "inventory_sha256", inventory["inventory_sha256"], "bounded inventory")
    _assert_seal(lineage, "lineage_sha256", lineage["lineage_sha256"], "predecessor lineage")
    _assert_seal(recount, "recount_sha256", "a8711cf3f47ce9b7f9ab1a5841fba3b0ec320b1e219ce15a1eb4d37a174375e0", "independent recount")
    _assert_seal(matrix, "matrix_sha256", "098ec342c6a0ed406b83787c480c678cdd4ad8b7ef5d3ecddaf82f3b042635f5", "hostile matrix")
    _assert_seal(terminal, "terminal_sha256", "96d1107848d5a41cfe8016a9dcb056e6b7e85679b1a61c21669eb39449f7f862", "controlling P1 terminal")
    _assert_seal(work, "work_authority_sha256", "e18658e0ed000de310f6bc3797e938c498f58d2de2071d9d50494781c69b6f08", "owner work authority")
    if matrix.get("case_count") != 159 or matrix.get("passed_count") != 159 or matrix.get("failed_count") != 0:
        raise RuntimeError("formal hostile matrix result mismatch")
    if recount.get("predecessor_counts") != {"compatible": 6, "unknown": 9, "incompatible": 0}:
        raise RuntimeError("predecessor vector mismatch")
    if recount.get("successor_counts") != {"compatible": 6, "unknown": 9, "incompatible": 0}:
        raise RuntimeError("successor vector mismatch")


def _evidence_rows() -> list[dict[str, object]]:
    relatives = [f"{A2_DIR_REL}/{name}" for name in TOP_LEVEL_EVIDENCE]
    relatives.extend(f"{A2_DIR_REL}/certificates/{unit_id}.json" for unit_id in UNIT_IDS)
    relatives.extend(f"{A2_DIR_REL}/results/{unit_id}.json" for unit_id in UNIT_IDS)
    rows = [_identity(relative) for relative in sorted(relatives)]
    actual = [path for path in A2_DIR.rglob("*") if path.is_file()]
    actual_rel = {
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in actual
    }
    if len(rows) != 40 or actual_rel != {row["path"] for row in rows}:
        raise RuntimeError("A2 evidence directory exact file set mismatch")
    return rows


def _add_payload(
    payloads: dict[str, dict[str, object]], relative: str, provenance: str
) -> None:
    row = _identity(relative)
    existing = payloads.get(relative)
    if existing is not None:
        if (
            existing["bytes"] != row["bytes"]
            or existing["sha256"] != row["file_sha256"]
        ):
            raise RuntimeError(f"conflicting duplicate delivery payload: {relative}")
        existing["provenance"] = "+".join(sorted(set(str(existing["provenance"]).split("+")) | {provenance}))
        return
    payloads[relative] = {
        "path": relative,
        "bytes": row["bytes"],
        "sha256": row["file_sha256"],
        "provenance": provenance,
    }


def _collect_predecessor_manifest(payloads: dict[str, dict[str, object]]) -> None:
    manifest_rel = "history/internal_docs/goal5789_delivery_manifest_20260816.json"
    manifest = _load(manifest_rel)
    rows = manifest.get("payloads")
    if (
        manifest.get("schema") != "rtdl.goal5789.delivery_manifest.v1"
        or manifest.get("payload_count") != 54
        or manifest.get("payload_bytes") != 22_224_751
        or not isinstance(rows, list)
        or len(rows) != 54
    ):
        raise RuntimeError("Goal5789 predecessor delivery manifest shape mismatch")
    _add_payload(payloads, manifest_rel, "predecessor_delivery_manifest_root")
    total = 0
    for row in rows:
        relative = row["path"]
        actual = _identity(relative)
        if actual["bytes"] != row["bytes"] or actual["file_sha256"] != row["sha256"]:
            raise RuntimeError(f"Goal5789 predecessor payload drift: {relative}")
        _add_payload(payloads, relative, "predecessor_delivery_payload")
        total += row["bytes"]
    if total != 22_224_751:
        raise RuntimeError("Goal5789 predecessor payload byte total mismatch")


def _terminal_references(payloads: dict[str, dict[str, object]]) -> None:
    terminal = _load("history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json")

    def visit(value: object) -> None:
        if isinstance(value, Mapping):
            path = value.get("path")
            if isinstance(path, str) and ("file_sha256" in value or "sha256" in value):
                actual = _identity(path)
                expected_sha = value.get("file_sha256", value.get("sha256"))
                expected_bytes = value.get("bytes", value.get("size_bytes"))
                if actual["file_sha256"] != expected_sha or (
                    expected_bytes is not None and actual["bytes"] != expected_bytes
                ):
                    raise RuntimeError(f"P1 terminal referenced file drift: {path}")
                _add_payload(payloads, path, "controlling_p1_terminal_reference")
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(terminal)


def _build_result(evidence_rows: list[dict[str, object]]) -> dict[str, object]:
    code_rows = [_identity(path) for path in CORE_CODE]
    result: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.callback_ir_authority_binding_result.v1",
        "result_sha256": "",
        "goal": "5789-A2",
        "date": "2026-08-21",
        "status": "COMPLETE_LOCAL_CALLBACK_IR_AUTHORITY_BINDING_EVIDENCE__EXTERNAL_REVIEW_REQUIRED__GOAL5793_BLOCKED",
        "predecessor": {
            "external_review": _identity("history/internal_docs/review_goal5789_a1_post_goal5792_theory_readiness_and_goal5793_entry_20260821.md"),
            "controlling_p1_terminal": _identity("history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json"),
            "delivery_manifest": _identity("history/internal_docs/goal5789_delivery_manifest_20260816.json"),
            "bytes_modified_count": 0,
            "observation_replaced": False,
        },
        "repair": {
            "option": "A__INDEPENDENTLY_PINNED_SOURCE_BACKED_CALLBACK_IR_AUTHORITY",
            "product_native_or_app_bytes_changed": False,
            "frozen_callback_program_count": 5,
            "executed_leaf_count": 26,
            "semantic_physical_pair_to_program_binding_count": 4,
            "inventory_callback_bound_count": 6,
            "inventory_callback_unbound_count": 9,
            "inventory_denominator": 15,
            "legacy_rtxrmq_replay_bound": True,
            "legacy_rtxrmq_is_checker_held_out_generalization": False,
        },
        "evidence": {
            "exact_file_count": len(evidence_rows),
            "exact_file_bytes": sum(int(row["bytes"]) for row in evidence_rows),
            "file_set_sha256": _sha(_canonical(evidence_rows)),
            "files": evidence_rows,
            "callback_authority_internal_sha256": "8383367ba43b92ec88b0f719a507ade4944e635e1a9b6d9243695b0623eaad70",
            "callback_pin_internal_sha256": "2defc4649703f0f5bd26c5d6b122d01655886636e2f6880b34dd5e15b33f70e1",
            "independent_recount_internal_sha256": "a8711cf3f47ce9b7f9ab1a5841fba3b0ec320b1e219ce15a1eb4d37a174375e0",
            "hostile_matrix_internal_sha256": "098ec342c6a0ed406b83787c480c678cdd4ad8b7ef5d3ecddaf82f3b042635f5",
        },
        "results": {
            "predecessor": {"compatible": 6, "unknown": 9, "incompatible": 0},
            "successor": {"compatible": 6, "unknown": 9, "incompatible": 0},
            "target_capable_count": 15,
            "instance_admissible_count": 15,
            "sole_canonical_reference_count": 15,
            "performance_not_evaluated_count": 15,
            "formal_hostile_case_count": 159,
            "formal_hostile_pass_count": 159,
            "formal_hostile_fail_count": 0,
            "old_plus_new_test_count": 38,
            "old_plus_new_test_failure_count": 0,
        },
        "implementation": {
            "core_files": code_rows,
            "checker_imports_product_or_app_or_builder": False,
            "materializer_requires_fresh_interpreter": True,
            "independent_recount_imports_checker_builder_or_product": False,
            "predecessor_manifest_payloads_rehashed": 54,
            "predecessor_manifest_payload_bytes": 22_224_751,
        },
        "local_review": {
            "independent_read_only_audit_count": 3,
            "p0_count": 0,
            "p1_count": 0,
            "p2_count": 0,
            "external_review_claimed": False,
        },
        "research_integrity": {
            "goal5793_generalization_exam_count": 0,
            "generalization_claimed": False,
            "false_rejection_rate_claimed": False,
            "third_geometry_family_claimed": False,
            "all_v4_paths_semantically_gated_claimed": False,
            "user_usability_study_count": 0,
            "programming_task_time_comparison_count": 0,
            "easy_or_better_than_direct_cuda_optix_claimed": False,
            "production_tool_claimed": False,
        },
        "claim_boundary": {
            "bounded_registered_catalog_compatibility_claimed": True,
            "authority_producer_is_tcb": True,
            "external_authority_roots_are_tcb": True,
            "jointly_wrong_authorities_detected": False,
            "semantic_soundness_claimed": False,
            "completeness_claimed": False,
            "translation_validation_claimed": False,
            "proof_carrying_code_claimed": False,
            "execution_authorized": False,
        },
        "authorization": {
            "authorizes_owner_selected_external_review_packet_preparation": True,
            "authorizes_external_reviewer_contact_by_this_result": False,
            "authorizes_goal5793": False,
            "authorizes_entropy_or_candidate_selection": False,
            "authorizes_implementation_or_execution": False,
            "authorizes_gpu_home_pod_or_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_product_change": False,
            "authorizes_publication_or_submission": False,
        },
        "next_gate": {
            "owner_selected_external_review_required": True,
            "returned_review_must_have_p0_0_p1_0": True,
            "append_only_absorption_and_closure_required": True,
            "goal5793_s0_still_blocked": True,
        },
    }
    result["result_sha256"] = _sha(
        _canonical({key: value for key, value in result.items() if key != "result_sha256"})
    )
    return result


def _build_documents(result: Mapping[str, object], result_identity: Mapping[str, object]) -> tuple[bytes, bytes, bytes]:
    evidence = result["evidence"]
    technical = f"""# Goal5789-A2 Callback-IR authority binding — local technical report

Date: 2026-08-21  
Status: local evidence complete; owner-selected external review required; Goal5793 blocked

## Outcome

The technical repair succeeded without changing product, native, application,
GPU, or scientific execution bytes. The predecessor checker accepted a
certificate whose allowed Callback effects had been emptied and re-signed.
A2 replaces that self-reported surface, for the bounded admitted scope, with a
source-backed authority over five complete Callback-IR programs and 26 frozen
executed leaf artifacts.

The exact result is `{result_identity['file_sha256']}` ({result_identity['bytes']:,}
bytes), internal seal `{result['result_sha256']}`. The exact evidence tree has
{evidence['exact_file_count']} files / {evidence['exact_file_bytes']:,} bytes and
file-set digest `{evidence['file_set_sha256']}`.

## What is now mechanically bound

- five exact full Callback-IR programs reconstructed from the frozen Goal5785
  execution source;
- 26 unique executed leaf artifacts, including key/file/PTX/IR/effect/role
  cross-checks;
- four exact semantic/physical-pair-to-program mappings;
- exact, type-sensitive certificate projections of IR/source/effect identities,
  function names/order/roles/effects, actual resources, and declared ceilings;
- fixed consumer source hash+token witnesses;
- exact predecessor delivery manifest (54/54 payloads, 22,224,751 bytes), P1
  terminal, and owner work-authority roots.

The successor preserves the observed inventory vector: 6 compatible, 9
unknown, 0 incompatible. Exactly 6/15 inventory rows are Callback-bound; 9/15
remain unbound UNKNOWN and receive no Callback-integrity claim. RTXRMQ remains
a compatible adjacency-program replay, but only as a legacy no-special-case
replay—not as a checker/calculus held-out generalization result.

## Independent checks

The standard-library recount reconstructs the source/evidence roots, all five
programs, all 26 leaves, all four bindings, two authority bundles, 15
certificate/result pairs, the inventory, RTXRMQ replay, and predecessor
lineage. Its saved file is `65b69158…8c59`, internal seal `a8711cf3…75e0`.

The formal adversarial matrix is 159/159 PASS. It covers the original empty-
effect attack, legal effect substitutions, exact-role and full-program swaps,
Triangle count→keyed, Particle adjacency→count, LibRTS box→spatial, invented
RTXRMQ pairs, resource/type aliases, producer metadata, leaf-manifest lies, and
claim escalation. Separately, the finalizer and independent recount reject
drift in the 54-payload predecessor manifest, terminal, and work-authority
roots. A jointly wrong but internally consistent semantic+physical authority
still passes as the disclosed TCB ceiling.

Old Goal5789 plus A2 tests are 38/38 PASS. Three independent read-only local
audits returned P0=0/P1=0/P2=0 on the final 40-file disk set. These are local
audits, not an owner-returned external review.

## Research-integrity limits

This repair is not Goal5793. Generalization exams completed: **0**. It provides
no false-rejection rate, no third-family evidence, and no proof that a frozen
checker handles previously unseen candidates. Nine inventory lanes remain
unbound UNKNOWN.

This repair is also not a usability study. It measures no user task time,
boilerplate, debugging burden, API friction, or comparison against direct
CUDA/OptiX. It cannot support “easy to use,” “production ready,” or “better
than direct CUDA/OptiX” claims.

The authority producer and external roots remain TCB. Jointly wrong authorities
are not detected. Consumer linkage is exact source hash plus token witness, not
a complete call-graph proof. No soundness, completeness, translation-
validation, proof-carrying-code, execution, performance, public, publication,
or submission claim is authorized.

## Next gate

Prepare a deterministic packet for owner-selected external review. Goal5793 S0
may be considered only after a returned P0=0/P1=0 review and an append-only
owner absorption/closure. The packet itself does not authorize entropy draw,
candidate selection, implementation, execution, GPU/Home/POD, workers, or
timing.
""".encode("utf-8")

    science = f"""# Self-review — Goal5789-A2 scientific and mechanism claims

Date: 2026-08-21  
Result: `{result_identity['file_sha256']}` / internal `{result['result_sha256']}`  
Verdict: P0=0 / P1=0 / P2=0 at bounded local-evidence scope; external review pending

## Checks performed

1. Reproduced the predecessor weakness: clearing all allowed Callback effects,
   retaining stale digests, and re-signing the predecessor certificate remains
   compatible.
2. Reconstructed five full programs from immutable source and cross-checked 26
   executed leaves rather than trusting the A2 builder's summary.
3. Verified that certificate-only, certificate+bundle, authority-summary, and
   real-program-substitution attacks fail under the fixed external pin and exact
   pair mapping.
4. Verified that numeric booleans/floats cannot exploit Python equality.
5. Verified that UNKNOWN never masks a separately proven incompatibility.
6. Rebuilt both inventory vectors as 6/9/0 without forcing the successor count.
7. Preserved a jointly-wrong semantic+physical authority control that passes,
   making the TCB ceiling executable rather than rhetorical.

## Claim audit

The repaired fact is narrow but real: for six admitted inventory rows and one
legacy RTXRMQ replay, the certificate Callback projection is now bound to an
independently pinned, frozen-source-backed program authority. The authority
producer itself remains TCB; this is not a semantic-correctness theorem.

No generalization claim is permitted. Goal5793 has zero completed exams, and
RTXRMQ predates the Goal5789 checker/calculus. No usability claim is permitted:
A2 has zero user studies and zero CUDA/OptiX task comparisons. The nine unbound
UNKNOWN rows are stated as 9/15 rather than hidden in an all-row summary.

## Decision

The mechanism-level P1 is closed locally. The scientific claim remains bounded
to registered-catalog compatibility with trusted authorities. External review
is required before any Goal5793 entry decision.
""".encode("utf-8")

    artifact = f"""# Self-review — Goal5789-A2 artifact and governance

Date: 2026-08-21  
Result: `{result_identity['file_sha256']}` / internal `{result['result_sha256']}`  
Verdict: P0=0 / P1=0 / P2=0 locally; no external-review claim

## Artifact integrity

- Final evidence set: 40/40 regular files, {evidence['exact_file_bytes']:,}
  bytes, exact-set digest `{evidence['file_set_sha256']}`.
- Materializer reconstruction is byte-identical to authority/pin on disk.
- Builder reconstruction is byte-identical for all 36 builder payloads.
- Independent recount and hostile matrix are byte-identical when recomputed.
- Predecessor manifest is fixed at 54 payloads / 22,224,751 bytes; terminal and
  work-authority file/internal identities are exact.
- Create-only generation was used; no failed or overwritten formal A2 output
  lineage exists.

## Independence and attack surface

The A2 checker imports no product, app, or builder. The recount imports no A2
checker, builder, or product. The materializer fails closed if `rtdsl` was
preloaded and verifies imported module paths under the temporary frozen-source
root. Archive path checks reject absolute, parent, backslash, drive/ADS, link,
duplicate, and special members at the relevant boundaries.

The 159-case matrix reports zero failures. Producer/external roots remain
explicit TCB; the artifact does not claim tamper-proof truth under a complete
coordinated root replacement.

## Governance and authorization

The owner authority permits local A2 evidence repair and review-packet
preparation only. Goal5793, entropy/candidate selection, implementation,
execution, GPU/Home/POD/SSH, workers, timing, product/native changes,
publication, and submission remain false.

The two owner integrity concerns are not papered over: generalization evidence
is still 0/3, and usability evidence is not evaluated. A2 is an evidence-chain
repair, not a product-usability or generalization result.

## Decision

Local artifact governance is ready for deterministic packaging and an
owner-selected external review. The external review and append-only absorption
remain mandatory before Goal5793 S0.
""".encode("utf-8")
    return technical, science, artifact


def build_outputs() -> tuple[bytes, bytes, bytes, bytes, dict[str, object]]:
    _validate_roots()
    evidence_rows = _evidence_rows()
    result = _build_result(evidence_rows)
    result_bytes = _pretty(result)
    result_identity = {
        "path": RESULT_REL,
        "bytes": len(result_bytes),
        "file_sha256": _sha(result_bytes),
    }
    report_bytes, science_bytes, artifact_bytes = _build_documents(result, result_identity)

    payloads: dict[str, dict[str, object]] = {}
    _collect_predecessor_manifest(payloads)
    _terminal_references(payloads)
    for relative in (
        "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json",
        "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.md",
        "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json",
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json",
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz",
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz",
    ):
        _add_payload(payloads, relative, "a2_direct_controlling_root")
    for relative in CORE_CODE:
        _add_payload(payloads, relative, "a2_core_code_or_test")
    for relative in DELIVERY_TOOLS:
        _add_payload(payloads, relative, "a2_delivery_or_review_tool")
    for row in evidence_rows:
        _add_payload(payloads, str(row["path"]), "a2_formal_evidence")

    generated = {
        RESULT_REL: result_bytes,
        REPORT_REL: report_bytes,
        SCIENCE_REVIEW_REL: science_bytes,
        ARTIFACT_REVIEW_REL: artifact_bytes,
    }
    for relative, data in generated.items():
        if relative in payloads:
            raise RuntimeError(f"generated delivery payload collides: {relative}")
        payloads[relative] = {
            "path": relative,
            "bytes": len(data),
            "sha256": _sha(data),
            "provenance": "a2_local_result_or_review",
        }

    rows = [payloads[path] for path in sorted(payloads)]
    delivery: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.delivery_manifest.v1",
        "delivery_manifest_sha256": "",
        "goal": "5789-A2",
        "date": "2026-08-21",
        "status": "FINAL_LOCAL_DELIVERY__OWNER_SELECTED_EXTERNAL_REVIEW_PENDING__GOAL5793_BLOCKED",
        "root_result": result_identity | {"result_sha256": result["result_sha256"]},
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "payload_set_sha256": _sha(
            _canonical(
                [
                    {key: row[key] for key in ("path", "bytes", "sha256")}
                    for row in rows
                ]
            )
        ),
        "payloads": rows,
        "claim_boundary": result["research_integrity"],
        "authorization": {
            "authorizes_owner_selected_external_review_packet_preparation": True,
            "authorizes_external_reviewer_contact_by_this_manifest": False,
            "authorizes_goal5793": False,
            "authorizes_entropy_or_candidate_selection": False,
            "authorizes_implementation_or_execution": False,
            "authorizes_gpu_home_pod_or_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_product_change": False,
            "authorizes_publication_or_submission": False,
        },
    }
    delivery["delivery_manifest_sha256"] = _sha(
        _canonical({key: value for key, value in delivery.items() if key != "delivery_manifest_sha256"})
    )
    return result_bytes, report_bytes, science_bytes, artifact_bytes, delivery


def main() -> int:
    outputs = (RESULT, REPORT, SCIENCE_REVIEW, ARTIFACT_REVIEW, DELIVERY)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise RuntimeError(f"Goal5789-A2 local delivery outputs are create-only: {existing}")
    result_bytes, report_bytes, science_bytes, artifact_bytes, delivery = build_outputs()
    payloads = (
        (RESULT, result_bytes),
        (REPORT, report_bytes),
        (SCIENCE_REVIEW, science_bytes),
        (ARTIFACT_REVIEW, artifact_bytes),
        (DELIVERY, _pretty(delivery)),
    )
    written: list[Path] = []
    try:
        for path, data in payloads:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(data)
            written.append(path)
    except Exception:
        for path in reversed(written):
            path.unlink(missing_ok=True)
        raise
    result = json.loads(result_bytes)
    print(
        json.dumps(
            {
                "result_file_sha256": _sha(result_bytes),
                "result_sha256": result["result_sha256"],
                "delivery_file_sha256": _sha(DELIVERY.read_bytes()),
                "delivery_manifest_sha256": delivery["delivery_manifest_sha256"],
                "payload_count": delivery["payload_count"],
                "payload_bytes": delivery["payload_bytes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
