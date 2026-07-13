#!/usr/bin/env python3
"""Run the Goal5439 X-HD external-request sent-receipt gate.

This gate verifies local receipt JSON files for outbound external requests
prepared by Goal5438. It only answers: "has an owner-recorded request send
receipt been written, and does it match the prepared request file/hash?"

It does not send requests, contact remote services, inspect incoming responses,
run POD, run author code, run RTDL routes, or upgrade any reproduction claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
REQUESTS = APP / "requests"
RESULTS = APP / "results"
SENT = REQUESTS / "sent"
MANIFEST_RESULT = RESULTS / "xhd_goal5438_external_request_send_manifest.json"
OUT = RESULTS / "xhd_goal5439_external_request_sent_receipt_gate.json"

RECEIPT_SCHEMA = "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1"
MANIFEST_SCHEMA = "rtdl.paper_reproduction.xhd.goal5438.external_request_send_manifest.v1"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _receipt_files(sent_dir: Path) -> list[Path]:
    if not sent_dir.exists():
        return []
    return sorted(path for path in sent_dir.glob("*.json") if path.is_file())


def _manifest_items(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"Unexpected manifest schema: {manifest.get('schema')!r}")
    items = manifest.get("items")
    if not isinstance(items, list):
        raise ValueError("Goal5438 manifest has no items list")
    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Goal5438 manifest item is malformed")
        by_id[item["id"]] = item
    return by_id


def _required_string(receipt: dict[str, Any], key: str, errors: list[str]) -> str | None:
    value = receipt.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing_or_empty_{key}")
        return None
    return value


def _classify_receipt(path: Path, manifest_items: dict[str, dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    try:
        receipt = _load_json(path)
    except Exception as exc:
        return {
            "path": _rel(path),
            "loaded": False,
            "valid": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "request_id": None,
            "request_path": None,
            "request_sha256_at_send_time": None,
            "current_request_sha256": None,
        }

    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("unexpected_receipt_schema")
    if receipt.get("status") == "template_not_a_receipt":
        errors.append("template_not_a_receipt")
    if receipt.get("sent") is not True:
        errors.append("sent_is_not_true")

    request_id = _required_string(receipt, "request_id", errors)
    request_path = _required_string(receipt, "request_path", errors)
    request_sha = _required_string(receipt, "request_sha256_at_send_time", errors)
    _required_string(receipt, "sent_at_utc", errors)
    _required_string(receipt, "sent_by", errors)
    _required_string(receipt, "channel", errors)
    _required_string(receipt, "recipient_or_reviewer", errors)

    manifest_item = manifest_items.get(request_id or "")
    current_sha: str | None = None
    if manifest_item is None:
        errors.append("request_id_not_in_goal5438_manifest")
    else:
        if manifest_item.get("sendable_external") is not True:
            errors.append("manifest_item_is_not_sendable_external")
        if request_path != manifest_item.get("path"):
            errors.append("request_path_does_not_match_manifest")
        if request_sha != manifest_item.get("sha256"):
            errors.append("request_sha256_at_send_time_does_not_match_manifest")
        item_path = ROOT / str(manifest_item.get("path"))
        current_sha = _sha256(item_path)
        if current_sha != manifest_item.get("sha256"):
            errors.append("current_request_file_sha256_does_not_match_manifest")

    boundary = receipt.get("claim_boundary")
    if isinstance(boundary, dict):
        if boundary.get("external_response_received") is True:
            errors.append("receipt_claims_external_response_received")
        for key in [
            "external_artifacts_acquired",
            "exact_equivalence_accepted",
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
            "performance_ratio_claimed",
        ]:
            if boundary.get(key) is True:
                errors.append(f"receipt_overclaims_{key}")

    return {
        "path": _rel(path),
        "loaded": True,
        "valid": not errors,
        "errors": errors,
        "request_id": request_id,
        "request_path": request_path,
        "request_sha256_at_send_time": request_sha,
        "current_request_sha256": current_sha,
        "sent_at_utc": receipt.get("sent_at_utc"),
        "channel": receipt.get("channel"),
        "recipient_or_reviewer": receipt.get("recipient_or_reviewer"),
        "raw_message_committed": receipt.get("raw_message_committed"),
    }


def build_sent_receipt_gate(
    sent_dir: Path = SENT,
    manifest_path: Path = MANIFEST_RESULT,
) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    manifest_items = _manifest_items(manifest)
    files = _receipt_files(sent_dir)
    receipts = [_classify_receipt(path, manifest_items) for path in files]
    valid = [row for row in receipts if row.get("valid") is True]
    invalid = [row for row in receipts if row.get("valid") is not True]

    if not files:
        status = "external_request_sent_receipt_gate_empty__no_request_sent"
        next_action = "send_owner_reviewed_request_then_record_receipt_or_wait"
    elif invalid:
        status = "external_request_sent_receipts_invalid__fix_before_response_claim"
        next_action = "fix_invalid_receipts_before_external_response_or_artifact_claims"
    else:
        status = "external_request_sent_receipts_valid__await_response_intake"
        next_action = "normalize_any_external_response_into_requests_incoming_then_run_goal5435_and_goal5437"

    sent_claimed = bool(valid) and not invalid
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5439.external_request_sent_receipt_gate.v1",
        "goal": "Goal5439",
        "date": "2026-07-10",
        "status": status,
        "sent_dir": _rel(sent_dir),
        "goal5438_manifest": _rel(manifest_path),
        "goal5438_manifest_status": manifest.get("status"),
        "receipt_count": len(files),
        "valid_receipt_count": len(valid),
        "invalid_receipt_count": len(invalid),
        "valid_request_ids": [row["request_id"] for row in valid],
        "invalid_request_ids": [row["request_id"] for row in invalid],
        "receipts": receipts,
        "next_action": next_action,
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Sent-receipt verification only. POD remains gated by classified external response and strict review.",
        },
        "claim_boundary": {
            "sent_receipt_gate_scanned": True,
            "request_send_manifest_claimed": True,
            "request_sent_claimed": sent_claimed,
            "external_response_received": False,
            "external_artifacts_acquired": False,
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
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external request sent-receipt gate / response intake workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: outbound receipt governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming a request was sent without a valid sent receipt",
            "treating a sent receipt as an external response",
            "claiming external artifacts were acquired from a sent receipt",
            "claiming exact-equivalence accepted from a sent receipt",
            "claiming exact paper dataset reproduction from a sent receipt",
            "claiming Figure 5 or full X-HD reproduction from a sent receipt",
            "claiming performance ratio from a sent receipt",
            "running POD or route work from this receipt gate",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sent-dir", type=Path, default=SENT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_RESULT)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    payload = build_sent_receipt_gate(args.sent_dir, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "receipt_count": payload["receipt_count"],
                "request_sent_claimed": payload["claim_boundary"]["request_sent_claimed"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
