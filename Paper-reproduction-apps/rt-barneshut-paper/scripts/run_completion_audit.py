#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def requirement(requirement_id: str, description: str, status: str, evidence: Any) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "description": description,
        "status": status,
        "evidence": evidence,
    }


def build_audit(app_dir: Path) -> dict[str, Any]:
    manifest_path = app_dir / "data" / "manifest.json"
    local_gate_path = app_dir / "_runs" / "local_contract_gate" / "summary.json"
    source_gate_path = app_dir / "_runs" / "author_source_contract_gate" / "summary.json"
    full_gate_path = app_dir / "_runs" / "full_pod_reproduction_gate" / "summary.json"
    performance_review_gate_path = app_dir / "_runs" / "phase_boundary_review_gate" / "summary.json"

    manifest = read_json(manifest_path)
    local_gate = read_json(local_gate_path)
    source_gate = read_json(source_gate_path)
    full_gate = read_json(full_gate_path)
    performance_review_gate = read_json(performance_review_gate_path)

    author = (manifest or {}).get("author_artifact", {})
    pinned_author_ready = bool(
        author.get("repository")
        and author.get("branch")
        and author.get("commit")
        and author.get("sample_path")
        and author.get("binary_target")
    )
    full_gate_available = full_gate is not None
    local_gate_complete = bool((local_gate or {}).get("status") == "passed")
    source_gate_complete = bool((source_gate or {}).get("status") == "passed")
    correctness_complete = bool((full_gate or {}).get("correctness_gates_complete"))
    performance_timing_ready = bool((full_gate or {}).get("performance_timing_gate_ready"))
    performance_review_accepted = bool((performance_review_gate or {}).get("status") == "accepted")

    requirements = [
        requirement(
            "author_artifact_pinned",
            "Pinned author repository, branch, commit, sample path, and binary target are recorded.",
            "complete" if pinned_author_ready else "missing",
            {"manifest": str(manifest_path), "author_artifact": author if manifest else None},
        ),
        requirement(
            "local_contract_gate_closed",
            "Local CPU contract gate closes one-bucket force/order alignment, expected historical multi-bucket diagnostic gap detection, and author-prepared aggregate-array alignment.",
            "complete" if local_gate_complete else "missing",
            {
                "summary": str(local_gate_path),
                "status": None if local_gate is None else local_gate.get("status"),
                "paper_reproduction_complete": None
                if local_gate is None
                else local_gate.get("paper_reproduction_complete"),
            },
        ),
        requirement(
            "author_source_contract_gate_closed",
            "Pinned raw author source checkout matches the manifest commit and contains the input, z-order, bucket-tree, opening-rule, and force-law anchors assumed by the app.",
            "complete" if source_gate_complete else "missing",
            {
                "summary": str(source_gate_path),
                "status": None if source_gate is None else source_gate.get("status"),
                "source_root": None if source_gate is None else source_gate.get("source_root"),
                "git": None if source_gate is None else source_gate.get("git"),
            },
        ),
        requirement(
            "full_pod_gate_ran",
            "Full POD gate summary exists for the current RT-BarnesHut app.",
            "complete" if full_gate_available else "missing",
            {"summary": str(full_gate_path), "overall_status": None if full_gate is None else full_gate.get("overall_status")},
        ),
        requirement(
            "same_input_correctness_closed",
            "Patched author same-input and author-vs-RTDL force-output correctness gates are closed.",
            "complete" if correctness_complete else "incomplete",
            {
                "summary": str(full_gate_path),
                "correctness_gates_complete": None if full_gate is None else full_gate.get("correctness_gates_complete"),
                "gates": None if full_gate is None else [
                    {"name": gate.get("name"), "status": gate.get("status")}
                    for gate in full_gate.get("gates", [])
                ],
            },
        ),
        requirement(
            "same_input_timing_summary_ready",
            "Same-input author and RTDL timing fields are summarized for phase-boundary review.",
            "complete" if performance_timing_ready else "incomplete",
            {
                "summary": str(full_gate_path),
                "performance_timing_gate_ready": None if full_gate is None else full_gate.get("performance_timing_gate_ready"),
            },
        ),
        requirement(
            "performance_phase_boundary_reviewed",
            "A phase-boundary review gate validates that the human review artifact accepts the timing comparison scope, source summary, phase labels, and ratio.",
            "complete" if performance_review_accepted else "missing",
            {
                "expected_gate_summary": str(performance_review_gate_path),
                "status": None if performance_review_gate is None else performance_review_gate.get("status"),
                "checks": None if performance_review_gate is None else performance_review_gate.get("checks"),
            },
        ),
    ]

    paper_reproduction_complete = all(row["status"] == "complete" for row in requirements)
    return {
        "mode": "rt_barneshut_completion_audit",
        "paper_reproduction_complete": paper_reproduction_complete,
        "overall_status": "complete" if paper_reproduction_complete else "incomplete",
        "requirements": requirements,
        "claim_boundary": (
            "Completion audit only. It proves RT-BarnesHut paper reproduction only "
            "when every listed requirement is complete. Local scaffold tests, "
            "manifest pins, or missing-summary failures are not enough."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit RT-BarnesHut paper-reproduction completion evidence.")
    parser.add_argument("--app-dir", type=Path, default=APP_DIR)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    app_dir = args.app_dir.resolve()
    output = args.output.resolve() if args.output else app_dir / "_runs" / "completion_audit" / "summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    audit = build_audit(app_dir)
    output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0 if audit["paper_reproduction_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
