"""Audit X-HD Figure 9 availability across pinned author branches.

This app-owned provenance script checks whether the missing Figure 9
`run_all/auto_tune` variants found in Goal5285 are present on another pinned
author branch.  It also records whether the checked-in `auto-tune.pdf` artifact
exists.  It does not treat a checked-in PDF as a reproduced figure.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_GIT_DIR = Path("scratch/xhd_author_goal5285.git")
DEFAULT_BRANCHES = ("paper", "main", "hybrid")
DEFAULT_OUTPUT = Path(
    "Paper-reproduction-apps/x-hd-paper/results/"
    "xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json"
)
FIGURE9_EXPECTED_VARIANTS = (
    "n_points_cell_false_max_hit_false",
    "n_points_cell_true_max_hit_false",
    "n_points_cell_false_max_hit_true",
    "n_points_cell_true_max_hit_true",
)


def _git(git_dir: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "--git-dir", str(git_dir), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def _list_files(git_dir: Path, rev: str) -> list[str]:
    return [
        line
        for line in _git(git_dir, "ls-tree", "-r", "--name-only", rev).splitlines()
        if line
    ]


def _tree_object(git_dir: Path, rev: str, path: str) -> dict[str, Any] | None:
    try:
        out = _git(git_dir, "ls-tree", rev, path).strip()
    except subprocess.CalledProcessError:
        return None
    if not out:
        return None
    # Format: "100644 blob <sha>\t<path>"
    meta, _, tree_path = out.partition("\t")
    pieces = meta.split()
    if len(pieces) < 3:
        return None
    size = int(_git(git_dir, "cat-file", "-s", pieces[2]).strip())
    return {
        "mode": pieces[0],
        "type": pieces[1],
        "object": pieces[2],
        "path": tree_path,
        "size_bytes": size,
    }


def _run_all_summary(files: list[str]) -> dict[str, Any]:
    prefix = "expr/for_the_paper/logs/run_all/auto_tune/"
    configs: Counter[str] = Counter()
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    pair_to_configs: dict[tuple[str, str], set[str]] = defaultdict(set)

    for path in files:
        if not path.startswith(prefix) or not path.endswith(".json"):
            continue
        rest = path[len(prefix) :]
        parts = rest.split("/")
        if len(parts) < 3:
            continue
        category, config = parts[0], parts[1]
        pair_name = "/".join(parts[2:])
        configs[config] += 1
        by_category[category][config] += 1
        pair_to_configs[(category, pair_name)].add(config)

    observed = sorted(configs)
    missing = [variant for variant in FIGURE9_EXPECTED_VARIANTS if variant not in configs]
    return {
        "record_count": sum(configs.values()),
        "unique_pair_count": len(pair_to_configs),
        "configs": dict(sorted(configs.items())),
        "by_category": {key: dict(sorted(value.items())) for key, value in sorted(by_category.items())},
        "config_set_size_histogram": {
            str(key): value for key, value in sorted(Counter(len(v) for v in pair_to_configs.values()).items())
        },
        "observed_configs": observed,
        "missing_expected_figure9_variants": missing,
        "all_expected_figure9_variants_present": not missing,
    }


def build_audit(git_dir: Path = DEFAULT_GIT_DIR, branches: tuple[str, ...] = DEFAULT_BRANCHES) -> dict[str, Any]:
    branch_payload: dict[str, Any] = {}
    any_branch_complete = False

    for branch in branches:
        head = _git(git_dir, "rev-parse", branch).strip()
        files = _list_files(git_dir, branch)
        run_all = _run_all_summary(files)
        any_branch_complete = any_branch_complete or run_all["all_expected_figure9_variants_present"]
        branch_payload[branch] = {
            "head": head,
            "run_all_auto_tune": run_all,
            "figure9_files": {
                "plot_script": _tree_object(git_dir, branch, "expr/for_the_paper/effective_autoune.py"),
                "runner_script": _tree_object(git_dir, branch, "expr/for_the_paper/effective_autotune.sh"),
                "train_script": _tree_object(git_dir, branch, "expr/for_the_paper/gen_train.sh"),
                "checked_in_pdf": _tree_object(git_dir, branch, "expr/for_the_paper/auto-tune.pdf"),
            },
        }

    return {
        "schema": "rtdl.paper_reproduction.xhd.figure9_branch_availability_audit.v1",
        "goal": "Goal5286",
        "author_repo": {
            "repository": "https://github.com/pwrliang/X-HD.git",
            "branches": list(branches),
            "audit_method": "git object access; no checkout required",
        },
        "expected_figure9_variants": list(FIGURE9_EXPECTED_VARIANTS),
        "branches": branch_payload,
        "decision": {
            "any_branch_has_all_expected_figure9_variants": any_branch_complete,
            "figure9_reproduced": False,
            "status": (
                "missing_figure9_variants_not_found_on_pinned_branches__figure9_not_reproduced"
                if not any_branch_complete
                else "some_branch_has_all_expected_variants__requires_plot_reproduction_review"
            ),
            "checked_in_pdf_is_reproduction_evidence_only": True,
            "reason": (
                "The pinned author branches do not provide all four expected run_all auto_tune "
                "variants. The paper branch contains a checked-in auto-tune.pdf artifact, but a "
                "PDF artifact is not a reproducible denominator for RTDL/author comparison."
            ),
            "forbidden_summaries": [
                "Figure 9 reproduced",
                "missing variants recovered from main or hybrid",
                "checked-in PDF equals reproducible Figure 9",
                "RTDL Figure 9 speedup or parity",
            ],
        },
        "claim_boundary": {
            "figure9_reproduced": False,
            "full_paper_reproduction_claimed": False,
            "rtdl_route_result_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 9 branch availability audit.")
    parser.add_argument("--git-dir", type=Path, default=DEFAULT_GIT_DIR)
    parser.add_argument("--branches", nargs="+", default=list(DEFAULT_BRANCHES))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    audit = build_audit(args.git_dir, tuple(args.branches))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": audit["decision"]["status"]}, indent=2))


if __name__ == "__main__":
    main()
