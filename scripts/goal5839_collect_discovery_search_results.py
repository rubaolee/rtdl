#!/usr/bin/env python3
"""Collect the two frozen Goal5839 search-provider result sets."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

from scripts import goal5839_build_discovery_execution_binding as binding_builder


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = binding_builder.prereg.EVIDENCE_ROOT
BINDING_PATH = binding_builder.OUTPUT_PATH
GITHUB_OUTPUT_PATH = EVIDENCE_ROOT / "DISCOVERY_GITHUB_RESULTS.json"
GENERAL_OUTPUT_PATH = EVIDENCE_ROOT / "DISCOVERY_GENERAL_WEB_RESULTS.json"

GITHUB_SCHEMA = "rtdl.goal5839.github_discovery_results.v1"
GENERAL_SCHEMA = "rtdl.goal5839.general_web_discovery_results.v1"
GITHUB_DOMAIN = "rtdl.goal5839.github_discovery_results.v1"
GENERAL_DOMAIN = "rtdl.goal5839.general_web_discovery_results.v1"
BINDING_FILE_SHA256 = (
    "f6753da2ac417a77f842c71ec3e519c13ee91b8b69736fb2bf0077d4c2d390ed"
)
BINDING_COMMIT = "7da8488ce"


class DiscoveryCollectionError(RuntimeError):
    """Fail-closed discovery collection error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiscoveryCollectionError(message)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _seal(value: dict[str, Any], field: str, domain: str) -> str:
    body = dict(value)
    body[field] = ""
    return _sha256(domain.encode("ascii") + b"\0" + _canonical_bytes(body))


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_binding() -> dict[str, Any]:
    payload = BINDING_PATH.read_bytes()
    _require(_sha256(payload) == BINDING_FILE_SHA256, "DISCOVERY_BINDING_FILE_MISMATCH")
    binding = json.loads(payload.decode("ascii"))
    binding_builder.validate_binding(binding)
    return binding


def _request_with_frozen_retries(
    url: str,
    headers: dict[str, str],
    parser: Callable[[bytes], Any],
) -> tuple[dict[str, Any], Any | None]:
    attempts: list[dict[str, Any]] = []
    for attempt_index, delay_seconds in enumerate((0, 5, 30), start=1):
        if delay_seconds:
            time.sleep(delay_seconds)
        started = _now_utc()
        try:
            request = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = response.read()
                status = int(response.status)
                resolved_url = response.geturl()
                response_headers = {
                    key.lower(): value
                    for key, value in response.headers.items()
                    if key.lower()
                    in {
                        "content-type",
                        "etag",
                        "last-modified",
                        "x-github-request-id",
                        "x-ratelimit-limit",
                        "x-ratelimit-remaining",
                        "x-ratelimit-reset",
                        "x-ratelimit-resource",
                        "x-ratelimit-used",
                    }
                }
            _require(status == 200, f"UNEXPECTED_HTTP_STATUS:{status}")
            parsed = parser(payload)
            attempts.append(
                {
                    "attempt": attempt_index,
                    "delay_before_attempt_seconds": delay_seconds,
                    "started_at_utc": started,
                    "completed_at_utc": _now_utc(),
                    "status": "SUCCESS",
                    "http_status": status,
                    "resolved_url": resolved_url,
                    "response_bytes": len(payload),
                    "response_sha256": _sha256(payload),
                    "response_headers": response_headers,
                }
            )
            return {"attempts": attempts, "terminal_status": "SUCCESS"}, parsed
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, DiscoveryCollectionError) as exc:
            status = exc.code if isinstance(exc, urllib.error.HTTPError) else None
            attempts.append(
                {
                    "attempt": attempt_index,
                    "delay_before_attempt_seconds": delay_seconds,
                    "started_at_utc": started,
                    "completed_at_utc": _now_utc(),
                    "status": "FAILED",
                    "http_status": status,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
    return {"attempts": attempts, "terminal_status": "TERMINAL_REQUEST_FAILURE"}, None


def _parse_github(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    _require(isinstance(value, dict), "GITHUB_RESPONSE_NOT_OBJECT")
    items = value.get("items")
    _require(isinstance(items, list), "GITHUB_RESPONSE_ITEMS_MISSING")
    rows: list[dict[str, Any]] = []
    for rank, item in enumerate(items[:50], start=1):
        _require(isinstance(item, dict), "GITHUB_RESPONSE_ITEM_NOT_OBJECT")
        owner = item.get("owner")
        rows.append(
            {
                "rank": rank,
                "id": item.get("id"),
                "node_id": item.get("node_id"),
                "full_name": item.get("full_name"),
                "html_url": item.get("html_url"),
                "owner_login": owner.get("login") if isinstance(owner, dict) else None,
                "fork": item.get("fork"),
                "archived": item.get("archived"),
                "default_branch": item.get("default_branch"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "pushed_at": item.get("pushed_at"),
                "description": item.get("description"),
            }
        )
    return {
        "total_count": value.get("total_count"),
        "incomplete_results": value.get("incomplete_results"),
        "returned_item_count": len(rows),
        "items": rows,
    }


class _DuckDuckGoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._active_href: str | None = None
        self._active_text: list[str] = []
        self.rows: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a" or self._active_href is not None:
            return
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        href = values.get("href")
        if "result__a" in classes and href:
            self._active_href = href
            self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._active_href is not None:
            self._active_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._active_href is not None:
            title = html.unescape("".join(self._active_text)).strip()
            self.rows.append((title, self._active_href))
            self._active_href = None
            self._active_text = []


def _normalize_duckduckgo_url(value: str) -> str:
    absolute = urllib.parse.urljoin("https://html.duckduckgo.com/html/", value)
    parsed = urllib.parse.urlparse(absolute)
    query = urllib.parse.parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return query["uddg"][0]
    return absolute


def _parse_general(payload: bytes) -> dict[str, Any]:
    parser = _DuckDuckGoParser()
    parser.feed(payload.decode("utf-8", errors="strict"))
    rows = [
        {"rank": rank, "title": title, "url": _normalize_duckduckgo_url(url)}
        for rank, (title, url) in enumerate(parser.rows[:20], start=1)
    ]
    return {"returned_item_count": len(rows), "items": rows}


def _github_url(endpoint: str, query: str) -> str:
    return endpoint + "?" + urllib.parse.urlencode(
        {"q": query, "page": "1", "per_page": "50"}
    )


def _general_url(endpoint: str, query: str) -> str:
    return endpoint + "?" + urllib.parse.urlencode({"q": query})


def collect(provider: str) -> dict[str, Any]:
    binding = _load_binding()
    started_at = _now_utc()
    rows: list[dict[str, Any]] = []
    token = os.environ.get("GITHUB_TOKEN")

    for index, query_row in enumerate(binding["query_rows"], start=1):
        if provider == "github":
            provider_contract = binding["github_repository_search"]
            query = query_row["github_query"]
            url = _github_url(provider_contract["endpoint"], query)
            headers = {
                "Accept": provider_contract["accept_header"],
                "X-GitHub-Api-Version": provider_contract["api_version_header"],
                "User-Agent": "RTDL-Goal5839-Census/1.0",
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"
            request_record, result = _request_with_frozen_retries(url, headers, _parse_github)
        elif provider == "general_web":
            provider_contract = binding["general_web_search"]
            query = query_row["general_web_query"]
            url = _general_url(provider_contract["endpoint"], query)
            headers = {"User-Agent": provider_contract["user_agent"]}
            request_record, result = _request_with_frozen_retries(url, headers, _parse_general)
        else:
            raise DiscoveryCollectionError("UNKNOWN_PROVIDER")

        print(
            json.dumps(
                {
                    "index": index,
                    "provider": provider,
                    "status": request_record["terminal_status"],
                    "work_id": query_row["work_id"],
                    "items": result["returned_item_count"] if result is not None else 0,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        rows.append(
            {
                "work_id": query_row["work_id"],
                "citation_key": query_row["citation_key"],
                "title": query_row["title"],
                "query": query,
                "request_url": url,
                "request": request_record,
                "result": result,
            }
        )

    result_count = sum(
        row["result"]["returned_item_count"]
        for row in rows
        if row["result"] is not None
    )
    failure_count = sum(
        row["request"]["terminal_status"] != "SUCCESS" for row in rows
    )
    if provider == "github":
        schema = GITHUB_SCHEMA
        domain = GITHUB_DOMAIN
        field = "result_sha256"
    else:
        schema = GENERAL_SCHEMA
        domain = GENERAL_DOMAIN
        field = "result_sha256"
    document: dict[str, Any] = {
        "schema": schema,
        "goal": 5839,
        "stage": f"{provider.upper()}_DISCOVERY_RESULT_COLLECTION",
        "status": (
            "COMPLETE_FROZEN_QUERY_SET_WITH_TERMINAL_FAILURES"
            if failure_count
            else "COMPLETE_FROZEN_QUERY_SET"
        ),
        "provider": provider,
        "binding": {
            "commit": BINDING_COMMIT,
            "file_sha256": BINDING_FILE_SHA256,
            "binding_sha256": binding["binding_sha256"],
        },
        "started_at_utc": started_at,
        "completed_at_utc": _now_utc(),
        "query_count": len(rows),
        "successful_query_count": len(rows) - failure_count,
        "terminal_failure_count": failure_count,
        "returned_item_count": result_count,
        "rows": rows,
        "execution_boundary": {
            "candidate_result_metadata_collected": True,
            "repository_cloned": False,
            "candidate_source_inspected": False,
            "artifact_eligibility_decided": False,
            "property_classified": False,
            "gpu_or_pod_used": False,
            "performance_timed": False,
        },
        "claim_boundary": {
            "search_result_set_only": True,
            "complete_artifact_discovery": False,
            "field_result_or_paper_claim": False,
            "external_review_or_consensus": False,
        },
        field: "",
    }
    document[field] = _seal(document, field, domain)
    validate_result(document, provider)
    return document


def validate_result(document: dict[str, Any], provider: str) -> None:
    expected_schema = GITHUB_SCHEMA if provider == "github" else GENERAL_SCHEMA
    expected_domain = GITHUB_DOMAIN if provider == "github" else GENERAL_DOMAIN
    _require(document.get("schema") == expected_schema, "DISCOVERY_RESULT_SCHEMA_MISMATCH")
    _require(
        document.get("result_sha256") == _seal(document, "result_sha256", expected_domain),
        "DISCOVERY_RESULT_SEAL_MISMATCH",
    )
    rows = document.get("rows")
    _require(isinstance(rows, list) and len(rows) == 29, "DISCOVERY_RESULT_ROW_COUNT_MISMATCH")
    _require(len({row["work_id"] for row in rows}) == 29, "DISCOVERY_RESULT_WORK_DUPLICATE")
    _require(document.get("query_count") == 29, "DISCOVERY_QUERY_COUNT_MISMATCH")
    boundary = document.get("execution_boundary")
    _require(
        isinstance(boundary, dict)
        and boundary.get("candidate_result_metadata_collected") is True
        and all(value is False for key, value in boundary.items() if key != "candidate_result_metadata_collected"),
        "DISCOVERY_EXECUTION_BOUNDARY_MISMATCH",
    )
    for row in rows:
        result = row["result"]
        if result is None:
            _require(
                row["request"]["terminal_status"] == "TERMINAL_REQUEST_FAILURE",
                "DISCOVERY_NULL_RESULT_WITHOUT_FAILURE",
            )
            continue
        cap = 50 if provider == "github" else 20
        _require(result["returned_item_count"] == len(result["items"]), "DISCOVERY_ITEM_COUNT_MISMATCH")
        _require(len(result["items"]) <= cap, "DISCOVERY_ITEM_CAP_EXCEEDED")
        _require(
            [item["rank"] for item in result["items"]]
            == list(range(1, len(result["items"]) + 1)),
            "DISCOVERY_RANK_MISMATCH",
        )


def _serialized(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("github", "general_web"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    if args.verify is not None:
        document = json.loads(args.verify.read_text(encoding="ascii"))
        validate_result(document, args.provider)
        print(
            json.dumps(
                {
                    "file_sha256": _sha256(args.verify.read_bytes()),
                    "result_sha256": document["result_sha256"],
                    "status": "PASS__GOAL5839_DISCOVERY_RESULT_VERIFIED",
                },
                sort_keys=True,
            )
        )
        return

    output = args.output
    if output is None:
        output = GITHUB_OUTPUT_PATH if args.provider == "github" else GENERAL_OUTPUT_PATH
    document = collect(args.provider)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(_serialized(document))
    print(
        json.dumps(
            {
                "file_sha256": _sha256(output.read_bytes()),
                "result_sha256": document["result_sha256"],
                "status": document["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
