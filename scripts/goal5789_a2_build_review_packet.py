"""Build the deterministic Goal5789-A2 owner-selected external-review packet.

The packet is a transport container for the exact local delivery manifest and
every payload it names.  It does not authorize Goal5793, execution, GPU/POD,
performance measurement, publication, or submission.
"""

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
DELIVERY_REL = "history/internal_docs/goal5789_a2_delivery_manifest_20260821.json"
ARCHIVE = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_20260821.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_twin_20260821.tar.gz"
MANIFEST = ROOT / "history/internal_docs/goal5789_a2_callback_ir_authority_binding_review_packet_v1_manifest_20260821.json"

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


def _safe(relative: str) -> str:
    if "\\" in relative:
        raise RuntimeError(f"backslash is forbidden in packet path: {relative!r}")
    value = PurePosixPath(relative)
    normalized = value.as_posix()
    if (
        value.is_absolute()
        or not value.parts
        or any(part in {"", ".", ".."} or ":" in part for part in value.parts)
        or normalized != relative
    ):
        raise RuntimeError(f"unsafe packet path: {relative!r}")
    return normalized


def _read_regular(relative: str, size: int, sha256: str) -> bytes:
    path = ROOT / Path(*PurePosixPath(_safe(relative)).parts)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"packet payload is not a regular non-link file: {relative}")
    data = path.read_bytes()
    if len(data) != size or _sha(data) != sha256:
        raise RuntimeError(f"packet payload identity mismatch: {relative}")
    return data


def _load_delivery() -> tuple[dict[str, Any], bytes]:
    path = ROOT / DELIVERY_REL
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Goal5789-A2 delivery manifest is absent or non-regular")
    data = path.read_bytes()
    value = json.loads(data)
    if not isinstance(value, dict):
        raise RuntimeError("Goal5789-A2 delivery manifest must be an object")
    if set(value) != {
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
        raise RuntimeError("Goal5789-A2 delivery manifest top-level schema mismatch")
    body = {key: item for key, item in value.items() if key != "delivery_manifest_sha256"}
    if value.get("delivery_manifest_sha256") != _sha(_canonical(body)):
        raise RuntimeError("Goal5789-A2 delivery manifest seal mismatch")
    if (
        value.get("schema") != "rtdl.goal5789_a2.delivery_manifest.v1"
        or value.get("goal") != "5789-A2"
        or value.get("date") != "2026-08-21"
        or value.get("status")
        != "FINAL_LOCAL_DELIVERY__OWNER_SELECTED_EXTERNAL_REVIEW_PENDING__GOAL5793_BLOCKED"
        or value.get("claim_boundary") != EXPECTED_DELIVERY_CLAIM_BOUNDARY
        or value.get("authorization") != EXPECTED_DELIVERY_AUTHORIZATION
    ):
        raise RuntimeError("Goal5789-A2 delivery manifest scope or claim mismatch")
    rows = value.get("payloads")
    if (
        not isinstance(rows, list)
        or value.get("payload_count") != len(rows)
        or type(value.get("payload_bytes")) is not int
    ):
        raise RuntimeError("Goal5789-A2 delivery manifest shape mismatch")
    digest_rows = []
    total = 0
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("Goal5789-A2 delivery manifest row mismatch")
        relative = row["path"]
        size = row["bytes"]
        sha256 = row["sha256"]
        if (
            not isinstance(relative, str)
            or relative in seen
            or relative == DELIVERY_REL
            or type(size) is not int
            or size < 0
            or not isinstance(sha256, str)
            or len(sha256) != 64
            or any(char not in "0123456789abcdef" for char in sha256)
            or not isinstance(row["provenance"], str)
            or not row["provenance"]
        ):
            raise RuntimeError("Goal5789-A2 delivery manifest row type or uniqueness mismatch")
        _safe(relative)
        seen.add(relative)
        total += size
        digest_rows.append({"path": relative, "bytes": size, "sha256": sha256})
    if [row["path"] for row in rows] != sorted(seen):
        raise RuntimeError("Goal5789-A2 delivery rows are not canonically ordered")
    if total != value["payload_bytes"] or _sha(_canonical(digest_rows)) != value.get("payload_set_sha256"):
        raise RuntimeError("Goal5789-A2 delivery manifest payload-set mismatch")
    root_result = value.get("root_result")
    if not isinstance(root_result, Mapping) or set(root_result) != {
        "path",
        "bytes",
        "file_sha256",
        "result_sha256",
    }:
        raise RuntimeError("Goal5789-A2 delivery root-result shape mismatch")
    result_row = next((row for row in rows if row["path"] == root_result["path"]), None)
    if (
        result_row is None
        or root_result["bytes"] != result_row["bytes"]
        or root_result["file_sha256"] != result_row["sha256"]
    ):
        raise RuntimeError("Goal5789-A2 delivery root-result row mismatch")
    result_data = _read_regular(
        str(root_result["path"]), int(root_result["bytes"]), str(root_result["file_sha256"])
    )
    result = json.loads(result_data)
    if not isinstance(result, dict):
        raise RuntimeError("Goal5789-A2 root result must be an object")
    result_body = {key: item for key, item in result.items() if key != "result_sha256"}
    if (
        result.get("schema") != "rtdl.goal5789_a2.callback_ir_authority_binding_result.v1"
        or result.get("status")
        != "COMPLETE_LOCAL_CALLBACK_IR_AUTHORITY_BINDING_EVIDENCE__EXTERNAL_REVIEW_REQUIRED__GOAL5793_BLOCKED"
        or result.get("result_sha256") != root_result["result_sha256"]
        or _sha(_canonical(result_body)) != root_result["result_sha256"]
        or result.get("research_integrity") != EXPECTED_DELIVERY_CLAIM_BOUNDARY
        or result.get("authorization") != EXPECTED_RESULT_AUTHORIZATION
    ):
        raise RuntimeError("Goal5789-A2 root-result seal, claim, or authorization mismatch")
    return value, data


def build_packet() -> tuple[bytes, bytes, dict[str, object]]:
    delivery, delivery_bytes = _load_delivery()
    payloads: dict[str, bytes] = {DELIVERY_REL: delivery_bytes}
    provenance: dict[str, str] = {DELIVERY_REL: "goal5789_a2_delivery_manifest_root"}
    total_delivery_bytes = 0
    for row in delivery["payloads"]:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("malformed Goal5789-A2 delivery row")
        relative = row["path"]
        size = row["bytes"]
        sha256 = row["sha256"]
        source = row["provenance"]
        if (
            not isinstance(relative, str)
            or type(size) is not int
            or size < 0
            or not isinstance(sha256, str)
            or len(sha256) != 64
            or not isinstance(source, str)
            or not source
        ):
            raise RuntimeError("invalid Goal5789-A2 delivery row types")
        if relative in payloads:
            raise RuntimeError(f"duplicate Goal5789-A2 delivery path: {relative}")
        payloads[relative] = _read_regular(relative, size, sha256)
        provenance[relative] = source
        total_delivery_bytes += size
    if total_delivery_bytes != delivery["payload_bytes"]:
        raise RuntimeError("Goal5789-A2 delivery byte total mismatch")

    rows = [
        {
            "path": relative,
            "bytes": len(data),
            "sha256": _sha(data),
            "provenance": provenance[relative],
        }
        for relative, data in sorted(payloads.items())
    ]
    manifest: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.external_review_packet.v1",
        "goal": "5789-A2",
        "date": "2026-08-21",
        "status": "FROZEN_EXACT_OWNER_SELECTED_EXTERNAL_REVIEW_PACKET__GOAL5793_BLOCKED",
        "root_delivery_manifest": {
            "path": DELIVERY_REL,
            "bytes": len(delivery_bytes),
            "file_sha256": _sha(delivery_bytes),
            "delivery_manifest_sha256": delivery["delivery_manifest_sha256"],
        },
        "payload_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "payload_set_sha256": _sha(
            _canonical(
                [
                    {key: row[key] for key in ("path", "bytes", "sha256")}
                    for row in rows
                ]
            )
        ),
        "payloads": rows,
        "claim_boundary": EXPECTED_PACKET_CLAIM_BOUNDARY,
        "authorization": EXPECTED_PACKET_AUTHORIZATION,
    }
    manifest_bytes = _pretty(manifest)

    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as archive:
            archive_payloads = dict(payloads)
            archive_payloads["PACKET_MANIFEST.json"] = manifest_bytes
            for relative, data in sorted(archive_payloads.items()):
                info = tarfile.TarInfo(f"{PREFIX}/{relative}")
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o444
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    return raw.getvalue(), manifest_bytes, manifest


def _write_create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def main() -> int:
    if ARCHIVE.exists() or TWIN.exists() or MANIFEST.exists():
        raise RuntimeError("Goal5789-A2 review packet outputs are create-only")
    archive, manifest_bytes, manifest = build_packet()
    _write_create_only(ARCHIVE, archive)
    try:
        _write_create_only(TWIN, archive)
        _write_create_only(MANIFEST, manifest_bytes)
    except Exception:
        ARCHIVE.unlink(missing_ok=True)
        TWIN.unlink(missing_ok=True)
        MANIFEST.unlink(missing_ok=True)
        raise
    print(
        json.dumps(
            {
                "archive_sha256": _sha(archive),
                "archive_bytes": len(archive),
                "manifest_sha256": _sha(manifest_bytes),
                "manifest_bytes": len(manifest_bytes),
                "payload_count": manifest["payload_count"],
                "payload_bytes": manifest["payload_bytes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
