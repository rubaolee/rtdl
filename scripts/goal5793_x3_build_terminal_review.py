#!/usr/bin/env python3
"""Build the terminal X3 provider-search audit and sole external-review CFR."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
JOURNAL = HISTORY / "goal5793_x3_provider_search_journal_20260822.jsonl"
FAILURE = HISTORY / "goal5793_x3_provider_search_terminal_failure_20260822.json"
TRANSCRIPT = HISTORY / "goal5793_x3_provider_search_transcript_20260822.json"
COMPLETE_AUTHORITY = HISTORY / "goal5793_x3_provider_search_authority_20260822.json"
AUDIT_NAME = "goal5793_x3_provider_search_terminal_audit_v2_20260822.json"
REPORT_NAME = "goal5793_x3_provider_search_terminal_report_v2_20260822.md"
CFR_NAME = "call_for_review_goal5793_x3_provider_search_terminal_failure_v2_20260822.md"
AUDIT_DOMAIN = "rtdl.goal5793.x3.provider_search_terminal_audit.v2"
AUDIT_VERSION = 2

PINNED = {
    "history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json": (4130, "ce3f83ef318085646cefdbbfbcc4290b66e745aa9ee88f4b041f84661997e659"),
    "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json": (56110, "126ee3c1dfe930a7bb25b2f19df8a6c4889c7ef8b619abe3cc69da54efa8b7c2"),
    "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json": (476230, "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"),
    "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json": (461251, "72a30e8b2a8998507ca2f27517346006f62ef6b370f9777a54bddf9dd8edae8b"),
    "history/internal_docs/goal5793_x3_provider_search_preaction_authority_20260822.json": (4069, "e43bd6fdbaddf35e80485113b79224403839d17f4225baad974c8aed404346a7"),
    "history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl": (9326661, "94ab0fc951c728569c0d57f649de918feeb547a8f4dac0ea48ec43f176b7e4c5"),
    "history/internal_docs/goal5793_x3_provider_search_terminal_failure_20260822.json": (587, "6a9f7228ff918c7c4a91c956f5ff5d12f09361c7e71eaf6e65a20054d330e2fd"),
    "scripts/goal5793_x3_capture_provider_search.py": (18977, "b70c85b24f2892888cca6466b8e233f9a853a7389aa5e47ce10b714b58c9d909"),
    "scripts/goal5793_x3_provider_search_authority.py": (11959, "3caa4bd799a523b35df3d1a9177db940c615b3379a767d315c2bd13bb202ea09"),
    "scripts/goal5793_x3_build_provider_search_preaction.py": (7575, "7ae3a1ca46753ad5ab03b64b0c149d28c3b7317ce158a61e8b233aa59364dd2f"),
    "tests/goal5793_x3_provider_search_test.py": (10232, "86d5646212c8d34ccdf2909ca017d5d0b249c7809d079c74e7f714d0680fcaea"),
    "tests/goal5793_x3_provider_search_preaction_test.py": (3139, "d2cf5bf64185e76bbf2c030cb390459d9ed2b9d16a045ea128f2a201eb5e39ef"),
    "scripts/goal5793_x2_offline_core.py": (57162, "48922c941f0ab11df9b507fefa06836e72ee7a479bb9c02ffe2e4700dc87be83"),
    "scripts/goal5793_x1_canonical.py": (3099, "13b22dbae22b0a70763fdf46031c7975ab1eaebe20c37789f397242b7a1c9b3a"),
}
SOURCE_ROOTS = (
    "scripts/goal5793_x3_build_terminal_review.py",
    "tests/goal5793_x3_terminal_review_test.py",
)


def _identity(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _verify_pins() -> None:
    for relative, (size, digest) in PINNED.items():
        row = _identity(relative)
        if row["bytes"] != size or row["sha256"] != digest:
            raise RuntimeError(f"PINNED_IDENTITY_MISMATCH:{relative}")
    if TRANSCRIPT.exists() or TRANSCRIPT.is_symlink() or COMPLETE_AUTHORITY.exists() or COMPLETE_AUTHORITY.is_symlink():
        raise RuntimeError("FORBIDDEN_COMPLETE_OUTPUT_EXISTS_AFTER_TERMINAL_FAILURE")


def _url_diagnostics(results: list[Mapping[str, Any]]) -> dict[str, Any]:
    invalid: list[dict[str, Any]] = []
    first_parser_failure: dict[str, Any] | None = None
    for index, work in enumerate(results):
        try:
            core._openalex_url_slots(
                work,
                core.normalize_doi(work.get("doi") or (work.get("ids") or {}).get("doi")),
                (work.get("ids") or {}).get("arxiv"),
            )
        except core.X2Error as exc:
            if first_parser_failure is None:
                first_parser_failure = {"result_index": index, "work_id": work.get("id"), "reason": str(exc)}
        locations = []
        for name in ("primary_location", "best_oa_location"):
            if isinstance(work.get(name), Mapping):
                locations.append((name, work[name]))
        for location_index, location in enumerate(work.get("locations") or []):
            if isinstance(location, Mapping):
                locations.append((f"locations[{location_index}]", location))
        for location_name, location in locations:
            for field in ("landing_page_url", "pdf_url"):
                value = location.get(field)
                if isinstance(value, str):
                    try:
                        core.normalize_https_url(value)
                    except core.X2Error:
                        invalid.append({
                            "result_index": index,
                            "work_id": work.get("id"),
                            "location": location_name,
                            "field": field,
                            "value": value,
                        })
    if first_parser_failure != {"result_index": 3, "work_id": "https://openalex.org/W2973457155", "reason": "SOURCE_URL_INVALID"}:
        raise RuntimeError("FIRST_PARSER_FAILURE_MISMATCH")
    if len(invalid) != 217:
        raise RuntimeError("INVALID_PROVIDER_URL_DENOMINATOR_MISMATCH")
    first_invalid = next(row for row in invalid if row["result_index"] == 3)
    return {
        "invalid_location_value_count": len(invalid),
        "affected_result_count": len({row["result_index"] for row in invalid}),
        "first_parser_failure": first_parser_failure,
        "first_invalid_value_in_failed_work": first_invalid,
        "scheme_counts": {
            "http": sum(str(row["value"]).lower().startswith("http://") for row in invalid),
            "malformed_https": sum(str(row["value"]).lower().startswith("https://") for row in invalid),
            "other": sum(not str(row["value"]).lower().startswith(("http://", "https://")) for row in invalid),
        },
        "all_invalid_values_sha256": hashlib.sha256(canonical_json_bytes(invalid)).hexdigest(),
        "sample_first_20": invalid[:20],
    }


def build_audit() -> dict[str, Any]:
    _verify_pins()
    lines = [json.loads(line) for line in JOURNAL.read_text(encoding="utf-8", errors="strict").splitlines()]
    if [line.get("event") for line in lines] != ["TRANSACTION_START", "HTTP_ATTEMPT", "TRANSACTION_TERMINAL_FAILURE"]:
        raise RuntimeError("JOURNAL_EVENT_SET_MISMATCH")
    start, attempt_event, terminal = lines
    attempt = attempt_event["attempt"]
    if attempt_event.get("provider") != "OpenAlex Works API" or attempt_event.get("request_sequence") != 0:
        raise RuntimeError("FIRST_REQUEST_IDENTITY_MISMATCH")
    if attempt_event.get("params") != core._openalex_params(core.TERMS[0], "*"):
        raise RuntimeError("FIRST_REQUEST_PARAMS_MISMATCH")
    if attempt.get("status") != 200 or attempt.get("error") is not None or attempt.get("attempt") != 1:
        raise RuntimeError("FIRST_REQUEST_RECEIPT_MISMATCH")
    body = base64.b64decode(attempt["body_base64"], validate=True)
    body_json = json.loads(body)
    if len(body_json.get("results", [])) != 200 or body_json.get("meta", {}).get("next_cursor") is None:
        raise RuntimeError("FIRST_RESPONSE_PAGE_SHAPE_MISMATCH")
    try:
        core._parse_openalex(body, term=core.TERMS[0], query_index=0, page_index=0)
    except core.X2Error as exc:
        replay_reason = str(exc)
    else:
        raise RuntimeError("TERMINAL_FAILURE_NOT_REPRODUCED")
    if replay_reason != "SOURCE_URL_INVALID":
        raise RuntimeError("TERMINAL_FAILURE_REASON_MISMATCH")
    failure = json.loads(FAILURE.read_text(encoding="utf-8", errors="strict"))
    if failure["journal"] != _identity("history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl"):
        raise RuntimeError("FAILURE_RECEIPT_JOURNAL_BINDING_MISMATCH")
    if terminal.get("reason") != failure.get("reason") or failure.get("authorization") != {
        "alternate_query": False, "entropy": False, "partial_universe": False, "rerun": False, "selection": False
    }:
        raise RuntimeError("TERMINAL_DISPOSITION_MISMATCH")
    audit: dict[str, Any] = {
        "schema": "rtdl.goal5793.x3.provider_search_terminal_audit.v2",
        "date": "2026-08-22",
        "status": "TERMINAL_SINGLE_EXPANSION_INFRA_FAILURE__NO_PARTIAL_UNIVERSE__NO_RERUN",
        "pinned_roots": [_identity(relative) for relative in PINNED],
        "source_roots": [_identity(relative) for relative in SOURCE_ROOTS],
        "event_counts": {
            "transaction_start": 1,
            "http_attempt": 1,
            "http_200": 1,
            "query_complete": 0,
            "transaction_complete": 0,
            "terminal_failure": 1,
        },
        "first_request": {
            "provider": attempt_event["provider"],
            "term": core.TERMS[0],
            "params": attempt_event["params"],
            "status": attempt["status"],
            "response_body_bytes": len(body),
            "response_body_sha256": hashlib.sha256(body).hexdigest(),
            "result_count": len(body_json["results"]),
            "next_cursor_present": True,
        },
        "failure_replay": {
            "reviewed_x2_parser_reason": replay_reason,
            "outer_terminal_reason": failure["reason"],
            "detail": failure["detail"],
            "url_diagnostics": _url_diagnostics(body_json["results"]),
        },
        "absence_proof": {
            "complete_transcript_exists": False,
            "complete_component_authority_exists": False,
            "partial_universe_published": False,
            "second_http_call_count": 0,
            "rerun_count": 0,
        },
        "scientific_disposition": {
            "generalization_exam_count": 0,
            "usability_study_count": 0,
            "candidate_count": None,
            "candidate_count_semantics": "UNDEFINED__NO_COMPLETE_POPULATION_EXISTS",
            "result_is_not_zero_candidates": True,
            "result_is_infrastructure_failure_before_a_complete_population": True,
            "goal5793_generality_objective_discharged": False,
        },
        "presentation_correction": {
            "scope": "AUDIT_AND_REVIEW_PACKAGING_ONLY__NO_RAW_OR_SCIENTIFIC_STATE_CHANGED",
            "defect": "UNSENT_V1_AUDIT_ENCODED_CANDIDATE_COUNT_AS_ZERO_WHILE_CORRECTLY_STATING_RESULT_IS_NOT_ZERO_CANDIDATES",
            "correction": "CANDIDATE_COUNT_IS_NULL_AND_EXPLICITLY_UNDEFINED_BECAUSE_NO_COMPLETE_POPULATION_EXISTS",
            "superseded_unsent_v1": {
                "audit": {"bytes": 8785, "sha256": "95556f80bd22613f9057344f90b7a08d2737e11c607ba926761d1008064b91f3"},
                "report": {"bytes": 1382, "sha256": "ec7407e89d23eacdf7472e8820052444710cdeefb07ebddf4a0f1e947fbe8adf"},
                "sole_cfr": {"bytes": 10478195, "sha256": "418b6d2930b8f35ba4dab487538c725498e2438f002472e6f49bcfd5babd20f6"},
            },
            "v1_was_sent_for_external_review": False,
            "provider_call_count_changed": False,
            "journal_or_failure_receipt_changed": False,
        },
        "authorization": {
            "provider_search_rerun": False,
            "alternate_query_or_provider": False,
            "partial_universe_use": False,
            "full_text_resolution": False,
            "science_row_construction": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "product_change": False,
            "publication_submission": False,
        },
        "next_permitted_action": "OWNER_CONTROLLED_EXTERNAL_REVIEW_OF_THIS_TERMINAL_LINEAGE_THROUGH_THE_SOLE_CFR",
        "audit_sha256": "",
    }
    audit["audit_sha256"] = seal_document(audit, seal_field="audit_sha256", domain=AUDIT_DOMAIN, version=AUDIT_VERSION)
    return audit


def _report() -> str:
    return """# Goal5793 X3 provider-search terminal report

The single authorized expansion terminated on the first OpenAlex page. The request itself succeeded once with HTTP 200 and returned 200 records plus a non-null next cursor. Before a second HTTP call, the reviewed X2 parser rejected a provider-supplied `http://` location as `SOURCE_URL_INVALID`. The exact first rejected record is OpenAlex `W2973457155`; its sixth location carries `http://doi.org/10.1107/S2059798319011471`. The page contains 217 location values rejected by the normalizer: 214 `http://` values and three malformed `https://` values.

This exposes a real offline-to-live validity gap: synthetic fixtures never exercised ordinary non-HTTPS URLs in raw OpenAlex location metadata. The downstream no-follow/source-resolution policy was applied as a fatal raw-record parsing rule. The project did not delete the record, coerce the URL, continue pagination, change the vocabulary, issue a second request, or publish a partial population.

Under the frozen single-expansion policy this is terminal infrastructure failure, not zero candidates and not a generalization result. Generalization exams remain 0; usability studies remain 0. No rerun, alternate query, full-text resolution, science-row construction, entropy, selection, candidate work, GPU/SSH/POD, timing, product change, publication or submission is authorized.

Presentation correction: an unsent local v1 audit encoded `candidate_count: 0` while also correctly stating that this was not a zero-candidate result. V2 replaces that contradictory presentation with `candidate_count: null` and the explicit semantic `UNDEFINED__NO_COMPLETE_POPULATION_EXISTS`. The raw journal, failure receipt, one-call lineage, and every scientific fact are unchanged.
"""


def build_documents() -> dict[str, bytes]:
    audit = build_audit()
    audit_bytes = canonical_json_bytes(audit) + b"\n"
    report = _report().encode("utf-8")
    embedded_paths = [*PINNED.keys(), *SOURCE_ROOTS]
    rows = [
        {"path": f"history/internal_docs/{AUDIT_NAME}", "bytes": len(audit_bytes), "sha256": hashlib.sha256(audit_bytes).hexdigest()},
        {"path": f"history/internal_docs/{REPORT_NAME}", "bytes": len(report), "sha256": hashlib.sha256(report).hexdigest()},
        *[_identity(path) for path in embedded_paths],
    ]
    table = "\n".join(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |" for row in rows)
    fence = "`" * 8
    blocks = [
        f"## Embedded `{AUDIT_NAME}`\n\n{fence}json\n{audit_bytes.decode().rstrip()}\n{fence}",
        f"## Embedded `{REPORT_NAME}`\n\n{fence}markdown\n{report.decode().rstrip()}\n{fence}",
    ]
    for relative in embedded_paths:
        raw = (ROOT / relative).read_bytes().decode("utf-8", errors="strict").rstrip("\n")
        language = "jsonl" if relative.endswith(".jsonl") else "json" if relative.endswith(".json") else "python"
        blocks.append(f"## Embedded `{relative}`\n\n{fence}{language}\n{raw}\n{fence}")
    sole = "SEND ONLY " + "THIS FILE"
    embedded = "\n\n".join(blocks)
    cfr = f"""# Call for external review: Goal5793 X3 terminal provider-search lineage

**{sole}.** It embeds the exact journal including the raw HTTP response, failure receipt, preaction authority, implementation/tests, audit and report. Do not send a packet or second attachment.

This v2 CFR supersedes an unsent local v1 review package only to correct the contradictory presentation `candidate_count: 0` to `candidate_count: null` / undefined. No network, parser, journal, failure receipt, or scientific result changed.

## Requested ruling

Please return P0/P1/P2/P3 and answer:

1. Does the journal prove exactly one HTTP attempt, HTTP 200, zero completed queries, zero second calls, and the exact terminal `SOURCE_URL_INVALID` replay?
2. Does the embedded raw page independently reproduce 200 records, a non-null next cursor, 217 rejected location values (214 `http://` plus three malformed `https://`), and first failure at OpenAlex W2973457155?
3. Is this correctly classified as terminal infrastructure failure rather than zero candidates, generalization evidence, or a scientific 0/3 result?
4. Under the frozen single-expansion/no-rerun policy, must Goal5793 stop without parser repair, new queries, partial-universe use or a second provider search?
5. May append-only owner closure mark the Goal5793 prospective-generalization branch terminal-negative/undischarged while authorizing no successor science, entropy, selection or candidate stage?

Generalization exams = 0. Usability studies = 0. Candidate count is undefined because no complete population exists.

## Exact embedded roots

| Path | Bytes | SHA-256 |
|---|---:|---|
{table}

{embedded}
""".encode("utf-8")
    return {AUDIT_NAME: audit_bytes, REPORT_NAME: report, CFR_NAME: cfr}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HISTORY)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    documents = build_documents()
    if args.write_create_only:
        targets = [args.output_dir / name for name in documents]
        if any(path.exists() or path.is_symlink() for path in targets):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in documents.items():
            with (args.output_dir / name).open("xb") as stream:
                stream.write(data)
        status = "CREATE_ONLY_TERMINAL_REVIEW_WRITE_PASS"
    elif args.verify_stored:
        for name, data in documents.items():
            path = args.output_dir / name
            if not path.is_file() or path.is_symlink() or path.read_bytes() != data:
                raise SystemExit(f"STORED_OUTPUT_MISMATCH:{name}")
        status = "POSTWRITE_TERMINAL_REVIEW_VERIFY_PASS"
    else:
        status = "DRY_RUN_TERMINAL_REVIEW_PASS"
    print(json.dumps({"status": status, "documents": [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in documents.items()]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
