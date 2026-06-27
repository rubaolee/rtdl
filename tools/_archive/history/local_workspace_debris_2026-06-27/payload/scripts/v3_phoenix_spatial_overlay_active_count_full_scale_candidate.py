#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_overlay_full_active_count_20260621"
    / "full_overlay_repeat25_m3.json"
)
DEFAULT_JSON_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_overlay_active_count_full_scale_candidate_2026-06-21.json"
)
DEFAULT_MD_OUT = DEFAULT_JSON_OUT.with_suffix(".md")

OUTPUT_CONTRACT = "overlay_active_pair_dependency_count"
GENERIC_CAPABILITY = "point_location_topology_stream"
MIN_PAIR_COUNT_FOR_FULL_SCALE_REVIEW = 1_000_000
MIN_REPEAT_FOR_REVIEW = 20
MIN_WALL_SPEEDUP_FOR_REVIEW = 1.20


def main() -> int:
    args = parse_args()
    payload = build_payload(
        evidence_path=args.evidence,
        min_pair_count=args.min_pair_count,
        min_repeat=args.min_repeat,
        min_wall_speedup=args.min_wall_speedup,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["failed_checks"] == [] else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate full-scale Spatial RayJoin overlay active-count evidence for Phoenix V3."
    )
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--min-pair-count", type=int, default=MIN_PAIR_COUNT_FOR_FULL_SCALE_REVIEW)
    parser.add_argument("--min-repeat", type=int, default=MIN_REPEAT_FOR_REVIEW)
    parser.add_argument("--min-wall-speedup", type=float, default=MIN_WALL_SPEEDUP_FOR_REVIEW)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_payload(
    *,
    evidence_path: Path,
    min_pair_count: int,
    min_repeat: int,
    min_wall_speedup: float,
) -> dict[str, Any]:
    evidence_path = evidence_path.resolve()
    evidence = _read_json(evidence_path) if evidence_path.exists() else {}
    rows = {str(row.get("backend")): row for row in evidence.get("rows", []) if isinstance(row, dict)}
    optix = rows.get("optix", {})
    embree = rows.get("embree", {})
    case_shape = evidence.get("case_shape", {})
    comparison = evidence.get("comparison", {})
    table = optix.get("topology_stream_m3_phase_table") or {}
    handle = optix.get("topology_stream_prepared_handle") or {}

    left_count = _int_or_none(case_shape.get("left_shape_count"))
    right_count = _int_or_none(case_shape.get("right_shape_count"))
    pair_count = None if left_count is None or right_count is None else left_count * right_count
    optix_repeat = _int_or_none(optix.get("repeat"))
    embree_repeat = _int_or_none(embree.get("repeat"))
    wall_speedup = comparison.get("embree_over_optix_timed_median")
    optix_active_count = _int_or_none(optix.get("active_count"))
    embree_active_count = _int_or_none(embree.get("active_count"))
    active_count_delta = (
        None
        if optix_active_count is None or embree_active_count is None
        else optix_active_count - embree_active_count
    )

    checks = {
        "evidence_file_exists": evidence_path.exists(),
        "evidence_status_ok": evidence.get("status") == "ok",
        "both_backends_present": set(rows) == {"embree", "optix"},
        "same_output_contract": comparison.get("same_output_contract") is True
        and optix.get("output_contract") == embree.get("output_contract") == OUTPUT_CONTRACT,
        "active_counts_match": comparison.get("active_counts_match") is True,
        "all_counts_stable": comparison.get("all_counts_stable") is True,
        "row_materialization_avoided": comparison.get("all_row_materialization_avoided") is True,
        "full_scale_pair_count": pair_count is not None and pair_count >= int(min_pair_count),
        "repeat_floor_met": optix_repeat is not None
        and embree_repeat is not None
        and optix_repeat >= int(min_repeat)
        and embree_repeat >= int(min_repeat),
        "wall_speedup_floor_met": isinstance(wall_speedup, (int, float))
        and float(wall_speedup) >= float(min_wall_speedup),
        "optix_m3_table_present": table.get("contract") == "topology_stream_m3_phase_table_v1",
        "optix_m3_table_complete": table.get("full_m3_phase_table_complete") is True,
        "optix_prepared_handle_present": handle.get("contract") == "topology_stream_prepared_handle_v1",
        "optix_prepared_handle_generic_capability": handle.get("generic_capability") == GENERIC_CAPABILITY,
        "all_claim_flags_false": _all_claim_flags_false(evidence, optix, embree, table, handle),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    local_review_ready = not failed_checks
    status = (
        "spatial_overlay_active_count_full_scale_m7_candidate_pending_external_review"
        if local_review_ready
        else "spatial_overlay_active_count_full_scale_no_go"
    )
    candidate_row_id = _candidate_row_id(left_count=left_count, right_count=right_count, repeat=optix_repeat)
    return {
        "tool": "v3_phoenix_spatial_overlay_active_count_full_scale_candidate",
        "status": status,
        "source_evidence": _rel(evidence_path),
        "generic_capability": GENERIC_CAPABILITY,
        "output_contract": OUTPUT_CONTRACT,
        "candidate_row_id": candidate_row_id,
        "local_evidence_sufficient_for_external_public_row_review": local_review_ready,
        "candidate_m7_contribution_if_external_review_approves": 1 if local_review_ready else 0,
        "m7_qualified_release_rows_added_now": 0,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "metrics": {
            "left_shape_count": left_count,
            "right_shape_count": right_count,
            "shape_pair_count": pair_count,
            "active_count": comparison.get("active_count"),
            "optix_active_count": optix_active_count,
            "embree_active_count": embree_active_count,
            "optix_minus_embree_active_count": active_count_delta,
            "optix_repeat": optix_repeat,
            "embree_repeat": embree_repeat,
            "optix_timed_median_sec": optix.get("timed_median_sec"),
            "embree_timed_median_sec": embree.get("timed_median_sec"),
            "embree_over_optix_timed_median": wall_speedup,
            "optix_m3_phase_seconds": table.get("phase_seconds"),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "required_before_m7": [
            "External AI review of this exact packet.",
            "Codex consensus file after external review.",
            "Public wording must say active-count topology stream only, not full polygon overlay.",
            "Public wording must not claim RayJoin paper Section 5.7 reproduction or RTDL beats RayJoin.",
            "Public wording must not claim broad V3-over-V2 speedup.",
        ],
        "goal_level_decision_audit": {
            "decision": "Evaluate full-scale overlay active-count as a possible Phoenix V3 topology-stream row, without promotion.",
            "was_i_foolish": (
                "No for this gate. It requires full-scale shape-pair count, stable same-contract counts, "
                "complete M3 metadata, and external review before any row can count."
            ),
            "foolish_actions": (
                "The foolish action would be to recycle the old 499x subset row as public proof without "
                "full-scale evidence, M3 table, and review; another foolish action was earlier using the "
                "Windows py launcher on Linux, which is now corrected to python3."
            ),
            "other_path": (
                "Keep only the PIP route and accept no M7 topology row. That remains valid if this "
                "active-count contract fails scale or review."
            ),
            "different_path_now": (
                "Use this as a narrow reusable topology-stream candidate only if the full-scale evidence "
                "passes, then seek Claude/Codex review before changing any release gate."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial Overlay Active-Count Full-Scale Candidate",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"row_scoped_public_speedup_claim_authorized: {str(payload['row_scoped_public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added now: {payload['m7_qualified_release_rows_added_now']}",
        "```",
        "",
        "## Candidate",
        "",
        f"- Row id: `{payload['candidate_row_id']}`",
        f"- Generic capability: `{payload['generic_capability']}`",
        f"- Output contract: `{payload['output_contract']}`",
        f"- Source evidence: `{payload['source_evidence']}`",
        f"- Local review-ready: `{payload['local_evidence_sufficient_for_external_public_row_review']}`",
        "",
        "## Metrics",
        "",
        f"- Left/right shapes: `{metrics['left_shape_count']}` / `{metrics['right_shape_count']}`",
        f"- Shape-pair count: `{metrics['shape_pair_count']}`",
        f"- Active count: `{metrics['active_count']}`",
        f"- OptiX / Embree active count: `{metrics['optix_active_count']}` / `{metrics['embree_active_count']}`",
        f"- OptiX minus Embree active count: `{metrics['optix_minus_embree_active_count']}`",
        f"- Repeat OptiX/Embree: `{metrics['optix_repeat']}` / `{metrics['embree_repeat']}`",
        f"- OptiX timed median sec: `{metrics['optix_timed_median_sec']}`",
        f"- Embree timed median sec: `{metrics['embree_timed_median_sec']}`",
        f"- Embree / OptiX wall speedup: `{metrics['embree_over_optix_timed_median']}`",
        "",
        "## Failed Checks",
        "",
    ]
    if payload["failed_checks"]:
        lines.extend(f"- `{item}`" for item in payload["failed_checks"])
    else:
        lines.append("- none")
    lines.extend(["", "## Required Before M7", ""])
    lines.extend(f"- {item}" for item in payload["required_before_m7"])
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _all_claim_flags_false(*items: dict[str, Any]) -> bool:
    keys = (
        "release_authorized",
        "public_speedup_claim_authorized",
        "row_scoped_public_speedup_claim_authorized",
        "m7_promotion_authorized",
        "whole_app_speedup_claim_authorized",
        "paper_reproduction_claim_authorized",
        "rtdl_beats_rayjoin_claim_authorized",
        "true_zero_copy_claim_authorized",
        "rt_core_speedup_claim_authorized",
    )
    for item in items:
        claim_boundary = item.get("claim_boundary") if isinstance(item, dict) else None
        for source in (item, claim_boundary if isinstance(claim_boundary, dict) else {}):
            for key in keys:
                if source.get(key) is True:
                    return False
    return True


def _candidate_row_id(*, left_count: int | None, right_count: int | None, repeat: int | None) -> str:
    left = "unknown" if left_count is None else str(left_count)
    right = "unknown" if right_count is None else str(right_count)
    rep = "unknown" if repeat is None else str(repeat)
    return f"overlay_active_count_full_scale_shape_pair_{left}x{right}_repeat{rep}_row_scoped"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
