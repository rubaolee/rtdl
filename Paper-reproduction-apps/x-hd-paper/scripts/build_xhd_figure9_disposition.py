#!/usr/bin/env python3
"""Build the Goal5287 Figure 9 disposition artifact.

The output consolidates Goal5284-5286 evidence and decides whether the current
Figure 9 line can be called reproduced.  It intentionally does not run an RTDL
route and does not compute an author-vs-RTDL performance ratio.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"could not parse JSON: {path}") from exc


def build_figure9_disposition(
    *,
    auto_tune_matrix_path: Path,
    source_audit_path: Path,
    branch_audit_path: Path,
    date: str,
) -> dict[str, Any]:
    auto_tune = _load_json(auto_tune_matrix_path)
    source = _load_json(source_audit_path)
    branches = _load_json(branch_audit_path)

    plot_expected = source["figure9_plot_script"]["expected_variants"]
    run_all_observed = source["run_all_vs_plot_script"]["observed_configs"]
    missing_variants = source["run_all_vs_plot_script"]["missing_plot_variants_from_run_all_logs"]
    any_branch_complete = branches["decision"]["any_branch_has_all_expected_figure9_variants"]

    claim_boundary = {
        "figure9_reproduced": False,
        "figure9_performance_ratio_claimed": False,
        "rtdl_route_result_claimed": False,
        "checked_in_pdf_treated_as_reproduction": False,
        "training_sweep_treated_as_figure9": False,
        "full_paper_reproduction_claimed": False,
    }
    close_current_line = (
        auto_tune["figure9_reproduction_decision"]["figure9_reproduced"] is False
        and source["decision"]["figure9_reproduced"] is False
        and branches["decision"]["figure9_reproduced"] is False
        and not any_branch_complete
        and bool(missing_variants)
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5287.figure9_disposition.v1",
        "goal": "Goal5287",
        "date": date,
        "status": "figure9_closed_current_line_author_denominator_missing",
        "inputs": {
            "auto_tune_matrix": str(auto_tune_matrix_path),
            "source_audit": str(source_audit_path),
            "branch_audit": str(branch_audit_path),
        },
        "evidence_summary": {
            "auto_tune_records": auto_tune["coverage"]["auto_tune_record_count"],
            "auto_tune_unique_pairs": auto_tune["coverage"]["unique_pair_count"],
            "run_all_observed_configs": run_all_observed,
            "plot_expected_variants": plot_expected,
            "missing_plot_variants": missing_variants,
            "plot_script": source["figure9_plot_script"]["path"],
            "plot_script_saves_pdf": source["figure9_plot_script"]["saves_pdf"],
            "checked_in_pdf": branches["branches"]["paper"]["figure9_files"]["checked_in_pdf"],
            "main_run_all_records": branches["branches"]["main"]["run_all_auto_tune"]["record_count"],
            "hybrid_run_all_records": branches["branches"]["hybrid"]["run_all_auto_tune"]["record_count"],
            "training_sweeps_exist": bool(source["training_sweeps"]["logs"]["n_points_cell_values"]),
            "training_sweeps_same_denominator_as_plot": False,
        },
        "decision": {
            "figure9_reproduced": False,
            "close_current_figure9_line": close_current_line,
            "why_closed": [
                "The Figure-9-like plot script expects four auto-tune variants.",
                "Current run_all/auto_tune logs provide only two of those variants.",
                "The missing variants are not present on pinned main or hybrid branches.",
                "The checked-in auto-tune.pdf is a rendered artifact, not a reproducible denominator.",
                "Training sweeps are separate logs and are not promoted to Figure 9 without an externally reviewed mapping.",
            ],
            "allowed_reopen_conditions": [
                "Regenerate or recover the two missing run_all auto_tune variants for the plotted workloads.",
                "Produce an externally reviewed mapping from logs/train sweeps to the checked-in auto-tune.pdf quantities.",
                "Obtain external review accepting a narrower Figure 9 question with explicit denominator limits.",
            ],
            "next_recommended_full_paper_work": (
                "Move to another full-paper blocker with a complete author-side denominator, "
                "or explicitly authorize a regeneration goal for Figure 9 missing variants."
            ),
            "forbidden_summaries": [
                "Figure 9 reproduced",
                "all auto-tune variants recovered",
                "checked-in PDF equals reproducible Figure 9",
                "training sweep equals Figure 9",
                "RTDL Figure 9 speedup or parity",
            ],
        },
        "claim_boundary": claim_boundary,
        "matched": close_current_line and all(value is False for value in claim_boundary.values()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 9 disposition artifact.")
    parser.add_argument("--auto-tune-matrix", required=True)
    parser.add_argument("--source-audit", required=True)
    parser.add_argument("--branch-audit", required=True)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    artifact = build_figure9_disposition(
        auto_tune_matrix_path=Path(args.auto_tune_matrix),
        source_audit_path=Path(args.source_audit),
        branch_audit_path=Path(args.branch_audit),
        date=args.date,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "status": artifact["status"], "matched": artifact["matched"]}, indent=2))
    return 0 if artifact["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
