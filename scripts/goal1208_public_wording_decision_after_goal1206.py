#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
DEFAULT_INTAKE = ROOT / "docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.json"
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md"
MIN_PUBLIC_RATIO = 1.2


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_sec(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _fmt_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}x"


def _db_decision(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [float(row["ratio_embree_over_optix"]) for row in rows if row.get("ratio_embree_over_optix") is not None]
    min_ratio = min(ratios) if ratios else None
    positive = bool(min_ratio is not None and min_ratio >= MIN_PUBLIC_RATIO)
    return {
        "app": "database_analytics",
        "path_name": "prepared_db_compact_summary",
        "decision": "propose_public_wording_reviewed" if positive else "keep_public_wording_blocked_no_positive_speedup",
        "status_to_apply": "public_wording_reviewed" if positive else "public_wording_blocked",
        "raw_ratio_embree_over_optix": min_ratio,
        "copies": [row["copies"] for row in rows],
        "candidate_public_wording": (
            "RTDL's prepared DB compact-summary RTX sub-path is repaired at 100k and 300k and measured above the public-ratio threshold versus same-scale Embree."
            if positive
            else "RTDL's prepared DB compact-summary RTX sub-path is repaired at 100k and 300k, but the measured 1.12x-1.16x advantage is below the 1.2x public speedup threshold."
        ),
        "boundary": "Only prepared compact-summary scan/group/count/sum traversal is covered; no DBMS, SQL engine, full dashboard, row-materialization, Python setup, or whole-app speedup claim is allowed.",
    }


def _road_decision(row: dict[str, Any]) -> dict[str, Any]:
    ratio = row.get("ratio_embree_over_optix")
    positive = bool(row.get("same_scale_public_positive_candidate") and ratio is not None and ratio >= MIN_PUBLIC_RATIO)
    return {
        "app": "road_hazard_screening",
        "path_name": "prepared_native_road_hazard_summary",
        "decision": "propose_public_wording_reviewed" if positive else "keep_public_wording_blocked_no_positive_speedup",
        "status_to_apply": "public_wording_reviewed" if positive else "public_wording_blocked",
        "embree_phase_sec": row.get("embree_sec"),
        "optix_phase_sec": row.get("optix_sec"),
        "raw_ratio_embree_over_optix": ratio,
        "candidate_public_wording": (
            f"RTDL's prepared native road-hazard RTX sub-path measured {_fmt_sec(row.get('optix_sec'))} s and {_fmt_ratio(ratio)} versus the reviewed same-scale Embree sub-path at 40k copies."
            if positive
            else "No positive public RTX speedup wording is authorized for road_hazard_screening from Goal1206 evidence."
        ),
        "boundary": "Only the prepared native segment/polygon road-hazard summary traversal and threshold-count continuation are covered; default app behavior, GIS/routing, row materialization, Python setup, and whole-app speedup remain outside this wording.",
    }


def _jaccard_decision(rows: list[dict[str, Any]]) -> dict[str, Any]:
    safe = next((row for row in rows if row.get("public_safe")), None)
    diagnostic = next((row for row in rows if row.get("diagnostic_only")), None)
    ready = bool(safe and safe.get("parity_vs_cpu") is True and diagnostic and diagnostic.get("parity_vs_cpu") is False)
    return {
        "app": "polygon_set_jaccard",
        "path_name": "native_assisted_lsi_pip_candidate_discovery",
        "decision": "correctness_ready_no_speedup_wording" if ready else "blocked_or_incomplete",
        "status_to_apply": "public_correctness_ready_speedup_blocked" if ready else "public_wording_blocked",
        "raw_ratio_embree_over_optix": None,
        "candidate_public_wording": (
            "RTDL's polygon-set Jaccard OptiX path has public-safe chunk correctness evidence at chunk 512; no positive RTX speedup wording is authorized because this packet has no same-scale Embree speedup comparison and chunk 64 remains diagnostic-only/parity-failing."
            if ready
            else "No public polygon-set Jaccard promotion is authorized from Goal1206 evidence."
        ),
        "boundary": "Only public-safe chunk correctness/readiness is covered; exact area refinement, Jaccard whole-app speedup, arbitrary chunk sizes, row materialization, and Python postprocess are outside this wording.",
    }


def build_packet(intake_path: Path = DEFAULT_INTAKE) -> dict[str, Any]:
    intake = _load(intake_path)
    if not intake.get("valid"):
        raise ValueError(f"{intake_path} is not a valid intake")
    rows = [
        _db_decision(intake["database_analytics"]),
        _road_decision(intake["road_hazard_screening"]),
        _jaccard_decision(intake["polygon_set_jaccard"]),
    ]
    return {
        "goal": "Goal1208 public wording decision after Goal1206",
        "date": DATE,
        "source_intake": str(intake_path.relative_to(ROOT)),
        "source_consensus": "docs/reports/goal1206_two_ai_consensus_2026-05-01.md",
        "min_public_ratio": MIN_PUBLIC_RATIO,
        "public_speedup_claim_authorized_count": 0,
        "public_speedup_claims_applied_by_this_packet": 0,
        "proposed_public_wording_reviewed_apps": [row["app"] for row in rows if row["status_to_apply"] == "public_wording_reviewed"],
        "proposed_public_wording_blocked_apps": [row["app"] for row in rows if row["status_to_apply"] == "public_wording_blocked"],
        "proposed_correctness_ready_speedup_blocked_apps": [
            row["app"] for row in rows if row["status_to_apply"] == "public_correctness_ready_speedup_blocked"
        ],
        "rows": rows,
        "boundary": (
            "Goal1208 is a public-wording decision packet only. It proposes narrow wording states "
            "from accepted Goal1206 evidence but does not edit public docs, authorize release, or "
            "by itself authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1208 Public Wording Decision After Goal1206",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- source intake: `{payload['source_intake']}`",
        f"- source consensus: `{payload['source_consensus']}`",
        f"- minimum positive public ratio: `{payload['min_public_ratio']}`",
        f"- proposed reviewed apps: `{', '.join(payload['proposed_public_wording_reviewed_apps']) or 'none'}`",
        f"- correctness-ready but speedup-blocked apps: `{', '.join(payload['proposed_correctness_ready_speedup_blocked_apps']) or 'none'}`",
        f"- blocked apps: `{', '.join(payload['proposed_public_wording_blocked_apps']) or 'none'}`",
        f"- public speedup claims authorized by this packet: `{payload['public_speedup_claim_authorized_count']}`",
        f"- public speedup claims applied by this packet: `{payload['public_speedup_claims_applied_by_this_packet']}`",
        "",
        "## Decisions",
        "",
        "| App | Path | Decision | Ratio |",
        "| --- | --- | --- | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['decision']}` | `{_fmt_ratio(row['raw_ratio_embree_over_optix'])}` |"
        )
    lines.extend(["", "## Candidate Public Wording", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                row["candidate_public_wording"],
                "",
                f"Boundary: {row['boundary']}",
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1208 public wording decision packet.")
    parser.add_argument("--input-json", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_packet(args.input_json)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": True, "reviewed": payload["proposed_public_wording_reviewed_apps"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
