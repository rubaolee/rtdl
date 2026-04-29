#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1103 baseline execution manifest"
OUT_DIR = "docs/reports/goal1101_current_contract_non_optix_baselines"


def build_manifest() -> dict[str, Any]:
    rows = [
        {
            "name": "barnes_hut_validation_embree",
            "recommended_order": 1,
            "risk": "moderate",
            "current_mac_recommendation": "safe_to_run",
            "command": (
                "PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py "
                "--scenario barnes_hut_node_coverage --backend embree --body-count 4096 --iterations 3 "
                f"--radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json {OUT_DIR}/barnes_hut_depth8_4096_embree_validation_baseline.json"
            ),
            "expected_artifact": f"{OUT_DIR}/barnes_hut_depth8_4096_embree_validation_baseline.json",
            "why": "Small validated baseline row needed before interpreting the Barnes-Hut 20M timing row.",
        },
        {
            "name": "facility_cpu_oracle",
            "recommended_order": 2,
            "risk": "high",
            "current_mac_recommendation": "prefer_linux_or_windows_large_ram",
            "command": (
                "PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py "
                "--scenario facility_service_coverage_recentered --backend cpu_oracle --copies 2500000 --iterations 3 "
                f"--radius 1.0 --output-json {OUT_DIR}/facility_recentered_2_5m_cpu_oracle_baseline.json"
            ),
            "expected_artifact": f"{OUT_DIR}/facility_recentered_2_5m_cpu_oracle_baseline.json",
            "why": "Same-current-contract CPU oracle timing for the 10M-query facility row; 2.5M copies expands to 10M customers because the fixture has four customers per copy.",
        },
        {
            "name": "facility_embree",
            "recommended_order": 3,
            "risk": "high",
            "current_mac_recommendation": "prefer_linux_or_windows_large_ram",
            "command": (
                "PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py "
                "--scenario facility_service_coverage_recentered --backend embree --copies 2500000 --iterations 3 "
                f"--radius 1.0 --output-json {OUT_DIR}/facility_recentered_2_5m_embree_baseline.json"
            ),
            "expected_artifact": f"{OUT_DIR}/facility_recentered_2_5m_embree_baseline.json",
            "why": "Same-current-contract Embree baseline for the 10M-query facility row; 2.5M copies expands to 10M customers and may allocate and scan large query arrays.",
        },
        {
            "name": "barnes_hut_timing_embree",
            "recommended_order": 4,
            "risk": "very_high",
            "current_mac_recommendation": "do_not_run_on_16gb_mac_without_user_approval",
            "command": (
                "PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py "
                "--scenario barnes_hut_node_coverage --backend embree --body-count 20000000 --iterations 3 "
                f"--radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json {OUT_DIR}/barnes_hut_depth8_20m_embree_timing_baseline.json"
            ),
            "expected_artifact": f"{OUT_DIR}/barnes_hut_depth8_20m_embree_timing_baseline.json",
            "why": "Large timing-only baseline paired with the validated Barnes-Hut row; likely too memory-heavy for a 16 GB laptop.",
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "output_dir": OUT_DIR,
        "row_count": len(rows),
        "rows": rows,
        "recommended_next_local_action": "run_barnes_hut_validation_embree_then_goal1102_intake",
        "boundary": (
            "Goal1103 is an execution manifest only. It does not run full baselines, does not start cloud, "
            "and does not authorize public RTX speedup claims."
        ),
        "valid": len(rows) == 4 and all(row["command"].startswith("PYTHONPATH=src:. python3") for row in rows),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1103 Baseline Execution Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        f"Recommended next local action: `{payload['recommended_next_local_action']}`",
        "",
        "## Rows",
        "",
        "| Order | Name | Risk | Current Mac recommendation | Expected artifact |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['recommended_order']} | `{row['name']}` | `{row['risk']}` | "
            f"`{row['current_mac_recommendation']}` | `{row['expected_artifact']}` |"
        )
    lines.extend(["", "## Commands", ""])
    for row in payload["rows"]:
        lines.extend([f"### {row['name']}", "", row["why"], "", "```bash", row["command"], "```", ""])
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit row-by-row current-contract baseline execution manifest.")
    parser.add_argument("--output-json", default="docs/reports/goal1103_baseline_execution_manifest_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1103_baseline_execution_manifest_2026-04-29.md")
    args = parser.parse_args()
    payload = build_manifest()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "row_count": payload["row_count"], "recommended_next_local_action": payload["recommended_next_local_action"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
