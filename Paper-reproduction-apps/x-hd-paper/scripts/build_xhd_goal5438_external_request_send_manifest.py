#!/usr/bin/env python3
"""Build the Goal5438 X-HD external request send manifest.

This manifest makes the outbound step auditable: which prepared request files
exist, what their hashes are, who they are intended for, and what receipt record
must be written if the owner sends them.

It does not send email/messages, contact remote services, run POD, or upgrade
any reproduction claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
REQUESTS = APP / "requests"
RESULTS = APP / "results"

ACTION_PACKET = REQUESTS / "water_bg_external_action_packet.md"
INBOX = REQUESTS / "incoming"
RECEIPT_TEMPLATE = REQUESTS / "external_request_send_receipt_template.json"
SEND_MANIFEST_MD = REQUESTS / "external_request_send_manifest.md"
OUT = RESULTS / "xhd_goal5438_external_request_send_manifest.json"


REQUEST_ITEMS = [
    {
        "id": "general_author_input_provenance_request",
        "path": REQUESTS / "author_input_provenance_request.md",
        "audience": "X-HD authors / artifact owner",
        "purpose": "Ask for exact paper input provenance across X-HD datasets.",
        "sendable_external": True,
    },
    {
        "id": "general_acm_supplement_inspection_request",
        "path": REQUESTS / "acm_supplement_inspection_request.md",
        "audience": "ACM supplement access holder / owner",
        "purpose": "Ask for authorized inspection of ACM supplement contents.",
        "sendable_external": True,
    },
    {
        "id": "water_bg_author_hash_request",
        "path": REQUESTS / "author_water_bg_input_hash_request.md",
        "audience": "X-HD authors / artifact owner",
        "purpose": "Ask specifically for WaterBodies/BG paper-run WKT hashes, bytes, or regeneration provenance.",
        "sendable_external": True,
    },
    {
        "id": "water_bg_exact_equivalence_review_request",
        "path": REQUESTS / "water_bg_exact_equivalence_review_request.md",
        "audience": "owner or external reviewer",
        "purpose": "Ask whether the current Water/BG public reconstruction can be accepted under a bounded renamed claim.",
        "sendable_external": True,
    },
    {
        "id": "water_bg_external_action_packet",
        "path": ACTION_PACKET,
        "audience": "owner/internal coordinator",
        "purpose": "Single internal packet tying requests, response normalization, classifier, and fail-closed next steps.",
        "sendable_external": False,
    },
]


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _status_from_text(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.lower().startswith("status:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


def _item_payload(item: dict[str, Any]) -> dict[str, Any]:
    path = item["path"]
    exists = path.exists()
    payload = {
        "id": item["id"],
        "path": _rel(path),
        "audience": item["audience"],
        "purpose": item["purpose"],
        "sendable_external": bool(item["sendable_external"]),
        "exists": exists,
        "status": _status_from_text(path) if exists else None,
        "sha256": _sha256(path) if exists else None,
        "bytes": path.stat().st_size if exists else None,
        "sent_claimed": False,
    }
    payload["ready_to_send_or_review"] = exists and payload["status"] == "prepared_not_sent"
    return payload


def _write_receipt_template() -> None:
    template = {
        "schema": "rtdl.paper_reproduction.xhd.external_request_send_receipt.v1",
        "status": "template_not_a_receipt",
        "request_id": "<one of external_request_send_manifest.items[].id>",
        "request_path": "<copied from manifest item>",
        "request_sha256_at_send_time": "<copied from manifest item>",
        "sent": False,
        "sent_at_utc": None,
        "sent_by": None,
        "channel": None,
        "recipient_or_reviewer": None,
        "subject_or_thread": None,
        "raw_message_committed": False,
        "privacy_notes": "Do not commit private raw correspondence unless sender permits it.",
        "expected_response_intake": "Normalize any response into Paper-reproduction-apps/x-hd-paper/requests/incoming using external_response_intake_template.json.",
        "claim_boundary": {
            "receipt_template_claimed": True,
            "request_sent_claimed": False,
            "external_response_received": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }
    RECEIPT_TEMPLATE.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_manifest_md(payload: dict[str, Any]) -> None:
    lines = [
        "# X-HD External Request Send Manifest",
        "",
        "Status: `prepared_not_sent`",
        "",
        "This manifest records prepared request files and their hashes. It does",
        "not claim that any request was sent.",
        "",
        "## Items",
        "",
    ]
    for item in payload["items"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                "```text",
                f"path = {item['path']}",
                f"audience = {item['audience']}",
                f"sendable_external = {str(item['sendable_external']).lower()}",
                f"status = {item['status']}",
                f"sha256 = {item['sha256']}",
                f"ready_to_send_or_review = {str(item['ready_to_send_or_review']).lower()}",
                f"sent_claimed = {str(item['sent_claimed']).lower()}",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Receipt Template",
            "",
            "If the owner sends a request, record a receipt using:",
            "",
            "```text",
            _rel(RECEIPT_TEMPLATE),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "request_send_manifest_claimed = true",
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
            "gate_non_app_consumer: external request send manifest / receipt workflow",
            "gate_requires_app_specific_logic: false",
            "gate_downstream_consumer_reachable: true",
            "```",
            "",
        ]
    )
    SEND_MANIFEST_MD.write_text("\n".join(lines), encoding="utf-8")


def build_payload() -> dict[str, Any]:
    REQUESTS.mkdir(parents=True, exist_ok=True)
    _write_receipt_template()
    items = [_item_payload(item) for item in REQUEST_ITEMS]
    missing = [item["id"] for item in items if not item["exists"]]
    not_prepared = [item["id"] for item in items if item["exists"] and item["status"] != "prepared_not_sent"]
    ready_external = [item["id"] for item in items if item["sendable_external"] and item["ready_to_send_or_review"]]

    if missing:
        status = "external_request_send_manifest_incomplete__missing_files"
        next_action = "restore_missing_request_files_before_owner_review"
    elif not_prepared:
        status = "external_request_send_manifest_incomplete__non_prepared_status"
        next_action = "fix_request_statuses_before_owner_review"
    else:
        status = "external_request_send_manifest_ready__prepared_not_sent"
        next_action = "owner_review_then_send_selected_requests_and_record_receipts"

    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5438.external_request_send_manifest.v1",
        "goal": "Goal5438",
        "date": "2026-07-10",
        "status": status,
        "items": items,
        "ready_external_request_ids": ready_external,
        "internal_packet_ids": [item["id"] for item in items if not item["sendable_external"]],
        "missing_item_ids": missing,
        "non_prepared_item_ids": not_prepared,
        "receipt_template": _rel(RECEIPT_TEMPLATE),
        "send_manifest": _rel(SEND_MANIFEST_MD),
        "incoming_response_dir": _rel(INBOX),
        "next_action": next_action,
        "claim_boundary": {
            "request_send_manifest_claimed": True,
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
            "reason": "Outbound manifest only. POD is gated by later classified response and reviewed next gate.",
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external request send manifest / receipt workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: outbound governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming any request was sent from this manifest alone",
            "claiming any response arrived from this manifest alone",
            "claiming external artifacts were acquired",
            "claiming exact-equivalence accepted",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD or route work from this manifest alone",
        ],
    }
    _write_manifest_md(payload)
    return payload


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "ready_external_request_count": len(payload["ready_external_request_ids"]),
                "request_sent_claimed": payload["claim_boundary"]["request_sent_claimed"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
