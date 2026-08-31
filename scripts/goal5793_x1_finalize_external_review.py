"""Create the single-file Goal5793 X1 external-review delivery."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
from typing import Any

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts.goal5793_x1_readiness_gate import readiness


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DATE = "2026-08-22"
EMBEDDED_MANIFEST = "GOAL5793_X1_EXTERNAL_REVIEW_MANIFEST.json"
PACKET_NAME = "goal5793_x1_external_review_single_file_20260822.tar.gz"
TWIN_NAME = "goal5793_x1_external_review_single_file_twin_20260822.tar.gz"
MANIFEST_NAME = "goal5793_x1_external_review_single_file_manifest_20260822.json"
AUDIT_NAME = "goal5793_x1_external_review_single_file_audit_20260822.json"
OWNER_NAME = "goal5793_x1_owner_local_linux_directive_record_20260822.json"
RESULT_NAME = "goal5793_x1_external_review_result_20260822.json"
REPORT_NAME = "goal5793_x1_external_review_technical_report_20260822.md"
SELF_REVIEW_NAME = "self_review_goal5793_x1_external_review_20260822.md"
CFR_NAME = "call_for_review_goal5793_x1_generic_examiner_environment_and_exposure_boundary_20260822.md"

FIXED_EVIDENCE: list[tuple[str, str, str]] = [
    ("evidence/s0/reproduction_capsule.tar.gz", "history/internal_docs/goal5793_x1_s0_reproduction_capsule_20260822.tar.gz", "S0_REPRODUCTION_CAPSULE"),
    ("evidence/s0/reproduction_manifest.json", "history/internal_docs/goal5793_x1_s0_reproduction_capsule_manifest_20260822.json", "S0_REPRODUCTION_MANIFEST"),
    ("evidence/s0/reproduction_audit.json", "history/internal_docs/goal5793_x1_s0_reproduction_capsule_audit_20260822.json", "S0_REPRODUCTION_AUDIT"),
    ("evidence/s0/returned_review.md", "history/internal_docs/review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md", "S0_RETURNED_REVIEW"),
    ("evidence/s0/owner_closure.json", "history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json", "S0_OWNER_CLOSURE"),
    ("evidence/exposure/survey_registry_v2.json", "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json", "SURVEY_186_ENTRY_REGISTRY"),
    ("evidence/exposure/declared_successor_registry_blocker.json", "history/internal_docs/goal5793_x1_declared_project_exposure_registry_blocker_20260822.json", "DECLARED_SUCCESSOR_EXPOSURE_REGISTRY"),
    ("evidence/exposure/no_memory_attestation_boundary.json", "history/internal_docs/goal5793_x1_no_owner_memory_attestation_boundary_20260822.json", "CONSERVATIVE_NO_MEMORY_ATTESTATION_BOUNDARY"),
    ("evidence/exposure/pinned_survey_source.tar", "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar", "PINNED_SURVEY_SOURCE_ARCHIVE"),
    ("evidence/mechanism/positive_vector_freeze.json", "history/internal_docs/goal5793_x1_positive_vector_freeze_20260822.json", "HISTORICAL_POSITIVE_VECTOR_FREEZE"),
    ("evidence/mechanism/historical_registry_authority.json", "history/internal_docs/goal5793_x1_historical_registry_authority_20260822.json", "HISTORICAL_REGISTRY_AUTHORITY"),
    ("evidence/mechanism/historical_registry_stage_pin.json", "history/internal_docs/goal5793_x1_historical_registry_stage_pin_20260822.json", "HISTORICAL_REGISTRY_STAGE_PIN"),
    ("evidence/mechanism/historical_registry_fixtures.json", "history/internal_docs/goal5793_x1_historical_registry_fixtures_20260822.json", "HISTORICAL_REGISTRY_FIXTURES"),
    ("evidence/mechanism/historical_candidate_envelope.json", "history/internal_docs/goal5793_x1_historical_runner_candidate_envelope_20260822.json", "HISTORICAL_CANDIDATE_ENVELOPE"),
    ("evidence/mechanism/historical_fresh_process_receipt.json", "history/internal_docs/goal5793_x1_historical_fresh_process_exam_receipt_20260822.json", "HISTORICAL_FRESH_PROCESS_RECEIPT"),
    ("evidence/environment/exact_capture_request.json", "history/internal_docs/goal5793_x1_exact_environment_capture_request_20260822.json", "EXACT_ENVIRONMENT_REQUEST"),
    ("evidence/environment/exact_capture.json", "history/internal_docs/goal5793_x1_exact_environment_capture_20260822.json", "EXACT_ENVIRONMENT_AUTHORITY"),
    ("evidence/environment/exact_capsule.tar.gz", "history/internal_docs/goal5793_x1_exact_environment_capsule_20260822.tar.gz", "SELF_CONTAINED_EXACT_ENVIRONMENT_CAPSULE"),
    ("evidence/environment/exact_capsule_manifest.json", "history/internal_docs/goal5793_x1_exact_environment_capsule_manifest_20260822.json", "EXACT_ENVIRONMENT_CAPSULE_MANIFEST"),
    ("evidence/environment/exact_capsule_audit.json", "history/internal_docs/goal5793_x1_exact_environment_capsule_audit_20260822.json", "EXACT_ENVIRONMENT_CAPSULE_AUDIT"),
    ("evidence/environment/native_trace_authority.json", "history/internal_docs/goal5793_x1_native_trace_authority_20260822.json", "NATIVE_TRACE_AUTHORITY"),
]


class FinalizeError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _identity(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _bytes_identity(payload: bytes) -> dict[str, object]:
    return {"bytes": len(payload), "sha256": _sha256_bytes(payload)}


def _safe_name(name: str) -> None:
    if not name or "\\" in name or any(part in ("", ".", "..") for part in name.split("/")):
        raise FinalizeError(f"unsafe_member_name:{name}")


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizeError(f"json_root_not_object:{path}")
    return value


def _root_identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        raise FinalizeError(f"root_absent_or_nonregular:{relative}")
    return {"path": relative, **_identity(path)}


def _tool_rows() -> list[dict[str, object]]:
    paths = sorted(
        list((ROOT / "scripts").glob("goal5793_x1*.py")) + list((ROOT / "tests").glob("goal5793_x1*_test.py")),
        key=lambda path: path.relative_to(ROOT).as_posix().encode("utf-8"),
    )
    rows = [{"path": path.relative_to(ROOT).as_posix(), **_identity(path)} for path in paths]
    if len(rows) < 30:
        raise FinalizeError("x1_tool_test_surface_underexpected")
    return rows


def _owner_directive() -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.owner_local_linux_directive_record.v1",
        "date": DATE,
        "status": "OWNER_DIRECTED_LOCAL_LINUX_NON_GPU_X1_MATERIALIZATION_RECORDED__NOT_A_GPU_OR_EXAM_AUTHORIZATION",
        "verbatim_owner_messages": [
            "继续前进直至GOAL完成！",
            "你不要降智! 这些事情根本不需要回复和授权。去做！每当你让我事情的话，自己反愚蠢三问先！",
            "去翻历史记录，找到本地的linux",
            "别用WSL",
            "192.168.1.20",
        ],
        "implemented_interpretation": {
            "host": "192.168.1.20",
            "transport": "SSH to owner-designated local Linux host; WSL not used",
            "purpose": "X1 exact non-GPU environment and native materialization only",
            "gpu_device_or_driver_api_call_count": 0,
            "candidate_work_count": 0,
            "generality_exam_count": 0,
            "registered_or_performance_timing_count": 0,
            "native_trace_forbidden_gpu_marker_hit_count": 0,
        },
        "historical_scope_disclosure": {
            "s0_closure_had_pod_or_ssh_allowed": False,
            "later_owner_directive_used_as_successor_transport_authority": True,
            "external_reviewer_must_judge_this_successor_scope_explicitly": True,
        },
        "authorization": {
            "search": False, "entropy": False, "selection": False,
            "candidate_implementation_or_execution": False, "gpu_execution": False,
            "registered_or_performance_timing": False, "publication_or_submission": False,
        },
        "record_sha256": "",
    }
    value["record_sha256"] = seal_document(
        value, seal_field="record_sha256", domain="rtdl.goal5793.x1.owner_local_linux_directive_record", version=1,
    )
    return value


def _markdown_documents() -> tuple[bytes, bytes, bytes]:
    report = f"""# Goal5793 X1 technical report: examiner, exposure boundary, and exact environment

## Outcome first

X1 is ready for one bounded external review, not complete and not an empirical generalization result. The candidate-agnostic examiner, registry derivation, fresh-process runner, historical positive-vector freeze, S0 reproduction capsule, survey exposure component, conservative no-memory-attestation boundary, and an exact Linux execution-environment capsule are now frozen. Prospective generalization exams remain **0** and usability evidence remains **0**. In literal count terms, there are zero prospective Goal5793 exams.

The only external delivery is `{PACKET_NAME}`. The reviewer should open `ENTRYPOINT/{CFR_NAME}` inside it. No second packet, CFR attachment, or twin should be sent.

## Why this matters to the paper

This X1 freeze removes the most dangerous researcher degree of freedom before Goal5793: candidate identity, role and expected disposition are not examiner inputs; a future registry authority is trusted only through a separately frozen stage pin; product and independent recount disagreements become infrastructure-invalid; and the exact source/native/Python/CUDA/OptiX/runtime bytes are captured before any live expansion search. This is necessary anti-overfitting infrastructure. It is not evidence that the system generalizes.

The environment was materialized on the owner-designated local Linux host `192.168.1.20` over SSH after the owner explicitly said to use local Linux and not WSL. No WSL was used. The direct build trace has zero `nvidia-smi`, `/dev/nvidia`, or `libnvidia-ml` hits; there were zero GPU calls, candidate executions, and registered timings. The returned reviewer must explicitly judge this successor transport scope because the earlier S0 closure had stated no SSH.

## Examiner and registry facts

- The same frozen examiner accepts historical fixtures and a distinct legal future template only when an out-of-band stage pin matches.
- Missing pin, wrong trusted digest, authority drift, and receipt/authority mismatch fail closed.
- Thirty-five declaration rules are executed with exact product/independent parity. SP022 is a closed-policy unreachable fallback; SP063/SP070/SP071 are authority-only. We do not claim generic 39/39 coverage.
- The frozen historical inventory remains 6 COMPATIBLE / 9 UNKNOWN / 0 INCOMPATIBLE. Seven positive provenances reduce to four structural vectors; Particle and RTXRMQ share a byte-identical callback program, so that program does not semantically distinguish them.
- The fresh-process boundary is not hermetic: interpreter, standard library and OS remain TCB. Exact frozen environment bytes now make that TCB reviewable.

## Exposure boundary

The pinned survey bibliography contributes all 186 entries and all are permanently selection-ineligible. The current repository/Git/S0-DAG scan is a successor observation and explicitly records gaps; it cannot be backdated into a complete S0 workspace snapshot. The owner supplied no off-repository memory list, and no such attestation is requested or fabricated.

Therefore X1 asks the reviewer to accept a conservative alternative: never claim unseen, blind, held-out, or complete mental exposure; treat registry nonmatch only as nonmatch; and if later-discovered or later-recalled pre-X1 exposure matches a future row, terminate the entire single expansion with no replacement, reuse, second search, or rescue. X2 remains blocked unless the reviewer accepts this exact boundary and owner closure absorbs it.

## Exact environment capsule

The nested exact-environment capsule has 4,239 payloads, 886,521,284 payload bytes, payload-set digest `0eeaf48fb8a6c49267568007fda3e57205464dca8a12dd350cde8950fd121c6a`, and archive SHA-256 `90ff09e084c4b9e9ba0262dfe9dc2ef028b2777b98ce4c16a5a8f4e3b1fe41d9`. It carries the 326-file source bundle, direct-native trace inputs, exact stripped native and runtime libraries, frozen Python home, 44 Numba artifacts, CUDA entry header, OptiX headers, request/authority, builder and independent verifier. Its local twin is byte-identical but is not a second review attachment; the enclosing packet binds its identity and contains enough bytes to rebuild it.

## Claim and authorization ceiling

X1 proves only that the examination instrument and one exact target environment are frozen and reviewable. It proves no prospective generalization, false-rejection rate, soundness, completeness, third family, usability, productivity, superiority to CUDA/OptiX, performance, production readiness, publication readiness, or submission readiness. Search, entropy, selection, candidate implementation/execution, GPU execution, timing, publication and submission all remain unauthorized.
""".encode("utf-8")
    self_review = f"""# Self-review: Goal5793 X1 external-review freeze

Verdict: ready to ask for external review; X1 is not closed.

I tried to falsify four boundaries. First, a candidate-controlled registry cannot authenticate itself: the examiner requires a separately trusted exact stage pin. Second, preloaded same-name Python modules do not control the scientific modules, although an arbitrary hostile Python process remains outside the claim. Third, the Linux environment is self-contained at exact-byte replay scope and independently recounted; no GPU result was produced. Fourth, the absent historical untracked snapshot and absent owner memory list are not hidden or reconstructed. They are replaced only by a reviewer-visible termination-without-replacement boundary.

The strongest negative statement is intentional: this work still contains zero prospective Goal5793 exams and zero usability observations. The packet must not be cited as generalization or ease-of-use evidence. The only file sent for review is `{PACKET_NAME}`.
""".encode("utf-8")
    cfr = f"""# Call for review: Goal5793 X1 examiner, exposure boundary, and exact environment

**SEND ONLY THE ENCLOSING `{PACKET_NAME}` FILE TO THE REVIEWER.** This Markdown is its sole entrypoint. Do not send a separate CFR, evidence capsule, manifest, audit, or twin.

## One ruling requested

Does exact X1 freeze a candidate-agnostic examiner and externally pinned registry path, preserve the complete pinned 186-entry survey exposure component plus the declared successor repository/Git/S0-DAG observation, honestly replace unavailable memory/historical-untracked attestation with a no-unseen-claim and terminate-without-replacement boundary, and freeze a self-contained exact Linux execution environment—such that X1 may be accepted and **X2 offline implementation only** may be considered after append-only owner absorption, while live search, entropy, selection, candidate implementation/execution, GPU use and timing remain forbidden?

Return one file named `review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md`. Required fields: P0/P1/P2/P3; X1 accepted yes/no; conservative no-memory-attestation boundary accepted yes/no; owner-directed SSH-to-local-Linux successor scope accepted yes/no; and whether X2 offline implementation only may be considered after owner closure. Any P0 or P1 means X1 is not accepted.

## Required independent checks

1. Run `python3 tools/goal5793_x1_verify_external_review_packet.py <this archive>` from outside the repository. Confirm every payload, embedded manifest, canonical tar/gzip field, claim and authorization boundary.
2. Run the packaged X1 tests without network/GPU. Confirm the examiner ignores candidate identity/role/expected disposition, uses a separate stage pin, rejects authority/pin drift, treats product/recount disagreement as infrastructure-invalid, and does not let the historical A2 checker control a new candidate.
3. Reconstruct the 35 reachable declaration-rule cases and exact product/recount decision projection. Confirm SP022 is unreachable fallback and SP063/070/071 authority-only; reject any 39/39 declaration claim.
4. Rebuild the 15 historical lanes and seven positive provenances/four structural vectors. Confirm this is historical mechanism regression, not prospective generalization.
5. Verify `evidence/environment/exact_capsule.tar.gz` independently: 4,239 payloads, 886,521,284 bytes, payload-set `0eeaf48f…21c6a`, archive `90ff09e0…e41d9`; verify source/native/Python/runtime/header/cache identities and 0 GPU markers.
6. Verify all 186 pinned bibliography entries remain permanently selection-ineligible, all original 35 crosslink, and the survey source archive is exact `bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857` / 752,766 bytes.
7. Inspect the 246,627,536-byte successor exposure authority. Confirm it is not called an S0 snapshot or complete mental exposure; confirm its gaps remain visible.
8. Decide the conservative substitute on its actual terms: no owner memory attestation, no unseen/blind/held-out claim, registry nonmatch only, later prior-exposure discovery terminates the entire single expansion with no replacement. If this is insufficient, return P1 and keep X2 blocked; do not ask us to fabricate memory.
9. Confirm owner messages directed use of local Linux `192.168.1.20`, WSL was not used, SSH was the transport, and the preserved build trace had zero GPU markers. Explicitly decide whether this successor directive legitimately supersedes only the S0 no-SSH transport restriction without widening GPU/candidate/timing scope.
10. Confirm the nested S0 capsule closes S0 P2-1 and the 186-entry registry plus pinned survey source closes P2-2; canonicalization uses the single X1 helper without rewriting historical digests.
11. Confirm the packet and all documents state 0 prospective generality exams and 0 usability evidence and authorize no search, entropy, selection, candidate work, GPU, timing, publication or submission.

## Non-authorization

Acceptance is an instrument-freeze decision, not a paper-result decision. It does not establish generalization or usability. An accepted X1 owner closure may at most authorize the already preregistered X2 **offline** harvester/taxonomy/enumerator/NIST-verifier/selection-client implementation and synthetic tests. It must still authorize zero live provider calls, search executions, entropy anchors/draws, selections, candidate implementations/executions, GPU calls, POD/SSH, registered timings, publication or submission.
""".encode("utf-8")
    return report, self_review, cfr


def _documents() -> dict[str, bytes]:
    ready = readiness()
    if ready["blockers"] or ready["status"] != "READY_FOR_SINGLE_FILE_X1_EXTERNAL_REVIEW_WITH_NO_MEMORY_ATTESTATION":
        raise FinalizeError("readiness_gate_not_exact_review_ready")
    owner = _owner_directive()
    owner_bytes = canonical_json_bytes(owner) + b"\n"
    report, self_review, cfr = _markdown_documents()
    tool_rows = _tool_rows()
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.external_review_result.v1",
        "date": DATE,
        "status": "X1_FROZEN_READY_FOR_SINGLE_FILE_EXTERNAL_REVIEW__NOT_CLOSED__X2_AND_ALL_SCIENTIFIC_ACTIONS_BLOCKED",
        "s0_closure": _root_identity("history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json"),
        "readiness": ready,
        "owner_local_linux_directive": {"path": f"history/internal_docs/{OWNER_NAME}", **_bytes_identity(owner_bytes), "record_sha256": owner["record_sha256"]},
        "mechanism": {
            "declaration_rule_count": 39, "declaration_rules_executed_with_product_recount_parity": 35,
            "closed_policy_unreachable_fallback_rule_ids": ["SP022"],
            "authority_only_rule_ids": ["SP063", "SP070", "SP071"],
            "historical_inventory": {"compatible": 6, "unknown": 9, "incompatible": 0},
            "positive_provenance_count": 7, "unique_structural_vector_count": 4,
            "future_authority_requires_out_of_band_trusted_stage_pin": True,
            "candidate_identity_role_expected_disposition_are_examiner_inputs": False,
            "product_recount_disagreement_selects_favorable_verdict": False,
            "fresh_process_is_hermetic_or_hostile_process_sandbox": False,
        },
        "exposure_boundary": {
            "survey_bibliography_entry_count": 186, "survey_entries_selection_eligible": 0,
            "declared_successor_registry_file": _root_identity("history/internal_docs/goal5793_x1_declared_project_exposure_registry_blocker_20260822.json"),
            "complete_historical_s0_untracked_snapshot_available": False,
            "owner_off_repository_memory_attestation_provided": False,
            "unseen_blind_held_out_or_complete_mental_exposure_claimed": False,
            "registry_nonmatch_means_only_nonmatch": True,
            "later_pre_x1_exposure_discovery_action": "TERMINATE_SINGLE_EXPANSION__NO_REPLACEMENT_REUSE_OR_SECOND_SEARCH",
            "external_review_acceptance_required": True,
        },
        "environment": {
            "exact_capture": _root_identity("history/internal_docs/goal5793_x1_exact_environment_capture_20260822.json"),
            "capsule": _root_identity("history/internal_docs/goal5793_x1_exact_environment_capsule_20260822.tar.gz"),
            "capsule_manifest": _root_identity("history/internal_docs/goal5793_x1_exact_environment_capsule_manifest_20260822.json"),
            "capsule_audit": _root_identity("history/internal_docs/goal5793_x1_exact_environment_capsule_audit_20260822.json"),
            "payload_count": 4239, "payload_bytes": 886521284,
            "payload_set_sha256": "0eeaf48fb8a6c49267568007fda3e57205464dca8a12dd350cde8950fd121c6a",
            "archive_sha256": "90ff09e084c4b9e9ba0262dfe9dc2ef028b2777b98ce4c16a5a8f4e3b1fe41d9",
            "gpu_marker_hit_count": 0, "wsl_used": False, "ssh_transport_used": True,
        },
        "documents": {
            "report": {"path": f"history/internal_docs/{REPORT_NAME}", **_bytes_identity(report)},
            "self_review": {"path": f"history/internal_docs/{SELF_REVIEW_NAME}", **_bytes_identity(self_review)},
            "single_cfr": {"path": f"history/internal_docs/{CFR_NAME}", **_bytes_identity(cfr)},
            "only_external_delivery_filename": PACKET_NAME,
        },
        "tool_and_test_surface": {
            "count": len(tool_rows), "rows": tool_rows,
            "rows_sha256": _sha256_bytes(canonical_json_bytes(tool_rows)),
        },
        "claim_boundary": {
            "prospective_generality_exam_count": 0, "usability_evidence_count": 0,
            "soundness_or_completeness_proven": False, "false_rejection_rate_proven": False,
            "third_geometry_family_proven": False, "all_paths_gated_proven": False,
            "easy_productive_or_better_than_cuda_optix_proven": False,
            "performance_or_production_result": False, "x1_complete": False, "x2_authorized": False,
        },
        "authorization": {
            "external_reviewer_contact_by_builder": False, "x2_offline_implementation": False,
            "live_search_or_provider_call": False, "entropy_anchor_or_draw": False,
            "candidate_selection": False, "candidate_implementation_or_execution": False,
            "gpu_home_pod_or_ssh": False, "registered_or_performance_timing": False,
            "product_src_native_family_role_opcode_rule_facade_change": False,
            "public_release_publication_or_submission": False,
        },
        "required_next_action": "SEND_EXACTLY_ONE_X1_EXTERNAL_REVIEW_ARCHIVE__AWAIT_RETURNED_REVIEW__THEN_APPEND_ONLY_OWNER_ABSORPTION_OR_REMAIN_BLOCKED",
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(
        result, seal_field="result_sha256", domain="rtdl.goal5793.x1.external_review_result", version=1,
    )
    return {
        OWNER_NAME: owner_bytes,
        RESULT_NAME: canonical_json_bytes(result) + b"\n",
        REPORT_NAME: report,
        SELF_REVIEW_NAME: self_review,
        CFR_NAME: cfr,
    }


def _add_path(archive: tarfile.TarFile, name: str, path: Path) -> None:
    info = tarfile.TarInfo(name)
    info.size = path.stat().st_size
    info.mode = 0o444
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    with path.open("rb") as handle:
        archive.addfile(info, handle)


def _add_bytes(archive: tarfile.TarFile, name: str, payload: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    info.mode = 0o444
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    archive.addfile(info, io.BytesIO(payload))


def _payloads(documents: dict[str, bytes]) -> tuple[list[dict[str, Any]], dict[str, tuple[Path | None, bytes | None]]]:
    records: list[dict[str, Any]] = []
    sources: dict[str, tuple[Path | None, bytes | None]] = {}

    def add_path(name: str, relative: str, role: str) -> None:
        _safe_name(name)
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise FinalizeError(f"packet_source_absent_or_nonregular:{relative}")
        records.append({"path": name, "role": role, **_identity(path)})
        sources[name] = (path, None)

    def add_bytes(name: str, payload: bytes, role: str) -> None:
        _safe_name(name)
        records.append({"path": name, "role": role, **_bytes_identity(payload)})
        sources[name] = (None, payload)

    for name, relative, role in FIXED_EVIDENCE:
        add_path(name, relative, role)
    for path in sorted(list((ROOT / "scripts").glob("goal5793_x1*.py")), key=lambda p: p.name.encode("utf-8")):
        add_path(f"tools/{path.name}", path.relative_to(ROOT).as_posix(), "X1_TOOL")
    for path in sorted(list((ROOT / "tests").glob("goal5793_x1*_test.py")), key=lambda p: p.name.encode("utf-8")):
        add_path(f"tests/{path.name}", path.relative_to(ROOT).as_posix(), "X1_TEST")
    for name, payload in documents.items():
        archive_name = f"ENTRYPOINT/{name}" if name == CFR_NAME else f"documents/{name}"
        add_bytes(archive_name, payload, "SOLE_CFR_ENTRYPOINT" if name == CFR_NAME else "X1_DOCUMENT")
    records.sort(key=lambda row: row["path"].encode("utf-8"))
    if len(records) != len({row["path"] for row in records}):
        raise FinalizeError("packet_duplicate_member")
    return records, sources


def _manifest(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], bytes]:
    projection = [{"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]} for row in rows]
    value: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.external_review_single_file_manifest.v1",
        "date": DATE,
        "status": "SINGLE_SELF_CONTAINED_X1_EXTERNAL_REVIEW_DELIVERY__NO_SCIENTIFIC_ACTION_AUTHORIZATION",
        "sole_entrypoint": f"ENTRYPOINT/{CFR_NAME}",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "payload_set_sha256": _sha256_bytes(canonical_json_bytes(projection)),
        "rows": rows,
        "claim_boundary": {"prospective_generality_exam_count": 0, "usability_evidence_count": 0, "x1_complete": False},
        "authorization": {"x2": False, "search": False, "entropy": False, "selection": False,
                          "candidate_work": False, "gpu": False, "timing": False, "publication_submission": False},
        "manifest_sha256": "",
    }
    value["manifest_sha256"] = seal_document(
        value, seal_field="manifest_sha256", domain="rtdl.goal5793.x1.external_review_single_file_manifest", version=1,
    )
    return value, canonical_json_bytes(value) + b"\n"


def _write_archive(path: Path, rows: list[dict[str, Any]], sources: dict[str, tuple[Path | None, bytes | None]], manifest_bytes: bytes) -> None:
    with path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT) as archive:
                for row in rows:
                    source_path, payload = sources[row["path"]]
                    if source_path is not None:
                        _add_path(archive, row["path"], source_path)
                    else:
                        _add_bytes(archive, row["path"], payload or b"")
                _add_bytes(archive, EMBEDDED_MANIFEST, manifest_bytes)


def build(output_root: Path) -> dict[str, Any]:
    documents = _documents()
    rows, sources = _payloads(documents)
    manifest, manifest_bytes = _manifest(rows)
    output_root.mkdir(parents=True, exist_ok=True)
    outputs = [output_root / name for name in (
        PACKET_NAME, TWIN_NAME, MANIFEST_NAME, AUDIT_NAME,
        OWNER_NAME, RESULT_NAME, REPORT_NAME, SELF_REVIEW_NAME, CFR_NAME,
    )]
    if any(path.exists() or path.is_symlink() for path in outputs):
        raise FinalizeError("create_only_output_exists")
    packet_path, twin_path = output_root / PACKET_NAME, output_root / TWIN_NAME
    _write_archive(packet_path, rows, sources, manifest_bytes)
    _write_archive(twin_path, rows, sources, manifest_bytes)
    if _identity(packet_path) != _identity(twin_path):
        raise FinalizeError("independent_packet_rebuild_not_byte_identical")
    (output_root / MANIFEST_NAME).write_bytes(manifest_bytes)
    for name, payload in documents.items():
        (output_root / name).write_bytes(payload)
    audit: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.external_review_single_file_audit.v1",
        "status": "PACKET_AND_TWIN_BYTE_IDENTICAL__EXTERNAL_REVIEW_PENDING__NO_X2_AUTHORIZATION",
        "packet": {"path": PACKET_NAME, **_identity(packet_path)},
        "twin": {"path": TWIN_NAME, **_identity(twin_path)},
        "manifest": {"path": MANIFEST_NAME, **_identity(output_root / MANIFEST_NAME), "manifest_sha256": manifest["manifest_sha256"]},
        "payload_count": manifest["payload_count"], "payload_bytes": manifest["payload_bytes"],
        "payload_set_sha256": manifest["payload_set_sha256"],
        "sole_external_delivery": PACKET_NAME,
        "authorization": manifest["authorization"],
        "audit_sha256": "",
    }
    audit["audit_sha256"] = seal_document(
        audit, seal_field="audit_sha256", domain="rtdl.goal5793.x1.external_review_single_file_audit", version=1,
    )
    (output_root / AUDIT_NAME).write_bytes(canonical_json_bytes(audit) + b"\n")
    return audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    if args.write_create_only:
        audit = build(HISTORY)
        print(json.dumps(audit, sort_keys=True))
    else:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_review_dry_") as raw:
            audit = build(Path(raw))
            print("DRY_RUN_NO_HISTORY_WRITE", json.dumps(audit, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
