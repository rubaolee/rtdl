"""Append-only correction: the sole X1 review delivery is one CFR Markdown file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DATE = "2026-08-22"
CFR_NAME = "call_for_review_goal5793_x1_generic_examiner_exposure_and_environment_single_cfr_20260822.md"
RESULT_NAME = "goal5793_x1_external_review_result_v2_single_cfr_20260822.json"
REPORT_NAME = "goal5793_x1_external_review_technical_report_v2_single_cfr_20260822.md"
SELF_NAME = "self_review_goal5793_x1_external_review_v2_single_cfr_20260822.md"
CORRECTION_NAME = "goal5793_x1_single_cfr_delivery_correction_20260822.json"
OLD_PACKET = "history/internal_docs/goal5793_x1_external_review_single_file_20260822.tar.gz"
OLD_CFR = "history/internal_docs/call_for_review_goal5793_x1_generic_examiner_environment_and_exposure_boundary_20260822.md"

MATERIALS: list[tuple[str, str]] = [
    ("controlling S0 closure", "history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json"),
    ("S0 returned review", "history/internal_docs/review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md"),
    ("S0 reproduction capsule", "history/internal_docs/goal5793_x1_s0_reproduction_capsule_20260822.tar.gz"),
    ("S0 reproduction manifest", "history/internal_docs/goal5793_x1_s0_reproduction_capsule_manifest_20260822.json"),
    ("S0 reproduction audit", "history/internal_docs/goal5793_x1_s0_reproduction_capsule_audit_20260822.json"),
    ("survey 186-entry registry", "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json"),
    ("declared successor exposure authority", "history/internal_docs/goal5793_x1_declared_project_exposure_registry_blocker_20260822.json"),
    ("no-memory-attestation boundary", "history/internal_docs/goal5793_x1_no_owner_memory_attestation_boundary_20260822.json"),
    ("positive-vector freeze", "history/internal_docs/goal5793_x1_positive_vector_freeze_20260822.json"),
    ("historical registry authority", "history/internal_docs/goal5793_x1_historical_registry_authority_20260822.json"),
    ("historical registry stage pin", "history/internal_docs/goal5793_x1_historical_registry_stage_pin_20260822.json"),
    ("historical registry fixtures", "history/internal_docs/goal5793_x1_historical_registry_fixtures_20260822.json"),
    ("fresh-process receipt", "history/internal_docs/goal5793_x1_historical_fresh_process_exam_receipt_20260822.json"),
    ("exact environment request", "history/internal_docs/goal5793_x1_exact_environment_capture_request_20260822.json"),
    ("exact environment authority", "history/internal_docs/goal5793_x1_exact_environment_capture_20260822.json"),
    ("exact environment capsule", "history/internal_docs/goal5793_x1_exact_environment_capsule_20260822.tar.gz"),
    ("exact environment manifest", "history/internal_docs/goal5793_x1_exact_environment_capsule_manifest_20260822.json"),
    ("exact environment audit", "history/internal_docs/goal5793_x1_exact_environment_capsule_audit_20260822.json"),
    ("native trace authority", "history/internal_docs/goal5793_x1_native_trace_authority_20260822.json"),
    ("owner local-Linux directive record", "history/internal_docs/goal5793_x1_owner_local_linux_directive_record_20260822.json"),
    ("local reproducibility packet; DO NOT SEND", OLD_PACKET),
    ("local reproducibility packet manifest", "history/internal_docs/goal5793_x1_external_review_single_file_manifest_20260822.json"),
    ("local reproducibility packet audit", "history/internal_docs/goal5793_x1_external_review_single_file_audit_20260822.json"),
]


class CorrectionError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        raise CorrectionError(f"material_absent_or_nonregular:{relative}")
    return {"path": relative, "bytes": path.stat().st_size, "sha256": _sha256(path)}


def _bytes_identity(path: str, payload: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def _material_rows() -> list[dict[str, object]]:
    rows = [{"role": role, **_identity(path)} for role, path in MATERIALS]
    survey = ROOT / "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar"
    if survey.stat().st_size != 752766 or _sha256(survey) != "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857":
        raise CorrectionError("pinned_survey_source_identity_mismatch")
    rows.append({
        "role": "pinned survey source archive",
        "path": "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar",
        "bytes": 752766,
        "sha256": "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857",
    })
    return rows


def _materials_markdown(rows: list[dict[str, object]]) -> str:
    lines = ["| Role | Local path | Bytes | SHA-256 |", "|---|---|---:|---|"]
    for row in rows:
        lines.append(f"| {row['role']} | `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    return "\n".join(lines)


def build_documents() -> dict[str, bytes]:
    rows = _material_rows()
    table = _materials_markdown(rows)
    report = f"""# Goal5793 X1 technical report v2: single-CFR delivery correction

## Controlling correction

The sole file sent to the reviewer is `{CFR_NAME}`. All archives, manifests, audits, results, reports, tools and tests remain at their listed local paths. The previously generated `{OLD_PACKET.split('/')[-1]}` is retained only as local reproducibility evidence and **must not be sent**.

The science is unchanged: X1 freezes the candidate-agnostic examiner, registry derivation, conservative exposure boundary and exact Linux environment. Prospective Goal5793 generalization exams remain 0 and usability evidence remains 0. X1 is not closed; X2, search, entropy, selection, candidate implementation/execution, GPU use and timing remain unauthorized.

This successor corrects delivery topology only. It does not rewrite or delete prior bytes.
""".encode("utf-8")
    self_review = f"""# Self-review: Goal5793 X1 v2 single-CFR delivery

The earlier local result incorrectly named a tar.gz as the external delivery. That interpretation violated the owner's explicit requirement that the reviewer receive one CFR file. This successor fixes the controlling delivery instruction: send only `{CFR_NAME}`. The tar.gz, twin, manifests and audits remain local supporting evidence.

No scientific claim, count, authorization or evidence byte is upgraded. Generalization exams = 0; usability evidence = 0.
""".encode("utf-8")
    cfr = f"""# Call for review: Goal5793 X1 examiner, exposure boundary, and exact environment

**SEND ONLY THIS CFR FILE TO THE REVIEWER.** Do not send a packet, archive, manifest, audit, twin, result, report, or second attachment. All supporting materials are already prepared at the exact local paths below.

## One ruling requested

Does exact X1 freeze a candidate-agnostic examiner and externally pinned registry path, preserve the pinned 186-entry survey exposure component plus the declared successor repository/Git/S0-DAG observation, honestly replace unavailable memory/historical-untracked attestation with a no-unseen-claim and terminate-without-replacement boundary, and freeze an exact Linux execution environment—such that X1 may be accepted and X2 offline implementation only may be considered after append-only owner absorption, while live search, entropy, selection, candidate implementation/execution, GPU use and timing remain forbidden?

Return one file named `review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md`. Required fields: P0/P1/P2/P3; X1 accepted yes/no; conservative no-memory-attestation boundary accepted yes/no; owner-directed SSH-to-local-Linux successor scope accepted yes/no; and whether X2 offline implementation only may be considered after owner closure. Any P0 or P1 keeps X1 blocked.

## Controlling local documents

- Result: `history/internal_docs/{RESULT_NAME}` — independently recompute its `result_sha256`.
- Technical report: `history/internal_docs/{REPORT_NAME}`.
- Self-review: `history/internal_docs/{SELF_NAME}`.
- Delivery correction: `history/internal_docs/{CORRECTION_NAME}` — independently recompute its `correction_sha256`.

## Exact supporting-material paths

{table}

## Required checks

1. Run `python -m scripts.goal5793_x1_verify_external_review_packet` against the local reproducibility packet and its local twin/manifest/audit. The packet is evidence only; do not request or return it as an attachment.
2. Run `python -m unittest discover -s tests -p 'goal5793_x1*_test.py'`; expected current result is 150/150 PASS with one Windows symlink-capability skip whose Linux integration branch passed.
3. Verify 35 declaration rules have exact product/independent parity; SP022 is unreachable fallback; SP063/SP070/SP071 are authority-only. Reject a generic 39/39 claim.
4. Verify the frozen historical inventory is 6 COMPATIBLE / 9 UNKNOWN / 0 INCOMPATIBLE, seven positive provenances and four structural vectors. These are historical regression, not prospective generalization evidence.
5. Verify the environment capsule: 4,239 payloads, 886,521,284 payload bytes, set `0eeaf48fb8a6c49267568007fda3e57205464dca8a12dd350cde8950fd121c6a`, archive `90ff09e084c4b9e9ba0262dfe9dc2ef028b2777b98ce4c16a5a8f4e3b1fe41d9`; confirm 0 GPU markers and no WSL.
6. Verify all 186 survey bibliography entries remain selection-ineligible and the pinned survey archive is 752,766 bytes / `bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857`.
7. Confirm the 246,627,536-byte successor exposure authority is not called an S0 snapshot or complete mental exposure. Decide whether the exact conservative rule is adequate: no unseen/blind/held-out claim; registry nonmatch only; later pre-X1 exposure discovery terminates the entire single expansion with no replacement, reuse or second search.
8. Confirm the owner explicitly directed local Linux `192.168.1.20`, prohibited WSL, and SSH was used only for non-GPU X1 environment materialization. Explicitly rule on that successor scope because the earlier S0 closure had said no SSH.
9. Confirm prospective generalization exams = 0 and usability evidence = 0 everywhere. No packaging or historical replay may be counted as either.

## Non-authorization

Acceptance is an instrument-freeze decision, not generalization or usability evidence. After returned review and owner closure, X2 may at most implement offline harvester/taxonomy/enumerator/NIST-verifier/selection-client tooling with synthetic fixtures. It may not execute live search, contact providers, draw entropy, select candidates, implement/run candidates, use GPU/POD/SSH, register timing, publish or submit.
""".encode("utf-8")

    prior = _identity(OLD_CFR)
    prior_packet = _identity(OLD_PACKET)
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.external_review_result.v2",
        "date": DATE,
        "status": "X1_READY_FOR_SINGLE_CFR_EXTERNAL_REVIEW__NOT_CLOSED__ALL_SUCCESSOR_SCIENCE_BLOCKED",
        "supersedes_delivery_instruction_only": _identity("history/internal_docs/goal5793_x1_external_review_result_20260822.json"),
        "documents": {
            "single_cfr": _bytes_identity(f"history/internal_docs/{CFR_NAME}", cfr),
            "report": _bytes_identity(f"history/internal_docs/{REPORT_NAME}", report),
            "self_review": _bytes_identity(f"history/internal_docs/{SELF_NAME}", self_review),
        },
        "supporting_materials": rows,
        "delivery": {
            "only_file_to_send": CFR_NAME,
            "previous_packet_is_local_evidence_only": True,
            "previous_packet_must_not_be_sent": True,
            "separate_attachment_count": 0,
        },
        "claim_boundary": {
            "prospective_generality_exam_count": 0, "usability_evidence_count": 0,
            "x1_complete": False, "x2_authorized": False,
            "soundness_completeness_false_rejection_rate_or_third_family_proven": False,
            "easy_productive_or_better_than_cuda_optix_proven": False,
        },
        "authorization": {
            "external_contact_by_builder": False, "x2": False, "live_search": False,
            "entropy": False, "selection": False, "candidate_work": False,
            "gpu_home_pod_ssh": False, "timing": False, "publication_submission": False,
        },
        "required_next_action": "SEND_ONLY_EXACT_SINGLE_CFR__AWAIT_RETURNED_REVIEW__THEN_APPEND_ONLY_OWNER_ABSORPTION_OR_REMAIN_BLOCKED",
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(
        result, seal_field="result_sha256", domain="rtdl.goal5793.x1.external_review_result", version=2,
    )
    result_bytes = canonical_json_bytes(result) + b"\n"
    correction: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.single_cfr_delivery_correction.v1",
        "date": DATE,
        "status": "APPEND_ONLY_DELIVERY_TOPOLOGY_CORRECTION__SCIENCE_AND_AUTHORIZATION_UNCHANGED",
        "incorrect_prior_instruction": {"cfr": prior, "packet": prior_packet, "packet_was_sent": False},
        "controlling_successor": {
            "single_cfr": _bytes_identity(f"history/internal_docs/{CFR_NAME}", cfr),
            "result": _bytes_identity(f"history/internal_docs/{RESULT_NAME}", result_bytes),
            "report": _bytes_identity(f"history/internal_docs/{REPORT_NAME}", report),
            "self_review": _bytes_identity(f"history/internal_docs/{SELF_NAME}", self_review),
            "only_single_cfr_may_be_sent": True,
            "all_other_files_are_local_paths_only": True,
        },
        "claim_or_authorization_changed": False,
        "authorization": {"packet_delivery": False, "second_attachment": False, "x2": False,
                          "search_entropy_selection_candidate_gpu_timing_publication": False},
        "correction_sha256": "",
    }
    correction["correction_sha256"] = seal_document(
        correction, seal_field="correction_sha256", domain="rtdl.goal5793.x1.single_cfr_delivery_correction", version=1,
    )
    return {
        CFR_NAME: cfr,
        REPORT_NAME: report,
        SELF_NAME: self_review,
        RESULT_NAME: result_bytes,
        CORRECTION_NAME: canonical_json_bytes(correction) + b"\n",
    }


def write_create_only(output_root: Path) -> dict[str, dict[str, object]]:
    documents = build_documents()
    outputs = {name: output_root / name for name in documents}
    if any(path.exists() or path.is_symlink() for path in outputs.values()):
        raise CorrectionError("create_only_output_exists")
    output_root.mkdir(parents=True, exist_ok=True)
    for name, payload in documents.items():
        with outputs[name].open("xb") as handle:
            handle.write(payload)
    return {name: _identity(str(path.relative_to(ROOT))) if ROOT in path.parents else
            {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}
            for name, path in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    if args.write_create_only:
        print(json.dumps(write_create_only(HISTORY), sort_keys=True))
    else:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_single_cfr_dry_") as raw:
            print("DRY_RUN_NO_HISTORY_WRITE", json.dumps(write_create_only(Path(raw)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
