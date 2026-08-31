#!/usr/bin/env python3
"""Capture the single authorized Goal5793 X3 provider-search expansion."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import ssl
import sys
import time
from typing import Any, Callable, Mapping, Sequence
import urllib.error
import urllib.parse
import urllib.request

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x3_provider_search_authority as authority


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_DOMAIN = authority.TRANSCRIPT_DOMAIN
USER_AGENT = "RTDL-Goal5793-X3-SingleExpansion/1.0"
TIMEOUT_SECONDS = 120
PREACTION_DOMAIN = "rtdl.goal5793.x3.provider_search_preaction_authority"
REQUEST_HEADERS = {
    "OpenAlex Works API": (("Accept", "application/json"), ("User-Agent", USER_AGENT)),
    "arXiv API": (("Accept", "application/atom+xml"), ("User-Agent", USER_AGENT)),
}
PREACTION_REQUIRED_PREDECESSOR_PATHS = {
    "history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json",
    "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json",
    "scripts/goal5793_x2_offline_core.py",
    "scripts/goal5793_x1_canonical.py",
}
PREACTION_REQUIRED_SOURCE_PATHS = {
    "scripts/goal5793_x3_capture_provider_search.py",
    "scripts/goal5793_x3_provider_search_authority.py",
    "tests/goal5793_x3_provider_search_test.py",
    "scripts/goal5793_x3_build_provider_search_preaction.py",
    "tests/goal5793_x3_provider_search_preaction_test.py",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _utc_now() -> str:
    value = datetime.now(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _full_url(endpoint: str, params: Mapping[str, Any]) -> str:
    query = urllib.parse.urlencode(
        [(key, str(value)) for key, value in params.items()],
        doseq=False,
        quote_via=urllib.parse.quote,
        safe="",
    )
    return f"{endpoint}?{query}"


def _header_rows(items: Sequence[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"name": str(name), "value": str(value)} for name, value in items]


def _network_fetch(
    full_url: str, request_headers: Sequence[tuple[str, str]], timeout_seconds: int
) -> tuple[int | None, list[tuple[str, str]], bytes, str | None]:
    request = urllib.request.Request(full_url, method="GET")
    for name, value in request_headers:
        request.add_header(name, value)
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            return int(response.status), list(response.headers.raw_items()), response.read(), None
    except urllib.error.HTTPError as exc:
        body = exc.read()
        headers = list(exc.headers.raw_items()) if exc.headers is not None else []
        return int(exc.code), headers, body, f"HTTP_STATUS_{exc.code}"
    except Exception as exc:  # noqa: BLE001 - preserved fail-closed evidence
        return None, [], b"", f"{type(exc).__module__}.{type(exc).__name__}:{exc}"


def _perform_page(
    *,
    provider: str,
    endpoint: str,
    params: Mapping[str, Any],
    request_sequence: int,
    fetch_fn: Callable[[str, Sequence[tuple[str, str]], int], tuple[int | None, list[tuple[str, str]], bytes, str | None]],
    sleep_fn: Callable[[float], None],
    now_fn: Callable[[], str],
    event_sink: Callable[[Mapping[str, Any]], None],
) -> tuple[dict[str, Any], bytes]:
    full_url = _full_url(endpoint, params)
    attempts: list[dict[str, Any]] = []
    headers = REQUEST_HEADERS[provider]
    for index, delay in enumerate(core.RETRY_DELAYS):
        if delay:
            sleep_fn(delay)
        started = now_fn()
        status, response_headers, body, error = fetch_fn(full_url, headers, TIMEOUT_SECONDS)
        ended = now_fn()
        attempt = {
            "attempt": index + 1,
            "scheduled_delay_seconds": delay,
            "request_url": endpoint,
            "request_headers": _header_rows(headers),
            "request_started_at_utc": started,
            "status": status,
            "response_headers": _header_rows(response_headers),
            "response_received_at_utc": ended,
            "body_base64": base64.b64encode(body).decode("ascii"),
            "error": error,
        }
        attempts.append(attempt)
        event_sink({
            "event": "HTTP_ATTEMPT",
            "provider": provider,
            "request_sequence": request_sequence,
            "params": dict(params),
            "full_url": full_url,
            "attempt": attempt,
        })
        if status == 200 and error is None:
            return {"request_sequence": request_sequence, "params": dict(params), "attempts": attempts}, body
    raise authority.X3SearchError("INFRA_INVALID__NO_PARTIAL_UNIVERSE__EXHAUSTED_RETRY", full_url)


def collect_search(
    *,
    fetch_fn: Callable[[str, Sequence[tuple[str, str]], int], tuple[int | None, list[tuple[str, str]], bytes, str | None]],
    sleep_fn: Callable[[float], None],
    now_fn: Callable[[], str],
    event_sink: Callable[[Mapping[str, Any]], None],
) -> dict[str, Any]:
    authority.verify_static_authorities()
    started = now_fn()
    queries: list[dict[str, Any]] = []
    network_calls = 0
    arxiv_request_seen = False
    for provider in core.PROVIDER_ORDER:
        for term in core.TERMS:
            lineages: list[dict[str, Any]] = []
            if provider == "OpenAlex Works API":
                endpoint = core.OPENALEX_ENDPOINT
                cursor: str | None = "*"
                sequence = 0
                while cursor is not None:
                    params = core._openalex_params(term, cursor)
                    lineage, body = _perform_page(
                        provider=provider, endpoint=endpoint, params=params, request_sequence=sequence,
                        fetch_fn=fetch_fn, sleep_fn=sleep_fn, now_fn=now_fn, event_sink=event_sink,
                    )
                    network_calls += len(lineage["attempts"])
                    lineages.append(lineage)
                    try:
                        _, next_cursor = core._parse_openalex(body, term=term, query_index=len(queries), page_index=sequence)
                    except core.X2Error as exc:
                        raise authority.X3SearchError("OPENALEX_SCHEMA_OR_IDENTITY_INVALID__NO_PARTIAL_UNIVERSE", str(exc)) from exc
                    if next_cursor == cursor:
                        raise authority.X3SearchError("OPENALEX_REPEATED_CURSOR_OR_NO_PROGRESS")
                    cursor = next_cursor
                    sequence += 1
            else:
                endpoint = core.ARXIV_ENDPOINT
                start = 0
                total: int | None = None
                sequence = 0
                while total is None or start < total:
                    if arxiv_request_seen:
                        # The frozen three-second minimum is global across all
                        # arXiv pages and terms, not merely within one query.
                        sleep_fn(3)
                    params = core._arxiv_params(term, start)
                    lineage, body = _perform_page(
                        provider=provider, endpoint=endpoint, params=params, request_sequence=sequence,
                        fetch_fn=fetch_fn, sleep_fn=sleep_fn, now_fn=now_fn, event_sink=event_sink,
                    )
                    arxiv_request_seen = True
                    network_calls += len(lineage["attempts"])
                    lineages.append(lineage)
                    try:
                        nodes, observed_total = core._parse_arxiv(body, term=term, query_index=len(queries), page_index=sequence)
                    except core.X2Error as exc:
                        raise authority.X3SearchError("ARXIV_SCHEMA_OR_IDENTITY_INVALID__NO_PARTIAL_UNIVERSE", str(exc)) from exc
                    if total is None:
                        total = observed_total
                    elif observed_total != total:
                        raise authority.X3SearchError("ARXIV_TOTAL_RESULTS_CHANGED__NO_PARTIAL_UNIVERSE")
                    if not nodes and start < total:
                        raise authority.X3SearchError("ARXIV_ZERO_ENTRIES_BEFORE_TOTAL__NO_PARTIAL_UNIVERSE")
                    start += len(nodes)
                    sequence += 1
            queries.append({"provider": provider, "term": term, "request_lineages": lineages})
            event_sink({"event": "QUERY_COMPLETE", "provider": provider, "term": term, "page_count": len(lineages)})
    transcript: dict[str, Any] = {
        "schema": "rtdl.goal5793.x3.provider_search_transcript.v1",
        "mode": "LIVE_PROVIDER_SEARCH_SINGLE_EXPANSION",
        "synthetic_fixture": False,
        "single_expansion_ordinal": 1,
        "provider_search_started_at_utc": started,
        "provider_search_ended_at_utc": now_fn(),
        "network_call_count": network_calls,
        "worker_count": 1,
        "concurrent_requests": False,
        "queries": queries,
        "manual_row_deletion_count": 0,
        "live_beacon_call_count": 0,
        "entropy_draw_count": 0,
        "candidate_work_count": 0,
        "authorization": {
            "full_text_resolution": False, "science_row_construction": False,
            "entropy": False, "selection": False, "candidate_work": False,
            "gpu_ssh_pod": False, "timing": False, "publication_submission": False,
        },
        "transcript_sha256": "",
    }
    transcript["transcript_sha256"] = seal_document(
        transcript, seal_field="transcript_sha256", domain=TRANSCRIPT_DOMAIN, version=1
    )
    authority.validate_live_transcript(transcript)
    return transcript


def _append_event(stream, event: Mapping[str, Any]) -> None:  # noqa: ANN001
    stream.write(canonical_json_bytes(dict(event)) + b"\n")
    stream.flush()
    os.fsync(stream.fileno())


def _runtime_boundary() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "openssl": ssl.OPENSSL_VERSION,
        "urllib": "PYTHON_STDLIB",
        "hermetic": False,
    }


def _verify_preaction(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise authority.X3SearchError("PREACTION_AUTHORITY_FILE_INVALID")
    try:
        document = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise authority.X3SearchError("PREACTION_AUTHORITY_JSON_INVALID") from exc
    if document.get("schema") != "rtdl.goal5793.x3.provider_search_preaction_authority.v1":
        raise authority.X3SearchError("PREACTION_AUTHORITY_SCHEMA_MISMATCH")
    seal = seal_document(document, seal_field="preaction_authority_sha256", domain=PREACTION_DOMAIN, version=1)
    if document.get("preaction_authority_sha256") != seal:
        raise authority.X3SearchError("PREACTION_AUTHORITY_SEAL_MISMATCH")
    authorization = document.get("authorization")
    if not isinstance(authorization, Mapping) or [key for key, value in authorization.items() if value] != ["execute_exact_single_provider_expansion_once"]:
        raise authority.X3SearchError("PREACTION_AUTHORIZATION_MISMATCH")
    schedule = document.get("schedule")
    expected_schedule = {
        "provider_order": list(core.PROVIDER_ORDER), "term_order": list(core.TERMS),
        "query_count": 22, "worker_count": 1, "concurrent_requests": False,
        "openalex_endpoint": core.OPENALEX_ENDPOINT, "openalex_filter": core.OPENALEX_FILTER,
        "openalex_per_page": 200, "arxiv_endpoint": core.ARXIV_ENDPOINT,
        "arxiv_date_window": core.ARXIV_DATE, "arxiv_page_size": 500,
        "arxiv_minimum_inter_request_seconds": 3,
        "retry_delay_seconds_including_initial": list(core.RETRY_DELAYS),
        "request_timeout_seconds": TIMEOUT_SECONDS, "user_agent": USER_AGENT,
        "redirects_followed": False, "partial_universe_allowed": False,
        "manual_relevance_cutoff_allowed": False, "second_query_round_or_rerun_allowed": False,
    }
    if schedule != expected_schedule:
        raise authority.X3SearchError("PREACTION_SCHEDULE_MISMATCH")
    predecessor_rows = document.get("predecessors")
    source_rows = document.get("implementation_and_tests")
    if not isinstance(predecessor_rows, list) or not isinstance(source_rows, list):
        raise authority.X3SearchError("PREACTION_SOURCE_ROWS_INVALID")
    if {row.get("path") for row in predecessor_rows if isinstance(row, Mapping)} != PREACTION_REQUIRED_PREDECESSOR_PATHS:
        raise authority.X3SearchError("PREACTION_PREDECESSOR_SET_MISMATCH")
    if {row.get("path") for row in source_rows if isinstance(row, Mapping)} != PREACTION_REQUIRED_SOURCE_PATHS:
        raise authority.X3SearchError("PREACTION_SOURCE_SET_MISMATCH")
    for row in [*predecessor_rows, *source_rows]:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
            raise authority.X3SearchError("PREACTION_SOURCE_ROWS_INVALID")
        source = ROOT / row["path"]
        if not source.is_file() or source.is_symlink() or source.stat().st_size != row["bytes"] or _sha(source) != row["sha256"]:
            raise authority.X3SearchError("PREACTION_SOURCE_IDENTITY_MISMATCH", str(row.get("path")))
    reported_path = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
    return {"path": reported_path, "bytes": path.stat().st_size, "sha256": _sha(path), "preaction_authority_sha256": seal}


def execute_once(preaction_path: Path, journal: Path, transcript_path: Path, failure_path: Path) -> dict[str, Any]:
    targets = (journal, transcript_path, failure_path)
    if any(path.exists() or path.is_symlink() for path in targets):
        raise SystemExit("SINGLE_EXPANSION_OUTPUT_EXISTS__NO_RERUN")
    preaction_identity = _verify_preaction(preaction_path)
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("xb") as stream:
        _append_event(stream, {
            "event": "TRANSACTION_START",
            "single_expansion_ordinal": 1,
            "started_at_utc": _utc_now(),
            "runtime_boundary": _runtime_boundary(),
            "client": {"path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "bytes": Path(__file__).stat().st_size, "sha256": _sha(Path(__file__))},
            "authority_module": {"path": "scripts/goal5793_x3_provider_search_authority.py", "bytes": (ROOT / "scripts/goal5793_x3_provider_search_authority.py").stat().st_size, "sha256": _sha(ROOT / "scripts/goal5793_x3_provider_search_authority.py")},
            "closure": authority.verify_static_authorities()["closure"],
            "preaction_authority": preaction_identity,
        })
        try:
            transcript = collect_search(
                fetch_fn=_network_fetch,
                sleep_fn=time.sleep,
                now_fn=_utc_now,
                event_sink=lambda event: _append_event(stream, event),
            )
            payload = canonical_json_bytes(transcript) + b"\n"
            with transcript_path.open("xb") as output:
                output.write(payload)
            _append_event(stream, {"event": "TRANSACTION_COMPLETE", "ended_at_utc": _utc_now(), "transcript": {"path": transcript_path.as_posix(), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}})
            return {"status": "COMPLETE", "transcript": transcript}
        except Exception as exc:  # noqa: BLE001 - terminal record, never retry expansion
            reason = exc.reason_id if isinstance(exc, authority.X3SearchError) else f"{type(exc).__module__}.{type(exc).__name__}"
            detail = str(exc)
            _append_event(stream, {"event": "TRANSACTION_TERMINAL_FAILURE", "ended_at_utc": _utc_now(), "reason": reason, "detail": detail})
            failure = {
                "schema": "rtdl.goal5793.x3.provider_search_terminal_failure.v1",
                "status": "TERMINAL_INFRA_FAILURE__NO_PARTIAL_UNIVERSE__NO_RERUN",
                "reason": reason,
                "detail": detail,
                "journal": {"path": journal.as_posix(), "bytes": journal.stat().st_size, "sha256": _sha(journal)},
                "authorization": {"rerun": False, "alternate_query": False, "partial_universe": False, "entropy": False, "selection": False},
            }
            with failure_path.open("xb") as output:
                output.write(canonical_json_bytes(failure) + b"\n")
            raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--failure-receipt", type=Path, required=True)
    parser.add_argument("--preaction-authority", type=Path, required=True)
    parser.add_argument("--execute-once", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if args.execute_once == args.preflight:
        parser.error("choose exactly one of --execute-once or --preflight")
    authority.verify_static_authorities()
    _verify_preaction(args.preaction_authority)
    if args.preflight:
        print(json.dumps({
            "status": "PREFLIGHT_PASS__NO_NETWORK",
            "provider_order": list(core.PROVIDER_ORDER),
            "term_count": len(core.TERMS),
            "minimum_network_calls": 22,
            "single_expansion_ordinal": 1,
        }, sort_keys=True))
        return 0
    result = execute_once(args.preaction_authority, args.journal, args.transcript, args.failure_receipt)
    transcript = result["transcript"]
    print(json.dumps({
        "status": "COMPLETE_SINGLE_EXPANSION",
        "network_call_count": transcript["network_call_count"],
        "query_count": len(transcript["queries"]),
        "transcript": {"path": args.transcript.as_posix(), "bytes": args.transcript.stat().st_size, "sha256": _sha(args.transcript)},
        "journal": {"path": args.journal.as_posix(), "bytes": args.journal.stat().st_size, "sha256": _sha(args.journal)},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
