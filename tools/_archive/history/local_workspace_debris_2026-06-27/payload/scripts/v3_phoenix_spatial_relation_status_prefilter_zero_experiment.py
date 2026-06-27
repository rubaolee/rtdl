#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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
    / "phoenix_v3_spatial_relation_status_prefilter_zero_experiment_20260621"
)
HOTPATH_NO_GO = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json"
AUTHOR_BASIS = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
NATIVE_SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.json"
OUT_MD = OUT_JSON.with_suffix(".md")


ORDER_PACKET_NAMES = {
    "natural": "prefilter_zero_relation_status_natural_repeat50_sample3.json",
    "x_then_y": "prefilter_zero_relation_status_x_then_y_repeat50_sample3.json",
    "morton_xy": "prefilter_zero_relation_status_morton_xy_repeat50_sample3.json",
    "y_then_x_sample5": "prefilter_zero_relation_status_y_then_x_repeat50_sample5.json",
    "y_then_x_sample7": "prefilter_zero_relation_status_y_then_x_repeat50_sample7.json",
    "restored_y_then_x_sample3": "prefilter_zero_restored_y_then_x_repeat50_sample3.json",
}


def main() -> int:
    args = parse_args()
    packet = build_packet()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(packet), encoding="utf-8")
    if args.pretty:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps(packet["summary"], indent=2, sort_keys=True))
    return 0 if not packet["failed_checks"] else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize the Phoenix V3 Spatial relation-status prefilter-zero experiment."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_packet() -> dict[str, Any]:
    hotpath = _read_json(HOTPATH_NO_GO)
    author = _read_json(AUTHOR_BASIS)
    packets = {name: _read_json(EVIDENCE_DIR / filename) for name, filename in ORDER_PACKET_NAMES.items()}
    rows = [_row_from_packet(name, payload) for name, payload in packets.items()]
    stable = packets["y_then_x_sample7"]
    restored = packets["restored_y_then_x_sample3"]
    stable_summary = stable["summary"]
    restored_summary = restored["summary"]
    old_best = hotpath["best_legal_route"]
    author_query_ms = float(author["author_run"]["query_ms"])
    stable_ms = _ms(stable_summary["prepared_query_sec_median"])
    restored_ms = _ms(restored_summary["prepared_query_sec_median"])
    old_best_ms = float(old_best["prepared_query_ms"])
    stable_speedup_vs_old = old_best_ms / stable_ms
    restored_speedup_vs_old = old_best_ms / restored_ms
    stable_rtdl_relative_to_author = author_query_ms / stable_ms
    stable_author_speedup_vs_rtdl = stable_ms / author_query_ms
    source_text = NATIVE_SOURCE.read_text(encoding="utf-8")
    checks = {
        "evidence_dir_exists": EVIDENCE_DIR.exists(),
        "all_order_packets_exist": all((EVIDENCE_DIR / filename).exists() for filename in ORDER_PACKET_NAMES.values()),
        "native_source_has_prefilter_zero_flag": "RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO" in source_text,
        "native_source_default_enables_prefilter_zero": (
            'relation_status_corrected_default_enabled("RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO")'
            in source_text
        ),
        "native_source_does_not_keep_default_off_prefilter_gate": (
            'std::getenv("RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO") != nullptr'
            not in source_text
        ),
        "stable_sample7_count_is_exact_47262": int(stable_summary["row_count"]) == 47262,
        "stable_sample7_count_consistent": stable_summary["row_count_consistent"] is True,
        "restored_smoke_count_is_exact_47262": int(restored_summary["row_count"]) == 47262,
        "restored_smoke_count_consistent": restored_summary["row_count_consistent"] is True,
        "all_public_claim_flags_false": all(_claim_flags_false(payload) for payload in packets.values()),
        "stable_sample7_material_speedup_vs_old_best": stable_speedup_vs_old >= 2.5,
        "restored_smoke_material_speedup_vs_old_best": restored_speedup_vs_old >= 2.5,
        "stable_sample7_still_slower_than_author_query": stable_ms > author_query_ms,
        "restored_smoke_still_slower_than_author_query": restored_ms > author_query_ms,
        "old_hotpath_was_not_m7": hotpath["m7_promotion_authorized"] is False,
        "author_basis_not_m7": author["m7_promotion_authorized"] is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "tool": "v3_phoenix_spatial_relation_status_prefilter_zero_experiment",
        "status": (
            "fail" if failed_checks else "spatial_relation_status_prefilter_zero_near_miss_not_m7"
        ),
        "generic_capability": "point_location_topology_stream",
        "optimization": {
            "name": "relation_status_zero_prefilter",
            "native_flag": "RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO",
            "default_enabled": True,
            "implementation_summary": (
                "The current source enables relation-status zero prefiltering by default: "
                "the corrected scalar-count pipeline drops relation_status == 0 candidates in the OptiX "
                "intersection stage before full f64 exact membership refinement unless "
                "the env flag is explicitly set to a false-like value."
            ),
            "why_generic": (
                "The change narrows the reusable point-location topology stream before "
                "the exact scalar-count continuation. It is not RayJoin-app custom logic."
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
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "dataset": "data/rayjoin_public_cdb/br_county.cdb",
        "pod": {
            "host": "213.173.108.14:11592",
            "gpu": "NVIDIA RTX 4000 Ada Generation, 550.127.05",
            "remote_repo": "/root/rtdl_v3_rebuild_20260620/current",
        },
        "source": {
            "native_file": _rel(NATIVE_SOURCE),
            "native_file_sha256": _sha256(NATIVE_SOURCE),
            "evidence_dir": _rel(EVIDENCE_DIR),
            "old_hotpath_no_go": _rel(HOTPATH_NO_GO),
            "author_basis": _rel(AUTHOR_BASIS),
        },
        "author_bar": {
            "author_query_ms": author_query_ms,
            "author_result_count_printed": bool(author["author_result_count_printed"]),
            "author_result_count_parity_verified": bool(author["author_result_count_parity_verified"]),
            "author_timer_basis": author["author_run"]["command_contract"],
        },
        "baseline_without_prefilter": {
            "source": old_best["source"],
            "count_mode": old_best["count_mode"],
            "point_order_mode": old_best["point_order_mode"],
            "prepared_query_ms": old_best_ms,
            "row_count": int(old_best["row_count"]),
            "rtdl_beats_rayjoin_claim_authorized": False,
        },
        "prefilter_zero_results": rows,
        "stable_candidate": {
            "source": _rel(EVIDENCE_DIR / ORDER_PACKET_NAMES["y_then_x_sample7"]),
            "point_order_mode": "y_then_x",
            "sample_repeat": int(stable["sample_repeat"]),
            "query_repeat": int(stable["query_repeat"]),
            "warmup": int(stable["warmup"]),
            "prepared_query_ms_median": stable_ms,
            "rt_traversal_ms_median": _ms(
                stable_summary["m3_phase_sec_medians"]["rt_traversal_sec"]
            ),
            "row_count": int(stable_summary["row_count"]),
            "row_count_consistent": bool(stable_summary["row_count_consistent"]),
            "speedup_vs_old_best_legal_route": stable_speedup_vs_old,
            "rtdl_relative_to_author_query": stable_rtdl_relative_to_author,
            "author_speedup_vs_rtdl": stable_author_speedup_vs_rtdl,
        },
        "restored_library_smoke": {
            "source": _rel(EVIDENCE_DIR / ORDER_PACKET_NAMES["restored_y_then_x_sample3"]),
            "prepared_query_ms_median": restored_ms,
            "speedup_vs_old_best_legal_route": restored_speedup_vs_old,
            "row_count": int(restored_summary["row_count"]),
            "row_count_consistent": bool(restored_summary["row_count_consistent"]),
        },
        "failed_followup_experiment": {
            "name": "boundary_helper_exact_contact_fast_path",
            "status": "rejected_exact_count_mismatch_not_kept",
            "observed_error": (
                "validated relation-status corrected closed-shape count did not "
                "match exact prepared count: 47259 != 47262"
            ),
            "decision": (
                "The boundary-helper fast path was reverted. The surviving source "
                "keeps full f64 exact membership after zero-status prefiltering."
            ),
        },
        "summary": {
            "m7_rows_added": 0,
            "old_best_prepared_query_ms": old_best_ms,
            "stable_prefilter_prepared_query_ms": stable_ms,
            "stable_prefilter_speedup_vs_old_best": stable_speedup_vs_old,
            "author_query_ms": author_query_ms,
            "author_speedup_vs_stable_prefilter": stable_author_speedup_vs_rtdl,
            "still_missing_author_bar_by_ms": stable_ms - author_query_ms,
            "row_count": int(stable_summary["row_count"]),
            "row_count_consistent": bool(stable_summary["row_count_consistent"]),
            "status": "correct_material_optimization_but_not_m7",
        },
        "required_next_actions": [
            "Do not promote Spatial topology-stream to M7 from this packet.",
            "If this path is continued, find a correctness-preserving optimization that clears the 1.865660 ms author Query bar with stable margin.",
            "Keep the failed boundary-helper fast path rejected unless a new proof explains the three-count loss.",
            "Only after a new promotable packet exists, request external AI review and Codex consensus.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record relation-status zero prefiltering as real generic Spatial "
                "topology-stream optimization evidence, but keep it not-M7."
            ),
            "was_i_foolish": (
                "No for the goal-level decision. The foolish move would be to call "
                "a 1.903 ms correct near-miss a release row when the same-dataset "
                "author Query bar is 1.865660 ms."
            ),
            "foolish_actions": (
                "I made one tooling mistake by using a Bash heredoc in PowerShell "
                "for a local JSON summary; it made no file changes and I reran it "
                "with a PowerShell here-string. The boundary-helper optimization "
                "was also a deliberately bounded experiment; it became invalid "
                "because it changed the exact count to 47,259."
            ),
            "other_path": (
                "I could have left Spatial closed as future research. That would "
                "avoid risk, but it would not test the obvious generic native "
                "bottleneck exposed by the M3 phase table."
            ),
            "different_path_now": (
                "Keep the correct prefilter-zero result as no-go optimization "
                "evidence, preserve the author bar, and continue only if a next "
                "generic optimization can clear that bar without count loss."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    summary = packet["summary"]
    stable = packet["stable_candidate"]
    failed = packet["failed_followup_experiment"]
    audit = packet["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial Relation-Status Prefilter-Zero Experiment",
        "",
        f"Status: `{packet['status']}`.",
        "",
        "This packet records a real generic native optimization attempt for",
        "`point_location_topology_stream`. It does not add an M7 row and does not",
        "authorize release or public speedup wording.",
        "",
        "```text",
        f"release_authorized: {str(packet['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(packet['public_speedup_claim_authorized']).lower()}",
        f"rtdl_beats_rayjoin_claim_authorized: {str(packet['rtdl_beats_rayjoin_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(packet['m7_promotion_authorized']).lower()}",
        f"M7 rows added: {packet['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Result",
        "",
        f"- Dataset: `{packet['dataset']}`",
        f"- Old best legal RTDL prepared query: `{summary['old_best_prepared_query_ms']:.6f} ms`",
        f"- Prefilter-zero stable prepared query: `{summary['stable_prefilter_prepared_query_ms']:.6f} ms`",
        f"- Improvement vs old legal route: `{summary['stable_prefilter_speedup_vs_old_best']:.3f}x`",
        f"- RayJoin author Query bar: `{summary['author_query_ms']:.6f} ms`",
        f"- Author remains faster by: `{summary['author_speedup_vs_stable_prefilter']:.3f}x`",
        f"- Remaining gap: `{summary['still_missing_author_bar_by_ms']:.6f} ms`",
        f"- Exact row count: `{summary['row_count']}`",
        f"- Row count consistent: `{str(summary['row_count_consistent']).lower()}`",
        "",
        "The optimization is material and correct on the public county packet, but",
        "it remains a near-miss against the same-dataset author timer. Therefore it",
        "is not a Phoenix V3 release row.",
        "",
        "## Stable Candidate",
        "",
        f"- Source: `{stable['source']}`",
        f"- Point order: `{stable['point_order_mode']}`",
        f"- repeat/warmup/sample: `{stable['query_repeat']}` / `{stable['warmup']}` / `{stable['sample_repeat']}`",
        f"- RT traversal median: `{stable['rt_traversal_ms_median']:.6f} ms`",
        f"- Speedup vs old route: `{stable['speedup_vs_old_best_legal_route']:.3f}x`",
        f"- RTDL relative to author Query: `{stable['rtdl_relative_to_author_query']:.3f}x`",
        "",
        "## Ordering Sweep",
        "",
        "| order | prepared query ms | row count | stable |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in packet["prefilter_zero_results"]:
        lines.append(
            f"| `{row['name']}` | `{row['prepared_query_ms_median']:.6f}` | `{row['row_count']}` | `{str(row['row_count_consistent']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Rejected Follow-Up",
            "",
            f"- `{failed['name']}`: `{failed['status']}`",
            f"- Observed error: `{failed['observed_error']}`",
            f"- Decision: {failed['decision']}",
            "",
            "## Required Next Actions",
            "",
        ]
    )
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


def _row_from_packet(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload["summary"]
    return {
        "name": name,
        "source": _rel(EVIDENCE_DIR / ORDER_PACKET_NAMES[name]),
        "prepared_query_ms_median": _ms(summary["prepared_query_sec_median"]),
        "rt_traversal_ms_median": _ms(summary["m3_phase_sec_medians"]["rt_traversal_sec"]),
        "row_count": int(summary["row_count"]),
        "row_count_consistent": bool(summary["row_count_consistent"]),
        "m7_promotion_authorized": bool(payload["m7_promotion_authorized"]),
        "public_speedup_claim_authorized": bool(payload["public_speedup_claim_authorized"]),
    }


def _claim_flags_false(payload: dict[str, Any]) -> bool:
    keys = (
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
    return all(payload.get(key) is False for key in keys)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ms(seconds: float) -> float:
    return float(seconds) * 1000.0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
