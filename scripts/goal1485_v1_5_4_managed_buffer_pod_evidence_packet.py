#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


REPORT_STEM = "goal1485_v1_5_4_managed_buffer_pod_evidence_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": 127,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _git_head() -> str:
    result = _run_command(["git", "rev-parse", "HEAD"])
    return result["stdout"] if result["returncode"] == 0 else "unknown"


def _probe_environment() -> dict[str, Any]:
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "git_head": _git_head(),
        "nvidia_smi": _run_command(["nvidia-smi"]),
        "nvcc_version": _run_command(["nvcc", "--version"]),
    }


def _make_descriptor(*, buffer_kind: str, device: str, allocation_method: str) -> dict[str, Any]:
    pointer = 123456 if device != "cpu" else None
    return rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
        buffer_kind=buffer_kind,
        backend="optix",
        device=device,
        dtype="int64",
        shape=(16, 2),
        lifetime="explicit_release",
        byte_count=256,
        pointer=pointer,
        transfer_count_state=(
            "instrumentation_planned"
            if allocation_method != "synthetic_contract_only"
            else "not_measured"
        ),
    )


def build_payload(
    *,
    buffer_kind: str,
    device: str,
    allocation_method: str,
    host_to_device_transfers: int,
    device_to_host_transfers: int,
    device_residency_observed: bool,
    measured_on_real_nvidia: bool,
    hardware_identity: str | None,
    backend_version: str | None,
    measurement_scope: str,
) -> dict[str, Any]:
    environment = _probe_environment()
    descriptor = _make_descriptor(
        buffer_kind=buffer_kind,
        device=device,
        allocation_method=allocation_method,
    )
    lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
        descriptor,
        allocation_id="goal1485_managed_buffer_probe",
    )
    evidence = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
        lifecycle,
        allocation_method=allocation_method,
        measurement_backend="optix",
        measurement_scope=measurement_scope,
        host_to_device_transfers=host_to_device_transfers,
        device_to_host_transfers=device_to_host_transfers,
        device_residency_observed=device_residency_observed,
        measured_on_real_nvidia=measured_on_real_nvidia,
        hardware_identity=hardware_identity,
        backend_version=backend_version,
    )
    validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(evidence)
    nvidia_probe_ok = environment["nvidia_smi"]["returncode"] == 0
    nvcc_probe_ok = environment["nvcc_version"]["returncode"] == 0
    return {
        "goal": "Goal1485",
        "scope": "v1.5.4 Python+RTDL managed-buffer pod evidence packet",
        "environment": environment,
        "input": {
            "buffer_kind": buffer_kind,
            "device": device,
            "allocation_method": allocation_method,
            "host_to_device_transfers": int(host_to_device_transfers),
            "device_to_host_transfers": int(device_to_host_transfers),
            "device_residency_observed": bool(device_residency_observed),
            "measured_on_real_nvidia": bool(measured_on_real_nvidia),
            "hardware_identity": hardware_identity,
            "backend_version": backend_version,
            "measurement_scope": measurement_scope,
        },
        "probe_summary": {
            "nvidia_smi_ok": nvidia_probe_ok,
            "nvcc_ok": nvcc_probe_ok,
            "real_nvidia_evidence_attempted": bool(measured_on_real_nvidia),
            "candidate_only": bool(validated["true_zero_copy_evidence_candidate"]),
            "accepted_public_claim": False,
        },
        "allocation_evidence": validated,
        "pod_needed_for_stronger_result": not bool(validated["true_zero_copy_evidence_candidate"]),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1485 prepares or records a managed-buffer allocation evidence "
            "packet only. A candidate result is not a public zero-copy claim. "
            "This packet does not authorize public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    evidence = payload["allocation_evidence"]
    lines = [
        "# Goal 1485: v1.5.4 Managed Buffer Pod Evidence Packet",
        "",
        "## Verdict",
        "",
        "Pod evidence packet generated.",
        "",
        "This artifact does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, or release action.",
        "",
        "## Environment",
        "",
        f"- Commit: `{payload['environment']['git_head']}`",
        f"- NVIDIA probe OK: `{payload['probe_summary']['nvidia_smi_ok']}`",
        f"- NVCC probe OK: `{payload['probe_summary']['nvcc_ok']}`",
        "",
        "## Evidence",
        "",
        f"- Buffer kind: `{payload['input']['buffer_kind']}`",
        f"- Device: `{payload['input']['device']}`",
        f"- Allocation method: `{payload['input']['allocation_method']}`",
        f"- Host-to-device transfers: `{evidence['host_to_device_transfers']}`",
        f"- Device-to-host transfers: `{evidence['device_to_host_transfers']}`",
        f"- Device residency observed: `{evidence['device_residency_observed']}`",
        f"- Measured on real NVIDIA: `{evidence['measured_on_real_nvidia']}`",
        f"- Hardware identity: `{evidence['hardware_identity']}`",
        f"- Backend version: `{evidence['backend_version']}`",
        f"- True zero-copy evidence candidate: `{evidence['true_zero_copy_evidence_candidate']}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Goal1485 managed-buffer pod evidence packet.")
    parser.add_argument("--buffer-kind", default="rtdl_device_resident")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--allocation-method", default="synthetic_contract_only")
    parser.add_argument("--host-to-device-transfers", type=int, default=1)
    parser.add_argument("--device-to-host-transfers", type=int, default=0)
    parser.add_argument("--device-residency-observed", action="store_true")
    parser.add_argument("--measured-on-real-nvidia", action="store_true")
    parser.add_argument("--hardware-identity", default=None)
    parser.add_argument("--backend-version", default=None)
    parser.add_argument("--measurement-scope", default="goal1485_local_fail_closed_contract")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(
        buffer_kind=args.buffer_kind,
        device=args.device,
        allocation_method=args.allocation_method,
        host_to_device_transfers=args.host_to_device_transfers,
        device_to_host_transfers=args.device_to_host_transfers,
        device_residency_observed=args.device_residency_observed,
        measured_on_real_nvidia=args.measured_on_real_nvidia,
        hardware_identity=args.hardware_identity,
        backend_version=args.backend_version,
        measurement_scope=args.measurement_scope,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(payload, args.md_out)
    print(json.dumps(payload["probe_summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
