#!/usr/bin/env python3
"""Extract an X-HD author-log workload manifest.

The author repository ships experiment scripts and JSON logs, but not the
input datasets under /local/storage/shared/HDDatasets. This tool turns those
logs into a structured provenance artifact so the paper-app can distinguish:

* exact input files available;
* author-log paths known but files missing;
* same-source representative candidates.

It does not claim paper reproduction by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _git_lines(repo: Path, *args: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def _float_list(values: list[Any], key: str) -> list[float]:
    out: list[float] = []
    for item in values:
        value = item.get(key) if isinstance(item, dict) else None
        if isinstance(value, (int, float)):
            out.append(float(value))
    return out


def _median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _input_record(file_record: dict[str, Any]) -> dict[str, Any]:
    path = str(file_record.get("Path", ""))
    return {
        "path": path,
        "basename": Path(path).name,
        "num_points": file_record.get("NumPoints"),
        "gini_index": file_record.get("GiniIndex"),
        "density": file_record.get("Density"),
        "stats_grid_num_points_per_cell": file_record.get("StatsGridNumPointsPerCell"),
        "mbr": file_record.get("MBR"),
        "exists_on_current_machine": Path(path).exists(),
        "author_repo_contains_file": False,
        "exact_status": "author_log_path_known__input_file_not_available",
    }


def _summarize_log(repo: Path, log_root: Path, log_path: Path) -> dict[str, Any]:
    data = json.loads(log_path.read_text())
    rel = log_path.relative_to(repo).as_posix()
    parts = log_path.relative_to(log_root).parts
    log_family = parts[0] if parts else None
    variant_execution = parts[1] if len(parts) > 1 else None
    category = parts[2] if len(parts) > 2 else None
    input_obj = data.get("Input", {}) if isinstance(data.get("Input"), dict) else {}
    files = input_obj.get("Files", [])
    if not isinstance(files, list):
        files = []
    running = data.get("Running", {}) if isinstance(data.get("Running"), dict) else {}
    repeats = running.get("Repeats", [])
    if not isinstance(repeats, list):
        repeats = []
    reported = _float_list(repeats, "ReportedTime")
    bvh = _float_list(repeats, "BVHBuildTime")
    iteration_count = 0
    rt_time_sum = 0.0
    cuda_time_sum = 0.0
    offload_sum = 0
    for repeat in repeats:
        for iteration in repeat.get("Iterations", []) if isinstance(repeat, dict) else []:
            if not isinstance(iteration, dict):
                continue
            iteration_count += 1
            if isinstance(iteration.get("RTTime"), (int, float)):
                rt_time_sum += float(iteration["RTTime"])
            if isinstance(iteration.get("CUDATime"), (int, float)):
                cuda_time_sum += float(iteration["CUDATime"])
            if isinstance(iteration.get("OffloadingSize"), int):
                offload_sum += int(iteration["OffloadingSize"])
    return {
        "relative_log_path": rel,
        "log_root": log_root.relative_to(repo).as_posix(),
        "log_family": log_family,
        "variant_execution": variant_execution,
        "category": category,
        "file_name": log_path.name,
        "datetime": data.get("DateTime"),
        "gpu": data.get("GPU"),
        "hd_result": data.get("HDResult"),
        "input": {
            "num_dims": input_obj.get("NumDims"),
            "type": input_obj.get("Type"),
            "normalize": input_obj.get("Normalize"),
            "translate": input_obj.get("Translate"),
            "limit": input_obj.get("Limit"),
            "serialization_prefix": input_obj.get("SerializationPrefix"),
            "files": [_input_record(f) for f in files if isinstance(f, dict)],
        },
        "running": {
            "avg_time": running.get("AvgTime"),
            "seed": running.get("Seed"),
            "num_points_per_cell": running.get("NumPointsPerCell"),
            "lb": running.get("LB"),
            "eb": running.get("EB"),
            "prune": running.get("Prune"),
            "repeat_count": len(repeats),
            "reported_time_median": _median_or_none(reported),
            "reported_time_min": min(reported) if reported else None,
            "reported_time_max": max(reported) if reported else None,
            "bvh_build_time_median": _median_or_none(bvh),
            "iteration_count": iteration_count,
            "iteration_rt_time_sum": rt_time_sum,
            "iteration_cuda_time_sum": cuda_time_sum,
            "iteration_offloading_size_sum": offload_sum,
        },
    }


def _branch_json_inventory(repo: Path, rev: str, root: str) -> dict[str, Any]:
    names = [
        name
        for name in _git_lines(repo, "ls-tree", "-r", "--name-only", rev, root)
        if name.endswith(".json")
    ]
    by_prefix_1: Counter[str] = Counter()
    by_prefix_2: Counter[str] = Counter()
    root_parts = Path(root).parts
    root_len = len(root_parts)
    for name in names:
        parts = Path(name).parts[root_len:]
        if parts:
            by_prefix_1[parts[0]] += 1
        if len(parts) >= 2:
            by_prefix_2["/".join(parts[:2])] += 1
    return {
        "rev": rev,
        "root": root,
        "json_count": len(names),
        "by_first_component": dict(sorted(by_prefix_1.items())),
        "by_first_two_components_top20": dict(by_prefix_2.most_common(20)),
        "sample_paths": names[:20],
        "status": "inventory_only__json_blobs_not_parsed_into_workloads",
    }


def build_manifest(author_repo: Path) -> dict[str, Any]:
    author_repo = author_repo.resolve()
    candidate_log_roots = [
        author_repo / "expr" / "logs",
        author_repo / "expr" / "for_the_paper" / "logs",
    ]
    log_roots = [root for root in candidate_log_roots if root.exists()]
    log_paths = [(root, p) for root in log_roots for p in sorted(root.rglob("*.json"))]
    records = [_summarize_log(author_repo, root, p) for root, p in log_paths]
    by_family: Counter[str] = Counter()
    by_variant: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    unique_inputs: dict[str, dict[str, Any]] = {}
    for record in records:
        by_family[str(record.get("log_family"))] += 1
        by_variant[str(record.get("variant_execution"))] += 1
        by_category[str(record.get("category"))] += 1
        for file_record in record["input"]["files"]:
            path = file_record["path"]
            if path not in unique_inputs:
                unique_inputs[path] = {
                    "path": path,
                    "basename": file_record["basename"],
                    "num_points": file_record["num_points"],
                    "gini_index": file_record["gini_index"],
                    "exists_on_current_machine": file_record["exists_on_current_machine"],
                    "author_repo_contains_file": file_record["author_repo_contains_file"],
                    "exact_status": file_record["exact_status"],
                    "seen_in_log_count": 0,
                    "categories": [],
                }
            unique_inputs[path]["seen_in_log_count"] += 1
            category = record.get("category")
            if category and category not in unique_inputs[path]["categories"]:
                unique_inputs[path]["categories"].append(category)
    source_files = [
        "expr/common.sh",
        "expr/run_fig5.sh",
        "expr/run_grid_tuning.sh",
        "expr/run_lb.sh",
        "expr/run_mem.sh",
        "expr/run_radius_tuning.sh",
        "expr/run_rt_comparison.sh",
        "expr/run_scalability.sh",
        "expr/run_translate.sh",
    ]
    source_hashes = {}
    for rel in source_files:
        p = author_repo / rel
        if p.exists():
            source_hashes[rel] = _sha256(p)
    return {
        "schema": "rtdl.paper_reproduction.xhd.author_log_workload_manifest.v1",
        "goal": "Goal5175",
        "status": "author_log_workload_manifest_extracted__input_files_not_present",
        "author_repo": {
            "path": str(author_repo),
            "head": _git(author_repo, "rev-parse", "HEAD"),
            "branch_heads": {
                "main": _git(author_repo, "rev-parse", "origin/main"),
                "paper": _git(author_repo, "rev-parse", "origin/paper"),
                "hybrid": _git(author_repo, "rev-parse", "origin/hybrid"),
            },
            "source_hashes": source_hashes,
        },
        "log_roots_scanned": [
            {
                "path": root.relative_to(author_repo).as_posix(),
                "json_count": len(list(root.rglob("*.json"))),
            }
            for root in log_roots
        ],
        "additional_branch_log_inventories": [
            _branch_json_inventory(
                author_repo,
                "origin/paper",
                "expr/for_the_paper",
            )
        ],
        "summary": {
            "total_json_logs": len(records),
            "logs_by_family": dict(sorted(by_family.items())),
            "logs_by_variant_execution": dict(sorted(by_variant.items())),
            "logs_by_category": dict(sorted(by_category.items())),
            "unique_input_path_count": len(unique_inputs),
            "input_files_available_on_current_machine": sum(
                1 for item in unique_inputs.values() if item["exists_on_current_machine"]
            ),
            "input_files_available_in_author_repo": sum(
                1 for item in unique_inputs.values() if item["author_repo_contains_file"]
            ),
        },
        "exact_dataset_rule": {
            "level_c_requires": [
                "author-provided input files",
                "retained hashes for converted point sets",
                "byte-identical converted point sets",
                "or a documented author script that deterministically regenerates the same point sets from pinned public source files",
            ],
            "author_logs_provide": [
                "input absolute paths",
                "dataset basenames",
                "point counts",
                "Gini indices",
                "MBR statistics",
                "HDResult and timing fields",
                "experiment script command structure",
            ],
            "author_logs_do_not_provide": [
                "input file bytes",
                "input file hashes",
                "public source snapshot hashes",
                "proof that a reconstructed public dataset is byte-identical",
            ],
        },
        "unique_inputs": sorted(unique_inputs.values(), key=lambda x: x["path"]),
        "workloads": records,
        "claim_boundary": {
            "full_paper_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-repo", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = build_manifest(Path(args.author_repo))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        "wrote",
        output,
        "logs=",
        manifest["summary"]["total_json_logs"],
        "unique_inputs=",
        manifest["summary"]["unique_input_path_count"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
