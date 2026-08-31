#!/usr/bin/env python3
"""Freeze exact bytes and policy before the one X3 provider-search call set."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x3_capture_provider_search as capture
from scripts import goal5793_x3_provider_search_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "history/internal_docs/goal5793_x3_provider_search_preaction_authority_20260822.json"
DOMAIN = "rtdl.goal5793.x3.provider_search_preaction_authority"
STATIC_PINS = {
    "history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json": (4130, "ce3f83ef318085646cefdbbfbcc4290b66e745aa9ee88f4b041f84661997e659"),
    "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json": (56110, "126ee3c1dfe930a7bb25b2f19df8a6c4889c7ef8b619abe3cc69da54efa8b7c2"),
    "scripts/goal5793_x2_offline_core.py": (57162, "48922c941f0ab11df9b507fefa06836e72ee7a479bb9c02ffe2e4700dc87be83"),
    "scripts/goal5793_x1_canonical.py": (3099, "13b22dbae22b0a70763fdf46031c7975ab1eaebe20c37789f397242b7a1c9b3a"),
}
SOURCE_PATHS = (
    "scripts/goal5793_x3_capture_provider_search.py",
    "scripts/goal5793_x3_provider_search_authority.py",
    "tests/goal5793_x3_provider_search_test.py",
    "scripts/goal5793_x3_build_provider_search_preaction.py",
    "tests/goal5793_x3_provider_search_preaction_test.py",
)


def _identity(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _verify_static() -> None:
    authority.verify_static_authorities()
    for relative, (size, digest) in STATIC_PINS.items():
        row = _identity(relative)
        if row["bytes"] != size or row["sha256"] != digest:
            raise RuntimeError(f"STATIC_PIN_MISMATCH:{relative}")


def build_authority() -> dict[str, Any]:
    _verify_static()
    document: dict[str, Any] = {
        "schema": "rtdl.goal5793.x3.provider_search_preaction_authority.v1",
        "date": "2026-08-22",
        "status": "EXACT_SINGLE_EXPANSION_PREACTION_FROZEN__ZERO_PROVIDER_CALLS_AT_FREEZE",
        "predecessors": [_identity(path) for path in STATIC_PINS],
        "implementation_and_tests": [_identity(path) for path in SOURCE_PATHS],
        "schedule": {
            "provider_order": list(core.PROVIDER_ORDER),
            "term_order": list(core.TERMS),
            "query_count": 22,
            "worker_count": 1,
            "concurrent_requests": False,
            "openalex_endpoint": core.OPENALEX_ENDPOINT,
            "openalex_filter": core.OPENALEX_FILTER,
            "openalex_per_page": 200,
            "arxiv_endpoint": core.ARXIV_ENDPOINT,
            "arxiv_date_window": core.ARXIV_DATE,
            "arxiv_page_size": 500,
            "arxiv_minimum_inter_request_seconds": 3,
            "retry_delay_seconds_including_initial": list(core.RETRY_DELAYS),
            "request_timeout_seconds": capture.TIMEOUT_SECONDS,
            "user_agent": capture.USER_AGENT,
            "redirects_followed": False,
            "partial_universe_allowed": False,
            "manual_relevance_cutoff_allowed": False,
            "second_query_round_or_rerun_allowed": False,
        },
        "outputs": {
            "journal": "history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl",
            "complete_transcript": "history/internal_docs/goal5793_x3_provider_search_transcript_20260822.json",
            "terminal_failure_receipt": "history/internal_docs/goal5793_x3_provider_search_terminal_failure_20260822.json",
            "complete_authority": "history/internal_docs/goal5793_x3_provider_search_authority_20260822.json",
            "create_only": True,
        },
        "preaction_observation": {
            "live_provider_call_count": 0,
            "raw_response_count": 0,
            "candidate_identity_observed_from_x3": False,
            "science_row_count": 0,
            "entropy_draw_count": 0,
            "selection_count": 0,
        },
        "terminal_policy": {
            "complete_success": "FREEZE_TRANSCRIPT_AND_COMPONENT_AUTHORITY__EXTERNAL_REVIEW_REQUIRED",
            "exhausted_retry_schema_drift_pagination_conflict_or_process_failure": "TERMINAL_INFRA_FAILURE__NO_PARTIAL_UNIVERSE__NO_RERUN",
            "crash_journal_may_be_recovered_without_new_HTTP": True,
            "any_new_HTTP_after_terminal_or_crash": False,
        },
        "authorization": {
            "execute_exact_single_provider_expansion_once": True,
            "full_text_resolution": False,
            "science_row_construction": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "live_beacon": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "product_change": False,
            "publication_submission": False,
        },
        "claim_boundary": {
            "generalization_evidence_count": 0,
            "usability_evidence_count": 0,
            "provider_results_are_not_yet_science_eligible": True,
        },
        "preaction_authority_sha256": "",
    }
    document["preaction_authority_sha256"] = seal_document(
        document, seal_field="preaction_authority_sha256", domain=DOMAIN, version=1
    )
    return document


def verify_authority(document: dict[str, Any]) -> None:
    expected = build_authority()
    if document != expected:
        raise RuntimeError("PREACTION_AUTHORITY_EXACT_DOCUMENT_MISMATCH")
    seal = seal_document(document, seal_field="preaction_authority_sha256", domain=DOMAIN, version=1)
    if document["preaction_authority_sha256"] != seal:
        raise RuntimeError("PREACTION_AUTHORITY_SEAL_MISMATCH")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    document = build_authority()
    payload = canonical_json_bytes(document) + b"\n"
    if args.write_create_only:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(payload)
        status = "CREATE_ONLY_PREACTION_FREEZE_PASS"
    elif args.verify_stored:
        if not args.output.is_file() or args.output.is_symlink() or args.output.read_bytes() != payload:
            raise SystemExit("STORED_PREACTION_AUTHORITY_MISMATCH")
        status = "POSTWRITE_PREACTION_VERIFY_PASS"
    else:
        status = "DRY_RUN_PREACTION_PASS__NO_NETWORK"
    print(json.dumps({"status": status, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "preaction_authority_sha256": document["preaction_authority_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
