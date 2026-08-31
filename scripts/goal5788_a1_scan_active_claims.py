#!/usr/bin/env python3
"""Fail-closed scan for unsuperseded all-ten Triangle attribution claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
SUCCESSOR = DOCS / "goal5788_amendment_a1_goal5787_claim_authority_successor_20260816.json"

RISK_PATTERNS = (
    re.compile(r"10 CI-clear wins", re.IGNORECASE),
    re.compile(r"ten (?:Goal5785 )?Triangle(?: clear)? wins", re.IGNORECASE),
    re.compile(r"Triangle has ten CI-clear wins", re.IGNORECASE),
    re.compile(r"Triangle \(10 CI-clear wins\)", re.IGNORECASE),
    re.compile(r"all ten Triangle(?: clear)? wins", re.IGNORECASE),
    re.compile(r"ten Triangle flips", re.IGNORECASE),
    re.compile(r"Triangle callback(?: plus| \+) device-reduction fusion: ten", re.IGNORECASE),
    re.compile(r"10 个.*Triangle", re.IGNORECASE),
    re.compile(r"十个 Triangle", re.IGNORECASE),
    re.compile(r"另外十个 Triangle", re.IGNORECASE),
)

CORRECTIVE_CONTEXT = {
    "history/internal_docs/goal5788_v4_cgo_academic_contribution_positioning_report_20260816.md",
    "history/internal_docs/self_review_goal5788_v4_cgo_academic_contribution_positioning_20260816.md",
    "history/internal_docs/review_goal5788_v4_cgo_academic_contribution_positioning_20260816.md",
    "history/internal_docs/goal5788_amendment_a1_attribution_and_claim_authority_correction_plan_20260816.md",
    "history/internal_docs/goal5788_amendment_a1_triangle_causal_interpretation_20260816.json",
    "history/internal_docs/goal5788_amendment_a1_goal5787_claim_authority_successor_20260816.json",
    "history/internal_docs/v4_competitive_cgo_submission_work_plan_after_goal5788_20260816.md",
    "history/internal_docs/goal5788_amendment_a1_attribution_and_claim_authority_correction_result_20260816.json",
    "history/internal_docs/goal5788_amendment_a1_attribution_and_claim_authority_correction_technical_report_20260816.md",
    "history/internal_docs/self_review_goal5788_amendment_a1_attribution_and_claim_authority_correction_20260816.md",
    "history/internal_docs/call_for_review_goal5788_amendment_a1_attribution_and_claim_authority_correction_20260816.md",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    successor = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
    superseded = {
        item["path"]: item["sha256"]
        for item in successor["immutable_historical_documents_with_superseded_all_ten_attribution"]
    }
    for relative, expected in superseded.items():
        path = ROOT / relative
        actual = digest(path)
        if actual != expected:
            raise AssertionError(f"superseded historical file drifted: {relative}: {actual}")

    occurrences = []
    unclassified = []
    for path in sorted(DOCS.glob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json"}:
            continue
        if path.resolve() == args.output.resolve():
            continue
        relative = path.relative_to(ROOT).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, 1):
            if not any(pattern.search(line) for pattern in RISK_PATTERNS):
                continue
            if relative in superseded:
                classification = "immutable_historical__explicitly_superseded_by_goal5788_a1"
            elif relative in CORRECTIVE_CONTEXT:
                classification = "corrective_or_forbidden-reading_context__not_active_all-ten_attribution"
            else:
                classification = "UNCLASSIFIED_ACTIVE_RISK"
                unclassified.append({"path": relative, "line": line_number, "text": line.strip()})
            occurrences.append(
                {
                    "path": relative,
                    "line": line_number,
                    "text": line.strip(),
                    "classification": classification,
                    "file_sha256": digest(path) if relative in superseded else None,
                }
            )
    if unclassified:
        raise AssertionError(json.dumps(unclassified, indent=2))
    result = {
        "schema": "rtdl.goal5788_a1.active_claim_scan.v1",
        "goal": "5788-A1",
        "scan_root": "history/internal_docs top-level UTF-8 .md/.json files",
        "successor_authority_path": SUCCESSOR.relative_to(ROOT).as_posix(),
        "successor_authority_sha256": digest(SUCCESSOR),
        "historical_superseded_file_count": len(superseded),
        "corrective_context_file_count": len(CORRECTIVE_CONTEXT),
        "matched_occurrence_count": len(occurrences),
        "occurrences": occurrences,
        "unclassified_active_risk_count": 0,
        "zero_unsuperseded_all_ten_checked_u64_attribution_statements": True,
        "scope_note": "Historical evidence remains byte-immutable. The successor controls all future manuscript and artifact claims.",
    }
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    args.output.write_bytes(payload)
    print(json.dumps({"output": str(args.output), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}))


if __name__ == "__main__":
    main()
