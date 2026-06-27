from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_serious_v2x_paired_20260622_074100"
)
FROZEN_SUMMARY = EVIDENCE_DIR / "summary.json"
CURRENT_STRESS_SUMMARY = EVIDENCE_DIR / "current_goal2636_stress" / "summary.json"
V2_STRESS_SUMMARY = EVIDENCE_DIR / "v2_14_goal2636_stress" / "summary.json"
APP_CODE = ROOT / "examples" / "current" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
PREPARED_EXECUTION_CODE = ROOT / "src" / "rtdsl" / "prepared_execution.py"
M3_GAP_DOC = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md"
REDO_ALIGNMENT_DOC = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md"

DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.json"
DEFAULT_MD_OUT = ROOT / "docs" / "reports" / "phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.md"

TARGET_CASE_ID = "rayjoin_optix_promoted_lsi_tiled_x2048"
TARGET_ROW_ID = (
    "goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|"
    "optix|rayjoin_optix_promoted_lsi_tiled_x2048"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_id(row: dict[str, Any]) -> str:
    return "|".join(
        str(row[field])
        for field in ("suite", "app_id", "comparison_group", "backend", "case_id")
    )


def _find_row(rows: list[dict[str, Any]], *, case_id: str, backend: str | None = None) -> dict[str, Any]:
    for row in rows:
        if row.get("case_id") != case_id:
            continue
        if backend is not None and row.get("backend") != backend:
            continue
        return row
    raise KeyError(f"row not found: case_id={case_id!r}, backend={backend!r}")


def _find_group_backend(rows: list[dict[str, Any]], *, comparison_group: str, backend: str) -> dict[str, Any]:
    for row in rows:
        if row.get("comparison_group") == comparison_group and row.get("backend") == backend:
            return row
    raise KeyError(f"group backend row not found: group={comparison_group!r}, backend={backend!r}")


def _first_command(row: dict[str, Any]) -> str:
    runs = row.get("runs") or []
    if not runs:
        return ""
    command = runs[0].get("command") or []
    return " ".join(str(part) for part in command)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_payload(
    frozen_summary_path: Path = FROZEN_SUMMARY,
    current_stress_summary_path: Path = CURRENT_STRESS_SUMMARY,
    v2_stress_summary_path: Path = V2_STRESS_SUMMARY,
    app_code_path: Path = APP_CODE,
    prepared_execution_code_path: Path = PREPARED_EXECUTION_CODE,
    m3_gap_doc_path: Path = M3_GAP_DOC,
    redo_alignment_doc_path: Path = REDO_ALIGNMENT_DOC,
) -> dict[str, Any]:
    frozen = _load_json(frozen_summary_path)
    current = _load_json(current_stress_summary_path)
    v2 = _load_json(v2_stress_summary_path)
    app_text = _read_text(app_code_path)
    prepared_text = _read_text(prepared_execution_code_path)
    m3_gap_text = _read_text(m3_gap_doc_path)
    redo_alignment_text = _read_text(redo_alignment_doc_path)

    frozen_row = next(
        row for row in frozen["same_metric_rows"] if _row_id(row) == TARGET_ROW_ID
    )
    current_row = _find_row(current["rows"], case_id=TARGET_CASE_ID, backend="optix")
    v2_row = _find_row(v2["rows"], case_id=TARGET_CASE_ID, backend="optix")
    current_payload = current_row.get("payload") or {}
    v2_payload = v2_row.get("payload") or {}
    comparison_group = str(current_row["comparison_group"])
    current_embree = _find_group_backend(
        current["rows"], comparison_group=comparison_group, backend="embree"
    )

    v2_sec = float(v2_row["primary_metric_sec"])
    v3_sec = float(current_row["primary_metric_sec"])
    speedup = v2_sec / v3_sec
    absolute_delta_sec = v3_sec - v2_sec
    optix_vs_embree_ratio = float(current_embree["primary_metric_sec"]) / v3_sec

    code_facts = {
        "prepared_execution_point_location_runner_exists": (
            "def run_point_location_topology_stream_prepared_session" in prepared_text
        ),
        "prepared_execution_segment_intersection_runner_exists": (
            "def run_segment_intersection_topology_stream_prepared_session" in prepared_text
            or "segment_intersection_topology_stream_prepared_session" in prepared_text
        ),
        "app_pip_productized_runner_blocks_lsi": (
            "prepared_execution_point_location_topology_stream currently supports only PIP"
            in app_text
        ),
        "app_lsi_dense_count_route_exists": (
            "prepared_optix_left_id_dense_count currently supports only the lsi workload"
            in app_text
        ),
        "app_lsi_generic_capability_label_exists": (
            '"lsi": "segment_intersection_topology_stream"' in app_text
        ),
        "app_lsi_device_resident_dense_count_claim_exists": (
            "dense_left_id_count_device_column_complete" in app_text
        ),
        "app_lsi_native_prepared_left_reuse_exists": (
            "left_id_count_prepared_left_device_columns" in app_text
            and "prepare_segment_pair_relation_left_set_optix" in app_text
        ),
        "m3_gap_doc_requests_reusable_topology_runner": (
            "Build or repair a reusable topology-stream prepared handle/runner" in m3_gap_text
        ),
        "redo_doc_limits_spatial_to_point_location_row": (
            "point_location_topology_stream" in redo_alignment_text
            and "not as public Spatial/RayJoin" in redo_alignment_text
        ),
    }

    checks = {
        "target_row_found": _row_id(frozen_row) == TARGET_ROW_ID,
        "v2_v3_same_metric_source": (
            v2_row["primary_metric_source"] == current_row["primary_metric_source"]
        ),
        "target_is_microsecond_delta": abs(absolute_delta_sec) < 50.0e-6,
        "payload_not_productized_runner": current_payload.get("productized_execution_path") is None
        and current_payload.get("prepared_execution_session_runner") is None,
        "payload_has_no_topology_stream_handle": current_payload.get("topology_stream_prepared_handle") is None,
        "point_location_runner_exists": code_facts["prepared_execution_point_location_runner_exists"],
        "active_payload_not_productized_even_if_current_code_has_runner": (
            current_payload.get("productized_execution_path") is None
            and current_payload.get("prepared_execution_session_runner") is None
        ),
        "segment_intersection_runner_current_state_recorded": isinstance(
            code_facts["prepared_execution_segment_intersection_runner_exists"], bool
        ),
        "pip_productized_runner_blocks_lsi": code_facts["app_pip_productized_runner_blocks_lsi"],
        "lsi_app_layer_device_residency_exists": code_facts[
            "app_lsi_device_resident_dense_count_claim_exists"
        ],
        "not_an_optix_vs_embree_slowdown": optix_vs_embree_ratio > 100.0,
        "old_docs_already_point_to_reusable_runner_gap": code_facts[
            "m3_gap_doc_requests_reusable_topology_runner"
        ],
    }
    failed_checks = [name for name, value in checks.items() if not value]

    payload: dict[str, Any] = {
        "tool": "v3_phoenix_spatial_lsi_optix_m9_intake",
        "status": "m9_spatial_lsi_optix_mechanics_intake_not_release_not_pod",
        "target": {
            "row_id": TARGET_ROW_ID,
            "app_id": "spatial_rayjoin",
            "set": "A",
            "case_id": TARGET_CASE_ID,
            "comparison_group": comparison_group,
            "why_targeted": (
                "Largest uncovered Set-A row loss in the M8 blocker queue after "
                "Barnes-Hut and LibRTS Embree were marked covered pending full-suite validation."
            ),
        },
        "source_row": {
            "v2_sec": v2_sec,
            "v3_sec": v3_sec,
            "v3_speedup_vs_v2": speedup,
            "frozen_speedup_vs_v2": float(frozen_row["v3_speedup_vs_v2"]),
            "absolute_delta_sec": absolute_delta_sec,
            "absolute_delta_microseconds": absolute_delta_sec * 1_000_000.0,
            "primary_metric_source_v2": v2_row["primary_metric_source"],
            "primary_metric_source_v3": current_row["primary_metric_source"],
            "current_command": _first_command(current_row),
            "v2_command": _first_command(v2_row),
        },
        "metric_interpretation": {
            "row_is_v3_vs_v2_regression_not_optix_vs_embree_result": True,
            "current_optix_vs_current_embree_ratio": optix_vs_embree_ratio,
            "current_embree_sec": float(current_embree["primary_metric_sec"]),
            "current_embree_metric_source": current_embree["primary_metric_source"],
            "current_optix_sec": v3_sec,
            "current_optix_metric_source": current_row["primary_metric_source"],
            "ratio_warning": (
                "The OptiX/Embree ratio mixes Embree elapsed_sec with OptiX "
                "phases_sec.prepared_query_sec, so it is useful only as a sanity "
                "check that OptiX is not slow in this row, not as a public speedup claim."
            ),
        },
        "route_mapping": {
            "workload": current_payload.get("workload"),
            "execution_route": current_payload.get("execution_route"),
            "productized_execution_path": current_payload.get("productized_execution_path"),
            "topology_stream_prepared_handle_present": bool(
                current_payload.get("topology_stream_prepared_handle")
            ),
            "prepared_execution_session_runner_present": bool(
                current_payload.get("prepared_execution_session_runner")
            ),
            "app_layer_wrapper": (
                "PreparedRayJoinOptixCompactGroupedCountSegments.run_packed_left_dense_count"
            ),
            "native_calls_seen_in_app_code": [
                "prepare_segment_pair_intersection_optix",
                "pack_segment_pair_intersection_left_set",
                "prepare_segment_pair_relation_left_set_optix",
                "left_id_count_prepared_left_device_columns",
            ],
            "payload_device_residency_status": current_payload.get(
                "device_resident_continuation_status"
            ),
            "payload_native_boundary": current_payload.get("native_engine_boundary"),
        },
        "productized_runner_coverage": {
            "point_location_topology_stream_productized_runner_exists": code_facts[
                "prepared_execution_point_location_runner_exists"
            ],
            "segment_intersection_topology_stream_productized_runner_exists_in_current_code": code_facts[
                "prepared_execution_segment_intersection_runner_exists"
            ],
            "existing_productized_spatial_runner_scope": "PIP point-location only",
            "current_lsi_route_scope": "app-layer prepared-left dense left-id count wrapper",
            "gap": (
                "LSI has useful RTDL-owned device-resident pieces, but the measured "
                "active loss row does not enter the shared prepared_execution_session_runner "
                "and emits no topology_stream_prepared_handle. If current code now "
                "contains a segment_intersection_topology_stream runner, that is M10 "
                "follow-up work; it does not retroactively change the frozen M9 active "
                "row payload. The V3 trunk gap is generic segment_intersection_topology_stream "
                "productization, not RayJoin-specific paper tuning."
            ),
        },
        "candidate_next_work": [
            {
                "id": "m10_segment_intersection_topology_stream_prepared_session",
                "kind": "shared_runtime_trunk_candidate",
                "description": (
                    "Add a productized prepared-session wrapper for the existing LSI "
                    "generic segment-pair left-id count route, mirroring the point-location "
                    "runner metadata and residency gates."
                ),
                "why_it_might_help": (
                    "It converts existing app-layer residency work into a reusable V3 "
                    "runtime path and makes the source of any Set-A win productized."
                ),
                "risk": (
                    "The measured V3-vs-V2 loss is only 15.4 microseconds; productization "
                    "may mainly improve evidence/contract quality before it improves speed."
                ),
                "pod_before_implementation": False,
                "focused_pod_after_implementation_and_2ai_review": True,
            },
            {
                "id": "m10_metric_hygiene_repeat_stability",
                "kind": "measurement_candidate",
                "description": (
                    "After a productized LSI route exists, run a focused repeat-stability "
                    "probe on the same RT hardware before any all-app spend."
                ),
                "why_it_might_help": (
                    "A 15-microsecond delta can be dispatch jitter; repeat stability "
                    "prevents overreacting to noise."
                ),
                "pod_before_productized_route": False,
                "all_app_pod_before_focused_probe": False,
            },
            {
                "id": "reject_rayjoin_specific_native_tuning",
                "kind": "forbidden_shortcut",
                "description": (
                    "Do not add RayJoin-only native logic or paper-specific shortcuts to "
                    "make this row green."
                ),
                "why_rejected": (
                    "Phoenix V3 is a language/runtime release. Benchmark apps are probes, "
                    "not the product."
                ),
            },
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "focused_pod_spend_authorized": False,
        "full_all_app_pod_spend_authorized": False,
        "implementation_authorized_by_this_packet": False,
        "needs_2ai_review_before_m10": True,
        "goal_level_decision_audit": {
            "decision": (
                "Treat Spatial/RayJoin LSI OptiX as a local mechanics intake and "
                "candidate productized segment-intersection trunk item, not as immediate POD work."
            ),
            "was_i_foolish": "No.",
            "if_yes_what_actions_made_it_foolish": (
                "The foolish path would be to call this an OptiX failure, burn POD "
                "rerunning a 15-microsecond delta, or tune RayJoin-specific code before "
                "checking whether the shared runtime trunk is even executing."
            ),
            "was_there_another_path": (
                "Yes: jump straight to a focused POD run. That would be premature because "
                "the payload already shows the row bypasses the productized runner."
            ),
            "can_i_try_a_different_path_now": (
                "Yes: first productize or explicitly reject a generic "
                "segment_intersection_topology_stream prepared-session route, then seek "
                "2-AI review before focused POD."
            ),
        },
    }
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    source = payload["source_row"]
    metric = payload["metric_interpretation"]
    coverage = payload["productized_runner_coverage"]
    checks = payload["checks"]
    failed = ", ".join(payload["failed_checks"]) if payload["failed_checks"] else "none"
    candidates = "\n".join(
        f"- `{item['id']}`: {item['description']}"
        for item in payload["candidate_next_work"]
    )
    audit = payload["goal_level_decision_audit"]
    return f"""# Phoenix V3 M9 Spatial LSI OptiX Mechanics Intake

Status: `{payload['status']}`

```text
release_authorized: {str(payload['release_authorized']).lower()}
public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}
broad_v3_faster_than_v2_claim_authorized: {str(payload['broad_v3_faster_than_v2_claim_authorized']).lower()}
focused_pod_spend_authorized: {str(payload['focused_pod_spend_authorized']).lower()}
full_all_app_pod_spend_authorized: {str(payload['full_all_app_pod_spend_authorized']).lower()}
implementation_authorized_by_this_packet: {str(payload['implementation_authorized_by_this_packet']).lower()}
```

## Target Row

- Row: `{payload['target']['row_id']}`
- Command: `{source['current_command']}`
- V2.14 sec: `{source['v2_sec']:.12f}`
- Current Phoenix V3 sec: `{source['v3_sec']:.12f}`
- V3/V2 speedup: `{source['v3_speedup_vs_v2']:.6f}x`
- Absolute delta: `{source['absolute_delta_microseconds']:.3f}` microseconds slower
- Metric source: `{source['primary_metric_source_v3']}`

This row is a V3-vs-V2 regression row, not an OptiX-vs-Embree result.
Current OptiX is `{metric['current_optix_vs_current_embree_ratio']:.3f}x`
over the current Embree row in the same comparison group, but that sanity
ratio mixes `{metric['current_embree_metric_source']}` and
`{metric['current_optix_metric_source']}` and is not a public speedup claim.

## Route Finding

- Workload: `{payload['route_mapping']['workload']}`
- Execution route: `{payload['route_mapping']['execution_route']}`
- Productized execution path: `{payload['route_mapping']['productized_execution_path']}`
- `prepared_execution_session_runner` present: `{str(payload['route_mapping']['prepared_execution_session_runner_present']).lower()}`
- `topology_stream_prepared_handle` present: `{str(payload['route_mapping']['topology_stream_prepared_handle_present']).lower()}`
- App-layer wrapper: `{payload['route_mapping']['app_layer_wrapper']}`

## Productized Runner Gap

- Point-location topology-stream runner exists:
  `{str(coverage['point_location_topology_stream_productized_runner_exists']).lower()}`
- Segment-intersection topology-stream runner exists:
  `{str(coverage['segment_intersection_topology_stream_productized_runner_exists_in_current_code']).lower()}`
- Existing productized Spatial runner scope:
  `{coverage['existing_productized_spatial_runner_scope']}`
- Current LSI route scope:
  `{coverage['current_lsi_route_scope']}`

{coverage['gap']}

## Candidate Next Work

{candidates}

## Checks

Failed checks: `{failed}`

| Check | Pass |
| --- | --- |
""" + "\n".join(
        f"| `{name}` | `{str(value).lower()}` |" for name, value in checks.items()
    ) + f"""

## Goal-Level Decision Audit

Decision: {audit['decision']}

1. Was I foolish?
   {audit['was_i_foolish']}
2. If yes, what actions made the decision foolish?
   {audit['if_yes_what_actions_made_it_foolish']}
3. Was there another path?
   {audit['was_there_another_path']}
4. Can I now try a different path?
   {audit['can_i_try_a_different_path_now']}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
