#!/usr/bin/env python3
"""Build a v0.7 external-input manifest."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RESEARCH_INPUTS = (
    Path("/Users/rl2025/Downloads/2024-rtscan.pdf"),
    Path("/Users/rl2025/Downloads/2025-raydb.pdf"),
)

EXTERNAL_TESTER_REPORTS = (
    Path("docs/reports/rtdl_user_correctness_test_report_2026-04-16.md"),
    Path("docs/reports/rtdl_v0_6_comprehensive_test_report_dev_handoff.md"),
    Path("docs/reports/rtdl_v0_6_windows_audit_report_2026-04-16.md"),
    Path("docs/reports/test_v07_db_attack_report_2026-04-16.md"),
    Path("docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md"),
    Path("docs/reports/external_independent_release_check_review_2026-04-15.md"),
)

TEST_RESULT_PATTERNS = (
    "docs/reports/goal4*.json",
    "docs/reports/goal4*.txt",
    "docs/reports/linux_*2026-04-16.log",
)

AI_REVIEW_PATTERNS = (
    "docs/reports/claude_goal4*_review*.md",
    "docs/reports/gemini_goal4*_review*.md",
    "docs/reports/goal4*_external_review*.md",
    "docs/reports/goal4*_review_2026-04-*.md",
    "docs/reports/goal470_claude_test_review_audit_2026-04-16.md",
)

SELF_ARTIFACT_PREFIXES = (
    "docs/goal_475_",
    "docs/handoff/GOAL475_",
    "docs/reports/goal475_",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal475-",
    "scripts/goal475_",
)

GOAL_RE = re.compile(r"(?:^|_)goal(\d+)")


@dataclass(frozen=True)
class ManifestEntry:
    category: str
    path: str
    exists: bool
    role: str
    source: str
    note: str


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _repo_entry(category: str, rel_path: Path, role: str, source: str, note: str) -> ManifestEntry:
    full = ROOT / rel_path
    return ManifestEntry(category, str(full), full.exists(), role, source, note)


def _external_entry(category: str, path: Path, role: str, source: str, note: str) -> ManifestEntry:
    return ManifestEntry(category, str(path), path.exists(), role, source, note)


def _glob_repo(patterns: tuple[str, ...]) -> list[Path]:
    seen: set[Path] = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file():
                seen.add(path.relative_to(ROOT))
    return sorted(seen)


def _is_goal400_or_later(path: Path) -> bool:
    match = GOAL_RE.search(path.name)
    if not match:
        return True
    goal = int(match.group(1))
    return 400 <= goal < 475


def _is_self_artifact(path: Path) -> bool:
    text = str(path)
    return text.startswith(SELF_ARTIFACT_PREFIXES)


def build_manifest() -> dict[str, object]:
    entries: list[ManifestEntry] = []

    for path in RESEARCH_INPUTS:
        entries.append(
            _external_entry(
                "research_source",
                path,
                "source paper",
                "user-provided local PDF",
                "Used by Goal 412 to scope v0.7 DB-style RT kernels.",
            )
        )

    for path in EXTERNAL_TESTER_REPORTS:
        entries.append(
            _repo_entry(
                "external_tester_report",
                path,
                "external tester/report input",
                "user/AI external report",
                "Preserved external input triaged by the v0.7 intake flow.",
            )
        )

    ignored_self_artifacts: list[str] = []
    ignored_out_of_scope: list[str] = []

    for path in _glob_repo(AI_REVIEW_PATTERNS):
        if _is_self_artifact(path):
            ignored_self_artifacts.append(str(ROOT / path))
            continue
        if not _is_goal400_or_later(path):
            ignored_out_of_scope.append(str(ROOT / path))
            continue
        entries.append(
            _repo_entry(
                "ai_review",
                path,
                "Claude/Gemini/external-style review",
                "AI reviewer",
                "Review or consensus evidence for a v0.7 goal.",
            )
        )

    for path in _glob_repo(TEST_RESULT_PATTERNS):
        if _is_self_artifact(path):
            ignored_self_artifacts.append(str(ROOT / path))
            continue
        if not _is_goal400_or_later(path):
            ignored_out_of_scope.append(str(ROOT / path))
            continue
        entries.append(
            _repo_entry(
                "test_or_perf_result",
                path,
                "test/performance/audit artifact",
                "local or remote validation run",
                "Machine-readable or transcript evidence for v0.7 validation.",
            )
        )

    # Deduplicate by absolute path while preserving first category assignment.
    deduped: dict[str, ManifestEntry] = {}
    for entry in entries:
        deduped.setdefault(entry.path, entry)
    entries = sorted(deduped.values(), key=lambda entry: (entry.category, entry.path))

    missing = [entry.path for entry in entries if not entry.exists]
    category_counts: dict[str, int] = {}
    for entry in entries:
        category_counts[entry.category] = category_counts.get(entry.category, 0) + 1

    ledger_path = ROOT / "docs/reports/goal439_external_tester_report_intake_ledger_2026-04-16.md"
    ledger_text = ledger_path.read_text(encoding="utf-8") if ledger_path.exists() else ""
    required_ledger_tokens = tuple(f"T439-{idx:03d}" for idx in range(1, 13))
    ledger_gaps = [token for token in required_ledger_tokens if token not in ledger_text]

    valid = bool(entries) and not missing and not ledger_gaps
    return {
        "goal": 475,
        "repo_root": str(ROOT),
        "entry_count": len(entries),
        "ignored_self_artifact_count": len(set(ignored_self_artifacts)),
        "ignored_self_artifacts": sorted(set(ignored_self_artifacts)),
        "ignored_out_of_scope_count": len(set(ignored_out_of_scope)),
        "ignored_out_of_scope": sorted(set(ignored_out_of_scope)),
        "category_counts": category_counts,
        "missing_paths": missing,
        "ledger_path": str(ledger_path),
        "required_ledger_tokens": list(required_ledger_tokens),
        "ledger_gaps": ledger_gaps,
        "staging_performed": False,
        "release_authorization": False,
        "valid": valid,
        "entries": [asdict(entry) for entry in entries],
    }


def write_csv(path: Path, entries: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "path", "exists", "role", "source", "note"])
        writer.writeheader()
        writer.writerows(entries)


def write_markdown(path: Path, manifest: dict[str, object], json_path: Path, csv_path: Path) -> None:
    lines = [
        "# Goal 475: v0.7 External Input Manifest",
        "",
        "Date: 2026-04-16",
        "Author: Codex",
        "Status: Generated manifest",
        "",
        "## Scope",
        "",
        "This manifest indexes current v0.7 external inputs: research source PDFs, preserved external tester reports, Claude/Gemini/external-style reviews, and test/performance/audit result artifacts.",
        "",
        "## Generated Artifacts",
        "",
        f"- JSON manifest: `{json_path}`",
        f"- CSV manifest: `{csv_path}`",
        "",
        "## Summary",
        "",
        f"- Entries: `{manifest['entry_count']}`",
        f"- Ignored Goal475 self-artifacts: `{manifest['ignored_self_artifact_count']}`",
        f"- Ignored out-of-scope older goal artifacts: `{manifest['ignored_out_of_scope_count']}`",
        f"- Category counts: `{json.dumps(manifest['category_counts'], sort_keys=True)}`",
        f"- Missing paths: `{len(manifest['missing_paths'])}`",
        f"- Ledger gaps: `{len(manifest['ledger_gaps'])}`",
        f"- Staging performed: `{manifest['staging_performed']}`",
        f"- Release authorization: `{manifest['release_authorization']}`",
        f"- Valid: `{manifest['valid']}`",
        "",
        "## Boundaries",
        "",
        "- The manifest is an index, not a new release authorization.",
        "- External reports are preserved as evidence and still require the scoped interpretation recorded in their goal reports.",
        "- Research PDFs are referenced by full local path and are not copied into the repo by this goal.",
        "- No staging, commit, tag, push, merge, or release action is performed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    manifest = build_manifest()
    json_path = ROOT / "docs/reports/goal475_external_input_manifest_2026-04-16.json"
    csv_path = ROOT / "docs/reports/goal475_external_input_manifest_2026-04-16.csv"
    md_path = ROOT / "docs/reports/goal475_external_input_manifest_generated_2026-04-16.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(csv_path, manifest["entries"])
    write_markdown(md_path, manifest, json_path, csv_path)
    print(
        json.dumps(
            {
                "output": str(json_path),
                "csv": str(csv_path),
                "md": str(md_path),
                "entry_count": manifest["entry_count"],
                "category_counts": manifest["category_counts"],
                "missing_paths": len(manifest["missing_paths"]),
                "ledger_gaps": len(manifest["ledger_gaps"]),
                "valid": manifest["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if manifest["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
