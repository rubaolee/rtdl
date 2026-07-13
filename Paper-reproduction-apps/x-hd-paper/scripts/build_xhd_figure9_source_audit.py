"""Audit X-HD Figure 9 source/script evidence.

This is an app-owned provenance script.  It reads the pinned author repository
through git object access, separates Figure-9 plotting scripts from training
sweeps, and writes a status-bearing artifact.  It intentionally does not run an
RTDL route and does not claim Figure 9 reproduction.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_GIT_DIR = Path("scratch/xhd_author_goal5285.git")
DEFAULT_REV = "paper"
DEFAULT_OUTPUT = Path(
    "Paper-reproduction-apps/x-hd-paper/results/"
    "xhd_goal5285_figure9_source_script_audit_2026-07-09.json"
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


def _show_text(git_dir: Path, rev: str, path: str) -> str:
    return _git(git_dir, "show", f"{rev}:{path}")


def _list_files(git_dir: Path, rev: str) -> list[str]:
    return [
        line
        for line in _git(git_dir, "ls-tree", "-r", "--name-only", rev).splitlines()
        if line
    ]


def _between(text: str, start: str, end: str | None = None) -> str:
    start_idx = text.find(start)
    if start_idx < 0:
        return ""
    if end is None:
        return text[start_idx:]
    end_idx = text.find(end, start_idx)
    if end_idx < 0:
        return text[start_idx:]
    return text[start_idx:end_idx]


def _extract_tuple_strings(text: str, var_name: str) -> list[str]:
    match = re.search(rf"{re.escape(var_name)}\s*=\s*\((.*?)\)", text, re.S)
    if not match:
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", match.group(1))


def _extract_list_argument(text: str, flag_name: str) -> list[int]:
    match = re.search(rf"{re.escape(flag_name)}\s+\"([0-9,]+)\"", text)
    if not match:
        return []
    return [int(piece) for piece in match.group(1).split(",") if piece]


def _run_all_auto_tune(files: list[str]) -> dict[str, Any]:
    prefix = "expr/for_the_paper/logs/run_all/auto_tune/"
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    configs: Counter[str] = Counter()
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
        by_category[category][config] += 1
        configs[config] += 1
        pair_to_configs[(category, pair_name)].add(config)

    complete_two_config_pairs = sum(1 for values in pair_to_configs.values() if len(values) == 2)
    incomplete_pairs = sum(1 for values in pair_to_configs.values() if len(values) != 2)
    return {
        "record_count": sum(configs.values()),
        "unique_pair_count": len(pair_to_configs),
        "configs": dict(sorted(configs.items())),
        "by_category": {key: dict(sorted(value.items())) for key, value in sorted(by_category.items())},
        "complete_two_config_pair_count": complete_two_config_pairs,
        "incomplete_pair_count": incomplete_pairs,
    }


def _train_sweeps(files: list[str]) -> dict[str, Any]:
    n_points_values: Counter[int] = Counter()
    max_hit_values: Counter[int] = Counter()

    for path in files:
        if not path.startswith("expr/for_the_paper/logs/train/") or not path.endswith(".json"):
            continue
        n_match = re.search(r"_n_points_cell_([0-9]+)\.json$", path)
        if n_match:
            n_points_values[int(n_match.group(1))] += 1
        max_match = re.search(r"_max_hit_([0-9]+)\.json$", path)
        if max_match:
            max_hit_values[int(max_match.group(1))] += 1

    return {
        "n_points_cell_value_count": len(n_points_values),
        "n_points_cell_values": sorted(n_points_values),
        "n_points_cell_record_count": sum(n_points_values.values()),
        "max_hit_value_count": len(max_hit_values),
        "max_hit_values": sorted(max_hit_values),
        "max_hit_record_count": sum(max_hit_values.values()),
    }


def build_audit(git_dir: Path = DEFAULT_GIT_DIR, rev: str = DEFAULT_REV) -> dict[str, Any]:
    files = _list_files(git_dir, rev)
    head = _git(git_dir, "rev-parse", rev).strip()

    plot_script = "expr/for_the_paper/effective_autoune.py"
    run_script = "expr/for_the_paper/effective_autotune.sh"
    train_script = "expr/for_the_paper/gen_train.sh"
    flags_source = "src/flags.cc"
    hybrid_source = "src/hd_impl/hausdorff_distance_hybrid.h"

    plot_text = _show_text(git_dir, rev, plot_script)
    run_text = _show_text(git_dir, rev, run_script)
    train_text = _show_text(git_dir, rev, train_script)
    flags_text = _show_text(git_dir, rev, flags_source)
    hybrid_text = _show_text(git_dir, rev, hybrid_source)

    draw_mri_modelnet_body = _between(plot_text, "def draw_mri_modelnet():", "def draw_spatial_graphics():")
    active_tail = plot_text.splitlines()[-8:]
    expected_variants = _extract_tuple_strings(draw_mri_modelnet_body, "variants")
    variant_labels = _extract_tuple_strings(draw_mri_modelnet_body, "variant_labels")
    plotted_dataset_names = re.findall(r'draw_subfig\("([^"]+)"', draw_mri_modelnet_body)

    run_all = _run_all_auto_tune(files)
    train_sweeps = _train_sweeps(files)

    observed_configs = sorted(run_all["configs"].keys())
    missing_plot_variants = [variant for variant in expected_variants if variant not in observed_configs]
    extra_log_configs = [config for config in observed_configs if config not in expected_variants]

    active_run_calls = {
        "run_mri_enabled": bool(re.search(r"^run_mri\s*$", run_text, re.M)),
        "run_modelnet_enabled": bool(re.search(r"^run_modelnet\s*$", run_text, re.M)),
        "run_geo_enabled": bool(re.search(r"^run_geo\s*$", run_text, re.M)),
        "run_graphics_enabled": bool(re.search(r"^run_graphics\s*$", run_text, re.M)),
    }
    run_script_config_flags = sorted(set(re.findall(r"run_hd .*? (true|false) (true|false)", run_text)))

    n_points_list = _extract_list_argument(train_text, "-n_points_cell_list")
    max_hit_list = _extract_list_argument(train_text, "-max_hit_list")

    source_flags = {
        "has_auto_tune_flag": "DEFINE_bool(auto_tune" in flags_text,
        "has_auto_tune_n_points_cell_flag": "DEFINE_bool(auto_tune_n_points_cell" in flags_text,
        "has_auto_tune_max_hit_flag": "DEFINE_bool(auto_tune_max_hit" in flags_text,
        "has_n_points_cell_list_flag": "DEFINE_string(n_points_cell_list" in flags_text,
        "has_max_hit_list_flag": "DEFINE_string(max_hit_list" in flags_text,
        "hybrid_predicts_num_points_per_cell": "PredictNumPointsPerCell_3D" in hybrid_text,
        "hybrid_predicts_max_hit": "PredictMaxHit_3D" in hybrid_text,
    }

    plot_script_exists = plot_script in files
    plot_script_active_draw = "draw_mri_modelnet()" in "\n".join(active_tail)
    train_sweep_exists = bool(train_sweeps["n_points_cell_values"] or train_sweeps["max_hit_values"])

    figure9_reproduced = False
    source_mapping_status = "figure9_source_script_mapped__figure9_not_reproduced"
    if not plot_script_exists:
        source_mapping_status = "figure9_plot_script_missing__figure9_not_reproduced"
    elif missing_plot_variants:
        source_mapping_status = "figure9_plot_script_expects_missing_run_all_variants__figure9_not_reproduced"

    return {
        "schema": "rtdl.paper_reproduction.xhd.figure9_source_script_audit.v1",
        "goal": "Goal5285",
        "status": source_mapping_status,
        "author_repo": {
            "repository": "https://github.com/pwrliang/X-HD.git",
            "rev": rev,
            "head": head,
            "audit_method": "git object access; no checkout required",
        },
        "figure9_plot_script": {
            "path": plot_script,
            "exists": plot_script_exists,
            "active_draw_call_in_source_tail": plot_script_active_draw,
            "active_tail": active_tail,
            "expected_variants": expected_variants,
            "variant_labels": variant_labels,
            "plotted_dataset_names_in_active_function": plotted_dataset_names,
            "saves_pdf": "auto-tune.pdf" in plot_text,
            "loads_run_all_auto_tune": "logs/run_all/auto_tune" in draw_mri_modelnet_body,
        },
        "run_all_auto_tune_logs": run_all,
        "run_all_vs_plot_script": {
            "observed_configs": observed_configs,
            "plot_expected_variants": expected_variants,
            "missing_plot_variants_from_run_all_logs": missing_plot_variants,
            "extra_run_all_configs_not_in_plot_variants": extra_log_configs,
            "all_plot_variants_present_in_current_run_all_logs": not missing_plot_variants,
        },
        "effective_autotune_runner": {
            "path": run_script,
            "active_calls": active_run_calls,
            "literal_boolean_run_hd_pairs_detected": run_script_config_flags,
            "observation": (
                "The checked paper-branch runner calls only false/false and true/true "
                "for enabled run_modelnet, while run_mri/run_geo/run_graphics are commented."
            ),
        },
        "training_sweeps": {
            "path": train_script,
            "script_n_points_cell_list": n_points_list,
            "script_max_hit_list": max_hit_list,
            "logs": train_sweeps,
            "not_same_as_figure9_run_all": True,
            "reason": (
                "gen_train.sh and logs/train contain multi-value parameter sweeps used to "
                "train/tune predictor models, but effective_autoune.py reads "
                "logs/run_all/auto_tune for the auto-tune figure."
            ),
        },
        "source_flags_and_models": source_flags,
        "claim_boundary": {
            "figure9_reproduced": figure9_reproduced,
            "full_paper_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "rtdl_route_result_claimed": False,
            "performance_ratio_claimed": False,
        },
        "decision": {
            "figure9_reproduced": figure9_reproduced,
            "reason": (
                "The source contains a Figure-9-like auto-tune plotting script and "
                "training sweeps, but the current paper-branch run_all auto_tune logs "
                "do not provide all four plotted variants or a paper-selected grid-size "
                "choice table. Training sweeps must not be promoted to Figure 9 "
                "reproduction without a script mapping from train logs to the plot."
            ),
            "allowed_next_steps": [
                "Treat Goal5285 as source/script mapping evidence only.",
                "If Figure 9 remains a priority, either recover the missing run_all variants or reconstruct the plot from an externally reviewed script/data mapping.",
                "Do not implement RTDL route work for Figure 9 until the author-side plot denominator is complete.",
            ],
            "forbidden_summaries": [
                "Figure 9 reproduced",
                "all auto-tune variants recovered",
                "training sweep equals Figure 9",
                "RTDL Figure 9 speedup or parity",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 9 source/script audit artifact.")
    parser.add_argument("--git-dir", type=Path, default=DEFAULT_GIT_DIR)
    parser.add_argument("--rev", default=DEFAULT_REV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    audit = build_audit(args.git_dir, args.rev)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": audit["status"]}, indent=2))


if __name__ == "__main__":
    main()
