#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FILES = (
    "README.md",
    "docs/README.md",
    "docs/current_v3_status.md",
    "docs/public_documentation_map.md",
    "docs/learn/README.md",
    "docs/learn/performance_wording.md",
    "docs/learn/source_tree_doctor.md",
    "tutorials/README.md",
    "tutorials/current/README.md",
    "tutorials/current/01_first_run.md",
    "tutorials/current/02_hello_world.md",
    "tutorials/current/03_backend_choice.md",
    "tutorials/current/04_prepared_runtime.md",
    "tutorials/current/05_measurement_boundaries.md",
    "examples/README.md",
    "examples/current/README.md",
)

REQUIRED_STRINGS = (
    "RTDL V3",
    "current V3",
    "scripts/rtdl_source_tree_doctor.py --run-smoke",
    "examples/current/getting_started/rtdl_hello_world.py",
    "Performance Wording Guide",
    "Use Exact Wording",
)

POSITIVE_OVERCLAIM_PATTERNS = (
    re.compile(r"\bv3(?:\.0)?\s+is\s+(?:now\s+)?released\b", re.IGNORECASE),
    re.compile(r"\bv3(?:\.0)?\s+is\s+(?:now\s+)?complete\b", re.IGNORECASE),
    re.compile(r"\bv3\b.*\bbroadly\s+beats\s+v2", re.IGNORECASE),
    re.compile(r"\brtdl\s+accelerates\s+every\s+benchmark\s+app", re.IGNORECASE),
    re.compile(r"\b(?:public-)?release[- ]ready\b", re.IGNORECASE),
    re.compile(r"\brelease[-_ ]candidate\b", re.IGNORECASE),
)

POST_V3_SCOPE_PATTERNS = (
    re.compile(r"\bC ABI\b", re.IGNORECASE),
    re.compile(r"\bembedding\b", re.IGNORECASE),
    re.compile(r"\bDLPack\b", re.IGNORECASE),
    re.compile(r"\btrue[- ]zero[- ]copy\b", re.IGNORECASE),
)

UNAUTHORIZED_TRUE_FLAG_PATTERNS = (
    ("release_authorized_true", re.compile(r"(?<![A-Za-z0-9_])release_authorized`?\s*[:=]\s*`?true`?", re.IGNORECASE)),
    (
        "public_speedup_claim_authorized_true",
        re.compile(r"(?<!row_scoped_)(?<![A-Za-z0-9_])public_speedup_claim_authorized`?\s*[:=]\s*`?true`?", re.IGNORECASE),
    ),
    (
        "broad_v3_faster_than_v2_claim_authorized_true",
        re.compile(r"(?<![A-Za-z0-9_])broad_v3_faster_than_v2_claim_authorized`?\s*[:=]\s*`?true`?", re.IGNORECASE),
    ),
)

NEGATION_MARKERS = (
    "do not",
    "not ",
    "not-",
    "no ",
    "blocked",
    "non-claim",
    "not a",
    "not an",
    "not currently",
    "does not authorize",
    "outside v3",
)

POSITIVE_OVERCLAIM_ALLOWED_CONTEXT = (
    "do not claim",
    "not authorized",
    "blocked",
)


def current_public_surface_files() -> list[str]:
    """Return the current user-facing files only; history is intentionally excluded."""
    files = list(DEFAULT_FILES)
    for folder in (ROOT / "docs" / "learn", ROOT / "tutorials" / "current"):
        for path in sorted(folder.glob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            if rel not in files:
                files.append(rel)
    return files


def line_is_negated(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in NEGATION_MARKERS)


def context_allows_positive_overclaim(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in POSITIVE_OVERCLAIM_ALLOWED_CONTEXT)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def scan_file(path: Path) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not path.exists():
        return [{"file": _rel(path), "line": None, "pattern": "missing-file", "text": ""}]

    lines = path.read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, start=1):
        context = "\n".join(lines[max(0, lineno - 10) : min(len(lines), lineno + 2)])
        for pattern in POSITIVE_OVERCLAIM_PATTERNS:
            if pattern.search(line) and not line_is_negated(line) and not context_allows_positive_overclaim(context):
                violations.append(
                    {"file": _rel(path), "line": lineno, "pattern": pattern.pattern, "text": line.strip()}
                )
        for pattern in POST_V3_SCOPE_PATTERNS:
            if pattern.search(line) and not line_is_negated(context):
                violations.append(
                    {"file": _rel(path), "line": lineno, "pattern": "post-v3-scope:" + pattern.pattern, "text": line.strip()}
                )
        for name, pattern in UNAUTHORIZED_TRUE_FLAG_PATTERNS:
            if pattern.search(line) and not line_is_negated(line):
                violations.append({"file": _rel(path), "line": lineno, "pattern": name, "text": line.strip()})
    return violations


def _normalize_rel(path: str) -> str:
    return str(Path(path.replace("\\", "/"))).replace("/", "\\")


def build_payload(required_scanned: tuple[str, ...] = ()) -> dict[str, Any]:
    files = [ROOT / rel for rel in current_public_surface_files()]
    violations: list[dict[str, Any]] = []
    for path in files:
        violations.extend(scan_file(path))

    joined = "\n".join(path.read_text(encoding="utf-8") for path in files if path.exists())
    missing_required_strings = [needle for needle in REQUIRED_STRINGS if needle not in joined]
    scanned_files = [str(path.relative_to(ROOT)) for path in files]
    scanned_normalized = {_normalize_rel(path) for path in scanned_files}
    missing_required_scanned_files = [
        required for required in required_scanned if _normalize_rel(required) not in scanned_normalized
    ]
    passed = not violations and not missing_required_strings and not missing_required_scanned_files

    return {
        "tool": "v3_release_wording_gate",
        "gate_level": "v3_0_public_release_wording_gate",
        "final_public_surface_gate": passed,
        "final_public_surface_scope": "clean_v3_0_user_release_surface",
        "status": "pass" if passed else "fail",
        "scanned_files": scanned_files,
        "required_scanned_files": list(required_scanned),
        "missing_required_scanned_files": missing_required_scanned_files,
        "violations": violations,
        "missing_required_strings": missing_required_strings,
        "expected_m7_row_ids": [],
        "missing_expected_m7_row_ids": [],
        "claim_flags": {
            "release_authorized": True,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "package_install_claim_authorized": False,
            "multi_gpu_performance_portability_claim_authorized": False,
            "secondary_rt_performance_confirmation_authorized": False,
        },
        "release_authorization_note": (
            "This is the V3.0.0 public release wording gate. The release surface is "
            "authorized when public docs stay clean and use scoped performance wording."
        ),
        "release_authorized": True,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan current V3 public docs for release wording overclaims.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument(
        "--require-scanned",
        action="append",
        default=[],
        help="Relative file path that must appear in the scanned file set.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(tuple(args.require_scanned))
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
