#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_guarded_squared_boundary_20260621"
)
BASELINE_EVIDENCE = EVIDENCE_DIR / "baseline_prefilter_zero_repeat50_sample7.json"
SQUARED_EVIDENCE = EVIDENCE_DIR / "guarded_squared_prefilter_zero_repeat50_sample7.json"
SQUARED_ONLY_EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_guarded_squared_boundary_only_20260621"
)
SQUARED_ONLY_BASELINE_EVIDENCE = SQUARED_ONLY_EVIDENCE_DIR / "default_no_prefilter_repeat50_sample3.json"
SQUARED_ONLY_EVIDENCE = SQUARED_ONLY_EVIDENCE_DIR / "guarded_squared_only_no_prefilter_repeat50_sample3.json"
AUTHOR_BASIS = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
PREFILTER_ZERO_PACKET = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.json"
)
EQUIVALENCE_PACKET = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.json"
)
NATIVE_SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md"
)
CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_spatial_squared_boundary_candidate_2ai_consensus_2026-06-22.md"
)
CLAUDE_DEFAULT_PATH_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md"
)
CODEX_DEFAULT_PATH_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md"
)
DEFAULT_PATH_EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_default_path_20260622"
)
DEFAULT_PATH_EVIDENCE = DEFAULT_PATH_EVIDENCE_DIR / "default_path_guarded_squared_repeat50_sample7.json"
DEFAULT_PATH_SMOKE_EVIDENCE = DEFAULT_PATH_EVIDENCE_DIR / "default_path_smoke_repeat10_sample1.json"
DISABLE_CONTROL_EVIDENCE = DEFAULT_PATH_EVIDENCE_DIR / "disable_control_both_zero_repeat10_sample1.json"
DEFAULT_PATH_BUILD_LOG = DEFAULT_PATH_EVIDENCE_DIR / "build_optix.log"
POD_BUILT_OPTIX_LIBRARY_SHA256 = "36500bba1bdd1bd7b517376b28ca23aeb51af82b97f908786bdb900ec1b40877"
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")

CLAIM_FLAG_KEYS = (
    "release_authorized",
    "public_speedup_claim_authorized",
    "row_scoped_public_speedup_claim_authorized",
    "broad_v3_faster_than_v2_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "true_zero_copy_claim_authorized",
    "v4_embedding_claim_authorized",
    "m7_promotion_authorized",
)


def main() -> int:
    args = parse_args()
    packet = build_packet()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(packet), encoding="utf-8")
    print(json.dumps(packet if args.pretty else packet["summary"], indent=2, sort_keys=True))
    return 0 if not packet["failed_checks"] else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize the Phoenix V3 Spatial exact-f64 squared-boundary candidate."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_packet() -> dict[str, Any]:
    required_paths = {
        "baseline_evidence": BASELINE_EVIDENCE,
        "squared_evidence": SQUARED_EVIDENCE,
        "squared_only_baseline_evidence": SQUARED_ONLY_BASELINE_EVIDENCE,
        "squared_only_evidence": SQUARED_ONLY_EVIDENCE,
        "author_basis": AUTHOR_BASIS,
        "prefilter_zero_packet": PREFILTER_ZERO_PACKET,
        "equivalence_packet": EQUIVALENCE_PACKET,
        "native_source": NATIVE_SOURCE,
        "previous_claude_review": CLAUDE_REVIEW,
        "previous_codex_consensus": CODEX_CONSENSUS,
        "claude_default_path_review": CLAUDE_DEFAULT_PATH_REVIEW,
        "codex_default_path_consensus": CODEX_DEFAULT_PATH_CONSENSUS,
        "default_path_evidence": DEFAULT_PATH_EVIDENCE,
        "default_path_smoke_evidence": DEFAULT_PATH_SMOKE_EVIDENCE,
        "disable_control_evidence": DISABLE_CONTROL_EVIDENCE,
        "default_path_build_log": DEFAULT_PATH_BUILD_LOG,
    }
    path_checks = {f"{name}_exists": path.exists() for name, path in required_paths.items()}
    if not all(path_checks.values()):
        failed_checks = [name for name, ok in path_checks.items() if not ok]
        return _failure_packet(path_checks, failed_checks)

    baseline = _read_json(BASELINE_EVIDENCE)
    squared = _read_json(SQUARED_EVIDENCE)
    squared_only_baseline = _read_json(SQUARED_ONLY_BASELINE_EVIDENCE)
    squared_only = _read_json(SQUARED_ONLY_EVIDENCE)
    author = _read_json(AUTHOR_BASIS)
    prefilter_packet = _read_json(PREFILTER_ZERO_PACKET)
    equivalence = _read_json(EQUIVALENCE_PACKET)
    default_path = _read_json(DEFAULT_PATH_EVIDENCE)
    default_path_smoke = _read_json(DEFAULT_PATH_SMOKE_EVIDENCE)
    disable_control = _read_json(DISABLE_CONTROL_EVIDENCE)
    source_text = NATIVE_SOURCE.read_text(encoding="utf-8")

    baseline_stats = _stats_from_packet(baseline)
    squared_stats = _stats_from_packet(squared)
    squared_only_baseline_stats = _stats_from_packet(squared_only_baseline)
    squared_only_stats = _stats_from_packet(squared_only)
    default_path_stats = _stats_from_packet(default_path)
    default_path_smoke_stats = _stats_from_packet(default_path_smoke)
    disable_control_stats = _stats_from_packet(disable_control)
    baseline_stats["source"] = _rel(BASELINE_EVIDENCE)
    squared_stats["source"] = _rel(SQUARED_EVIDENCE)
    squared_only_baseline_stats["source"] = _rel(SQUARED_ONLY_BASELINE_EVIDENCE)
    squared_only_stats["source"] = _rel(SQUARED_ONLY_EVIDENCE)
    default_path_stats["source"] = _rel(DEFAULT_PATH_EVIDENCE)
    default_path_smoke_stats["source"] = _rel(DEFAULT_PATH_SMOKE_EVIDENCE)
    disable_control_stats["source"] = _rel(DISABLE_CONTROL_EVIDENCE)
    author_query_ms = float(author["author_run"]["query_ms"])
    speedup_vs_baseline = baseline_stats["median_ms"] / squared_stats["median_ms"]
    squared_only_speedup = squared_only_baseline_stats["median_ms"] / squared_only_stats["median_ms"]
    speedup_vs_author_query = author_query_ms / squared_stats["median_ms"]
    default_path_speedup_vs_author_query = author_query_ms / default_path_stats["median_ms"]
    default_path_speedup_vs_disable_control = disable_control_stats["median_ms"] / default_path_stats["median_ms"]
    author_bar_margin_ms = author_query_ms - squared_stats["median_ms"]
    default_path_author_bar_margin_ms = author_query_ms - default_path_stats["median_ms"]
    prefilter_previous_ms = float(prefilter_packet["stable_candidate"]["prepared_query_ms_median"])

    checks = {
        **path_checks,
        "baseline_repeat50_sample7": baseline.get("query_repeat") == 50 and baseline.get("sample_repeat") == 7,
        "squared_repeat50_sample7": squared.get("query_repeat") == 50 and squared.get("sample_repeat") == 7,
        "default_path_repeat50_sample7": (
            default_path.get("query_repeat") == 50 and default_path.get("sample_repeat") == 7
        ),
        "default_path_smoke_repeat10_sample1": (
            default_path_smoke.get("query_repeat") == 10 and default_path_smoke.get("sample_repeat") == 1
        ),
        "disable_control_repeat10_sample1": (
            disable_control.get("query_repeat") == 10 and disable_control.get("sample_repeat") == 1
        ),
        "squared_only_repeat50_sample3": (
            squared_only.get("query_repeat") == 50 and squared_only.get("sample_repeat") == 3
        ),
        "same_dataset": (
            baseline.get("dataset")
            == squared.get("dataset")
            == default_path.get("dataset")
            == disable_control.get("dataset")
            == "data/rayjoin_public_cdb/br_county.cdb"
        ),
        "squared_only_same_dataset": (
            squared_only_baseline.get("dataset")
            == squared_only.get("dataset")
            == "data/rayjoin_public_cdb/br_county.cdb"
        ),
        "same_count_mode": (
            baseline.get("count_mode")
            == squared.get("count_mode")
            == "relation_status_corrected_executor_validated"
        ),
        "same_point_order": baseline.get("point_order_mode") == squared.get("point_order_mode") == "y_then_x",
        "baseline_exact_count_47262": baseline_stats["row_count"] == 47262,
        "squared_exact_count_47262": squared_stats["row_count"] == 47262,
        "default_path_exact_count_47262": default_path_stats["row_count"] == 47262,
        "default_path_smoke_exact_count_47262": default_path_smoke_stats["row_count"] == 47262,
        "disable_control_exact_count_47262": disable_control_stats["row_count"] == 47262,
        "squared_only_exact_count_47262": squared_only_stats["row_count"] == 47262,
        "row_counts_consistent": (
            baseline_stats["row_count_consistent"]
            and squared_stats["row_count_consistent"]
            and squared_only_stats["row_count_consistent"]
            and default_path_stats["row_count_consistent"]
            and default_path_smoke_stats["row_count_consistent"]
            and disable_control_stats["row_count_consistent"]
        ),
        "guarded_equivalence_packet_passes": (
            equivalence.get("status") == "spatial_guarded_squared_boundary_equivalence_pass_not_release"
        ),
        "guarded_equivalence_has_zero_mismatch": int(equivalence.get("guarded_mismatch_count", -1)) == 0,
        "pure_squared_mismatch_risk_recorded": int(equivalence.get("pure_squared_mismatch_count", 0)) > 0,
        "raw_candidate_counts_match": baseline_stats["raw_counts"] == squared_stats["raw_counts"] == [47570],
        "emitted_counts_match": baseline_stats["emitted_counts"] == squared_stats["emitted_counts"] == [47262],
        "boundary_counts_match": baseline_stats["boundary_counts"] == squared_stats["boundary_counts"] == [47550],
        "dropped_counts_match": baseline_stats["dropped_counts"] == squared_stats["dropped_counts"] == [308],
        "default_path_counts_match_squared_candidate": (
            default_path_stats["raw_counts"] == squared_stats["raw_counts"] == [47570]
            and default_path_stats["emitted_counts"] == squared_stats["emitted_counts"] == [47262]
            and default_path_stats["boundary_counts"] == squared_stats["boundary_counts"] == [47550]
            and default_path_stats["dropped_counts"] == squared_stats["dropped_counts"] == [308]
        ),
        "disable_control_returns_old_candidate_volume": (
            disable_control_stats["raw_counts"] == [155555]
            and disable_control_stats["dropped_counts"] == [108293]
            and disable_control_stats["emitted_counts"] == [47262]
        ),
        "squared_materially_faster_than_current_prefilter": speedup_vs_baseline >= 1.25,
        "default_path_materially_faster_than_disable_control": default_path_speedup_vs_disable_control >= 3.0,
        "squared_only_materially_faster_than_default_no_prefilter": squared_only_speedup >= 1.25,
        "squared_only_does_not_clear_author_bar": squared_only_stats["median_ms"] > author_query_ms,
        "squared_median_clears_author_query_bar": squared_stats["median_ms"] < author_query_ms,
        "default_path_median_clears_author_query_bar": default_path_stats["median_ms"] < author_query_ms,
        "squared_worst_sample_clears_author_query_bar": squared_stats["max_ms"] < author_query_ms,
        "default_path_worst_sample_clears_author_query_bar": default_path_stats["max_ms"] < author_query_ms,
        "squared_clears_author_bar_by_stable_margin": speedup_vs_author_query >= 1.20,
        "default_path_clears_author_bar_by_stable_margin": default_path_speedup_vs_author_query >= 1.20,
        "previous_prefilter_near_miss_confirmed": prefilter_previous_ms > author_query_ms,
        "all_packet_claim_flags_false": (
            _claim_flags_false(baseline)
            and _claim_flags_false(squared)
            and _claim_flags_false(default_path)
            and _claim_flags_false(default_path_smoke)
            and _claim_flags_false(disable_control)
        ),
        "author_basis_claim_flags_false": all(author.get(key) is False for key in CLAIM_FLAG_KEYS if key in author),
        "native_source_has_squared_boundary_flag": (
            "RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY" in source_text
        ),
        "native_source_has_default_on_relation_status_helper": (
            "relation_status_corrected_default_enabled" in source_text
        ),
        "native_source_default_enables_prefilter_zero": (
            'relation_status_corrected_default_enabled("RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO")'
            in source_text
        ),
        "native_source_default_enables_squared_boundary": (
            'relation_status_corrected_default_enabled("RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY")'
            in source_text
        ),
        "native_source_does_not_keep_default_off_squared_boundary_gate": (
            'std::getenv("RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY") != nullptr'
            not in source_text
        ),
        "native_source_has_guarded_fallback": (
            "const double guard_tol = 1.0e-6;" in source_text
            and "bool needs_fallback" in source_text
            and "const double len = sqrt(len2);" in source_text
        ),
        "native_source_does_not_define_dead_exact_boundary_contact": (
            "exact_boundary_contact_f64" not in source_text
        ),
        "native_source_does_not_retain_count_only_no_diagnostics": (
            "RTDL_OPTIX_RELATION_STATUS_CORRECTED_COUNT_ONLY_NO_DIAGNOSTICS" not in source_text
        ),
        "author_result_count_not_used_as_parity": author["author_result_count_printed"] is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]

    return {
        "tool": "v3_phoenix_spatial_relation_status_squared_boundary_candidate",
        "status": (
            "fail"
            if failed_checks
            else "spatial_relation_status_squared_boundary_default_path_m7_row_accepted_with_boundary"
        ),
        "generic_capability": "point_location_topology_stream",
        "candidate_row_id": (
            "point_location_topology_stream_relation_status_guarded_squared_boundary_"
            "prefilter_zero_county_repeat50_sample7"
        ),
        "candidate_route": "relation_status_corrected_executor_validated",
        "optimization": {
            "name": "exact_f64_guarded_squared_boundary_after_relation_status_zero_prefilter",
            "native_flags": [
                "RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO",
                "RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY",
            ],
            "default_enabled": True,
            "default_disable_values": ["0", "false", "False", "FALSE", "off", "Off", "OFF", "no", "No", "NO"],
            "implementation_summary": (
                "The candidate keeps the generic relation-status corrected scalar-count "
                "executor and replaces most full f64 membership boundary segment tests "
                "with squared fast-path comparisons while falling back to the old "
                "sqrt/along-epsilon predicate inside a small threshold guard band. "
                "The current source enables the prefilter and guarded squared-boundary "
                "path by default unless the corresponding env flag is explicitly set "
                "to a false-like value."
            ),
            "correctness_summary": (
                "The equivalence packet records that pure squared comparison is not "
                "safe on endpoint-adjacent floating cases, while the guarded version "
                "matches the old predicate on the deterministic and seeded finite-double "
                "case set."
            ),
            "why_generic": (
                "The changed predicate is inside the reusable closed-shape point-location "
                "topology stream. It does not special-case RayJoin, counties, CDB files, "
                "or the public benchmark dataset."
            ),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_claim_authorized": False,
        "m7_promotion_authorized": not failed_checks,
        "m7_candidate": not failed_checks,
        "m7_qualified_release_rows_added": 1 if not failed_checks else 0,
        "external_review_status": "claude_accept_with_boundary_default_path",
        "previous_external_review_status": "claude_accept_with_boundary",
        "codex_consensus_status": "claude_codex_consensus_accept_default_path_m7_row",
        "previous_codex_consensus_status": "claude_codex_consensus_accept_with_boundary_not_release",
        "p1_default_path_resolution_required": False,
        "dataset": "data/rayjoin_public_cdb/br_county.cdb",
        "pod": {
            "host": "213.173.108.14:11592",
            "gpu": "NVIDIA RTX 4000 Ada Generation, 550.127.05",
            "driver": "550.127.05",
            "remote_repo": "/root/rtdl_v3_rebuild_20260620/current",
        },
        "source": {
            "native_file": _rel(NATIVE_SOURCE),
            "native_file_sha256": _sha256(NATIVE_SOURCE),
            "baseline_evidence": _rel(BASELINE_EVIDENCE),
            "squared_evidence": _rel(SQUARED_EVIDENCE),
            "default_path_evidence": _rel(DEFAULT_PATH_EVIDENCE),
            "default_path_smoke_evidence": _rel(DEFAULT_PATH_SMOKE_EVIDENCE),
            "disable_control_evidence": _rel(DISABLE_CONTROL_EVIDENCE),
            "default_path_build_log": _rel(DEFAULT_PATH_BUILD_LOG),
            "pod_built_optix_library_sha256": POD_BUILT_OPTIX_LIBRARY_SHA256,
            "equivalence_packet": _rel(EQUIVALENCE_PACKET),
            "squared_only_baseline_evidence": _rel(SQUARED_ONLY_BASELINE_EVIDENCE),
            "squared_only_evidence": _rel(SQUARED_ONLY_EVIDENCE),
            "author_basis": _rel(AUTHOR_BASIS),
            "previous_external_review": _rel(CLAUDE_REVIEW),
            "previous_codex_consensus": _rel(CODEX_CONSENSUS),
            "external_review": _rel(CLAUDE_DEFAULT_PATH_REVIEW),
            "codex_consensus": _rel(CODEX_DEFAULT_PATH_CONSENSUS),
            "previous_near_miss_packet": _rel(PREFILTER_ZERO_PACKET),
            "provenance_limitations": [
                "The remote POD source copy is not a git checkout, so evidence records rely on local source SHA and copied JSON artifacts rather than a remote git commit.",
                "RayJoin author query_exec does not print result count in this run; this packet uses RTDL exact count parity and treats the author Query timer only as a performance bar.",
            ],
        },
        "author_bar": {
            "author_query_ms": author_query_ms,
            "author_result_count_printed": bool(author["author_result_count_printed"]),
            "author_result_count_parity_verified": bool(author["author_result_count_parity_verified"]),
            "author_timer_basis": author["author_run"]["command_contract"],
            "query_exec_sha256": author["author_run"]["query_exec_sha256"],
            "data_sha256": author["author_run"]["data_sha256"],
        },
        "baseline_prefilter_zero": baseline_stats,
        "squared_boundary_candidate": squared_stats,
        "guarded_squared_boundary_candidate": squared_stats,
        "default_path_candidate": {
            **default_path_stats,
            "activation": "default_path_no_enabling_env_flags",
            "command_contract": (
                "env -u RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO "
                "-u RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY "
                "PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so "
                "RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so python3 "
                "scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py "
                "--dataset data/rayjoin_public_cdb/br_county.cdb "
                "--count-mode relation_status_corrected_executor_validated "
                "--point-order-mode y_then_x --query-repeat 50 --warmup 5 --sample-repeat 7"
            ),
        },
        "default_path_smoke": {
            **default_path_smoke_stats,
            "activation": "default_path_no_enabling_env_flags",
        },
        "disable_control": {
            **disable_control_stats,
            "activation": "both_default_enabled_controls_set_to_zero",
            "command_contract": (
                "RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO=0 "
                "RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY=0 "
                "PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so "
                "RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so python3 "
                "scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py "
                "--dataset data/rayjoin_public_cdb/br_county.cdb "
                "--count-mode relation_status_corrected_executor_validated "
                "--point-order-mode y_then_x --query-repeat 10 --warmup 2 --sample-repeat 1"
            ),
        },
        "predicate_equivalence": {
            "packet": _rel(EQUIVALENCE_PACKET),
            "status": equivalence["status"],
            "guarded_mismatch_count": int(equivalence["guarded_mismatch_count"]),
            "pure_squared_mismatch_count": int(equivalence["pure_squared_mismatch_count"]),
            "guard_tol": float(equivalence["equivalence_scope"]["guard_tol"]),
        },
        "squared_boundary_only": {
            "baseline_default_no_prefilter": squared_only_baseline_stats,
            "squared_only_no_prefilter": squared_only_stats,
            "speedup_vs_default_no_prefilter": squared_only_speedup,
            "clears_author_query_bar": squared_only_stats["median_ms"] < author_query_ms,
            "interpretation": (
                "The guarded squared-boundary predicate is a material generic optimization by itself, "
                "but the public-county author Query bar is cleared only when paired with "
                "relation-status zero prefiltering."
            ),
        },
        "summary": {
            "m7_rows_added_now": 1 if not failed_checks else 0,
            "candidate_pending_external_review": False,
            "external_review_accepted_with_boundary": not failed_checks,
            "p1_default_path_resolution_required": False,
            "default_path_evidence_collected": True,
            "baseline_prefilter_zero_median_ms": baseline_stats["median_ms"],
            "squared_boundary_median_ms": squared_stats["median_ms"],
            "default_path_median_ms": default_path_stats["median_ms"],
            "default_path_best_ms": default_path_stats["best_ms"],
            "default_path_worst_ms": default_path_stats["max_ms"],
            "squared_boundary_best_ms": squared_stats["best_ms"],
            "squared_boundary_worst_ms": squared_stats["max_ms"],
            "speedup_vs_current_prefilter_zero": speedup_vs_baseline,
            "default_path_speedup_vs_author_query_timer": default_path_speedup_vs_author_query,
            "default_path_author_bar_margin_ms": default_path_author_bar_margin_ms,
            "default_path_speedup_vs_disable_control": default_path_speedup_vs_disable_control,
            "disable_control_median_ms": disable_control_stats["median_ms"],
            "squared_only_no_prefilter_median_ms": squared_only_stats["median_ms"],
            "squared_only_speedup_vs_default_no_prefilter": squared_only_speedup,
            "squared_only_clears_author_query_bar": squared_only_stats["median_ms"] < author_query_ms,
            "author_query_ms": author_query_ms,
            "speedup_vs_author_query_timer": speedup_vs_author_query,
            "author_bar_margin_ms": author_bar_margin_ms,
            "previous_prefilter_near_miss_ms": prefilter_previous_ms,
            "row_count": default_path_stats["row_count"],
            "row_count_consistent": default_path_stats["row_count_consistent"],
            "status": "default_path_m7_row_accepted_with_boundary_not_release",
        },
        "claim_boundary_note": (
            "This packet can support external review of a row-scoped M7 candidate. "
            "It does not by itself authorize public release, broad V3-vs-V2 claims, "
            "RTDL-beats-RayJoin wording, paper reproduction wording, true zero-copy, "
            "or V4 embedding claims."
        ),
        "required_next_actions": [
            "Update the release-surface breadth gate so point_location_topology_stream contributes one bounded M7 row.",
            "Carry the git_commit:null provenance gap forward to public-release readiness gates.",
            "Keep all public release, V3-vs-V2, RTDL-beats-RayJoin, paper reproduction, zero-copy, and V4/embedding claims unauthorized.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Accept the guarded squared-boundary evidence with Claude/Codex boundary, "
                "record the new default-path POD evidence, and promote it to one bounded "
                "M7 release-surface row after external review and consensus."
            ),
            "was_i_foolish": (
                "No. The candidate is a generic predicate optimization with an explicit "
                "fallback for pure-squared edge cases, row count is stable at 47,262, "
                "the measured gain is material rather than a tiny 1.01x result, and I "
                "kept release promotion blocked after external review."
            ),
            "foolish_actions": (
                "The foolish action would be to call this a public RayJoin win, a "
                "whole-app win, or a released V3 capability because the default-path POD "
                "evidence clears the author Query timer. This packet only counts an "
                "internal M7 row and keeps public/broad claims disabled."
            ),
            "other_path": (
                "I could have left Spatial as a future-research gap after the "
                "prefilter-zero near miss. That would avoid risk, but it would miss "
                "a real generic hot-path optimization visible in the exact f64 helper."
            ),
            "different_path_now": (
                "Update the release-surface gates with one bounded row, then keep working "
                "on Phoenix V3 breadth without weakening claim boundaries."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    summary = packet["summary"]
    candidate = packet["squared_boundary_candidate"]
    default_path = packet["default_path_candidate"]
    disable_control = packet["disable_control"]
    baseline = packet["baseline_prefilter_zero"]
    squared_only = packet["squared_boundary_only"]
    equivalence = packet["predicate_equivalence"]
    audit = packet["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial Guarded Squared-Boundary Candidate",
        "",
        f"Status: `{packet['status']}`.",
        "",
        "This packet adds default-path POD evidence for the missing",
        "`point_location_topology_stream` V3 capability family. The optimized",
        "route is now default-enabled in source and has been measured with no",
        "enabling env flags. Claude and Codex accept it as one bounded M7",
        "release-surface row, while public speedup claims remain disabled.",
        "",
        f"- External review: `{packet['source']['external_review']}`",
        f"- Codex consensus: `{packet['source']['codex_consensus']}`",
        f"- Previous external review: `{packet['source']['previous_external_review']}`",
        f"- Previous Codex consensus: `{packet['source']['previous_codex_consensus']}`",
        f"- Current external review status: `{packet['external_review_status']}`",
        f"- Current Codex consensus status: `{packet['codex_consensus_status']}`",
        f"- P1 default-path resolution required: `{str(packet['p1_default_path_resolution_required']).lower()}`",
        "",
        "```text",
        f"release_authorized: {str(packet['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(packet['public_speedup_claim_authorized']).lower()}",
        f"row_scoped_public_speedup_claim_authorized: {str(packet['row_scoped_public_speedup_claim_authorized']).lower()}",
        f"rtdl_beats_rayjoin_claim_authorized: {str(packet['rtdl_beats_rayjoin_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(packet['m7_promotion_authorized']).lower()}",
        f"M7 rows added now: {packet['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Result",
        "",
        f"- Dataset: `{packet['dataset']}`",
        f"- Candidate row id: `{packet['candidate_row_id']}`",
        f"- Baseline prefilter-zero median: `{summary['baseline_prefilter_zero_median_ms']:.6f} ms`",
        f"- Guarded squared-boundary median: `{summary['squared_boundary_median_ms']:.6f} ms`",
        f"- Default-path guarded squared-boundary median: `{summary['default_path_median_ms']:.6f} ms`",
        f"- Default-path sample range: `{summary['default_path_best_ms']:.6f}` to `{summary['default_path_worst_ms']:.6f} ms`",
        f"- Candidate sample range: `{summary['squared_boundary_best_ms']:.6f}` to `{summary['squared_boundary_worst_ms']:.6f} ms`",
        f"- Speedup vs current prefilter-zero route: `{summary['speedup_vs_current_prefilter_zero']:.3f}x`",
        f"- Default path vs disable control: `{summary['default_path_speedup_vs_disable_control']:.3f}x`",
        f"- Guarded-squared-only no-prefilter median: `{summary['squared_only_no_prefilter_median_ms']:.6f} ms`",
        f"- Guarded-squared-only speedup vs default no-prefilter: `{summary['squared_only_speedup_vs_default_no_prefilter']:.3f}x`",
        f"- RayJoin author Query timer: `{summary['author_query_ms']:.6f} ms`",
        f"- Default path vs author Query timer: `{summary['default_path_speedup_vs_author_query_timer']:.3f}x`",
        f"- Default path margin under author Query: `{summary['default_path_author_bar_margin_ms']:.6f} ms`",
        f"- Candidate vs author Query timer: `{summary['speedup_vs_author_query_timer']:.3f}x`",
        f"- Candidate margin under author Query: `{summary['author_bar_margin_ms']:.6f} ms`",
        f"- Exact row count: `{summary['row_count']}`",
        f"- Row count consistent: `{str(summary['row_count_consistent']).lower()}`",
        "",
        "## Count Invariants",
        "",
        "| route | raw candidates | boundary candidates | emitted | dropped |",
        "| --- | ---: | ---: | ---: | ---: |",
        (
            f"| baseline | `{baseline['raw_counts']}` | `{baseline['boundary_counts']}` | "
            f"`{baseline['emitted_counts']}` | `{baseline['dropped_counts']}` |"
        ),
        (
            f"| guarded squared | `{candidate['raw_counts']}` | `{candidate['boundary_counts']}` | "
            f"`{candidate['emitted_counts']}` | `{candidate['dropped_counts']}` |"
        ),
        (
            f"| default path | `{default_path['raw_counts']}` | `{default_path['boundary_counts']}` | "
            f"`{default_path['emitted_counts']}` | `{default_path['dropped_counts']}` |"
        ),
        (
            f"| disable control | `{disable_control['raw_counts']}` | `{disable_control['boundary_counts']}` | "
            f"`{disable_control['emitted_counts']}` | `{disable_control['dropped_counts']}` |"
        ),
        "",
        "## Default Path Evidence",
        "",
        f"- Default-path packet: `{default_path['source']}`",
        f"- Activation: `{default_path['activation']}`",
        f"- Disable-control packet: `{disable_control['source']}`",
        f"- Disable-control median: `{disable_control['median_ms']:.6f} ms`",
        f"- Built OptiX library SHA256: `{packet['source']['pod_built_optix_library_sha256']}`",
        "",
        "## Predicate Equivalence",
        "",
        f"- Equivalence packet: `{equivalence['packet']}`",
        f"- Guarded mismatch count: `{equivalence['guarded_mismatch_count']}`",
        f"- Pure squared mismatch count recorded: `{equivalence['pure_squared_mismatch_count']}`",
        f"- Guard tolerance: `{equivalence['guard_tol']}`",
        "",
        "Pure squared comparison is not claimed equivalent. The candidate uses a",
        "guarded squared fast path and falls back to the old sqrt predicate near",
        "thresholds.",
        "",
        "## Guarded-Squared-Only Default-Surface Probe",
        "",
        f"- Default no-prefilter median: `{squared_only['baseline_default_no_prefilter']['median_ms']:.6f} ms`",
        f"- Guarded-squared-only no-prefilter median: `{squared_only['squared_only_no_prefilter']['median_ms']:.6f} ms`",
        f"- Speedup: `{squared_only['speedup_vs_default_no_prefilter']:.3f}x`",
        f"- Clears author Query bar: `{str(squared_only['clears_author_query_bar']).lower()}`",
        "",
        squared_only["interpretation"],
        "",
        "## Boundary",
        "",
        packet["claim_boundary_note"],
        "",
        "The author Query timer is used as a performance bar only. The author run",
        "does not print result count, so this packet cannot support broad",
        "`RTDL beats RayJoin` wording without review and wording constraints.",
        "",
        "## Required Next Actions",
        "",
    ]
    lines.extend(f"- {item}" for item in packet["required_next_actions"])
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
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


def _failure_packet(checks: dict[str, bool], failed_checks: list[str]) -> dict[str, Any]:
    return {
        "tool": "v3_phoenix_spatial_relation_status_squared_boundary_candidate",
        "status": "fail",
        "generic_capability": "point_location_topology_stream",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_candidate": False,
        "m7_qualified_release_rows_added": 0,
        "summary": {"status": "missing_required_evidence"},
        "checks": checks,
        "failed_checks": failed_checks,
    }


def _stats_from_packet(packet: dict[str, Any]) -> dict[str, Any]:
    values_ms = [float(sample["phases_sec"]["prepared_query_sec"]) * 1000.0 for sample in packet["samples"]]
    return {
        "source": "",
        "query_repeat": int(packet["query_repeat"]),
        "warmup": int(packet["warmup"]),
        "sample_repeat": int(packet["sample_repeat"]),
        "median_ms": statistics.median(values_ms),
        "best_ms": min(values_ms),
        "max_ms": max(values_ms),
        "values_ms": values_ms,
        "row_count": int(packet["summary"]["row_count"]),
        "row_count_consistent": bool(packet["summary"]["row_count_consistent"]),
        "raw_counts": sorted(
            set(int(sample["native_phase_timings"]["raw_candidate_count"]) for sample in packet["samples"])
        ),
        "emitted_counts": sorted(
            set(int(sample["native_phase_timings"]["emitted_count"]) for sample in packet["samples"])
        ),
        "boundary_counts": sorted(
            set(int(sample["native_phase_timings"]["boundary_candidate_count"]) for sample in packet["samples"])
        ),
        "dropped_counts": sorted(
            set(int(sample["native_phase_timings"]["dropped_candidate_count"]) for sample in packet["samples"])
        ),
        "query_stream_residency": packet["summary"]["query_stream_residency"],
        "m3_phase_sec_medians": packet["summary"]["m3_phase_sec_medians"],
    }


def _claim_flags_false(payload: dict[str, Any]) -> bool:
    return all(payload.get(key) is False for key in CLAIM_FLAG_KEYS)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
