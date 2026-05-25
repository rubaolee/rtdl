from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_DIRS = {
    "docs/audit",
    "docs/directives",
    "docs/engineering",
    "docs/handoff",
    "docs/history",
    "docs/reports",
    "docs/reviews",
}

SUPPORT_EXAMPLE_DIRS = {
    "examples/generated",
    "examples/internal",
    "examples/legacy_or_backend_proofs",
    "examples/reference",
}

CURRENT_TOP_LEVEL_DOCS = {
    "README.md",
    "docs/README.md",
    "docs/app_engine_support_matrix.md",
    "docs/app_example_quickstart.md",
    "docs/application_catalog.md",
    "docs/backend_maturity.md",
    "docs/capability_boundaries.md",
    "docs/current_architecture.md",
    "docs/current_main_support_matrix.md",
    "docs/performance_model.md",
    "docs/public_documentation_map.md",
    "docs/quick_tutorial.md",
    "docs/release_facing_examples.md",
    "docs/rtdl_feature_guide.md",
    "docs/partner_acceleration_boundaries.md",
    "docs/runtime_overhead_architecture.md",
    "docs/vision.md",
}

CURRENT_DOC_PREFIXES = (
    "docs/features/",
    "docs/learn/",
    "docs/rtdl/",
    "docs/tutorials/",
    "docs/release_reports/v2_3/",
    "examples/v2_0/",
)

CURRENT_EXAMPLE_DOCS = {"examples/README.md"}

STALE_VERSION_RE = re.compile(r"\bv(?:0|1)\.\d+(?:\.\d+)?\b|\bv2\.0\b|\bv2\.1\b|v0_|v1_")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")


@dataclass(frozen=True)
class DocAuditRow:
    path: str
    category: str
    state: str
    stale_version_hits: list[str]
    dead_local_links: list[str]
    action: str


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _git_changed_files() -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT,
        text=True,
        check=False,
        capture_output=True,
    )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        text=True,
        check=False,
        capture_output=True,
    )
    return {
        line.strip()
        for line in (result.stdout + "\n" + staged.stdout).splitlines()
        if line.strip()
    }


def classify(rel_path: str) -> str:
    if rel_path in CURRENT_TOP_LEVEL_DOCS or rel_path in CURRENT_EXAMPLE_DOCS:
        return "current_public"
    if rel_path.startswith(CURRENT_DOC_PREFIXES):
        return "current_public"
    if rel_path.startswith("docs/release_reports/"):
        return "historical_release_package"
    if any(rel_path.startswith(prefix + "/") or rel_path == prefix for prefix in HISTORICAL_DIRS):
        return "historical_audit"
    if any(rel_path.startswith(prefix + "/") or rel_path == prefix for prefix in SUPPORT_EXAMPLE_DIRS):
        return "support_artifact"
    if rel_path.startswith("examples/visual_demo/"):
        return "current_public"
    return "support_artifact"


def _text_without_code(text: str) -> str:
    no_blocks = CODE_BLOCK_RE.sub("", text)
    return INLINE_CODE_RE.sub("", no_blocks)


def stale_versions(text: str) -> list[str]:
    cleaned = _text_without_code(text)
    # Do not flag current directory names or links after code stripping.
    cleaned = cleaned.replace("examples/v2_0", "")
    return sorted(set(match.group(0) for match in STALE_VERSION_RE.finditer(cleaned)))


def _is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "tel:"))


def dead_local_links(path: Path, text: str) -> list[str]:
    dead: list[str] = []
    for raw in LINK_RE.findall(text):
        target = raw.strip()
        if not target or target.startswith("#") or _is_external(target):
            continue
        target = target.split()[0]
        target_path = unquote(target.split("#", 1)[0])
        if not target_path:
            continue
        candidate = (path.parent / target_path).resolve()
        if not candidate.exists():
            dead.append(target)
    return sorted(set(dead))


def audit_file(path: Path, changed: set[str]) -> DocAuditRow:
    rel_path = _rel(path)
    category = classify(rel_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    stale = stale_versions(text) if category == "current_public" else []
    dead = dead_local_links(path, text)
    if category == "current_public" and (stale or dead):
        state = "needs_fix"
    elif dead:
        state = "link_debt_in_non_current_artifact"
    elif category == "current_public":
        state = "current_ok"
    else:
        state = "classified_non_current"

    if rel_path in changed:
        action = "modified_or_reclassified_this_goal"
    elif category == "current_public":
        action = "reviewed_current_surface_no_change"
    elif category.startswith("historical"):
        action = "classified_historical_or_audit; not rewritten"
    else:
        action = "classified_support_artifact; not first-run doc"

    return DocAuditRow(
        path=rel_path,
        category=category,
        state=state,
        stale_version_hits=stale,
        dead_local_links=dead,
        action=action,
    )


def write_markdown(rows: list[DocAuditRow], output: Path) -> None:
    summary: dict[str, int] = {}
    for row in rows:
        summary[row.state] = summary.get(row.state, 0) + 1
    lines = [
        "# Goal2617 Documentation Cleanliness Audit",
        "",
        "This file is generated by `scripts/goal2617_current_surface_audit.py`.",
        "It classifies every Markdown file, checks local Markdown links, and",
        "enforces no stale version wording on the current public surface.",
        "",
        "## Summary",
        "",
        "| State | Count |",
        "| --- | ---: |",
    ]
    for state, count in sorted(summary.items()):
        lines.append(f"| `{state}` | {count} |")
    lines.extend(
        [
            "",
            "## Per-File Audit",
            "",
            "| File | Category | State | Stale Version Hits | Dead Local Links | Action |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        stale = ", ".join(f"`{hit}`" for hit in row.stale_version_hits) or "-"
        dead = "<br>".join(f"`{link}`" for link in row.dead_local_links) or "-"
        lines.append(
            f"| `{row.path}` | `{row.category}` | `{row.state}` | {stale} | {dead} | {row.action} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit RTDL current docs for v2.3 cleanliness.")
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    changed = _git_changed_files()
    files = sorted(
        [ROOT / "README.md"]
        + list((ROOT / "docs").rglob("*.md"))
        + list((ROOT / "examples").rglob("README.md"))
    )
    rows = [audit_file(path, changed) for path in files]
    payload = {
        "goal": "Goal2617",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "counts": {
            "total_markdown_files": len(rows),
            "current_public": sum(row.category == "current_public" for row in rows),
            "current_needs_fix": sum(row.category == "current_public" and row.state == "needs_fix" for row in rows),
            "dead_local_link_files": sum(bool(row.dead_local_links) for row in rows),
        },
        "rows": [asdict(row) for row in rows],
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(rows, args.markdown)
    return 1 if payload["counts"]["current_needs_fix"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
