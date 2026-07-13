#!/usr/bin/env python3
"""Extract a compact X-HD paper-branch log index through git objects.

The author ``paper`` branch contains tens of thousands of JSON logs under
``expr/for_the_paper``. Many paths are too long for a normal Windows checkout,
so this tool reads the git tree and blob contents directly instead of
materializing those paths in the working tree.

This is provenance/index evidence only. It does not provide the input dataset
bytes or hashes needed for exact paper reproduction.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def _git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _ls_tree_json_blobs(repo: Path, rev: str, root: str) -> list[dict[str, str]]:
    raw = subprocess.check_output(
        ["git", "-C", str(repo), "ls-tree", "-r", "-z", rev, root],
        stderr=subprocess.DEVNULL,
    )
    out: list[dict[str, str]] = []
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        meta, path_b = entry.split(b"\t", 1)
        mode, typ, oid = meta.decode("ascii").split()
        path = path_b.decode("utf-8", errors="replace")
        if typ == "blob" and path.endswith(".json"):
            out.append({"mode": mode, "type": typ, "oid": oid, "path": path})
    return out


def _cat_file_batch(repo: Path, oids: Iterable[str]):
    proc = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None
    try:
        for oid in oids:
            proc.stdin.write((oid + "\n").encode("ascii"))
            proc.stdin.flush()
            header = proc.stdout.readline().decode("ascii").strip()
            if not header:
                raise RuntimeError(f"empty git cat-file header for {oid}")
            parts = header.split()
            if len(parts) != 3 or parts[1] != "blob":
                raise RuntimeError(f"unexpected git cat-file header: {header}")
            size = int(parts[2])
            data = proc.stdout.read(size)
            trailing = proc.stdout.read(1)
            if trailing not in (b"\n", b""):
                raise RuntimeError(f"unexpected cat-file separator after {oid!r}")
            yield oid, data
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        try:
            proc.stdout.close()
        except Exception:
            pass
        try:
            if proc.stderr is not None:
                proc.stderr.close()
        except Exception:
            pass


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


def _numeric_stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {
        "count": len(values),
        "min": min(values),
        "median": float(statistics.median(values)),
        "max": max(values),
    }


def _path_parts(path: str, root: str) -> tuple[str, str | None, str | None, str | None]:
    rel = str(Path(path).as_posix())
    root_norm = str(Path(root).as_posix()).rstrip("/") + "/"
    if rel.startswith(root_norm):
        rel = rel[len(root_norm) :]
    parts = rel.split("/")
    return (
        parts[0] if len(parts) > 0 else "",
        parts[1] if len(parts) > 1 else None,
        parts[2] if len(parts) > 2 else None,
        parts[3] if len(parts) > 3 else None,
    )


def _summarize_json(path: str, root: str, oid: str, data: dict[str, Any]) -> dict[str, Any]:
    group, section, category, config = _path_parts(path, root)
    input_obj = data.get("Input", {}) if isinstance(data.get("Input"), dict) else {}
    files = input_obj.get("Files", [])
    if not isinstance(files, list):
        files = []
    running = data.get("Running", {}) if isinstance(data.get("Running"), dict) else {}
    repeats = running.get("Repeats", [])
    if not isinstance(repeats, list):
        repeats = []
    reported = _float_list(repeats, "ReportedTime")
    file_records = []
    for item in files:
        if not isinstance(item, dict):
            continue
        p = str(item.get("Path", ""))
        file_records.append(
            {
                "path": p,
                "basename": Path(p).name,
                "num_points": item.get("NumPoints"),
                "gini_index": item.get("GiniIndex"),
                "mbr": item.get("MBR"),
                "exact_status": "author_log_path_known__input_file_not_available",
            }
        )
    return {
        "relative_log_path": path,
        "blob": oid,
        "log_group": group,
        "section": section,
        "category": category,
        "config": config,
        "file_name": Path(path).name,
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
            "files": file_records,
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
        },
    }


def build_index(
    repo: Path,
    rev: str,
    root: str,
    *,
    max_sample_records: int = 250,
) -> dict[str, Any]:
    repo = repo.resolve()
    blobs = _ls_tree_json_blobs(repo, rev, root)
    by_oid = {item["oid"]: item for item in blobs}
    parsed_count = 0
    parse_errors: list[dict[str, str]] = []
    by_group: Counter[str] = Counter()
    by_section: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    by_config: Counter[str] = Counter()
    by_input_type: Counter[str] = Counter()
    by_dims: Counter[str] = Counter()
    hd_values: list[float] = []
    avg_times: list[float] = []
    unique_inputs: dict[str, dict[str, Any]] = {}
    run_all_records: list[dict[str, Any]] = []
    sample_records: list[dict[str, Any]] = []
    blobs_sorted = sorted(blobs, key=lambda item: item["path"])
    for oid, raw in _cat_file_batch(repo, [item["oid"] for item in blobs_sorted]):
        meta = by_oid[oid]
        try:
            payload = json.loads(raw.decode("utf-8"))
            record = _summarize_json(meta["path"], root, oid, payload)
        except Exception as exc:  # pragma: no cover - exercised by bad artifacts.
            parse_errors.append(
                {"relative_log_path": meta["path"], "blob": oid, "error": str(exc)}
            )
            continue
        parsed_count += 1
        by_group[str(record["log_group"])] += 1
        if record.get("section") is not None:
            by_section[f"{record['log_group']}/{record['section']}"] += 1
        if record.get("category") is not None:
            by_category[f"{record['log_group']}/{record['section']}/{record['category']}"] += 1
        if record.get("config") is not None:
            by_config[
                f"{record['log_group']}/{record['section']}/{record['category']}/{record['config']}"
            ] += 1
        input_type = record["input"].get("type")
        dims = record["input"].get("num_dims")
        if input_type is not None:
            by_input_type[str(input_type)] += 1
        if dims is not None:
            by_dims[str(dims)] += 1
        if isinstance(record.get("hd_result"), (int, float)):
            hd_values.append(float(record["hd_result"]))
        avg_time = record["running"].get("avg_time")
        if isinstance(avg_time, (int, float)):
            avg_times.append(float(avg_time))
        for file_record in record["input"]["files"]:
            path = file_record["path"]
            if path not in unique_inputs:
                unique_inputs[path] = {
                    "path": path,
                    "basename": file_record["basename"],
                    "num_points": file_record["num_points"],
                    "gini_index": file_record["gini_index"],
                    "exact_status": file_record["exact_status"],
                    "seen_in_log_count": 0,
                    "log_groups": [],
                    "categories": [],
                }
            unique_inputs[path]["seen_in_log_count"] += 1
            group = record["log_group"]
            category = record["category"]
            if group not in unique_inputs[path]["log_groups"]:
                unique_inputs[path]["log_groups"].append(group)
            if category and category not in unique_inputs[path]["categories"]:
                unique_inputs[path]["categories"].append(category)
        if record["log_group"] == "run_all":
            run_all_records.append(record)
        elif len(sample_records) < max_sample_records:
            sample_records.append(record)
    return {
        "schema": "rtdl.paper_reproduction.xhd.paper_branch_log_index.v1",
        "goal": "Goal5176",
        "status": "paper_branch_log_index_extracted_via_git_objects__input_files_not_present",
        "author_repo": {
            "path": str(repo),
            "rev": rev,
            "head": _git(repo, "rev-parse", rev),
            "root": root,
        },
        "summary": {
            "json_blob_count": len(blobs),
            "parsed_json_count": parsed_count,
            "parse_error_count": len(parse_errors),
            "run_all_record_count": len(run_all_records),
            "sample_record_count": len(sample_records),
            "unique_input_path_count": len(unique_inputs),
            "input_files_available_in_author_repo": 0,
            "input_files_available_on_current_machine": 0,
            "by_log_group": dict(sorted(by_group.items())),
            "by_section_top50": dict(by_section.most_common(50)),
            "by_category_top50": dict(by_category.most_common(50)),
            "by_config_top50": dict(by_config.most_common(50)),
            "by_input_type": dict(sorted(by_input_type.items())),
            "by_num_dims": dict(sorted(by_dims.items())),
            "hd_result_stats": _numeric_stats(hd_values),
            "running_avg_time_stats": _numeric_stats(avg_times),
        },
        "exact_dataset_rule": {
            "author_paper_branch_logs_provide": [
                "input absolute paths",
                "dataset basenames",
                "point counts and Gini indices where present",
                "HDResult and timing fields where present",
                "paper-branch experiment grouping",
            ],
            "author_paper_branch_logs_do_not_provide": [
                "input file bytes",
                "input file hashes",
                "public source snapshot hashes",
                "proof that a reconstructed public dataset is byte-identical",
            ],
            "level_c_requires": [
                "author-provided input files",
                "retained hashes for converted point sets",
                "byte-identical converted point sets",
                "or a documented author script that deterministically regenerates the same point sets from pinned public source files",
            ],
        },
        "parse_errors": parse_errors[:50],
        "unique_inputs_sample": sorted(unique_inputs.values(), key=lambda x: x["path"])[
            :500
        ],
        "run_all_records": run_all_records,
        "sample_records": sample_records,
        "output_bounding": {
            "all_run_all_records_included": True,
            "non_run_all_records_are_sampled": True,
            "max_sample_records": max_sample_records,
        },
        "claim_boundary": {
            "full_paper_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--rev", default="HEAD")
    parser.add_argument("--root", default="expr/for_the_paper/logs")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-sample-records", type=int, default=250)
    args = parser.parse_args()
    index = build_index(
        Path(args.repo),
        args.rev,
        args.root,
        max_sample_records=args.max_sample_records,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    print(
        "wrote",
        out,
        "json_blobs=",
        index["summary"]["json_blob_count"],
        "parsed=",
        index["summary"]["parsed_json_count"],
        "run_all=",
        index["summary"]["run_all_record_count"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
