from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4775_release_staging_manifest import (  # noqa: E402
    V4_GOAL4775_STATUS,
    validate_v4_goal4775_release_staging_manifest,
)


DEFAULT_JSON = ROOT / "tools/_archive/future/v4/evidence/v4_goal4775_release_staging_manifest_2026-06-27.json"
DEFAULT_MD = ROOT / "tools/_archive/future/v4/v4_goal4775_release_staging_manifest_2026-06-27.md"
DEFAULT_PATHSPEC = ROOT / "tools/_archive/future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt"


def _write_markdown(payload: dict, path: Path, pathspec_path: Path) -> None:
    lines = [
        "# Goal4775 - V4 Release Staging Manifest",
        "",
        f"Status: `{V4_GOAL4775_STATUS}`",
        "",
        "## Summary",
        "",
        f"- dirty file entries from `git status -uall`: `{payload['total_dirty_file_entries']}`",
        f"- stage for V4 release commit: `{payload['stage_for_v4_release_commit_count']}`",
        f"- exclude from V4 release commit: `{payload['exclude_from_v4_release_commit_count']}`",
        f"- hold V3 history out of V4 tag: `{payload['hold_v3_history_not_v4_tag_count']}`",
        f"- manual review required: `{payload['manual_review_required_count']}`",
        f"- pathspec ready: `{str(payload['pathspec_ready']).lower()}`",
        f"- direct git tag allowed now: `{str(payload['direct_git_tag_allowed_now']).lower()}`",
        f"- clean release commit required before tag: `{str(payload['clean_release_commit_required_before_tag']).lower()}`",
        f"- POD required for this manifest: `{str(payload['pod_required_for_staging_manifest']).lower()}`",
        f"- Claude required for this manifest: `{str(payload['claude_required_for_staging_manifest']).lower()}`",
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
            "## Pathspec",
            "",
            f"- generated pathspec file: `{pathspec_path.as_posix()}`",
            "- use only after the release owner agrees this exact staging set is the desired V4.0 tag content",
            "",
            "## Required Stage Paths",
            "",
        ]
    )
    for item in payload["required_stage_paths"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## V3 History Held Out",
            "",
            "These paths are not staged for the V4 public tag. They can remain as workspace history",
            "or be archived separately, but they must not be silently bundled into the V4 release commit.",
            "",
        ]
    )
    for item in payload["hold_v3_history_not_v4_tag"][:80]:
        lines.append(f"- `{item}`")
    if len(payload["hold_v3_history_not_v4_tag"]) > 80:
        lines.append(f"- ... `{len(payload['hold_v3_history_not_v4_tag']) - 80}` more")
    lines.extend(
        [
            "",
            "## Excluded Raw Or External Artifacts",
            "",
        ]
    )
    for item in payload["exclude_from_v4_release_commit"][:80]:
        lines.append(f"- `{item}`")
    if len(payload["exclude_from_v4_release_commit"]) > 80:
        lines.append(f"- ... `{len(payload['exclude_from_v4_release_commit']) - 80}` more")
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            "1. 我是否愚蠢了？没有继续 `git add .`，这是正确的；但 Goal4774 的候选分桶过宽，若直接使用会愚蠢。",
            "2. 如果是，我做了哪些动作使决策愚蠢？把所有 `tests/`、`scripts/` 粗略视为候选，会把 V3 Phoenix 历史混进 V4 tag。",
            "3. 是否有别的路径避免卡在坏思路？有：逐文件展开 `git status -uall`，把 V3 history、raw logs、external/build artifacts 独立排除。",
            "4. 是否可以尝试不同路径真正解决问题？可以，下一步只用这份 pathspec 做可审 staging，不直接打 tag。",
            "",
            "## Next Step",
            "",
            "Run the manifest tests and full V4 tests. If they pass, the release owner can inspect",
            "the generated pathspec before any staging or commit. A public V4.0 tag still requires",
            "a clean release commit; this file does not create the tag.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_pathspec(payload: dict, path: Path) -> None:
    text = "\n".join(payload["stage_for_v4_release_commit"]) + "\n"
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--pathspec-out", type=Path, default=DEFAULT_PATHSPEC)
    args = parser.parse_args(argv)

    payload = validate_v4_goal4775_release_staging_manifest(ROOT)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.pathspec_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_pathspec(payload, args.pathspec_out)
    _write_markdown(payload, args.md_out, args.pathspec_out)
    print(
        json.dumps(
            {
                "status": "ok",
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "pathspec": str(args.pathspec_out),
                "stage_count": payload["stage_for_v4_release_commit_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
