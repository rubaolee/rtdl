#!/usr/bin/env python3
"""Validate uniform full-text/source resolution using offline fixtures only."""

from __future__ import annotations

import base64
import hashlib
from typing import Any, Mapping, Sequence

try:
    from scripts.goal5793_x1_canonical import seal_document
    from scripts.goal5793_x2_offline_core import RETRY_DELAYS, X2Error, normalize_https_url, parse_timestamp_ms
    from scripts.goal5793_x2_run_pdf_identity import run_isolated_pdf_identity
except ModuleNotFoundError:
    from goal5793_x1_canonical import seal_document  # type: ignore
    from goal5793_x2_offline_core import RETRY_DELAYS, X2Error, normalize_https_url, parse_timestamp_ms  # type: ignore
    from goal5793_x2_run_pdf_identity import run_isolated_pdf_identity  # type: ignore


REPOSITORY_OR_ARTIFACT_HOSTS = (
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "zenodo.org",
    "figshare.com",
    "osf.io",
    "huggingface.co",
)
ARCHIVE_SUFFIXES = (".zip", ".tar.gz", ".tgz", ".tar", ".git")


def _exact(value: Mapping[str, Any], keys: set[str], reason: str) -> None:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise X2Error(reason)


def _headers(value: Any, reason: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise X2Error(reason)
    result: list[dict[str, str]] = []
    for row in value:
        if not isinstance(row, Mapping) or set(row) != {"name", "value"}:
            raise X2Error(reason)
        if not isinstance(row["name"], str) or not row["name"] or not isinstance(row["value"], str):
            raise X2Error(reason)
        result.append({"name": row["name"], "value": row["value"]})
    return result


def _content_type(rows: Sequence[Mapping[str, str]]) -> str | None:
    values = [row["value"].split(";", 1)[0].strip().lower() for row in rows if row["name"].lower() == "content-type"]
    if len(values) > 1:
        raise X2Error("SOURCE_RESPONSE_CONTENT_TYPE_AMBIGUOUS")
    return values[0] if values else None


def _redirects(value: Any, request_url: str) -> tuple[str, list[dict[str, Any]]]:
    if not isinstance(value, list) or len(value) > 10:
        raise X2Error("SOURCE_REDIRECT_CHAIN_INVALID")
    current = request_url
    result: list[dict[str, Any]] = []
    for row in value:
        _exact(row, {"status", "from_url", "location_url", "headers", "received_at_utc"}, "SOURCE_REDIRECT_SCHEMA_INVALID")
        if row["status"] not in (301, 302, 303, 307, 308) or normalize_https_url(row["from_url"]) != current:
            raise X2Error("SOURCE_REDIRECT_CHAIN_INVALID")
        location = normalize_https_url(row["location_url"])
        headers = _headers(row["headers"], "SOURCE_REDIRECT_HEADERS_INVALID")
        received_ms = parse_timestamp_ms(row["received_at_utc"])
        result.append({"status": row["status"], "from_url": current, "location_url": location, "headers": headers, "received_ms": received_ms})
        current = location
    return current, result


def _attempts(slot: Mapping[str, str], lineage: Mapping[str, Any], previous_response_ms: int | None) -> tuple[bytes | None, list[dict[str, Any]], int]:
    _exact(lineage, {"slot_kind", "url", "attempts"}, "SOURCE_LINEAGE_SCHEMA_MISMATCH")
    if lineage["slot_kind"] != slot["slot_kind"] or normalize_https_url(lineage["url"]) != slot["url"]:
        raise X2Error("SOURCE_LINEAGE_SLOT_ORDER_MISMATCH")
    attempts = lineage["attempts"]
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= 6:
        raise X2Error("SOURCE_ATTEMPT_COUNT_INVALID")
    expected_request_headers = [{"name": "Accept", "value": "application/pdf"}] if slot["slot_kind"] == "DOI_ACCEPT_PDF" else []
    evidence: list[dict[str, Any]] = []
    success: bytes | None = None
    last_response_ms = previous_response_ms
    for index, attempt in enumerate(attempts):
        _exact(
            attempt,
            {
                "attempt", "scheduled_delay_seconds", "request_url", "request_headers", "request_started_at_utc",
                "redirect_chain", "final_url", "status", "response_headers", "response_received_at_utc", "body_base64", "error",
            },
            "SOURCE_ATTEMPT_SCHEMA_MISMATCH",
        )
        if attempt["attempt"] != index + 1 or attempt["scheduled_delay_seconds"] != RETRY_DELAYS[index]:
            raise X2Error("SOURCE_RETRY_SCHEDULE_DRIFT")
        request_url = normalize_https_url(attempt["request_url"])
        if request_url != slot["url"] or _headers(attempt["request_headers"], "SOURCE_REQUEST_HEADERS_INVALID") != expected_request_headers:
            raise X2Error("SOURCE_REQUEST_IDENTITY_OR_HEADERS_DRIFT")
        started_ms = parse_timestamp_ms(attempt["request_started_at_utc"])
        final_from_chain, redirects = _redirects(attempt["redirect_chain"], request_url)
        final_url = normalize_https_url(attempt["final_url"])
        if final_url != final_from_chain:
            raise X2Error("SOURCE_REDIRECT_FINAL_URL_MISMATCH")
        response_ms = parse_timestamp_ms(attempt["response_received_at_utc"])
        if response_ms < started_ms or any(row["received_ms"] < started_ms or row["received_ms"] > response_ms for row in redirects):
            raise X2Error("SOURCE_ATTEMPT_TIME_ORDER_INVALID")
        if last_response_ms is not None and started_ms < last_response_ms + (RETRY_DELAYS[index] * 1000 if index else 0):
            raise X2Error("SOURCE_ATTEMPT_OVERLAP_OR_RETRY_TOO_EARLY")
        last_response_ms = response_ms
        status = attempt["status"]
        if status is not None and (type(status) is not int or not 100 <= status <= 599):
            raise X2Error("SOURCE_HTTP_STATUS_INVALID")
        error = attempt["error"]
        if error is not None and (not isinstance(error, str) or not error):
            raise X2Error("SOURCE_ERROR_FIELD_INVALID")
        try:
            body = base64.b64decode(attempt["body_base64"], validate=True)
        except Exception as exc:
            raise X2Error("SOURCE_BODY_BASE64_INVALID") from exc
        response_headers = _headers(attempt["response_headers"], "SOURCE_RESPONSE_HEADERS_INVALID")
        is_http_success = status == 200 and error is None
        is_pdf = is_http_success and _content_type(response_headers) == "application/pdf" and body.startswith(b"%PDF-")
        evidence.append(
            {
                "attempt": index + 1, "request_url": request_url, "final_url": final_url, "redirect_count": len(redirects),
                "status": status, "error": error, "response_headers": response_headers,
                "request_started_ms": started_ms, "response_received_ms": response_ms,
                "body_bytes": len(body), "body_sha256": hashlib.sha256(body).hexdigest(),
                "classification": "VALID_PDF_RESPONSE" if is_pdf else ("HTTP_200_NON_PDF__URL_TERMINAL" if is_http_success else "RETRYABLE_FAILURE"),
            }
        )
        if is_pdf:
            if index != len(attempts) - 1:
                raise X2Error("SOURCE_ATTEMPTS_AFTER_SUCCESS")
            success = body
        elif is_http_success:
            if index != len(attempts) - 1:
                raise X2Error("SOURCE_ATTEMPTS_AFTER_TERMINAL_NON_PDF")
        elif index == len(attempts) - 1 and len(attempts) < 6:
            raise X2Error("SOURCE_PREMATURE_RETRY_STOP")
    return success, evidence, int(last_response_ms)


def _artifact_links(component_links: Sequence[Mapping[str, str]], annotation_urls: Sequence[str]) -> list[dict[str, str]]:
    candidates: list[tuple[str, str]] = []
    for row in component_links:
        if not isinstance(row, Mapping) or set(row) != {"slot_kind", "url"}:
            raise X2Error("DIRECT_LINK_SLOT_SCHEMA_INVALID")
        candidates.append((row["slot_kind"], normalize_https_url(row["url"])))
    candidates.extend(("PDF_ANNOTATION", normalize_https_url(url)) for url in annotation_urls)
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for kind, url in candidates:
        host_and_path = url[8:]
        host = host_and_path.split("/", 1)[0].split(":", 1)[0]
        path_lower = ("/" + host_and_path.split("/", 1)[1] if "/" in host_and_path else "").lower()
        eligible = host in REPOSITORY_OR_ARTIFACT_HOSTS or path_lower.endswith(ARCHIVE_SUFFIXES)
        if eligible and url not in seen:
            result.append({"source": kind, "url": url})
            seen.add(url)
    return result


def validate_resolution_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    _exact(
        fixture,
        {"schema", "mode", "synthetic_fixture", "network_call_count", "component", "source_lineages"},
        "SOURCE_FIXTURE_SCHEMA_MISMATCH",
    )
    if fixture["schema"] != "rtdl.goal5793.x2.offline_source_resolution_fixture.v1":
        raise X2Error("SOURCE_FIXTURE_SCHEMA_MISMATCH")
    if fixture["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY" or fixture["synthetic_fixture"] is not True or fixture["network_call_count"] != 0:
        raise X2Error("LIVE_SOURCE_RESOLUTION_FORBIDDEN_IN_X2")
    component = fixture["component"]
    required_component = {"component_id", "doi", "arxiv", "openalex", "title", "first_author", "year", "source_url_slots", "direct_link_slots"}
    if not isinstance(component, Mapping) or not required_component <= set(component):
        raise X2Error("SOURCE_COMPONENT_SCHEMA_MISMATCH")
    slots = component["source_url_slots"]
    lineages = fixture["source_lineages"]
    if not isinstance(slots, list) or not isinstance(lineages, list) or len(lineages) > len(slots):
        raise X2Error("SOURCE_LINEAGE_SET_MISMATCH")
    success_receipt: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] = []
    previous_response_ms: int | None = None
    for index, lineage in enumerate(lineages):
        if success_receipt is not None:
            raise X2Error("SOURCE_LINEAGES_AFTER_FIRST_SUCCESS")
        slot = slots[index]
        body, attempts, previous_response_ms = _attempts(slot, lineage, previous_response_ms)
        evidence.append({"slot_index": index, "slot": dict(slot), "attempts": attempts})
        if body is not None:
            isolated = run_isolated_pdf_identity(body, component)
            success_receipt = isolated["pdf_identity_receipt"]
    if success_receipt is None and len(lineages) != len(slots):
        raise X2Error("SOURCE_URL_SLOT_NOT_ATTEMPTED")
    source_qualified = bool(success_receipt and success_receipt["identity_checks"]["matched"])
    annotation_urls = success_receipt["extraction"]["annotation_urls_in_object_order"] if success_receipt else []
    direct_plan = _artifact_links(component["direct_link_slots"], annotation_urls)
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.offline_source_resolution_result.v1",
        "status": "SOURCE_QUALIFIED" if source_qualified else "SOURCE_GAP__SELECTION_INELIGIBLE__NO_MANUAL_VERSION_SUBSTITUTION",
        "component_id": component["component_id"],
        "source_slots": [dict(row) for row in slots],
        "source_evidence": evidence,
        "controlling_pdf_identity_receipt": success_receipt,
        "pdf_parser_execution_boundary": "FRESH_PYTHON_PROCESS__I_AND_B_FLAGS__NO_IN_PROCESS_FALLBACK__NONHERMETIC_OS_STDLIB_TCB",
        "source_qualified": source_qualified,
        "author_code_direct_link_plan": direct_plan,
        "author_code_required_for_selection_eligibility": False,
        "manual_extra_search_or_source_substitution_allowed": False,
        "activity": {"network_calls": 0, "live_source_requests": 0, "manual_choices": 0, "candidate_decisions": 0},
        "authorization": {"live_search": False, "source_fetch": False, "candidate_work": False, "entropy": False, "selection": False},
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(
        result, seal_field="result_sha256", domain="rtdl.goal5793.x2.offline_source_resolution_result", version=1
    )
    return result
