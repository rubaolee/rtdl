#!/usr/bin/env python3
"""Build or verify Goal5839's pre-result discovery execution binding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts import goal5839_build_real_artifact_census_preregistration as prereg


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = prereg.EVIDENCE_ROOT / "DISCOVERY_EXECUTION_BINDING.json"
SCHEMA = "rtdl.goal5839.discovery_execution_binding.v1"
DOMAIN = "rtdl.goal5839.discovery_execution_binding.v1"
FROZEN_AT_UTC = "2026-09-03T07:04:58Z"
PREREGISTRATION_COMMIT = "17c189c0f"
PREREGISTRATION_AUTHORITY_SHA256 = (
    "767fb5e8601268aea8c505babec0fcbf25d6c9407b54cb9801c5271c8015df0c"
)
PREREGISTRATION_FILE_SHA256 = (
    "995dbbf1e23cb561a97472a83e240a1c29d7972899bf586e8748f7b8a0ba26f3"
)


class DiscoveryBindingError(RuntimeError):
    """Fail-closed discovery-binding error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiscoveryBindingError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _seal(value: dict[str, Any]) -> str:
    body = dict(value)
    body["binding_sha256"] = ""
    return _sha256(DOMAIN.encode("ascii") + b"\0" + _canonical_bytes(body))


def build_binding() -> dict[str, Any]:
    preregistration_payload = prereg.AUTHORITY_PATH.read_bytes()
    _require(
        _sha256(preregistration_payload) == PREREGISTRATION_FILE_SHA256,
        "PREREGISTRATION_FILE_IDENTITY_MISMATCH",
    )
    authority = json.loads(preregistration_payload.decode("ascii"))
    prereg.validate_authority(authority)
    _require(
        authority["authority_sha256"] == PREREGISTRATION_AUTHORITY_SHA256,
        "PREREGISTRATION_AUTHORITY_IDENTITY_MISMATCH",
    )

    works = authority["denominator"]["works"]
    query_rows = [
        {
            "work_id": row["work_id"],
            "citation_key": row["citation_key"],
            "title": row["title"],
            "github_query": f'"{row["title"]}" in:name,description,readme',
            "general_web_query": f'"{row["title"]}" "source code"',
        }
        for row in works
    ]

    binding: dict[str, Any] = {
        "schema": SCHEMA,
        "goal": 5839,
        "stage": "DISCOVERY_EXECUTION_BINDING_BEFORE_RESULT_REQUESTS",
        "status": "FROZEN_DISCOVERY_PROVIDER_AND_QUERY_BINDING__NO_CANDIDATE_RESULT",
        "frozen_at_utc": FROZEN_AT_UTC,
        "preregistration": {
            "commit": PREREGISTRATION_COMMIT,
            "authority_sha256": PREREGISTRATION_AUTHORITY_SHA256,
            "file_sha256": PREREGISTRATION_FILE_SHA256,
            "work_count": 29,
        },
        "github_repository_search": {
            "provider": "GitHub REST API",
            "endpoint": "https://api.github.com/search/repositories",
            "method": "GET",
            "api_version_header": "2022-11-28",
            "accept_header": "application/vnd.github+json",
            "authentication": "authenticated when GITHUB_TOKEN is available; token never recorded",
            "query_template": '"{exact_title}" in:name,description,readme',
            "page": 1,
            "per_page": 50,
            "sort": "best_match_by_omitting_sort_and_order_parameters",
            "preserve_first_n_items": 50,
            "preserved_identity_fields": [
                "rank",
                "id",
                "node_id",
                "full_name",
                "html_url",
                "owner_login",
                "fork",
                "archived",
                "default_branch",
                "created_at",
                "updated_at",
                "pushed_at",
                "description",
            ],
        },
        "general_web_search": {
            "provider": "DuckDuckGo HTML",
            "endpoint": "https://html.duckduckgo.com/html/",
            "method": "GET",
            "query_parameter": "q",
            "query_template": '"{exact_title}" "source code"',
            "user_agent": "RTDL-Goal5839-Census/1.0",
            "redirects_followed": True,
            "parser": "stdlib_html_parser__anchors_whose_class_contains_result__a",
            "redirect_url_normalization": "decode_uddg_query_parameter_when_present",
            "preserve_first_n_items": 20,
            "preserved_identity_fields": ["rank", "title", "url"],
        },
        "paper_and_publisher_discovery": {
            "order": [
                "exact bibliography DOI field",
                "exact bibliography URL field",
                "canonical paper URL discovered in frozen search results",
                "publisher supplementary-material links in paper order",
                "paper full-text code/repository/artifact links in document order",
            ],
            "preserve": [
                "requested URL",
                "resolved URL",
                "retrieval status",
                "retrieved_at_utc",
                "response SHA-256 when bytes are retained",
                "repository or artifact links in source order",
            ],
            "candidate_source_classification_during_link_discovery": False,
        },
        "request_failure_and_retry_policy": {
            "successful_response_definition": "HTTP 200 with parseable provider response",
            "maximum_attempts_per_exact_request": 3,
            "retry_changes_query_or_provider": False,
            "retry_schedule_seconds": [0, 5, 30],
            "rate_limit_response_is_empty_result": False,
            "terminal_request_failure": (
                "record request failure; do not substitute a different query or provider and do "
                "not remove the work"
            ),
        },
        "query_rows": query_rows,
        "execution_state": {
            "github_candidate_query_count": 0,
            "general_web_candidate_query_count": 0,
            "paper_or_publisher_candidate_fetch_count": 0,
            "candidate_result_count": 0,
            "candidate_source_inspection_count": 0,
        },
        "claim_boundary": {
            "provider_and_query_binding_only": True,
            "artifact_discovered": False,
            "artifact_eligible": False,
            "source_inspected": False,
            "property_classified": False,
            "field_result_or_paper_claim": False,
            "external_review_or_consensus": False,
        },
        "binding_sha256": "",
    }
    binding["binding_sha256"] = _seal(binding)
    validate_binding(binding)
    return binding


def validate_binding(binding: dict[str, Any]) -> None:
    _require(binding.get("schema") == SCHEMA, "BINDING_SCHEMA_MISMATCH")
    _require(binding.get("binding_sha256") == _seal(binding), "BINDING_SEAL_MISMATCH")
    _require(
        binding.get("status")
        == "FROZEN_DISCOVERY_PROVIDER_AND_QUERY_BINDING__NO_CANDIDATE_RESULT",
        "BINDING_STATUS_MISMATCH",
    )
    preregistration = binding.get("preregistration")
    _require(
        isinstance(preregistration, dict)
        and preregistration.get("authority_sha256") == PREREGISTRATION_AUTHORITY_SHA256
        and preregistration.get("file_sha256") == PREREGISTRATION_FILE_SHA256
        and preregistration.get("work_count") == 29,
        "BINDING_PREREGISTRATION_MISMATCH",
    )
    queries = binding.get("query_rows")
    _require(isinstance(queries, list) and len(queries) == 29, "BINDING_QUERY_COUNT_MISMATCH")
    _require(len({row["work_id"] for row in queries}) == 29, "BINDING_QUERY_WORK_DUPLICATE")
    _require(
        all(row["title"] in row["github_query"] and row["title"] in row["general_web_query"] for row in queries),
        "BINDING_QUERY_TITLE_MISMATCH",
    )
    execution = binding.get("execution_state")
    _require(isinstance(execution, dict) and all(value == 0 for value in execution.values()), "BINDING_HAS_RESULTS")
    boundary = binding.get("claim_boundary")
    _require(
        isinstance(boundary, dict)
        and boundary.get("provider_and_query_binding_only") is True
        and all(value is False for key, value in boundary.items() if key != "provider_and_query_binding_only"),
        "BINDING_CLAIM_BOUNDARY_MISMATCH",
    )


def _serialized(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()

    expected = build_binding()
    if args.verify_stored:
        stored = json.loads(args.output.read_text(encoding="ascii"))
        validate_binding(stored)
        _require(_serialized(stored) == _serialized(expected), "STORED_BINDING_REBUILD_MISMATCH")
        print(
            json.dumps(
                {
                    "binding_sha256": stored["binding_sha256"],
                    "file_sha256": _sha256(args.output.read_bytes()),
                    "status": "PASS__GOAL5839_DISCOVERY_BINDING_VERIFIED",
                },
                sort_keys=True,
            )
        )
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_serialized(expected))
    print(
        json.dumps(
            {
                "binding_sha256": expected["binding_sha256"],
                "file_sha256": _sha256(args.output.read_bytes()),
                "status": expected["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
