#!/usr/bin/env python3
"""Build the Goal5445 X-HD external action dispatch bundle.

This turns the Goal5438 prepared external request manifest into a concrete
handoff bundle: an index, one README, and one receipt stub per sendable request.

It does not send requests, record a receipt, inspect responses, run POD, run
author code, run RTDL routes, or upgrade any reproduction claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
REQUESTS = APP / "requests"
RESULTS = APP / "results"

SOURCE_MANIFEST = RESULTS / "xhd_goal5438_external_request_send_manifest.json"
BUNDLE_DIR = REQUESTS / "send_bundle"
BUNDLE_RECEIPTS = BUNDLE_DIR / "receipts"
BUNDLE_INDEX = BUNDLE_DIR / "request_index.json"
BUNDLE_README = BUNDLE_DIR / "README.md"
OUT = RESULTS / "xhd_goal5445_external_action_dispatch_bundle.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_manifest() -> dict[str, Any]:
    return json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))


def _sendable_items(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in manifest.get("items", [])
        if item.get("sendable_external") is True and item.get("ready_to_send_or_review") is True
    ]


def _receipt_stub(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1",
        "status": "stub_not_a_receipt",
        "request_id": item["id"],
        "request_path": item["path"],
        "request_sha256_at_prepare_time": item["sha256"],
        "request_sha256_at_send_time": None,
        "sent": False,
        "sent_at_utc": None,
        "sent_by": None,
        "channel": None,
        "recipient_or_reviewer": item["audience"],
        "subject_or_thread": None,
        "raw_message_committed": False,
        "privacy_notes": "Do not commit private raw correspondence unless the sender permits it.",
        "expected_response_intake": (
            "If a response arrives, normalize it into "
            "Paper-reproduction-apps/x-hd-paper/requests/incoming before running the response inbox gate."
        ),
        "claim_boundary": {
            "receipt_stub_claimed": True,
            "request_sent_claimed": False,
            "external_response_received": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
        },
    }


def _write_stub(item: dict[str, Any]) -> Path:
    BUNDLE_RECEIPTS.mkdir(parents=True, exist_ok=True)
    path = BUNDLE_RECEIPTS / f"{item['id']}_receipt_stub.json"
    path.write_text(json.dumps(_receipt_stub(item), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_readme(payload: dict[str, Any]) -> None:
    lines = [
        "# X-HD External Action Dispatch Bundle",
        "",
        "Status: `prepared_not_sent`",
        "",
        "This directory gathers the currently prepared external requests and one",
        "receipt stub per sendable request. It is a handoff bundle only.",
        "It does not claim that any request was sent.",
        "",
        "## Sendable Requests",
        "",
    ]
    for request in payload["sendable_requests"]:
        lines.extend(
            [
                f"### {request['id']}",
                "",
                "```text",
                f"request_path = {request['path']}",
                f"audience = {request['audience']}",
                f"purpose = {request['purpose']}",
                f"sha256_at_prepare_time = {request['sha256']}",
                f"receipt_stub = {request['receipt_stub_path']}",
                "sent = false",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## How To Use",
            "",
            "1. Review the selected request text.",
            "2. If the owner sends it outside this repository, copy the matching",
            "   receipt stub, fill the send fields, and place the real receipt in",
            "   `Paper-reproduction-apps/x-hd-paper/requests/sent/`.",
            "3. If a response arrives, normalize it into",
            "   `Paper-reproduction-apps/x-hd-paper/requests/incoming/` before",
            "   running the response inbox gate.",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "external_action_dispatch_bundle_claimed = true",
            "request_sent_claimed = false",
            "external_response_received = false",
            "external_artifacts_acquired = false",
            "exact_equivalence_accepted = false",
            "exact_paper_dataset_reproduction_claimed = false",
            "figure5_reproduction_claimed = false",
            "full_xhd_paper_reproduction_claimed = false",
            "performance_ratio_claimed = false",
            "pod_execution_claimed = false",
            "```",
            "",
            "## Stop-Loss Rule",
            "",
            "```text",
            "gate_generic_capability_produced: true",
            "gate_non_app_consumer: external action dispatch bundle / receipt workflow",
            "gate_requires_app_specific_logic: false",
            "gate_downstream_consumer_reachable: true",
            "```",
            "",
        ]
    )
    BUNDLE_README.write_text("\n".join(lines), encoding="utf-8")


def build_payload() -> dict[str, Any]:
    manifest = _load_manifest()
    items = _sendable_items(manifest)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    BUNDLE_RECEIPTS.mkdir(parents=True, exist_ok=True)

    sendable_requests = []
    for item in items:
        stub_path = _write_stub(item)
        sendable_requests.append(
            {
                "id": item["id"],
                "path": item["path"],
                "audience": item["audience"],
                "purpose": item["purpose"],
                "sha256": item["sha256"],
                "status": item["status"],
                "ready_to_send_or_review": item["ready_to_send_or_review"],
                "sent_claimed": False,
                "receipt_stub_path": _rel(stub_path),
            }
        )

    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5445.external_action_dispatch_bundle.v1",
        "goal": "Goal5445",
        "date": "2026-07-10",
        "status": "external_action_dispatch_bundle_ready__not_sent",
        "source_manifest": _rel(SOURCE_MANIFEST),
        "bundle_dir": _rel(BUNDLE_DIR),
        "bundle_index": _rel(BUNDLE_INDEX),
        "bundle_readme": _rel(BUNDLE_README),
        "sendable_requests": sendable_requests,
        "ready_external_request_count": len(sendable_requests),
        "receipt_stub_count": len(sendable_requests),
        "request_sent_claimed": False,
        "external_response_received": False,
        "exact_input_blocker_removed": False,
        "pod_expected_next": False,
        "claim_boundary": {
            "external_action_dispatch_bundle_claimed": True,
            "request_sent_claimed": False,
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
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Dispatch bundle only. POD is gated by a later classified response and reviewed next gate.",
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external action dispatch bundle / receipt workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: outbound governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming any request was sent from this bundle alone",
            "claiming any response arrived from this bundle alone",
            "claiming external artifacts were acquired",
            "claiming exact-equivalence accepted",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD or route work from this bundle alone",
        ],
        "next_action": "owner_send_selected_request_then_record_real_receipt_or_wait_for_authorized_acm_access",
    }

    _write_readme(payload)
    BUNDLE_INDEX.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "ready_external_request_count": payload["ready_external_request_count"],
                "receipt_stub_count": payload["receipt_stub_count"],
                "request_sent_claimed": payload["request_sent_claimed"],
                "pod_expected_next": payload["pod_expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
