#!/usr/bin/env python3
"""Build a POD execution plan from a mapped X-HD same-input command packet.

The input is the Goal5339 packet produced after candidate files are materialized.
This helper rewrites local input/output/script paths into a remote POD workspace
and emits only a plan: upload, remote command, download, and post-compare steps.

It does not contact POD, upload files, execute commands, or compare outputs.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import posixpath
import shlex
import sys
from typing import Any, Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[3]
CURRENT_POD_WRAPPER = ROOT / "scripts" / "current_pod_ssh.py"
RTDL_SCRIPT_RELATIVE = "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py"
COMPARATOR_RELATIVE = "Paper-reproduction-apps/x-hd-paper/scripts/compare_xhd_mapped_candidate_same_input_outputs.py"


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _safe_workload_id(value: Any) -> str:
    raw = str(value or "workload")
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in raw)


def _suffix_from_path(path_text: str, default: str) -> str:
    suffix = pathlib.PurePosixPath(path_text.replace("\\", "/")).suffix
    return suffix or default


def _replace_arg(command: List[str], flag: str, value: str) -> List[str]:
    out = list(command)
    try:
        idx = out.index(flag)
    except ValueError as exc:
        raise ValueError(f"command missing {flag}") from exc
    if idx + 1 >= len(out):
        raise ValueError(f"command has no value after {flag}")
    out[idx + 1] = value
    return out


def _quote_command(command: List[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def _rewrite_workload(
    workload: Dict[str, Any],
    *,
    remote_root: str,
    remote_repo_root: str,
    remote_author_bin: str,
    remote_python: str,
) -> Dict[str, Any]:
    workload_id = _safe_workload_id(workload.get("workload_id"))
    input1_local = str(workload.get("input1", {}).get("materialized_path") or "")
    input2_local = str(workload.get("input2", {}).get("materialized_path") or "")
    if not input1_local or not input2_local:
        raise ValueError(f"workload {workload_id} has no materialized input paths")
    if not pathlib.Path(input1_local).exists() or not pathlib.Path(input2_local).exists():
        raise ValueError(f"workload {workload_id} materialized input paths do not exist")

    remote_input_dir = posixpath.join(remote_root, "inputs", workload_id)
    remote_output_dir = posixpath.join(remote_root, "outputs")
    remote_input1 = posixpath.join(remote_input_dir, "input1" + _suffix_from_path(input1_local, ".dat"))
    remote_input2 = posixpath.join(remote_input_dir, "input2" + _suffix_from_path(input2_local, ".dat"))
    remote_author_json = posixpath.join(remote_output_dir, f"{workload_id}.author_hd_exec.json")
    remote_rtdl_json = posixpath.join(remote_output_dir, f"{workload_id}.rtdl_hd_exec.json")

    author_cmd = list(workload.get("author_command") or [])
    rtdl_cmd = list(workload.get("rtdl_command") or [])
    if not author_cmd or not rtdl_cmd:
        raise ValueError(f"workload {workload_id} missing author or RTDL command")

    author_cmd[0] = remote_author_bin
    author_cmd = _replace_arg(author_cmd, "-input1", remote_input1)
    author_cmd = _replace_arg(author_cmd, "-input2", remote_input2)
    author_cmd = _replace_arg(author_cmd, "-json", remote_author_json)

    rtdl_cmd[0] = remote_python
    if len(rtdl_cmd) < 2:
        raise ValueError(f"workload {workload_id} malformed RTDL command")
    rtdl_cmd[1] = posixpath.join(remote_repo_root, RTDL_SCRIPT_RELATIVE)
    rtdl_cmd = _replace_arg(rtdl_cmd, "-input1", remote_input1)
    rtdl_cmd = _replace_arg(rtdl_cmd, "-input2", remote_input2)
    rtdl_cmd = _replace_arg(rtdl_cmd, "-json", remote_rtdl_json)

    return {
        "workload_id": workload_id,
        "local_inputs": {
            "input1": input1_local,
            "input2": input2_local,
        },
        "remote_inputs": {
            "input1": remote_input1,
            "input2": remote_input2,
        },
        "remote_outputs": {
            "author_json": remote_author_json,
            "rtdl_json": remote_rtdl_json,
        },
        "author_command": author_cmd,
        "rtdl_command": rtdl_cmd,
        "author_command_shell": _quote_command(author_cmd),
        "rtdl_command_shell": _quote_command(rtdl_cmd),
    }


def build_plan(
    packet_path: pathlib.Path,
    *,
    remote_root: str,
    remote_repo_root: str,
    remote_author_bin: str,
    remote_python: str,
    host: str,
    port: int,
) -> Dict[str, Any]:
    packet = _load_json(packet_path)
    errors: List[str] = []
    if packet.get("schema") != "rtdl.paper_reproduction.xhd.mapped_candidate_same_input_gate_packet.v1":
        errors.append("packet schema mismatch")
    if packet.get("classification") != "mapped_candidate_same_input_gate_commands_ready":
        errors.append(f"packet is not command-ready: {packet.get('classification')}")
    if packet.get("pod_allowed_next") is not True:
        errors.append("packet does not allow POD next")

    workloads = packet.get("workload_packets")
    if not isinstance(workloads, list) or not workloads:
        errors.append("packet has no workload_packets")
        workloads = []

    remote_workloads: List[Dict[str, Any]] = []
    if not errors:
        for workload in workloads:
            if not isinstance(workload, dict):
                errors.append("non-object workload packet")
                continue
            try:
                remote_workloads.append(
                    _rewrite_workload(
                        workload,
                        remote_root=remote_root.rstrip("/"),
                        remote_repo_root=remote_repo_root.rstrip("/"),
                        remote_author_bin=remote_author_bin,
                        remote_python=remote_python,
                    )
                )
            except Exception as exc:
                errors.append(f"{workload.get('workload_id')}: {exc}")

    classification = (
        "mapped_candidate_pod_execution_plan_ready"
        if not errors and remote_workloads
        else "mapped_candidate_pod_execution_plan_not_ready"
    )
    remote_prepare_commands = [
        f"mkdir -p {shlex.quote(posixpath.join(remote_root, 'inputs'))} {shlex.quote(posixpath.join(remote_root, 'outputs'))}",
    ]
    upload_steps: List[Dict[str, Any]] = []
    for workload in remote_workloads:
        remote_dir = posixpath.dirname(workload["remote_inputs"]["input1"])
        remote_prepare_commands.append(f"mkdir -p {shlex.quote(remote_dir)}")
        for role in ("input1", "input2"):
            upload_steps.append(
                {
                    "local": workload["local_inputs"][role],
                    "remote": workload["remote_inputs"][role],
                    "wrapper_command": _wrapper_upload(host, port, workload["local_inputs"][role], workload["remote_inputs"][role]),
                }
            )

    execution_commands: List[str] = []
    for workload in remote_workloads:
        execution_commands.extend([workload["author_command_shell"], workload["rtdl_command_shell"]])
    remote_execute_shell = "set -e; " + "; ".join(remote_prepare_commands + execution_commands) if remote_workloads else ""

    download_steps: List[Dict[str, Any]] = []
    local_output_dir = pathlib.Path(str(packet_path)).resolve().parent / "pod-output"
    for workload in remote_workloads:
        for key, remote in workload["remote_outputs"].items():
            local = str((local_output_dir / pathlib.PurePosixPath(remote).name).resolve())
            download_steps.append(
                {
                    "remote": remote,
                    "local": local,
                    "wrapper_command": _wrapper_download(host, port, remote, local),
                    "output_key": key,
                }
            )

    comparator_command = [
        sys.executable,
        str((ROOT / COMPARATOR_RELATIVE).resolve()),
        str(packet_path.resolve()),
        "--output",
        str((local_output_dir / "mapped_candidate_output_comparison.json").resolve()),
    ]

    return {
        "schema": "rtdl.paper_reproduction.xhd.mapped_candidate_pod_execution_plan.v1",
        "packet_path": str(packet_path.resolve()),
        "classification": classification,
        "pod_allowed_next": classification == "mapped_candidate_pod_execution_plan_ready",
        "host": host,
        "port": int(port),
        "remote_root": remote_root,
        "remote_repo_root": remote_repo_root,
        "remote_author_bin": remote_author_bin,
        "remote_python": remote_python,
        "remote_workload_count": len(remote_workloads),
        "remote_workloads": remote_workloads,
        "upload_steps": upload_steps,
        "remote_execute_shell": remote_execute_shell,
        "wrapper_preflight_command": _wrapper_preflight(host, port),
        "wrapper_remote_execute_command": _wrapper_exec(host, port, remote_execute_shell) if remote_execute_shell else None,
        "download_steps": download_steps,
        "local_comparator_command": comparator_command,
        "local_comparator_command_shell": _quote_command(comparator_command),
        "commands_executed": False,
        "outputs_compared": False,
        "errors": errors,
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
            "claiming POD execution from this plan",
            "claiming same-input correctness from this plan",
            "claiming exact paper dataset reproduction from this plan",
            "claiming Figure 5 reproduction from this plan",
            "claiming full X-HD paper reproduction from this plan",
            "claiming author-vs-RTDL performance ratio from this plan",
            "running naked ssh or scp instead of scripts/current_pod_ssh.py",
        ],
    }


def _wrapper_base(host: str, port: int) -> List[str]:
    return [sys.executable, str(CURRENT_POD_WRAPPER), "--host", host, "--port", str(port)]


def _wrapper_preflight(host: str, port: int) -> List[str]:
    return _wrapper_base(host, port) + ["preflight"]


def _wrapper_exec(host: str, port: int, command: str) -> List[str]:
    return _wrapper_base(host, port) + ["exec", command]


def _wrapper_upload(host: str, port: int, local: str, remote: str) -> List[str]:
    return _wrapper_base(host, port) + ["upload", local, remote]


def _wrapper_download(host: str, port: int, remote: str, local: str) -> List[str]:
    return _wrapper_base(host, port) + ["download", remote, local]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_json", type=pathlib.Path)
    parser.add_argument("--remote-root", required=True)
    parser.add_argument("--remote-repo-root", required=True)
    parser.add_argument("--remote-author-bin", default="hd_exec")
    parser.add_argument("--remote-python", default="python3")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        plan = build_plan(
            args.packet_json,
            remote_root=args.remote_root,
            remote_repo_root=args.remote_repo_root,
            remote_author_bin=args.remote_author_bin,
            remote_python=args.remote_python,
            host=args.host,
            port=args.port,
        )
    except Exception as exc:
        print(f"mapped candidate POD execution plan failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(plan, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if plan["classification"] == "mapped_candidate_pod_execution_plan_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
