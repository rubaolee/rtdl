#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALL_APP_SUMMARY = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_claim_grade_all_benchmarks_calibrated_20260620" / "summary.json"
M23_EVIDENCE = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_m4_grouped_continuation_20260620" / "m23_dbscan_component_signature_524288.json"
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.json"
DEFAULT_MD_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.md"


def build_payload(
    *,
    all_app_summary_path: Path = ALL_APP_SUMMARY,
    m23_evidence_path: Path = M23_EVIDENCE,
) -> dict[str, Any]:
    all_app = json.loads(all_app_summary_path.read_text(encoding="utf-8"))
    m23 = json.loads(m23_evidence_path.read_text(encoding="utf-8"))
    rt_rows = [row for row in all_app["rows"] if row.get("app_id") == "rt_dbscan"]
    embree = _find_row(rt_rows, "embree")
    optix = _find_row(rt_rows, "optix")
    embree_sec = float(embree["primary_metric_sec"])
    optix_sec = float(optix["primary_metric_sec"])
    speedup = embree_sec / optix_sec
    m23_rows = list(m23["rows"])
    return {
        "status": "rtdbscan_component_union_m7_feasibility_not_promoted",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "m7_promoted": False,
        "m7_qualified_release_rows": 0,
        "generic_capability": "component_union",
        "app_id": "rt_dbscan",
        "source_evidence": {
            "all_app_summary": str(all_app_summary_path.relative_to(ROOT)),
            "m23_evidence": str(m23_evidence_path.relative_to(ROOT)),
        },
        "all_app_ratio_row": {
            "comparison_group": "dbscan_cluster_signature",
            "dataset": optix["payload"].get("dataset"),
            "point_count": optix["payload"].get("point_count"),
            "embree_case_id": embree["case_id"],
            "optix_case_id": optix["case_id"],
            "embree_primary_metric_sec": embree_sec,
            "optix_primary_metric_sec": optix_sec,
            "optix_over_embree_speedup": speedup,
            "matches_reference": optix["payload"].get("matches_reference"),
            "reference_signature": optix["payload"].get("reference_signature"),
            "optix_wall_median_sec": optix.get("wall_median_sec"),
            "embree_wall_median_sec": embree.get("wall_median_sec"),
            "claim_status": "internal_ratio_not_m7_validation_missing",
            "main_blocker": "all_app_ratio_row_has_matches_reference_null",
        },
        "m23_scale_evidence": {
            "status": m23["status"],
            "point_count": m23["parameters"]["point_count"],
            "copies": m23["parameters"]["copies"],
            "output_mode": m23["parameters"]["output_mode"],
            "partners": m23["parameters"]["partners"],
            "all_match_oracle": m23["comparison"]["all_match_oracle"],
            "cluster_size_signatures_match": m23["comparison"]["cluster_size_signatures_match"],
            "core_counts_match": m23["comparison"]["core_counts_match"],
            "noise_counts_match": m23["comparison"]["noise_counts_match"],
            "rt_core_accelerated": m23["comparison"]["rt_core_accelerated"],
            "native_continuation_active": m23["comparison"]["native_continuation_active"],
            "materializes_python_rows": any(bool(row["materializes_python_rows"]) for row in m23_rows),
            "partners_present": sorted({row["partner"] for row in m23_rows}),
            "hot_component_label_elapsed_sec_median_by_partner": {
                row["partner"]: row["hot_component_label_elapsed_sec_median"] for row in m23_rows
            },
            "prepare_sec_by_partner": {row["partner"]: row["prepare_sec"] for row in m23_rows},
            "claim_status": "internal_scale_parity_not_m7_no_same_scale_embree_baseline",
            "main_blocker": "no_same_scale_embree_baseline_for_m23_component_signature",
        },
        "m7_blockers": [
            "all_app_ratio_row_has_matches_reference_null",
            "all_app_ratio_row_is_8192_points_not_m23_524288_scale",
            "m23_scale_evidence_has_no_same_scale_embree_baseline",
            "component_signature_not_full_dbscan_labels",
            "no_public_component_union_contract",
            "no_final_external_public_row_review",
            "broad_v3_faster_than_v2_claim_authorized_false",
        ],
        "next_rerun_requirements": [
            "Use the same component-size signature contract for Embree and OptiX at the same scale.",
            "Keep validation on or attach an oracle signature artifact, not matches_reference: null.",
            "Report prepare, hot query, wall, warmup, repeat, partner, and backend separately.",
            "State component_signature only; do not call it full DBSCAN labels.",
            "Keep count/core/noise and cluster-size signature parity visible.",
        ],
        "allowed_internal_reading": (
            "RTDBSCAN has strong internal evidence for component_union: a huge small-scale "
            "OptiX/Embree ratio and a separate 524,288-point M23 oracle-matching component "
            "signature run."
        ),
        "forbidden_public_reading": (
            "Do not claim RTDBSCAN V3 is 1483x faster end to end; do not claim paper "
            "reproduction; do not claim full DBSCAN acceleration from component signatures."
        ),
        "goal_level_decision_audit": {
            "decision": "classify RTDBSCAN component_union feasibility without promotion",
            "was_i_foolish": "No. The packet separates the strong ratio row from the validated M23 scale row.",
            "foolish_actions": (
                "It would be foolish to combine the 1483x all-app ratio with the 524,288-point "
                "M23 validation as if they were the same M7 row."
            ),
            "other_path": "Run a pod rerun immediately. That is plausible but needs a precise packet first.",
            "different_path_now": (
                "Write the feasibility boundary first, then produce a focused same-scale rerun packet if RTDBSCAN remains the next candidate."
            ),
        },
    }


def _find_row(rows: list[dict[str, Any]], backend: str) -> dict[str, Any]:
    matches = [row for row in rows if row.get("backend") == backend]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one rt_dbscan {backend} row, found {len(matches)}")
    return matches[0]


def render_markdown(payload: dict[str, Any]) -> str:
    ratio = payload["all_app_ratio_row"]
    m23 = payload["m23_scale_evidence"]
    blockers = "\n".join(f"- `{blocker}`" for blocker in payload["m7_blockers"])
    requirements = "\n".join(f"- {item}" for item in payload["next_rerun_requirements"])
    audit = payload["goal_level_decision_audit"]
    return f"""# Phoenix V3 RTDBSCAN Component-Union M7 Feasibility

Status: feasibility packet, not M7 promotion.

```text
status: {payload['status']}
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

## Verdict

RTDBSCAN/component_union remains internal. The evidence is promising, but no
single row currently satisfies M7.

## All-App Ratio Row

| Field | Value |
| --- | --- |
| Comparison group | `{ratio['comparison_group']}` |
| Dataset | `{ratio['dataset']}` |
| Point count | `{ratio['point_count']}` |
| Embree primary metric | `{ratio['embree_primary_metric_sec']:.6f}` sec |
| OptiX primary metric | `{ratio['optix_primary_metric_sec']:.6f}` sec |
| OptiX-vs-Embree speedup | `{ratio['optix_over_embree_speedup']:.3f}x` |
| matches_reference | `{ratio['matches_reference']}` |
| reference_signature | `{ratio['reference_signature']}` |
| Claim status | `{ratio['claim_status']}` |

This row cannot be promoted because validation is missing in the ratio row.

## M23 Scale Evidence

| Field | Value |
| --- | --- |
| Status | `{m23['status']}` |
| Point count | `{m23['point_count']}` |
| Copies | `{m23['copies']}` |
| Output mode | `{m23['output_mode']}` |
| Partners | `{m23['partners_present']}` |
| Oracle match | `{m23['all_match_oracle']}` |
| Cluster-size signatures match | `{m23['cluster_size_signatures_match']}` |
| Core counts match | `{m23['core_counts_match']}` |
| Noise counts match | `{m23['noise_counts_match']}` |
| RT-core accelerated | `{m23['rt_core_accelerated']}` |
| Materializes Python rows | `{m23['materializes_python_rows']}` |
| Claim status | `{m23['claim_status']}` |

This row cannot be promoted because it has no same-scale Embree baseline.

## M7 Blockers

{blockers}

## Next Rerun Requirements

{requirements}

## Boundary

Allowed internal reading:

```text
{payload['allowed_internal_reading']}
```

Forbidden public reading:

```text
{payload['forbidden_public_reading']}
```

## Goal-Level Decision Audit

Decision: {audit['decision']}

1. Was I foolish?

   {audit['was_i_foolish']}

2. If yes, what actions made the decision foolish?

   {audit['foolish_actions']}

3. Was there another path?

   {audit['other_path']}

4. Can I now try a different path that actually solves the problem?

   {audit['different_path_now']}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build RTDBSCAN component_union M7 feasibility packet.")
    parser.add_argument("--all-app-summary", type=Path, default=ALL_APP_SUMMARY)
    parser.add_argument("--m23-evidence", type=Path, default=M23_EVIDENCE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_app_summary = args.all_app_summary if args.all_app_summary.is_absolute() else ROOT / args.all_app_summary
    m23_evidence = args.m23_evidence if args.m23_evidence.is_absolute() else ROOT / args.m23_evidence
    payload = build_payload(all_app_summary_path=all_app_summary, m23_evidence_path=m23_evidence)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "json_out": str(args.json_out), "md_out": str(args.md_out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
