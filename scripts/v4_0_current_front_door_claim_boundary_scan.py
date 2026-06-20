#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Iterable


PUBLIC_PATTERNS = (
    "README.md",
    "docs/README.md",
    "docs/release_reports/README.md",
    "docs/release_reports/v4_0_0/*.md",
    "docs/learn/current_claim_boundaries.md",
    "src/v4/README.md",
    "docs/engineering/README.md",
    "docs/engineering/rtdl_v4_0_m1_experimental_status_2026-06-19.md",
    "docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md",
    "docs/reviews/codex_v4_m8_external_review_request_2026-06-19.md",
    "docs/reviews/codex_v4_m8_internal_2ai_critical_review_2026-06-19.md",
    "docs/reviews/codex_v4_m8_external_ai_access_attempt_2026-06-19.md",
    "docs/reviews/claude_v4_0_m8_external_review_2026-06-19.md",
    "tutorials/README.md",
    "tutorials/v4_0/*.md",
    "examples/README.md",
    "examples/v4_0/**/*.md",
)

CLAIM_PATTERNS = (
    r"\bstable V4 SDK\b",
    r"\bpackage[- ]install\b",
    r"\bPyPI\b",
    r"\bwheel support\b",
    r"\bgenerated[- ]bindings?\b",
    r"\bpublic multi-language C ABI release\b",
    r"\btrue[- ]zero[- ]copy\b",
    r"\bend-to-end zero[- ]copy\b",
    r"\bzero[- ]copy\b",
    r"\bno copies\b",
    r"\bno staging\b",
    r"\bno H2D copies\b",
    r"\basync\b",
    r"\bnonblocking\b",
    r"\bcross-stream event wait support\b",
    r"\bRT-core speedup\b",
    r"\bRTX speedup\b",
    r"\bRTDL is faster\b",
    r"\bPyTorch route support\b",
    r"\bfull DLPack support\b",
)

NEGATIVE_CONTEXT = (
    "not ",
    "not a ",
    "not the ",
    "no ",
    "do not",
    "does not",
    "without",
    "blocked",
    "forbidden",
    "claim boundary",
    "claim_boundaries",
    "not claimed",
    "not authorize",
    "not authorized",
    "promise",
    "target inputs without",
    "until ",
    "unless ",
    "after ",
    "before ",
    "must not",
    "keeps ",
    "remains ",
    "reserved ",
    "v4.0 scope",
    "v4 scope",
    "remain v4.0 work",
    "remain v4 work",
    "excluded",
    "excludes",
    "deferred",
    "deferrals",
    "must not claim",
    "must not be described",
    "what this release must not claim",
    "not claim",
    "does not claim",
    "not v3.0 release claims",
    "not v3.0.2 release criteria",
    "not released",
    "not part of",
    "non-claims",
    "public wording boundaries",
    "no observed host staging",
    "overclaim",
    "too broad",
    "review request",
    "external review",
)

NEGATIVE_SECTION_HEADINGS = (
    "blocked wording",
    "v4 deferrals",
    "non-claims",
    "what this release must not claim",
    "release boundary",
    "public wording boundaries",
    "current claim flags",
    "review request",
    "forbidden wording",
    "p0 blockers",
    "p1 risks",
    "p2 polish issues",
)


def _public_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in PUBLIC_PATTERNS:
        files.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(files))


def _line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _snippet(text: str, start: int, end: int, window: int = 180) -> str:
    return text[max(0, start - window) : min(len(text), end + window)].replace("\n", " ").strip()


def _nearest_heading(text: str, offset: int) -> str:
    prefix = text[:offset].splitlines()
    for line in reversed(prefix):
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip().lower()
    return ""


def _is_negative_context(text: str, start: int, end: int) -> bool:
    snippet = _snippet(text, start, end, window=420)
    normalized = snippet.lower()
    heading = _nearest_heading(text, start)
    return any(token in normalized for token in NEGATIVE_CONTEXT) or any(
        token in heading for token in NEGATIVE_SECTION_HEADINGS
    )


def _front_door_identity(root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    docs_index = (root / "docs" / "README.md").read_text(encoding="utf-8")
    release_index = (root / "docs" / "release_reports" / "README.md").read_text(encoding="utf-8")

    identity = {
        "current_version": version,
        "pyproject_version_is_4_0_0": 'version = "4.0.0"' in pyproject,
        "root_readme_claims_current_v4_0_0": "current V4.0.0 source-tree RTDL surface" in readme,
        "docs_index_claims_current_v4_0_0": "RTDL V4.0.0 is the active source-tree" in docs_index,
        "release_index_claims_v4_0_0_current": "RTDL V4.0.0 Release Package" in release_index,
        "v3_0_2_release_package_exists": (root / "docs" / "release_reports" / "v3_0_2").is_dir(),
        "v4_0_0_release_package_exists": (root / "docs" / "release_reports" / "v4_0_0").is_dir(),
    }
    errors: list[dict[str, object]] = []
    expected_truths = {
        "current_version": version == "v4.0.0",
        "pyproject_version_is_4_0_0": bool(identity["pyproject_version_is_4_0_0"]),
        "root_readme_claims_current_v4_0_0": bool(identity["root_readme_claims_current_v4_0_0"]),
        "docs_index_claims_current_v4_0_0": bool(identity["docs_index_claims_current_v4_0_0"]),
        "release_index_claims_v4_0_0_current": bool(identity["release_index_claims_v4_0_0_current"]),
        "v3_0_2_release_package_exists": bool(identity["v3_0_2_release_package_exists"]),
        "v4_0_0_release_package_exists": bool(identity["v4_0_0_release_package_exists"]),
    }
    for key, ok in expected_truths.items():
        if not ok:
            errors.append(
                {
                    "kind": "front_door_identity",
                    "check": key,
                    "message": "current front door must resolve to the bounded V4.0.0 source-tree release",
                }
            )
    return identity, errors


def scan(root: Path) -> dict[str, object]:
    root = root.resolve()
    findings: list[dict[str, object]] = []
    accepted_negative_occurrences: list[dict[str, object]] = []
    regex = re.compile("|".join(f"({pattern})" for pattern in CLAIM_PATTERNS), re.IGNORECASE)
    for path in _public_files(root):
        text = path.read_text(encoding="utf-8")
        for match in regex.finditer(text):
            snippet = _snippet(text, match.start(), match.end())
            record = {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "line": _line_for(text, match.start()),
                "phrase": match.group(0),
                "snippet": snippet,
            }
            if _is_negative_context(text, match.start(), match.end()):
                accepted_negative_occurrences.append(record)
            else:
                findings.append(record)

    front_door, identity_errors = _front_door_identity(root)
    findings.extend(identity_errors)
    return {
        "report_id": "v4_0_current_front_door_claim_boundary_scan_2026-06-19",
        "status": "pass" if not findings else "fail",
        "public_files_scanned": [str(path.relative_to(root)).replace("\\", "/") for path in _public_files(root)],
        "front_door": front_door,
        "accepted_negative_occurrences": accepted_negative_occurrences,
        "findings": findings,
        "claim_boundaries": {
            "v4_current_release_claim_authorized": True,
            "v4_release_package_claim_authorized": True,
            "fixed_radius_m1_python_gpu_operator_claim_authorized": True,
            "stable_v4_sdk_claim_authorized": False,
            "package_install_claim_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "cross_stream_event_wait_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "pytorch_route_claim_authorized": False,
            "full_dlpack_route_claim_authorized": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan current front-door docs for premature V4 claims.")
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="docs/reports/v4_0_current_front_door_claim_boundary_scan_2026-06-19.json",
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
