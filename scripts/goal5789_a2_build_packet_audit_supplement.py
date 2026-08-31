"""Append-only supplemental re-audit for Goal5789-A2 packet check reporting.

The externally reviewed v1 packet auditor already rehashed every payload and
recomputed the payload-set digest, but its emitted ``checks`` object did not
name those two checks.  This script independently repeats the fixed packet
audit and emits a create-only receipt that reports them explicitly.  It does
not modify or supersede any reviewed byte and grants no Goal5793 or execution
authority.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5789_a2_callback_ir_authority_binding_review_packet_v1"
ARCHIVE_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
TWIN_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_twin_20260821.tar.gz"
MANIFEST_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_manifest_20260821.json"
AUDIT_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_audit_20260821.json"
REVIEW_REL = "history/internal_docs/review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md"
WORK_REL = "history/internal_docs/goal5789_a2_postreview_absorption_work_authority_20260821.json"
SCRIPT_REL = "scripts/goal5789_a2_build_packet_audit_supplement.py"
OUTPUT_REL = "history/internal_docs/goal5789_a2_postreview_packet_audit_supplement_20260821.json"
OUTPUT = ROOT / OUTPUT_REL

ARCHIVE_SHA256 = "2c2711f1a75bc7571b222f8c7175767ade46ea23f15b9068a9aeef0dba317b25"
ARCHIVE_BYTES = 50_105_014
MANIFEST_SHA256 = "62e4024ec444d26c46bc24abb1f08203735ae75cfeb78cdb388a5136ae7a690a"
MANIFEST_BYTES = 34_211
AUDIT_SHA256 = "42ffc730963c04dffb0f88486f4bc205e488a937e12716a748a13b9732dc42bb"
AUDIT_BYTES = 1_648
AUDIT_INTERNAL_SHA256 = "567133f82948d99c84c8999940d7f9857c16bb8e6653ac899700f69137c21ff3"
REVIEW_SHA256 = "88e0aff9fcc0579c4721a8a3422517beff9146acfcef7862f9dd7e880da1bd3a"
REVIEW_BYTES = 27_657
WORK_SHA256 = "96be56ab7f450664fa2d2c27f3df3e9be667eacf9cc45ee0d45725924520e3a0"
WORK_BYTES = 4_249
WORK_INTERNAL_SHA256 = "d37051d04ff5b3ed99abd11f7469de5fc79bbbac59301ad6fd7b210946961e25"
PAYLOAD_COUNT = 120
PAYLOAD_BYTES = 52_007_905
PAYLOAD_SET_SHA256 = "a94730860617895531f89473cbb367588d2404848b750429f0621f0bb665c487"

EXPECTED_V1_CHECKS = {
    "canonical_metadata": True,
    "delivery_manifest_crossbound": True,
    "embedded_manifest_byte_identical": True,
    "exact_member_set": True,
    "regular_file_only": True,
    "unsafe_member_count": 0,
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


def _safe(relative: str) -> str:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise RuntimeError(f"unsafe packet path: {relative!r}")
    path = PurePosixPath(relative)
    normalized = path.as_posix()
    if (
        path.is_absolute()
        or normalized != relative
        or not path.parts
        or any(part in {"", ".", ".."} or ":" in part for part in path.parts)
    ):
        raise RuntimeError(f"unsafe packet path: {relative!r}")
    return normalized


def _read_fixed(relative: str, expected_bytes: int, expected_sha256: str) -> bytes:
    path = ROOT / Path(*PurePosixPath(_safe(relative)).parts)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"fixed input is absent or non-regular: {relative}")
    data = path.read_bytes()
    if len(data) != expected_bytes or _sha(data) != expected_sha256:
        raise RuntimeError(f"fixed input identity mismatch: {relative}")
    return data


def _object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data)
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise RuntimeError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be an object")
    return value


def _assert_self_seal(value: Mapping[str, Any], field: str, expected: str, label: str) -> None:
    if value.get(field) != expected:
        raise RuntimeError(f"{label} stored seal mismatch")
    body = {key: item for key, item in value.items() if key != field}
    if _sha(_canonical(body)) != expected:
        raise RuntimeError(f"{label} canonical seal mismatch")


def audit(
    *,
    archive_bytes: bytes | None = None,
    twin_bytes: bytes | None = None,
    manifest_bytes: bytes | None = None,
    audit_bytes: bytes | None = None,
) -> dict[str, object]:
    archive = archive_bytes if archive_bytes is not None else _read_fixed(
        ARCHIVE_REL, ARCHIVE_BYTES, ARCHIVE_SHA256
    )
    twin = twin_bytes if twin_bytes is not None else _read_fixed(
        TWIN_REL, ARCHIVE_BYTES, ARCHIVE_SHA256
    )
    manifest_raw = manifest_bytes if manifest_bytes is not None else _read_fixed(
        MANIFEST_REL, MANIFEST_BYTES, MANIFEST_SHA256
    )
    prior_audit_raw = audit_bytes if audit_bytes is not None else _read_fixed(
        AUDIT_REL, AUDIT_BYTES, AUDIT_SHA256
    )
    if (
        len(archive) != ARCHIVE_BYTES
        or _sha(archive) != ARCHIVE_SHA256
        or twin != archive
        or len(manifest_raw) != MANIFEST_BYTES
        or _sha(manifest_raw) != MANIFEST_SHA256
        or len(prior_audit_raw) != AUDIT_BYTES
        or _sha(prior_audit_raw) != AUDIT_SHA256
    ):
        raise RuntimeError("fixed packet, twin, manifest, or audit identity mismatch")

    manifest = _object(manifest_raw, "packet manifest")
    expected_top = {
        "schema",
        "goal",
        "date",
        "status",
        "root_delivery_manifest",
        "payload_count",
        "payload_bytes",
        "payload_set_sha256",
        "payloads",
        "claim_boundary",
        "authorization",
    }
    if set(manifest) != expected_top:
        raise RuntimeError("packet manifest top-level schema mismatch")
    rows = manifest.get("payloads")
    if (
        manifest.get("schema") != "rtdl.goal5789_a2.external_review_packet.v1"
        or manifest.get("payload_count") != PAYLOAD_COUNT
        or manifest.get("payload_bytes") != PAYLOAD_BYTES
        or manifest.get("payload_set_sha256") != PAYLOAD_SET_SHA256
        or not isinstance(rows, list)
        or len(rows) != PAYLOAD_COUNT
    ):
        raise RuntimeError("packet manifest identity or count mismatch")

    expected: dict[str, Mapping[str, Any]] = {}
    digest_rows: list[dict[str, object]] = []
    total = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("packet payload row schema mismatch")
        relative = row.get("path")
        size = row.get("bytes")
        sha256 = row.get("sha256")
        if (
            not isinstance(relative, str)
            or relative in expected
            or type(size) is not int
            or size < 0
            or not isinstance(sha256, str)
            or len(sha256) != 64
            or any(char not in "0123456789abcdef" for char in sha256)
            or not isinstance(row.get("provenance"), str)
            or not row.get("provenance")
        ):
            raise RuntimeError("packet payload row type or uniqueness mismatch")
        _safe(relative)
        expected[relative] = row
        total += size
        digest_rows.append({"path": relative, "bytes": size, "sha256": sha256})
    if [row["path"] for row in rows] != sorted(expected):
        raise RuntimeError("packet payload rows are not sorted")
    recomputed_set = _sha(_canonical(digest_rows))
    if total != PAYLOAD_BYTES or recomputed_set != PAYLOAD_SET_SHA256:
        raise RuntimeError("packet payload-set digest or byte total mismatch")

    seen: dict[str, bytes] = {}
    embedded: bytes | None = None
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as packet:
        members = packet.getmembers()
        if len(members) != PAYLOAD_COUNT + 1:
            raise RuntimeError("packet member count mismatch")
        for member in members:
            if not member.isfile() or member.issym() or member.islnk():
                raise RuntimeError("packet contains a non-regular member")
            if (
                member.mode != 0o444
                or member.uid != 0
                or member.gid != 0
                or member.mtime != 0
                or member.uname != ""
                or member.gname != ""
            ):
                raise RuntimeError("packet member metadata is noncanonical")
            prefix = PREFIX + "/"
            if not member.name.startswith(prefix):
                raise RuntimeError("packet member prefix mismatch")
            relative = member.name[len(prefix) :]
            _safe(relative)
            if relative in seen or relative == "":
                raise RuntimeError("duplicate or empty packet member path")
            handle = packet.extractfile(member)
            if handle is None:
                raise RuntimeError("packet regular member has no payload")
            payload = handle.read()
            if len(payload) != member.size:
                raise RuntimeError("packet member size mismatch")
            if relative == "PACKET_MANIFEST.json":
                embedded = payload
            else:
                seen[relative] = payload
    if embedded != manifest_raw or set(seen) != set(expected):
        raise RuntimeError("embedded manifest or exact member set mismatch")
    mismatch_count = 0
    for relative, row in expected.items():
        payload = seen[relative]
        if len(payload) != row["bytes"] or _sha(payload) != row["sha256"]:
            mismatch_count += 1
    if mismatch_count != 0:
        raise RuntimeError("packet payload identity mismatch")

    prior_audit = _object(prior_audit_raw, "packet audit v1")
    _assert_self_seal(prior_audit, "audit_sha256", AUDIT_INTERNAL_SHA256, "packet audit v1")
    if prior_audit.get("checks") != EXPECTED_V1_CHECKS:
        raise RuntimeError("packet audit v1 checks block drifted")
    _read_fixed(REVIEW_REL, REVIEW_BYTES, REVIEW_SHA256)
    work_raw = _read_fixed(WORK_REL, WORK_BYTES, WORK_SHA256)
    work = _object(work_raw, "postreview work authority")
    _assert_self_seal(work, "work_authority_sha256", WORK_INTERNAL_SHA256, "work authority")

    result: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.postreview_packet_audit_supplement.v1",
        "supplement_sha256": "",
        "goal": "5789-A2-postreview",
        "date": "2026-08-21",
        "status": "PASS__APPEND_ONLY_PACKET_PAYLOAD_IDENTITY_AND_PAYLOAD_SET_CHECKS_EXPLICIT",
        "predecessor_packet": {
            "path": ARCHIVE_REL,
            "bytes": ARCHIVE_BYTES,
            "file_sha256": ARCHIVE_SHA256,
            "payload_count": PAYLOAD_COUNT,
            "payload_bytes": PAYLOAD_BYTES,
        },
        "predecessor_manifest": {
            "path": MANIFEST_REL,
            "bytes": MANIFEST_BYTES,
            "file_sha256": MANIFEST_SHA256,
            "payload_set_sha256": PAYLOAD_SET_SHA256,
        },
        "predecessor_audit": {
            "path": AUDIT_REL,
            "bytes": AUDIT_BYTES,
            "file_sha256": AUDIT_SHA256,
            "audit_sha256": AUDIT_INTERNAL_SHA256,
        },
        "returned_review": {
            "path": REVIEW_REL,
            "bytes": REVIEW_BYTES,
            "file_sha256": REVIEW_SHA256,
            "finding": "P3-1",
        },
        "work_authority": {
            "path": WORK_REL,
            "bytes": WORK_BYTES,
            "file_sha256": WORK_SHA256,
            "work_authority_sha256": WORK_INTERNAL_SHA256,
        },
        "checks": {
            **EXPECTED_V1_CHECKS,
            "payload_identity": True,
            "payload_set_digest": True,
        },
        "payload_identity_checked_count": PAYLOAD_COUNT,
        "payload_identity_mismatch_count": mismatch_count,
        "payload_bytes": total,
        "payload_set_digest_declared": PAYLOAD_SET_SHA256,
        "payload_set_digest_recomputed": recomputed_set,
        "claim_boundary": {
            "append_only_reporting_repair_only": True,
            "predecessor_packet_or_audit_changed": False,
            "new_scientific_or_generalization_evidence": False,
        },
        "authorization": {
            "authorizes_goal5793": False,
            "authorizes_entropy_or_candidate_selection": False,
            "authorizes_implementation_or_execution": False,
            "authorizes_gpu_home_pod_or_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_product_change": False,
            "authorizes_publication_or_submission": False,
        },
        "auditor": {
            "path": SCRIPT_REL,
            "file_sha256": _sha((ROOT / SCRIPT_REL).read_bytes()),
        },
    }
    result["supplement_sha256"] = _sha(
        _canonical({key: value for key, value in result.items() if key != "supplement_sha256"})
    )
    return result


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("Goal5789-A2 packet-audit supplement is create-only")
    result = audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("xb") as handle:
        handle.write(_pretty(result))
    print(
        json.dumps(
            {
                "file_sha256": _sha(OUTPUT.read_bytes()),
                "supplement_sha256": result["supplement_sha256"],
                "payload_identity_checked_count": result["payload_identity_checked_count"],
                "payload_identity_mismatch_count": result["payload_identity_mismatch_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
