#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.goal1502_v1_5_4_python_optix_collect_k_bounds_probe import (
    validate_probe as validate_goal1502_probe,
)
from scripts.goal1503_v1_5_4_optix_collect_k_scaling_probe import (
    validate_probe as validate_goal1503_probe,
)
from scripts.goal1504_v1_5_4_optix_collect_k_tiled_overflow_probe import (
    validate_probe as validate_goal1504_probe,
)


REPORT_STEM = "goal1505_v1_5_4_optix_collect_k_evidence_summary_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
REPORTS_DIR = ROOT / "docs" / "reports"

ARTIFACTS = {
    "ada_bounds": REPORTS_DIR / "goal1502_v1_5_4_python_optix_collect_k_bounds_probe_2026-05-08.json",
    "blackwell_bounds": (
        REPORTS_DIR / "goal1502_v1_5_4_python_optix_collect_k_bounds_probe_blackwell_2026-05-08.json"
    ),
    "ada_scaling": REPORTS_DIR / "goal1503_v1_5_4_optix_collect_k_scaling_probe_2026-05-08.json",
    "blackwell_scaling": REPORTS_DIR / "goal1503_v1_5_4_optix_collect_k_scaling_probe_blackwell_2026-05-08.json",
    "blackwell_overflow": REPORTS_DIR / "goal1504_v1_5_4_optix_collect_k_tiled_overflow_probe_2026-05-08.json",
}

CLAIM_FLAGS = (
    "true_zero_copy_authorized",
    "public_speedup_wording_authorized",
    "whole_app_speedup_claim_authorized",
    "stable_public_primitive_authorized",
    "partner_tensor_handoff_authorized",
    "release_action_authorized",
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_record(name: str, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "goal": payload["goal"],
        "status": payload["status"],
        "git_commit": payload.get("git_commit", "unknown"),
        "device_name": payload.get("device_name", "unknown"),
        "measured_on_real_nvidia": payload.get("measured_on_real_nvidia") is True,
    }


def _scaling_summary(payload: dict[str, Any]) -> dict[str, Any]:
    cases = payload["cases"]
    max_case = max(cases, key=lambda case: int(case["candidate_count"]))
    tiled_cases = [
        case
        for case in cases
        if case.get("expected_native_path") == "row_width2_bounded_multi_tile_sort_merge"
    ]
    return {
        "artifact_status": payload["status"],
        "device_name": payload["device_name"],
        "case_count": len(cases),
        "max_candidate_count": int(max_case["candidate_count"]),
        "max_candidate_median_ms": float(max_case["median_ms"]),
        "tiled_case_count": len(tiled_cases),
        "all_parity_passed": payload["all_parity_passed"],
    }


def _collect_claim_flags(payloads: list[dict[str, Any]]) -> dict[str, bool]:
    flags: dict[str, bool] = {flag: False for flag in CLAIM_FLAGS}
    for payload in payloads:
        for flag, value in payload.get("claim_flags", {}).items():
            if flag in flags:
                flags[flag] = flags[flag] or bool(value)
    return flags


def build_summary() -> dict[str, Any]:
    payloads = {name: _read_json(path) for name, path in ARTIFACTS.items()}

    validate_goal1502_probe(payloads["ada_bounds"])
    validate_goal1502_probe(payloads["blackwell_bounds"])
    validate_goal1503_probe(payloads["ada_scaling"])
    validate_goal1503_probe(payloads["blackwell_scaling"])
    validate_goal1504_probe(payloads["blackwell_overflow"])

    all_payloads = list(payloads.values())
    observed_claim_flags = _collect_claim_flags(all_payloads)
    if any(observed_claim_flags.values()):
        enabled = [flag for flag, value in observed_claim_flags.items() if value]
        raise ValueError(f"Goal1505 evidence summary requires conservative claim flags: {enabled}")

    ada_scaling = _scaling_summary(payloads["ada_scaling"])
    blackwell_scaling = _scaling_summary(payloads["blackwell_scaling"])
    blackwell_overflow = payloads["blackwell_overflow"]
    overflow_cases = blackwell_overflow["cases"]

    return {
        "goal": "Goal1505",
        "status": "goal1505_optix_collect_k_evidence_summary_recorded",
        "source_artifacts": [
            _artifact_record(name, ARTIFACTS[name], payloads[name])
            for name in (
                "ada_bounds",
                "blackwell_bounds",
                "ada_scaling",
                "blackwell_scaling",
                "blackwell_overflow",
            )
        ],
        "evidence_scope": {
            "primitive": "experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge",
            "row_width2_fast_path_max_candidate_count": 131072,
            "dynamic_row_width_validated": True,
            "int64_max_pair_validated": True,
            "overflow_fail_closed_validated": True,
            "measured_devices": sorted(
                {
                    payloads["ada_bounds"]["device_name"],
                    payloads["ada_scaling"]["device_name"],
                    payloads["blackwell_bounds"]["device_name"],
                    payloads["blackwell_scaling"]["device_name"],
                    payloads["blackwell_overflow"]["device_name"],
                }
            ),
        },
        "scaling_summaries": {
            "ada": ada_scaling,
            "blackwell": blackwell_scaling,
        },
        "overflow_summary": {
            "device_name": blackwell_overflow["device_name"],
            "case_count": len(overflow_cases),
            "candidate_counts": [int(case["candidate_count"]) for case in overflow_cases],
            "all_fail_closed_passed": blackwell_overflow["all_fail_closed_passed"],
        },
        "claim_authorization": {
            "experimental_public_promotion_authorized": False,
            "stable_public_primitive_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1505 only indexes already committed Goal1502/Goal1503/Goal1504 OptiX "
            "COLLECT_K_BOUNDED artifacts. It records that real NVIDIA parity, bounded "
            "row_width=2 scaling through 131072 candidates, dynamic-width behavior, "
            "INT64_MAX row behavior, and fail-closed overflow behavior have evidence. "
            "It does not authorize public speedup wording, true zero-copy wording, "
            "whole-app claims, partner tensor handoff, stable primitive promotion, "
            "experimental public promotion, release action, or any new GPU claim."
        ),
    }


def validate_summary(summary: dict[str, Any]) -> dict[str, Any]:
    if summary.get("goal") != "Goal1505":
        raise ValueError("invalid Goal1505 summary goal")
    if summary.get("status") != "goal1505_optix_collect_k_evidence_summary_recorded":
        raise ValueError("invalid Goal1505 summary status")
    artifacts = summary.get("source_artifacts", [])
    if len(artifacts) != len(ARTIFACTS):
        raise ValueError("Goal1505 must list every source artifact")
    if not all(artifact.get("measured_on_real_nvidia") for artifact in artifacts):
        raise ValueError("Goal1505 source artifacts must be real NVIDIA measurements")
    scope = summary.get("evidence_scope", {})
    if scope.get("row_width2_fast_path_max_candidate_count") != 131072:
        raise ValueError("Goal1505 must preserve the bounded row_width=2 max scope")
    for key in ("dynamic_row_width_validated", "int64_max_pair_validated", "overflow_fail_closed_validated"):
        if scope.get(key) is not True:
            raise ValueError(f"Goal1505 requires {key}=True")
    for flag, value in summary.get("claim_authorization", {}).items():
        if value is not False:
            raise ValueError(f"Goal1505 must keep {flag}=False")
    if "does not authorize public speedup wording" not in summary.get("claim_boundary", ""):
        raise ValueError("Goal1505 claim boundary must reject public speedup wording")
    return summary


def to_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Goal 1505: OptiX COLLECT_K_BOUNDED Evidence Summary",
        "",
        "## Verdict",
        "",
        f"`{summary['status']}`",
        "",
        "This is an evidence registry, not a new measurement and not a release action.",
        "",
        "## Source Artifacts",
        "",
    ]
    for artifact in summary["source_artifacts"]:
        lines.append(
            "- `{path}`: goal=`{goal}`, status=`{status}`, device=`{device_name}`, commit=`{git_commit}`".format(
                **artifact
            )
        )
    lines.extend(["", "## Evidence Scope", ""])
    scope = summary["evidence_scope"]
    lines.extend(
        [
            f"- Primitive: `{scope['primitive']}`",
            f"- Row_width=2 fast/tiled path max candidate count: `{scope['row_width2_fast_path_max_candidate_count']}`",
            f"- Dynamic row-width validated: `{scope['dynamic_row_width_validated']}`",
            f"- INT64_MAX pair validated: `{scope['int64_max_pair_validated']}`",
            f"- Overflow fail-closed validated: `{scope['overflow_fail_closed_validated']}`",
            f"- Measured devices: `{', '.join(scope['measured_devices'])}`",
            "",
            "## Scaling",
            "",
        ]
    )
    for name, scaling in summary["scaling_summaries"].items():
        lines.append(
            "- `{name}`: device=`{device_name}`, cases=`{case_count}`, max_candidates=`{max_candidate_count}`, "
            "max_candidate_median_ms=`{max_candidate_median_ms:.6f}`, tiled_cases=`{tiled_case_count}`, "
            "all_parity_passed=`{all_parity_passed}`".format(name=name, **scaling)
        )
    overflow = summary["overflow_summary"]
    lines.extend(
        [
            "",
            "## Overflow",
            "",
            f"- Device: `{overflow['device_name']}`",
            f"- Candidate counts: `{overflow['candidate_counts']}`",
            f"- All fail-closed passed: `{overflow['all_fail_closed_passed']}`",
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize committed OptiX collect-k evidence artifacts.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = validate_summary(build_summary())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(summary), encoding="utf-8")
    print(json.dumps({"status": summary["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
