#!/usr/bin/env python3
"""Run the Goal5446 X-HD external artifact dropbox gate.

The dropbox is a fixed place for authorized local artifacts after an external
action produces them. This gate records file names, hashes, and conservative
next-gate recommendations.

It does not download artifacts, extract archives, inspect private content,
run POD, run author code, run RTDL routes, or upgrade any reproduction claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import zipfile


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
REQUESTS = APP / "requests"
RESULTS = APP / "results"
DEFAULT_DROPBOX = REQUESTS / "artifacts"
OUT = RESULTS / "xhd_goal5446_external_artifact_dropbox_gate.json"


ARCHIVE_SUFFIXES = (".zip", ".tar", ".tgz", ".tar.gz", ".tar.zst", ".7z", ".bz2", ".gz")
RESPONSE_SUFFIXES = (".json",)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_readme(dropbox: Path) -> None:
    dropbox.mkdir(parents=True, exist_ok=True)
    readme = dropbox / "README.md"
    if readme.exists():
        return
    readme.write_text(
        "\n".join(
            [
                "# X-HD External Artifact Dropbox",
                "",
                "Status: `empty_waiting_for_authorized_artifact`",
                "",
                "Place only owner-authorized local artifacts here, such as an ACM",
                "supplement zip, an author-provided input archive, or a normalized",
                "response JSON. Do not commit private raw correspondence or",
                "redistribution-restricted bytes unless explicitly allowed.",
                "",
                "Run:",
                "",
                "```text",
                "py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5446_external_artifact_dropbox_gate.py",
                "```",
                "",
                "This gate only records file hashes and next-gate recommendations.",
                "It does not extract archives, run POD, or claim exact paper",
                "reproduction.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _candidate_files(dropbox: Path) -> list[Path]:
    if not dropbox.exists():
        return []
    files = []
    for path in sorted(p for p in dropbox.rglob("*") if p.is_file()):
        rel = path.relative_to(dropbox).as_posix().lower()
        if rel == "readme.md":
            continue
        files.append(path)
    return files


def _kind(path: Path) -> str:
    lower = path.name.lower()
    if lower.endswith(RESPONSE_SUFFIXES):
        return "normalized_or_raw_json_candidate"
    if lower.endswith(ARCHIVE_SUFFIXES):
        if lower.endswith(".zip") and zipfile.is_zipfile(path):
            if "ics26" in lower or "supplement" in lower or "acm" in lower:
                return "acm_or_supplement_zip_candidate"
            return "zip_archive_candidate"
        return "archive_candidate"
    return "manual_review_candidate"


def _next_gate(kind: str) -> str:
    if kind == "acm_or_supplement_zip_candidate":
        return "inspect_xhd_acm_supplement_zip_then_acm_artifact_instruction_ingestion_if_actionable"
    if kind == "zip_archive_candidate":
        return "review_archive_identity_then_run_acm_or_author_archive_intake_if_applicable"
    if kind == "archive_candidate":
        return "record_hash_and_request_extraction_policy_before_any_pod_gate"
    if kind == "normalized_or_raw_json_candidate":
        return "validate_or_ingest_external_response_json_before_any_pod_gate"
    return "manual_review_before_any_pod_gate"


def _file_record(path: Path, dropbox: Path) -> dict[str, Any]:
    kind = _kind(path)
    return {
        "path": _rel(path),
        "dropbox_relative_path": path.relative_to(dropbox).as_posix(),
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "kind": kind,
        "is_zipfile": bool(path.name.lower().endswith(".zip") and zipfile.is_zipfile(path)),
        "recommended_next_gate": _next_gate(kind),
        "pod_allowed_from_this_record": False,
        "claim_exact_input_from_this_record": False,
    }


def build_gate(dropbox: Path = DEFAULT_DROPBOX) -> dict[str, Any]:
    _write_readme(dropbox)
    files = _candidate_files(dropbox)
    records = [_file_record(path, dropbox) for path in files]

    if records:
        status = "external_artifact_dropbox_candidates_present__requires_intake_gate"
        next_action = "run_the_record_specific_intake_gate_before_any_pod_or_claim"
    else:
        status = "external_artifact_dropbox_empty__await_authorized_artifact"
        next_action = "obtain_authorized_acm_zip_author_archive_hash_manifest_or_response"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5446.external_artifact_dropbox_gate.v1",
        "goal": "Goal5446",
        "date": "2026-07-10",
        "status": status,
        "dropbox_dir": _rel(dropbox),
        "artifact_candidate_count": len(records),
        "records": records,
        "next_action": next_action,
        "exact_input_blocker_removed": False,
        "external_artifacts_acquired": bool(records),
        "pod_expected_next": False,
        "claim_boundary": {
            "external_artifact_dropbox_scanned": True,
            "external_artifacts_acquired": bool(records),
            "acm_supplement_inspected": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Dropbox scan only. POD requires a later intake/classifier gate and strict review.",
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external artifact dropbox gate / intake workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: external artifact intake governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming exact paper dataset reproduction from this dropbox scan alone",
            "claiming ACM supplement inspection from this dropbox scan alone",
            "claiming Figure 5 or full X-HD reproduction from this dropbox scan alone",
            "claiming author-vs-RTDL performance ratio from this dropbox scan alone",
            "running POD or route work from this dropbox scan alone",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dropbox", type=Path, default=DEFAULT_DROPBOX)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)

    payload = build_gate(args.dropbox)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "artifact_candidate_count": payload["artifact_candidate_count"],
                "exact_input_blocker_removed": payload["exact_input_blocker_removed"],
                "pod_expected_next": payload["pod_expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
