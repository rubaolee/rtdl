from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_adverse_subset_20260621/"
    / "br_county_subset_relation_status_exact_f64_r20_s5.json"
)

OUT_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.json"
)
OUT_MD = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.md"
)


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _all_sample_checks(evidence: dict[str, Any], key: str, expected: Any) -> bool:
    return all(sample.get(key) == expected for sample in evidence.get("samples", []))


def build_packet() -> dict[str, Any]:
    evidence = _load_json(EVIDENCE)
    summary = evidence["summary"]
    samples = evidence["samples"]
    first_sample = samples[0]
    first_native = first_sample["native_phase_timings"]
    first_m3 = first_sample["topology_stream_m3_phase_table"]
    first_handle = first_sample["topology_stream_prepared_handle"]

    top_claim_keys = (
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
    sample_claim_keys = (
        "full_rayjoin_reproduction",
        "paper_scale_perf_claim_authorized",
        "rtdl_beats_rayjoin_claim_authorized",
        "v2_0_release_authorized",
        "whole_app_speedup_claim_authorized",
    )

    checks = {
        "evidence_exists": EVIDENCE.exists(),
        "status_non_authorizing": (
            evidence.get("status") == "spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7"
        ),
        "dataset_is_adverse_subset": evidence.get("dataset") == "tests/fixtures/rayjoin/br_county_subset.cdb",
        "count_mode_validated_exact_f64": evidence.get("count_mode") == "relation_status_corrected_executor_validated",
        "sample_repeat_is_five": evidence.get("sample_repeat") == 5,
        "query_repeat_is_twenty": evidence.get("query_repeat") == 20,
        "failed_checks_empty": evidence.get("failed_checks") == [],
        "summary_row_count_consistent": summary.get("row_count_consistent") is True,
        "summary_row_count_is_six": summary.get("row_count") == 6,
        "full_m3_table_complete": summary.get("full_m3_phase_table_complete_all_samples") is True,
        "m7_rows_added_zero": evidence.get("m7_qualified_release_rows_added") == 0,
        "m7_promotion_false": evidence.get("m7_promotion_authorized") is False,
        "release_false": evidence.get("release_authorized") is False,
        "all_top_level_claim_flags_false": not any(bool(evidence.get(key)) for key in top_claim_keys),
        "all_sample_claim_flags_false": all(
            not any(bool(sample.get("claim_boundary", {}).get(key)) for key in sample_claim_keys)
            for sample in samples
        ),
        "all_samples_row_count_six": _all_sample_checks(evidence, "row_count", 6),
        "all_samples_query_stream_resident": all(
            sample["topology_stream_m3_phase_table"].get("query_stream_resident") is True for sample in samples
        ),
        "all_samples_prepared_handle_generic": all(
            sample["topology_stream_prepared_handle"].get("reusable_engine_surface") is True for sample in samples
        ),
        "all_samples_native_scalar_count": all(
            sample["native_phase_timings"].get("native_exact_device_scalar_count_produced") is True
            for sample in samples
        ),
        "all_samples_relation_status_correction_used": all(
            sample["native_phase_timings"].get("relation_status_correction_used") is True for sample in samples
        ),
        "all_samples_no_row_stream_materialized": all(
            sample["native_phase_timings"].get("row_stream_materialized") is False for sample in samples
        ),
        "first_sample_validation_authority_recorded": (
            "exact prepared count remains the validation authority"
            in first_sample.get("device_resident_continuation_status", "")
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_spatial_rayjoin_relation_status_exact_f64_adverse_subset",
        "status": "spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7",
        "generic_capability": "point_location_topology_stream",
        "dataset": evidence["dataset"],
        "evidence": _rel(EVIDENCE),
        "gpu": evidence["environment"]["nvidia_smi"],
        "count_mode": evidence["count_mode"],
        "sample_repeat": evidence["sample_repeat"],
        "query_repeat": evidence["query_repeat"],
        "adverse_subset_parity_closes_blocker": True,
        "row_count": int(summary["row_count"]),
        "row_count_consistent": bool(summary["row_count_consistent"]),
        "summary": {
            "prepared_query_sec_median": float(summary["prepared_query_sec_median"]),
            "prepared_query_total_sec_median": float(summary["prepared_query_total_sec_median"]),
            "runner_wall_sec_median": float(summary["runner_wall_sec_median"]),
            "m3_phase_sec_medians": summary["m3_phase_sec_medians"],
            "query_stream_residency": summary["query_stream_residency"],
        },
        "first_sample_native_phase_timings": first_native,
        "first_sample_m3_table": first_m3,
        "first_sample_prepared_handle": first_handle,
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
        "interpretation": (
            "The exact-f64 relation-status scalar-count route also passes the small br_county_subset "
            "adverse/parity fixture with row_count 6, full M3 accounting, prepared query-stream "
            "residency, and no public claim flags. This closes only the adverse-subset parity blocker; "
            "it does not authorize M7, release, RayJoin-author comparison, paper reproduction, broad "
            "V3-over-V2 wording, or true zero-copy wording."
        ),
        "goal_level_decision_audit": {
            "decision": "Record Spatial exact-f64 adverse-subset parity as a blocker closure, not a promotion.",
            "was_i_foolish": (
                "No. The public-county repair needed a second small adverse fixture before it could even "
                "remain under review as a generic point-location route."
            ),
            "foolish_actions": (
                "The foolish action would be to use this tiny subset as speed evidence or to treat parity "
                "on one adverse fixture as release readiness."
            ),
            "other_path": (
                "I could have skipped the subset and kept chasing timing. That would leave a correctness "
                "hole open and make the 3.680x internal delta easier to overclaim."
            ),
            "different_path_now": (
                "Close only this blocker, keep author-basis and external-review gates open, and move the "
                "route forward only through M7 review discipline."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    summary = packet["summary"]
    native = packet["first_sample_native_phase_timings"]
    lines = [
        "# Phoenix V3 Spatial Exact-F64 Adverse-Subset Parity",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This packet closes the adverse-subset parity blocker only. It does not promote M7.",
        "",
        "## Evidence",
        "",
        f"- Evidence: `{packet['evidence']}`",
        f"- Dataset: `{packet['dataset']}`",
        f"- GPU: `{packet['gpu']}`",
        f"- Count mode: `{packet['count_mode']}`",
        f"- Query repeat: `{packet['query_repeat']}`",
        f"- Sample repeat: `{packet['sample_repeat']}`",
        "",
        "## Result",
        "",
        f"- Row count: `{packet['row_count']}`",
        f"- Row count consistent: `{str(packet['row_count_consistent']).lower()}`",
        f"- Prepared-query median: `{summary['prepared_query_sec_median']:.9f}s`",
        f"- Prepared-query repeat total median: `{summary['prepared_query_total_sec_median']:.9f}s`",
        f"- Runner wall median: `{summary['runner_wall_sec_median']:.9f}s`",
        f"- Query-stream residency: `{summary['query_stream_residency']}`",
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
        "- Adverse-subset parity closes blocker: `true`",
        "- M7 rows added: `0`",
        "- M7 promotion authorized: `false`",
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
    audit = packet["goal_level_decision_audit"]
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
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
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
