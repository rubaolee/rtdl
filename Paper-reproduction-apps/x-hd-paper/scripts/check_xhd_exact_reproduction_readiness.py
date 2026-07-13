#!/usr/bin/env python3
"""Summarize whether X-HD exact-reproduction POD execution is currently ready.

This is an app-owned gatekeeper for the external-artifact path. It folds the
Goal5341-Goal5344 status artifacts into one machine-readable answer:

  - do we have actual artifact access?
  - did the local artifact pipeline produce a command-ready packet?
  - did the POD plan builder produce a ready wrapper-only plan?
  - is the dry-run-by-default runner available?

It does not inspect ACM contents, run author/RTDL commands, contact a POD, or
compare outputs. Those remain separate explicit goals.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[3]
XHD_RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"

DEFAULT_ACM_PROBE = XHD_RESULTS / "xhd_goal5341_acm_supplement_live_access_probe.json"
DEFAULT_PIPELINE = XHD_RESULTS / "xhd_goal5342_acm_artifact_to_packet_pipeline.json"
DEFAULT_PLAN = XHD_RESULTS / "xhd_goal5343_mapped_candidate_pod_execution_plan.json"
DEFAULT_RUNNER = XHD_RESULTS / "xhd_goal5344_mapped_candidate_pod_execution_runner.json"


def _load_optional_json(path: pathlib.Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "loaded": False,
            "error": "missing",
            "payload": None,
        }
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as exc:  # pragma: no cover - defensive, exercised via status.
        return {
            "path": str(path),
            "loaded": False,
            "error": f"{type(exc).__name__}: {exc}",
            "payload": None,
        }
    if not isinstance(payload, dict):
        return {
            "path": str(path),
            "loaded": False,
            "error": "json root is not an object",
            "payload": None,
        }
    return {
        "path": str(path),
        "loaded": True,
        "error": None,
        "payload": payload,
    }


def _payload(record: Dict[str, Any]) -> Dict[str, Any]:
    payload = record.get("payload")
    return payload if isinstance(payload, dict) else {}


def _current_artifact_access_ready(acm_probe: Dict[str, Any]) -> bool:
    payload = _payload(acm_probe)
    interpretation = payload.get("interpretation")
    if isinstance(interpretation, dict):
        if interpretation.get("exact_input_blocker_removed") is True:
            return True
        if interpretation.get("current_environment_can_download_zip") is True:
            return True
    live_summary = payload.get("live_probe_summary")
    if isinstance(live_summary, dict) and live_summary.get("zip_magic_observed") is True:
        return True
    return False


def _pipeline_packet_ready(pipeline: Dict[str, Any]) -> bool:
    payload = _payload(pipeline)
    return (
        payload.get("classification") == "local_artifact_pipeline_packet_ready__await_pod_execution"
        or payload.get("status") == "local_artifact_pipeline_packet_ready__await_pod_execution"
        or payload.get("pod_allowed_next") is True
    )


def _plan_ready(plan: Dict[str, Any]) -> bool:
    payload = _payload(plan)
    return (
        payload.get("classification") == "mapped_candidate_pod_execution_plan_ready"
        or payload.get("status") == "mapped_candidate_pod_execution_plan_ready"
        or payload.get("pod_allowed_next") is True
    )


def _runner_capability_ready(runner: Dict[str, Any]) -> bool:
    payload = _payload(runner)
    script = payload.get("script")
    if isinstance(script, dict) and script.get("execute_requires_flag") == "--execute":
        return True
    return payload.get("status") == "mapped_candidate_pod_execution_runner_ready__dry_run_only_until_real_plan"


def _missing_or_invalid(records: Dict[str, Dict[str, Any]]) -> List[str]:
    return [
        name
        for name, record in records.items()
        if record.get("loaded") is not True
    ]


def build_readiness(
    *,
    acm_probe_path: pathlib.Path,
    pipeline_path: pathlib.Path,
    plan_path: pathlib.Path,
    runner_path: pathlib.Path,
) -> Dict[str, Any]:
    records = {
        "acm_probe": _load_optional_json(acm_probe_path),
        "artifact_to_packet_pipeline": _load_optional_json(pipeline_path),
        "pod_execution_plan": _load_optional_json(plan_path),
        "pod_execution_runner": _load_optional_json(runner_path),
    }
    artifact_access_ready = _current_artifact_access_ready(records["acm_probe"])
    packet_ready = _pipeline_packet_ready(records["artifact_to_packet_pipeline"])
    plan_ready = _plan_ready(records["pod_execution_plan"])
    runner_ready = _runner_capability_ready(records["pod_execution_runner"])
    missing_or_invalid = _missing_or_invalid(records)

    pod_execution_allowed_now = bool(
        not missing_or_invalid
        and packet_ready
        and plan_ready
        and runner_ready
    )

    if missing_or_invalid:
        classification = "exact_reproduction_readiness_unknown__missing_status_artifacts"
        next_action = "restore or regenerate the missing status artifacts before deciding whether POD is allowed"
    elif pod_execution_allowed_now:
        classification = "exact_reproduction_pod_execution_ready__requires_explicit_execute_goal"
        next_action = "open a separate POD execution goal, dry-run the plan, then run Goal5344 with --execute"
    elif not artifact_access_ready:
        classification = "exact_reproduction_not_pod_ready__await_artifact_access"
        next_action = "obtain authorized ACM access or real artifact bytes, then run Goal5341 and Goal5342"
    elif not packet_ready:
        classification = "exact_reproduction_not_pod_ready__await_command_ready_packet"
        next_action = "run Goal5342 with real artifact bytes and an accepted mapping until it emits a command-ready packet"
    elif not plan_ready:
        classification = "exact_reproduction_not_pod_ready__await_pod_plan"
        next_action = "run Goal5343 on the real command-ready packet"
    else:
        classification = "exact_reproduction_not_pod_ready__runner_not_validated"
        next_action = "validate the Goal5344 dry-run runner before any --execute use"

    return {
        "schema": "rtdl.paper_reproduction.xhd.exact_reproduction_readiness.v1",
        "classification": classification,
        "pod_execution_allowed_now": pod_execution_allowed_now,
        "readiness": {
            "status_artifacts_loaded": not missing_or_invalid,
            "artifact_access_or_zip_ready": artifact_access_ready,
            "command_ready_packet_ready": packet_ready,
            "pod_execution_plan_ready": plan_ready,
            "pod_runner_capability_ready": runner_ready,
        },
        "status_artifacts": {
            name: {
                "path": record["path"],
                "loaded": record["loaded"],
                "error": record["error"],
                "schema": _payload(record).get("schema"),
                "status": _payload(record).get("status"),
                "classification": _payload(record).get("classification"),
                "exit_label": _payload(record).get("exit_label"),
            }
            for name, record in records.items()
        },
        "next_action": next_action,
        "pod_usage": {
            "used": False,
            "expected_next": pod_execution_allowed_now,
            "reason": "POD is allowed only after a real command-ready packet and ready POD execution plan exist.",
        },
        "claim_boundary": {
            "pod_preflight_ran": False,
            "uploads_executed": False,
            "remote_commands_executed": False,
            "downloads_executed": False,
            "outputs_compared": False,
            "same_input_gate_passed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "running POD from URL visibility or 403 HTML responses",
            "running Goal5344 --execute without a real command-ready packet and ready plan",
            "claiming dry-run readiness is execution evidence",
            "claiming same-input correctness before Goal5340 compares real outputs",
            "claiming exact paper dataset reproduction from readiness status",
            "claiming Figure 5 or full-paper reproduction from readiness status",
            "claiming author-vs-RTDL performance ratio from readiness status",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acm-probe-json", type=pathlib.Path, default=DEFAULT_ACM_PROBE)
    parser.add_argument("--pipeline-json", type=pathlib.Path, default=DEFAULT_PIPELINE)
    parser.add_argument("--plan-json", type=pathlib.Path, default=DEFAULT_PLAN)
    parser.add_argument("--runner-json", type=pathlib.Path, default=DEFAULT_RUNNER)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    summary = build_readiness(
        acm_probe_path=args.acm_probe_json,
        pipeline_path=args.pipeline_json,
        plan_path=args.plan_json,
        runner_path=args.runner_json,
    )
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if summary["classification"] != "exact_reproduction_readiness_unknown__missing_status_artifacts" else 1


if __name__ == "__main__":
    raise SystemExit(main())
