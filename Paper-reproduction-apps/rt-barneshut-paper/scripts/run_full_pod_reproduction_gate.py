#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import subprocess
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"


def _tail(text: str, limit: int = 4000) -> str:
    return text if len(text) <= limit else text[-limit:]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"json_read_error": repr(exc), "path": str(path)}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bash_path(path: Path) -> str:
    if os.name != "nt":
        return str(path)
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return str(resolved)
    rest = resolved.as_posix().split(":", 1)[1].lstrip("/")
    return f"/mnt/{drive}/{rest}"


def run_gate(
    name: str,
    command: list[str],
    summary_path: Path,
    *,
    root_dir: Path,
    run_dir: Path,
) -> dict[str, Any]:
    print(f"[gate] {name}: {' '.join(command)}", flush=True)
    proc = subprocess.run(
        command,
        cwd=root_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=os.environ.copy(),
    )
    stdout_path = run_dir / f"{name}.stdout.txt"
    stderr_path = run_dir / f"{name}.stderr.txt"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    result = {
        "name": name,
        "status": "passed" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
        "command": command,
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
        "stdout_tail": _tail(proc.stdout),
        "stderr_tail": _tail(proc.stderr),
        "summary_path": str(summary_path),
        "summary": _read_json(summary_path),
    }
    print(f"[gate] {name}: {result['status']} (returncode={proc.returncode})", flush=True)
    return result


def skipped_gate(name: str, reason: str, depends_on: list[str] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": "skipped",
        "reason": reason,
        "depends_on": depends_on or [],
    }


def build_full_gate_summary(*, root_dir: Path, app_dir: Path, run_dir: Path) -> tuple[dict[str, Any], int]:
    run_dir.mkdir(parents=True, exist_ok=True)
    gates: list[dict[str, Any]] = []

    local_contract = run_gate(
        "local_contract_gate",
        ["bash", _bash_path(app_dir / "scripts" / "run_local_contract_gate.sh")],
        app_dir / "_runs" / "local_contract_gate" / "summary.json",
        root_dir=root_dir,
        run_dir=run_dir,
    )
    gates.append(local_contract)

    author_source_contract = run_gate(
        "author_source_contract_gate",
        ["bash", _bash_path(app_dir / "scripts" / "run_author_source_contract_gate.sh")],
        app_dir / "_runs" / "author_source_contract_gate" / "summary.json",
        root_dir=root_dir,
        run_dir=run_dir,
    )
    gates.append(author_source_contract)

    preflight = run_gate(
        "pod_environment_preflight",
        ["bash", _bash_path(app_dir / "scripts" / "check_pod_environment.sh")],
        app_dir / "_runs" / "pod_preflight" / "pod_environment_preflight.json",
        root_dir=root_dir,
        run_dir=run_dir,
    )
    gates.append(preflight)

    preflight_payload = preflight.get("summary") or {}
    ready_for_author_build = bool(preflight_payload.get("ready_for_author_build"))
    ready_for_rtdl_cuda_gate = bool(preflight_payload.get("ready_for_rtdl_cuda_gate"))

    local_contract_closed = bool(
        local_contract.get("status") == "passed"
        and (local_contract.get("summary") or {}).get("status") == "passed"
    )
    author_source_contract_closed = bool(
        author_source_contract.get("status") == "passed"
        and (author_source_contract.get("summary") or {}).get("status") == "passed"
    )

    if ready_for_rtdl_cuda_gate and local_contract_closed and author_source_contract_closed:
        rtdl_contract = run_gate(
            "author_contract_rtdl_cuda_gate",
            ["bash", _bash_path(app_dir / "scripts" / "run_author_contract_rtdl_cuda_gate.sh")],
            app_dir / "_runs" / "author_contract_rtdl_cuda_gate" / "summary.json",
            root_dir=root_dir,
            run_dir=run_dir,
        )
    else:
        reason = (
            "local_contract_gate did not pass"
            if not local_contract_closed
            else "author_source_contract_gate did not pass"
            if not author_source_contract_closed
            else "pod preflight did not report ready_for_rtdl_cuda_gate=true"
        )
        rtdl_contract = skipped_gate(
            "author_contract_rtdl_cuda_gate",
            reason,
            ["local_contract_gate", "author_source_contract_gate", "pod_environment_preflight"],
        )
    gates.append(rtdl_contract)

    if ready_for_author_build:
        author_comparator = run_gate(
            "author_comparator_gate",
            ["bash", _bash_path(app_dir / "scripts" / "run_author_comparator_gate.sh")],
            app_dir / "_runs" / "author_comparator_gate" / "summary.json",
            root_dir=root_dir,
            run_dir=run_dir,
        )
    else:
        author_comparator = skipped_gate(
            "author_comparator_gate",
            "pod preflight did not report ready_for_author_build=true",
            ["pod_environment_preflight"],
        )
    gates.append(author_comparator)

    if author_comparator["status"] == "passed":
        generic_force = run_gate(
            "generic_aggregate_force_same_input_gate",
            ["bash", _bash_path(app_dir / "scripts" / "run_generic_aggregate_force_same_input_gate.sh")],
            app_dir / "_runs" / "generic_aggregate_force_same_input_gate" / "summary.json",
            root_dir=root_dir,
            run_dir=run_dir,
        )
    else:
        generic_force = skipped_gate(
            "generic_aggregate_force_same_input_gate",
            "requires author_comparator_gate to produce author same-input prepared arrays and force output",
            ["author_comparator_gate"],
        )
    gates.append(generic_force)

    if author_comparator["status"] == "passed" and rtdl_contract["status"] == "passed":
        same_input = run_gate(
            "same_input_author_vs_rtdl_gate",
            ["bash", _bash_path(app_dir / "scripts" / "run_same_input_rtdl_comparison_gate.sh")],
            app_dir / "_runs" / "same_input_rtdl_comparison_gate" / "summary.json",
            root_dir=root_dir,
            run_dir=run_dir,
        )
    else:
        same_input = skipped_gate(
            "same_input_author_vs_rtdl_gate",
            "requires both author_comparator_gate and author_contract_rtdl_cuda_gate to pass",
            ["author_comparator_gate", "author_contract_rtdl_cuda_gate"],
        )
    gates.append(same_input)

    if same_input["status"] == "passed":
        performance = run_gate(
            "same_input_performance_gate",
            ["bash", _bash_path(app_dir / "scripts" / "run_same_input_performance_gate.sh")],
            app_dir / "_runs" / "same_input_performance_gate" / "summary.json",
            root_dir=root_dir,
            run_dir=run_dir,
        )
    else:
        performance = skipped_gate(
            "same_input_performance_gate",
            "requires same_input_author_vs_rtdl_gate to pass",
            ["same_input_author_vs_rtdl_gate"],
        )
    gates.append(performance)

    all_gates_passed = all(gate["status"] == "passed" for gate in gates)
    author_closed = bool((author_comparator.get("summary") or {}).get("same_input_author_comparator_closed"))
    generic_force_closed = bool(
        generic_force.get("status") == "passed"
        and (generic_force.get("summary") or {}).get("same_input_author_comparator")
        and ((generic_force.get("summary") or {}).get("force_comparison") or {}).get("matched")
    )
    rtdl_closed = bool((same_input.get("summary") or {}).get("same_input_author_rtdl_comparator_closed"))
    contract_closed = bool((rtdl_contract.get("summary") or {}).get("matched"))
    performance_ready = bool((performance.get("summary") or {}).get("status") == "ready_for_phase_boundary_review")
    correctness_gates_complete = bool(
        local_contract_closed
        and author_source_contract_closed
        and author_closed
        and generic_force_closed
        and rtdl_closed
        and contract_closed
    )

    if correctness_gates_complete and performance_ready:
        overall_status = "passed_correctness_and_timing_gates__phase_boundary_review_required"
    elif correctness_gates_complete:
        overall_status = "passed_correctness_gates__performance_timing_gate_open"
    elif not local_contract_closed:
        overall_status = "blocked_by_local_contract_gate"
    elif not author_source_contract_closed:
        overall_status = "blocked_by_author_source_contract_gate"
    elif preflight["status"] != "passed":
        overall_status = "blocked_by_pod_environment_preflight"
    elif any(gate["status"] == "failed" for gate in gates):
        overall_status = "blocked_by_failed_pod_gate"
    else:
        overall_status = "blocked_by_skipped_dependency"

    summary = {
        "mode": "rt_barneshut_full_pod_reproduction_gate",
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "overall_status": overall_status,
        "paper_reproduction_complete": False,
        "local_contract_gate_complete": local_contract_closed,
        "author_source_contract_gate_complete": author_source_contract_closed,
        "generic_aggregate_force_same_input_gate_complete": generic_force_closed,
        "correctness_gates_complete": correctness_gates_complete,
        "performance_timing_gate_ready": performance_ready,
        "performance_review_complete": False,
        "ready_for_author_build": ready_for_author_build,
        "ready_for_rtdl_cuda_gate": ready_for_rtdl_cuda_gate,
        "gates": gates,
        "claim_boundary": (
            "Full POD gate runner for RT-BarnesHut paper-reproduction engineering. "
            "It can close the local CPU contract, pinned author-source contract, "
            "environment, RTDL CUDA author-contract, patched-author same-input, "
            "generic aggregate same-input force-output, author-vs-RTDL force-output, "
            "and same-input timing summary gates. "
            "It does not by itself authorize a completed paper-reproduction claim "
            "until matched performance phase boundaries are reviewed."
        ),
    }
    return summary, 0 if correctness_gates_complete and performance_ready else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RT-BarnesHut full POD reproduction gates.")
    parser.add_argument("--root-dir", type=Path, default=ROOT_DIR)
    parser.add_argument("--app-dir", type=Path, default=APP_DIR)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    root_dir = args.root_dir.resolve()
    app_dir = args.app_dir.resolve()
    run_dir = app_dir / "_runs" / "full_pod_reproduction_gate"
    summary, exit_code = build_full_gate_summary(root_dir=root_dir, app_dir=app_dir, run_dir=run_dir)
    summary_path = args.output.resolve() if args.output else run_dir / "summary.json"
    _write_json(summary_path, summary)
    print(summary_path)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
