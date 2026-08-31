#!/usr/bin/env python3
"""Validate author-code materialization receipts using offline fixtures only."""

from __future__ import annotations

import base64
import hashlib
import io
from pathlib import PurePosixPath
import stat
import tarfile
from typing import Any, Mapping, Sequence
import zipfile

try:
    from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
    from scripts.goal5793_x2_offline_core import RETRY_DELAYS, X2Error, normalize_https_url, parse_timestamp_ms
except ModuleNotFoundError:
    from goal5793_x1_canonical import canonical_json_bytes, seal_document  # type: ignore
    from goal5793_x2_offline_core import RETRY_DELAYS, X2Error, normalize_https_url, parse_timestamp_ms  # type: ignore


MAX_ARCHIVE_BYTES = 250_000_000
MAX_MEMBERS = 100_000
MAX_UNCOMPRESSED_BYTES = 1_000_000_000


def _exact(value: Mapping[str, Any], keys: set[str], fail_id: str) -> None:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise X2Error(fail_id)


def _rel(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise X2Error("AUTHOR_CODE_ARCHIVE_PATH_INVALID")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or "." in path.parts or ".." in path.parts:
        raise X2Error("AUTHOR_CODE_ARCHIVE_PATH_INVALID")
    return value


def _rows_from_archive(data: bytes, archive_format: str) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    if not data or len(data) > MAX_ARCHIVE_BYTES:
        raise X2Error("AUTHOR_CODE_ARCHIVE_SIZE_INVALID")
    files: dict[str, bytes] = {}
    if archive_format == "zip":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                infos = archive.infolist()
                if len(infos) > MAX_MEMBERS:
                    raise X2Error("AUTHOR_CODE_ARCHIVE_MEMBER_LIMIT")
                for info in infos:
                    if info.is_dir():
                        continue
                    mode = (info.external_attr >> 16) & 0xFFFF
                    if mode and not stat.S_ISREG(mode):
                        raise X2Error("AUTHOR_CODE_ARCHIVE_NONREGULAR_MEMBER")
                    rel = _rel(info.filename)
                    if rel in files:
                        raise X2Error("AUTHOR_CODE_ARCHIVE_DUPLICATE_MEMBER")
                    files[rel] = archive.read(info)
        except (zipfile.BadZipFile, RuntimeError) as exc:
            if isinstance(exc, X2Error):
                raise
            raise X2Error("AUTHOR_CODE_ARCHIVE_PARSE_FAILED") from exc
    elif archive_format == "tar":
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                members = archive.getmembers()
                if len(members) > MAX_MEMBERS:
                    raise X2Error("AUTHOR_CODE_ARCHIVE_MEMBER_LIMIT")
                for member in members:
                    if member.isdir():
                        continue
                    if not member.isreg():
                        raise X2Error("AUTHOR_CODE_ARCHIVE_NONREGULAR_MEMBER")
                    rel = _rel(member.name)
                    if rel in files:
                        raise X2Error("AUTHOR_CODE_ARCHIVE_DUPLICATE_MEMBER")
                    stream = archive.extractfile(member)
                    if stream is None:
                        raise X2Error("AUTHOR_CODE_ARCHIVE_PARSE_FAILED")
                    files[rel] = stream.read()
        except (tarfile.TarError, OSError) as exc:
            if isinstance(exc, X2Error):
                raise
            raise X2Error("AUTHOR_CODE_ARCHIVE_PARSE_FAILED") from exc
    else:
        raise X2Error("AUTHOR_CODE_ARCHIVE_FORMAT_INVALID")
    if sum(map(len, files.values())) > MAX_UNCOMPRESSED_BYTES:
        raise X2Error("AUTHOR_CODE_ARCHIVE_UNCOMPRESSED_LIMIT")
    rows = [
        {"path": rel, "bytes": len(files[rel]), "sha256": hashlib.sha256(files[rel]).hexdigest()}
        for rel in sorted(files, key=lambda item: item.encode("utf-8"))
    ]
    return rows, files


def _attempt_body(lineage: Mapping[str, Any], expected_url: str, previous_response_ms: int | None) -> tuple[bytes | None, list[dict[str, Any]], int]:
    attempts = lineage.get("attempts")
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= 6:
        raise X2Error("AUTHOR_CODE_ATTEMPT_COUNT_INVALID")
    preserved: list[dict[str, Any]] = []
    body: bytes | None = None
    last = previous_response_ms
    for index, attempt in enumerate(attempts):
        _exact(
            attempt,
            {"attempt", "scheduled_delay_seconds", "request_url", "request_headers", "request_started_at_utc", "status", "response_headers", "response_received_at_utc", "body_base64", "error"},
            "AUTHOR_CODE_ATTEMPT_SCHEMA_INVALID",
        )
        if attempt["attempt"] != index + 1 or attempt["scheduled_delay_seconds"] != RETRY_DELAYS[index]:
            raise X2Error("AUTHOR_CODE_RETRY_SCHEDULE_DRIFT")
        if normalize_https_url(attempt["request_url"]) != expected_url or attempt["request_headers"] != []:
            raise X2Error("AUTHOR_CODE_REQUEST_IDENTITY_DRIFT")
        started = parse_timestamp_ms(attempt["request_started_at_utc"])
        received = parse_timestamp_ms(attempt["response_received_at_utc"])
        if received < started or (last is not None and started < last + (RETRY_DELAYS[index] * 1000 if index else 0)):
            raise X2Error("AUTHOR_CODE_REQUEST_TIME_ORDER_INVALID")
        last = received
        status = attempt["status"]
        error = attempt["error"]
        if status is not None and (type(status) is not int or not 100 <= status <= 599):
            raise X2Error("AUTHOR_CODE_STATUS_INVALID")
        if error is not None and (not isinstance(error, str) or not error):
            raise X2Error("AUTHOR_CODE_ERROR_INVALID")
        try:
            decoded = base64.b64decode(attempt["body_base64"], validate=True)
        except Exception as exc:
            raise X2Error("AUTHOR_CODE_BODY_BASE64_INVALID") from exc
        success = status == 200 and error is None
        if success and index != len(attempts) - 1:
            raise X2Error("AUTHOR_CODE_ATTEMPTS_AFTER_SUCCESS")
        if not success and index == len(attempts) - 1 and len(attempts) < 6:
            raise X2Error("AUTHOR_CODE_PREMATURE_RETRY_STOP")
        if success:
            body = decoded
        preserved.append(
            {
                "attempt": index + 1,
                "request_started_ms": started,
                "response_received_ms": received,
                "status": status,
                "error": error,
                "response_headers": attempt["response_headers"],
                "body_bytes": len(decoded),
                "body_sha256": hashlib.sha256(decoded).hexdigest(),
            }
        )
    return body, preserved, int(last)


def _materialize(body: bytes, materialization: Mapping[str, Any], url: str) -> dict[str, Any]:
    _exact(
        materialization,
        {"kind", "archive_format", "license_path", "requested_ref", "resolved_commit", "resolved_tree", "lfs_objects", "submodules"},
        "AUTHOR_CODE_MATERIALIZATION_SCHEMA_INVALID",
    )
    if materialization["kind"] not in {"ARCHIVE", "GIT_REPOSITORY"}:
        raise X2Error("AUTHOR_CODE_MATERIALIZATION_KIND_INVALID")
    rows, files = _rows_from_archive(body, materialization["archive_format"])
    license_path = _rel(materialization["license_path"])
    if license_path not in files:
        raise X2Error("AUTHOR_CODE_LICENSE_MISSING")
    if materialization["kind"] == "GIT_REPOSITORY":
        if not isinstance(materialization["requested_ref"], str) or not materialization["requested_ref"]:
            raise X2Error("AUTHOR_CODE_GIT_REF_INVALID")
        for key in ("resolved_commit", "resolved_tree"):
            value = materialization[key]
            if not isinstance(value, str) or len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
                raise X2Error("AUTHOR_CODE_GIT_IDENTITY_INVALID")
    elif any(materialization[key] is not None for key in ("requested_ref", "resolved_commit", "resolved_tree")):
        raise X2Error("AUTHOR_CODE_ARCHIVE_GIT_FIELDS_NON_NULL")
    lfs = materialization["lfs_objects"]
    submodules = materialization["submodules"]
    if not isinstance(lfs, list) or not isinstance(submodules, list):
        raise X2Error("AUTHOR_CODE_AUXILIARY_SCHEMA_INVALID")
    lfs_by_path: dict[str, Mapping[str, Any]] = {}
    for row in lfs:
        _exact(row, {"path", "oid_sha256", "bytes", "fetched", "object_sha256"}, "AUTHOR_CODE_LFS_SCHEMA_INVALID")
        rel = _rel(row["path"])
        if rel in lfs_by_path:
            raise X2Error("AUTHOR_CODE_LFS_DUPLICATE")
        lfs_by_path[rel] = row
    detected: list[dict[str, Any]] = []
    for rel, member in files.items():
        if not member.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
            continue
        lines = member.decode("utf-8", errors="strict").splitlines()
        oid = next((line[11:] for line in lines if line.startswith("oid sha256:")), None)
        size_text = next((line[5:] for line in lines if line.startswith("size ")), None)
        if oid is None or size_text is None or len(oid) != 64 or not size_text.isdigit():
            raise X2Error("AUTHOR_CODE_LFS_POINTER_INVALID")
        declared = lfs_by_path.get(rel)
        if declared is None or declared["oid_sha256"] != oid or declared["bytes"] != int(size_text):
            raise X2Error("AUTHOR_CODE_LFS_RECEIPT_MISMATCH")
        detected.append({"path": rel, "oid_sha256": oid, "bytes": int(size_text), "fetched": declared["fetched"], "object_sha256": declared["object_sha256"]})
    if set(lfs_by_path) != {row["path"] for row in detected}:
        raise X2Error("AUTHOR_CODE_LFS_RECEIPT_MISMATCH")
    submodule_rows: list[dict[str, Any]] = []
    for row in submodules:
        _exact(row, {"path", "commit", "fetched"}, "AUTHOR_CODE_SUBMODULE_SCHEMA_INVALID")
        rel = _rel(row["path"])
        commit = row["commit"]
        if not isinstance(commit, str) or len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
            raise X2Error("AUTHOR_CODE_SUBMODULE_IDENTITY_INVALID")
        submodule_rows.append({"path": rel, "commit": commit, "fetched": row["fetched"] is True})
    complete = all(row["fetched"] is True and isinstance(row["object_sha256"], str) and len(row["object_sha256"]) == 64 for row in detected) and all(row["fetched"] for row in submodule_rows)
    identity = {
        "kind": materialization["kind"],
        "url": url,
        "requested_ref": materialization["requested_ref"],
        "resolved_commit": materialization["resolved_commit"],
        "resolved_tree": materialization["resolved_tree"],
    }
    return {
        "identity": identity,
        "archive": {"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "format": materialization["archive_format"], "member_count": len(rows), "member_bytes": sum(row["bytes"] for row in rows), "member_rows_sha256": hashlib.sha256(canonical_json_bytes(rows)).hexdigest(), "members": rows},
        "license": {"path": license_path, "bytes": len(files[license_path]), "sha256": hashlib.sha256(files[license_path]).hexdigest()},
        "lfs_objects": detected,
        "submodules": submodule_rows,
        "materialization_complete": complete,
    }


def validate_author_code_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    _exact(fixture, {"schema", "mode", "synthetic_fixture", "network_call_count", "direct_link_plan", "link_lineages"}, "AUTHOR_CODE_FIXTURE_SCHEMA_INVALID")
    if fixture["schema"] != "rtdl.goal5793.x2.offline_author_code_fixture.v1" or fixture["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY" or fixture["synthetic_fixture"] is not True or fixture["network_call_count"] != 0:
        raise X2Error("LIVE_AUTHOR_CODE_RESOLUTION_FORBIDDEN_IN_X2")
    plan = fixture["direct_link_plan"]
    lineages = fixture["link_lineages"]
    if not isinstance(plan, list) or not isinstance(lineages, list) or len(lineages) != len(plan):
        raise X2Error("AUTHOR_CODE_ALL_DIRECT_LINKS_NOT_ATTEMPTED")
    successful: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    previous: int | None = None
    for index, (planned, lineage) in enumerate(zip(plan, lineages)):
        _exact(planned, {"source", "url"}, "AUTHOR_CODE_PLAN_SCHEMA_INVALID")
        _exact(lineage, {"source", "url", "attempts", "materialization"}, "AUTHOR_CODE_LINEAGE_SCHEMA_INVALID")
        url = normalize_https_url(planned["url"])
        if lineage["source"] != planned["source"] or normalize_https_url(lineage["url"]) != url:
            raise X2Error("AUTHOR_CODE_LINK_ORDER_MISMATCH")
        body, attempts, previous = _attempt_body(lineage, url, previous)
        materialized = None
        if body is not None:
            if not isinstance(lineage["materialization"], Mapping):
                raise X2Error("AUTHOR_CODE_SUCCESS_WITHOUT_MATERIALIZATION")
            materialized = _materialize(body, lineage["materialization"], url)
            successful.append(materialized)
        elif lineage["materialization"] is not None:
            raise X2Error("AUTHOR_CODE_FAILED_REQUEST_HAS_MATERIALIZATION")
        evidence.append({"link_index": index, "source": planned["source"], "url": url, "attempts": attempts, "materialization": materialized})
    identities = [row["identity"] for row in successful]
    unique = {hashlib.sha256(canonical_json_bytes(row)).hexdigest() for row in identities}
    ambiguous = len(unique) > 1
    incomplete = any(not row["materialization_complete"] for row in successful)
    if ambiguous:
        status = "NA_AMBIGUOUS_AUTHOR_CODE__NO_MANUAL_CHOICE"
    elif incomplete:
        status = "NA_INCOMPLETE_LFS_OR_SUBMODULE"
    elif len(successful) == 1:
        status = "AUTHOR_CODE_MATERIALIZED_FOR_STRUCTURAL_COMPARISON_ONLY"
    else:
        status = "NA_AUTHOR_CODE_NOT_MATERIALIZED"
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.offline_author_code_result.v1",
        "status": status,
        "all_direct_links_attempted_in_order": True,
        "first_success_short_circuit_used": False,
        "general_repository_search_used": False,
        "link_evidence": evidence,
        "successful_materialization_count": len(successful),
        "distinct_repository_or_ref_identity_count": len(unique),
        "ambiguous": ambiguous,
        "incomplete_lfs_or_submodule": incomplete,
        "author_code_required_for_selection_eligibility": False,
        "selection_eligibility_changed_by_author_code": False,
        "activity": {"network_calls": 0, "live_repository_requests": 0, "manual_choices": 0},
        "authorization": {"live_search": False, "source_fetch": False, "git_fetch": False, "candidate_work": False, "selection": False},
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(result, seal_field="result_sha256", domain="rtdl.goal5793.x2.offline_author_code_result", version=1)
    return result

