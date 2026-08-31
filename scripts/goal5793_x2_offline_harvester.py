#!/usr/bin/env python3
"""Run the frozen Goal5793 X2 harvester over offline transcript bytes only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts.goal5793_x2_offline_core import (
    X2Error,
    build_exposure_alias_rows,
    build_identity_components,
    validate_offline_transcript,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPOSURE = ROOT / "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json"
DEFAULT_OUTPUT = ROOT / "history/internal_docs/goal5793_x2_offline_harvester_fixture_result_20260822.json"
EXPOSURE_SHA256 = "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_result(transcript_path: Path, exposure_path: Path = DEFAULT_EXPOSURE) -> dict[str, Any]:
    if not transcript_path.is_file() or transcript_path.is_symlink():
        raise X2Error("OFFLINE_TRANSCRIPT_FILE_INVALID")
    if not exposure_path.is_file() or exposure_path.is_symlink() or _sha256(exposure_path) != EXPOSURE_SHA256:
        raise X2Error("EXPOSURE_REGISTRY_IDENTITY_MISMATCH")
    try:
        transcript = json.loads(transcript_path.read_text(encoding="utf-8", errors="strict"))
        exposure_registry = json.loads(exposure_path.read_text(encoding="utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise X2Error("OFFLINE_INPUT_JSON_INVALID") from exc
    harvested = validate_offline_transcript(transcript)
    exposure_rows = build_exposure_alias_rows(exposure_registry)
    components = build_identity_components(harvested["raw_nodes"], exposure_rows)
    counts = {
        "query_count": harvested["query_count"],
        "response_page_count": len(harvested["response_evidence"]),
        "raw_node_count": harvested["raw_node_count"],
        "component_count": len(components),
        "preexisting_exposure_component_count": sum(
            component["identity_disposition"] == "PREEXISTING_PROJECT_EXPOSURE__SELECTION_INELIGIBLE"
            for component in components
        ),
        "identity_conflict_component_count": sum(component["identity_conflict"] for component in components),
        "fallback_ambiguous_component_count": sum(component["fallback_identity_ambiguous"] for component in components),
        "not_yet_science_eligible_component_count": sum(component["identity_stage_selection_eligible"] for component in components),
        "network_call_count": 0,
        "live_provider_call_count": 0,
        "candidate_decision_invocation_count": 0,
        "entropy_or_selection_count": 0,
    }
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.offline_harvester_fixture_result.v1",
        "status": "OFFLINE_SYNTHETIC_FIXTURE_HARVEST_VALIDATED__NOT_LIVE_SEARCH__NOT_X3_UNIVERSE",
        "transcript": {
            "path": transcript_path.as_posix(),
            "bytes": transcript_path.stat().st_size,
            "sha256": _sha256(transcript_path),
            "synthetic_fixture": True,
        },
        "exposure_registry": {
            "path": exposure_path.relative_to(ROOT).as_posix() if exposure_path.is_relative_to(ROOT) else exposure_path.as_posix(),
            "bytes": exposure_path.stat().st_size,
            "sha256": _sha256(exposure_path),
            "bibliography_entries": len(exposure_rows),
            "missing_strong_identifier_entries": sum(not row["strong_identifier_present"] for row in exposure_rows),
        },
        "counts": counts,
        "raw_nodes": harvested["raw_nodes"],
        "components": components,
        "response_evidence": harvested["response_evidence"],
        "scope": {
            "fixture_only": True,
            "live_search_executed_or_authorized": False,
            "literature_completeness_claimed": False,
            "not_matched_to_declared_exposure_means_unseen": False,
            "generalization_or_usability_evidence_count": 0,
        },
        "authorization": {
            "x3_live_search": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "publication_submission": False,
        },
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(
        result,
        seal_field="result_sha256",
        domain="rtdl.goal5793.x2.offline_harvester_fixture_result",
        version=1,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--exposure-registry", type=Path, default=DEFAULT_EXPOSURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    result = build_result(args.transcript, args.exposure_registry)
    payload = canonical_json_bytes(result) + b"\n"
    if not args.write_create_only:
        print(json.dumps({"status": "DRY_RUN_NO_HISTORY_WRITE", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}))
        return 0
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("CREATE_ONLY_OUTPUT_ALREADY_EXISTS")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps({"path": args.output.as_posix(), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

