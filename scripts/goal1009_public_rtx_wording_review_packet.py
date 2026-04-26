#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt

DATE = "2026-04-26"
GOAL = "Goal1009 public RTX sub-path wording review packet"
GOAL1006 = ROOT / "docs" / "reports" / "goal1006_public_rtx_claim_wording_gate_2026-04-26.json"
GOAL1008 = ROOT / "docs" / "reports" / "goal1008_large_repeat_artifact_intake_2026-04-26.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_ratio(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return "unknown"


def _fmt_sec(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.6f}"
    return ""


def _candidate_wording(row: dict[str, Any]) -> str:
    return (
        f"On the recorded RTX A5000 artifact set, the prepared RTDL `{row['app']} / "
        f"{row['path_name']}` query/native sub-path had median RTX phase "
        f"{_fmt_sec(row['rtx_phase_sec'])} s and was {_fmt_ratio(row['ratio'])}x faster "
        f"than the fastest same-semantics non-OptiX baseline for that measured sub-path. "
        "This is not a whole-app speedup claim, not a default-mode claim, and not a "
        "claim about Python-side postprocessing or unrelated app stages."
    )


def build_packet(goal1006_path: Path = GOAL1006, goal1008_path: Path = GOAL1008) -> dict[str, Any]:
    goal1006 = _load_json(goal1006_path)
    goal1008 = _load_json(goal1008_path)
    rows: list[dict[str, Any]] = []

    for source in goal1006["rows"]:
        if source["public_wording_status"] != "public_review_ready_query_phase_claim":
            continue
        public_wording = rt.rtx_public_wording_status(str(source["app"]))
        rows.append(
            {
                "source_goal": "goal1006",
                "app": source["app"],
                "path_name": source["path_name"],
                "current_public_wording_status": public_wording.status,
                "current_public_wording_boundary": public_wording.boundary,
                "rtx_phase_key": source["rtx_phase_key"],
                "rtx_phase_sec": source["rtx_native_or_query_phase_sec"],
                "ratio": source["fastest_ratio_baseline_over_rtx"],
                "fastest_baseline": source["fastest_baseline"],
                "review_status": "candidate_for_2ai_public_wording_review",
                "public_speedup_claim_authorized": False,
            }
        )

    for source in goal1008["rows"]:
        if source["large_repeat_status"] != "timing_floor_cleared_for_separate_2ai_public_wording_review":
            continue
        public_wording = rt.rtx_public_wording_status(str(source["app"]))
        rows.append(
            {
                "source_goal": "goal1008",
                "app": source["app"],
                "path_name": source["path_name"],
                "current_public_wording_status": public_wording.status,
                "current_public_wording_boundary": public_wording.boundary,
                "rtx_phase_key": source["rtx_phase_key"],
                "rtx_phase_sec": source["rtx_phase_sec"],
                "ratio": source["goal1006_ratio"],
                "fastest_baseline": source["goal1006_fastest_baseline"],
                "chosen_artifact": source["chosen_artifact"],
                "review_status": "candidate_for_2ai_public_wording_review",
                "public_speedup_claim_authorized": False,
            }
        )

    blocked = []
    for source in goal1008["rows"]:
        if source["large_repeat_status"] == "still_below_public_review_timing_floor":
            public_wording = rt.rtx_public_wording_status(str(source["app"]))
            blocked.append(
                {
                    "app": source["app"],
                    "path_name": source["path_name"],
                    "current_public_wording_status": public_wording.status,
                    "current_public_wording_boundary": public_wording.boundary,
                    "reason": "Still below the 100 ms public-review timing floor after larger RTX repeats.",
                    "rtx_phase_sec": source["rtx_phase_sec"],
                    "chosen_artifact": source["chosen_artifact"],
                }
            )

    for row in rows:
        row["candidate_public_wording"] = _candidate_wording(row)

    return {
        "goal": GOAL,
        "date": DATE,
        "sources": [
            str(goal1006_path.relative_to(ROOT)),
            str(goal1008_path.relative_to(ROOT)),
        ],
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "candidate_count": len(rows),
        "blocked_count": len(blocked),
        "public_speedup_claim_authorized_count": 0,
        "rows": rows,
        "blocked_rows": blocked,
        "boundary": (
            "Goal1009 packages candidate wording for external review. It does not edit public docs "
            "and does not authorize public speedup claims. The candidate wording is limited to prepared "
            "RTX A5000 query/native sub-paths with same-semantics non-OptiX baselines."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1009 Public RTX Sub-Path Wording Review Packet",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- candidate wording rows: `{payload['candidate_count']}`",
        f"- blocked rows: `{payload['blocked_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Candidate Rows",
        "",
        "| App | Path | RTX phase (s) | Ratio | Fastest baseline | Source |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | {_fmt_sec(row['rtx_phase_sec'])} | "
            f"{_fmt_ratio(row['ratio'])} | `{row['fastest_baseline']}` | `{row['source_goal']}` |"
        )
    lines.extend(["", "## Candidate Wording", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                row["candidate_public_wording"],
                "",
            ]
        )
    lines.extend(["## Blocked Rows", ""])
    for row in payload["blocked_rows"]:
        lines.append(
            f"- `{row['app']} / {row['path_name']}` remains blocked: {row['reason']} "
            f"median RTX phase `{_fmt_sec(row['rtx_phase_sec'])}` s. "
            f"Current public wording status: `{row['current_public_wording_status']}`."
        )
    lines.extend(
        [
            "",
            "## Reviewer Questions",
            "",
            "- Is every candidate wording line accurately scoped to a prepared query/native sub-path?",
            "- Does any line imply whole-app, default-mode, Python-postprocess, or broad RT-core acceleration?",
            "- Are the blocked rows correctly excluded from public wording?",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1009 public RTX wording review packet.")
    parser.add_argument("--goal1006", default=str(GOAL1006))
    parser.add_argument("--goal1008", default=str(GOAL1008))
    parser.add_argument("--output-json", default="docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.md")
    args = parser.parse_args()
    payload = build_packet(Path(args.goal1006), Path(args.goal1008))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = to_markdown(payload)
    Path(args.output_md).write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
