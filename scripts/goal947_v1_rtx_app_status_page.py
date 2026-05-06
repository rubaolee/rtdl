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


GOAL = "Goal947 v1.0 RTX app status page"
DATE = "2026-04-30"

APP_PATHS = {
    "database_analytics": "examples/rtdl_database_analytics_app.py",
    "graph_analytics": "examples/rtdl_graph_analytics_app.py",
    "apple_rt_demo": "examples/rtdl_apple_rt_demo_app.py",
    "service_coverage_gaps": "examples/rtdl_service_coverage_gaps.py",
    "event_hotspot_screening": "examples/rtdl_event_hotspot_screening.py",
    "facility_knn_assignment": "examples/rtdl_facility_knn_assignment.py",
    "road_hazard_screening": "examples/rtdl_road_hazard_screening.py",
    "segment_polygon_hitcount": "examples/rtdl_segment_polygon_hitcount.py",
    "segment_polygon_anyhit_rows": "examples/rtdl_segment_polygon_anyhit_rows.py",
    "polygon_pair_overlap_area_rows": "examples/rtdl_polygon_pair_overlap_area_rows.py",
    "polygon_set_jaccard": "examples/rtdl_polygon_set_jaccard.py",
    "hausdorff_distance": "examples/rtdl_hausdorff_distance_app.py",
    "ann_candidate_search": "examples/rtdl_ann_candidate_app.py",
    "outlier_detection": "examples/rtdl_outlier_detection_app.py",
    "dbscan_clustering": "examples/rtdl_dbscan_clustering_app.py",
    "robot_collision_screening": "examples/rtdl_robot_collision_screening_app.py",
    "barnes_hut_force_app": "examples/rtdl_barnes_hut_force_app.py",
    "hiprt_ray_triangle_hitcount": "examples/rtdl_hiprt_ray_triangle_hitcount.py",
}

CLAIM_COMMANDS = {
    "database_analytics": "PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend optix --output-mode compact_summary --require-rt-core",
    "graph_analytics": "PYTHONPATH=src:. python examples/rtdl_graph_analytics_app.py --backend optix --scenario visibility_edges --require-rt-core",
    "service_coverage_gaps": "PYTHONPATH=src:. python examples/rtdl_service_coverage_gaps.py --backend optix --optix-summary-mode gap_summary_prepared --require-rt-core",
    "event_hotspot_screening": "PYTHONPATH=src:. python examples/rtdl_event_hotspot_screening.py --backend optix --optix-summary-mode count_summary_prepared --require-rt-core",
    "facility_knn_assignment": "PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py --backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core",
    "road_hazard_screening": "PYTHONPATH=src:. python examples/rtdl_road_hazard_screening.py --backend optix --output-mode summary --optix-mode native --require-rt-core",
    "segment_polygon_hitcount": "PYTHONPATH=src:. python scripts/goal933_prepared_segment_polygon_optix_profiler.py --backend optix --scenario segment_polygon_hitcount_prepared",
    "segment_polygon_anyhit_rows": "PYTHONPATH=src:. python scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py --backend optix --scenario segment_polygon_anyhit_rows_prepared_bounded",
    "polygon_pair_overlap_area_rows": "PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix --require-rt-core",
    "polygon_set_jaccard": "PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py --backend optix --require-rt-core",
    "hausdorff_distance": "PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core",
    "ann_candidate_search": "PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py --backend optix --optix-summary-mode candidate_threshold_prepared --require-rt-core",
    "outlier_detection": "PYTHONPATH=src:. python examples/rtdl_outlier_detection_app.py --backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count",
    "dbscan_clustering": "PYTHONPATH=src:. python examples/rtdl_dbscan_clustering_app.py --backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count",
    "robot_collision_screening": "PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend optix --optix-summary-mode prepared_count",
    "barnes_hut_force_app": "PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend optix --optix-summary-mode node_coverage_prepared --require-rt-core",
    "apple_rt_demo": "not a NVIDIA RTX target",
    "hiprt_ray_triangle_hitcount": "not a NVIDIA RTX target",
}

RT_CORE_SUBPATHS = {
    "database_analytics": "prepared DB compact-summary traversal/filter/grouping",
    "graph_analytics": "bounded visibility any-hit plus native graph-ray BFS/triangle candidate generation",
    "service_coverage_gaps": "prepared fixed-radius gap-summary traversal",
    "event_hotspot_screening": "prepared fixed-radius count-summary traversal",
    "facility_knn_assignment": "prepared fixed-radius service-coverage decision",
    "road_hazard_screening": "prepared native segment/polygon road-hazard summary traversal",
    "segment_polygon_hitcount": "prepared native segment/polygon hit-count traversal",
    "segment_polygon_anyhit_rows": "prepared bounded native pair-row traversal",
    "polygon_pair_overlap_area_rows": "native-assisted LSI/PIP candidate discovery",
    "polygon_set_jaccard": "native-assisted LSI/PIP candidate discovery",
    "hausdorff_distance": "prepared fixed-radius Hausdorff threshold decision",
    "ann_candidate_search": "prepared fixed-radius ANN candidate-coverage decision",
    "outlier_detection": "prepared fixed-radius scalar threshold-count traversal",
    "dbscan_clustering": "prepared fixed-radius scalar core-count traversal",
    "robot_collision_screening": "prepared ray/triangle any-hit scalar pose-count traversal",
    "barnes_hut_force_app": "prepared fixed-radius Barnes-Hut node-coverage decision",
    "apple_rt_demo": "Apple Metal/MPS RT demo, outside NVIDIA RTX table",
    "hiprt_ray_triangle_hitcount": "HIPRT-specific hit-count validation, outside NVIDIA RTX table",
}

NATIVE_CONTINUATION_CONTRACTS = {
    "database_analytics": "native continuation only for materialization-free compact DB summaries",
    "graph_analytics": "top-level metadata aggregates selected native graph sections; visibility_edges uses optix_visibility_pair_rows on OptiX",
    "service_coverage_gaps": "native continuation only for Embree gap_summary or OptiX gap_summary_prepared threshold-count paths",
    "event_hotspot_screening": "native continuation only for Embree count_summary or OptiX count_summary_prepared threshold-count paths",
    "facility_knn_assignment": "native continuation only for OptiX coverage_threshold_prepared service-coverage decisions",
    "road_hazard_screening": "app native OptiX hit-count mode is metadata-gated; accepted claim surface remains prepared road-hazard summary traversal",
    "segment_polygon_hitcount": "app native OptiX hit-count mode is metadata-gated; accepted claim surface remains prepared hit-count traversal",
    "segment_polygon_anyhit_rows": "native continuation is RT-core accelerated only for explicit bounded OptiX native rows mode",
    "polygon_pair_overlap_area_rows": "backend-neutral native exact-area summary follows RT-assisted LSI/PIP candidate discovery in compact summary mode",
    "polygon_set_jaccard": "backend-neutral native set-area/Jaccard summary follows bounded candidate discovery in compact summary mode",
    "hausdorff_distance": "native continuation only for Embree directed_summary or OptiX directed_threshold_prepared decision paths",
    "ann_candidate_search": "native KNN rerank summaries follow candidate KNN rows; OptiX prepared threshold path covers candidate-coverage decision only",
    "outlier_detection": "native continuation only for OptiX density_count scalar path or Embree/OptiX per-point threshold summary paths",
    "dbscan_clustering": "native continuation only for OptiX core_count scalar path or Embree/OptiX per-point core-flag summary paths, not full cluster expansion",
    "robot_collision_screening": "native continuation only for prepared OptiX count or pose-flag summaries",
    "barnes_hut_force_app": "native fixed-radius candidate summaries follow candidate rows; OptiX prepared threshold path covers node-coverage decision only",
    "apple_rt_demo": "outside NVIDIA RTX app table",
    "hiprt_ray_triangle_hitcount": "outside NVIDIA RTX app table",
}

NEXT_CLOUD_ACTION = {
    "ready_for_rtx_claim_review": "Goal1048/Goal1058 and Goal1135/Goal1136 RTX A5000 evidence remain historical validation context. Goal1164 collected a newer RTX A5000 smoke/medium batch, Goal1165 fixed local ANN/robot/Jaccard bottlenecks, Goal1166 prepared the next pod packet, Goal1177 accepted the recovered clean-source Goal1170 eight-row RTX A5000 batch as external-review input only, and Goal1184 accepted the newer Goal1182 RTX A4500 eight-row batch as external-review input only. This is bounded sub-path evidence, not whole-app speedup evidence, and it does not authorize new public wording.",
    "exclude_from_rtx_app_benchmark": "never include in NVIDIA RTX cloud batch",
}

GOAL1009_REVIEWED_PUBLIC_WORDING_ROWS = {
    "service_coverage_gaps": {
        "app_path": "service_coverage_gaps / prepared_gap_summary",
        "rtx_phase_sec": "0.136545",
        "ratio": "1.61x",
        "scope": "prepared gap-summary query/native sub-path only",
    },
    "event_hotspot_screening": {
        "app_path": "event_hotspot_screening / prepared_count_summary",
        "rtx_phase_sec": "0.165999",
        "ratio": "1.55x",
        "scope": "prepared count-summary query phase only",
    },
    "outlier_detection": {
        "app_path": "outlier_detection / prepared_fixed_radius_density_summary",
        "rtx_phase_sec": "0.122348",
        "ratio": "4.64x",
        "scope": "prepared fixed-radius scalar threshold-count sub-path only",
    },
    "dbscan_clustering": {
        "app_path": "dbscan_clustering / prepared_fixed_radius_core_flags",
        "rtx_phase_sec": "0.122921",
        "ratio": "6.62x",
        "scope": "prepared fixed-radius scalar core-count sub-path only",
    },
    "robot_collision_screening": {
        "app_path": "robot_collision_screening / prepared_pose_flags",
        "rtx_phase_sec": "0.178471",
        "ratio": "918.91x normalized per-pose",
        "scope": "prepared ray/triangle any-hit pose-count query sub-path only",
    },
    "facility_knn_assignment": {
        "app_path": "facility_knn_assignment / coverage_threshold_prepared_recentered",
        "rtx_phase_sec": "0.111619",
        "ratio": "80.60x",
        "scope": "prepared facility coverage-threshold query sub-path only",
    },
    "road_hazard_screening": {
        "app_path": "road_hazard_screening / prepared_native_compact_summary_40k",
        "rtx_phase_sec": "0.230652",
        "ratio": "3.53x",
        "scope": "prepared native road-hazard compact-summary traversal/count sub-path at 40k copies only",
    },
    "segment_polygon_hitcount": {
        "app_path": "segment_polygon_hitcount / segment_polygon_hitcount_native_experimental",
        "rtx_phase_sec": "0.146860",
        "ratio": "1.71x",
        "scope": "prepared native segment/polygon hit-count traversal only",
    },
    "segment_polygon_anyhit_rows": {
        "app_path": "segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate",
        "rtx_phase_sec": "0.192639",
        "ratio": "3.03x",
        "scope": "prepared bounded native pair-row traversal only",
    },
    "ann_candidate_search": {
        "app_path": "ann_candidate_search / candidate_threshold_prepared",
        "rtx_phase_sec": "0.105215",
        "ratio": "4.86x",
        "scope": "prepared ANN candidate-coverage decision sub-path only",
    },
    "barnes_hut_force_app": {
        "app_path": "barnes_hut_force_app / node_coverage_prepared_rich",
        "rtx_phase_sec": "0.222256",
        "ratio": "240.56x",
        "scope": "prepared Barnes-Hut node-coverage query sub-path only",
    },
    "hausdorff_distance": {
        "app_path": "hausdorff_distance / directed_threshold_prepared",
        "rtx_phase_sec": "0.122389",
        "ratio": "13.73x",
        "scope": "prepared Hausdorff <= radius threshold-decision traversal sub-path only",
    },
}


def _row(app: str) -> dict[str, Any]:
    readiness = rt.optix_app_benchmark_readiness(app)
    maturity = rt.rt_core_app_maturity(app)
    performance = rt.optix_app_performance_support(app)
    public_wording = rt.rtx_public_wording_status(app)
    app_matrix = rt.app_engine_support_matrix()[app]
    cloud_action = NEXT_CLOUD_ACTION.get(readiness.status, maturity.cloud_policy)
    if public_wording.status == "public_wording_blocked":
        cloud_action = maturity.cloud_policy
    if app == "polygon_pair_overlap_area_rows":
        cloud_action = maturity.cloud_policy
    return {
        "app": app,
        "app_path": APP_PATHS[app],
        "claim_command": CLAIM_COMMANDS[app],
        "rt_core_subpath": RT_CORE_SUBPATHS[app],
        "native_continuation_contract": NATIVE_CONTINUATION_CONTRACTS[app],
        "readiness_status": readiness.status,
        "rt_core_status": maturity.current_status,
        "performance_class": performance.performance_class,
        "public_wording_status": public_wording.status,
        "public_wording": public_wording.reviewed_wording,
        "public_wording_evidence": public_wording.evidence,
        "public_wording_boundary": public_wording.boundary,
        "evidence_or_goal": readiness.next_goal,
        "allowed_claim": readiness.allowed_claim,
        "non_claim_boundary": readiness.blocker,
        "cloud_action": cloud_action,
        "engine_support": {engine: support.status for engine, support in app_matrix.items()},
    }


def _merge_evidence(existing: str, extra: str) -> str:
    parts = existing.split("/") if existing else []
    for item in extra.split("/"):
        if item and item not in parts:
            parts.append(item)
    return "/".join(parts)


def _merge_boundary(primary: str, extra: str) -> str:
    if not extra or extra in primary:
        return primary
    if not primary or primary in extra:
        return extra
    return f"{primary} {extra}"


def build_status_page() -> dict[str, Any]:
    rows = [_row(app) for app in rt.public_apps()]
    ready_rows = [row for row in rows if row["readiness_status"] == "ready_for_rtx_claim_review"]
    non_target_rows = [row for row in rows if row["rt_core_status"] == "not_nvidia_rt_core_target"]
    public_wording_rows = rt.rtx_public_wording_matrix()
    reviewed_wording_rows = [
        app for app, row in public_wording_rows.items() if row.status == "public_wording_reviewed"
    ]
    blocked_wording_rows = [
        app for app, row in public_wording_rows.items() if row.status == "public_wording_blocked"
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "source_of_truth": {
            "apps": "rtdsl.public_apps()",
            "engine_support": "rtdsl.app_engine_support_matrix()",
            "readiness": "rtdsl.optix_app_benchmark_readiness_matrix()",
            "maturity": "rtdsl.rt_core_app_maturity_matrix()",
            "public_wording": "rtdsl.rtx_public_wording_matrix()",
        },
        "summary": {
            "public_app_count": len(rows),
            "ready_for_rtx_claim_review": len(ready_rows),
            "not_nvidia_rt_core_target": len(non_target_rows),
            "reviewed_public_wording": len(reviewed_wording_rows),
            "blocked_public_wording": len(blocked_wording_rows),
            "public_speedup_claim_authorized": False,
            "broad_or_whole_app_public_speedup_claim_authorized": False,
        },
        "reviewed_public_wording_rows": [
            GOAL1009_REVIEWED_PUBLIC_WORDING_ROWS[app]
            for app in GOAL1009_REVIEWED_PUBLIC_WORDING_ROWS
            if app in reviewed_wording_rows
        ],
        "rows": rows,
        "boundary": (
            "This page is the public v1.0 RTX app status index. It lists bounded "
            "NVIDIA OptiX/RTX claim-review candidates and non-claim boundaries. "
            "It is not release authorization and not a public speedup claim."
        ),
    }


def _md_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def to_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# v1.0 RTX App Status",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- public app rows: `{summary['public_app_count']}`",
        f"- NVIDIA-target rows ready for claim review: `{summary['ready_for_rtx_claim_review']}`",
        f"- non-NVIDIA target rows: `{summary['not_nvidia_rt_core_target']}`",
        f"- reviewed public RTX sub-path wording rows: `{summary['reviewed_public_wording']}`",
        f"- broad or whole-app public speedup claim authorized: `{summary['broad_or_whole_app_public_speedup_claim_authorized']}`",
        f"- post-Goal1048 validated RTX artifact intake completed (Goal1058): `True`",
        f"- changed-path RTX artifact intake completed (Goal1135/Goal1136): `True`",
        f"- latest RTX pod batch and local follow-up completed (Goal1164/Goal1165): `True`",
        f"- next RTX pod packet accepted by 2-AI review (Goal1166): `True`",
        f"- recovered clean-source Goal1170 RTX batch accepted for external-review input (Goal1177): `True`",
        f"- newer Goal1182 RTX A4500 batch accepted for external-review input (Goal1184): `True`",
        f"- repaired RTX evidence merged and road-hazard wording reviewed (Goal1206/Goal1208): `True`",
        f"- graph/Hausdorff wording resolved by Goal1224 and polygon-pair promoted by Goal1263: `True`",
        "",
        "Use this page as the release-facing source of truth for app-level RTX claim review. For engine-by-engine details, see `docs/app_engine_support_matrix.md`.",
        "Goal1048 completed the consolidated RTX rerun on an RTX A5000 from commit `0c79b64d1b71383080f2e8572612488796d1c16c`. Goal1058 added a tracked-only archive rerun from commit `21fa036881bf9a0c806f69c15727d87b482ccfcf` and validated the facility and robot diagnostic rows with oracle parity. Goal1121/Goal1123/Goal1126 are public-wording context for facility, robot, and Barnes-Hut; Goal1142 collected same-source replacement evidence, and Goal1142/Goal1143 Gemini review accepted the evidence review. Goal1146 re-promoted facility and Barnes-Hut with bounded current-source public wording, and Goal1126 promoted robot only with explicit normalized per-pose wording. Goal1135/Goal1136 added changed-path RTX A5000 artifacts for DB compact summary, graph visibility edges, road hazard, polygon pair overlap, polygon set Jaccard, and Hausdorff threshold gates. Goal1164 added a newer RTX A5000 smoke/medium batch: all smoke rows passed, ANN and robot exposed large-scale timing bottlenecks, and Jaccard had historical chunk evidence at 512-4096 while 256/8192 remained diagnostic boundaries; Goal1262 supersedes that operational policy and uses chunk 1024 as the current safe default. Goal1165 made local ANN/robot/Jaccard follow-up fixes, and Goal1166 accepted the next pod packet by Codex+Gemini review. Goal1177 then accepted the recovered clean-source staged-archive Goal1170 eight-row RTX A5000 batch as external-review input only after documenting the initial missing-manifest failure, manifest-generation recovery, and Gemini ACCEPT review. Goal1184 accepted the newer Goal1182 RTX A4500 eight-row batch as external-review input only after SHA-matched copy-back and valid local intake. Goal1206 merged repaired RTX pod evidence with Embree4 recovery controls, and Goal1208/Claude review authorized only the bounded road-hazard prepared native compact-summary wording. Goal1224 promoted Hausdorff and kept graph blocked; Goal1263 then promoted bounded polygon-pair wording for RT-assisted LSI/PIP positive candidate discovery plus exact area continuation. Current main also has internal v1.5 backend-neutral native polygon area/set-area summary plumbing, but public wording remains limited to reviewed bounded sub-paths. Only validated/strict bounded paths may be described as claim-review evidence, and most rows remain bounded prepared sub-path or native-assisted phase evidence, not whole-app speedup.",
        "",
        "## Reviewed Public RTX Sub-Path Wording",
        "",
        "The following rows have passed bounded wording review for prepared",
        "RTX A5000 query/native sub-path wording. These are not whole-app, default-mode,",
        "Python-postprocess, or broad RT-core acceleration claims:",
        "",
        "| App/path | RTX phase (s) | Ratio | Scope |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in payload["reviewed_public_wording_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_md_escape(row['app_path'])}`",
                    f"`{_md_escape(row['rtx_phase_sec'])}`",
                    f"`{_md_escape(row['ratio'])}`",
                    _md_escape(row["scope"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "`facility_knn_assignment` and `barnes_hut_force_app` were re-promoted by Goal1146",
            "with current-source same-contract wording. `robot_collision_screening` was promoted",
            "by Goal1126 with explicit normalized per-pose wording only; it is not a",
            "same-total-work wall-time claim and not a whole-app robot-planning claim.",
            "Other `ready_for_rtx_claim_review` rows remain engineering-ready or",
            "claim-review-ready, but do not yet have reviewed public speedup wording.",
            "Goal1177 does not add a new reviewed public wording row.",
            "Goal1184 does not add a new reviewed public wording row.",
            "Goal1208 adds exactly one reviewed public wording row for the bounded road-hazard prepared native compact-summary sub-path.",
            "Goal1224 resolves graph and Hausdorff; Goal1263 promotes bounded polygon-pair wording. Graph remains blocked.",
            "",
        "## Status Table",
        "",
        "| App | Status | RT-core subpath | Native-continuation contract | Claim command | Evidence | What is not claimed | Cloud action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        readiness_status = row["readiness_status"]
        evidence_or_goal = row["evidence_or_goal"]
        non_claim_boundary = row["non_claim_boundary"]
        if row["public_wording_status"] == "public_wording_reviewed":
            evidence_or_goal = _merge_evidence(evidence_or_goal, row["public_wording_evidence"])
        if row["public_wording_status"] == "public_wording_blocked":
            readiness_status = "blocked_for_public_speedup_wording"
            evidence_or_goal = _merge_evidence(evidence_or_goal, row["public_wording_evidence"])
            non_claim_boundary = _merge_boundary(
                row["public_wording_boundary"],
                row["non_claim_boundary"],
            )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_md_escape(row['app_path'])}`",
                    f"`{_md_escape(row['rt_core_status'])}` / `{_md_escape(readiness_status)}`",
                    _md_escape(row["rt_core_subpath"]),
                    _md_escape(row["native_continuation_contract"]),
                    f"`{_md_escape(row['claim_command'])}`",
                    _md_escape(evidence_or_goal),
                    _md_escape(non_claim_boundary),
                    _md_escape(row["cloud_action"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Allowed Wording",
            "",
            "RTDL includes a bounded NVIDIA OptiX/RTX-backed subpath for `<app>`: `<allowed claim>`. The claim covers that named traversal/summary phase only; excluded Python, validation, postprocess, exact refinement, ranking, row-materialization, or whole-app work remains outside the claim.",
            "",
            "## Forbidden Wording",
            "",
            "- RTDL accelerates the whole app.",
            "- RTDL beats CPU, Embree, PostGIS, or another baseline for an app unless a later same-semantics review explicitly authorizes that specific wording.",
            "- All graph, database, or spatial work is RT-core accelerated.",
            "- Polygon area or Jaccard refinement is fully native OptiX.",
            "- `--backend optix` alone means RT cores were used.",
            "",
            "## Source Of Truth",
            "",
        ]
    )
    for key, value in payload["source_of_truth"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the public v1.0 RTX app status page.")
    parser.add_argument("--output-json", default="docs/reports/goal947_v1_rtx_app_status_2026-04-25.json")
    parser.add_argument("--output-md", default="docs/v1_0_rtx_app_status.md")
    args = parser.parse_args(argv)

    payload = build_status_page()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload).rstrip() + "\n", encoding="utf-8")
    print(json.dumps({"json": str(output_json), "md": str(output_md)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
