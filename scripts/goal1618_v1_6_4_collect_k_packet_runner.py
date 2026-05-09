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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import goal1614_v1_6_4_collect_k_bounds_stress as goal1614
from scripts import goal1615_v1_6_4_collect_k_reduced_copy_benchmark as goal1615


REPORT_STEM = "goal1618_v1_6_4_collect_k_packet_runner_smoke_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _git_head() -> str:
    return _run_text(["git", "rev-parse", "HEAD"]) or "unknown"


def _nvidia_smi_summary() -> str:
    return _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader",
        ]
    )


def _claim_boundary() -> str:
    return (
        "Goal1618 is a collect-k packet runner that executes Goal1614 bounds "
        "stress and Goal1615 reduced-copy/materialization-count benchmark "
        "commands under one artifact. It is packet-execution evidence only. "
        "Timing remains diagnostic only and this runner does not authorize "
        "public speedup wording, true zero-copy wording, stable "
        "COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, release tags, or "
        "release action."
    )


def build_manifest() -> dict[str, Any]:
    return {
        "goal": "Goal1618",
        "version_slot": "v1.6.4_packet_runner",
        "purpose": "single collect-k packet runner for local rehearsal and future RTX pod execution",
        "subgoals": ("Goal1614", "Goal1615"),
        "claim_boundary": _claim_boundary(),
        "representative_rtx_performance_evidence_authorized": False,
        "public_speedup_wording_authorized": False,
        "true_zero_copy_wording_authorized": False,
        "stable_collect_k_promotion_authorized": False,
        "broad_rtx_wording_authorized": False,
        "release_action_authorized": False,
    }


def run_packet(
    *,
    backends: tuple[str, ...] = ("fake_native",),
    required_backends: tuple[str, ...] = ("fake_native",),
    environment_label: str = "local_packet_runner_smoke",
) -> dict[str, Any]:
    bounds = goal1614.run_package(backends=backends, required_backends=required_backends)
    reduced = goal1615.run_package(backends=backends, required_backends=required_backends)
    accepted = bool(bounds["accepted"]) and bool(reduced["accepted"])
    return {
        "goal": "Goal1618",
        "version_slot": "v1.6.4_packet_runner",
        "status": "accepted_packet_execution" if accepted else "not_accepted",
        "accepted": accepted,
        "environment_label": environment_label,
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "nvidia_smi": _nvidia_smi_summary(),
        "backends": backends,
        "required_backends": required_backends,
        "manifest": build_manifest(),
        "subpackages": {
            "goal1614_bounds_stress": bounds,
            "goal1615_reduced_copy_benchmark": reduced,
        },
        "failed_subpackages": tuple(
            name
            for name, payload in (
                ("goal1614_bounds_stress", bounds),
                ("goal1615_reduced_copy_benchmark", reduced),
            )
            if not payload["accepted"]
        ),
        "representative_rtx_performance_evidence_authorized": False,
        "public_speedup_wording_authorized": False,
        "true_zero_copy_wording_authorized": False,
        "stable_collect_k_promotion_authorized": False,
        "broad_rtx_wording_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": _claim_boundary(),
    }


def validate_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["goal"] != "Goal1618":
        raise ValueError("Goal1618 payload must identify Goal1618")
    if payload["accepted"] is not True:
        raise ValueError("Goal1618 packet must have accepted subpackages")
    if tuple(payload["manifest"]["subgoals"]) != ("Goal1614", "Goal1615"):
        raise ValueError("Goal1618 must run Goal1614 and Goal1615")
    if payload["failed_subpackages"]:
        raise ValueError("Goal1618 accepted packet cannot have failed subpackages")
    subpackages = payload["subpackages"]
    if subpackages["goal1614_bounds_stress"]["accepted"] is not True:
        raise ValueError("Goal1618 requires accepted Goal1614 subpackage")
    if subpackages["goal1615_reduced_copy_benchmark"]["accepted"] is not True:
        raise ValueError("Goal1618 requires accepted Goal1615 subpackage")
    for flag in (
        "representative_rtx_performance_evidence_authorized",
        "public_speedup_wording_authorized",
        "true_zero_copy_wording_authorized",
        "stable_collect_k_promotion_authorized",
        "broad_rtx_wording_authorized",
        "release_action_authorized",
    ):
        if payload[flag] is not False:
            raise ValueError(f"Goal1618 must keep {flag}=False")
    boundary = payload["claim_boundary"]
    for phrase in (
        "packet-execution evidence only",
        "Timing remains diagnostic only",
        "does not authorize public speedup wording",
        "true zero-copy wording",
        "stable COLLECT_K_BOUNDED promotion",
        "broad RTX/GPU wording",
        "release action",
    ):
        if phrase not in boundary:
            raise ValueError("Goal1618 claim boundary is incomplete")
    return payload


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def to_markdown(payload: dict[str, Any]) -> str:
    bounds = payload["subpackages"]["goal1614_bounds_stress"]
    reduced = payload["subpackages"]["goal1615_reduced_copy_benchmark"]
    lines = [
        "# Goal1618 v1.6.4 Collect-K Packet Runner",
        "",
        "## Verdict",
        "",
        "ACCEPTED as packet-execution evidence." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        f"- Environment label: `{payload['environment_label']}`",
        f"- Backends: `{', '.join(payload['backends'])}`",
        f"- Required backends: `{', '.join(payload['required_backends'])}`",
        f"- Git commit: `{payload['git_commit']}`",
        f"- Host: `{payload['host']}`",
        f"- NVIDIA summary: `{payload['nvidia_smi'] or 'not reported'}`",
        "- Timing remains diagnostic only.",
        "",
        "## Subpackages",
        "",
        "| Subpackage | Status | Accepted |",
        "| --- | --- | --- |",
        f"| Goal1614 bounds stress | `{bounds['status']}` | `{bounds['accepted']}` |",
        f"| Goal1615 reduced-copy benchmark | `{reduced['status']}` | `{reduced['accepted']}` |",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1618 collect-k packet runner.")
    parser.add_argument("--backends", nargs="+", default=["fake_native"])
    parser.add_argument("--required-backends", nargs="*", default=["fake_native"])
    parser.add_argument("--environment-label", default="local_packet_runner_smoke")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = validate_packet(
        run_packet(
            backends=tuple(args.backends),
            required_backends=tuple(args.required_backends),
            environment_label=args.environment_label,
        )
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "accepted": payload["accepted"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
