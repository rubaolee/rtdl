#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Iterable


PUBLIC_PATTERNS = (
    "README.md",
    "docs/README.md",
    "docs/partner_acceleration_boundaries.md",
    "docs/tutorials/*.md",
)

CLAIM_PATTERNS = (
    r"pip install(?: -e)?",
    r"\bPyPI\b",
    r"package-install support",
    r"arbitrary PyTorch(?:/CuPy)? acceleration",
    r"arbitrary CuPy acceleration",
    r"broad RT-core (?:speedup|acceleration|evidence)",
    r"whole-application (?:acceleration|evidence|performance)",
    r"whole-app (?:speedup|acceleration|claim)",
    r"v2\.0 release readiness",
    r"v2\.0 is ready",
)

NEGATIVE_CONTEXT = (
    "not ",
    "not a ",
    "not part",
    "does not",
    "do not",
    "without",
    "blocked",
    "hard gate",
    "hard gates",
    "remains blocked",
    "release boundary",
    "blocked wording",
    "unsupported",
    "before v2.0 release",
    "needs external review",
    "must stay inside",
    "must name the exact",
    "do not read",
)


def _public_files(root: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for pattern in PUBLIC_PATTERNS:
        files.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(files))


def _line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _snippet(text: str, start: int, end: int, window: int = 180) -> str:
    return text[max(0, start - window) : min(len(text), end + window)].replace("\n", " ")


def scan(root: pathlib.Path) -> dict[str, object]:
    findings = []
    accepted = []
    regex = re.compile("|".join(f"({pattern})" for pattern in CLAIM_PATTERNS), re.IGNORECASE)
    for path in _public_files(root):
        text = path.read_text(encoding="utf-8")
        for match in regex.finditer(text):
            snippet = _snippet(text, match.start(), match.end())
            normalized = snippet.lower()
            record = {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "line": _line_for(text, match.start()),
                "phrase": match.group(0),
                "snippet": snippet.strip(),
            }
            if any(token in normalized for token in NEGATIVE_CONTEXT):
                accepted.append(record)
            else:
                findings.append(record)
    release_authorized = (
        (root / "VERSION").exists()
        and (root / "VERSION").read_text(encoding="utf-8").strip() == "v2.0"
        and (root / "docs/reports/goal2322_final_v2_0_release_cleanup_3ai_consensus_2026-05-18.md").exists()
        and (root / "docs/reports/goal2323_v2_0_release_action_2026-05-18.md").exists()
    )
    return {
        "goal": "Goal1906",
        "status": "pass" if not findings else "fail",
        "public_files_scanned": [str(path.relative_to(root)).replace("\\", "/") for path in _public_files(root)],
        "accepted_negative_occurrences": accepted,
        "findings": findings,
        "claim_boundary": {
            "v2_0_release_authorized": release_authorized,
            "package_install_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "arbitrary_partner_program_acceleration_authorized": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan public docs for premature v2.0 claims.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="docs/reports/goal1906_public_v2_claim_boundary_scan.json")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = pathlib.Path(args.root)
    payload = scan(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
