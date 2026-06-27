from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4774_release_packaging_audit import (  # noqa: E402
    validate_v4_goal4774_release_packaging_audit,
)


DEFAULT_JSON = ROOT / "future/v4/evidence/v4_goal4774_release_packaging_audit_2026-06-27.json"
DEFAULT_MD = ROOT / "future/v4/v4_goal4774_release_packaging_audit_2026-06-27.md"


def _write_markdown(payload: dict, path: Path) -> None:
    lines = [
        "# Goal4774 - V4 Release Packaging Audit",
        "",
        "Status: `release_packaging_audit_created__clean_commit_required_before_tag`",
        "",
        "## Summary",
        "",
        f"- dirty entries: `{payload['total_dirty_entries']}`",
        f"- release commit candidates: `{payload['release_commit_candidate_count']}`",
        f"- excluded from release commit: `{payload['exclude_from_release_commit_count']}`",
        f"- manual review required: `{payload['manual_review_required_count']}`",
        f"- direct git tag allowed now: `{str(payload['direct_git_tag_allowed_now']).lower()}`",
        f"- clean commit required before tag: `{str(payload['clean_commit_required_before_tag']).lower()}`",
        f"- POD required for packaging: `{str(payload['pod_required_for_packaging']).lower()}`",
        f"- Claude required for packaging audit: `{str(payload['claude_required_for_packaging_audit']).lower()}`",
        "",
        "## Bucket Counts",
        "",
        "| Bucket | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(payload["bucket_counts"].items()):
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Manual Review Required",
            "",
        ]
    )
    if payload["manual_review_required"]:
        for item in payload["manual_review_required"][:80]:
            lines.append(f"- `{item}`")
        if len(payload["manual_review_required"]) > 80:
            lines.append(f"- ... `{len(payload['manual_review_required']) - 80}` more")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Excluded From Release Commit",
            "",
            "These paths should not be blindly committed into the V4 release tree.",
            "",
        ]
    )
    for item in payload["excluded_from_release_commit"][:80]:
        lines.append(f"- `{item}`")
    if len(payload["excluded_from_release_commit"]) > 80:
        lines.append(f"- ... `{len(payload['excluded_from_release_commit']) - 80}` more")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Create a clean release branch/commit from the release candidates after",
            "manual-review paths are resolved. Do not create a public V4.0 tag on",
            "the current stale committed HEAD.",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)

    payload = validate_v4_goal4774_release_packaging_audit(ROOT)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, args.md_out)
    print(json.dumps({"status": "ok", "json": str(args.json_out), "markdown": str(args.md_out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
