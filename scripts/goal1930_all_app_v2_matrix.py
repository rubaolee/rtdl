#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]


APP_ROWS = (
    {
        "app": "database_analytics",
        "family": "E-columnar-database-analytics",
        "v2_state": "bounded-partner-row",
        "v2_contract": "CuPy RawKernel predicate scan plus grouped count/sum continuation over Python-owned column payloads",
        "comparison_status": "pod-evidence-collected-bounded",
        "v18_reference": "scripts/goal756_db_prepared_session_perf.py",
        "v2_evidence": "docs/reports/goal1957_partner_identity_payload_pod_retest_2026-05-14.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1955_rawkernel_control_app_perf.py --apps database_analytics --copies 100000 --partner cupy --repeats 3 --warmups 1",
        "claim_class": "bounded-implemented",
        "analysis_hint": "The RawKernel v2 row is fast and correct, but the next generalization is a reusable partner grouped-reduction adapter rather than app-local DB code.",
    },
    {
        "app": "graph_analytics",
        "family": "F-graph-split-rows",
        "v2_state": "bounded-closed-form-row",
        "v2_contract": "CuPy RawKernel summary for the authored replicated graph case; not a generic graph traversal/triangle engine",
        "comparison_status": "pod-evidence-collected-bounded",
        "v18_reference": "scripts/goal982_graph_same_scale_timing_repair.py",
        "v2_evidence": "docs/reports/goal1957_partner_identity_payload_pod_retest_2026-05-14.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1955_rawkernel_control_app_perf.py --apps graph_analytics --copies 1000 --partner cupy --repeats 3 --warmups 1",
        "claim_class": "bounded-closed-form",
        "analysis_hint": "The authored app is fast, but this remains the largest semantic debt: no reusable partner graph primitive for frontier traversal, triangle counting, or visibility-edge aggregation.",
    },
    {
        "app": "service_coverage_gaps",
        "family": "A-fixed-radius-threshold",
        "v2_state": "implemented-and-pod-timed",
        "v2_contract": "prepared OptiX fixed-radius counts plus partner threshold flags",
        "comparison_status": "pod-evidence-collected",
        "v18_reference": "goal1903 fixed-radius v1.8 baseline",
        "v2_evidence": "docs/reports/goal1903_fixed_radius_batch_pod.json",
        "next_command": "covered by scripts/goal1903_v2_partner_pod_batch_runner.sh",
        "claim_class": "implemented",
        "analysis_hint": "Positive rows are expected when prepared reuse and partner-owned threshold outputs amortize dispatch and transfer cost.",
    },
    {
        "app": "event_hotspot_screening",
        "family": "A-fixed-radius-threshold",
        "v2_state": "implemented-and-pod-timed",
        "v2_contract": "prepared OptiX fixed-radius counts plus partner hotspot flags",
        "comparison_status": "pod-evidence-collected",
        "v18_reference": "goal1903 fixed-radius v1.8 baseline",
        "v2_evidence": "docs/reports/goal1903_fixed_radius_batch_pod.json",
        "next_command": "covered by scripts/goal1903_v2_partner_pod_batch_runner.sh",
        "claim_class": "implemented",
        "analysis_hint": "This row should track the fixed-radius primitive shape; small cases can still be setup-bound.",
    },
    {
        "app": "facility_knn_assignment",
        "family": "A-fixed-radius-threshold",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "coverage-threshold decision using prepared OptiX fixed-radius counts and partner columns; not ranked KNN assignment",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1925_fixed_radius_family_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py --apps facility_knn_assignment --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "The honest row is coverage/threshold. Ranked KNN ordering is outside this adapter.",
    },
    {
        "app": "road_hazard_screening",
        "family": "C-segment-polygon-count-derived-flags",
        "v2_state": "implemented-and-pod-timed",
        "v2_contract": "prepared generic ray/primitive witness counts plus partner priority flags",
        "comparison_status": "pod-evidence-collected",
        "v18_reference": "goal1889 prepared reuse baseline",
        "v2_evidence": "docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json",
        "next_command": "covered by scripts/goal1903_v2_partner_pod_batch_runner.sh",
        "claim_class": "implemented",
        "analysis_hint": "Prepared reuse at larger rows is the meaningful comparison; 512-row behavior is overhead-sensitive.",
    },
    {
        "app": "segment_polygon_hitcount",
        "family": "C-segment-polygon-count-derived-flags",
        "v2_state": "implemented-and-pod-timed",
        "v2_contract": "generic witness rows counted into partner-owned hit-count columns",
        "comparison_status": "pod-evidence-collected",
        "v18_reference": "goal1903 segment/polygon v1.8 baseline",
        "v2_evidence": "docs/reports/goal1903_segment_polygon_batch_pod_2048.json",
        "next_command": "covered by scripts/goal1903_v2_partner_pod_batch_runner.sh",
        "claim_class": "implemented",
        "analysis_hint": "The improvement depends on avoiding host row materialization and reusing prepared triangle state.",
    },
    {
        "app": "segment_polygon_anyhit_rows",
        "family": "B-ray-triangle-anyhit-rows",
        "v2_state": "implemented-rerun-needed",
        "v2_contract": "generic ray/primitive witness rows through partner-owned input columns",
        "comparison_status": "needs-current-pod-rerun",
        "v18_reference": "scripts/goal1856_segment_polygon_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1856_segment_polygon_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1856_segment_polygon_v2_partner_perf.py --count 2048 --iterations 5 --partners cupy,torch --output docs/reports/goal1856_segment_polygon_v2_partner_perf_pod_current_2048.json",
        "claim_class": "implemented-needs-current-hardware",
        "analysis_hint": "This is row-output materialization, so it may lag compact count/flag rows even though the native RT discovery is generic.",
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "family": "D-polygon-exact-metric-continuation",
        "v2_state": "bounded-partner-row",
        "v2_contract": "OptiX candidate discovery plus CuPy identity-payload extent continuation for authored axis-aligned bounded shapes",
        "comparison_status": "pod-evidence-collected-bounded",
        "v18_reference": "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
        "v2_evidence": "docs/reports/goal1957_partner_identity_payload_pod_retest_2026-05-14.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1955_rawkernel_control_app_perf.py --apps polygon_pair_overlap_area_rows --copies 2048 --partner cupy --candidate-backend optix --repeats 3 --warmups 1",
        "claim_class": "bounded-implemented",
        "analysis_hint": "Goal1957 fixes the dense-mask handoff with compact identity-payload columns; still bounded to authored axis-aligned shapes and currently near-parity/slower than v1.8, not arbitrary polygon overlay.",
    },
    {
        "app": "polygon_set_jaccard",
        "family": "D-polygon-exact-metric-continuation",
        "v2_state": "bounded-partner-row",
        "v2_contract": "OptiX candidate discovery plus CuPy identity-payload extent continuation for authored axis-aligned bounded-shape set Jaccard",
        "comparison_status": "pod-evidence-collected-bounded",
        "v18_reference": "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
        "v2_evidence": "docs/reports/goal1957_partner_identity_payload_pod_retest_2026-05-14.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1955_rawkernel_control_app_perf.py --apps polygon_set_jaccard --copies 2048 --partner cupy --candidate-backend optix --repeats 3 --warmups 1",
        "claim_class": "bounded-implemented",
        "analysis_hint": "Goal1957 fixes the dense-mask handoff with compact identity-payload columns; still bounded to authored axis-aligned shapes and near parity rather than a clean speedup.",
    },
    {
        "app": "hausdorff_distance",
        "family": "A-fixed-radius-threshold",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "non-degenerate fixed-radius nearest-candidate threshold decision, not exact Hausdorff ranking",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1925_fixed_radius_family_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py --apps hausdorff_distance --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "This is a thresholded nearest-candidate workload. Exact directed Hausdorff max-distance remains a different app continuation.",
    },
    {
        "app": "ann_candidate_search",
        "family": "A-fixed-radius-threshold",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "fixed-radius candidate coverage decision; not an ANN index such as HNSW or FAISS",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1925_fixed_radius_family_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py --apps ann_candidate_search --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "The row tests candidate coverage, not arbitrary nearest-neighbor indexing.",
    },
    {
        "app": "outlier_detection",
        "family": "A-fixed-radius-threshold",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "fixed-radius neighbor count threshold flags in partner columns",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1925_fixed_radius_family_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py --apps outlier_detection --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "The v2 output should be compact flags/counts; host materialized row lists would erase much of the point.",
    },
    {
        "app": "dbscan_clustering",
        "family": "A-fixed-radius-threshold",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "core-point count/threshold flags; full cluster expansion remains app logic",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1925_fixed_radius_family_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py --apps dbscan_clustering --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "Only the RTDL neighbor/core test is accelerated; transitive cluster labeling is not yet a partner graph algorithm.",
    },
    {
        "app": "robot_collision_screening",
        "family": "B-ray-triangle-anyhit-flags",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "prepared generic any-hit ray flags reduced to partner-owned pose collision flags",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1928_robot_collision_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1928_robot_collision_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1928_robot_collision_v2_partner_perf.py --pose-count 4096 --obstacle-count 256 --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "The important correctness check is exact pose-flag parity, not just colliding-pose count parity.",
    },
    {
        "app": "barnes_hut_force_app",
        "family": "A-fixed-radius-threshold",
        "v2_state": "harness-ready-pod-needed",
        "v2_contract": "fixed-radius node coverage decision; force-vector accumulation remains app logic",
        "comparison_status": "needs-pod-timing",
        "v18_reference": "scripts/goal1925_fixed_radius_family_v2_partner_perf.py",
        "v2_evidence": "docs/reports/goal1925_fixed_radius_family_v2_partner_perf_2026-05-13.md",
        "next_command": "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py --apps barnes_hut_force_app --partners cupy,torch --repeat 5",
        "claim_class": "implemented-needs-hardware",
        "analysis_hint": "This covers spatial node coverage, not a full Barnes-Hut force-vector GPU solver.",
    },
)


def _git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    value = completed.stdout.strip()
    return value or "unknown"


def build_matrix() -> dict[str, object]:
    rows = [dict(row) for row in APP_ROWS]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["comparison_status"]] = counts.get(row["comparison_status"], 0) + 1
    blockers = []
    if counts.get("needs-pod-timing", 0) or counts.get("needs-current-pod-rerun", 0):
        blockers.append("current RTX pod timing is missing for harness-ready rows")
    if counts.get("evidence-only-control", 0):
        blockers.append("control/fallback rows cannot be marketed as v2 partner speedups")
    return {
        "goal": "Goal1930",
        "status": "all-app-rows-classified-final-pod-batch-needed",
        "git_commit": _git_commit(),
        "row_count": len(rows),
        "rows": rows,
        "counts_by_comparison_status": counts,
        "blockers": blockers,
        "final_pod_batch_needed": True,
        "release_claim_boundary": {
            "v2_0_release_authorized": False,
            "all_apps_have_a_row_decision": True,
            "all_apps_have_measured_v2_speedup": False,
            "whole_app_speedup_claim_authorized": False,
            "control_rows_are_release_speedup_evidence": False,
        },
    }


def to_markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    assert isinstance(rows, list)
    lines = [
        "# Goal1930 - All-App v2 Matrix and v1.8 Comparison Packet",
        "",
        "Status: all-app-rows-classified-final-pod-batch-needed",
        "",
        "Date: 2026-05-13",
        "",
        "Goal1930 converts the v2.0 all-app discussion into a concrete row matrix. It does not claim v2.0 release readiness. The point is to make every app either implemented, harness-ready, rerun-needed, or explicitly marked as an evidence-only control/fallback row before the final RTX pod batch.",
        "",
        "## Summary",
        "",
        f"- row count: `{payload['row_count']}`",
        f"- comparison status counts: `{json.dumps(payload['counts_by_comparison_status'], sort_keys=True)}`",
        "- release authorized: `False`",
        "- whole-app speedup claim authorized: `False`",
        "",
        "## App Rows",
        "",
        "| App | Family | v2 state | Comparison status | Claim class |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            f"| `{row['app']}` | `{row['family']}` | `{row['v2_state']}` | `{row['comparison_status']}` | `{row['claim_class']}` |"
        )
    lines.extend(
        [
            "",
            "## Control Rows",
            "",
            "The following rows are deliberately evidence-only controls for now, not v2 partner speedup rows:",
            "",
        ]
    )
    for row in rows:
        assert isinstance(row, dict)
        if row["comparison_status"] == "evidence-only-control":
            lines.append(f"- `{row['app']}`: {row['analysis_hint']}")
    lines.extend(
        [
            "",
            "## Final Pod Batch Commands",
            "",
            "Run the harness-ready rows on RTX hardware with progress output:",
            "",
            "```bash",
            "PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py \\",
            "  --apps facility_knn_assignment,hausdorff_distance,ann_candidate_search,outlier_detection,dbscan_clustering,barnes_hut_force_app \\",
            "  --partners cupy,torch --repeat 5 \\",
            "  --output docs/reports/goal1925_fixed_radius_family_v2_partner_perf_pod.json",
            "",
            "PYTHONPATH=src:. python3 scripts/goal1928_robot_collision_v2_partner_perf.py \\",
            "  --pose-count 4096 --obstacle-count 256 --partners cupy,torch --repeat 5 \\",
            "  --output docs/reports/goal1928_robot_collision_v2_partner_perf_pod.json",
            "",
            "PYTHONPATH=src:. python3 scripts/goal1856_segment_polygon_v2_partner_perf.py \\",
            "  --count 2048 --iterations 5 --partners cupy,torch \\",
            "  --output docs/reports/goal1856_segment_polygon_v2_partner_perf_pod_current_2048.json",
            "```",
            "",
            "## Analysis Rule",
            "",
            "The final report must compare v1.8 and v2.0 row by row, but it must not collapse implemented rows and control rows into one marketing claim. Positive rows explain amortized prepared reuse and partner-owned outputs; negative or neutral rows explain setup overhead, host materialization, or exact app continuation dominating the RT subpath.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the all-app v2 matrix packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1930_all_app_v2_matrix_2026-05-13.json")
    parser.add_argument("--output-md", default="docs/reports/goal1930_all_app_v2_matrix_2026-05-13.md")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = build_matrix()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
