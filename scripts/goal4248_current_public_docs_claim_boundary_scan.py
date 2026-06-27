#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any, Iterable


SCHEMA = "rtdl.goal4248.current_public_docs_claim_boundary_scan.v1"

PUBLIC_DOC_ROOTS = (
    "README.md",
    "docs/versioning.md",
    "docs/learn",
    "tutorials",
    "examples/README.md",
    "examples/benchmark_apps",
)

CLAIM_PATTERNS = (
    r"\brelease authori[sz](?:e|ed|ation)\b",
    r"\bpublic speedup claim\b",
    r"\bwhole[- ]app(?:lication)? speedup\b",
    r"\bbroad RT[- ]core (?:speedup|claim|acceleration)\b",
    r"\bRTDL beats RayJoin\b",
    r"\bpaper[- ]reproduction claim\b",
    r"\bpaper reproduction\b",
    r"\btrue[- ]zero[- ]copy\b",
    r"\bautomatic partner selection\b",
    r"\bAMD(?:/HIPRT)? performance\b",
    r"\bHIPRT performance\b",
    r"\bpip install\b",
    r"\bpackage[- ]install\b",
    r"\b(?:faster|speedup|accelerated)\b",
)

NEGATIVE_OR_BOUNDARY_TOKENS = (
    "not ",
    "not a ",
    "does not",
    "do not",
    "no ",
    "without",
    "unauthorized",
    "blocked",
    "boundary",
    "claim-sensitive",
    "must remain",
    "remains false",
    "requires exact",
    "requires the",
    "before publishing",
    "before any",
    "not automatically",
    "cannot claim",
    "not public",
    "not universal",
    "not a release",
)

SCOPED_EVIDENCE_TOKENS = (
    "goal",
    "evidence",
    "reviewed",
    "bounded",
    "current",
    "about `",
    "about ",
    "limited",
    "same-contract",
    "per-request",
    "internal",
    "specific",
    "where available",
    "where documented",
)


def _public_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for item in PUBLIC_DOC_ROOTS:
        path = root / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return sorted(set(files))


def _line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _snippet(text: str, start: int, end: int, window: int = 180) -> str:
    return text[max(0, start - window) : min(len(text), end + window)].replace("\n", " ")


def _classify(snippet: str) -> str:
    normalized = snippet.lower()
    if any(token in normalized for token in NEGATIVE_OR_BOUNDARY_TOKENS):
        return "accepted_boundary_or_negative_context"
    if any(token in normalized for token in SCOPED_EVIDENCE_TOKENS):
        return "accepted_scoped_evidence_context"
    return "hard_blocker_unscoped_positive_claim"


def scan(root: Path) -> dict[str, Any]:
    regex = re.compile("|".join(f"({pattern})" for pattern in CLAIM_PATTERNS), re.IGNORECASE)
    findings: list[dict[str, Any]] = []
    by_class: dict[str, list[dict[str, Any]]] = {
        "hard_blocker_unscoped_positive_claim": [],
        "accepted_boundary_or_negative_context": [],
        "accepted_scoped_evidence_context": [],
    }
    for path in _public_files(root):
        text = path.read_text(encoding="utf-8")
        for match in regex.finditer(text):
            snippet = _snippet(text, match.start(), match.end())
            record = {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "line": _line_for(text, match.start()),
                "phrase": match.group(0),
                "classification": _classify(snippet),
                "snippet": snippet.strip(),
            }
            findings.append(record)
            by_class[record["classification"]].append(record)

    return {
        "schema": SCHEMA,
        "status": "pass" if not by_class["hard_blocker_unscoped_positive_claim"] else "fail",
        "public_files_scanned": [str(path.relative_to(root)).replace("\\", "/") for path in _public_files(root)],
        "public_file_count": len(_public_files(root)),
        "finding_count": len(findings),
        "hard_blocker_count": len(by_class["hard_blocker_unscoped_positive_claim"]),
        "accepted_boundary_or_negative_count": len(by_class["accepted_boundary_or_negative_context"]),
        "accepted_scoped_evidence_count": len(by_class["accepted_scoped_evidence_context"]),
        "hard_blockers": by_class["hard_blocker_unscoped_positive_claim"],
        "accepted_boundary_or_negative_context": by_class["accepted_boundary_or_negative_context"],
        "accepted_scoped_evidence_context": by_class["accepted_scoped_evidence_context"],
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "amd_performance_claim_authorized": False,
            "package_install_claim_authorized": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan current public docs for unscoped release/perf claims.")
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="docs/reports/goal4248_current_public_docs_claim_boundary_scan.json",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root)
    payload = scan(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
