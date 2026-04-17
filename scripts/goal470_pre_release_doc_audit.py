#!/usr/bin/env python3
"""Mechanical v0.7 pre-release doc and audit checks for Goal 470."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

RELEASE_DOCS = (
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/features/README.md"),
    Path("docs/features/db_workloads/README.md"),
    Path("docs/quick_tutorial.md"),
    Path("docs/tutorials/db_workloads.md"),
    Path("docs/release_facing_examples.md"),
    Path("docs/release_reports/v0_7/release_statement.md"),
    Path("docs/release_reports/v0_7/support_matrix.md"),
    Path("docs/release_reports/v0_7/audit_report.md"),
    Path("docs/release_reports/v0_7/tag_preparation.md"),
    Path("docs/history/goals/v0_7_goal_sequence_2026-04-15.md"),
)

REQUIRED_ARTIFACTS = (
    Path("docs/reports/goal470_local_full_unittest_discovery_after_fix_2026-04-16.txt"),
    Path("docs/reports/goal470_linux_focused_pre_release_test_2026-04-16.txt"),
    Path("docs/reports/goal470_external_review_2026-04-16.md"),
    Path("docs/reports/goal470_claude_test_review_audit_2026-04-16.md"),
    Path("docs/reports/goal469_external_review_2026-04-16.md"),
    Path("docs/reports/goal469_v0_7_db_attack_report_gap_closure_2026-04-16.md"),
    Path("docs/reports/test_v07_db_attack_report_2026-04-16.md"),
    Path("tests/test_v07_db_attack.py"),
    Path("tests/goal469_v0_7_db_attack_gap_closure_test.py"),
)

REQUIRED_RELEASE_CLAIMS = {
    Path("docs/release_reports/v0_7/release_statement.md"): (
        "Goal 469",
        "Goal 470",
        "not release authorization",
        "not a DBMS",
    ),
    Path("docs/release_reports/v0_7/support_matrix.md"): (
        "Goal 470",
        "941",
        "155",
        "PostgreSQL 16.13",
        "Vulkan runtime probe",
    ),
    Path("docs/release_reports/v0_7/audit_report.md"): (
        "through Goal 470",
        "external DB attack report",
        "941",
        "155",
        "does not authorize tagging",
    ),
    Path("docs/release_reports/v0_7/tag_preparation.md"): (
        "Do not tag",
        "Goal 470",
        "941 tests",
        "155 tests",
    ),
    Path("docs/history/goals/v0_7_goal_sequence_2026-04-15.md"): (
        "Goal 469",
        "Goal 470",
        "pre-release full test",
    ),
}

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def _is_external_link(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def _strip_anchor(target: str) -> str:
    return target.split("#", 1)[0]


def _resolve_link(source: Path, target: str) -> Path | None:
    target = unquote(_strip_anchor(target).strip())
    if not target or _is_external_link(target):
        return None
    if target.startswith("/"):
        return Path(target)
    return (ROOT / source.parent / target).resolve()


def _check_links(path: Path) -> list[dict[str, str]]:
    text = (ROOT / path).read_text(encoding="utf-8")
    broken = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        resolved = _resolve_link(path, target)
        if resolved is None:
            continue
        if not resolved.exists():
            broken.append({"source": str(path), "target": target, "resolved": str(resolved)})
    return broken


def build_report() -> dict[str, object]:
    release_docs = [{"path": str(path), "exists": (ROOT / path).exists()} for path in RELEASE_DOCS]
    artifacts = [{"path": str(path), "exists": (ROOT / path).exists()} for path in REQUIRED_ARTIFACTS]
    missing_release_docs = [row["path"] for row in release_docs if not row["exists"]]
    missing_artifacts = [row["path"] for row in artifacts if not row["exists"]]

    claim_gaps = []
    for path, needles in REQUIRED_RELEASE_CLAIMS.items():
        text = (ROOT / path).read_text(encoding="utf-8") if (ROOT / path).exists() else ""
        for needle in needles:
            if needle not in text:
                claim_gaps.append({"path": str(path), "missing": needle})

    broken_links = []
    for path in RELEASE_DOCS:
        if (ROOT / path).exists() and path.suffix == ".md":
            broken_links.extend(_check_links(path))

    local_log = (ROOT / "docs/reports/goal470_local_full_unittest_discovery_after_fix_2026-04-16.txt").read_text(
        encoding="utf-8"
    )
    linux_log = (ROOT / "docs/reports/goal470_linux_focused_pre_release_test_2026-04-16.txt").read_text(
        encoding="utf-8"
    )
    transcript_checks = {
        "local_941_ok": "Ran 941 tests" in local_log and "OK (skipped=105)" in local_log,
        "linux_155_ok": "Ran 155 tests" in linux_log and "\nOK\n" in linux_log,
        "linux_postgresql_ready": "psql (PostgreSQL) 16.13" in linux_log and "accepting connections" in linux_log,
        "linux_backends_ready": all(token in linux_log for token in ("\"embree\": [4, 3, 0]", "\"optix\": [9, 0, 0]", "\"vulkan\": [0, 1, 0]")),
    }

    valid = (
        not missing_release_docs
        and not missing_artifacts
        and not claim_gaps
        and not broken_links
        and all(transcript_checks.values())
    )
    return {
        "goal": 470,
        "repo_root": str(ROOT),
        "release_docs": release_docs,
        "required_artifacts": artifacts,
        "missing_release_docs": missing_release_docs,
        "missing_artifacts": missing_artifacts,
        "claim_gaps": claim_gaps,
        "broken_release_doc_links": broken_links,
        "transcript_checks": transcript_checks,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
    }


def main() -> int:
    report = build_report()
    out = ROOT / "docs/reports/goal470_pre_release_doc_audit_2026-04-16.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"valid": report["valid"], "output": str(out)}, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
