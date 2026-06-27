#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RERANK = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m6_barnes_hut_20260620"
    / "m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json"
)
DEFAULT_JSON_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.json"
)
DEFAULT_MD_OUT = DEFAULT_JSON_OUT.with_suffix(".md")

EXPECTED_ROUTES = (
    "cpu_numba_fused",
    "numba_cuda_fused",
    "optix_numba_prepared_frontier",
    "optix_cupy_prepared_frontier",
)
CLAIM_FLAG_KEYS = (
    "automatic_partner_selection_authorized",
    "rt_core_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "public_speedup_claim_authorized",
    "app_specific_native_engine_logic_allowed",
)
CHECKSUM_ABS_TOL = 1.0e-4
CHECKSUM_REL_TOL = 1.0e-9


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def _check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _claim_flags_false(payload: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(payload.get(key) is False for key in keys)


def _rows_by_body(payload: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    by_body: dict[int, list[dict[str, Any]]] = {}
    for row in payload.get("rows", []):
        by_body.setdefault(int(row["body_count"]), []).append(dict(row))
    return by_body


def _checksum_tolerance(values: list[float]) -> float:
    max_abs = max((abs(value) for value in values), default=0.0)
    return max(CHECKSUM_ABS_TOL, CHECKSUM_REL_TOL * max_abs)


def _checksum_delta(values: list[float]) -> float:
    if not values:
        return math.inf
    return max(values) - min(values)


def _ms(seconds: float | None) -> float | None:
    if seconds is None:
        return None
    return round(float(seconds) * 1000.0, 6)


def _same_basis_seconds(row: dict[str, Any]) -> float:
    value = row.get("repeat_seconds_median")
    if value is None:
        value = row.get("call_wall_median_seconds")
    if value is None:
        value = row.get("hot_median_seconds")
    return float(value)


def _body_summary(body_count: int, rows: list[dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    by_route = {str(row.get("route_id")): row for row in rows}
    route_ids = set(by_route)
    missing = tuple(route for route in EXPECTED_ROUTES if route not in route_ids)
    extra = tuple(sorted(route_ids - set(EXPECTED_ROUTES)))
    _check(not missing, f"{body_count}: missing routes: {missing}", failures)
    _check(not extra, f"{body_count}: unexpected routes: {extra}", failures)

    contribution_counts = [int(row.get("contribution_row_count", -1)) for row in rows]
    _check(
        len(set(contribution_counts)) == 1,
        f"{body_count}: contribution row counts differ: {contribution_counts}",
        failures,
    )
    checksum_x = [float(row.get("checksum_force_x", math.nan)) for row in rows]
    checksum_y = [float(row.get("checksum_force_y", math.nan)) for row in rows]
    _check(all(math.isfinite(value) for value in checksum_x), f"{body_count}: non-finite x checksum", failures)
    _check(all(math.isfinite(value) for value in checksum_y), f"{body_count}: non-finite y checksum", failures)
    delta_x = _checksum_delta(checksum_x)
    delta_y = _checksum_delta(checksum_y)
    tolerance_x = _checksum_tolerance(checksum_x)
    tolerance_y = _checksum_tolerance(checksum_y)
    _check(delta_x <= tolerance_x, f"{body_count}: x checksum delta {delta_x} exceeds {tolerance_x}", failures)
    _check(delta_y <= tolerance_y, f"{body_count}: y checksum delta {delta_y} exceeds {tolerance_y}", failures)

    route_rows: list[dict[str, Any]] = []
    for route_id in EXPECTED_ROUTES:
        row = by_route.get(route_id)
        if row is None:
            continue
        same_seconds = _same_basis_seconds(row)
        route_rows.append(
            {
                "route_id": route_id,
                "same_basis_wall_repeat_seconds": same_seconds,
                "same_basis_wall_repeat_ms": _ms(same_seconds),
                "original_hot_median_seconds": row.get("hot_median_seconds"),
                "original_hot_time_kind": row.get("hot_time_kind"),
                "repeat_seconds_median": row.get("repeat_seconds_median"),
                "call_wall_median_seconds": row.get("call_wall_median_seconds"),
                "partner_wall_median_seconds": row.get("partner_wall_median_seconds"),
                "frontier_traversal_median_seconds": row.get("frontier_traversal_median_seconds"),
                "rt_core_accelerated_metadata": row.get("rt_core_accelerated_metadata"),
                "public_speedup_claim_authorized": row.get("public_speedup_claim_authorized"),
                "rt_core_speedup_claim_authorized": row.get("rt_core_speedup_claim_authorized"),
            }
        )
        _check(
            row.get("repeat_seconds_median") is not None,
            f"{body_count}/{route_id}: repeat_seconds_median missing for same-basis wall comparison",
            failures,
        )
        _check(
            row.get("public_speedup_claim_authorized") is False,
            f"{body_count}/{route_id}: public speedup flag is not false",
            failures,
        )
        _check(
            row.get("rt_core_speedup_claim_authorized") is False,
            f"{body_count}/{route_id}: RT-core speedup flag is not false",
            failures,
        )

    fastest = min(route_rows, key=lambda row: float(row["same_basis_wall_repeat_seconds"])) if route_rows else {}
    optix_numba = next((row for row in route_rows if row["route_id"] == "optix_numba_prepared_frontier"), {})
    optix_cupy = next((row for row in route_rows if row["route_id"] == "optix_cupy_prepared_frontier"), {})
    fastest_seconds = float(fastest.get("same_basis_wall_repeat_seconds", math.nan)) if fastest else math.nan
    optix_numba_seconds = float(optix_numba.get("same_basis_wall_repeat_seconds", math.nan)) if optix_numba else math.nan
    optix_cupy_seconds = float(optix_cupy.get("same_basis_wall_repeat_seconds", math.nan)) if optix_cupy else math.nan

    return {
        "body_count": body_count,
        "route_rows": route_rows,
        "contribution_row_count": contribution_counts[0] if contribution_counts else None,
        "route_parity_passed": (
            not missing
            and not extra
            and len(set(contribution_counts)) == 1
            and delta_x <= tolerance_x
            and delta_y <= tolerance_y
        ),
        "checksum_delta_x": delta_x,
        "checksum_delta_y": delta_y,
        "checksum_tolerance_x": tolerance_x,
        "checksum_tolerance_y": tolerance_y,
        "fastest_same_basis_route_id": fastest.get("route_id"),
        "fastest_same_basis_ms": _ms(fastest_seconds) if math.isfinite(fastest_seconds) else None,
        "optix_numba_same_basis_ms": _ms(optix_numba_seconds) if math.isfinite(optix_numba_seconds) else None,
        "optix_cupy_same_basis_ms": _ms(optix_cupy_seconds) if math.isfinite(optix_cupy_seconds) else None,
        "optix_numba_over_fastest_same_basis": (
            optix_numba_seconds / fastest_seconds
            if math.isfinite(optix_numba_seconds) and math.isfinite(fastest_seconds) and fastest_seconds > 0.0
            else None
        ),
        "optix_cupy_over_fastest_same_basis": (
            optix_cupy_seconds / fastest_seconds
            if math.isfinite(optix_cupy_seconds) and math.isfinite(fastest_seconds) and fastest_seconds > 0.0
            else None
        ),
    }


def build_payload(rerank_json: Path = DEFAULT_RERANK) -> dict[str, Any]:
    failures: list[str] = []
    rerank_json = rerank_json.resolve()
    _check(rerank_json.exists(), f"missing rerank artifact: {rerank_json}", failures)
    source = _read_json(rerank_json) if rerank_json.exists() else {}

    _check(source.get("dry_run") is False, "rerank artifact is a dry run", failures)
    _check(int(source.get("repeat", 0)) >= 11, "repeat count is below serious-run floor 11", failures)
    _check(int(source.get("warmup", -1)) >= 2, "warmup count is below serious-run floor 2", failures)
    _check(
        _claim_flags_false(source.get("claim_flags", {}), CLAIM_FLAG_KEYS),
        "top-level claim flags are not all false",
        failures,
    )

    body_summaries = [
        _body_summary(body_count, rows, failures)
        for body_count, rows in sorted(_rows_by_body(source).items())
    ]
    fastest_by_scale = {
        str(row["body_count"]): row["fastest_same_basis_route_id"] for row in body_summaries
    }
    optix_numba_ratios = {
        str(row["body_count"]): row["optix_numba_over_fastest_same_basis"]
        for row in body_summaries
    }
    optix_cupy_ratios = {
        str(row["body_count"]): row["optix_cupy_over_fastest_same_basis"]
        for row in body_summaries
    }
    all_fastest_numba_cuda = all(route == "numba_cuda_fused" for route in fastest_by_scale.values())
    optix_numba_slower_all = all(
        ratio is not None and float(ratio) > 1.0 for ratio in optix_numba_ratios.values()
    )
    route_parity_passed = all(bool(row["route_parity_passed"]) for row in body_summaries)
    min_optix_numba_gap = min(float(ratio) for ratio in optix_numba_ratios.values() if ratio is not None)
    checks = {
        "rerank_artifact_exists": rerank_json.exists(),
        "serious_repeat_floor": int(source.get("repeat", 0)) >= 11,
        "serious_warmup_floor": int(source.get("warmup", -1)) >= 2,
        "not_dry_run": source.get("dry_run") is False,
        "claim_flags_false": _claim_flags_false(source.get("claim_flags", {}), CLAIM_FLAG_KEYS),
        "body_summaries_present": bool(body_summaries),
        "route_parity_passed": route_parity_passed,
        "same_basis_uses_wall_repeat_for_all_rows": all(
            row_item["repeat_seconds_median"] is not None
            for summary in body_summaries
            for row_item in summary["route_rows"]
        ),
        "timing_basis_mixed_removed_for_ratios": all(
            row_item["same_basis_wall_repeat_seconds"] == row_item["repeat_seconds_median"]
            for summary in body_summaries
            for row_item in summary["route_rows"]
        ),
        "fused_numba_cuda_fastest_all_scales_same_basis": all_fastest_numba_cuda,
        "prepared_optix_numba_slower_all_scales_same_basis": optix_numba_slower_all,
        "prepared_optix_numba_min_gap_above_2x_same_basis": min_optix_numba_gap > 2.0,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    failures.extend(f"check failed: {name}" for name in failed_checks)
    status = (
        "barnes_hut_same_basis_no_go_current_frontier_shape_not_m7"
        if not failures
        else "fail"
    )

    return {
        "tool": "v3_phoenix_barnes_hut_same_basis_wall_time_no_go",
        "version": "phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026_06_21",
        "status": status,
        "generic_capability": "aggregate_frontier",
        "refined_generic_capability": "vector_accumulation",
        "source_artifact": _rel(rerank_json) if rerank_json.exists() else str(rerank_json),
        "same_basis_timing_kind": "wall_repeat_median_seconds",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "aggregate_frontier_m7_gap_closed": False,
        "current_prepared_optix_frontier_shape_m7_authorized": False,
        "fused_partner_route_is_fastest_same_basis": all_fastest_numba_cuda,
        "fused_partner_route_may_be_pursued_as_separate_v3_partner_row": True,
        "fused_partner_route_m7_authorized_by_this_packet": False,
        "body_summaries": body_summaries,
        "same_basis_summary": {
            "fastest_by_scale": fastest_by_scale,
            "prepared_optix_numba_over_fastest": optix_numba_ratios,
            "prepared_optix_cupy_over_fastest": optix_cupy_ratios,
            "min_prepared_optix_numba_over_fastest": min_optix_numba_gap,
            "all_fastest_numba_cuda": all_fastest_numba_cuda,
            "prepared_optix_numba_slower_all_scales": optix_numba_slower_all,
        },
        "decision": (
            "Same-basis wall timing removes the mixed-timing objection but does not rescue "
            "the current prepared RTDL/OptiX frontier-emission shape. The V3 performance path "
            "is the reusable fused aggregate-tree/vector partner route, not an app-specific "
            "Barnes-Hut native engine and not an RT-core speedup claim."
        ),
        "next_actions": [
            "Keep current prepared OptiX frontier-emission Barnes-Hut rows out of M7.",
            "If aggregate_frontier is reopened, use a separate public-row review for the generic fused vector-accumulation partner contract.",
            "Do not claim RT-core acceleration for the Numba CUDA fused partner route.",
            "Do not use this packet as whole-app Barnes-Hut, paper reproduction, or broad V3-over-V2 evidence.",
            "Require external AI review before any M7 classification packet is updated from this evidence.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "failures": failures,
        "goal_level_decision_audit": {
            "decision": "Close the current aggregate_frontier RT frontier-emission path as same-basis no-go, while preserving the generic fused partner path as the next V3 candidate.",
            "was_i_foolish": "No. I rechecked the historical artifact under one wall-clock basis before deciding.",
            "foolish_actions": (
                "The foolish action would be to keep blaming mixed timing after the wall-repeat fields already "
                "show the same ordering, or to promote a slow OptiX route because it contains RTDL machinery."
            ),
            "other_path": (
                "I could have rerun the pod first. That is still valid if external review asks for it, but the "
                "saved serious-run artifact already has the needed wall-repeat fields for this bounded decision."
            ),
            "different_path_now": (
                "Advance V3 through the reusable fused aggregate/vector partner contract, with a separate M7 review, "
                "instead of forcing the current RT frontier-emission shape into release."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Barnes-Hut Same-Basis Wall-Time No-Go",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet re-reads the M6 Barnes-Hut rerank artifact with one timing basis:",
        "`repeat_seconds_median` wall time for every route. It does not authorize a release row.",
        "",
        "```text",
        f"same_basis_timing_kind: {payload['same_basis_timing_kind']}",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"rt_core_speedup_claim_authorized: {str(payload['rt_core_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Same-Basis Result",
        "",
        "| Bodies | Fastest wall route | Fastest wall | OptiX+Numba wall | OptiX+Numba / fastest | OptiX+CuPy / fastest | Contribution rows |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["body_summaries"]:
        lines.append(
            "| "
            f"{int(row['body_count']):,} | `{row['fastest_same_basis_route_id']}` | "
            f"{float(row['fastest_same_basis_ms']):.3f} ms | "
            f"{float(row['optix_numba_same_basis_ms']):.3f} ms | "
            f"{float(row['optix_numba_over_fastest_same_basis']):.3f}x | "
            f"{float(row['optix_cupy_over_fastest_same_basis']):.3f}x | "
            f"{int(row['contribution_row_count']):,} |"
        )
    lines.extend(
        [
            "",
            payload["decision"],
            "",
            "## Boundary",
            "",
            "- Current prepared RTDL/OptiX frontier-emission rows remain not M7.",
            "- The fused Numba CUDA route is not an RT-core result.",
            "- This is not whole-app Barnes-Hut evidence, not paper reproduction, and not broad V3-over-V2 evidence.",
            "- A future aggregate-frontier M7 attempt must be a separate reusable partner-contract review.",
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["next_actions"])
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made it foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
            "",
            "## Failures",
            "",
        ]
    )
    if payload["failures"]:
        lines.extend(f"- {failure}" for failure in payload["failures"])
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-read Phoenix V3 Barnes-Hut M6 evidence under a single wall-time basis."
    )
    parser.add_argument("--rerank-json", type=Path, default=DEFAULT_RERANK)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.rerank_json)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(text + "\n", encoding="utf-8")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(text)
    return 0 if payload["status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
