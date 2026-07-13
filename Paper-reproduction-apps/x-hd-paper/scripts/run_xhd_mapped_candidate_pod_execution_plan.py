#!/usr/bin/env python3
"""Run or dry-run an X-HD mapped-candidate POD execution plan.

The input is the Goal5343 plan. By default this script performs a dry-run only:
it validates the plan and records the preflight/upload/remote-exec/download/
compare steps that would run. Actual POD work requires ``--execute``.

Even in execute mode, this runner does not claim exact paper input identity or
performance parity. It can only report whether the same-input HDResult
comparison produced by Goal5340 passed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from typing import Any, Dict, List


PLAN_SCHEMA = "rtdl.paper_reproduction.xhd.mapped_candidate_pod_execution_plan.v1"
SUMMARY_SCHEMA = "rtdl.paper_reproduction.xhd.mapped_candidate_pod_execution_run.v1"


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _command_contains_wrapper(command: Any) -> bool:
    if not isinstance(command, list):
        return False
    return any(str(part).endswith("current_pod_ssh.py") or str(part).replace("\\", "/").endswith("/current_pod_ssh.py") for part in command)


def _validate_plan(plan: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if plan.get("schema") != PLAN_SCHEMA:
        errors.append("plan schema mismatch")
    if plan.get("classification") != "mapped_candidate_pod_execution_plan_ready":
        errors.append(f"plan is not ready: {plan.get('classification')}")
    if plan.get("pod_allowed_next") is not True:
        errors.append("plan does not allow POD next")
    if not _command_contains_wrapper(plan.get("wrapper_preflight_command")):
        errors.append("preflight command does not use scripts/current_pod_ssh.py")
    if not _command_contains_wrapper(plan.get("wrapper_remote_execute_command")):
        errors.append("remote execute command does not use scripts/current_pod_ssh.py")
    for idx, step in enumerate(plan.get("upload_steps", [])):
        if not isinstance(step, dict) or not _command_contains_wrapper(step.get("wrapper_command")):
            errors.append(f"upload step {idx} does not use scripts/current_pod_ssh.py")
    for idx, step in enumerate(plan.get("download_steps", [])):
        if not isinstance(step, dict) or not _command_contains_wrapper(step.get("wrapper_command")):
            errors.append(f"download step {idx} does not use scripts/current_pod_ssh.py")
    comparator = plan.get("local_comparator_command")
    if not isinstance(comparator, list) or not comparator:
        errors.append("local comparator command missing")
    return errors


def _stage(name: str, command: List[Any], *, execute: bool, timeout_sec: float | None) -> Dict[str, Any]:
    started = time.perf_counter()
    command_str = [str(part) for part in command]
    if not execute:
        return {
            "stage": name,
            "executed": False,
            "returncode": None,
            "elapsed_sec": 0.0,
            "command": command_str,
            "stdout": "",
            "stderr": "",
        }
    proc = subprocess.run(command_str, check=False, text=True, capture_output=True, timeout=timeout_sec)
    return {
        "stage": name,
        "executed": True,
        "returncode": proc.returncode,
        "elapsed_sec": time.perf_counter() - started,
        "command": command_str,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def _read_comparison_from_plan(plan: Dict[str, Any]) -> Dict[str, Any] | None:
    command = plan.get("local_comparator_command")
    if not isinstance(command, list):
        return None
    try:
        output_idx = command.index("--output") + 1
        output_path = pathlib.Path(str(command[output_idx]))
    except Exception:
        return None
    if not output_path.exists():
        return None
    try:
        return _load_json(output_path)
    except Exception:
        return None


def run_plan(plan_path: pathlib.Path, *, execute: bool, timeout_sec: float | None) -> Dict[str, Any]:
    plan = _load_json(plan_path)
    validation_errors = _validate_plan(plan)
    stages: List[Dict[str, Any]] = []
    comparison: Dict[str, Any] | None = None

    if validation_errors:
        classification = "mapped_candidate_pod_execution_run_not_ready"
        executed = False
    elif not execute:
        classification = "mapped_candidate_pod_execution_dry_run_ready"
        executed = False
        stages.extend(_planned_stages(plan))
    else:
        executed = True
        for stage_name, command in _execution_sequence(plan):
            result = _stage(stage_name, command, execute=True, timeout_sec=timeout_sec)
            stages.append(result)
            if result["returncode"] != 0:
                break
        all_stage_ok = bool(stages and all(stage.get("returncode") == 0 for stage in stages))
        comparison = _read_comparison_from_plan(plan)
        comparison_passed = bool(comparison and comparison.get("classification") == "mapped_candidate_same_input_gate_passed")
        if all_stage_ok and comparison_passed:
            classification = "mapped_candidate_pod_execution_and_comparison_passed"
        elif all_stage_ok:
            classification = "mapped_candidate_pod_execution_finished_comparison_failed_or_missing"
        else:
            classification = "mapped_candidate_pod_execution_failed"

    return {
        "schema": SUMMARY_SCHEMA,
        "plan_path": str(plan_path.resolve()),
        "classification": classification,
        "dry_run": not execute,
        "pod_execution_attempted": bool(executed),
        "stage_count": len(stages),
        "stages": stages,
        "validation_errors": validation_errors,
        "comparison": comparison,
        "same_input_gate_passed": classification == "mapped_candidate_pod_execution_and_comparison_passed",
        "claim_boundary": {
            "pod_preflight_ran": bool(execute and any(stage["stage"] == "preflight" and stage["returncode"] == 0 for stage in stages)),
            "uploads_executed": bool(execute and any(stage["stage"].startswith("upload:") and stage["returncode"] == 0 for stage in stages)),
            "remote_commands_executed": bool(execute and any(stage["stage"] == "remote_execute" and stage["returncode"] == 0 for stage in stages)),
            "downloads_executed": bool(execute and any(stage["stage"].startswith("download:") and stage["returncode"] == 0 for stage in stages)),
            "outputs_compared": bool(execute and any(stage["stage"] == "local_compare" and stage["returncode"] in {0, 1} for stage in stages)),
            "same_input_gate_passed": classification == "mapped_candidate_pod_execution_and_comparison_passed",
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "claiming exact paper dataset reproduction from this execution alone",
            "claiming Figure 5 reproduction from this execution alone",
            "claiming full X-HD paper reproduction from this execution alone",
            "claiming author-vs-RTDL performance ratio from this execution",
        ],
    }


def _planned_stages(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        _stage(name, command, execute=False, timeout_sec=None)
        for name, command in _execution_sequence(plan)
    ]


def _execution_sequence(plan: Dict[str, Any]) -> List[tuple[str, List[Any]]]:
    sequence: List[tuple[str, List[Any]]] = []
    sequence.append(("preflight", plan["wrapper_preflight_command"]))
    for idx, upload in enumerate(plan.get("upload_steps", [])):
        sequence.append((f"upload:{idx}:{upload.get('remote')}", upload["wrapper_command"]))
    sequence.append(("remote_execute", plan["wrapper_remote_execute_command"]))
    for idx, download in enumerate(plan.get("download_steps", [])):
        sequence.append((f"download:{idx}:{download.get('remote')}", download["wrapper_command"]))
    sequence.append(("local_compare", plan["local_comparator_command"]))
    return sequence


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=pathlib.Path)
    parser.add_argument("--execute", action="store_true", help="Actually run wrapper commands and local comparator.")
    parser.add_argument("--timeout-sec", type=float, default=None)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        summary = run_plan(args.plan_json, execute=args.execute, timeout_sec=args.timeout_sec)
    except Exception as exc:
        print(f"mapped candidate POD execution runner failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if summary["classification"] in {
        "mapped_candidate_pod_execution_dry_run_ready",
        "mapped_candidate_pod_execution_and_comparison_passed",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
