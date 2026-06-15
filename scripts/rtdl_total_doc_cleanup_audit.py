from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = "v2.14"

DOC_GLOBS = ("*.md", "*.rst", "*.txt")
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal4391_total_doc_cleanup_audit_2026-06-15.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal4391_total_doc_cleanup_audit_2026-06-15.md"

HISTORICAL_PREFIXES = (
    "history/",
    "docs/history/",
    "docs/reports/",
    "docs/reviews/",
    "docs/handoff/",
    "docs/patches/",
    "docs/engineering/handoffs/",
    "docs/research/archive/",
    "docs/release_reports/v0_",
    "docs/release_reports/v1_",
    "docs/release_reports/v2_0",
    "docs/release_reports/v2_1",
    "docs/release_reports/v2_2",
    "docs/release_reports/v2_3",
    "docs/release_reports/v2_4",
    "docs/release_reports/v2_5",
    "docs/release_reports/v2_6",
    "docs/release_reports/v2_7",
    "docs/release_reports/v2_8",
    "docs/release_reports/v2_9",
    "docs/release_reports/v2_10",
    "docs/release_reports/v2_11",
    "docs/release_reports/v2_12",
    "docs/release_reports/v2_13",
)

CURRENT_PREFIXES = (
    "README.md",
    "docs/",
    "tutorials/",
    "examples/README.md",
    "examples/current/",
)

EXCLUDED_DIR_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
    ".venv",
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+(?:\s+\"[^\"]*\")?)\)")
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+(?:\s+\"[^\"]*\")?)\)")
HTML_LINK_RE = re.compile(r"<a\s+[^>]*href=[\"']([^\"']+)[\"']", re.IGNORECASE)

STALE_CURRENT_RE = re.compile(
    r"\b("
    r"current v2\.13|"
    r"v2\.13 is the current|"
    r"active v2\.13|"
    r"current source-tree release marker.*v2\.13|"
    r"current v2\.13 release boundary|"
    r"current v2\.13 source-tree|"
    r"current learner-facing milestone is the v2\.13|"
    r"RTDL v2\.13 is the current"
    r")\b",
    re.IGNORECASE,
)

DRAFT_RELEASE_RE = re.compile(
    r"\b("
    r"Draft Release Package|"
    r"Draft Publication|"
    r"publication candidate|"
    r"not published|"
    r"not released|"
    r"pending maintainer authorization|"
    r"tagging still require|"
    r"still require maintainer authorization"
    r")\b",
    re.IGNORECASE,
)

CURRENT_DOC_ALLOW_DRAFT_PHRASE = (
    "docs/release_reports/v0_4_preview/",
)

CLEANUP_ACTIONS = {
    "README.md": "fixed: current source-tree surface, release package, and mixed-row wording updated from v2.13 to v2.14.",
    "docs/versioning.md": "fixed: current version marker updated from v2.13 to v2.14.",
    "docs/release_reports/v2_13/README.md": "fixed: marked v2.13 as a previous release superseded by v2.14.",
    "docs/release_reports/v2_13/publication.md": "fixed: marked v2.13 publication note as previous-release evidence.",
    "docs/release_reports/v2_13/release_publication.json": "fixed: release statement now says v2.13 is previous and records superseded_by=v2.14.",
    "docs/reports/goal4386_v2_14_final_closeout_2026-06-15.md": "fixed: post-publication status now records that v2.14 was authorized, tagged, and pushed.",
    "docs/audit/process/current_milestone_qa.md": "fixed: archived QA links now resolve to their actual release-report, report, tutorial, and visual-demo paths.",
    "docs/engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md": "fixed: historical foundations link now points to docs/research/archive/future.",
    "scripts/rtdl_total_doc_cleanup_audit.py": "added: total documentation audit tooling with per-document reporting.",
}


@dataclass(frozen=True)
class DocIssue:
    code: str
    line: int | None
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {"code": self.code, "line": self.line, "detail": self.detail}


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_generated_or_binary_text(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    return bool(parts & EXCLUDED_DIR_PARTS)


def iter_doc_files() -> list[Path]:
    files: list[Path] = []
    for pattern in DOC_GLOBS:
        files.extend(ROOT.rglob(pattern))
    return sorted(
        path
        for path in files
        if path.is_file()
        and not is_generated_or_binary_text(path)
        and not relpath(path).startswith("docs/reports/goal2332_rayjoin_same_contract_pod/debug_")
    )


def classify(path: Path) -> str:
    rp = relpath(path)
    if any(rp.startswith(prefix) for prefix in HISTORICAL_PREFIXES):
        return "historical_or_evidence"
    if any(rp == prefix or rp.startswith(prefix) for prefix in CURRENT_PREFIXES):
        return "current_facing"
    return "other_doc"


def strip_link_title(raw: str) -> str:
    raw = raw.strip()
    if " " in raw and not raw.startswith("<"):
        candidate, _, _title = raw.partition(" ")
        if candidate:
            return candidate
    return raw.strip("<>")


def is_external(target: str) -> bool:
    lower = target.lower()
    return lower.startswith(("http://", "https://", "mailto:", "tel:", "ftp:", "app://", "file://"))


def target_without_fragment(target: str) -> str:
    return target.split("#", 1)[0].split("?", 1)[0]


def resolve_internal_link(source: Path, target: str) -> Path | None:
    clean = unquote(strip_link_title(target))
    if not clean or clean.startswith("#") or is_external(clean):
        return None
    clean = target_without_fragment(clean)
    if not clean:
        return None
    if clean.startswith("/"):
        clean = clean.lstrip("/")
        return ROOT / clean
    return source.parent / clean


def extract_links(text: str) -> list[tuple[int, str]]:
    links: list[tuple[int, str]] = []
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for regex in (MARKDOWN_LINK_RE, IMAGE_LINK_RE, HTML_LINK_RE):
            for match in regex.finditer(line):
                links.append((lineno, match.group(1)))
    return links


def audit_doc(path: Path) -> dict[str, object]:
    rp = relpath(path)
    classification = classify(path)
    issues: list[DocIssue] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
        issues.append(DocIssue("decode_replacement", None, "File required UTF-8 replacement while reading."))

    for lineno, line in enumerate(text.splitlines(), start=1):
        if classification == "current_facing" and STALE_CURRENT_RE.search(line):
            issues.append(DocIssue("stale_current_version", lineno, line.strip()))
        if (
            classification == "current_facing"
            and not any(rp.startswith(prefix) for prefix in CURRENT_DOC_ALLOW_DRAFT_PHRASE)
            and DRAFT_RELEASE_RE.search(line)
        ):
            issues.append(DocIssue("draft_or_pending_wording_in_current_doc", lineno, line.strip()))

    internal_links_checked = 0
    external_links_seen = 0
    for lineno, target in extract_links(text):
        if is_external(strip_link_title(target)):
            external_links_seen += 1
            continue
        resolved = resolve_internal_link(path, target)
        if resolved is None:
            continue
        internal_links_checked += 1
        if not resolved.exists():
            issues.append(
                DocIssue(
                    "dead_internal_link",
                    lineno,
                    f"{strip_link_title(target)} -> {relpath(resolved) if resolved.is_absolute() and ROOT in resolved.parents else resolved}",
                )
            )

    historical_mentions = len(re.findall(r"\bv(?:0|1|2)_[0-9]+|\bv(?:0|1|2)\.[0-9]+", text))
    status_line = ""
    for line in text.splitlines()[:8]:
        if line.lower().startswith("status:"):
            status_line = line.strip()
            break

    action = CLEANUP_ACTIONS.get(
        rp,
        "verified_current_clean" if classification == "current_facing" else "no_change_needed",
    )
    if issues:
        if classification == "historical_or_evidence":
            action = "preserved_as_historical_or_evidence; old links/status belong to frozen audit context unless revived"
        else:
            action = "needs_manual_review_or_fixed_by_cleanup"
    elif classification == "historical_or_evidence":
        action = CLEANUP_ACTIONS.get(rp, "preserved_as_historical_or_evidence")

    return {
        "path": rp,
        "classification": classification,
        "status_line": status_line,
        "line_count": len(text.splitlines()),
        "internal_links_checked": internal_links_checked,
        "external_links_seen_unchecked": external_links_seen,
        "historical_version_mentions": historical_mentions,
        "issue_count": len(issues),
        "issues": [issue.as_dict() for issue in issues],
        "action": action,
    }


def render_markdown(payload: dict[str, object]) -> str:
    docs = payload["documents"]
    assert isinstance(docs, list)
    summary = payload["summary"]
    assert isinstance(summary, dict)

    lines = [
        "# Goal4391 Total Documentation Cleanup Audit",
        "",
        "Date: 2026-06-15",
        "",
        "## Scope",
        "",
        "This audit scans repository Markdown/RST/TXT documentation, classifies each file as current-facing, historical/evidence, or other, checks internal links, and flags stale current-version or draft/pending release wording where it appears in current-facing docs.",
        "",
        "Historical evidence files are allowed to mention old versions and old not-released states when they are under history, reports, reviews, handoff, patches, or old release-report paths. They are preserved rather than rewritten unless they leak into the current reader path.",
        "",
        "## Summary",
        "",
        f"- Documents scanned: `{summary['documents_scanned']}`",
        f"- Current-facing documents: `{summary['current_facing']}`",
        f"- Historical/evidence documents: `{summary['historical_or_evidence']}`",
        f"- Other documents: `{summary['other_doc']}`",
        f"- Documents with issues: `{summary['documents_with_issues']}`",
        f"- Current-facing documents with issues: `{summary['current_documents_with_issues']}`",
        f"- Dead internal links: `{summary['dead_internal_links']}`",
        f"- Current-facing dead internal links: `{summary['current_dead_internal_links']}`",
        f"- Historical/evidence dead internal links preserved in archive context: `{summary['historical_dead_internal_links']}`",
        f"- Stale current-version wording hits: `{summary['stale_current_version_hits']}`",
        f"- Draft/pending wording hits in current docs: `{summary['draft_or_pending_hits']}`",
        "",
        "Current-facing gate: pass when current-facing documents with issues, current-facing dead internal links, stale current-version wording hits, and draft/pending wording hits are all zero.",
        "",
        "Historical/evidence policy: old reports, reviews, handoffs, patches, and history snapshots are not rewritten to pretend they were authored today. Old version mentions and frozen-context links are reported per document and kept out of the current reader path.",
        "",
        "## Per-Document Findings",
        "",
        "| Document | Class | Links | Issues | Finding | Action |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for doc in docs:
        assert isinstance(doc, dict)
        issues = doc["issues"]
        assert isinstance(issues, list)
        action = doc["action"]
        finding = "clean"
        if issues:
            issue_bits = []
            for issue in issues[:3]:
                assert isinstance(issue, dict)
                loc = f":{issue['line']}" if issue["line"] else ""
                issue_bits.append(f"{issue['code']}{loc}")
            if len(issues) > 3:
                issue_bits.append(f"+{len(issues) - 3} more")
            finding = "; ".join(issue_bits)
        lines.append(
            f"| `{doc['path']}` | {doc['classification']} | {doc['internal_links_checked']} | {doc['issue_count']} | {finding} | {action} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_payload() -> dict[str, object]:
    docs = [audit_doc(path) for path in iter_doc_files()]
    summary = {
        "documents_scanned": len(docs),
        "current_facing": sum(1 for doc in docs if doc["classification"] == "current_facing"),
        "historical_or_evidence": sum(1 for doc in docs if doc["classification"] == "historical_or_evidence"),
        "other_doc": sum(1 for doc in docs if doc["classification"] == "other_doc"),
        "documents_with_issues": sum(1 for doc in docs if doc["issue_count"]),
        "current_documents_with_issues": sum(
            1 for doc in docs if doc["classification"] == "current_facing" and doc["issue_count"]
        ),
        "dead_internal_links": sum(
            1
            for doc in docs
            for issue in doc["issues"]
            if issue["code"] == "dead_internal_link"
        ),
        "current_dead_internal_links": sum(
            1
            for doc in docs
            if doc["classification"] == "current_facing"
            for issue in doc["issues"]
            if issue["code"] == "dead_internal_link"
        ),
        "historical_dead_internal_links": sum(
            1
            for doc in docs
            if doc["classification"] == "historical_or_evidence"
            for issue in doc["issues"]
            if issue["code"] == "dead_internal_link"
        ),
        "stale_current_version_hits": sum(
            1
            for doc in docs
            for issue in doc["issues"]
            if issue["code"] == "stale_current_version"
        ),
        "draft_or_pending_hits": sum(
            1
            for doc in docs
            for issue in doc["issues"]
            if issue["code"] == "draft_or_pending_wording_in_current_doc"
        ),
    }
    return {
        "version": CURRENT_VERSION,
        "scope": "repository_doc_markdown_rst_txt",
        "summary": summary,
        "documents": docs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = build_payload()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    summary = payload["summary"]
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
