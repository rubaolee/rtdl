#!/usr/bin/env python3
"""Pure offline reference machinery for Goal5793 X2.

This module deliberately has no network client.  It validates preserved or
strictly synthetic provider transcripts, normalizes and de-duplicates work
identities, applies the frozen exposure boundary, enumerates role triplets,
and implements the frozen length-framed NIST selection mapping.  Live search,
beacon access, candidate decisions, GPU work and timing are outside this file.
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_TRANSCRIPT = "rtdl.goal5793.x2.offline_provider_transcript.v1"
SCHEMA_SCIENCE_ROW = "rtdl.goal5793.x2.preentropy_science_row.v1"
S0_PROTOCOL_PATH = "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json"
S0_PROTOCOL_SHA256 = "126ee3c1dfe930a7bb25b2f19df8a6c4889c7ef8b619abe3cc69da54efa8b7c2"
X1_CLOSURE_PATH = "history/internal_docs/goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json"
X1_CLOSURE_SHA256 = "5fa675288edbc7c2ff400b9fb966b9de48183577a5e917c75b41a24f267c2ac1"

PROVIDER_ORDER = ("OpenAlex Works API", "arXiv API")
TERMS = (
    "ray tracing core",
    "ray tracing cores",
    "ray tracing unit",
    "ray tracing units",
    "ray tracing accelerator",
    "ray tracing accelerators",
    "hardware ray tracing",
    "DirectX Raytracing",
    "Vulkan ray tracing",
    "OptiX",
    "HIPRT",
)
RETRY_DELAYS = (0, 3, 6, 12, 24, 48)
OPENALEX_ENDPOINT = "https://api.openalex.org/works"
ARXIV_ENDPOINT = "https://export.arxiv.org/api/query"
OPENALEX_FILTER = "from_publication_date:2018-01-01,to_publication_date:2026-08-22"
ARXIV_DATE = "submittedDate:[201801010000 TO 202608222359]"

STRUCTURAL_AXES = (
    "geometry_family",
    "primitive_type",
    "ray_construction",
    "hit_policy",
    "multiplicity",
    "boundary_convention",
    "tie_break",
    "numeric_domain",
    "overflow_domain",
    "decode",
    "continuation",
    "composition",
    "ownership_epoch",
)
ROLE_B_AXES = ("geometry_family", "primitive_type", "continuation", "composition")
RISK_FLAGS = ("multiplicity", "tie_boundary", "continuation", "ownership_epoch", "global_composition")

# X2 freezes a finite categorical vocabulary.  A returned row that cannot be
# mapped without judgement remains visible but selection-ineligible.
STRUCTURAL_VOCABULARY: Mapping[str, tuple[str, ...]] = {
    "geometry_family": ("BUILTIN_TRIANGLE", "CUSTOM_AABB"),
    "primitive_type": (
        "TRIANGLE",
        "CUSTOM_AABB_POINT_OR_SPHERE",
        "CUSTOM_AABB_BOX_OR_INTERVAL",
        "CUSTOM_AABB_OTHER_EXACT_INTERSECTION",
    ),
    "ray_construction": (
        "ORIGIN_DIRECTION",
        "FINITE_SEGMENT",
        "AXIS_ALIGNED_INTERVAL",
        "QUERY_EMBEDDED_RANK_OR_KEY",
        "MESH_ORIENTATION_QUERY",
    ),
    "hit_policy": (
        "CLOSEST_HIT_OR_MISS",
        "ANY_HIT_ACCEPT_CONTINUE",
        "FIRST_ACCEPTED_HIT",
        "ALL_ACCEPTED_HITS",
        "CUSTOM_INTERSECTION_THEN_CLOSEST",
    ),
    "multiplicity": (
        "ZERO_OR_ONE",
        "EXACTLY_ONE",
        "SET",
        "MULTISET",
        "TOP_K",
        "CHECKED_SCALAR_REDUCTION",
        "BOUNDED_VECTOR_REDUCTION",
    ),
    "boundary_convention": (
        "OPEN",
        "CLOSED",
        "HALF_OPEN",
        "ORIENTED_TRIANGLE",
        "INCLUSIVE_AABB",
        "INTERIOR_CELL",
        "EXACT_INTEGER",
    ),
    "tie_break": (
        "NOT_APPLICABLE",
        "MIN_PRIMITIVE_ID",
        "MIN_KEY_THEN_ID",
        "LEFTMOST_INDEX",
        "LEXICOGRAPHIC_IDS",
        "STABLE_INPUT_ORDER",
    ),
    "numeric_domain": (
        "EXACT_U32",
        "EXACT_U64",
        "CHECKED_U32_TO_U64",
        "BINARY32_PINNED_GEOMETRY",
        "BINARY64_PINNED_GEOMETRY",
        "MIXED_INTEGER_BINARY32",
    ),
    "overflow_domain": (
        "NOT_APPLICABLE",
        "FAIL_CLOSED_CAPACITY",
        "FAIL_CLOSED_CHECKED_INTEGER",
        "FAIL_CLOSED_STATUS_BEFORE_OUTPUT",
    ),
    "decode": (
        "SCALAR",
        "PER_QUERY_VALUE",
        "ORDERED_VECTOR",
        "SET",
        "MULTISET",
        "TOP_K",
    ),
    "continuation": (
        "SINGLE_TRACE",
        "BOUNDED_STATIC_RETRACE",
        "DATA_DEPENDENT_RETRACE",
        "RECURSIVE_TRACE",
        "STOCHASTIC_PATH_CONTINUATION",
    ),
    "composition": (
        "INDEPENDENT_PER_QUERY",
        "COMMUTATIVE_CHECKED_REDUCTION",
        "ORDERED_REDUCTION",
        "GRAPH_OR_RELATION_CONSTRUCTION",
        "GLOBAL_ITERATIVE_COMPOSITION",
        "PATH_ACCUMULATION",
        "STOCHASTIC_TALLY",
    ),
    "ownership_epoch": (
        "STATIC_IMMUTABLE",
        "REFIT_OR_UPDATE_PER_EPOCH",
        "MUTABLE_SHARED_STATE",
        "STREAM_LOCAL_STATE",
    ),
}

SELECTION_DOMAIN = "rtdl.goal5793.triplet.selection.v1"
SELECTION_MAGIC = bytes.fromhex("5254444c3537393353454c0001")
SELECTION_FIELDS = (
    "domain",
    "s0_protocol_authority_file_sha256",
    "complete_source_rows_sha256",
    "x1_examiner_closure_file_sha256",
    "x2_harvester_entropy_closure_file_sha256",
    "x3_science_triplet_owner_closure_file_sha256",
    "expanded_append_only_row_table_file_sha256",
    "preentropy_science_projection_rows_sha256",
    "ordered_triplets_rows_sha256",
    "ordered_triplet_count",
    "anchor_chain_index",
    "anchor_pulse_index",
    "anchor_timestamp_ms",
    "anchor_certificate_id",
    "anchor_output_value",
    "target_chain_index",
    "target_pulse_index",
    "target_timestamp_ms",
    "target_certificate_id",
    "target_output_value",
    "counter",
)
SHA_FIELDS = {
    "s0_protocol_authority_file_sha256",
    "complete_source_rows_sha256",
    "x1_examiner_closure_file_sha256",
    "x2_harvester_entropy_closure_file_sha256",
    "x3_science_triplet_owner_closure_file_sha256",
    "expanded_append_only_row_table_file_sha256",
    "preentropy_science_projection_rows_sha256",
    "ordered_triplets_rows_sha256",
}
U64_FIELDS = {
    "ordered_triplet_count",
    "anchor_chain_index",
    "anchor_pulse_index",
    "anchor_timestamp_ms",
    "target_chain_index",
    "target_pulse_index",
    "target_timestamp_ms",
    "counter",
}
HEX512_FIELDS = {
    "anchor_certificate_id",
    "anchor_output_value",
    "target_certificate_id",
    "target_output_value",
}

FORBIDDEN_PRESELECTION_KEYS = {
    "actual_exam_outcome",
    "checker_verdict",
    "measured_performance",
    "selected_index",
    "selected_triplet",
    "candidate_implementation",
    "execution_receipt",
}


class X2Error(ValueError):
    """Stable fail-closed error with a machine-readable reason id."""

    def __init__(self, reason_id: str, detail: str = "") -> None:
        super().__init__(f"{reason_id}:{detail}" if detail else reason_id)
        self.reason_id = reason_id
        self.detail = detail


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _exact_keys(value: Mapping[str, Any], keys: Iterable[str], reason: str) -> None:
    if set(value) != set(keys):
        raise X2Error(reason)


def _plain_int(value: Any, reason: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        raise X2Error(reason)
    return value


def _nonempty_string(value: Any, reason: str) -> str:
    if not isinstance(value, str) or not value:
        raise X2Error(reason)
    return value


def _strict_hex(value: Any, count: int, reason: str, *, lowercase: bool = True) -> str:
    if not isinstance(value, str) or len(value) != count or re.fullmatch(r"[0-9A-Fa-f]+", value) is None:
        raise X2Error(reason)
    if lowercase and value != value.lower():
        raise X2Error(reason)
    return value.lower()


def normalize_doi(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise X2Error("IDENTITY_SCHEMA_INVALID__DOI")
    text = value.strip()
    text = re.sub(r"(?i)^doi:\s*", "", text, count=1)
    text = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", text, count=1)
    text = text.strip().lower()
    if not text or re.search(r"\s", text) or not text.startswith("10.") or "/" not in text:
        raise X2Error("IDENTITY_SCHEMA_INVALID__DOI")
    return text


def normalize_arxiv(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise X2Error("IDENTITY_SCHEMA_INVALID__ARXIV")
    text = value.strip().lower()
    text = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", text)
    text = re.sub(r"(?i)^arxiv:\s*", "", text)
    text = text.removesuffix(".pdf")
    text = re.sub(r"v[0-9]+$", "", text)
    if re.fullmatch(r"(?:[a-z-]+(?:\.[a-z-]+)?/\d{7}|\d{4}\.\d{4,5})", text) is None:
        raise X2Error("IDENTITY_SCHEMA_INVALID__ARXIV")
    return text


def normalize_openalex(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise X2Error("IDENTITY_SCHEMA_INVALID__OPENALEX")
    match = re.search(r"(?i)(?:^|/)(W[0-9]+)$", value.strip())
    if match is None:
        raise X2Error("IDENTITY_SCHEMA_INVALID__OPENALEX")
    return match.group(1).upper()


def normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        raise X2Error("IDENTITY_SCHEMA_INVALID__TEXT")
    text = html.unescape(value)
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ").replace("&", " and ")
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(ch if ch.isalnum() else " " for ch in text)
    return " ".join(text.split())


def normalize_author(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    if "," in str(value):
        family = normalize_text(str(value).split(",", 1)[0])
        return family.split()[-1] if family else ""
    return text.split()[-1]


def normalize_https_url(value: Any) -> str:
    if not isinstance(value, str) or not value or re.search(r"[\x00-\x20]", value):
        raise X2Error("SOURCE_URL_INVALID")
    match = re.fullmatch(r"(?i)https://([^/?#]+)([^#]*)?(?:#.*)?", value)
    if match is None:
        raise X2Error("SOURCE_URL_INVALID")
    authority, tail = match.group(1), match.group(2) or ""
    if "@" in authority or authority.startswith("[") or authority.count(":") > 1:
        raise X2Error("SOURCE_URL_INVALID")
    if ":" in authority:
        host, port = authority.rsplit(":", 1)
        if not port.isdigit() or not 1 <= int(port) <= 65535:
            raise X2Error("SOURCE_URL_INVALID")
        authority = host if port == "443" else f"{host}:{port}"
    authority = authority.lower()
    if not authority or authority.startswith(".") or authority.endswith(".") or ".." in authority:
        raise X2Error("SOURCE_URL_INVALID")
    return f"https://{authority}{tail}"


def _append_unique_url(rows: list[dict[str, str]], seen: set[str], kind: str, value: Any) -> None:
    if value is None or value == "":
        return
    url = normalize_https_url(value)
    if url not in seen:
        rows.append({"slot_kind": kind, "url": url})
        seen.add(url)


def _openalex_url_slots(work: Mapping[str, Any], normalized_doi: str | None, raw_arxiv: Any) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    source: list[dict[str, str]] = []
    direct: list[dict[str, str]] = []
    source_seen: set[str] = set()
    direct_seen: set[str] = set()
    if raw_arxiv:
        arxiv = normalize_arxiv(raw_arxiv)
        if arxiv is not None:
            _append_unique_url(source, source_seen, "ARXIV_PDF", f"https://arxiv.org/pdf/{arxiv}")
    for key, kind in (("primary_location", "OPENALEX_PRIMARY_OA_PDF"), ("best_oa_location", "OPENALEX_BEST_OA_PDF")):
        location = work.get(key)
        if isinstance(location, Mapping) and location.get("is_oa") is True:
            _append_unique_url(source, source_seen, kind, location.get("pdf_url"))
    remaining: list[str] = []
    locations = work.get("locations")
    if locations is not None and not isinstance(locations, list):
        raise X2Error("OPENALEX_LOCATIONS_SCHEMA_INVALID")
    for location in locations or []:
        if not isinstance(location, Mapping):
            raise X2Error("OPENALEX_LOCATIONS_SCHEMA_INVALID")
        if location.get("is_oa") is True and location.get("pdf_url"):
            remaining.append(normalize_https_url(location["pdf_url"]))
        for field in ("landing_page_url", "pdf_url"):
            _append_unique_url(direct, direct_seen, f"OPENALEX_LOCATION_{field.upper()}", location.get(field))
    for url in sorted(set(remaining), key=lambda item: item.encode("utf-8")):
        _append_unique_url(source, source_seen, "OPENALEX_REMAINING_OA_PDF", url)
    if normalized_doi is not None:
        _append_unique_url(source, source_seen, "DOI_ACCEPT_PDF", f"https://doi.org/{normalized_doi}")
    return source, direct


def fallback_sha256(title: str, first_author: str, year: int | str) -> str:
    if isinstance(year, str):
        if not year.isdigit():
            raise X2Error("IDENTITY_SCHEMA_INVALID__YEAR")
        year_value = int(year)
    else:
        year_value = _plain_int(year, "IDENTITY_SCHEMA_INVALID__YEAR", minimum=1000, maximum=9999)
    body = {
        "first_author": normalize_author(first_author),
        "title": normalize_text(title),
        "year": year_value,
    }
    return sha256_bytes(canonical_bytes(body))


def _title_tokens(text: str) -> tuple[str, ...]:
    return tuple(sorted(set(normalize_text(text).split())))


def _jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if a | b else 0.0


def build_exposure_alias_rows(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    entries = registry.get("bibliography_entries")
    if not isinstance(entries, list) or len(entries) != 186:
        raise X2Error("EXPOSURE_REGISTRY_ROW_SET_MISMATCH")
    rows: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise X2Error("EXPOSURE_REGISTRY_ROW_SCHEMA_MISMATCH")
        projection = entry.get("normalized_identity_projection")
        aliases = entry.get("aliases")
        if not isinstance(projection, Mapping) or not isinstance(aliases, list):
            raise X2Error("EXPOSURE_REGISTRY_ROW_SCHEMA_MISMATCH")
        strong: dict[str, list[str]] = {"doi": [], "arxiv": [], "openalex": []}
        fallback: list[str] = []
        for alias in aliases:
            if not isinstance(alias, Mapping) or not isinstance(alias.get("value"), str):
                raise X2Error("EXPOSURE_REGISTRY_ALIAS_SCHEMA_MISMATCH")
            kind, _, value = alias["value"].partition(":")
            if kind in strong:
                strong[kind].append(value)
            elif kind == "fallback_sha256":
                fallback.append(value)
        title = _nonempty_string(projection.get("title"), "EXPOSURE_REGISTRY_TITLE_MISSING")
        author = projection.get("first_author_family")
        year = projection.get("year")
        if isinstance(author, str) and author and isinstance(year, str) and year.isdigit():
            # The S0 protocol froze an unprefixed canonical-JSON SHA-256
            # fallback, while the predecessor X1 component used a separately
            # domain-separated identity.  Preserve both; do not silently
            # reinterpret the historical identity as the X2 protocol value.
            fallback.append(fallback_sha256(title, author, year))
        rows.append(
            {
                "citation_key": _nonempty_string(entry.get("citation_key"), "EXPOSURE_REGISTRY_CITATION_KEY_MISSING"),
                "title": title,
                "title_tokens": list(_title_tokens(title)),
                "first_author": author if isinstance(author, str) else "",
                "year": int(year) if isinstance(year, str) and year.isdigit() else None,
                "doi": sorted(set(strong["doi"])),
                "arxiv": sorted(set(strong["arxiv"])),
                "openalex": sorted(set(strong["openalex"])),
                "fallback_sha256": sorted(set(fallback)),
                "strong_identifier_present": bool(strong["doi"] or strong["arxiv"] or strong["openalex"]),
                "selection_eligible": False,
            }
        )
    rows.sort(key=lambda row: row["citation_key"].encode("utf-8"))
    if len({row["citation_key"] for row in rows}) != 186:
        raise X2Error("EXPOSURE_REGISTRY_CITATION_KEY_DUPLICATE")
    return rows


def _header_rows(value: Any, reason: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise X2Error(reason)
    rows: list[dict[str, str]] = []
    for row in value:
        if not isinstance(row, Mapping) or set(row) != {"name", "value"}:
            raise X2Error(reason)
        name, item = row["name"], row["value"]
        if not isinstance(name, str) or not name or not isinstance(item, str):
            raise X2Error(reason)
        rows.append({"name": name, "value": item})
    return rows


def _attempt_body(lineage: Mapping[str, Any], *, expected_url: str) -> tuple[bytes, list[dict[str, Any]]]:
    _exact_keys(lineage, ("request_sequence", "params", "attempts"), "TRANSCRIPT_LINEAGE_SCHEMA_MISMATCH")
    attempts = lineage["attempts"]
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= 6:
        raise X2Error("TRANSCRIPT_RETRY_COUNT_INVALID")
    evidence: list[dict[str, Any]] = []
    successful: bytes | None = None
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, Mapping):
            raise X2Error("TRANSCRIPT_ATTEMPT_SCHEMA_MISMATCH")
        _exact_keys(
            attempt,
            (
                "attempt",
                "scheduled_delay_seconds",
                "request_url",
                "request_headers",
                "request_started_at_utc",
                "status",
                "response_headers",
                "response_received_at_utc",
                "body_base64",
                "error",
            ),
            "TRANSCRIPT_ATTEMPT_SCHEMA_MISMATCH",
        )
        if _plain_int(attempt["attempt"], "TRANSCRIPT_ATTEMPT_ORDINAL_INVALID", minimum=1) != index + 1:
            raise X2Error("TRANSCRIPT_ATTEMPT_ORDINAL_INVALID")
        if attempt["scheduled_delay_seconds"] != RETRY_DELAYS[index]:
            raise X2Error("TRANSCRIPT_RETRY_SCHEDULE_DRIFT")
        if attempt["request_url"] != expected_url:
            raise X2Error("TRANSCRIPT_REQUEST_URL_DRIFT")
        request_headers = _header_rows(attempt["request_headers"], "TRANSCRIPT_REQUEST_HEADERS_INVALID")
        response_headers = _header_rows(attempt["response_headers"], "TRANSCRIPT_RESPONSE_HEADERS_INVALID")
        request_started_ms = parse_timestamp_ms(attempt["request_started_at_utc"])
        response_received_ms = parse_timestamp_ms(attempt["response_received_at_utc"])
        if response_received_ms < request_started_ms:
            raise X2Error("TRANSCRIPT_RESPONSE_BEFORE_REQUEST")
        if evidence and request_started_ms < evidence[-1]["response_received_ms"] + RETRY_DELAYS[index] * 1000:
            raise X2Error("TRANSCRIPT_RETRY_STARTED_TOO_EARLY")
        status = attempt["status"]
        if status is not None:
            _plain_int(status, "TRANSCRIPT_HTTP_STATUS_INVALID", minimum=100, maximum=599)
        try:
            body = base64.b64decode(attempt["body_base64"], validate=True)
        except Exception as exc:  # noqa: BLE001 - stable fail-closed boundary
            raise X2Error("TRANSCRIPT_BODY_BASE64_INVALID") from exc
        error = attempt["error"]
        if error is not None and (not isinstance(error, str) or not error):
            raise X2Error("TRANSCRIPT_ERROR_FIELD_INVALID")
        ok = status == 200 and error is None
        evidence.append(
            {
                "attempt": index + 1,
                "status": status,
                "error": error,
                "request_url": expected_url,
                "request_headers": request_headers,
                "request_started_ms": request_started_ms,
                "response_headers": response_headers,
                "response_received_ms": response_received_ms,
                "body_bytes": len(body),
                "body_sha256": sha256_bytes(body),
            }
        )
        if ok:
            if index != len(attempts) - 1:
                raise X2Error("TRANSCRIPT_ATTEMPTS_AFTER_SUCCESS")
            successful = body
        elif index == len(attempts) - 1 and len(attempts) < 6:
            raise X2Error("TRANSCRIPT_PREMATURE_RETRY_STOP")
    if successful is None:
        raise X2Error("INFRA_INVALID__NO_PARTIAL_UNIVERSE__EXHAUSTED_RETRY")
    return successful, evidence


def _openalex_params(term: str, cursor: str) -> dict[str, Any]:
    return {"cursor": cursor, "filter": OPENALEX_FILTER, "per-page": 200, "search": term}


def _arxiv_params(term: str, start: int) -> dict[str, Any]:
    return {
        "max_results": 500,
        "search_query": f'{ARXIV_DATE} AND all:"{term}"',
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
        "start": start,
    }


def _node(
    *,
    provider: str,
    term: str,
    query_index: int,
    page_index: int,
    ordinal: int,
    record: Mapping[str, Any],
    doi: Any,
    arxiv: Any,
    openalex: Any,
    title: Any,
    first_author: Any,
    year: Any,
    source_url_slots: Sequence[Mapping[str, str]],
    direct_link_slots: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    title_string = _nonempty_string(title, "PROVIDER_RECORD_TITLE_MISSING")
    author_string = _nonempty_string(first_author, "PROVIDER_RECORD_FIRST_AUTHOR_MISSING")
    year_int = _plain_int(year, "PROVIDER_RECORD_YEAR_INVALID", minimum=1000, maximum=9999)
    normalized = {
        "doi": normalize_doi(doi),
        "arxiv": normalize_arxiv(arxiv),
        "openalex": normalize_openalex(openalex),
        "title": normalize_text(title_string),
        "first_author": normalize_author(author_string),
        "year": year_int,
    }
    normalized["fallback_sha256"] = fallback_sha256(title_string, author_string, year_int)
    identity = {
        "provider": provider,
        "term": term,
        "query_index": query_index,
        "page_index": page_index,
        "ordinal": ordinal,
        "record_sha256": sha256_bytes(canonical_bytes(record)),
    }
    return {
        "node_id": f"raw_node_sha256:{sha256_bytes(canonical_bytes(identity))}",
        **identity,
        **normalized,
        "raw_title": title_string,
        "raw_first_author": author_string,
        "source_url_slots": [dict(row) for row in source_url_slots],
        "direct_link_slots": [dict(row) for row in direct_link_slots],
    }


def _parse_openalex(body: bytes, *, term: str, query_index: int, page_index: int) -> tuple[list[dict[str, Any]], str | None]:
    try:
        data = json.loads(body)
    except Exception as exc:  # noqa: BLE001
        raise X2Error("OPENALEX_RESPONSE_JSON_INVALID") from exc
    if not isinstance(data, Mapping) or not isinstance(data.get("meta"), Mapping) or not isinstance(data.get("results"), list):
        raise X2Error("OPENALEX_RESPONSE_SCHEMA_INVALID")
    next_cursor = data["meta"].get("next_cursor")
    if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor):
        raise X2Error("OPENALEX_CURSOR_INVALID")
    nodes: list[dict[str, Any]] = []
    for ordinal, work in enumerate(data["results"]):
        if not isinstance(work, Mapping):
            raise X2Error("OPENALEX_WORK_SCHEMA_INVALID")
        authorships = work.get("authorships")
        if not isinstance(authorships, list) or not authorships or not isinstance(authorships[0], Mapping):
            raise X2Error("OPENALEX_FIRST_AUTHOR_MISSING")
        author = authorships[0].get("author")
        if not isinstance(author, Mapping):
            raise X2Error("OPENALEX_FIRST_AUTHOR_MISSING")
        ids = work.get("ids") if isinstance(work.get("ids"), Mapping) else {}
        normalized_doi = normalize_doi(work.get("doi") or ids.get("doi"))
        source_slots, direct_slots = _openalex_url_slots(work, normalized_doi, ids.get("arxiv"))
        nodes.append(
            _node(
                provider="OpenAlex Works API",
                term=term,
                query_index=query_index,
                page_index=page_index,
                ordinal=ordinal,
                record=work,
                doi=normalized_doi,
                arxiv=ids.get("arxiv"),
                openalex=work.get("id") or ids.get("openalex"),
                title=work.get("title"),
                first_author=author.get("display_name"),
                year=work.get("publication_year"),
                source_url_slots=source_slots,
                direct_link_slots=direct_slots,
            )
        )
    return nodes, next_cursor


def _xml_text(element: ET.Element, suffix: str) -> str | None:
    found = element.find(f"{{*}}{suffix}")
    return found.text.strip() if found is not None and found.text else None


def _parse_arxiv(body: bytes, *, term: str, query_index: int, page_index: int) -> tuple[list[dict[str, Any]], int]:
    try:
        root = ET.fromstring(body)
    except Exception as exc:  # noqa: BLE001
        raise X2Error("ARXIV_RESPONSE_XML_INVALID") from exc
    total_text = _xml_text(root, "totalResults")
    if total_text is None or not total_text.isdigit():
        raise X2Error("ARXIV_TOTAL_RESULTS_INVALID")
    total = int(total_text)
    entries = root.findall("{*}entry")
    nodes: list[dict[str, Any]] = []
    for ordinal, entry in enumerate(entries):
        title = _xml_text(entry, "title")
        identifier = _xml_text(entry, "id")
        published = _xml_text(entry, "published")
        author_element = entry.find("{*}author")
        author = _xml_text(author_element, "name") if author_element is not None else None
        doi = _xml_text(entry, "doi")
        normalized_arxiv = normalize_arxiv(identifier)
        source_slots: list[dict[str, str]] = []
        source_seen: set[str] = set()
        if normalized_arxiv is not None:
            _append_unique_url(source_slots, source_seen, "ARXIV_PDF", f"https://arxiv.org/pdf/{normalized_arxiv}")
        normalized_doi = normalize_doi(doi)
        if normalized_doi is not None:
            _append_unique_url(source_slots, source_seen, "DOI_ACCEPT_PDF", f"https://doi.org/{normalized_doi}")
        direct_slots: list[dict[str, str]] = []
        direct_seen: set[str] = set()
        for link in entry.findall("{*}link"):
            _append_unique_url(direct_slots, direct_seen, "ARXIV_METADATA_LINK", link.get("href"))
        if published is None or re.match(r"^[0-9]{4}-", published) is None:
            raise X2Error("ARXIV_PUBLISHED_YEAR_INVALID")
        record_projection = {
            "id": identifier,
            "title": title,
            "author": author,
            "published": published,
            "doi": doi,
        }
        nodes.append(
            _node(
                provider="arXiv API",
                term=term,
                query_index=query_index,
                page_index=page_index,
                ordinal=ordinal,
                record=record_projection,
                doi=normalized_doi,
                arxiv=identifier,
                openalex=None,
                title=title,
                first_author=author,
                year=int(published[:4]),
                source_url_slots=source_slots,
                direct_link_slots=direct_slots,
            )
        )
    return nodes, total


def validate_offline_transcript(transcript: Mapping[str, Any]) -> dict[str, Any]:
    _exact_keys(
        transcript,
        ("schema", "mode", "synthetic_fixture", "network_call_count", "worker_count", "concurrent_requests", "queries"),
        "TRANSCRIPT_TOP_LEVEL_SCHEMA_MISMATCH",
    )
    if transcript["schema"] != SCHEMA_TRANSCRIPT or transcript["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY":
        raise X2Error("TRANSCRIPT_MODE_INVALID")
    if transcript["synthetic_fixture"] is not True or transcript["network_call_count"] != 0:
        raise X2Error("LIVE_PROVIDER_CALL_FORBIDDEN_IN_X2")
    if transcript["worker_count"] != 1 or transcript["concurrent_requests"] is not False:
        raise X2Error("GLOBAL_QUERY_EXECUTION_NOT_SINGLE_THREADED")
    queries = transcript["queries"]
    expected = [(provider, term) for provider in PROVIDER_ORDER for term in TERMS]
    if not isinstance(queries, list) or len(queries) != len(expected):
        raise X2Error("GLOBAL_QUERY_SCHEDULE_MISMATCH")
    all_nodes: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    seen_body_hashes: set[tuple[int, str]] = set()
    last_global_response_ms: int | None = None
    last_arxiv_response_ms: int | None = None
    for query_index, (query, expected_pair) in enumerate(zip(queries, expected, strict=True)):
        if not isinstance(query, Mapping):
            raise X2Error("TRANSCRIPT_QUERY_SCHEMA_MISMATCH")
        _exact_keys(query, ("provider", "term", "request_lineages"), "TRANSCRIPT_QUERY_SCHEMA_MISMATCH")
        provider, term = expected_pair
        if (query["provider"], query["term"]) != expected_pair:
            raise X2Error("GLOBAL_QUERY_SCHEDULE_MISMATCH")
        lineages = query["request_lineages"]
        if not isinstance(lineages, list) or not lineages:
            raise X2Error("TRANSCRIPT_QUERY_HAS_NO_PAGE")
        cursor: str | None = "*" if provider == "OpenAlex Works API" else None
        arxiv_start = 0
        arxiv_total: int | None = None
        for page_index, lineage in enumerate(lineages):
            if not isinstance(lineage, Mapping):
                raise X2Error("TRANSCRIPT_LINEAGE_SCHEMA_MISMATCH")
            sequence = _plain_int(lineage.get("request_sequence"), "TRANSCRIPT_REQUEST_SEQUENCE_INVALID")
            if sequence != page_index:
                raise X2Error("TRANSCRIPT_REQUEST_SEQUENCE_INVALID")
            expected_params = _openalex_params(term, cursor or "") if provider == "OpenAlex Works API" else _arxiv_params(term, arxiv_start)
            if lineage.get("params") != expected_params:
                raise X2Error("TRANSCRIPT_REQUEST_PARAMETERS_DRIFT")
            expected_url = OPENALEX_ENDPOINT if provider == "OpenAlex Works API" else ARXIV_ENDPOINT
            body, attempts = _attempt_body(lineage, expected_url=expected_url)
            for attempt in attempts:
                if last_global_response_ms is not None and attempt["request_started_ms"] < last_global_response_ms:
                    raise X2Error("GLOBAL_QUERY_REQUEST_OVERLAP_OR_REORDER")
                if provider == "arXiv API" and last_arxiv_response_ms is not None and attempt["request_started_ms"] < last_arxiv_response_ms + 3000:
                    raise X2Error("ARXIV_INTER_REQUEST_DELAY_TOO_SHORT")
                last_global_response_ms = attempt["response_received_ms"]
                if provider == "arXiv API":
                    last_arxiv_response_ms = attempt["response_received_ms"]
            body_hash = sha256_bytes(body)
            body_identity = (query_index, body_hash)
            if body_identity in seen_body_hashes:
                raise X2Error("TRANSCRIPT_DUPLICATE_PAGE_BODY")
            seen_body_hashes.add(body_identity)
            responses.append(
                {
                    "provider": provider,
                    "term": term,
                    "query_index": query_index,
                    "page_index": page_index,
                    "body_bytes": len(body),
                    "body_sha256": body_hash,
                    "attempts": attempts,
                }
            )
            if provider == "OpenAlex Works API":
                nodes, next_cursor = _parse_openalex(body, term=term, query_index=query_index, page_index=page_index)
                all_nodes.extend(nodes)
                if next_cursor is None:
                    if page_index != len(lineages) - 1:
                        raise X2Error("OPENALEX_PAGES_AFTER_TERMINAL_CURSOR")
                    cursor = None
                else:
                    if next_cursor == cursor:
                        raise X2Error("OPENALEX_REPEATED_CURSOR_OR_NO_PROGRESS")
                    cursor = next_cursor
            else:
                nodes, total = _parse_arxiv(body, term=term, query_index=query_index, page_index=page_index)
                if arxiv_total is None:
                    arxiv_total = total
                elif total != arxiv_total:
                    raise X2Error("ARXIV_TOTAL_RESULTS_CHANGED")
                if not nodes and arxiv_start < total:
                    raise X2Error("ARXIV_ZERO_ENTRIES_BEFORE_TOTAL")
                all_nodes.extend(nodes)
                arxiv_start += len(nodes)
                if arxiv_start >= total:
                    if page_index != len(lineages) - 1:
                        raise X2Error("ARXIV_PAGES_AFTER_TOTAL")
                elif page_index == len(lineages) - 1:
                    raise X2Error("ARXIV_INCOMPLETE_PAGINATION")
        if provider == "OpenAlex Works API" and cursor is not None:
            raise X2Error("OPENALEX_INCOMPLETE_PAGINATION")
    if len({node["node_id"] for node in all_nodes}) != len(all_nodes):
        raise X2Error("RAW_NODE_ID_DUPLICATE")
    return {
        "raw_nodes": sorted(all_nodes, key=lambda row: row["node_id"].encode("utf-8")),
        "response_evidence": responses,
        "query_count": len(queries),
        "raw_node_count": len(all_nodes),
        "network_call_count": 0,
    }


class _UnionFind:
    def __init__(self, keys: Sequence[str]) -> None:
        self.parent = {key: key for key in keys}

    def find(self, key: str) -> str:
        root = key
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[key] != key:
            parent = self.parent[key]
            self.parent[key] = root
            key = parent
        return root

    def union(self, left: str, right: str) -> None:
        a, b = self.find(left), self.find(right)
        if a == b:
            return
        low, high = sorted((a, b), key=lambda value: value.encode("utf-8"))
        self.parent[high] = low


def _component_exposure_matches(component: Mapping[str, Any], exposure_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    dois, arxivs, openalex_ids = set(component["doi"]), set(component["arxiv"]), set(component["openalex"])
    fallbacks = set(component["fallback_sha256"])
    titles = set(component["title"])
    authors = set(component["first_author"])
    years = set(component["year"])
    component_token_sets = [tuple(tokens) for tokens in component["title_tokens"]]
    for exposure in exposure_rows:
        reason: str | None = None
        if dois & set(exposure["doi"]) or arxivs & set(exposure["arxiv"]) or openalex_ids & set(exposure["openalex"]):
            reason = "PREEXISTING_EXPOSURE_STRONG_IDENTIFIER_MATCH"
        elif fallbacks & set(exposure["fallback_sha256"]):
            reason = "PREEXISTING_EXPOSURE_EXACT_FALLBACK_MATCH"
        elif exposure["title"] in titles and (exposure["year"] in years or exposure["year"] is None):
            reason = "PREEXISTING_EXPOSURE_EXACT_NORMALIZED_TITLE_MATCH"
        elif exposure["first_author"] in authors and exposure["year"] in years:
            reference_tokens = tuple(exposure["title_tokens"])
            for candidate_tokens in component_token_sets:
                overlap = _jaccard(candidate_tokens, reference_tokens)
                containment = bool(reference_tokens) and set(reference_tokens).issubset(set(candidate_tokens))
                if overlap >= 0.90 or (containment and len(reference_tokens) >= 4):
                    reason = "PREEXISTING_EXPOSURE_CONSERVATIVE_TITLE_AUTHOR_YEAR_MATCH"
                    break
        if reason is not None:
            matches.append({"citation_key": exposure["citation_key"], "reason": reason})
    return sorted(matches, key=lambda row: (row["citation_key"].encode("utf-8"), row["reason"]))


def build_identity_components(raw_nodes: Sequence[Mapping[str, Any]], exposure_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    nodes = sorted(raw_nodes, key=lambda row: str(row.get("node_id", "")).encode("utf-8"))
    ids = [_nonempty_string(node.get("node_id"), "RAW_NODE_ID_INVALID") for node in nodes]
    if len(set(ids)) != len(ids):
        raise X2Error("RAW_NODE_ID_DUPLICATE")
    uf = _UnionFind(ids)
    for field in ("doi", "arxiv", "openalex"):
        groups: dict[str, list[str]] = {}
        for node in nodes:
            value = node.get(field)
            if value is not None:
                groups.setdefault(_nonempty_string(value, "RAW_NODE_IDENTITY_INVALID"), []).append(node["node_id"])
        for group in groups.values():
            first = min(group, key=lambda value: value.encode("utf-8"))
            for other in group:
                uf.union(first, other)
    members: dict[str, list[Mapping[str, Any]]] = {}
    for node in nodes:
        members.setdefault(uf.find(node["node_id"]), []).append(node)
    interim: list[dict[str, Any]] = []
    source_priority = {
        "ARXIV_PDF": 0,
        "OPENALEX_PRIMARY_OA_PDF": 1,
        "OPENALEX_BEST_OA_PDF": 2,
        "OPENALEX_REMAINING_OA_PDF": 3,
        "DOI_ACCEPT_PDF": 4,
    }
    for group in members.values():
        values = lambda field: sorted({node[field] for node in group if node.get(field) is not None})
        dois, arxivs, openalex_ids = values("doi"), values("arxiv"), values("openalex")
        conflict = len(dois) > 1 or len(arxivs) > 1 or len(openalex_ids) > 1
        if dois:
            representative = "doi:" + dois[0]
        elif arxivs:
            representative = "arxiv:" + arxivs[0]
        elif openalex_ids:
            representative = "openalex:" + openalex_ids[0]
        else:
            representative = "fallback_sha256:" + values("fallback_sha256")[0]
        source_rows: list[dict[str, str]] = []
        direct_rows: list[dict[str, str]] = []
        source_seen: set[str] = set()
        direct_seen: set[str] = set()
        for node in sorted(group, key=lambda item: item["node_id"].encode("utf-8")):
            for row in node.get("source_url_slots", []):
                if not isinstance(row, Mapping) or set(row) != {"slot_kind", "url"} or row["slot_kind"] not in source_priority:
                    raise X2Error("SOURCE_URL_SLOT_SCHEMA_INVALID")
                url = normalize_https_url(row["url"])
                if url not in source_seen:
                    source_rows.append({"slot_kind": row["slot_kind"], "url": url})
                    source_seen.add(url)
            for row in node.get("direct_link_slots", []):
                if not isinstance(row, Mapping) or set(row) != {"slot_kind", "url"}:
                    raise X2Error("DIRECT_LINK_SLOT_SCHEMA_INVALID")
                url = normalize_https_url(row["url"])
                if url not in direct_seen:
                    direct_rows.append({"slot_kind": row["slot_kind"], "url": url})
                    direct_seen.add(url)
        source_rows.sort(key=lambda row: (source_priority[row["slot_kind"]], row["url"].encode("utf-8")))
        interim.append(
            {
                "component_id": representative,
                "member_node_ids": sorted(node["node_id"] for node in group),
                "doi": dois,
                "arxiv": arxivs,
                "openalex": openalex_ids,
                "fallback_sha256": values("fallback_sha256"),
                "title": values("title"),
                "title_tokens": sorted({tuple(_title_tokens(node["title"])) for node in group}),
                "first_author": values("first_author"),
                "year": values("year"),
                "source_url_slots": source_rows,
                "direct_link_slots": direct_rows,
                "identity_conflict": conflict,
                "fallback_identity_ambiguous": False,
            }
        )
    fallback_to_components: dict[str, list[int]] = {}
    for index, component in enumerate(interim):
        for value in component["fallback_sha256"]:
            fallback_to_components.setdefault(value, []).append(index)
    for indexes in fallback_to_components.values():
        if len(set(indexes)) > 1:
            for index in indexes:
                interim[index]["fallback_identity_ambiguous"] = True
    for component in interim:
        matches = _component_exposure_matches(component, exposure_rows)
        component["exposure_matches"] = matches
        if component["identity_conflict"]:
            disposition = "IDENTITY_CONFLICT__SELECTION_INELIGIBLE"
        elif component["fallback_identity_ambiguous"]:
            disposition = "FALLBACK_IDENTITY_AMBIGUOUS__SELECTION_INELIGIBLE"
        elif matches:
            disposition = "PREEXISTING_PROJECT_EXPOSURE__SELECTION_INELIGIBLE"
        else:
            disposition = "NOT_MATCHED_TO_FROZEN_DECLARED_EXPOSURE__NOT_YET_SCIENCE_ELIGIBLE"
        component["identity_disposition"] = disposition
        component["identity_stage_selection_eligible"] = disposition.endswith("NOT_YET_SCIENCE_ELIGIBLE")
    return sorted(interim, key=lambda row: row["component_id"].encode("utf-8"))


def _scan_forbidden_keys(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in FORBIDDEN_PRESELECTION_KEYS:
                raise X2Error("PRESELECTION_OUTCOME_LEAKAGE", ".".join(path + (key,)))
            _scan_forbidden_keys(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden_keys(child, path + (str(index),))


def validate_science_row(row: Mapping[str, Any], positive_vectors: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    _scan_forbidden_keys(row)
    required = {
        "schema",
        "candidate_id",
        "canonical_work_identity",
        "normalized_problem_family",
        "source_basis_exact",
        "oracle_exact",
        "stock_rt",
        "existing_registered_family",
        "expected_disposition",
        "public_admit_compile_run_reachable",
        "no_core_change_predicted",
        "structural_vector",
        "risk_flags",
        "identity_stage_selection_eligible",
    }
    _exact_keys(row, required, "SCIENCE_ROW_SCHEMA_MISMATCH")
    if row["schema"] != SCHEMA_SCIENCE_ROW:
        raise X2Error("SCIENCE_ROW_SCHEMA_MISMATCH")
    candidate_id = _nonempty_string(row["candidate_id"], "SCIENCE_ROW_CANDIDATE_ID_INVALID")
    work_identity = _nonempty_string(row["canonical_work_identity"], "SCIENCE_ROW_WORK_ID_INVALID")
    problem_family = _nonempty_string(row["normalized_problem_family"], "SCIENCE_ROW_PROBLEM_FAMILY_INVALID")
    vector = row["structural_vector"]
    flags = row["risk_flags"]
    if not isinstance(vector, Mapping) or set(vector) != set(STRUCTURAL_AXES):
        raise X2Error("SCIENCE_ROW_STRUCTURAL_VECTOR_SCHEMA_MISMATCH")
    if not isinstance(flags, Mapping) or set(flags) != set(RISK_FLAGS) or any(type(value) is not bool for value in flags.values()):
        raise X2Error("SCIENCE_ROW_RISK_VECTOR_SCHEMA_MISMATCH")
    for axis in STRUCTURAL_AXES:
        if vector[axis] not in STRUCTURAL_VOCABULARY[axis]:
            raise X2Error("SCIENCE_ROW_UNMAPPED_STRUCTURAL_VALUE", axis)
    if row["expected_disposition"] not in ("COMPATIBLE", "UNKNOWN", "INCOMPATIBLE"):
        raise X2Error("SCIENCE_ROW_EXPECTED_DISPOSITION_INVALID")
    bool_fields = (
        "source_basis_exact",
        "oracle_exact",
        "stock_rt",
        "existing_registered_family",
        "public_admit_compile_run_reachable",
        "no_core_change_predicted",
        "identity_stage_selection_eligible",
    )
    if any(type(row[field]) is not bool for field in bool_fields):
        raise X2Error("SCIENCE_ROW_BOOL_ALIAS_INVALID")
    if not positive_vectors:
        raise X2Error("INFRA_INVALID__ROLE_DIVERSITY_UNDEFINED")
    normalized_positives: list[Mapping[str, Any]] = []
    for positive in positive_vectors:
        if not isinstance(positive, Mapping) or set(positive) != set(STRUCTURAL_AXES):
            raise X2Error("POSITIVE_VECTOR_SCHEMA_MISMATCH")
        normalized_positives.append(positive)
    base = row["identity_stage_selection_eligible"] and row["source_basis_exact"] and row["stock_rt"]
    differs_all = all(any(vector[axis] != positive[axis] for axis in STRUCTURAL_AXES) for positive in normalized_positives)
    differs_b_all = all(any(vector[axis] != positive[axis] for axis in ROLE_B_AXES) for positive in normalized_positives)
    role_a = bool(
        base
        and row["oracle_exact"]
        and row["existing_registered_family"]
        and row["expected_disposition"] == "COMPATIBLE"
        and row["public_admit_compile_run_reachable"]
        and row["no_core_change_predicted"]
        and differs_all
    )
    role_b = bool(base and differs_b_all)
    role_c = bool(base and any(flags.values()))
    return {
        "candidate_id": candidate_id,
        "canonical_work_identity": work_identity,
        "normalized_problem_family": problem_family,
        "role_A": role_a,
        "role_B": role_b,
        "role_C": role_c,
        "expected_disposition": row["expected_disposition"],
        "structural_vector": dict(vector),
        "risk_flags": dict(flags),
    }


def enumerate_ordered_triplets(rows: Sequence[Mapping[str, Any]]) -> list[list[str]]:
    validated = list(rows)
    if len({row["candidate_id"] for row in validated}) != len(validated):
        raise X2Error("TRIPLET_CANDIDATE_ID_DUPLICATE")
    a_rows = sorted((row for row in validated if row["role_A"]), key=lambda row: row["candidate_id"].encode("utf-8"))
    b_rows = sorted((row for row in validated if row["role_B"]), key=lambda row: row["candidate_id"].encode("utf-8"))
    c_rows = sorted((row for row in validated if row["role_C"]), key=lambda row: row["candidate_id"].encode("utf-8"))
    triples: list[tuple[str, str, str]] = []
    for a in a_rows:
        for b in b_rows:
            for c in c_rows:
                selected = (a, b, c)
                if len({row["candidate_id"] for row in selected}) != 3:
                    continue
                if len({row["canonical_work_identity"] for row in selected}) != 3:
                    continue
                if len({row["normalized_problem_family"] for row in selected}) != 3:
                    continue
                triples.append(tuple(row["candidate_id"] for row in selected))
    triples.sort(key=lambda triple: tuple(value.encode("utf-8") for value in triple))
    return [list(triple) for triple in triples]


def _selection_value(name: str, value: Any) -> bytes:
    if name == "domain":
        if value != SELECTION_DOMAIN:
            raise X2Error("ENTROPY_DOMAIN_OR_TARGET_MISMATCH")
        return value.encode("utf-8")
    if name in SHA_FIELDS:
        return bytes.fromhex(_strict_hex(value, 64, "SELECTION_SHA256_FIELD_INVALID"))
    if name in HEX512_FIELDS:
        return bytes.fromhex(_strict_hex(value, 128, "SELECTION_512_FIELD_INVALID", lowercase=False))
    if name in U64_FIELDS:
        integer = _plain_int(value, "SELECTION_U64_FIELD_INVALID", maximum=2**64 - 1)
        return integer.to_bytes(8, "big")
    raise X2Error("SELECTION_UNKNOWN_FIELD")


def build_selection_frame(inputs: Mapping[str, Any]) -> bytes:
    if set(inputs) != set(SELECTION_FIELDS):
        raise X2Error("SELECTION_FIELD_SET_MISMATCH")
    framed: list[bytes] = []
    for name in SELECTION_FIELDS:
        name_bytes = name.encode("ascii")
        value_bytes = _selection_value(name, inputs[name])
        framed.append(len(name_bytes).to_bytes(2, "big") + name_bytes + len(value_bytes).to_bytes(8, "big") + value_bytes)
    return SELECTION_MAGIC + len(SELECTION_FIELDS).to_bytes(2, "big") + b"".join(framed)


def select_index(
    base_inputs: Mapping[str, Any],
    n: int,
    *,
    synthetic_digest_sequence: Sequence[str] | None = None,
    counter_start: int = 0,
) -> dict[str, Any]:
    n_value = _plain_int(n, "SELECTION_CARDINALITY_INVALID", maximum=2**64 - 1)
    if n_value == 0:
        return {
            "selected_index": None,
            "hash_evaluation_count": 0,
            "beacon_request_count": 0,
            "terminal": "TERMINAL_NEGATIVE__NO_BEACON_REQUEST__NO_HASH__NO_SELECTION__NO_RESCUE",
            "evaluations": [],
        }
    if set(base_inputs) != set(SELECTION_FIELDS) - {"counter"}:
        raise X2Error("SELECTION_BASE_FIELD_SET_MISMATCH")
    counter = _plain_int(counter_start, "SELECTION_COUNTER_INVALID", maximum=2**64 - 1)
    limit = (2**256 // n_value) * n_value
    evaluations: list[dict[str, Any]] = []
    sequence = list(synthetic_digest_sequence) if synthetic_digest_sequence is not None else None
    while True:
        inputs = dict(base_inputs)
        inputs["counter"] = counter
        frame = build_selection_frame(inputs)
        if sequence is not None:
            if not sequence:
                raise X2Error("SYNTHETIC_DIGEST_SEQUENCE_EXHAUSTED")
            digest_hex = _strict_hex(sequence.pop(0), 64, "SYNTHETIC_DIGEST_INVALID", lowercase=False)
            digest = bytes.fromhex(digest_hex)
        else:
            digest = hashlib.sha256(frame).digest()
            digest_hex = digest.hex()
        x = int.from_bytes(digest, "big")
        accepted = n_value == 1 or x < limit
        evaluations.append(
            {
                "counter": counter,
                "frame_bytes": len(frame),
                "frame_sha256": sha256_bytes(frame),
                "digest": digest_hex,
                "x_decimal": str(x),
                "accepted": accepted,
            }
        )
        if accepted:
            return {
                "selected_index": 0 if n_value == 1 else x % n_value,
                "hash_evaluation_count": len(evaluations),
                "beacon_request_count": 0,
                "terminal": None,
                "threshold_hex": f"{limit:064x}",
                "evaluations": evaluations,
            }
        if counter == 2**64 - 1:
            return {
                "selected_index": None,
                "hash_evaluation_count": len(evaluations),
                "beacon_request_count": 0,
                "terminal": "TERMINAL_INFRASTRUCTURE_FAILURE__NO_FALLBACK",
                "threshold_hex": f"{limit:064x}",
                "evaluations": evaluations,
            }
        counter += 1


def parse_timestamp_ms(value: Any) -> int:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z", value) is None:
        raise X2Error("NIST_TIMESTAMP_SCHEMA_INVALID")
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise X2Error("NIST_TIMESTAMP_SCHEMA_INVALID") from exc
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = dt - epoch
    return delta.days * 86_400_000 + delta.seconds * 1000 + delta.microseconds // 1000


def validate_pulse_structure(response: Mapping[str, Any]) -> dict[str, Any]:
    _exact_keys(response, ("pulse",), "NIST_RESPONSE_TOP_LEVEL_SCHEMA_INVALID")
    pulse = response["pulse"]
    required = (
        "uri",
        "version",
        "cipherSuite",
        "period",
        "certificateId",
        "chainIndex",
        "pulseIndex",
        "timeStamp",
        "localRandomValue",
        "external",
        "listValues",
        "precommitmentValue",
        "statusCode",
        "signatureValue",
        "outputValue",
    )
    if not isinstance(pulse, Mapping):
        raise X2Error("NIST_PULSE_SCHEMA_INVALID")
    _exact_keys(pulse, required, "NIST_PULSE_SCHEMA_INVALID")
    if pulse["version"] != "2.0" or pulse["cipherSuite"] != 0 or pulse["period"] != 60000 or pulse["statusCode"] != 0:
        raise X2Error("NIST_PULSE_FIXED_FIELD_MISMATCH")
    external = pulse["external"]
    if not isinstance(external, Mapping):
        raise X2Error("NIST_EXTERNAL_SCHEMA_INVALID")
    _exact_keys(external, ("sourceId", "statusCode", "value"), "NIST_EXTERNAL_SCHEMA_INVALID")
    if external["statusCode"] != 0:
        raise X2Error("NIST_EXTERNAL_STATUS_INVALID")
    for value in (
        pulse["certificateId"],
        pulse["localRandomValue"],
        external["sourceId"],
        external["value"],
        pulse["precommitmentValue"],
        pulse["outputValue"],
    ):
        _strict_hex(value, 128, "NIST_512_FIELD_INVALID", lowercase=False)
    _nonempty_string(pulse["signatureValue"], "NIST_SIGNATURE_FIELD_INVALID")
    chain = _plain_int(pulse["chainIndex"], "NIST_CHAIN_INDEX_INVALID", maximum=2**64 - 1)
    index = _plain_int(pulse["pulseIndex"], "NIST_PULSE_INDEX_INVALID", maximum=2**64 - 1)
    timestamp_ms = parse_timestamp_ms(pulse["timeStamp"])
    values = pulse["listValues"]
    if not isinstance(values, list):
        raise X2Error("NIST_LIST_VALUES_SCHEMA_INVALID")
    normalized_values: list[dict[str, str]] = []
    for item in values:
        if not isinstance(item, Mapping):
            raise X2Error("NIST_LIST_VALUE_SCHEMA_INVALID")
        _exact_keys(item, ("uri", "type", "value"), "NIST_LIST_VALUE_SCHEMA_INVALID")
        normalized_values.append(
            {
                "uri": _nonempty_string(item["uri"], "NIST_LIST_VALUE_URI_INVALID"),
                "type": _nonempty_string(item["type"], "NIST_LIST_VALUE_TYPE_INVALID"),
                "value": _strict_hex(item["value"], 128, "NIST_LIST_VALUE_HEX_INVALID", lowercase=False),
            }
        )
    return {
        "uri": _nonempty_string(pulse["uri"], "NIST_PULSE_URI_INVALID"),
        "certificate_id": pulse["certificateId"].lower(),
        "chain_index": chain,
        "pulse_index": index,
        "timestamp_ms": timestamp_ms,
        "output_value": pulse["outputValue"].lower(),
        "precommitment_value": pulse["precommitmentValue"].lower(),
        "list_values": normalized_values,
        "raw_pulse": dict(pulse),
    }


def validate_anchor_first_next(anchor_response: Mapping[str, Any], previous_response: Mapping[str, Any], not_before_ms: int) -> dict[str, Any]:
    not_before = _plain_int(not_before_ms, "NIST_NOT_BEFORE_INVALID", maximum=2**63 - 1)
    anchor = validate_pulse_structure(anchor_response)
    previous = validate_pulse_structure(previous_response)
    if not (previous["timestamp_ms"] <= not_before < anchor["timestamp_ms"]):
        raise X2Error("NIST_ANCHOR_NOT_STRICT_FIRST_NEXT")
    if anchor["chain_index"] != previous["chain_index"]:
        raise X2Error("NIST_ANCHOR_PREVIOUS_CHAIN_MISMATCH")
    if anchor["pulse_index"] != previous["pulse_index"] + 1:
        raise X2Error("NIST_ANCHOR_PREVIOUS_INDEX_MISMATCH")
    if anchor["timestamp_ms"] != previous["timestamp_ms"] + 60_000:
        raise X2Error("NIST_ANCHOR_PREVIOUS_TIME_MISMATCH")
    previous_links = [item for item in anchor["list_values"] if item["type"] == "previous"]
    if len(previous_links) != 1:
        raise X2Error("NIST_ANCHOR_PREVIOUS_LINK_COUNT_MISMATCH")
    link = previous_links[0]
    if link["uri"] != previous["uri"] or link["value"] != previous["output_value"]:
        raise X2Error("NIST_ANCHOR_PREVIOUS_LINK_MISMATCH")
    return {"anchor": anchor, "previous": previous, "not_before_ms": not_before}


def validate_exact_target(target_response: Mapping[str, Any], anchor: Mapping[str, Any], target_ms: int) -> dict[str, Any]:
    target = validate_pulse_structure(target_response)
    exact_ms = _plain_int(target_ms, "NIST_TARGET_MS_INVALID", maximum=2**63 - 1)
    if target["timestamp_ms"] != exact_ms:
        raise X2Error("NIST_NEXT_CLOSEST_TARGET_REJECTED")
    if target["timestamp_ms"] != anchor["timestamp_ms"] + 86_400_000:
        raise X2Error("NIST_TARGET_OFFSET_MISMATCH")
    if target["chain_index"] != anchor["chain_index"]:
        raise X2Error("NIST_TARGET_CHAIN_MISMATCH")
    if target["pulse_index"] != anchor["pulse_index"] + 1440:
        raise X2Error("NIST_TARGET_PULSE_INDEX_MISMATCH")
    uri_lower = target["uri"].lower()
    if str(target["chain_index"]) not in uri_lower or str(target["pulse_index"]) not in uri_lower:
        raise X2Error("NIST_TARGET_URI_IDENTITY_MISMATCH")
    return target
