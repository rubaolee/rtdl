#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


REPORT_STEM = "goal1489_v1_5_4_optix_device_buffer_preflight_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _probe(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "output_tail": completed.stdout[-4000:],
        }
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "output_tail": f"{type(exc).__name__}: {exc}"}


def _git_head() -> str:
    result = _probe(["git", "rev-parse", "HEAD"])
    return result["output_tail"].strip() if result["returncode"] == 0 else "unknown"


def _cuda_prefix() -> Path:
    if os.environ.get("CUDA_PREFIX"):
        return Path(os.environ["CUDA_PREFIX"])
    return Path("/usr/local/cuda")


def _nvcc(cuda_prefix: Path) -> Path:
    if os.environ.get("NVCC"):
        return Path(os.environ["NVCC"])
    return cuda_prefix / "bin" / "nvcc"


def _optix_prefix() -> Path | None:
    value = os.environ.get("OPTIX_PREFIX") or os.environ.get("OptiX_INSTALL_DIR")
    return Path(value) if value else None


def _optix_library() -> Path:
    value = os.environ.get("RTDL_OPTIX_LIB") or os.environ.get("RTDL_OPTIX_LIBRARY")
    if value:
        return Path(value)
    return ROOT / "build" / "librtdl_optix.so"


def _goal1488_gate_status() -> dict[str, Any]:
    reports = ROOT / "docs" / "reports"
    try:
        allocation = json.loads(
            (reports / "goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.json").read_text(
                encoding="utf-8"
            )
        )["allocation_evidence"]
        copy_boundary = json.loads(
            (reports / "goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json").read_text(
                encoding="utf-8"
            )
        )["allocation_evidence"]
        gate = rt.v1_5_4_managed_buffer_cuda_evidence_boundary_gate(
            allocation_evidence=allocation,
            copy_boundary_evidence=copy_boundary,
        )
        rt.validate_v1_5_4_managed_buffer_cuda_evidence_boundary_gate(gate)
    except Exception as exc:
        return {"accepted": False, "reason": f"{type(exc).__name__}: {exc}"}
    return {"accepted": True, "reason": None, "status": gate["status"]}


def run_preflight(*, dry_run: bool) -> dict[str, Any]:
    cuda_prefix = _cuda_prefix()
    nvcc = _nvcc(cuda_prefix)
    optix_prefix = _optix_prefix()
    optix_library = _optix_library()
    source_status = _probe(["git", "status", "--short"])
    dirty = bool(source_status["output_tail"].strip())
    nvidia_smi_path = shutil.which("nvidia-smi")
    libcuda = ctypes.util.find_library("cuda")
    optix_header_candidates = []
    if optix_prefix is not None:
        optix_header_candidates.append(optix_prefix / "include" / "optix.h")
    optix_header_candidates.extend(
        [
            ROOT / "third_party" / "optix" / "include" / "optix.h",
            Path("/usr/local/optix/include/optix.h"),
            Path("/opt/optix/include/optix.h"),
        ]
    )
    optix_header = next((path for path in optix_header_candidates if path.exists()), None)
    boundary_gate = _goal1488_gate_status()
    checks = {
        "source_clean": dry_run or not dirty,
        "goal1488_boundary_gate_accepted": boundary_gate["accepted"],
        "nvidia_smi_available": dry_run or nvidia_smi_path is not None,
        "cuda_driver_library_available": dry_run or libcuda is not None,
        "cuda_prefix_exists": dry_run or cuda_prefix.exists(),
        "nvcc_exists": dry_run or nvcc.exists(),
        "optix_header_available": dry_run or optix_header is not None,
        "optix_library_or_build_toolchain_available": dry_run
        or optix_library.exists()
        or (nvcc.exists() and optix_header is not None),
        "rtdl_optix_library_exists": dry_run or optix_library.exists(),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "goal": "Goal1489",
        "scope": "v1.5.4 OptiX device-buffer execution preflight",
        "dry_run": dry_run,
        "valid_for_optix_device_buffer_execution_work": not blockers,
        "checks": checks,
        "blockers": blockers,
        "source_commit": _git_head(),
        "environment": {
            "cuda_prefix": str(cuda_prefix),
            "nvcc": str(nvcc),
            "optix_prefix": None if optix_prefix is None else str(optix_prefix),
            "optix_header": None if optix_header is None else str(optix_header),
            "rtdl_optix_library": str(optix_library),
            "nvidia_smi_path": nvidia_smi_path,
            "libcuda": libcuda,
            "nvidia_smi": _probe(["nvidia-smi"]) if nvidia_smi_path else None,
            "nvcc_version": _probe([str(nvcc), "--version"]) if nvcc.exists() else None,
            "git_status_short": source_status,
            "goal1488_boundary_gate": boundary_gate,
        },
        "required_next_evidence": (
            "build_or_provide_librtdl_optix",
            "add_backend_entry_accepting_rtdl_owned_device_memory_descriptor",
            "run_same_contract_parity_against_host_or_embree_path",
            "record_transfer_counts_around_backend_execution",
            "external_ai_review_before_public_claims",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1489 is only an OptiX device-buffer execution preflight. It "
            "does not run backend execution and does not authorize true "
            "zero-copy wording, public speedup wording, whole-app claims, "
            "partner tensor handoff, or release action."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal 1489: v1.5.4 OptiX Device-Buffer Preflight",
        "",
        "## Verdict",
        "",
        f"Valid for OptiX device-buffer execution work: `{payload['valid_for_optix_device_buffer_execution_work']}`.",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for name, result in payload["checks"].items():
        lines.append(f"| `{name}` | `{result}` |")
    lines.extend(["", "## Blockers", ""])
    if payload["blockers"]:
        for blocker in payload["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Required Next Evidence",
            "",
        ]
    )
    for item in payload["required_next_evidence"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Goal1489 OptiX device-buffer preflight.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_preflight(dry_run=args.dry_run)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid_for_optix_device_buffer_execution_work"], "blockers": payload["blockers"]}, indent=2))
    return 0 if payload["valid_for_optix_device_buffer_execution_work"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
