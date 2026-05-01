#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-28"
GOAL = "Goal1067 scale-contract repair audit"

HAUSDORFF_DRY_RUN = ROOT / "docs/reports/goal1067_hausdorff_scale_contract_dry_run_2026-04-28.json"
BARNES_200K_DRY_RUN = ROOT / "docs/reports/goal1067_barnes_hut_scale_contract_dry_run_2026-04-28.json"
BARNES_1M_DRY_RUN = ROOT / "docs/reports/goal1067_barnes_hut_scale_contract_1m_dry_run_2026-04-28.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _timing(payload: dict[str, Any], key: str) -> float:
    return float(payload["scenario"]["timings_sec"][key])


def build_audit() -> dict[str, Any]:
    hausdorff = _load(HAUSDORFF_DRY_RUN)
    barnes_200k = _load(BARNES_200K_DRY_RUN)
    barnes_1m = _load(BARNES_1M_DRY_RUN)

    rows = [
        {
            "app": "hausdorff_distance",
            "path_name": "directed_threshold_prepared",
            "input_artifact": str(HAUSDORFF_DRY_RUN.relative_to(ROOT)),
            "tested_scale": {
                "copies": hausdorff["parameters"]["copies"],
                "point_count_a": hausdorff["scenario"]["result"]["point_count_a"],
                "point_count_b": hausdorff["scenario"]["result"]["point_count_b"],
                "radius": hausdorff["scenario"]["result"]["radius"],
            },
            "cpu_reference_total_sec": _timing(hausdorff, "cpu_reference_total_sec"),
            "input_build_sec": _timing(hausdorff, "input_build_sec"),
            "decision": "blocked_scale_contract_not_repaired",
            "reason": (
                "The authored Hausdorff fixture uses an analytic tiled oracle, so "
                "raising copies to 20,000 creates 80k logical points per side but "
                "does not create a meaningful same-semantics CPU speed baseline."
            ),
            "next_local_action": (
                "Do not pod-rerun this as a public speedup candidate. Either keep it "
                "as an RTX capability/parity path or design a separate non-analytic "
                "threshold-decision benchmark contract with bounded validation."
            ),
            "pod_policy": "no_pod_until_benchmark_contract_changes",
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared",
            "input_artifacts": [
                str(BARNES_200K_DRY_RUN.relative_to(ROOT)),
                str(BARNES_1M_DRY_RUN.relative_to(ROOT)),
            ],
            "tested_scales": [
                {
                    "body_count": barnes_200k["scenario"]["result"]["body_count"],
                    "covered_body_count": barnes_200k["scenario"]["result"]["covered_body_count"],
                    "cpu_reference_total_sec": _timing(barnes_200k, "cpu_reference_total_sec"),
                    "input_build_sec": _timing(barnes_200k, "input_build_sec"),
                    "radius": barnes_200k["scenario"]["result"]["radius"],
                },
                {
                    "body_count": barnes_1m["scenario"]["result"]["body_count"],
                    "covered_body_count": barnes_1m["scenario"]["result"]["covered_body_count"],
                    "cpu_reference_total_sec": _timing(barnes_1m, "cpu_reference_total_sec"),
                    "input_build_sec": _timing(barnes_1m, "input_build_sec"),
                    "radius": barnes_1m["scenario"]["result"]["radius"],
                },
            ],
            "recommended_cloud_scale": {
                "body_count": barnes_1m["scenario"]["result"]["body_count"],
                "radius": barnes_1m["scenario"]["result"]["radius"],
                "mode": "optix",
                "skip_validation": True,
                "validation_reference": "Use the saved dry-run semantic validation and run one smaller validated RTX pass before large timing repeats.",
            },
            "decision": "pod_candidate_after_review",
            "reason": (
                "The 1M-body local dry-run keeps the same node-coverage decision, "
                "separates input build from CPU reference, and produces a non-trivial "
                "same-semantics CPU reference above the 100 ms scale target."
            ),
            "next_local_action": (
                "Add Barnes-Hut 1M node-coverage to the next one-pod batch only after "
                "review; keep public wording blocked until real RTX timing, baseline "
                "comparison, and 2-AI review exist."
            ),
            "pod_policy": "eligible_for_next_pod_after_review",
        },
    ]

    return {
        "goal": GOAL,
        "date": DATE,
        "rows": rows,
        "summary": {
            "scale_contract_rows": len(rows),
            "blocked_rows": sum(1 for row in rows if str(row["decision"]).startswith("blocked")),
            "pod_candidate_after_review_rows": sum(
                1 for row in rows if row["decision"] == "pod_candidate_after_review"
            ),
        },
        "valid": (
            rows[0]["decision"] == "blocked_scale_contract_not_repaired"
            and rows[0]["pod_policy"].startswith("no_pod_until")
            and rows[1]["decision"] == "pod_candidate_after_review"
            and rows[1]["recommended_cloud_scale"]["body_count"] >= 1_000_000
            and rows[1]["tested_scales"][-1]["cpu_reference_total_sec"] >= 0.1
        ),
        "boundary": (
            "Goal1067 is a local scale-contract audit. It does not run OptiX, "
            "does not run cloud, does not change public wording, and does not "
            "authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1067 Scale-Contract Repair Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- scale-contract rows: `{payload['summary']['scale_contract_rows']}`",
        f"- blocked rows: `{payload['summary']['blocked_rows']}`",
        f"- pod candidates after review: `{payload['summary']['pod_candidate_after_review_rows']}`",
        "",
        "## Decisions",
        "",
        "| App | Path | Decision | Pod policy | Reason | Next local action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['decision']}` | "
            f"`{row['pod_policy']}` | {row['reason']} | {row['next_local_action']} |"
        )
    lines.extend(
        [
            "",
            "## Barnes-Hut Recommended Cloud Scale",
            "",
            "The only repaired scale-contract candidate is "
            "`barnes_hut_force_app / node_coverage_prepared` at "
            f"`{payload['rows'][1]['recommended_cloud_scale']['body_count']}` bodies. "
            "This remains a candidate for a future pod batch, not a public claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Hausdorff/Barnes-Hut RTX scale-contract repair.")
    parser.add_argument("--output-json", default="docs/reports/goal1067_scale_contract_repair_audit_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1067_scale_contract_repair_audit_2026-04-28.md")
    args = parser.parse_args(argv)
    payload = build_audit()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "valid": payload["valid"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
