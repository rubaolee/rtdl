"""Build the X-HD Figure 7 load-balance source/log audit artifact.

This script is intentionally app-owned. It reads the author repository checkout
and the existing paper-target/log mapping artifacts, then records what is and is
not available for Figure 7 before any RTDL execution work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AUTHOR_REPO = ROOT / ".codex_tmp" / "xhd_author_repo"
DEFAULT_MAPPING = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_target_log_mapping_goal5177_2026-07-08.json"
)
DEFAULT_TARGET_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_target_matrix_2026-07-08.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5292_figure7_load_balance_audit_2026-07-09.json"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_figure(payload: dict[str, Any], figure: str, key: str) -> dict[str, Any]:
    for row in payload.get(key, []):
        if row.get("figure") == figure:
            return row
    raise KeyError(f"{figure} not found in {key}")


def _extract_run_lb_contract(script_text: str) -> dict[str, Any]:
    datasets1: list[str] = []
    datasets2: list[str] = []
    for line in script_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("datasets1=("):
            datasets1 = stripped.removeprefix("datasets1=(").removesuffix(")").split()
        if stripped.startswith("datasets2=("):
            datasets2 = stripped.removeprefix("datasets2=(").removesuffix(")").split()

    pairs = [
        {"input1": left, "input2": right}
        for left, right in zip(datasets1, datasets2, strict=False)
    ]
    return {
        "script_lists_geo_pairs": any(".wkt" in item for item in datasets1 + datasets2),
        "script_lists_graphics_pairs": all(
            item.endswith(".ply") for item in datasets1 + datasets2
        )
        if pairs
        else False,
        "graphics_pair_count": len(pairs),
        "graphics_pairs": pairs,
        "lb_values": [0, 256]
        if '"0"' in script_text and '"256"' in script_text
        else [],
        "variant": "rt" if '"rt"' in script_text else None,
        "execution": "gpu" if '"gpu"' in script_text else None,
        "profiling_flag_present": "-profiling" in script_text,
        "check_flag_present": "-check=true" in script_text,
        "normalize": "false" if '-normalize="$normalize"' in script_text else None,
        "output_pattern": "logs/lb_comparison/lb_${lb}/{out_prefix}/{name1}_{name2}.json",
    }


def _extract_draw_lb_contract(script_text: str) -> dict[str, Any]:
    expected_dirs = []
    for family in ("geo", "graphics"):
        if f'"{family}"' in script_text:
            expected_dirs.extend(
                [
                    f"logs/lb_comparison/lb_0/{family}",
                    f"logs/lb_comparison/lb_256/{family}",
                ]
            )
    return {
        "expects_geo": '"geo"' in script_text,
        "expects_graphics": '"graphics"' in script_text,
        "expected_log_dirs": expected_dirs,
        "stacked_components": ["BVHBuildup", "LBKernel", "RTShader"],
        "iteration_fields_used": [
            "AdjustBVHTime",
            "CUDATime",
            "RTTime",
            "Hits",
            "ComparedPoints",
        ],
        "speedup_formula": "NoLB.RTShader / (LB.RTShader + LB.LBKernel)",
    }


def _scan_lb_logs(author_repo: Path) -> dict[str, Any]:
    roots = [
        author_repo / "expr" / "logs" / "lb_comparison" / "lb_0" / "geo",
        author_repo / "expr" / "logs" / "lb_comparison" / "lb_256" / "geo",
        author_repo / "expr" / "logs" / "lb_comparison" / "lb_0" / "graphics",
        author_repo / "expr" / "logs" / "lb_comparison" / "lb_256" / "graphics",
    ]
    per_dir = {
        str(path.relative_to(author_repo)): len(list(path.rglob("*.json")))
        if path.exists()
        else 0
        for path in roots
    }
    return {
        "total_json_count": sum(per_dir.values()),
        "per_expected_dir_json_count": per_dir,
        "complete_lb0_lb256_matrix_present": all(count > 0 for count in per_dir.values()),
    }


def _summarize_run_all_rt_gpu(author_repo: Path) -> dict[str, Any]:
    base = author_repo / "expr" / "logs" / "end2end" / "rt_gpu"
    rows: list[dict[str, Any]] = []
    for category in ("geo", "graphics"):
        for path in sorted((base / category).glob("*.json")):
            payload = _load_json(path)
            running = payload.get("Running", {})
            repeats = running.get("Repeats", [])
            first_repeat = repeats[0] if repeats else {}
            iterations = first_repeat.get("Iterations", [])
            first_iter = iterations[0] if iterations else {}
            input_files = payload.get("Input", {}).get("Files", [])
            rows.append(
                {
                    "category": category,
                    "file_name": path.name,
                    "hd_result": payload.get("HDResult"),
                    "avg_time_ms": running.get("AvgTime"),
                    "lb": running.get("LB"),
                    "repeat_count": len(repeats),
                    "iteration_count_first_repeat": len(iterations),
                    "profiling": first_repeat.get("Profiling"),
                    "has_rt_time": "RTTime" in first_iter,
                    "has_cuda_time": "CUDATime" in first_iter,
                    "has_offloading_size": "OffloadingSize" in first_iter,
                    "has_adjust_bvh_time": "AdjustBVHTime" in first_iter,
                    "input_basenames": [
                        Path(item.get("Path", "")).name for item in input_files
                    ],
                    "num_points": [item.get("NumPoints") for item in input_files],
                }
            )

    by_category: dict[str, dict[str, Any]] = {}
    for row in rows:
        cat = row["category"]
        bucket = by_category.setdefault(
            cat,
            {
                "record_count": 0,
                "lb_values": set(),
                "records_with_iteration_profiling": 0,
                "records": [],
            },
        )
        bucket["record_count"] += 1
        bucket["lb_values"].add(row["lb"])
        if row["has_rt_time"] and row["has_cuda_time"] and row["has_offloading_size"]:
            bucket["records_with_iteration_profiling"] += 1
        bucket["records"].append(row)

    for bucket in by_category.values():
        bucket["lb_values"] = sorted(v for v in bucket["lb_values"] if v is not None)

    return {
        "record_count": len(rows),
        "by_category": by_category,
        "has_lb0_records": any(row["lb"] == 0 for row in rows),
        "has_lb256_records": any(row["lb"] == 256 for row in rows),
        "has_iteration_metrics": all(
            row["has_rt_time"] and row["has_cuda_time"] and row["has_offloading_size"]
            for row in rows
        )
        if rows
        else False,
    }


def build_figure7_audit(
    *,
    author_repo: Path = DEFAULT_AUTHOR_REPO,
    mapping_path: Path = DEFAULT_MAPPING,
    target_matrix_path: Path = DEFAULT_TARGET_MATRIX,
    date: str = "2026-07-09",
) -> dict[str, Any]:
    mapping = _load_json(mapping_path)
    target_matrix = _load_json(target_matrix_path)
    figure7_mapping = _find_figure(mapping, "Figure 7", "figure_mappings")
    figure7_target = _find_figure(target_matrix, "Figure 7", "figure_targets")

    run_lb_path = author_repo / "expr" / "run_lb.sh"
    draw_lb_path = author_repo / "expr" / "draw_lb.py"
    run_lb_text = _read_text(run_lb_path) if run_lb_path.exists() else ""
    draw_lb_text = _read_text(draw_lb_path) if draw_lb_path.exists() else ""

    run_lb_contract = _extract_run_lb_contract(run_lb_text)
    draw_lb_contract = _extract_draw_lb_contract(draw_lb_text)
    lb_log_scan = _scan_lb_logs(author_repo)
    run_all_rt_gpu = _summarize_run_all_rt_gpu(author_repo)

    script_draw_mismatch = (
        draw_lb_contract["expects_geo"] and not run_lb_contract["script_lists_geo_pairs"]
    )
    missing_lb0 = not run_all_rt_gpu["has_lb0_records"]
    complete_lb_matrix = lb_log_scan["complete_lb0_lb256_matrix_present"]

    status = (
        (
            "figure7_load_balance_source_audit_ready__figure7_not_reproduced__"
            "lb_comparison_logs_missing"
        )
        if not complete_lb_matrix
        else "figure7_load_balance_source_audit_ready__lb_comparison_logs_present"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.figure7_load_balance_audit.v1",
        "goal": "Goal5292",
        "date": date,
        "status": status,
        "matched": None,
        "sources": {
            "author_repo": str(author_repo),
            "author_commit": "7bf41c8442d059c94f4178355c6d5a10571d9658",
            "run_lb": str(run_lb_path),
            "draw_lb": str(draw_lb_path),
            "paper_target_log_mapping": str(mapping_path),
            "paper_target_matrix": str(target_matrix_path),
        },
        "source_hashes": {
            "expr/run_lb.sh": _sha256(run_lb_path),
            "expr/draw_lb.py": _sha256(draw_lb_path),
        },
        "figure7_target": figure7_target,
        "figure7_prior_mapping": figure7_mapping,
        "author_script_contract": {
            "run_lb": run_lb_contract,
            "draw_lb": draw_lb_contract,
            "script_draw_contract_mismatch": script_draw_mismatch,
            "mismatch_note": (
                "draw_lb.py expects both geo and graphics lb_comparison logs, "
                "but run_lb.sh at the pinned main commit lists only graphics pairs."
            )
            if script_draw_mismatch
            else None,
        },
        "checked_in_log_evidence": {
            "lb_comparison": lb_log_scan,
            "run_all_rt_gpu": run_all_rt_gpu,
            "interpretation": (
                "run_all rt_gpu logs contain per-iteration RTTime/CUDATime/"
                "OffloadingSize fields for geo and graphics, but they are LB=256 "
                "records only and do not provide the lb=0 vs lb=256 matrix that "
                "draw_lb.py requires for Figure 7."
            ),
        },
        "decision": {
            "figure7_reproduced": False,
            "lb_comparison_numeric_matrix_available": complete_lb_matrix,
            "run_all_iteration_metrics_available": run_all_rt_gpu["has_iteration_metrics"],
            "run_all_lb0_counterpart_available": not missing_lb0,
            "author_script_available": run_lb_path.exists() and draw_lb_path.exists(),
            "current_blocker": (
                "Author source contains Figure 7 scripts, and run_all contains "
                "profiling-style iteration fields for LB=256 records, but checked-in "
                "lb_comparison lb=0/lb=256 logs are absent. Figure 7 reproduction "
                "requires rerunning or reconstructing the author lb_comparison matrix "
                "with exact or explicitly Level-B inputs."
            ),
            "next_allowed_steps": [
                "If exact HDDatasets inputs are available on a POD, run author run_lb.sh or equivalent commands to regenerate lb_comparison logs.",
                "If exact inputs are unavailable, define a separately named Level-B load-balance diagnostic and do not call it Figure 7 reproduction.",
                "Only after a value/correctness-clean author lb=0/lb=256 matrix exists should RTDL comparison work begin.",
            ],
        },
        "claim_boundary": {
            "figure7_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "rtdl_author_load_balance_parity_claimed": False,
            "lb2048_or_other_substitute_claimed_as_figure7": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-repo", type=Path, default=DEFAULT_AUTHOR_REPO)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--target-matrix", type=Path, default=DEFAULT_TARGET_MATRIX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--date", default="2026-07-09")
    args = parser.parse_args()

    artifact = build_figure7_audit(
        author_repo=args.author_repo,
        mapping_path=args.mapping,
        target_matrix_path=args.target_matrix,
        date=args.date,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
