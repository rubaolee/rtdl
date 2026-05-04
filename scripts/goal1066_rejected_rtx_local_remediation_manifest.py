#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-28"
GOAL = "Goal1066 rejected RTX local remediation manifest"
GOAL1063 = ROOT / "docs/reports/goal1063_pre_pod_local_completion_audit_2026-04-28.json"


REMEDIATION: dict[tuple[str, str], dict[str, Any]] = {
    ("database_analytics", "prepared_db_session_sales_risk"): {
        "class": "code_path_profile",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 3 --output-mode compact_summary --strict --output-json /tmp/goal1066_db_sales_optix.json",
        ],
        "acceptance_before_pod": [
            "phase breakdown identifies whether OptiX query, prepare, or Python/native transfer dominates",
            "a concrete code or scale change is recorded before any cloud rerun",
        ],
    },
    ("database_analytics", "prepared_db_session_regional_dashboard"): {
        "class": "code_path_profile",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario regional_dashboard --copies 20000 --iterations 3 --output-mode compact_summary --strict --output-json /tmp/goal1066_db_dashboard_optix.json",
        ],
        "acceptance_before_pod": [
            "grouped aggregation and compact-summary copyback costs are separated",
            "a concrete code or scale change is recorded before any cloud rerun",
        ],
    },
    ("graph_analytics", "graph_visibility_edges_gate"): {
        "class": "rt_mapping_profile",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal889_graph_visibility_optix_gate.py --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json /tmp/goal1066_graph_visibility_dry_probe.json",
        ],
        "acceptance_before_pod": [
            "RT traversal timing is separated from graph bookkeeping and validation",
            "a local decision exists on whether to optimize the RT mapping or change the benchmark scale",
        ],
    },
    ("road_hazard_screening", "road_hazard_native_summary_gate"): {
        "class": "code_path_profile",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 2000 --iterations 3 --mode dry-run --output-json /tmp/goal1066_road_hazard_dry_probe.json",
        ],
        "acceptance_before_pod": [
            "same-semantics Embree advantage is explained or a native OptiX optimization target is identified",
            "no cloud rerun until the prepared segment/polygon summary path changes or a new scale contract exists",
        ],
    },
    ("polygon_pair_overlap_area_rows", "polygon_pair_overlap_optix_native_assisted_phase_gate"): {
        "class": "chunking_and_candidate_discovery",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode dry-run --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json /tmp/goal1066_pair_overlap_dry_probe.json",
        ],
        "acceptance_before_pod": [
            "candidate discovery row volume and chunking costs are bounded before cloud",
            "PostGIS/Embree baseline mismatch is addressed before any public wording review",
        ],
    },
    ("polygon_set_jaccard", "polygon_set_jaccard_optix_native_assisted_phase_gate"): {
        "class": "chunking_and_candidate_discovery",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode dry-run --copies 2000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json /tmp/goal1066_jaccard_dry_probe.json",
        ],
        "acceptance_before_pod": [
            "Jaccard candidate discovery avoids known large-chunk diagnostic failures",
            "exact set-area/Jaccard CPU handoff is clearly outside the RT claim",
        ],
    },
    ("hausdorff_distance", "directed_threshold_prepared"): {
        "class": "scale_contract_repair",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode dry-run --copies 20000 --iterations 1 --radius 0.4 --output-json /tmp/goal1066_hausdorff_dry_probe.json",
        ],
        "acceptance_before_pod": [
            "CPU same-semantics baseline is no longer microsecond-trivial or is explicitly excluded as a claim baseline",
            "the threshold-decision scale remains semantically meaningful and dry-run validated",
        ],
    },
    ("barnes_hut_force_app", "node_coverage_prepared"): {
        "class": "scale_contract_repair",
        "local_probe_commands": [
            "PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode dry-run --body-count 200000 --iterations 1 --radius 10.0 --output-json /tmp/goal1066_barnes_hut_dry_probe.json",
        ],
        "acceptance_before_pod": [
            "CPU same-semantics baseline is no longer trivial or the benchmark target is reframed away from a speedup claim",
            "node-coverage remains bounded to candidate discovery, not force-vector reduction",
        ],
    },
}


def _load_goal1063() -> dict[str, Any]:
    return json.loads(GOAL1063.read_text(encoding="utf-8"))


def build_manifest() -> dict[str, Any]:
    source = _load_goal1063()
    rejected = source["rejected_rows_requiring_local_work"]
    rows: list[dict[str, Any]] = []
    for row in rejected:
        key = (row["app"], row["path_name"])
        remediation = REMEDIATION.get(key)
        rows.append(
            {
                "app": row["app"],
                "path_name": row["path_name"],
                "ratio_baseline_over_rtx": row["ratio_baseline_over_rtx"],
                "fastest_baseline": row["fastest_baseline"],
                "pod_policy": row["pod_policy"],
                "goal1063_local_next": row["local_next"],
                "remediation_class": remediation["class"] if remediation else "missing",
                "local_probe_commands": remediation["local_probe_commands"] if remediation else [],
                "acceptance_before_pod": remediation["acceptance_before_pod"] if remediation else [],
            }
        )
    missing = [
        f"{row['app']}/{row['path_name']}"
        for row in rows
        if row["remediation_class"] == "missing"
    ]
    class_counts: dict[str, int] = {}
    for row in rows:
        klass = str(row["remediation_class"])
        class_counts[klass] = class_counts.get(klass, 0) + 1
    return {
        "goal": GOAL,
        "date": DATE,
        "source": str(GOAL1063.relative_to(ROOT)),
        "rejected_row_count": len(rows),
        "remediation_class_counts": class_counts,
        "missing_remediation": missing,
        "rows": rows,
        "valid": (
            len(rows) == 5
            and not missing
            and all(row["pod_policy"].startswith("no_pod_until") for row in rows)
            and all(row["local_probe_commands"] for row in rows)
            and all(row["acceptance_before_pod"] for row in rows)
        ),
        "boundary": (
            "Goal1066 is a local remediation manifest for rejected RTX rows. "
            "It does not run cloud, change public wording, authorize release, "
            "or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1066 Rejected RTX Local Remediation Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- rejected rows: `{payload['rejected_row_count']}`",
        f"- remediation classes: `{payload['remediation_class_counts']}`",
        f"- missing remediation: `{payload['missing_remediation']}`",
        "",
        "## Rows",
        "",
        "| App | Path | Class | Pod policy | Local probe | Acceptance before pod |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['remediation_class']}` | "
            f"`{row['pod_policy']}` | `{' && '.join(row['local_probe_commands'])}` | "
            f"{'; '.join(row['acceptance_before_pod'])} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build rejected RTX local remediation manifest.")
    parser.add_argument("--output-json", default="docs/reports/goal1066_rejected_rtx_local_remediation_manifest_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1066_rejected_rtx_local_remediation_manifest_2026-04-28.md")
    args = parser.parse_args(argv)
    payload = build_manifest()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "valid": payload["valid"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
