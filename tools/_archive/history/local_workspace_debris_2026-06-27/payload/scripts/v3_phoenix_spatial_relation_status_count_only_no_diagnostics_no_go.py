#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    / "phoenix_v3_spatial_relation_status_count_only_no_diag_20260621"
)
DIAGNOSTIC_PACKET = EVIDENCE_DIR / "diagnostic_prefilter_zero_repeat50_sample7.json"
COUNT_ONLY_PACKET = EVIDENCE_DIR / "count_only_prefilter_zero_repeat50_sample7.json"
NATIVE_SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")

COUNT_ONLY_FLAG = "RTDL_OPTIX_RELATION_STATUS_CORRECTED_COUNT_ONLY_NO_DIAGNOSTICS"
PREFILTER_ZERO_FLAG = "RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO"
AUTHOR_QUERY_MS = 1.865660


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
        description="Record the Phoenix V3 Spatial count-only/no-diagnostics no-go experiment."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_packet() -> dict[str, Any]:
    diagnostic = _read_json(DIAGNOSTIC_PACKET)
    count_only = _read_json(COUNT_ONLY_PACKET)
    diagnostic_stats = _stats(diagnostic)
    count_only_stats = _stats(count_only)
    source_text = NATIVE_SOURCE.read_text(encoding="utf-8")
    delta_ms = count_only_stats["prepared_query_ms_median"] - diagnostic_stats["prepared_query_ms_median"]
    rt_delta_ms = count_only_stats["rt_traversal_ms_median"] - diagnostic_stats["rt_traversal_ms_median"]
    count_only_relative = (
        diagnostic_stats["prepared_query_ms_median"] / count_only_stats["prepared_query_ms_median"]
    )
    checks = {
        "diagnostic_packet_exists": DIAGNOSTIC_PACKET.exists(),
        "count_only_packet_exists": COUNT_ONLY_PACKET.exists(),
        "diagnostic_failed_checks_empty": diagnostic["failed_checks"] == [],
        "count_only_failed_checks_empty": count_only["failed_checks"] == [],
        "diagnostic_exact_count_47262": diagnostic_stats["row_count"] == 47262,
        "count_only_exact_count_47262": count_only_stats["row_count"] == 47262,
        "diagnostic_counts_consistent": diagnostic_stats["row_count_consistent"] is True,
        "count_only_counts_consistent": count_only_stats["row_count_consistent"] is True,
        "diagnostic_raw_candidates_present": all(
            raw == 47570 for raw in diagnostic_stats["raw_candidate_counts"]
        ),
        "count_only_diagnostics_suppressed": all(
            raw == 0 for raw in count_only_stats["raw_candidate_counts"]
        ),
        "count_only_not_faster_than_diagnostic": delta_ms > 0.0,
        "count_only_still_slower_than_author_query": (
            count_only_stats["prepared_query_ms_median"] > AUTHOR_QUERY_MS
        ),
        "native_source_does_not_keep_failed_count_only_flag": COUNT_ONLY_FLAG not in source_text,
        "native_source_keeps_prefilter_zero_flag": PREFILTER_ZERO_FLAG in source_text,
        "all_public_claim_flags_false": (
            _claim_flags_false(diagnostic) and _claim_flags_false(count_only)
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "tool": "v3_phoenix_spatial_relation_status_count_only_no_diagnostics_no_go",
        "status": (
            "fail"
            if failed_checks
            else "spatial_relation_status_count_only_no_diagnostics_no_go_not_m7"
        ),
        "generic_capability": "point_location_topology_stream",
        "candidate": {
            "name": "relation_status_corrected_count_only_no_diagnostics",
            "tested_flag": COUNT_ONLY_FLAG,
            "default_enabled": False,
            "source_retained": False,
            "decision": (
                "Rejected. Suppressing diagnostic candidate atomics preserved the "
                "exact count but did not improve the prepared-query median."
            ),
        },
        "surviving_related_candidate": {
            "name": "relation_status_zero_prefilter",
            "flag": PREFILTER_ZERO_FLAG,
            "status": "near_miss_not_m7",
        },
        "dataset": "data/rayjoin_public_cdb/br_county.cdb",
        "pod": {
            "host": "213.173.108.14:11592",
            "gpu": "NVIDIA RTX 4000 Ada Generation, 550.127.05",
            "remote_repo": "/root/rtdl_v3_rebuild_20260620/current",
        },
        "evidence": {
            "dir": _rel(EVIDENCE_DIR),
            "diagnostic_packet": _rel(DIAGNOSTIC_PACKET),
            "count_only_packet": _rel(COUNT_ONLY_PACKET),
        },
        "provenance_limitations": {
            "pod_evidence_git_commit": None,
            "reason": (
                "The POD measurement source copy at /root/rtdl_v3_rebuild_20260620/current "
                "was not a git checkout, so the runner recorded git_commit as null."
            ),
            "mitigation": (
                "The no-go packet records the exact copied evidence files, GPU identity, "
                "remote source path, live current-source absence of the failed flag, and "
                "tests that rebuild the packet from those evidence files."
            ),
            "future_requirement": (
                "Future POD evidence packets should include a git commit or explicit "
                "source_manifest.sha256 for the measured source tree."
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
        "diagnostic_prefilter_zero": diagnostic_stats,
        "count_only_no_diagnostics": count_only_stats,
        "comparison": {
            "prepared_query_delta_ms_count_only_minus_diagnostic": delta_ms,
            "rt_traversal_delta_ms_count_only_minus_diagnostic": rt_delta_ms,
            "count_only_relative_to_diagnostic": count_only_relative,
            "author_query_ms": AUTHOR_QUERY_MS,
            "count_only_gap_to_author_ms": count_only_stats["prepared_query_ms_median"] - AUTHOR_QUERY_MS,
            "diagnostic_gap_to_author_ms": diagnostic_stats["prepared_query_ms_median"] - AUTHOR_QUERY_MS,
        },
        "summary": {
            "m7_rows_added": 0,
            "diagnostic_prepared_query_ms_median": diagnostic_stats["prepared_query_ms_median"],
            "count_only_prepared_query_ms_median": count_only_stats["prepared_query_ms_median"],
            "prepared_query_delta_ms": delta_ms,
            "count_only_was_faster": delta_ms < 0.0,
            "count_only_preserved_exact_count": count_only_stats["row_count"] == 47262,
            "count_only_source_retained": False,
            "status": "rejected_no_go",
        },
        "required_next_actions": [
            "Do not reintroduce the count-only/no-diagnostics flag without new evidence.",
            "Do not promote Spatial topology-stream to M7 from this packet.",
            "Continue only with correctness-preserving generic optimizations that can beat the 1.865660 ms author Query bar with stable margin.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Reject and remove the count-only/no-diagnostics Spatial hot-path candidate."
            ),
            "was_i_foolish": (
                "No in the final decision: the evidence shows the candidate is slower, "
                "so rejecting it is the responsible move."
            ),
            "foolish_actions": (
                "The foolish action would be to keep a default-off code path just "
                "because it sounded plausible, or to rerun it repeatedly after a "
                "clean paired test showed no benefit."
            ),
            "other_path": (
                "Leave it in source as an experimental flag. That would increase "
                "surface area without helping V3 performance."
            ),
            "different_path_now": (
                "Record the no-go, keep the correct prefilter-zero near-miss, and "
                "move to another generic topology-stream bottleneck."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    summary = packet["summary"]
    comparison = packet["comparison"]
    audit = packet["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial Count-Only/No-Diagnostics No-Go",
        "",
        f"Status: `{packet['status']}`.",
        "",
        "This packet closes a focused follow-up to the Spatial relation-status",
        "prefilter-zero near-miss. Removing diagnostic atomics from the exact",
        "scalar-count hot path preserved the count but did not improve the stable",
        "prepared-query median, so the code path was removed.",
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
        f"- Diagnostic prefilter-zero median: `{summary['diagnostic_prepared_query_ms_median']:.6f} ms`",
        f"- Count-only/no-diagnostics median: `{summary['count_only_prepared_query_ms_median']:.6f} ms`",
        f"- Delta count-only minus diagnostic: `{summary['prepared_query_delta_ms']:.6f} ms`",
        f"- Count-only faster: `{str(summary['count_only_was_faster']).lower()}`",
        f"- Count-only preserved exact count: `{str(summary['count_only_preserved_exact_count']).lower()}`",
        f"- Count-only gap to author Query: `{comparison['count_only_gap_to_author_ms']:.6f} ms`",
        f"- Count-only source retained: `{str(summary['count_only_source_retained']).lower()}`",
        "",
        "## Evidence",
        "",
        f"- Diagnostic packet: `{packet['evidence']['diagnostic_packet']}`",
        f"- Count-only packet: `{packet['evidence']['count_only_packet']}`",
        f"- Dataset: `{packet['dataset']}`",
        "",
        "## Provenance Limitation",
        "",
        f"- POD evidence git commit: `{packet['provenance_limitations']['pod_evidence_git_commit']}`",
        f"- Reason: {packet['provenance_limitations']['reason']}",
        f"- Mitigation: {packet['provenance_limitations']['mitigation']}",
        f"- Future requirement: {packet['provenance_limitations']['future_requirement']}",
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


def _stats(packet: dict[str, Any]) -> dict[str, Any]:
    prepared_ms = [
        _ms(sample["phases_sec"]["prepared_query_sec"]) for sample in packet["samples"]
    ]
    traversal_ms = [
        _ms(sample["native_phase_timings"]["candidate_count_pass"])
        for sample in packet["samples"]
    ]
    return {
        "status": packet["status"],
        "failed_checks": packet["failed_checks"],
        "sample_repeat": int(packet["sample_repeat"]),
        "query_repeat": int(packet["query_repeat"]),
        "warmup": int(packet["warmup"]),
        "row_count": int(packet["summary"]["row_count"]),
        "row_count_consistent": bool(packet["summary"]["row_count_consistent"]),
        "prepared_query_ms_median": statistics.median(prepared_ms),
        "prepared_query_ms_best": min(prepared_ms),
        "prepared_query_ms_max": max(prepared_ms),
        "rt_traversal_ms_median": statistics.median(traversal_ms),
        "rt_traversal_ms_best": min(traversal_ms),
        "rt_traversal_ms_max": max(traversal_ms),
        "raw_candidate_counts": [
            int(sample["native_phase_timings"]["raw_candidate_count"])
            for sample in packet["samples"]
        ],
        "emitted_counts": [
            int(sample["native_phase_timings"]["emitted_count"])
            for sample in packet["samples"]
        ],
    }


def _claim_flags_false(packet: dict[str, Any]) -> bool:
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
    return all(packet.get(key) is False for key in keys)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ms(seconds: float) -> float:
    return float(seconds) * 1000.0


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
