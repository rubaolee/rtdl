#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]

FINAL_MATRIX = "docs/reports/goal2068_final_v2_0_release_matrix.json"
PRE_RELEASE_GATE = "docs/reports/goal2069_v2_0_pre_release_gate.json"
GEMINI_REVIEW = "docs/reviews/goal2321_gemini_final_v2_0_release_cleanup_review_2026-05-18.md"
CLAUDE_REVIEW = "docs/reviews/goal2320_claude_final_v2_0_release_cleanup_review_2026-05-18.md"
FINAL_CONSENSUS = "docs/reports/goal2322_final_v2_0_release_cleanup_3ai_consensus_2026-05-18.md"
RELEASE_ACTION = "docs/reports/goal2323_v2_0_release_action_2026-05-18.md"


def _exists(path_text: str) -> bool:
    return (ROOT / path_text).exists()


def _json(path_text: str) -> dict[str, object]:
    return json.loads((ROOT / path_text).read_text(encoding="utf-8"))


def _text(path_text: str) -> str:
    return (ROOT / path_text).read_text(encoding="utf-8")


def _git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout.strip() or "unknown"


def _review_status(path_text: str, expected_reviewer: str) -> dict[str, object]:
    if not _exists(path_text):
        return {"present": False, "path": path_text, "verdict": None, "expected_reviewer": expected_reviewer}
    text = _text(path_text)
    verdict = None
    for candidate in ("accept-with-boundary", "accept", "reject", "needs-more-evidence"):
        if candidate in text.lower():
            verdict = candidate
            break
    return {
        "present": True,
        "path": path_text,
        "verdict": verdict,
        "expected_reviewer": expected_reviewer,
        "mentions_reviewer": expected_reviewer.lower() in text.lower(),
    }


def build_payload() -> dict[str, object]:
    matrix = _json(FINAL_MATRIX)
    gate = _json(PRE_RELEASE_GATE)
    gemini = _review_status(GEMINI_REVIEW, "Gemini")
    claude = _review_status(CLAUDE_REVIEW, "Claude")
    consensus_present = _exists(FINAL_CONSENSUS)
    release_action_present = _exists(RELEASE_ACTION)
    version_is_v2 = (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "v2.0"

    blockers: list[str] = []
    if matrix.get("status") != "final-v2-0-release-matrix-candidate":
        blockers.append("final v2.0 matrix candidate missing or not current")
    if gate.get("status") != "pass":
        blockers.append("v2.0 pre-release gate is not passing")
    if gate.get("claim_scan_status") != "pass":
        blockers.append("public v2.0 claim scan is not passing")
    if not gemini["present"]:
        blockers.append("final Gemini v2.0 release-gate review missing")
    if not claude["present"]:
        blockers.append("final Claude v2.0 release-gate review missing")
    if not consensus_present:
        blockers.append("final v2.0 3-AI release consensus missing")
    if not release_action_present or not version_is_v2:
        blockers.append("explicit user-requested release action missing")

    status = (
        "released"
        if release_action_present and version_is_v2 and consensus_present and not blockers
        else "blocked"
        if blockers
        else "ready-for-explicit-release-action"
    )
    return {
        "goal": "Goal2072",
        "date": "2026-05-18",
        "status": status,
        "git_commit": _git_commit(),
        "final_matrix": FINAL_MATRIX,
        "final_matrix_status": matrix.get("status"),
        "final_matrix_counts": matrix.get("counts_by_comparison_status"),
        "mixed_apps": matrix.get("mixed_apps"),
        "bounded_apps": matrix.get("bounded_apps"),
        "pre_release_gate": PRE_RELEASE_GATE,
        "pre_release_gate_status": gate.get("status"),
        "pre_release_gate_tests": gate.get("gate_tests", {}).get("summary"),
        "claim_scan_status": gate.get("claim_scan_status"),
        "external_reviews": {
            "gemini": gemini,
            "claude": claude,
        },
        "final_consensus_file": FINAL_CONSENSUS if consensus_present else None,
        "blockers": blockers,
        "release_claim_boundary": {
            "v2_0_release_authorized": release_action_present and version_is_v2 and consensus_present,
            "all_apps_have_current_pod_evidence": True,
            "all_apps_have_measured_v2_speedup": bool(
                matrix.get("release_claim_boundary", {}).get("all_apps_have_measured_v2_speedup", False)
            ),
            "all_current_optix_rt_rows_have_measured_v2_speedup": bool(
                matrix.get("release_claim_boundary", {}).get("all_current_optix_rt_rows_have_measured_v2_speedup", False)
            ),
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "arbitrary_partner_program_acceleration_authorized": False,
            "package_install_claim_authorized": False,
        },
        "next_action": (
            "Wait for current-head external reviews, then write final 3-AI consensus if both accept with appropriate boundaries."
            if not claude["present"] or not gemini["present"]
            else "Release action is complete; tag and push the committed tree if not already done."
            if consensus_present and release_action_present and version_is_v2
            else "Wait for explicit user release action."
            if consensus_present
            else "Write final 3-AI consensus if both current-head reviews accept with appropriate boundaries."
        ),
    }


def to_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal2072 v2.0 Final Readiness Aggregator",
        "",
        "Date: 2026-05-18",
        "",
        f"Status: `{payload['status']}`",
        "",
        "Goal2072 is the current final readiness object after Goal2068/2069/2073 and the Goal2323 release action.",
        "",
        "## Current Packet",
        "",
        f"- final matrix: `{payload['final_matrix']}`",
        f"- final matrix status: `{payload['final_matrix_status']}`",
        f"- final matrix counts: `{json.dumps(payload['final_matrix_counts'], sort_keys=True)}`",
        f"- mixed apps: `{json.dumps(payload['mixed_apps'])}`",
        f"- bounded apps: `{json.dumps(payload['bounded_apps'])}`",
        f"- pre-release gate: `{payload['pre_release_gate_status']}`",
        f"- focused gate tests: `{payload['pre_release_gate_tests']}`",
        f"- claim scan: `{payload['claim_scan_status']}`",
        "",
        "## External Reviews",
        "",
    ]
    reviews = payload["external_reviews"]
    assert isinstance(reviews, dict)
    for key, value in reviews.items():
        assert isinstance(value, dict)
        lines.append(
            f"- {key}: present=`{value['present']}`, verdict=`{value['verdict']}`, path=`{value['path']}`"
        )
    lines.extend(["", "## Blockers", ""])
    for blocker in payload["blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in payload["release_claim_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Next Action", "", str(payload["next_action"])])
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build final v2.0 readiness aggregator.")
    parser.add_argument("--output-json", default="docs/reports/goal2072_v2_0_final_readiness_aggregator.json")
    parser.add_argument("--output-md", default="docs/reports/goal2072_v2_0_final_readiness_aggregator_2026-05-15.md")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_payload()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
