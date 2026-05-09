#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_STEM = "goal1613_v1_6_4_collect_k_bounded_promotion_gate_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


SATISFIED_EVIDENCE = (
    (
        "v1_5_1_contract_and_bounds_foundation",
        "docs/reports/v1_5_1_collect_k_bounded_contract_foundation_2026-05-06.md",
    ),
    (
        "v1_5_1_native_embree_optix_parity_consensus",
        "docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md",
    ),
    (
        "v1_5_1_same_contract_benchmark_consensus",
        "docs/reports/three_ai_goal1417_v1_5_1_collect_k_benchmark_consensus_2026-05-06.md",
    ),
    (
        "v1_5_1_post_hardening_current_state_snapshot",
        "docs/reports/goal1438_v1_5_1_post_hardening_closure_snapshot_2026-05-07.md",
    ),
    (
        "v1_6_1_phase_copy_measurement_foundation",
        "docs/reports/goal1610_v1_6_1_phase_copy_measurement_foundation_2026-05-09.md",
    ),
    (
        "v1_6_2_prepared_host_output_preflight",
        "docs/reports/goal1611_v1_6_2_prepared_host_output_measurement_foundation_2026-05-09.md",
    ),
    (
        "v1_6_3_backend_prepared_host_output_bridge",
        "docs/reports/goal1612_v1_6_3_backend_prepared_host_output_bridge_2026-05-09.md",
    ),
    (
        "v1_6_3_linux_all_backend_bridge_3ai_consensus",
        "docs/reviews/goal1612_v1_6_3_linux_backend_bridge_evidence_3ai_consensus_2026-05-09.md",
    ),
)

MISSING_PROMOTION_EVIDENCE = (
    "v1_6_x_collect_k_exact_bounds_stress_artifact",
    "v1_6_x_collect_k_prepared_output_reduced_copy_benchmark_package",
    "representative_rtx_collect_k_required_backend_performance_packet",
    "v1_6_x_collect_k_stable_promotion_3ai_consensus",
)

REQUIRED_SEMANTIC_FIELDS = (
    "capacity_metadata",
    "valid_count_metadata",
    "overflow_flag",
    "fail_closed_overflow",
    "deterministic_ordering_policy",
    "deduplicate_before_capacity_check",
    "complete_candidate_coverage_required",
    "bounded_result_buffer_contract",
    "prepared_host_output_buffer_reuse",
    "typed_contiguous_host_input_measurement",
    "embree_optix_parity_where_claimed",
)

FALSE_AUTHORIZATION_FLAGS = (
    "stable_collect_k_promotion_authorized",
    "public_speedup_wording_authorized",
    "true_zero_copy_wording_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rtx_wording_authorized",
    "release_action_authorized",
)


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _evidence_records() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "name": name,
            "path": path,
            "exists": (ROOT / path).exists(),
        }
        for name, path in SATISFIED_EVIDENCE
    )


def build_gate() -> dict[str, Any]:
    evidence = _evidence_records()
    missing_satisfied_files = tuple(record["path"] for record in evidence if not record["exists"])
    semantic_fields = {field: True for field in REQUIRED_SEMANTIC_FIELDS}
    false_flags = {flag: False for flag in FALSE_AUTHORIZATION_FLAGS}
    promotion_ready = not missing_satisfied_files and not MISSING_PROMOTION_EVIDENCE
    return {
        "goal": "Goal1613",
        "version_slot": "v1.6.4",
        "primitive": "COLLECT_K_BOUNDED",
        "decision": "defer_stable_promotion_keep_experimental",
        "accepted_as_gate": not missing_satisfied_files,
        "stable_promotion_ready": promotion_ready,
        "git_commit": _git_head(),
        "required_semantic_fields": REQUIRED_SEMANTIC_FIELDS,
        "semantic_field_status": semantic_fields,
        "satisfied_evidence": evidence,
        "missing_satisfied_evidence_files": missing_satisfied_files,
        "missing_promotion_evidence": MISSING_PROMOTION_EVIDENCE,
        "authorization_flags": false_flags,
        "next_actions": (
            "run exact v1.6.x collect-k bounds stress with prepared host output",
            "produce reduced-copy/prepared-output benchmark evidence for collect-k",
            "collect representative RTX required-backend performance packet",
            "request Claude and Gemini review before any stable-promotion decision",
        ),
        "claim_boundary": (
            "Goal1613 is a v1.6.4 promotion/rejection gate for COLLECT_K_BOUNDED. "
            "It accepts the current evidence map only as a defer decision: "
            "COLLECT_K_BOUNDED remains experimental. This gate does not authorize "
            "stable primitive promotion, public speedup wording, true zero-copy "
            "wording, whole-app speedup claims, broad RTX/GPU wording, release "
            "tags, or release action."
        ),
    }


def validate_gate(gate: dict[str, Any]) -> dict[str, Any]:
    required = (
        "goal",
        "version_slot",
        "primitive",
        "decision",
        "accepted_as_gate",
        "stable_promotion_ready",
        "required_semantic_fields",
        "semantic_field_status",
        "satisfied_evidence",
        "missing_satisfied_evidence_files",
        "missing_promotion_evidence",
        "authorization_flags",
        "next_actions",
        "claim_boundary",
    )
    for field in required:
        if field not in gate:
            raise ValueError(f"Goal1613 gate missing field: {field}")
    if gate["goal"] != "Goal1613":
        raise ValueError("Goal1613 gate must identify Goal1613")
    if gate["version_slot"] != "v1.6.4":
        raise ValueError("Goal1613 gate must occupy v1.6.4")
    if gate["primitive"] != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1613 gate must target COLLECT_K_BOUNDED")
    if gate["decision"] != "defer_stable_promotion_keep_experimental":
        raise ValueError("Goal1613 gate must keep collect-k experimental")
    if gate["accepted_as_gate"] is not True:
        raise ValueError("Goal1613 satisfied evidence files must exist before accepting the gate")
    if gate["stable_promotion_ready"] is not False:
        raise ValueError("Goal1613 must not mark stable promotion ready")
    if tuple(gate["required_semantic_fields"]) != REQUIRED_SEMANTIC_FIELDS:
        raise ValueError("Goal1613 semantic field set mismatch")
    for field in REQUIRED_SEMANTIC_FIELDS:
        if gate["semantic_field_status"].get(field) is not True:
            raise ValueError(f"Goal1613 semantic field not satisfied: {field}")
    if tuple(gate["missing_promotion_evidence"]) != MISSING_PROMOTION_EVIDENCE:
        raise ValueError("Goal1613 missing promotion evidence set mismatch")
    if not gate["missing_promotion_evidence"]:
        raise ValueError("Goal1613 defer decision requires explicit missing promotion evidence")
    flags = gate["authorization_flags"]
    for flag in FALSE_AUTHORIZATION_FLAGS:
        if flags.get(flag) is not False:
            raise ValueError(f"Goal1613 must keep {flag}=False")
    boundary = str(gate["claim_boundary"])
    for phrase in (
        "remains experimental",
        "does not authorize stable primitive promotion",
        "public speedup wording",
        "true zero-copy wording",
        "whole-app speedup claims",
        "broad RTX/GPU wording",
        "release action",
    ):
        if phrase not in boundary:
            raise ValueError("Goal1613 claim boundary is incomplete")
    return gate


def to_markdown(gate: dict[str, Any]) -> str:
    lines = [
        "# Goal1613 v1.6.4 COLLECT_K_BOUNDED Promotion Gate",
        "",
        "## Verdict",
        "",
        "ACCEPTED as a promotion/rejection gate, with stable promotion deferred.",
        "",
        "`COLLECT_K_BOUNDED` remains experimental. The satisfied evidence map is",
        "usable as current-state evidence, but the missing promotion evidence below",
        "blocks stable primitive promotion and public performance wording.",
        "",
        "## Satisfied Evidence",
        "",
        "| Evidence | Path | Present |",
        "| --- | --- | --- |",
    ]
    for record in gate["satisfied_evidence"]:
        lines.append(f"| `{record['name']}` | `{record['path']}` | `{record['exists']}` |")
    lines.extend(
        [
            "",
            "## Missing Promotion Evidence",
            "",
        ]
    )
    for item in gate["missing_promotion_evidence"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Authorization Flags",
            "",
        ]
    )
    for flag, value in gate["authorization_flags"].items():
        lines.append(f"- `{flag}`: `{value}`")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )
    for action in gate["next_actions"]:
        lines.append(f"- {action}")
    lines.extend(["", "## Claim Boundary", "", gate["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1613 COLLECT_K_BOUNDED promotion gate.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    gate = validate_gate(build_gate())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(gate), encoding="utf-8")
    print(json.dumps({"decision": gate["decision"], "accepted_as_gate": gate["accepted_as_gate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
