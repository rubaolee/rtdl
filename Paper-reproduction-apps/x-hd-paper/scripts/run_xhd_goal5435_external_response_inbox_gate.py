#!/usr/bin/env python3
"""Run the Goal5435 X-HD Water/BG external-response inbox gate.

This is the executable handoff after Goal5434. It scans an incoming response
directory for normalized Goal5329 response JSON files, classifies each response
with the Goal5433 classifier, and emits one machine-readable status.

It does not send requests, contact remote machines, run author code, run RTDL
routes, or upgrade claims. Positive classifier outcomes authorize only the next
separate gate described by the classifier.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
REQUESTS = APP / "requests"
RESULTS = APP / "results"
INCOMING = REQUESTS / "incoming"
ACTION_PACKET = REQUESTS / "water_bg_external_action_packet.md"
ACTION_SUMMARY = RESULTS / "xhd_goal5434_water_bg_external_action_packet.json"
CLASSIFIER_SCRIPT = APP / "scripts" / "classify_xhd_goal5433_water_bg_external_response.py"
OUT = RESULTS / "xhd_goal5435_external_response_inbox_gate.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def _load_classifier_module():
    spec = importlib.util.spec_from_file_location("goal5433_classifier", CLASSIFIER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:  # pragma: no cover - importlib defensive guard.
        raise RuntimeError(f"Cannot load {CLASSIFIER_SCRIPT}")
    spec.loader.exec_module(module)
    return module


def _response_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    return sorted(path for path in input_dir.glob("*.json") if path.is_file())


def build_inbox_gate(input_dir: Path = INCOMING) -> dict[str, Any]:
    action_summary = _load_json(ACTION_SUMMARY)
    classifier = _load_classifier_module()
    files = _response_files(input_dir)
    classified: list[dict[str, Any]] = []

    for path in files:
        try:
            response = _load_json(path)
            result = classifier.classify_response(response)
            classified.append(
                {
                    "path": _rel(path) if path.is_relative_to(ROOT) else str(path),
                    "loaded": True,
                    "error": None,
                    "response_type": response.get("response_type"),
                    "classification": result.get("classification"),
                    "recommended_next_action": result.get("recommended_next_action"),
                    "validation_status": result.get("validation_status", {}),
                    "claim_boundary": result.get("claim_boundary", {}),
                }
            )
        except Exception as exc:  # pragma: no cover - status path is tested through malformed JSON as needed.
            classified.append(
                {
                    "path": _rel(path) if path.is_relative_to(ROOT) else str(path),
                    "loaded": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "response_type": None,
                    "classification": "invalid_response_json__manual_review_keep_level_b",
                    "recommended_next_action": "fix_or_remove_invalid_response_before_any_gate",
                    "validation_status": {
                        "sufficient_to_run_pod_gate": False,
                        "sufficient_to_claim_exact_input": False,
                    },
                    "claim_boundary": {
                        "exact_paper_dataset_reproduction_claimed": False,
                    },
                }
            )

    positive = [
        row
        for row in classified
        if row.get("validation_status", {}).get("sufficient_to_run_pod_gate") is True
        or row.get("validation_status", {}).get("exact_equivalence_accepted") is True
    ]
    invalid = [row for row in classified if row.get("loaded") is not True]

    if not files:
        status = "external_response_inbox_empty__await_response"
        next_action = "wait_for_external_response_or_send_owner_reviewed_action_packet"
    elif invalid:
        status = "external_response_inbox_has_invalid_items__fix_before_gate"
        next_action = "fix_or_remove_invalid_response_json_before_classification_driven_action"
    elif positive:
        status = "external_response_inbox_has_positive_classifier_outcome__manual_review_before_gate"
        next_action = "strictly_review_classifier_output_then_open_the_separate_next_gate_if_approved"
    else:
        status = "external_response_inbox_all_fail_closed__keep_level_b"
        next_action = "record_response_outcomes_and_keep_level_b_until_stronger_evidence_arrives"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5435.external_response_inbox_gate.v1",
        "goal": "Goal5435",
        "date": "2026-07-10",
        "status": status,
        "input_dir": _rel(input_dir) if input_dir.is_relative_to(ROOT) else str(input_dir),
        "action_packet": _rel(ACTION_PACKET),
        "action_packet_status": action_summary.get("status"),
        "response_count": len(files),
        "loaded_response_count": sum(1 for row in classified if row.get("loaded") is True),
        "invalid_response_count": len(invalid),
        "positive_classifier_outcome_count": len(positive),
        "classified_responses": classified,
        "next_action": next_action,
        "pod_usage": {
            "used": False,
            "expected_next": bool(positive) and not invalid,
            "reason": "POD remains a separate next gate and is never run by this inbox scanner.",
        },
        "claim_boundary": {
            "inbox_scanned": True,
            "request_sent_claimed": False,
            "external_response_received": bool(files),
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
            "gate_non_app_consumer": "external response inbox gate / classifier-driven provenance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: inbox governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "treating a positive classifier outcome as exact/full reproduction by itself",
            "running POD inside the inbox scanner",
            "running author or RTDL route code inside the inbox scanner",
            "claiming exact-equivalence accepted without strict review of the classifier output",
            "claiming exact paper dataset reproduction from response presence alone",
            "claiming Figure 5 or full X-HD reproduction from response presence alone",
            "claiming performance ratio from response presence alone",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=INCOMING)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    payload = build_inbox_gate(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "response_count": payload["response_count"],
                "positive_classifier_outcome_count": payload["positive_classifier_outcome_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
