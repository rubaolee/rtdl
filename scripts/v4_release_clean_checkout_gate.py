#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4758_local_completion_audit import validate_v4_goal4758_local_completion_audit


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_lines(root: Path, *args: str) -> list[str]:
    proc = _run_git(root, *args)
    return [line for line in proc.stdout.splitlines() if line.strip()]


def git_status(root: Path) -> list[str]:
    return git_lines(root, "status", "--porcelain")


def git_tracked_paths(root: Path) -> set[str]:
    return set(git_lines(root, "ls-files"))


def tag_target(root: Path, tag: str) -> str:
    proc = _run_git(root, "rev-parse", f"{tag}^{{}}", check=False)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def head_commit(root: Path) -> str:
    return git_lines(root, "rev-parse", "HEAD")[0]


def check_ignored(root: Path, path: str) -> bool:
    proc = _run_git(root, "check-ignore", "--no-index", "-q", path, check=False)
    return proc.returncode == 0


def release_artifact_paths(root: Path) -> tuple[str, ...]:
    audit = validate_v4_goal4758_local_completion_audit(root)
    paths: set[str] = {
        str(audit["package_wheel"]),
        str(audit["package_build_log"]),
        str(audit["wheel_install_log"]),
        str(audit["wheel_import_log"]),
        str(audit["wheel_smoke_summary"]),
        str(audit["final_review_manifest"]),
    }

    manifest_path = root / str(audit["final_review_manifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        paths.add(str(artifact["path"]))

    return tuple(sorted(paths))


def check_release_artifact_tracking(root: Path) -> dict[str, Any]:
    tracked = git_tracked_paths(root)
    paths = release_artifact_paths(root)
    missing = [path for path in paths if not (root / path).exists()]
    untracked = [path for path in paths if path not in tracked]
    ignored_log_paths = [path for path in paths if path.endswith(".log") and check_ignored(root, path)]
    ignored_untracked_logs = [path for path in ignored_log_paths if path not in tracked]
    return {
        "artifact_count": len(paths),
        "missing_artifacts": missing,
        "untracked_artifacts": untracked,
        "ignored_log_artifacts": ignored_log_paths,
        "ignored_untracked_log_artifacts": ignored_untracked_logs,
        "tracked_ignored_log_artifacts": [path for path in ignored_log_paths if path in tracked],
        "passed": not missing and not untracked and not ignored_untracked_logs,
    }


def run_universe_gate(root: Path, *, strict_release: bool) -> dict[str, Any]:
    import importlib.util

    script = root / "scripts" / "v4_universe_audit.py"
    spec = importlib.util.spec_from_file_location("v4_universe_audit_for_release_gate", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load v4_universe_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_audit(strict_release=strict_release)


def run_gate(
    root: Path,
    *,
    allow_dirty: bool = False,
    strict_release: bool = True,
    require_tag_head: bool = False,
    tag: str = "v4.0.0",
) -> dict[str, Any]:
    status_entries = git_status(root)
    universe = run_universe_gate(root, strict_release=strict_release)
    artifact_tracking = check_release_artifact_tracking(root)
    head = head_commit(root)
    tag_sha = tag_target(root, tag)
    tag_ok = (tag_sha == head) if require_tag_head else True

    failures: list[str] = []
    if status_entries and not allow_dirty:
        failures.append("working_tree_not_clean")
    universe_ok = universe["status"] == "pass" or (
        allow_dirty and not strict_release and str(universe["status"]).startswith("pass")
    )
    if not universe_ok:
        failures.append(f"universe_gate_{universe['status']}")
    if not artifact_tracking["passed"]:
        failures.append("release_artifacts_not_tracked")
    if not tag_ok:
        failures.append("tag_target_mismatch")

    return {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "head": head,
        "tag": tag,
        "tag_target": tag_sha,
        "tag_matches_head": tag_sha == head,
        "working_tree_clean": not status_entries,
        "dirty_entry_count": len(status_entries),
        "dirty_entries": status_entries[:40],
        "universe_gate_status": universe["status"],
        "universe_public_findings": universe["public_findings"],
        "universe_unknown_untracked_count": universe["unknown_untracked_count"],
        "artifact_tracking": artifact_tracking,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 release clean-checkout gate.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--non-strict-release", action="store_true")
    parser.add_argument("--require-tag-head", action="store_true")
    parser.add_argument("--tag", default="v4.0.0")
    args = parser.parse_args()

    result = run_gate(
        args.root.resolve(),
        allow_dirty=args.allow_dirty,
        strict_release=not args.non_strict_release,
        require_tag_head=args.require_tag_head,
        tag=args.tag,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
