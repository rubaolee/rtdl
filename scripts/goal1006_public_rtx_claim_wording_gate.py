#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "reports" / "goal1005_post_a5000_speedup_candidate_audit_2026-04-26.json"
DATE = "2026-04-26"
GOAL = "Goal1006 public RTX claim wording gate"

MIN_PHASE_SEC_FOR_PUBLIC_SPEEDUP = 0.10
MIN_RATIO_FOR_PUBLIC_SPEEDUP = 1.20


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _classify(row: dict[str, Any]) -> dict[str, Any]:
    recommendation = row.get("recommendation")
    phase = row.get("rtx_native_or_query_phase_sec")
    ratio = row.get("fastest_ratio_baseline_over_rtx")
    warnings = list(row.get("warnings") or [])
    if recommendation != "candidate_for_separate_2ai_public_claim_review":
        return {
            "public_wording_status": "not_public_speedup_candidate",
            "allowed_public_wording": "Do not use as a public RTX speedup claim under current evidence.",
            "reason": "Goal1005 did not classify this row as a speedup-claim candidate.",
        }
    if not isinstance(phase, (int, float)) or not isinstance(ratio, (int, float)):
        return {
            "public_wording_status": "blocked_missing_timing",
            "allowed_public_wording": "Do not use as a public RTX speedup claim until timing evidence is repaired.",
            "reason": "Comparable RTX phase or baseline ratio is missing.",
        }
    if phase < MIN_PHASE_SEC_FOR_PUBLIC_SPEEDUP:
        return {
            "public_wording_status": "candidate_but_needs_larger_scale_repeat",
            "allowed_public_wording": (
                "Internal candidate only. Public docs may say this RTDL sub-path executed on RTX A5000, "
                "but must not quote a speedup until a larger-scale repeat keeps the comparable RTX phase "
                "at or above 100 ms."
            ),
            "reason": "RTX phase is below the 100 ms public-wording floor.",
            "warnings": warnings,
        }
    if ratio < MIN_RATIO_FOR_PUBLIC_SPEEDUP:
        return {
            "public_wording_status": "candidate_but_margin_too_small",
            "allowed_public_wording": "Do not use as a public speedup claim; margin is below the 20% floor.",
            "reason": "Fastest-baseline/RTX ratio is below 1.20.",
            "warnings": warnings,
        }
    return {
        "public_wording_status": "public_review_ready_query_phase_claim",
        "allowed_public_wording": (
            f"On the recorded RTX A5000 run, the bounded `{row['app']} / {row['path_name']}` "
            f"query phase was {ratio:.2f}x faster than the fastest same-semantics non-OptiX baseline "
            f"for the measured sub-path. This is not a whole-app speedup claim."
        ),
        "reason": "Candidate has >=20% margin and comparable RTX phase is at least 100 ms.",
        "warnings": warnings,
    }


def build_gate(source_path: Path = SOURCE) -> dict[str, Any]:
    source = _load_json(source_path)
    rows: list[dict[str, Any]] = []
    for row in source["rows"]:
        decision = _classify(row)
        rows.append(
            {
                "app": row["app"],
                "path_name": row["path_name"],
                "claim_scope": row.get("claim_scope"),
                "non_claim": row.get("non_claim"),
                "goal1005_recommendation": row.get("recommendation"),
                "rtx_phase_key": row.get("rtx_phase_key"),
                "rtx_native_or_query_phase_sec": row.get("rtx_native_or_query_phase_sec"),
                "fastest_baseline": row.get("fastest_baseline"),
                "fastest_baseline_sec": row.get("fastest_baseline_sec"),
                "fastest_ratio_baseline_over_rtx": row.get("fastest_ratio_baseline_over_rtx"),
                "public_speedup_claim_authorized": False,
                **decision,
            }
        )
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["public_wording_status"])
        counts[status] = counts.get(status, 0) + 1
    return {
        "goal": GOAL,
        "date": DATE,
        "source": str(source_path.relative_to(ROOT)),
        "row_count": len(rows),
        "status_counts": counts,
        "public_review_ready_count": counts.get("public_review_ready_query_phase_claim", 0),
        "public_speedup_claim_authorized_count": 0,
        "min_phase_sec_for_public_speedup": MIN_PHASE_SEC_FOR_PUBLIC_SPEEDUP,
        "min_ratio_for_public_speedup": MIN_RATIO_FOR_PUBLIC_SPEEDUP,
        "rows": rows,
        "boundary": (
            "Goal1006 is a wording gate. It does not authorize public speedup claims. It only identifies "
            "which Goal1005 candidates are mature enough to send to a separate 2-AI public wording review."
        ),
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1006 Public RTX Claim Wording Gate",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rows audited: `{payload['row_count']}`",
        f"- public-review-ready query-phase rows: `{payload['public_review_ready_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        f"- minimum phase duration for public speedup wording: `{payload['min_phase_sec_for_public_speedup']}` s",
        f"- minimum ratio for public speedup wording: `{payload['min_ratio_for_public_speedup']}`",
        f"- status counts: `{payload['status_counts']}`",
        "",
        "## Decisions",
        "",
        "| App | Path | RTX phase (s) | Ratio | Status |",
        "|---|---|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | "
            f"{_fmt(row['rtx_native_or_query_phase_sec'])} | "
            f"{_fmt(row['fastest_ratio_baseline_over_rtx'])} | "
            f"`{row['public_wording_status']}` |"
        )
    lines.extend(["", "## Allowed Public Wording Candidates", ""])
    for row in payload["rows"]:
        if row["public_wording_status"] != "public_review_ready_query_phase_claim":
            continue
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                row["allowed_public_wording"],
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "- No row is authorized for front-page wording by this gate alone.",
            "- Rows under 100 ms are intentionally held for larger-scale repeat evidence.",
            "- Whole-app speedups remain disallowed unless a future audit measures whole-app same-semantics timing.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate Goal1005 candidates for public RTX wording review.")
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--output-json", default="docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.md")
    args = parser.parse_args()
    payload = build_gate(Path(args.source))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = to_markdown(payload)
    Path(args.output_md).write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
