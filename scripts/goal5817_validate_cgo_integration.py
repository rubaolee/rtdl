#!/usr/bin/env python3
"""Validate that the CGO table and anonymous projection equal Goal5817 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


TASK_LABELS = {"relation": "Relation", "triangle": "Triangle"}
REGIME_LABELS = {
    "DEPLOYMENT_COLD": "cold",
    "PREPARE": "prepare",
    "STEADY_E2E": "steady",
}
COMPARISONS = (
    ("RTDL", "PYOPTIX"),
    ("PYOPTIX", "DIRECT"),
    ("RTDL", "DIRECT"),
)
FORBIDDEN = re.compile(
    r"Goal[0-9]|Lestat|Claude|/root/|C:\\Users|157\.157\.|213\.173\."
    r"|192\.168\.|ssh root|review_goal|internal_docs|owner_directive|POD",
    re.IGNORECASE,
)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root differs: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_row(row: dict) -> dict:
    return {key: row[key] for key in (
        "task", "regime", "numerator", "denominator", "ratio", "ci95",
        "bootstrap_seed", "threshold", "pass", "claim_mode",
    )}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--artifact-performance", type=Path, required=True)
    parser.add_argument("--artifact-manifest", type=Path, required=True)
    parser.add_argument("--tex", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    result = load(args.result)
    artifact = load(args.artifact_performance)
    tex = args.tex.read_text(encoding="utf-8")
    rows = result["formal"]["registered_rows"]
    if len(rows) != 18 or artifact["reported_rows"] != [public_row(row) for row in rows]:
        raise RuntimeError("anonymous reported rows differ from formal result")
    pyoptix = artifact["arm_definitions"]["PYOPTIX"]
    if pyoptix != {
        "distribution": "NVIDIA otk-pyoptix",
        "distribution_version": "9.1.0",
        "optix_api_version": "9.0.0",
        "paper_label": "PyOptiX-compat",
        "role": "OPTIX_9_0_COMPATIBILITY_SCALAR_ARM",
        "stock_current_9_1_api_claimed": False,
    }:
        raise RuntimeError("PyOptiX-compat identity differs")
    lineage = artifact["registration_lineage"]
    if lineage["observed_predecessors"] != [
                {
                    "arm_count": 3,
                    "arms": ["DIRECT", "PYOPTIX", "RTDL"],
                    "block_count": 24,
                    "result_known_before_successor_freeze": True,
                    "rtdl_pyoptix_gate_pass_count": 0,
                    "rtdl_pyoptix_gate_row_count": 6,
                    "target_class": "NVIDIA RTX A4500",
                },
                {
                    "arm_count": 2,
                    "arms": ["PYOPTIX", "RTDL"],
                    "block_count": 16,
                    "result_known_before_successor_freeze": True,
                    "rtdl_pyoptix_gate_pass_count": 2,
                    "rtdl_pyoptix_gate_row_count": 6,
                    "target_class": "NVIDIA RTX 4000 Ada",
                },
            ] \
            or lineage["withdrawn_asymmetric_predecessor"] != {
                "claim_reused": False,
                "disposition": (
                    "WITHDRAWN__AVOIDABLE_BASELINE_SIDE_PYTHON_WORK_"
                    "EXCEEDED_APPARENT_ADVANTAGE"
                ),
                "observed_before_successor_freeze": True,
                "timings_reused": False,
            } \
            or lineage["successor_block_count"] != 18 \
            or lineage["all_listed_predecessor_results_known_before_successor_freeze"] is not True \
            or lineage["successor_frozen_before_own_timings"] is not True \
            or lineage["prior_rows_reused"] is not False \
            or lineage["unconditional_outcome_acceptance"] is not True:
        raise RuntimeError("predecessor-to-18 registration lineage differs")

    row_map = {
        (row["task"], row["regime"], row["numerator"], row["denominator"]): row
        for row in rows
    }
    table_lines = []
    for task in ("relation", "triangle"):
        for regime in ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E"):
            formatted = []
            for numerator, denominator in COMPARISONS:
                row = row_map[(task, regime, numerator, denominator)]
                formatted.append(
                    f"{row['ratio']:.3f} [{row['ci95'][0]:.3f},{row['ci95'][1]:.3f}]"
                )
            gate = row_map[(task, regime, "RTDL", "PYOPTIX")]
            suffix = f"{'pass' if gate['pass'] else 'fail'} {gate['threshold']:.2f}"
            line = (
                f"{TASK_LABELS[task]} & {REGIME_LABELS[regime]} & "
                + " & ".join(formatted) + f" & {suffix} \\\\"
            )
            if tex.count(line) != 1:
                raise RuntimeError(f"paper table row differs: {line}")
            table_lines.append(line)

    normalized_tex = " ".join(tex.split())
    if "324 fresh workers and 7,128" not in normalized_tex \
            or "all 18 reported comparison rows" not in normalized_tex \
            or "setup differences are instead 162--223\\,ms" not in normalized_tex \
            or "It is not a stock/current OptiX-9.1-API arm" not in normalized_tex \
            or "24-block three-arm RTX~A4500 study" not in normalized_tex \
            or "16-block two-arm RTX~4000 Ada study" not in normalized_tex \
            or "withdrawn after the baseline's avoidable Python work" not in normalized_tex:
        raise RuntimeError("paper headline facts differ")
    if FORBIDDEN.search(tex):
        raise RuntimeError("paper source contains identifying/internal token")
    artifact_root = args.artifact_performance.parent.parent
    for path in artifact_root.rglob("*"):
        if path.is_file() and path.name != "manifest.json":
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if FORBIDDEN.search(text):
                raise RuntimeError(f"anonymous artifact contains forbidden token: {path}")

    receipt = {
        "schema": "rtdl.goal5817.cgo_integration_validation.v1",
        "status": "PASS__FORMAL_RESULT_EQUALS_ANONYMOUS_ARTIFACT_AND_PAPER_TABLE",
        "formal_result_file_sha256": sha256(args.result),
        "anonymous_performance_file_sha256": sha256(args.artifact_performance),
        "anonymous_manifest_file_sha256": sha256(args.artifact_manifest),
        "paper_tex_file_sha256": sha256(args.tex),
        "paper_pdf_file_sha256": sha256(args.pdf),
        "formal_row_count": len(rows),
        "anonymous_row_exact_match_count": len(rows),
        "paper_table_row_exact_match_count": len(table_lines),
        "paper_table_comparison_value_count": len(table_lines) * len(COMPARISONS),
        "anonymous_forbidden_token_count": 0,
        "paper_forbidden_token_count": 0,
    }
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(
        receipt, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")).hexdigest()
    args.output.write_bytes(json.dumps(
        receipt, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
