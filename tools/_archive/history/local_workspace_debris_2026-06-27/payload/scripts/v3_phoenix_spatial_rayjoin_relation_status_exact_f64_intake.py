from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NEW_EVIDENCE = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/"
    / "relation_status_exact_f64_repeat50_sample5.json"
)
NEW_SMOKE = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/"
    / "relation_status_exact_f64_smoke.json"
)
BUILD_LOG = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/"
    / "build-optix.log"
)
SOURCE_MANIFEST = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/"
    / "source_manifest.sha256"
)
OLD_EXACT_EVIDENCE = (
    ROOT
    / "docs/rebuild/v3/evidence/"
    / "phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/"
    / "summary.json"
)
OLD_NO_GO = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.json"
NATIVE_SOURCE = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0.0:
        return 0.0
    return float(numerator) / float(denominator)


def build_packet() -> dict[str, Any]:
    new = _load_json(NEW_EVIDENCE)
    smoke = _load_json(NEW_SMOKE)
    old_exact = _load_json(OLD_EXACT_EVIDENCE)
    old_no_go = _load_json(OLD_NO_GO)
    native_source = NATIVE_SOURCE.read_text(encoding="utf-8")
    build_log = BUILD_LOG.read_text(encoding="utf-8")

    new_summary = new["summary"]
    old_summary = old_exact["summary"]
    new_phases = new_summary["m3_phase_sec_medians"]
    old_phases = old_summary["m3_phase_sec_medians"]
    first_native = new["samples"][0]["native_phase_timings"]

    checks = {
        "new_evidence_exists": NEW_EVIDENCE.exists(),
        "new_smoke_exists": NEW_SMOKE.exists(),
        "build_log_exists": BUILD_LOG.exists(),
        "build_succeeded": "build_exit=0" in build_log,
        "source_manifest_exists": SOURCE_MANIFEST.exists(),
        "native_source_uses_exact_f64_full_predicate": "exact_closed_shape_membership_f64" in native_source,
        "native_source_no_longer_keeps_status_one_without_exact_check": "bool keep = relation_status == 1u" not in native_source,
        "smoke_exact_count_matches": int(smoke["summary"]["row_count"]) == 47262,
        "repeat_exact_count_matches": int(new_summary["row_count"]) == 47262,
        "row_count_consistent": bool(new_summary["row_count_consistent"]),
        "full_m3_phase_table_complete": bool(new_summary["full_m3_phase_table_complete_all_samples"]),
        "failed_checks_empty": not new.get("failed_checks"),
        "claim_flags_false": not any(
            bool(new.get(key))
            for key in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "row_scoped_public_speedup_claim_authorized",
                "broad_v3_faster_than_v2_claim_authorized",
                "rtdl_beats_rayjoin_claim_authorized",
                "paper_reproduction_claim_authorized",
                "true_zero_copy_claim_authorized",
                "v4_embedding_claim_authorized",
                "whole_app_speedup_claim_authorized",
            )
        ),
        "native_scalar_count_no_row_stream": not bool(first_native["row_stream_materialized"]),
        "native_exact_device_scalar_count": bool(first_native["native_exact_device_scalar_count_produced"]),
        "old_no_go_retained": old_no_go["status"] == "spatial_rayjoin_relation_status_corrected_executor_no_go_exact_mismatch",
        "old_no_go_added_no_m7_rows": int(old_no_go["m7_qualified_release_rows_added"]) == 0,
    }

    failed_checks = [name for name, passed in checks.items() if not passed]

    prepared_query_speedup = _ratio(
        float(old_summary["prepared_query_sec_median"]),
        float(new_summary["prepared_query_sec_median"]),
    )
    prepared_total_speedup = _ratio(
        float(old_summary["prepared_query_total_sec_median"]),
        float(new_summary["prepared_query_total_sec_median"]),
    )
    runner_wall_speedup = _ratio(
        float(old_summary["runner_wall_sec_median"]),
        float(new_summary["runner_wall_sec_median"]),
    )

    return {
        "tool": "v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake",
        "status": "spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7",
        "generic_capability": "point_location_topology_stream",
        "dataset": new["dataset"],
        "gpu": new["environment"]["nvidia_smi"],
        "count_mode": new["count_mode"],
        "old_no_go_status": old_no_go["status"],
        "old_no_go_candidate_minus_exact": int(old_no_go["candidate_minus_exact"]),
        "current_exact_count": int(new_summary["row_count"]),
        "current_row_count_consistent": bool(new_summary["row_count_consistent"]),
        "current_failed_checks": new.get("failed_checks", []),
        "new_evidence": str(NEW_EVIDENCE.relative_to(ROOT)).replace("\\", "/"),
        "new_smoke": str(NEW_SMOKE.relative_to(ROOT)).replace("\\", "/"),
        "old_exact_executor_evidence": str(OLD_EXACT_EVIDENCE.relative_to(ROOT)).replace("\\", "/"),
        "old_no_go_packet": str(OLD_NO_GO.relative_to(ROOT)).replace("\\", "/"),
        "build_log": str(BUILD_LOG.relative_to(ROOT)).replace("\\", "/"),
        "source_manifest": str(SOURCE_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "m3_phase_sec_medians": new_phases,
        "old_exact_executor_m3_phase_sec_medians": old_phases,
        "native_phase_timings_first_sample": first_native,
        "comparison_vs_exact_executor": {
            "prepared_query_sec_old_exact_executor": float(old_summary["prepared_query_sec_median"]),
            "prepared_query_sec_exact_f64_device_scalar": float(new_summary["prepared_query_sec_median"]),
            "prepared_query_speedup_vs_exact_executor": prepared_query_speedup,
            "prepared_query_total_sec_old_exact_executor": float(old_summary["prepared_query_total_sec_median"]),
            "prepared_query_total_sec_exact_f64_device_scalar": float(new_summary["prepared_query_total_sec_median"]),
            "prepared_query_total_speedup_vs_exact_executor": prepared_total_speedup,
            "runner_wall_sec_old_exact_executor": float(old_summary["runner_wall_sec_median"]),
            "runner_wall_sec_exact_f64_device_scalar": float(new_summary["runner_wall_sec_median"]),
            "runner_wall_speedup_vs_exact_executor": runner_wall_speedup,
            "old_topology_continuation_sec": float(old_phases["topology_continuation_sec"]),
            "new_topology_continuation_sec": float(new_phases["topology_continuation_sec"]),
            "old_rt_traversal_sec": float(old_phases["rt_traversal_sec"]),
            "new_rt_traversal_sec": float(new_phases["rt_traversal_sec"]),
        },
        "interpretation": (
            "The prior relation-status route failed because it could not recover float32 device-prefilter "
            "false negatives. The current native source uses a device-side double full closed-shape predicate "
            "for each AABB candidate, which restores exact public-county parity and removes host topology "
            "continuation from the prepared query path. This is generic engine progress, not release or M7 "
            "authorization."
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "m7_qualified_release_rows_added": 0,
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "next_engine_action": (
            "Seek external review for the exact-f64 native scalar-count intake, then decide whether this can "
            "become a narrow Spatial topology-stream M7 candidate after author-basis and wording gates."
        ),
        "goal_level_decision_audit": {
            "decision": (
                "Treat the exact-f64 relation-status scalar-count repair as a new Phoenix intake, not an "
                "automatic M7 promotion."
            ),
            "was_i_foolish": (
                "No. The old route failed exactness; the repair changed the generic device predicate semantics "
                "and reran real POD evidence before any promotion."
            ),
            "foolish_actions": (
                "The foolish action would be to erase the old no-go, claim the smoke run as release evidence, "
                "or describe the row as RTDL beating RayJoin without author-basis review."
            ),
            "other_path": (
                "I could have abandoned Spatial after the no-go and tuned another app. That would avoid risk but "
                "would leave a known generic topology-stream bottleneck unsolved."
            ),
            "different_path_now": (
                "Keep the route behind not-M7 gates, request 2-AI review, and only then consider a narrow "
                "row-scoped candidate."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    comparison = packet["comparison_vs_exact_executor"]
    native = packet["native_phase_timings_first_sample"]
    lines = [
        "# Phoenix V3 Spatial Relation-Status Exact-F64 Intake",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This is an intake packet, not release authorization and not an M7 promotion.",
        "",
        "## What Changed",
        "",
        "- Previous relation-status corrected executor failed exact validation: "
        f"candidate minus exact `{packet['old_no_go_candidate_minus_exact']}`.",
        "- Current native source uses `exact_closed_shape_membership_f64` on the device for each AABB candidate.",
        "- Current public-county POD repeat50/sample5 evidence is exact and stable at "
        f"`{packet['current_exact_count']}` rows.",
        "- Full M3 phase table is present and all public/release claim flags remain false.",
        "",
        "## Evidence",
        "",
        f"- New repeat packet: `{packet['new_evidence']}`",
        f"- New smoke packet: `{packet['new_smoke']}`",
        f"- Build log: `{packet['build_log']}`",
        f"- Source manifest: `{packet['source_manifest']}`",
        f"- Previous exact-executor packet: `{packet['old_exact_executor_evidence']}`",
        f"- Previous no-go packet retained: `{packet['old_no_go_packet']}`",
        "",
        "## Comparison Against Exact Executor",
        "",
        "| Metric | Exact executor | Exact-f64 device scalar | Ratio |",
        "| --- | ---: | ---: | ---: |",
        (
            "| Prepared query median | "
            f"{comparison['prepared_query_sec_old_exact_executor']:.9f}s | "
            f"{comparison['prepared_query_sec_exact_f64_device_scalar']:.9f}s | "
            f"{comparison['prepared_query_speedup_vs_exact_executor']:.3f}x |"
        ),
        (
            "| Prepared query repeat total | "
            f"{comparison['prepared_query_total_sec_old_exact_executor']:.9f}s | "
            f"{comparison['prepared_query_total_sec_exact_f64_device_scalar']:.9f}s | "
            f"{comparison['prepared_query_total_speedup_vs_exact_executor']:.3f}x |"
        ),
        (
            "| Runner wall median | "
            f"{comparison['runner_wall_sec_old_exact_executor']:.9f}s | "
            f"{comparison['runner_wall_sec_exact_f64_device_scalar']:.9f}s | "
            f"{comparison['runner_wall_speedup_vs_exact_executor']:.3f}x |"
        ),
        (
            "| Topology continuation median | "
            f"{comparison['old_topology_continuation_sec']:.9f}s | "
            f"{comparison['new_topology_continuation_sec']:.9f}s | n/a |"
        ),
        "",
        "## Native First-Sample Counters",
        "",
        f"- Raw AABB candidate count: `{native['raw_candidate_count']}`",
        f"- Boundary-status candidate count: `{native['boundary_candidate_count']}`",
        f"- Dropped by exact-f64 predicate: `{native['dropped_candidate_count']}`",
        f"- Emitted exact count: `{native['emitted_count']}`",
        f"- Row stream materialized: `{native['row_stream_materialized']}`",
        "",
        "## Claim Boundary",
        "",
        "- M7 rows added: `0`",
        "- Release authorized: `false`",
        "- Public speedup claim authorized: `false`",
        "- Broad V3-over-V2 claim authorized: `false`",
        "- RTDL-beats-RayJoin claim authorized: `false`",
        "- True zero-copy claim authorized: `false`",
        "",
        "## Checks",
        "",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"- `{name}`: `{str(bool(passed)).lower()}`")
    lines.extend(
        [
            "",
            f"Failed checks: `{packet['failed_checks']}`",
            "",
            "## Interpretation",
            "",
            packet["interpretation"],
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {packet['goal_level_decision_audit']['decision']}",
            "",
            f"1. Was I foolish? {packet['goal_level_decision_audit']['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {packet['goal_level_decision_audit']['foolish_actions']}",
            f"3. Was there another path? {packet['goal_level_decision_audit']['other_path']}",
            f"4. Can I now try a different path? {packet['goal_level_decision_audit']['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    print(json.dumps({"status": packet["status"], "failed_checks": packet["failed_checks"]}, indent=2))


if __name__ == "__main__":
    main()
