"""Build the X-HD Figure 10 scalability / overlap source-log audit artifact."""

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
    / "xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json"
)

EXPECTED_VARIANTS = ("eb_gpu", "nn_gpu", "clover_gpu", "rt_gpu")
EXPECTED_RUN_VARIANTS = ("eb", "nn", "clover", "rt")
EXPECTED_SWEEPS = ("scal_vary_size", "scal_vary_translate")


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


def _extract_numeric_for_values(script_text: str, variable: str) -> list[float | int]:
    match = re.search(rf"for\s+{re.escape(variable)}\s+in\s+([^;]+);\s+do", script_text)
    if not match:
        return []
    values: list[float | int] = []
    for token in match.group(1).split():
        if "." in token:
            values.append(float(token))
        else:
            values.append(int(token))
    return values


def _extract_run_scalability_contract(script_text: str) -> dict[str, Any]:
    size_values = _extract_numeric_for_values(script_text, "size")
    translate_values = _extract_numeric_for_values(script_text, "translate")
    return {
        "dataset": "all_nodes.wkt" if "all_nodes.wkt" in script_text else None,
        "input_type": "wkt" if '"wkt"' in script_text else None,
        "n_dims": 3 if '"wkt" 3' in script_text else None,
        "run_variants": [
            variant for variant in EXPECTED_RUN_VARIANTS if f" {variant};" in script_text or f" {variant} " in script_text
        ],
        "execution": "gpu" if '"gpu"' in script_text else None,
        "size_values": size_values,
        "translate_values": translate_values,
        "size_sweep_count": len(size_values),
        "translate_sweep_count": len(translate_values),
        "size_fixed_translate": "0.005" if '"0.005"' in script_text else None,
        "translate_fixed_limit": 10000000 if "10000000" in script_text else None,
        "output_pattern": "logs/scalability/${variant}_${execution}/{out_prefix}/{name1}_{name2}_limit_${limit}_translate_${translate}.json",
        "check": "false" if "-check=false" in script_text else None,
        "repeat": 1 if "-repeat 1" in script_text else None,
    }


def _extract_draw_scalability_contract(script_text: str) -> dict[str, Any]:
    return {
        "expected_variants": [variant for variant in EXPECTED_VARIANTS if variant in script_text],
        "expected_labels": [
            label for label in ("EB", "NN-KD", "NN-Clover", "X-HD") if label in script_text
        ],
        "expects_count_subplot": "Varying the Scale of Datasets" in script_text
        and "Count" in script_text,
        "expects_translate_subplot": "Sensitivity to Overlap" in script_text
        and "Translate" in script_text,
        "expected_log_dirs": [
            f"logs/scalability/{variant}/{sweep}"
            for variant in EXPECTED_VARIANTS
            for sweep in EXPECTED_SWEEPS
        ],
        "count_x_field": "Input.Files[0].NumPoints"
        if "Input.Files" in script_text and "NumPoints" in script_text
        else None,
        "translate_x_field": "Input.Translate" if "Input.Translate" in script_text else None,
        "metric": "Running.AvgTime" if "Running.AvgTime" in script_text else None,
        "output_pdf": "scalability.pdf" if "scalability.pdf" in script_text else None,
    }


def _scan_scalability_logs(author_repo: Path) -> dict[str, Any]:
    base = author_repo / "expr" / "logs" / "scalability"
    per_dir: dict[str, int] = {}
    examples: list[dict[str, Any]] = []
    for variant in EXPECTED_VARIANTS:
        for sweep in EXPECTED_SWEEPS:
            path = base / variant / sweep
            count = len(list(path.rglob("*.json"))) if path.exists() else 0
            per_dir[str(path.relative_to(author_repo))] = count
            if count and len(examples) < 5:
                for json_path in sorted(path.rglob("*.json"))[: 5 - len(examples)]:
                    payload = _load_json(json_path)
                    input_files = payload.get("Input", {}).get("Files", [])
                    examples.append(
                        {
                            "relative_path": str(json_path.relative_to(author_repo)),
                            "hd_result": payload.get("HDResult"),
                            "avg_time_ms": payload.get("Running", {}).get("AvgTime"),
                            "translate": payload.get("Input", {}).get("Translate"),
                            "num_points": [item.get("NumPoints") for item in input_files],
                        }
                    )

    total = sum(per_dir.values())
    return {
        "root_exists": base.exists(),
        "total_json_count": total,
        "per_expected_dir_json_count": per_dir,
        "complete_variant_sweep_matrix_present": all(count > 0 for count in per_dir.values()),
        "example_records": examples,
    }


def build_figure10_audit(
    *,
    author_repo: Path = DEFAULT_AUTHOR_REPO,
    mapping_path: Path = DEFAULT_MAPPING,
    target_matrix_path: Path = DEFAULT_TARGET_MATRIX,
    date: str = "2026-07-09",
) -> dict[str, Any]:
    mapping = _load_json(mapping_path)
    target_matrix = _load_json(target_matrix_path)
    figure10_mapping = _find_figure(mapping, "Figure 10", "figure_mappings")
    figure10_target = _find_figure(target_matrix, "Figure 10", "figure_targets")

    run_path = author_repo / "expr" / "run_scalability.sh"
    draw_path = author_repo / "expr" / "draw_scalability.py"
    run_text = _read_text(run_path) if run_path.exists() else ""
    draw_text = _read_text(draw_path) if draw_path.exists() else ""

    run_contract = _extract_run_scalability_contract(run_text)
    draw_contract = _extract_draw_scalability_contract(draw_text)
    log_scan = _scan_scalability_logs(author_repo)

    numeric_matrix_available = log_scan["complete_variant_sweep_matrix_present"]
    run_all_record_count = figure10_mapping.get("record_summary", {}).get("record_count", 0)

    status = (
        "figure10_scalability_overlap_audit_ready__figure10_not_reproduced__scalability_logs_missing"
        if not numeric_matrix_available
        else "figure10_scalability_overlap_audit_ready__scalability_logs_present"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.figure10_scalability_overlap_audit.v1",
        "goal": "Goal5294",
        "date": date,
        "status": status,
        "matched": None,
        "sources": {
            "author_repo": str(author_repo),
            "author_commit": "7bf41c8442d059c94f4178355c6d5a10571d9658",
            "run_scalability": str(run_path),
            "draw_scalability": str(draw_path),
            "paper_target_log_mapping": str(mapping_path),
            "paper_target_matrix": str(target_matrix_path),
        },
        "source_hashes": {
            "expr/run_scalability.sh": _sha256(run_path),
            "expr/draw_scalability.py": _sha256(draw_path),
        },
        "figure10_target": figure10_target,
        "figure10_prior_mapping": figure10_mapping,
        "author_script_contract": {
            "run_scalability": run_contract,
            "draw_scalability": draw_contract,
            "script_draw_contract_aligned": (
                set(run_contract["run_variants"]) == set(EXPECTED_RUN_VARIANTS)
                and set(draw_contract["expected_variants"]) == set(EXPECTED_VARIANTS)
                and draw_contract["expects_count_subplot"]
                and draw_contract["expects_translate_subplot"]
            ),
        },
        "checked_in_log_evidence": {
            "scalability": log_scan,
            "run_all_mapping": {
                "coverage_status": figure10_mapping.get("coverage_status"),
                "record_count": run_all_record_count,
                "interpretation": figure10_mapping.get("interpretation"),
                "missing_evidence": figure10_mapping.get("missing_evidence", []),
            },
        },
        "decision": {
            "figure10_reproduced": False,
            "scalability_numeric_matrix_available": numeric_matrix_available,
            "run_all_workload_family_records_available": run_all_record_count > 0,
            "run_all_scale_overlap_labels_available": False,
            "author_script_available": run_path.exists() and draw_path.exists(),
            "current_blocker": (
                "Author source contains run_scalability.sh and draw_scalability.py "
                "for size and translate/overlap sweeps, but checked-in "
                "logs/scalability has no JSON records. The paper-branch run_all "
                "logs have workload-family records, but they do not identify the "
                "Figure 10 scale/overlap subsets or overlap diagnostics. Figure 10 "
                "reproduction requires regenerating or recovering the scalability "
                "numeric matrix with exact or explicitly Level-B inputs."
            ),
            "next_allowed_steps": [
                "If exact all_nodes/HDDatasets inputs are available on a POD, run author run_scalability.sh or equivalent commands to regenerate scalability logs.",
                "If exact inputs are unavailable, define a separately named Level-B scalability/overlap diagnostic and do not call it Figure 10 reproduction.",
                "Only after an author size/translate numeric matrix exists should RTDL scalability or overlap comparison work begin.",
            ],
        },
        "claim_boundary": {
            "figure10_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "rtdl_author_scalability_overlap_parity_claimed": False,
            "run_all_workload_families_claimed_as_figure10": False,
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

    artifact = build_figure10_audit(
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
