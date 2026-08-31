"""Independent verifier for the single-file Goal5793 X1 review delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any
import zlib

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


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
GZIP_HEADER = bytes.fromhex("1f8b08000000000002ff")
EXPECTED_DOCUMENTS = {
    f"documents/{REPORT_NAME}": (4875, "31dc5404fa18cdfcf11f25e59333cc3a218e7b1e3b32849d4106f76dacafbf2f"),
    f"documents/{SELF_REVIEW_NAME}": (1063, "842ec89f2f7407a4f4cd8282b20c9d023f2adc25af7131b034308b744aba5766"),
    f"ENTRYPOINT/{CFR_NAME}": (4563, "d28f7dbc8882daa3329830cb3447ef3bbb4fb921aabede2aaeacb5e7e075bce6"),
    f"documents/{OWNER_NAME}": (1338, "e5761628d84a72bded1647be9cc616a6eda65b54e11eadfa6423c9f105c31969"),
}
REQUIRED_PAYLOADS = {
    "evidence/s0/reproduction_capsule.tar.gz",
    "evidence/s0/returned_review.md",
    "evidence/s0/owner_closure.json",
    "evidence/exposure/survey_registry_v2.json",
    "evidence/exposure/declared_successor_registry_blocker.json",
    "evidence/exposure/no_memory_attestation_boundary.json",
    "evidence/exposure/pinned_survey_source.tar",
    "evidence/mechanism/positive_vector_freeze.json",
    "evidence/mechanism/historical_registry_authority.json",
    "evidence/mechanism/historical_fresh_process_receipt.json",
    "evidence/environment/exact_capture.json",
    "evidence/environment/exact_capsule.tar.gz",
    "evidence/environment/exact_capsule_manifest.json",
    "evidence/environment/exact_capsule_audit.json",
    "tools/goal5793_x1_generic_examiner.py",
    "tools/goal5793_x1_registry_derivation.py",
    "tools/goal5793_x1_run_generic_examiner.py",
    "tools/goal5793_x1_verify_exact_environment_capsule.py",
    "tools/goal5793_x1_verify_external_review_packet.py",
}


class VerificationError(ValueError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise VerificationError(reason)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _safe_name(name: str) -> bool:
    return bool(name) and "\\" not in name and all(part not in ("", ".", "..") for part in name.split("/"))


def _single_canonical_gzip(path: Path) -> None:
    with path.open("rb") as handle:
        _require(handle.read(10) == GZIP_HEADER, "PACKET_GZIP_HEADER_MISMATCH")
        handle.seek(0)
        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            inflater.decompress(chunk)
            _require(not inflater.unused_data, "PACKET_GZIP_TRAILING_OR_CONCATENATED_STREAM")
        inflater.flush()
        _require(inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail, "PACKET_GZIP_INCOMPLETE")


def _payload_set_digest(rows: list[dict[str, Any]]) -> str:
    projection = [{"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]} for row in rows]
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def _verify_result(payload: bytes, retained: dict[str, bytes]) -> dict[str, Any]:
    result = json.loads(payload)
    _require(payload == canonical_json_bytes(result) + b"\n", "RESULT_NOT_CANONICAL")
    _require(result.get("schema") == "rtdl.goal5793.x1.external_review_result.v1", "RESULT_SCHEMA_MISMATCH")
    expected_seal = seal_document(
        result, seal_field="result_sha256", domain="rtdl.goal5793.x1.external_review_result", version=1,
    )
    _require(result.get("result_sha256") == expected_seal, "RESULT_SEAL_MISMATCH")
    _require(result.get("status") == "X1_FROZEN_READY_FOR_SINGLE_FILE_EXTERNAL_REVIEW__NOT_CLOSED__X2_AND_ALL_SCIENTIFIC_ACTIONS_BLOCKED", "RESULT_STATUS_OVERREACH")
    _require(result.get("claim_boundary") == {
        "all_paths_gated_proven": False, "easy_productive_or_better_than_cuda_optix_proven": False,
        "false_rejection_rate_proven": False, "performance_or_production_result": False,
        "prospective_generality_exam_count": 0, "soundness_or_completeness_proven": False,
        "third_geometry_family_proven": False, "usability_evidence_count": 0,
        "x1_complete": False, "x2_authorized": False,
    }, "RESULT_CLAIM_BOUNDARY_OVERREACH")
    _require(result.get("authorization") == {
        "candidate_implementation_or_execution": False, "candidate_selection": False,
        "entropy_anchor_or_draw": False, "external_reviewer_contact_by_builder": False,
        "gpu_home_pod_or_ssh": False, "live_search_or_provider_call": False,
        "product_src_native_family_role_opcode_rule_facade_change": False,
        "public_release_publication_or_submission": False,
        "registered_or_performance_timing": False, "x2_offline_implementation": False,
    }, "RESULT_AUTHORIZATION_ESCALATION")
    mechanism = result.get("mechanism", {})
    _require(mechanism.get("declaration_rules_executed_with_product_recount_parity") == 35, "RESULT_RULE_COUNT_MISMATCH")
    _require(mechanism.get("closed_policy_unreachable_fallback_rule_ids") == ["SP022"], "RESULT_SP022_MISMATCH")
    _require(mechanism.get("authority_only_rule_ids") == ["SP063", "SP070", "SP071"], "RESULT_AUTHORITY_RULE_MISMATCH")
    _require(mechanism.get("historical_inventory") == {"compatible": 6, "incompatible": 0, "unknown": 9}, "RESULT_INVENTORY_MISMATCH")
    exposure = result.get("exposure_boundary", {})
    _require(exposure.get("survey_bibliography_entry_count") == 186 and exposure.get("survey_entries_selection_eligible") == 0, "RESULT_EXPOSURE_COUNT_MISMATCH")
    _require(exposure.get("unseen_blind_held_out_or_complete_mental_exposure_claimed") is False, "RESULT_EXPOSURE_OVERCLAIM")
    _require(exposure.get("later_pre_x1_exposure_discovery_action") == "TERMINATE_SINGLE_EXPANSION__NO_REPLACEMENT_REUSE_OR_SECOND_SEARCH", "RESULT_EXPOSURE_RESCUE_GAP")
    environment = result.get("environment", {})
    _require(environment.get("payload_count") == 4239 and environment.get("payload_bytes") == 886521284, "RESULT_ENVIRONMENT_COUNT_MISMATCH")
    _require(environment.get("gpu_marker_hit_count") == 0 and environment.get("wsl_used") is False and environment.get("ssh_transport_used") is True, "RESULT_TRANSPORT_DISCLOSURE_MISMATCH")
    documents = result.get("documents", {})
    mapping = {
        "report": f"documents/{REPORT_NAME}", "self_review": f"documents/{SELF_REVIEW_NAME}",
        "single_cfr": f"ENTRYPOINT/{CFR_NAME}",
    }
    for role, name in mapping.items():
        expected = {"path": f"history/internal_docs/{name.split('/', 1)[1]}", "bytes": len(retained[name]), "sha256": hashlib.sha256(retained[name]).hexdigest()}
        _require(documents.get(role) == expected, f"RESULT_DOCUMENT_CROSSBIND_MISMATCH:{role}")
    owner_name = f"documents/{OWNER_NAME}"
    owner_expected = {"path": f"history/internal_docs/{OWNER_NAME}", "bytes": len(retained[owner_name]), "sha256": hashlib.sha256(retained[owner_name]).hexdigest(),
                      "record_sha256": json.loads(retained[owner_name])["record_sha256"]}
    _require(result.get("owner_local_linux_directive") == owner_expected, "RESULT_OWNER_DIRECTIVE_CROSSBIND_MISMATCH")
    return result


def _verify_owner(payload: bytes) -> None:
    value = json.loads(payload)
    _require(payload == canonical_json_bytes(value) + b"\n", "OWNER_RECORD_NOT_CANONICAL")
    _require(value.get("schema") == "rtdl.goal5793.x1.owner_local_linux_directive_record.v1", "OWNER_RECORD_SCHEMA_MISMATCH")
    expected = seal_document(value, seal_field="record_sha256", domain="rtdl.goal5793.x1.owner_local_linux_directive_record", version=1)
    _require(value.get("record_sha256") == expected, "OWNER_RECORD_SEAL_MISMATCH")
    _require(value.get("verbatim_owner_messages") == [
        "继续前进直至GOAL完成！",
        "你不要降智! 这些事情根本不需要回复和授权。去做！每当你让我事情的话，自己反愚蠢三问先！",
        "去翻历史记录，找到本地的linux", "别用WSL", "192.168.1.20",
    ], "OWNER_RECORD_TRANSCRIPTION_MISMATCH")
    interpretation = value.get("implemented_interpretation", {})
    _require(interpretation.get("host") == "192.168.1.20" and interpretation.get("gpu_device_or_driver_api_call_count") == 0, "OWNER_RECORD_SCOPE_MISMATCH")
    _require(not any(value.get("authorization", {}).values()), "OWNER_RECORD_AUTHORIZATION_ESCALATION")


def verify(*, packet_path: Path, twin_path: Path | None = None, manifest_path: Path | None = None, audit_path: Path | None = None) -> dict[str, Any]:
    _require(packet_path.is_file() and not packet_path.is_symlink(), "PACKET_NOT_REGULAR")
    _single_canonical_gzip(packet_path)
    packet_identity = _identity(packet_path)
    if twin_path is not None:
        _require(twin_path.is_file() and not twin_path.is_symlink() and _identity(twin_path) == packet_identity, "PACKET_TWIN_MISMATCH")
        _single_canonical_gzip(twin_path)

    retained: dict[str, bytes] = {}
    observed: list[dict[str, Any]] = []
    embedded_manifest: bytes | None = None
    wanted = set(EXPECTED_DOCUMENTS) | {f"documents/{RESULT_NAME}"}
    with tarfile.open(packet_path, mode="r:gz") as archive:
        _require(not archive.pax_headers, "PACKET_GLOBAL_PAX_FORBIDDEN")
        members = archive.getmembers()
        _require(len({member.name for member in members}) == len(members), "PACKET_DUPLICATE_MEMBER")
        for member in members:
            _require(member.isfile(), f"PACKET_NONREGULAR_MEMBER:{member.name}")
            _require(_safe_name(member.name), f"PACKET_UNSAFE_MEMBER:{member.name}")
            _require((member.mode, member.uid, member.gid, member.mtime) == (0o444, 0, 0, 0), f"PACKET_METADATA_MISMATCH:{member.name}")
            _require((member.uname, member.gname) == ("", "") and not member.pax_headers, f"PACKET_PAX_OR_NAME_METADATA_MISMATCH:{member.name}")
            handle = archive.extractfile(member)
            _require(handle is not None, f"PACKET_MEMBER_UNREADABLE:{member.name}")
            digest = hashlib.sha256()
            count = 0
            body = bytearray() if member.name in wanted or member.name == EMBEDDED_MANIFEST else None
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                count += len(chunk)
                if body is not None:
                    body.extend(chunk)
            if member.name == EMBEDDED_MANIFEST:
                embedded_manifest = bytes(body or b"")
            else:
                observed.append({"path": member.name, "bytes": count, "sha256": digest.hexdigest()})
                if body is not None:
                    retained[member.name] = bytes(body)
    _require(embedded_manifest is not None, "PACKET_EMBEDDED_MANIFEST_ABSENT")
    manifest = json.loads(embedded_manifest)
    _require(embedded_manifest == canonical_json_bytes(manifest) + b"\n", "PACKET_MANIFEST_NOT_CANONICAL")
    _require(manifest.get("schema") == "rtdl.goal5793.x1.external_review_single_file_manifest.v1", "PACKET_MANIFEST_SCHEMA_MISMATCH")
    expected_manifest_seal = seal_document(manifest, seal_field="manifest_sha256", domain="rtdl.goal5793.x1.external_review_single_file_manifest", version=1)
    _require(manifest.get("manifest_sha256") == expected_manifest_seal, "PACKET_MANIFEST_SEAL_MISMATCH")
    rows = manifest.get("rows")
    _require(isinstance(rows, list) and all(isinstance(row, dict) and set(row) == {"path", "role", "bytes", "sha256"} for row in rows), "PACKET_MANIFEST_ROW_SCHEMA_MISMATCH")
    names = [row["path"] for row in rows]
    _require(names == sorted(names, key=lambda value: value.encode("utf-8")), "PACKET_MANIFEST_NOT_SORTED")
    _require([row["path"] for row in observed] == names, "PACKET_MEMBER_ORDER_OR_SET_MISMATCH")
    for row, actual in zip(rows, observed):
        _require({key: row[key] for key in ("path", "bytes", "sha256")} == actual, f"PACKET_PAYLOAD_IDENTITY_MISMATCH:{row['path']}")
    _require(manifest.get("payload_count") == len(rows) and manifest.get("payload_bytes") == sum(row["bytes"] for row in rows), "PACKET_PAYLOAD_SUMMARY_MISMATCH")
    _require(manifest.get("payload_set_sha256") == _payload_set_digest(rows), "PACKET_PAYLOAD_SET_MISMATCH")
    _require(manifest.get("sole_entrypoint") == f"ENTRYPOINT/{CFR_NAME}", "PACKET_ENTRYPOINT_MISMATCH")
    _require(REQUIRED_PAYLOADS.issubset(set(names)), "PACKET_REQUIRED_PAYLOAD_MISSING")
    _require(manifest.get("claim_boundary") == {"prospective_generality_exam_count": 0, "usability_evidence_count": 0, "x1_complete": False}, "PACKET_MANIFEST_CLAIM_OVERREACH")
    _require(not any(manifest.get("authorization", {}).values()), "PACKET_MANIFEST_AUTHORIZATION_ESCALATION")
    for name, (expected_bytes, expected_sha) in EXPECTED_DOCUMENTS.items():
        _require(len(retained[name]) == expected_bytes and hashlib.sha256(retained[name]).hexdigest() == expected_sha, f"PACKET_DOCUMENT_DRIFT:{name}")
    _verify_owner(retained[f"documents/{OWNER_NAME}"])
    result = _verify_result(retained[f"documents/{RESULT_NAME}"], retained)
    cfr = retained[f"ENTRYPOINT/{CFR_NAME}"].decode("utf-8")
    _require(cfr.count("SEND ONLY THE ENCLOSING") == 1 and cfr.count(PACKET_NAME) >= 1, "PACKET_SINGLE_FILE_INSTRUCTION_MISMATCH")
    _require("zero prospective Goal5793 exams" in retained[f"documents/{REPORT_NAME}"].decode("utf-8"), "PACKET_REPORT_GENERALITY_BOUNDARY_MISSING")

    if manifest_path is not None:
        _require(manifest_path.read_bytes() == embedded_manifest, "PACKET_EXTERNAL_MANIFEST_MISMATCH")
    if audit_path is not None:
        audit_payload = audit_path.read_bytes()
        audit = json.loads(audit_payload)
        _require(audit_payload == canonical_json_bytes(audit) + b"\n", "PACKET_AUDIT_NOT_CANONICAL")
        expected_audit_seal = seal_document(audit, seal_field="audit_sha256", domain="rtdl.goal5793.x1.external_review_single_file_audit", version=1)
        _require(audit.get("audit_sha256") == expected_audit_seal, "PACKET_AUDIT_SEAL_MISMATCH")
        _require(audit.get("packet") == {"path": PACKET_NAME, **packet_identity}, "PACKET_AUDIT_PACKET_MISMATCH")
        if twin_path is not None:
            _require(audit.get("twin") == {"path": TWIN_NAME, **packet_identity}, "PACKET_AUDIT_TWIN_MISMATCH")
        _require(audit.get("sole_external_delivery") == PACKET_NAME and not any(audit.get("authorization", {}).values()), "PACKET_AUDIT_SCOPE_ESCALATION")
    return {
        "status": "GOAL5793_X1_SINGLE_FILE_EXTERNAL_REVIEW_PACKET_PASS",
        "packet": packet_identity,
        "payload_count": len(rows), "payload_bytes": manifest["payload_bytes"],
        "payload_set_sha256": manifest["payload_set_sha256"],
        "result_sha256": result["result_sha256"], "manifest_sha256": manifest["manifest_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--twin", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--audit", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(packet_path=args.packet, twin_path=args.twin,
                            manifest_path=args.manifest, audit_path=args.audit), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
