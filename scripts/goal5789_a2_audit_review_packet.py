"""Independently audit the exact Goal5789-A2 external-review packet."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5789_a2_callback_ir_authority_binding_review_packet_v1"
ARCHIVE = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_twin_20260821.tar.gz"
MANIFEST = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_manifest_20260821.json"
OUTPUT = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_audit_20260821.json"

# Repeated deliberately instead of imported from the packet builder.  This
# auditor is an independent consumer of the packet contract.
EXPECTED_DELIVERY_CLAIM_BOUNDARY = {
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


def _safe_member(name: str) -> str:
    if "\\" in name:
        raise RuntimeError(f"backslash in archive member: {name!r}")
    value = PurePosixPath(name)
    if (
        value.is_absolute()
        or value.as_posix() != name
        or any(part in {"", ".", ".."} or ":" in part for part in value.parts)
    ):
        raise RuntimeError(f"unsafe archive member: {name!r}")
    prefix = PREFIX + "/"
    if not name.startswith(prefix):
        raise RuntimeError(f"wrong archive prefix: {name!r}")
    relative = name[len(prefix) :]
    relative_path = PurePosixPath(relative)
    if (
        not relative
        or relative_path.is_absolute()
        or relative_path.as_posix() != relative
        or any(part in {"", ".", ".."} or ":" in part for part in relative_path.parts)
    ):
        raise RuntimeError("empty archive payload path")
    return relative


def _load_object(data: bytes, label: str) -> dict[str, Any]:
    value = json.loads(data)
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return value


def audit() -> dict[str, object]:
    archive = ARCHIVE.read_bytes()
    twin = TWIN.read_bytes()
    manifest_bytes = MANIFEST.read_bytes()
    if archive != twin:
        raise RuntimeError("review packet twin differs")
    manifest = _load_object(manifest_bytes, "external packet manifest")
    if set(manifest) != {
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
    }:
        raise RuntimeError("external packet manifest top-level schema mismatch")
    if (
        manifest.get("schema") != "rtdl.goal5789_a2.external_review_packet.v1"
        or manifest.get("goal") != "5789-A2"
        or manifest.get("date") != "2026-08-21"
        or manifest.get("status")
        != "FROZEN_EXACT_OWNER_SELECTED_EXTERNAL_REVIEW_PACKET__GOAL5793_BLOCKED"
        or manifest.get("claim_boundary") != EXPECTED_PACKET_CLAIM_BOUNDARY
        or manifest.get("authorization") != EXPECTED_PACKET_AUTHORIZATION
    ):
        raise RuntimeError("external packet status, claim, or authorization drift")
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or manifest.get("payload_count") != len(rows):
        raise RuntimeError("external packet manifest row shape mismatch")
    expected: dict[str, Mapping[str, object]] = {}
    total = 0
    digest_rows = []
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("malformed external packet row")
        relative = row["path"]
        size = row["bytes"]
        sha256 = row["sha256"]
        provenance = row["provenance"]
        if (
            not isinstance(relative, str)
            or relative in expected
            or type(size) is not int
            or size < 0
            or not isinstance(sha256, str)
            or len(sha256) != 64
            or any(char not in "0123456789abcdef" for char in sha256)
            or not isinstance(provenance, str)
            or not provenance
        ):
            raise RuntimeError("invalid or duplicate external packet row")
        _safe_member(f"{PREFIX}/{relative}")
        expected[relative] = row
        total += size
        digest_rows.append({"path": relative, "bytes": size, "sha256": sha256})
    if total != manifest.get("payload_bytes"):
        raise RuntimeError("external packet manifest byte total mismatch")
    if [row["path"] for row in rows] != sorted(expected):
        raise RuntimeError("external packet manifest rows are not in canonical path order")
    if _sha(_canonical(digest_rows)) != manifest.get("payload_set_sha256"):
        raise RuntimeError("external packet payload-set digest mismatch")

    observed: dict[str, bytes] = {}
    with gzip.GzipFile(fileobj=io.BytesIO(archive), mode="rb") as uncompressed:
        with tarfile.open(fileobj=uncompressed, mode="r:") as packet:
            for member in packet.getmembers():
                relative = _safe_member(member.name)
                if not member.isfile() or member.issym() or member.islnk():
                    raise RuntimeError(f"non-regular packet member: {member.name}")
                if (
                    member.mtime != 0
                    or member.uid != 0
                    or member.gid != 0
                    or member.mode != 0o444
                ):
                    raise RuntimeError(f"non-canonical packet metadata: {member.name}")
                if relative in observed:
                    raise RuntimeError(f"duplicate packet member: {relative}")
                stream = packet.extractfile(member)
                if stream is None:
                    raise RuntimeError(f"unreadable packet member: {relative}")
                observed[relative] = stream.read()
    embedded = observed.pop("PACKET_MANIFEST.json", None)
    if embedded != manifest_bytes:
        raise RuntimeError("embedded and external packet manifests differ")
    if set(observed) != set(expected):
        raise RuntimeError("packet and manifest member sets differ")
    for relative, row in expected.items():
        data = observed[relative]
        if len(data) != row["bytes"] or _sha(data) != row["sha256"]:
            raise RuntimeError(f"packet payload identity mismatch: {relative}")

    root = manifest.get("root_delivery_manifest")
    if not isinstance(root, Mapping) or set(root) != {
        "path",
        "bytes",
        "file_sha256",
        "delivery_manifest_sha256",
    }:
        raise RuntimeError("packet delivery root shape mismatch")
    delivery_bytes = observed.get(root["path"])
    if (
        delivery_bytes is None
        or len(delivery_bytes) != root["bytes"]
        or _sha(delivery_bytes) != root["file_sha256"]
    ):
        raise RuntimeError("packet delivery root identity mismatch")
    delivery = _load_object(delivery_bytes, "delivery manifest")
    if set(delivery) != {
        "schema",
        "delivery_manifest_sha256",
        "goal",
        "date",
        "status",
        "root_result",
        "payload_count",
        "payload_bytes",
        "payload_set_sha256",
        "payloads",
        "claim_boundary",
        "authorization",
    }:
        raise RuntimeError("delivery manifest top-level schema mismatch")
    body = dict(delivery)
    delivery_seal = body.pop("delivery_manifest_sha256", None)
    if delivery_seal != root["delivery_manifest_sha256"] or _sha(_canonical(body)) != delivery_seal:
        raise RuntimeError("delivery manifest internal seal mismatch")
    if (
        delivery.get("schema") != "rtdl.goal5789_a2.delivery_manifest.v1"
        or delivery.get("goal") != "5789-A2"
        or delivery.get("date") != "2026-08-21"
        or delivery.get("status")
        != "FINAL_LOCAL_DELIVERY__OWNER_SELECTED_EXTERNAL_REVIEW_PENDING__GOAL5793_BLOCKED"
        or delivery.get("claim_boundary") != EXPECTED_DELIVERY_CLAIM_BOUNDARY
        or delivery.get("authorization") != EXPECTED_DELIVERY_AUTHORIZATION
    ):
        raise RuntimeError("delivery manifest status, claim, or authorization drift")
    delivery_rows = delivery.get("payloads")
    if (
        not isinstance(delivery_rows, list)
        or delivery.get("payload_count") != len(delivery_rows)
        or type(delivery.get("payload_bytes")) is not int
    ):
        raise RuntimeError("delivery manifest payloads missing")
    delivery_paths: set[str] = set()
    delivery_digest_rows = []
    delivery_total = 0
    for row in delivery_rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("delivery manifest row shape mismatch")
        relative = row["path"]
        if (
            not isinstance(relative, str)
            or relative in delivery_paths
            or type(row["bytes"]) is not int
            or row["bytes"] < 0
            or not isinstance(row["sha256"], str)
            or len(row["sha256"]) != 64
            or any(char not in "0123456789abcdef" for char in row["sha256"])
            or not isinstance(row["provenance"], str)
            or not row["provenance"]
        ):
            raise RuntimeError(f"duplicate delivery manifest path: {relative}")
        _safe_member(f"{PREFIX}/{relative}")
        delivery_paths.add(relative)
        delivery_total += row["bytes"]
        delivery_digest_rows.append(
            {key: row[key] for key in ("path", "bytes", "sha256")}
        )
        observed_row = expected.get(relative)
        if observed_row is None or any(observed_row[key] != row[key] for key in ("bytes", "sha256")):
            raise RuntimeError(f"delivery-to-packet crossbind mismatch: {relative}")
    if [row["path"] for row in delivery_rows] != sorted(delivery_paths):
        raise RuntimeError("delivery manifest rows are not in canonical path order")
    if (
        delivery_total != delivery["payload_bytes"]
        or _sha(_canonical(delivery_digest_rows)) != delivery.get("payload_set_sha256")
    ):
        raise RuntimeError("delivery manifest payload-set digest mismatch")
    if set(expected) != delivery_paths | {str(root["path"])}:
        raise RuntimeError("packet contains payloads outside exact delivery root plus delivery rows")

    root_result = delivery.get("root_result")
    if not isinstance(root_result, Mapping) or set(root_result) != {
        "path",
        "bytes",
        "file_sha256",
        "result_sha256",
    }:
        raise RuntimeError("delivery root-result shape mismatch")
    result_bytes = observed.get(root_result["path"])
    if (
        result_bytes is None
        or len(result_bytes) != root_result["bytes"]
        or _sha(result_bytes) != root_result["file_sha256"]
    ):
        raise RuntimeError("delivery root-result file identity mismatch")
    result = _load_object(result_bytes, "Goal5789-A2 result")
    result_body = {key: item for key, item in result.items() if key != "result_sha256"}
    if (
        result.get("schema")
        != "rtdl.goal5789_a2.callback_ir_authority_binding_result.v1"
        or result.get("result_sha256") != root_result["result_sha256"]
        or _sha(_canonical(result_body)) != root_result["result_sha256"]
        or result.get("status")
        != "COMPLETE_LOCAL_CALLBACK_IR_AUTHORITY_BINDING_EVIDENCE__EXTERNAL_REVIEW_REQUIRED__GOAL5793_BLOCKED"
        or result.get("research_integrity") != EXPECTED_DELIVERY_CLAIM_BOUNDARY
        or result.get("authorization") != EXPECTED_RESULT_AUTHORIZATION
    ):
        raise RuntimeError("delivery root-result seal, status, claim, or authorization mismatch")

    result: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.external_review_packet_audit.v1",
        "audit_sha256": "",
        "status": "PASS__EXACT_DETERMINISTIC_PACKET_TWIN_MANIFEST_AND_DELIVERY_CROSSBIND",
        "archive": {
            "path": str(ARCHIVE.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(archive),
            "file_sha256": _sha(archive),
        },
        "twin": {
            "path": str(TWIN.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(twin),
            "file_sha256": _sha(twin),
            "byte_identical": True,
        },
        "manifest": {
            "path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(manifest_bytes),
            "file_sha256": _sha(manifest_bytes),
            "payload_count": len(expected),
            "payload_bytes": total,
            "payload_set_sha256": manifest["payload_set_sha256"],
        },
        "checks": {
            "exact_member_set": True,
            "embedded_manifest_byte_identical": True,
            "delivery_manifest_crossbound": True,
            "regular_file_only": True,
            "canonical_metadata": True,
            "unsafe_member_count": 0,
        },
        "authorization": {
            "authorizes_goal5793": False,
            "authorizes_execution": False,
            "authorizes_gpu_home_pod_or_ssh": False,
            "authorizes_worker_or_timing": False,
            "authorizes_product_change": False,
            "authorizes_publication_or_submission": False,
        },
    }
    result["audit_sha256"] = _sha(_canonical({k: v for k, v in result.items() if k != "audit_sha256"}))
    return result


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("Goal5789-A2 packet audit receipt is create-only")
    result = audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("xb") as handle:
        handle.write(_pretty(result))
    print(
        json.dumps(
            {
                "file_sha256": _sha(OUTPUT.read_bytes()),
                "audit_sha256": result["audit_sha256"],
                "status": result["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
