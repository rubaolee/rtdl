#!/usr/bin/env python3
"""Validate and seal the one live Goal5793 X3 provider-search transcript.

The reviewed X2 core is reused only through an explicit projection that changes
the live-origin envelope to its offline-fixture envelope.  Raw attempts and the
outer authority remain truthfully marked live; the projection proves schedule,
pagination, parser, normalisation and component parity, not offline origin.
"""

from __future__ import annotations

import argparse
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
EXPOSURE = ROOT / "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json"
EXPOSURE_SHA256 = "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"
CLOSURE = ROOT / "history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json"
CLOSURE_SHA256 = "ce3f83ef318085646cefdbbfbcc4290b66e745aa9ee88f4b041f84661997e659"
ALIAS_V2 = ROOT / "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json"
ALIAS_V2_SHA256 = "72a30e8b2a8998507ca2f27517346006f62ef6b370f9777a54bddf9dd8edae8b"
TRANSCRIPT_DOMAIN = "rtdl.goal5793.x3.provider_search_transcript"
AUTHORITY_DOMAIN = "rtdl.goal5793.x3.provider_search_authority"


class X3SearchError(RuntimeError):
    def __init__(self, reason_id: str, detail: str | None = None):
        self.reason_id = reason_id
        self.detail = detail
        super().__init__(reason_id if detail is None else f"{reason_id}:{detail}")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": _sha(path)}


def _exact_keys(value: Mapping[str, Any], expected: set[str], reason: str) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise X3SearchError(reason)


def verify_static_authorities() -> dict[str, Any]:
    expected = ((CLOSURE, CLOSURE_SHA256), (EXPOSURE, EXPOSURE_SHA256), (ALIAS_V2, ALIAS_V2_SHA256))
    for path, digest in expected:
        if not path.is_file() or path.is_symlink() or _sha(path) != digest:
            raise X3SearchError("STATIC_AUTHORITY_IDENTITY_MISMATCH", path.as_posix())
    closure = json.loads(CLOSURE.read_text(encoding="utf-8", errors="strict"))
    auth = closure.get("authorization")
    if not isinstance(auth, Mapping) or auth.get("x3_provider_search") is not True:
        raise X3SearchError("X3_PROVIDER_SEARCH_NOT_AUTHORIZED")
    if [key for key, value in auth.items() if value] != ["x3_provider_search"]:
        raise X3SearchError("CLOSURE_AUTHORIZATION_ESCALATION")
    controlling = closure.get("controlling_implementations")
    if not isinstance(controlling, Mapping) or controlling.get("v1_predecessors_may_produce_a_stage_of_record_output") is not False:
        raise X3SearchError("CONTROLLING_IMPLEMENTATION_BINDING_MISSING")
    alias = json.loads(ALIAS_V2.read_text(encoding="utf-8", errors="strict"))
    if alias.get("counts", {}).get("strong_identifier_rows") != 7 or alias.get("counts", {}).get("weak_identifier_rows_with_author_year_fallback_path") != 176 or alias.get("counts", {}).get("weak_identifier_rows_exact_title_only") != 3:
        raise X3SearchError("CONTROLLING_ALIAS_COUNT_MISMATCH")
    if any(row.get("selection_eligible") is not False for row in alias.get("rows", [])):
        raise X3SearchError("CONTROLLING_ALIAS_ELIGIBILITY_ESCALATION")
    return {"closure": _identity(CLOSURE), "exposure_registry": _identity(EXPOSURE), "alias_v2": _identity(ALIAS_V2)}


def validate_live_transcript(transcript: Mapping[str, Any]) -> dict[str, Any]:
    static = verify_static_authorities()
    _exact_keys(
        transcript,
        {
            "schema", "mode", "synthetic_fixture", "single_expansion_ordinal",
            "provider_search_started_at_utc", "provider_search_ended_at_utc",
            "network_call_count", "worker_count", "concurrent_requests", "queries",
            "manual_row_deletion_count", "live_beacon_call_count", "entropy_draw_count",
            "candidate_work_count", "authorization", "transcript_sha256",
        },
        "LIVE_TRANSCRIPT_SCHEMA_MISMATCH",
    )
    if transcript["schema"] != "rtdl.goal5793.x3.provider_search_transcript.v1":
        raise X3SearchError("LIVE_TRANSCRIPT_SCHEMA_MISMATCH")
    if transcript["mode"] != "LIVE_PROVIDER_SEARCH_SINGLE_EXPANSION" or transcript["synthetic_fixture"] is not False:
        raise X3SearchError("LIVE_TRANSCRIPT_ORIGIN_MISLABELLED")
    if type(transcript["single_expansion_ordinal"]) is not int or transcript["single_expansion_ordinal"] != 1:
        raise X3SearchError("SINGLE_EXPANSION_ORDINAL_MISMATCH")
    for field in ("manual_row_deletion_count", "live_beacon_call_count", "entropy_draw_count", "candidate_work_count"):
        if type(transcript[field]) is not int or transcript[field] != 0:
            raise X3SearchError("FORBIDDEN_ACTIVITY_IN_PROVIDER_SEARCH", field)
    if transcript["worker_count"] != 1 or transcript["concurrent_requests"] is not False:
        raise X3SearchError("PROVIDER_SEARCH_CONCURRENCY_MISMATCH")
    if not isinstance(transcript["queries"], list) or len(transcript["queries"]) != 22:
        raise X3SearchError("PROVIDER_SEARCH_QUERY_COUNT_MISMATCH")
    call_count = sum(
        len(lineage.get("attempts", []))
        for query in transcript["queries"]
        for lineage in query.get("request_lineages", [])
    )
    if type(transcript["network_call_count"]) is not int or transcript["network_call_count"] != call_count or call_count < 22:
        raise X3SearchError("LIVE_NETWORK_CALL_DENOMINATOR_MISMATCH")
    authorization = transcript["authorization"]
    if not isinstance(authorization, Mapping) or any(authorization.values()):
        raise X3SearchError("TRANSCRIPT_AUTHORIZATION_ESCALATION")
    expected_seal = seal_document(
        transcript, seal_field="transcript_sha256", domain=TRANSCRIPT_DOMAIN, version=1
    )
    if transcript["transcript_sha256"] != expected_seal:
        raise X3SearchError("LIVE_TRANSCRIPT_SEAL_MISMATCH")

    # The reviewed parser intentionally rejects network-origin envelopes.  The
    # projection changes only those three origin/count literals and is never
    # persisted or represented as a real transcript.
    projection = {
        "schema": core.SCHEMA_TRANSCRIPT,
        "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True,
        "network_call_count": 0,
        "worker_count": transcript["worker_count"],
        "concurrent_requests": transcript["concurrent_requests"],
        "queries": transcript["queries"],
    }
    try:
        harvested = core.validate_offline_transcript(projection)
    except core.X2Error as exc:
        raise X3SearchError("REVIEWED_X2_TRANSCRIPT_VALIDATION_FAILED", str(exc)) from exc
    registry = json.loads(EXPOSURE.read_text(encoding="utf-8", errors="strict"))
    exposure_rows = core.build_exposure_alias_rows(registry)
    components = core.build_identity_components(harvested["raw_nodes"], exposure_rows)
    return {
        "static_authorities": static,
        "harvested": harvested,
        "components": components,
        "projection_boundary": {
            "live_origin_lost_or_relabelled": False,
            "projection_persisted_as_evidence": False,
            "reviewed_x2_parser_reuse_only": True,
            "projected_fields": {
                "schema": core.SCHEMA_TRANSCRIPT,
                "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
                "synthetic_fixture": True,
                "network_call_count": 0,
            },
        },
    }


def build_authority(transcript_path: Path) -> dict[str, Any]:
    if not transcript_path.is_file() or transcript_path.is_symlink():
        raise X3SearchError("LIVE_TRANSCRIPT_FILE_INVALID")
    try:
        transcript = json.loads(transcript_path.read_text(encoding="utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise X3SearchError("LIVE_TRANSCRIPT_JSON_INVALID") from exc
    validated = validate_live_transcript(transcript)
    harvested = validated["harvested"]
    components = validated["components"]
    disposition_counts: dict[str, int] = {}
    for component in components:
        key = component["identity_disposition"]
        disposition_counts[key] = disposition_counts.get(key, 0) + 1
    authority: dict[str, Any] = {
        "schema": "rtdl.goal5793.x3.provider_search_authority.v1",
        "status": "COMPLETE_SINGLE_LIVE_PROVIDER_SEARCH__RAW_UNIVERSE_FROZEN__NO_SCIENCE_ROWS_OR_SELECTION",
        "transcript": _identity(transcript_path),
        "static_authorities": validated["static_authorities"],
        "counts": {
            "query_count": harvested["query_count"],
            "response_page_count": len(harvested["response_evidence"]),
            "network_call_count": transcript["network_call_count"],
            "raw_node_count": harvested["raw_node_count"],
            "identity_component_count": len(components),
            "dispositions": dict(sorted(disposition_counts.items())),
            "science_row_count": 0,
            "full_text_resolution_count": 0,
            "entropy_draw_count": 0,
            "selection_count": 0,
            "candidate_work_count": 0,
            "generalization_exam_count": 0,
            "usability_study_count": 0,
        },
        "raw_nodes": harvested["raw_nodes"],
        "identity_components": components,
        "response_evidence": harvested["response_evidence"],
        "projection_boundary": validated["projection_boundary"],
        "claim_boundary": {
            "literature_complete": False,
            "provider_query_defined_population_only": True,
            "not_matched_to_declared_exposure_means_unseen": False,
            "selection_measure_is_over_identity_components_not_proven_underlying_works": True,
            "generalization_evidence_created": False,
            "usability_evidence_created": False,
        },
        "authorization": {
            "full_text_resolution": False,
            "science_row_construction": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "publication_submission": False,
        },
        "authority_sha256": "",
    }
    authority["authority_sha256"] = seal_document(
        authority, seal_field="authority_sha256", domain=AUTHORITY_DOMAIN, version=1
    )
    return authority


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    authority = build_authority(args.transcript)
    payload = canonical_json_bytes(authority) + b"\n"
    if args.write_create_only:
        if args.output is None or args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_INVALID_OR_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(json.dumps({"status": "PASS", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "authority_sha256": authority["authority_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
