#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_STEM = "goal1490_v1_5_4_optix_dependency_handoff_2026-05-07"
DEFAULT_PREFLIGHT = ROOT / "docs" / "reports" / "goal1489_v1_5_4_optix_device_buffer_preflight_pod_2026-05-07.json"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def load_preflight(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_handoff(preflight: dict[str, Any]) -> dict[str, Any]:
    blockers = tuple(preflight.get("blockers", ()))
    optix_blocked = any(
        blocker in blockers
        for blocker in (
            "optix_header_available",
            "optix_library_or_build_toolchain_available",
            "rtdl_optix_library_exists",
        )
    )
    acceptable_resolution_paths = (
        {
            "name": "install_optix_sdk_headers_then_build",
            "requires": (
                "OptiX SDK root with include/optix.h",
                "CUDA toolkit with nvcc",
                "CUDA driver library",
            ),
            "commands": (
                "export OPTIX_PREFIX=/path/to/NVIDIA-OptiX-SDK",
                "export CUDA_PREFIX=/usr/local/cuda",
                "make build-optix OPTIX_PREFIX=$OPTIX_PREFIX CUDA_PREFIX=$CUDA_PREFIX",
                "export RTDL_OPTIX_LIB=$(pwd)/build/librtdl_optix.so",
                "PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py",
            ),
        },
        {
            "name": "provide_compatible_prebuilt_librtdl_optix",
            "requires": (
                "prebuilt librtdl_optix.so from the same source commit or documented compatible commit",
                "matching CUDA driver/runtime availability",
            ),
            "commands": (
                "export RTDL_OPTIX_LIB=/path/to/librtdl_optix.so",
                "PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py",
            ),
        },
        {
            "name": "use_optix_ready_image",
            "requires": (
                "image already contains OptiX SDK headers",
                "image already contains CUDA toolkit and nvcc",
                "repo can build or load librtdl_optix.so",
            ),
            "commands": (
                "git fetch origin",
                "git reset --hard origin/main",
                "PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py",
            ),
        },
    )
    return {
        "goal": "Goal1490",
        "scope": "v1.5.4 OptiX dependency handoff for RTDL-owned device-buffer execution",
        "source_preflight_valid": bool(preflight.get("valid_for_optix_device_buffer_execution_work")),
        "source_preflight_blockers": blockers,
        "optix_dependency_blocked": optix_blocked,
        "accepted_current_pod_uses": (
            "CUDA Driver API allocation probes",
            "CUDA Driver API copy-boundary probes",
            "preflight and diagnostic checks",
        ),
        "blocked_current_pod_uses": (
            "end_to_end_rtdl_optix_device_buffer_execution",
            "native_optix_extension_build_without_optix_headers",
            "public_true_zero_copy_or_speedup_claims",
        ),
        "acceptable_resolution_paths": acceptable_resolution_paths,
        "must_rerun_after_resolution": (
            "PYTHONPATH=src:. python3 scripts/goal1489_v1_5_4_optix_device_buffer_preflight.py",
            "PYTHONPATH=src:. python3 -m unittest tests.goal1489_v1_5_4_optix_device_buffer_preflight_test tests.goal1488_v1_5_4_cuda_evidence_boundary_gate_test",
        ),
        "next_milestone_after_green_preflight": (
            "add_or_select_backend_entry_accepting_rtdl_owned_device_memory_descriptor",
            "run_same_contract_parity_against_host_or_embree_path",
            "record_transfer_counts_around_backend_execution",
            "write candidate-only evidence report",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1490 is an OptiX dependency handoff only. It does not install "
            "OptiX, does not run RTDL/OptiX backend execution, and does not "
            "authorize true zero-copy wording, public speedup wording, "
            "whole-app claims, partner tensor handoff, or release action."
        ),
    }


def validate_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("goal") != "Goal1490":
        raise ValueError("invalid Goal1490 handoff goal")
    if payload.get("optix_dependency_blocked") is not True:
        raise ValueError("Goal1490 handoff should be based on blocked OptiX dependencies")
    if len(payload.get("acceptable_resolution_paths", ())) != 3:
        raise ValueError("Goal1490 handoff must list the three acceptable resolution paths")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if payload.get(flag) is not False:
            raise ValueError(f"Goal1490 handoff must keep {flag}=False")
    for phrase in (
        "dependency handoff only",
        "does not install OptiX",
        "does not run RTDL/OptiX backend execution",
        "does not authorize true zero-copy wording",
        "public speedup wording",
        "release action",
    ):
        if phrase not in payload.get("claim_boundary", ""):
            raise ValueError("Goal1490 handoff claim boundary is incomplete")
    return payload


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal 1490: v1.5.4 OptiX Dependency Handoff",
        "",
        "## Verdict",
        "",
        f"OptiX dependency blocked: `{payload['optix_dependency_blocked']}`.",
        "",
        "## Current Pod",
        "",
        "Accepted uses:",
    ]
    for item in payload["accepted_current_pod_uses"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "Blocked uses:"])
    for item in payload["blocked_current_pod_uses"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Resolution Paths", ""])
    for path in payload["acceptable_resolution_paths"]:
        lines.append(f"### {path['name']}")
        lines.append("")
        lines.append("Requires:")
        for requirement in path["requires"]:
            lines.append(f"- `{requirement}`")
        lines.append("")
        lines.append("Commands:")
        lines.append("")
        lines.append("```bash")
        for command in path["commands"]:
            lines.append(command)
        lines.append("```")
        lines.append("")
    lines.extend(["## Must Rerun", ""])
    for command in payload["must_rerun_after_resolution"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Goal1490 OptiX dependency handoff.")
    parser.add_argument("--preflight-json", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = validate_handoff(build_handoff(load_preflight(args.preflight_json)))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"optix_dependency_blocked": payload["optix_dependency_blocked"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
