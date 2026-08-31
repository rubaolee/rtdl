#!/usr/bin/env python3
"""Build the sole-CFR pre-action review for exact pinned NIST source recovery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_build_offline_review_capsule as capsule_builder
from scripts import goal5793_x2_recover_pinned_normative_sources as recovery


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"
AUTHORITY_NAME = "goal5793_x2_normative_source_recovery_preaction_work_authority_v2_20260822.json"
CFR_NAME = "call_for_review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md"
AUTHORITY_DOMAIN = recovery.AUTHORITY_DOMAIN

PREDECESSORS = {
    "s0_protocol": "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json",
    "x1_owner_closure": "history/internal_docs/goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json",
    "x1_returned_review": "history/internal_docs/review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _identity(rel: str) -> dict[str, Any]:
    data = (ROOT / rel).read_bytes()
    return {"path": rel, "bytes": len(data), "sha256": _sha(data)}


def _x2_rows() -> list[dict[str, Any]]:
    paths = [
        *ROOT.glob("scripts/goal5793_x2_*.py"),
        *ROOT.glob("tests/goal5793_x2_*_test.py"),
        *ROOT.glob("tests/fixtures/goal5793_x2_nist/*"),
        *ROOT.glob("tests/fixtures/goal5793_x2_pdf/*"),
    ]
    rows = []
    for path in sorted(set(paths), key=lambda item: item.relative_to(ROOT).as_posix().encode("utf-8")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        rows.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": _sha(data)})
    return rows


def build_authority() -> dict[str, Any]:
    recovery_tool = _identity("scripts/goal5793_x2_recover_pinned_normative_sources.py")
    rows = _x2_rows()
    dry_capsule = capsule_builder.build_outputs()
    authority: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.normative_source_recovery_work_authority.v2",
        "goal": 5793,
        "stage": "X2_PREACTION_NORMATIVE_SOURCE_RECOVERY_AMENDMENT",
        "date": DATE,
        "status": "PREACTION_EXTERNAL_REVIEW_REQUIRED__NO_NETWORK_EXECUTION_AUTHORIZED",
        "predecessors": {name: _identity(path) for name, path in PREDECESSORS.items()},
        "supersedes_noncontrolling_v1_seal_convention_mismatch": {
            "work_authority": _identity("history/internal_docs/goal5793_x2_normative_source_recovery_preaction_work_authority_20260822.json"),
            "cfr": _identity("history/internal_docs/call_for_review_goal5793_x2_normative_source_recovery_preaction_amendment_20260822.md"),
            "defect": "v1 builder used X1 canonical_digest seal while the v1 recovery tool validated a different hand-written seal framing; disk postwrite verification caught the mismatch before review or network execution",
            "v1_reviewed": False,
            "v1_sent": False,
            "v1_network_calls": 0,
            "v1_authorizes_any_action": False,
        },
        "controlling_problem": {
            "exact_pinned_normative_source_bytes_locally_available": False,
            "local_exact_length_and_sha_search_roots": ["C:/Users/Lestat", "D:/MovedFromC"],
            "local_exact_matches": 0,
            "search_observation_is_complete_mental_or_all_machine_inventory": False,
            "offline_synthetic_nist_crypto_can_substitute": False,
            "x2_normative_verifier_closeable_without_bytes": False,
        },
        "exact_sources": list(recovery.SOURCES),
        "recovery_tool": recovery_tool,
        "execution_protocol": {
            "method": "GET",
            "source_order": [source["source_id"] for source in recovery.SOURCES],
            "retry_schedule_seconds": list(recovery.RETRY_DELAYS),
            "maximum_total_http_calls": len(recovery.SOURCES) * len(recovery.RETRY_DELAYS),
            "redirects_followed": False,
            "only_exact_declared_urls": True,
            "http_200_wrong_length_or_sha": "TERMINAL_SOURCE_DRIFT__NO_RETRY_NO_ALTERNATE",
            "exhausted_transport_or_non_200": "TERMINAL_RECOVERY_FAILURE__NO_PARTIAL_WRITE",
            "raw_attempt_headers_timestamps_body_and_error_preserved": True,
            "create_only_outputs": [source["output_name"] for source in recovery.SOURCES] + ["goal5793_x2_normative_source_recovery_receipt_20260822.json"],
            "tool_requires_exact_work_authority_returned_review_and_owner_closure_bindings_before_first_call": True,
        },
        "offline_checkpoint": {
            "test_command": "bundled-python -m unittest <all thirteen current X2 offline/recovery/review suites>",
            "tests_passed": 82,
            "tests_failed": 0,
            "x2_file_count": len(rows),
            "x2_file_bytes": sum(row["bytes"] for row in rows),
            "x2_rows_sha256": _sha(canonical_json_bytes(rows)),
            "x2_rows": rows,
            "dry_capsule_outputs": [{"path": name, "bytes": len(data), "sha256": _sha(data)} for name, data in dry_capsule.items()],
            "dry_capsule_external_send_authorized": False,
            "compact_capsule_archive_bytes": len(dry_capsule[capsule_builder.ARCHIVE_NAME]),
            "compact_capsule_under_seven_mb": len(dry_capsule[capsule_builder.ARCHIVE_NAME]) < 7_000_000,
        },
        "network_execution_authorized_before_returned_review_and_owner_closure": False,
        "requested_postreview_authorization": {
            "authorizes_exact_pinned_source_recovery": True,
            "live_provider_search": False,
            "beacon_call": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "normative_verifier_result_claim": False,
            "x2_closure": False,
            "x3": False,
            "gpu": False,
            "ssh": False,
            "pod": False,
            "timing": False,
            "product_change": False,
            "publication": False,
        },
        "authorization": {
            "network": False, "live_provider_search": False, "beacon": False, "entropy": False,
            "selection": False, "candidate_work": False, "x2_closure": False, "x3": False,
            "gpu_ssh_pod": False, "timing": False, "product_change": False, "publication": False,
        },
        "external_delivery": {"send_exactly_one_file": True, "sent_file": CFR_NAME, "send_capsule_or_authority_as_second_attachment": False},
        "work_authority_sha256": "",
    }
    authority["work_authority_sha256"] = seal_document(authority, seal_field="work_authority_sha256", domain=AUTHORITY_DOMAIN, version=1)
    return authority


def build_outputs() -> dict[str, bytes]:
    authority = build_authority()
    authority_bytes = canonical_json_bytes(authority) + b"\n"
    tool_rel = authority["recovery_tool"]["path"]
    tool_bytes = (ROOT / tool_rel).read_bytes()
    cfr = f"""# Call for review — Goal5793 X2 exact normative-source recovery pre-action amendment

**SEND ONLY THIS FILE. Do not send the local authority JSON or the X2 capsule as a second attachment.**

Date: {DATE}  
Scope: v2 governance-ordering amendment and exact two-URL recovery tool only  
Current network calls: **0**  
Current beacon calls / entropy draws / selections / candidate work / GPU / SSH / POD / timings: **0 / 0 / 0 / 0 / 0 / 0 / 0 / 0**

## Why this review exists

The externally closed X1 authorizes X2 offline implementation only. The S0 protocol requires the exact pinned NIST IR 8213 draft and Beacon 2.0 XSD bytes for the normative verifier, but those bytes are absent from the local roots searched. The synthetic certificate/signature harness is deliberately non-normative and cannot close X2. Fetching now without a pre-action reviewed amendment would repeat the ordering defect already identified in X1.

This request does **not** ask you to accept X2, authorize a beacon request, run a literature search, draw entropy, select a candidate, or execute anything on GPU/SSH/POD. It asks only whether an append-only owner closure may authorize one create-only recovery transaction whose URL, method, headers, retry schedule, target length and SHA-256 are fixed below.

## Exact local work authority

Path: `history/internal_docs/{AUTHORITY_NAME}`  
Bytes: `{len(authority_bytes)}`  
SHA-256: `{_sha(authority_bytes)}`  
Internal seal: `{authority['work_authority_sha256']}`

The following code block is the complete UTF-8 authority content before its single terminal LF. It lets a reviewer holding only this CFR reconstruct and hash the local authority.

```json
{authority_bytes.decode('utf-8').rstrip(chr(10))}
```

## Exact proposed recovery tool

Path: `{tool_rel}`  
Bytes: `{len(tool_bytes)}`  
SHA-256: `{_sha(tool_bytes)}`

The following code block is the complete tool source, byte-for-byte as UTF-8. It has no Markdown fence in its source.

```python
{tool_bytes.decode('utf-8')}
```

## Required hostile conclusions

Please verify that:

1. No network call can occur without an exact work authority, returned-review identity and append-only owner closure that binds this tool.
2. The tool has exactly two fixed HTTPS targets; no query/search/beacon/API/candidate URL is accepted from CLI or payload.
3. A 200 response with wrong length or SHA terminates immediately; it cannot retry toward a convenient version or choose an alternate source.
4. Transport/non-200 retries use only `[0,3,6,12,24,48]`; exhaustion writes no partial formal output.
5. Outputs are create-only and raw attempt metadata/body identities are preserved.
6. Approval cannot be interpreted as X2 acceptance or permission for live provider search, beacon calls, entropy, selection, candidate work, GPU/SSH/POD, timing, product changes or publication.

## Requested verdict

Return explicit `P0 / P1 / P2 / P3`, and answer exactly:

- May append-only owner absorption/closure authorize **only** the exact pinned two-source recovery transaction above?
- Does any P0/P1 remain that must be repaired before the first HTTP call?
- Confirm that X2 remains unaccepted and all search/beacon/entropy/selection/candidate/execution authorizations remain false.

The returned review will itself be pinned and absorbed before any network call. After exact source recovery, the normative verifier and final X2 bytes will require their own later sole-CFR review; this amendment cannot approve future code or results.
"""
    return {AUTHORITY_NAME: authority_bytes, CFR_NAME: cfr.encode("utf-8")}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-dir", type=Path); parser.add_argument("--write-create-only", action="store_true"); args = parser.parse_args()
    if args.write_create_only != (args.output_dir is not None):
        parser.error("formal write requires --output-dir and --write-create-only together")
    outputs = build_outputs()
    if args.output_dir is not None:
        paths = [args.output_dir / name for name in outputs]
        if any(path.exists() or path.is_symlink() for path in paths):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in outputs.items():
            (args.output_dir / name).write_bytes(data)
    print(json.dumps({"status": "WRITE_PASS" if args.output_dir else "DRY_RUN_PASS", "outputs": [{"path": name, "bytes": len(data), "sha256": _sha(data)} for name, data in outputs.items()]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
