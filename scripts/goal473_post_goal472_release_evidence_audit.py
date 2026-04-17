#!/usr/bin/env python3
"""Mechanical release-evidence audit after Goal 472."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

RELEASE_DOCS = (
    Path("docs/release_reports/v0_7/release_statement.md"),
    Path("docs/release_reports/v0_7/support_matrix.md"),
    Path("docs/release_reports/v0_7/audit_report.md"),
    Path("docs/release_reports/v0_7/tag_preparation.md"),
    Path("docs/history/goals/v0_7_goal_sequence_2026-04-15.md"),
)

REQUIRED_ARTIFACTS = (
    Path("docs/goal_471_v0_7_external_v0_6_1_expert_attack_suite_intake.md"),
    Path("docs/goal_472_v0_7_release_reports_refresh_after_goal471.md"),
    Path("docs/handoff/GOAL471_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md"),
    Path("docs/handoff/GOAL472_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-16.md"),
    Path("docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md"),
    Path("docs/reports/goal471_v0_7_external_v0_6_1_expert_attack_suite_intake_2026-04-16.md"),
    Path("docs/reports/goal471_external_review_2026-04-16.md"),
    Path("docs/reports/goal472_v0_7_release_reports_refresh_after_goal471_2026-04-16.md"),
    Path("docs/reports/goal472_external_review_2026-04-16.md"),
    Path("history/ad_hoc_reviews/2026-04-16-codex-consensus-goal471-v0_7-external-v0_6_1-expert-attack-suite-intake.md"),
    Path("history/ad_hoc_reviews/2026-04-16-codex-consensus-goal472-v0_7-release-reports-refresh-after-goal471.md"),
)

REQUIRED_CLAIMS = {
    Path("docs/release_reports/v0_7/release_statement.md"): (
        "Goal 471",
        "v0.6.1 Expert Attack Suite",
        "not a v0.7 DB/PostgreSQL release gate",
        "not v0.7 DB release authorization",
    ),
    Path("docs/release_reports/v0_7/support_matrix.md"): (
        "Goal 471",
        "graph/geometry stress evidence only",
        "does not authorize staging, tagging, merging, or release",
    ),
    Path("docs/release_reports/v0_7/audit_report.md"): (
        "seventh branch pass",
        "Certified for deployment",
        "not used as a v0.7 DB/PostgreSQL gate or release authorization",
    ),
    Path("docs/release_reports/v0_7/tag_preparation.md"): (
        "Do not tag",
        "Goal 471",
        "not v0.7 release authorization",
    ),
    Path("docs/history/goals/v0_7_goal_sequence_2026-04-15.md"): (
        "Goal 471",
        "Goal 472",
        "no-stage/no-tag/no-merge/no-release hold",
    ),
    Path("docs/reports/goal439_external_tester_report_intake_ledger_2026-04-16.md"): (
        "T439-010",
        "T439-011",
        "T439-012",
        "Goal 471",
    ),
    Path("docs/reports/goal471_v0_7_external_v0_6_1_expert_attack_suite_intake_2026-04-16.md"): (
        "Status: Accepted with 2-AI consensus",
        "DO NOT USE",
        "standalone authorization",
    ),
    Path("docs/reports/goal472_v0_7_release_reports_refresh_after_goal471_2026-04-16.md"): (
        "Status: Accepted with 2-AI consensus",
        "no-stage/no-tag/no-merge/no-release hold",
    ),
    Path("docs/reports/goal471_external_review_2026-04-16.md"): (
        "Verdict: **ACCEPT**",
    ),
    Path("docs/reports/goal472_external_review_2026-04-16.md"): (
        "Verdict: **ACCEPT**",
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
    for path, needles in REQUIRED_CLAIMS.items():
        text = (ROOT / path).read_text(encoding="utf-8") if (ROOT / path).exists() else ""
        for needle in needles:
            if needle not in text:
                claim_gaps.append({"path": str(path), "missing": needle})

    broken_links = []
    for path in RELEASE_DOCS:
        if (ROOT / path).exists():
            broken_links.extend(_check_links(path))

    preserved_report = ROOT / "docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md"
    preserved_text = preserved_report.read_text(encoding="utf-8") if preserved_report.exists() else ""
    source_report_checks = {
        "has_bfs_galaxy": "BFS Galaxy Attack" in preserved_text and "2.4065 seconds" in preserved_text,
        "has_triangle_clique": "Triangle Clique Attack" in preserved_text and "105.7947 seconds" in preserved_text,
        "has_pip_cloud": "PIP Cloud Attack" in preserved_text and "4.0971 seconds" in preserved_text,
        "has_lsi_cross": "LSI Cross Attack" in preserved_text and "2.1265 seconds" in preserved_text,
        "has_pressure_test": "Resource Pressure Test" in preserved_text and "0.0933 seconds" in preserved_text,
        "has_parity": "Parity Attack" in preserved_text and "100% bit-exact match" in preserved_text,
    }

    valid = (
        not missing_release_docs
        and not missing_artifacts
        and not claim_gaps
        and not broken_links
        and all(source_report_checks.values())
    )

    return {
        "goal": 473,
        "repo_root": str(ROOT),
        "release_docs": release_docs,
        "required_artifacts": artifacts,
        "missing_release_docs": missing_release_docs,
        "missing_artifacts": missing_artifacts,
        "claim_gaps": claim_gaps,
        "broken_release_doc_links": broken_links,
        "source_report_checks": source_report_checks,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
    }


def main() -> int:
    report = build_report()
    out = ROOT / "docs/reports/goal473_post_goal472_release_evidence_audit_2026-04-16.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"valid": report["valid"], "output": str(out)}, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
