"""Build the X-HD Figure 8 radius-growing strategy source/log audit artifact.

This script is app-owned. It inspects the pinned author checkout and existing
paper target/log mapping artifacts before any RTDL execution work. The goal is
to determine whether Figure 8 already has a reproducible author-side
radius-strategy denominator in checked-in source/logs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    / "xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json"
)

EXPECTED_VARIANTS = ("rt_gpu_radius_add", "rt_gpu_radius_double", "rt_gpu_radius_adaptive")
EXPECTED_RADIUS_VALUES = ("add", "double", "adaptive")
EXPECTED_CATEGORIES = ("geo", "graphics")


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


def _parse_bash_array(line: str) -> list[str]:
    match = re.search(r"\((.*?)\)", line)
    if not match:
        return []
    return [item.strip().strip('"').strip("'") for item in match.group(1).split() if item.strip()]


def _extract_run_radius_contract(script_text: str) -> dict[str, Any]:
    functions: dict[str, dict[str, Any]] = {}
    current: str | None = None
    pending_left: list[str] = []
    pending_right: list[str] = []

    for raw_line in script_text.splitlines():
        line = raw_line.strip()
        if line.startswith("function run_all_geo"):
            current = "geo"
            pending_left = []
            pending_right = []
            functions[current] = {"pairs": []}
            continue
        if line.startswith("function run_all_graphics"):
            current = "graphics"
            pending_left = []
            pending_right = []
            functions[current] = {"pairs": []}
            continue
        if current is None:
            continue
        if line.startswith("datasets1=("):
            pending_left = _parse_bash_array(line)
        elif line.startswith("datasets2=("):
            pending_right = _parse_bash_array(line)
            functions[current]["pairs"] = [
                {"input1": left, "input2": right}
                for left, right in zip(pending_left, pending_right, strict=False)
            ]

    return {
        "calls_run_all_geo": "run_all_geo" in script_text.splitlines()[-5:],
        "calls_run_all_graphics": "run_all_graphics" in script_text.splitlines()[-5:],
        "categories": {
            category: {
                "pair_count": len(info.get("pairs", [])),
                "pairs": info.get("pairs", []),
            }
            for category, info in functions.items()
        },
        "radius_values": [
            value for value in EXPECTED_RADIUS_VALUES if f'"{value}"' in script_text
        ],
        "variant": "rt" if '"rt"' in script_text else None,
        "execution": "gpu" if '"gpu"' in script_text else None,
        "normalize": "false" if '"false"' in script_text else None,
        "check": "false" if "-check=false" in script_text else None,
        "repeat": 1 if "-repeat 1" in script_text else None,
        "output_pattern": "logs/tune_radius/${variant}_${execution}_radius_${radius}/{out_prefix}/{name1}_{name2}.json",
    }


def _extract_draw_radius_contract(script_text: str) -> dict[str, Any]:
    return {
        "expected_variants": [
            variant for variant in EXPECTED_VARIANTS if variant in script_text
        ],
        "expected_labels": [
            label
            for label in ("Add by Diagonal", "Double Radius", "Our Method")
            if label in script_text
        ],
        "expects_geo": 'base_dir="geo"' in script_text or 'base_dir = "geo"' in script_text,
        "expects_graphics": 'base_dir="graphics"' in script_text
        or 'base_dir = "graphics"' in script_text,
        "expected_log_dirs": [
            f"logs/tune_radius/{variant}/{category}"
            for variant in EXPECTED_VARIANTS
            for category in EXPECTED_CATEGORIES
        ],
        "metric": "Running.AvgTime" if "Running.AvgTime" in script_text else None,
        "output_pdf": "tune_radius.pdf" if "tune_radius.pdf" in script_text else None,
    }


def _scan_tune_radius_logs(author_repo: Path) -> dict[str, Any]:
    base = author_repo / "expr" / "logs" / "tune_radius"
    per_dir: dict[str, int] = {}
    examples: list[dict[str, Any]] = []
    for variant in EXPECTED_VARIANTS:
        for category in EXPECTED_CATEGORIES:
            path = base / variant / category
            count = len(list(path.rglob("*.json"))) if path.exists() else 0
            rel = path.relative_to(author_repo)
            per_dir[str(rel)] = count
            if count and len(examples) < 5:
                for json_path in sorted(path.rglob("*.json"))[: 5 - len(examples)]:
                    payload = _load_json(json_path)
                    examples.append(
                        {
                            "relative_path": str(json_path.relative_to(author_repo)),
                            "hd_result": payload.get("HDResult"),
                            "avg_time_ms": payload.get("Running", {}).get("AvgTime"),
                            "tune_radius": payload.get("Running", {}).get("TuneRadius"),
                        }
                    )

    total = sum(per_dir.values())
    return {
        "root_exists": base.exists(),
        "total_json_count": total,
        "per_expected_dir_json_count": per_dir,
        "complete_variant_category_matrix_present": all(count > 0 for count in per_dir.values()),
        "example_records": examples,
    }


def build_figure8_audit(
    *,
    author_repo: Path = DEFAULT_AUTHOR_REPO,
    mapping_path: Path = DEFAULT_MAPPING,
    target_matrix_path: Path = DEFAULT_TARGET_MATRIX,
    date: str = "2026-07-09",
) -> dict[str, Any]:
    mapping = _load_json(mapping_path)
    target_matrix = _load_json(target_matrix_path)
    figure8_mapping = _find_figure(mapping, "Figure 8", "figure_mappings")
    figure8_target = _find_figure(target_matrix, "Figure 8", "figure_targets")

    run_radius_path = author_repo / "expr" / "run_radius_tuning.sh"
    draw_radius_path = author_repo / "expr" / "draw_tune_radius.py"
    run_radius_text = _read_text(run_radius_path) if run_radius_path.exists() else ""
    draw_radius_text = _read_text(draw_radius_path) if draw_radius_path.exists() else ""

    run_contract = _extract_run_radius_contract(run_radius_text)
    draw_contract = _extract_draw_radius_contract(draw_radius_text)
    log_scan = _scan_tune_radius_logs(author_repo)

    script_available = run_radius_path.exists() and draw_radius_path.exists()
    numeric_matrix_available = log_scan["complete_variant_category_matrix_present"]
    run_all_covered = figure8_mapping.get("record_summary", {}).get("record_count", 0) > 0

    status = (
        "figure8_radius_strategy_audit_ready__figure8_not_reproduced__tune_radius_logs_missing"
        if not numeric_matrix_available
        else "figure8_radius_strategy_audit_ready__tune_radius_logs_present"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.figure8_radius_strategy_audit.v1",
        "goal": "Goal5293",
        "date": date,
        "status": status,
        "matched": None,
        "sources": {
            "author_repo": str(author_repo),
            "author_commit": "7bf41c8442d059c94f4178355c6d5a10571d9658",
            "run_radius_tuning": str(run_radius_path),
            "draw_tune_radius": str(draw_radius_path),
            "paper_target_log_mapping": str(mapping_path),
            "paper_target_matrix": str(target_matrix_path),
        },
        "source_hashes": {
            "expr/run_radius_tuning.sh": _sha256(run_radius_path),
            "expr/draw_tune_radius.py": _sha256(draw_radius_path),
        },
        "figure8_target": figure8_target,
        "figure8_prior_mapping": figure8_mapping,
        "author_script_contract": {
            "run_radius_tuning": run_contract,
            "draw_tune_radius": draw_contract,
            "script_draw_contract_aligned": (
                set(run_contract["radius_values"]) == set(EXPECTED_RADIUS_VALUES)
                and set(draw_contract["expected_variants"]) == set(EXPECTED_VARIANTS)
                and draw_contract["expects_geo"]
                and draw_contract["expects_graphics"]
            ),
        },
        "checked_in_log_evidence": {
            "tune_radius": log_scan,
            "run_all_mapping": {
                "coverage_status": figure8_mapping.get("coverage_status"),
                "record_count": figure8_mapping.get("record_summary", {}).get("record_count", 0),
                "interpretation": figure8_mapping.get("interpretation"),
            },
        },
        "decision": {
            "figure8_reproduced": False,
            "tune_radius_numeric_matrix_available": numeric_matrix_available,
            "run_all_radius_strategy_evidence_available": run_all_covered,
            "author_script_available": script_available,
            "current_blocker": (
                "Author source contains run_radius_tuning.sh and draw_tune_radius.py "
                "for add/double/adaptive radius strategies, but checked-in "
                "logs/tune_radius has no JSON records. The paper-branch run_all log "
                "mapping also identifies no explicit radius-growing strategy records. "
                "Figure 8 reproduction requires regenerating or recovering the "
                "tune_radius numeric matrix with exact or explicitly Level-B inputs."
            ),
            "next_allowed_steps": [
                "If exact HDDatasets inputs are available on a POD, run author run_radius_tuning.sh or equivalent commands to regenerate tune_radius logs.",
                "If exact inputs are unavailable, define a separately named Level-B radius-strategy diagnostic and do not call it Figure 8 reproduction.",
                "Only after an author add/double/adaptive numeric matrix exists should RTDL radius-strategy comparison work begin.",
            ],
        },
        "claim_boundary": {
            "figure8_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "rtdl_author_radius_strategy_parity_claimed": False,
            "run_all_logs_claimed_as_figure8": False,
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

    artifact = build_figure8_audit(
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
