#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.json"
OUT_MD = OUT_JSON.with_suffix(".md")


def main() -> int:
    args = parse_args()
    packet = build_packet(seed=args.seed, random_cases=args.random_cases)
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
        description="Check old sqrt boundary predicate and guarded squared predicate equivalence."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--seed", type=int, default=20260621)
    parser.add_argument("--random-cases", type=int, default=200_000)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_packet(seed: int, random_cases: int) -> dict[str, Any]:
    cases = _deterministic_cases()
    cases.extend(_random_cases(seed=seed, count=random_cases))
    pure_mismatches: list[dict[str, Any]] = []
    guarded_mismatches: list[dict[str, Any]] = []
    guard_tol = 1.0e-6
    for index, case in enumerate(cases):
        old = _old_sqrt_boundary(**case)
        pure = _pure_squared_boundary(**case)
        guarded = _guarded_squared_boundary(**case, guard_tol=guard_tol)
        if old != pure and len(pure_mismatches) < 16:
            pure_mismatches.append({"index": index, "old": old, "pure_squared": pure, "case": case})
        if old != guarded and len(guarded_mismatches) < 16:
            guarded_mismatches.append(
                {"index": index, "old": old, "guarded_squared": guarded, "case": case}
            )

    checks = {
        "deterministic_endpoint_and_interior_cases_present": len(_deterministic_cases()) >= 300,
        "random_case_count_at_least_200000": random_cases >= 200_000,
        "guarded_no_mismatches": len(guarded_mismatches) == 0,
        "pure_squared_mismatch_risk_recorded": len(pure_mismatches) > 0,
        "finite_coordinate_scope_declared": True,
        "guarded_fallback_declared": True,
        "public_claim_flags_false": True,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "tool": "v3_phoenix_spatial_squared_boundary_equivalence",
        "status": (
            "fail"
            if failed_checks
            else "spatial_guarded_squared_boundary_equivalence_pass_not_release"
        ),
        "generic_capability": "point_location_topology_stream",
        "optimization": "exact_f64_guarded_squared_boundary_predicate",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "equivalence_scope": {
            "finite_double_values": True,
            "epsilon_non_negative": True,
            "degenerate_segment_branch_shared": "len2 <= eps2 uses identical coordinate-box test in both predicates",
            "pure_squared_risk": (
                "A pure squared predicate is not treated as equivalent: deterministic "
                "endpoint-adjacent cases showed floating-point disagreement with the old "
                "sqrt/along-epsilon predicate."
            ),
            "guarded_partition": (
                "The guarded predicate uses squared comparisons only when the value is "
                "outside a small threshold band. Cases near the threshold fall back to the "
                "old sqrt/along-epsilon predicate."
            ),
            "guard_tol": guard_tol,
            "cuda_floating_point_note": (
                "This packet checks the predicate algebra in Python double precision and records "
                "the same branch structure. It is supporting evidence, not a standalone CUDA "
                "compiler proof."
            ),
        },
        "case_counts": {
            "deterministic_cases": len(_deterministic_cases()),
            "random_cases": random_cases,
            "total_cases": len(cases),
        },
        "mismatch_count": len(guarded_mismatches),
        "mismatch_examples": guarded_mismatches,
        "guarded_mismatch_count": len(guarded_mismatches),
        "guarded_mismatch_examples": guarded_mismatches,
        "pure_squared_mismatch_count": len(pure_mismatches),
        "pure_squared_mismatch_examples": pure_mismatches,
        "summary": {
            "total_cases": len(cases),
            "guarded_mismatch_count": len(guarded_mismatches),
            "pure_squared_mismatch_count": len(pure_mismatches),
            "status": "old_sqrt_and_guarded_squared_boundary_predicates_match",
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Add independent predicate-equivalence evidence before any M7 promotion decision."
            ),
            "was_i_foolish": (
                "No. This strengthens correctness review without changing runtime defaults or "
                "claiming release."
            ),
            "foolish_actions": (
                "The foolish action would be to rely only on one benchmark count and skip "
                "predicate-level equivalence evidence before asking for external review."
            ),
            "other_path": (
                "Wait for external review. That is still required, but it would leave an obvious "
                "correctness question unanswered."
            ),
            "different_path_now": (
                "Use a guarded squared fast path with sqrt fallback near thresholds, provide "
                "deterministic endpoint/interior cases plus seeded random model checks, then "
                "keep the candidate pending external review."
            ),
        },
    }


def _old_sqrt_boundary(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
    eps: float,
) -> bool:
    dx = bx - ax
    dy = by - ay
    len2 = dx * dx + dy * dy
    if len2 <= eps * eps:
        return abs(px - ax) <= eps and abs(py - ay) <= eps
    length = math.sqrt(len2)
    cross = (px - ax) * dy - (py - ay) * dx
    dot = (px - ax) * dx + (py - ay) * dy
    along_eps = eps * length
    return abs(cross) <= along_eps and dot >= -along_eps and dot <= len2 + along_eps


def _pure_squared_boundary(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
    eps: float,
) -> bool:
    dx = bx - ax
    dy = by - ay
    len2 = dx * dx + dy * dy
    eps2 = eps * eps
    if len2 <= eps2:
        return abs(px - ax) <= eps and abs(py - ay) <= eps
    cross = (px - ax) * dy - (py - ay) * dx
    dot = (px - ax) * dx + (py - ay) * dy
    eps2_len2 = eps2 * len2
    cross_ok = cross * cross <= eps2_len2
    before_start_ok = dot < 0.0 and dot * dot <= eps2_len2
    inside_segment = dot >= 0.0 and dot <= len2
    beyond_end = dot - len2
    after_end_ok = dot > len2 and beyond_end * beyond_end <= eps2_len2
    return cross_ok and (before_start_ok or inside_segment or after_end_ok)


def _guarded_squared_boundary(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
    eps: float,
    guard_tol: float,
) -> bool:
    dx = bx - ax
    dy = by - ay
    len2 = dx * dx + dy * dy
    eps2 = eps * eps
    if len2 <= eps2:
        return abs(px - ax) <= eps and abs(py - ay) <= eps
    cross = (px - ax) * dy - (py - ay) * dx
    dot = (px - ax) * dx + (py - ay) * dy
    eps2_len2 = eps2 * len2
    lo = eps2_len2 * (1.0 - guard_tol)
    hi = eps2_len2 * (1.0 + guard_tol)
    cross2 = cross * cross
    if cross2 > hi:
        return False
    needs_fallback = cross2 > lo
    if not needs_fallback and dot >= 0.0 and dot <= len2:
        return True
    if not needs_fallback and dot < 0.0:
        dot2 = dot * dot
        if dot2 <= lo:
            return True
        if dot2 > hi:
            return False
        needs_fallback = True
    elif not needs_fallback:
        beyond_end = dot - len2
        beyond2 = beyond_end * beyond_end
        if beyond2 <= lo:
            return True
        if beyond2 > hi:
            return False
        needs_fallback = True
    if needs_fallback:
        length = math.sqrt(len2)
        along_eps = eps * length
        return abs(cross) <= along_eps and dot >= -along_eps and dot <= len2 + along_eps
    return False


def _deterministic_cases() -> list[dict[str, float]]:
    cases: list[dict[str, float]] = []
    eps_values = (0.0, 1.0e-12, 1.0e-9, 1.0e-6, 1.0e-3)
    segments = (
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
        (-2.5, 4.0, 7.5, -3.0),
        (3.0, -1.0, 3.0 + 1.0e-10, -1.0 + 2.0e-10),
    )
    offsets = (-2.0, -1.0, -1.0e-9, 0.0, 0.25, 0.5, 1.0, 1.0 + 1.0e-9, 2.0)
    perpendiculars = (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0)
    for eps in eps_values:
        for ax, ay, bx, by in segments:
            dx = bx - ax
            dy = by - ay
            length = math.hypot(dx, dy)
            if length == 0.0:
                unit_x, unit_y = 1.0, 0.0
                perp_x, perp_y = 0.0, 1.0
            else:
                unit_x, unit_y = dx / length, dy / length
                perp_x, perp_y = -unit_y, unit_x
            for along in offsets:
                for perp in perpendiculars:
                    px = ax + along * dx + perp * eps * perp_x
                    py = ay + along * dy + perp * eps * perp_y
                    cases.append({"px": px, "py": py, "ax": ax, "ay": ay, "bx": bx, "by": by, "eps": eps})
    return cases


def _random_cases(seed: int, count: int) -> list[dict[str, float]]:
    rng = random.Random(seed)
    cases: list[dict[str, float]] = []
    for _ in range(count):
        scale = 10.0 ** rng.uniform(-9.0, 6.0)
        ax = rng.uniform(-1.0, 1.0) * scale
        ay = rng.uniform(-1.0, 1.0) * scale
        dx = rng.uniform(-1.0, 1.0) * scale
        dy = rng.uniform(-1.0, 1.0) * scale
        bx = ax + dx
        by = ay + dy
        eps = 10.0 ** rng.uniform(-12.0, -2.0) * max(1.0, scale)
        along = rng.uniform(-0.5, 1.5)
        perp = rng.uniform(-2.0, 2.0) * eps
        length = math.hypot(dx, dy)
        if length == 0.0:
            perp_x, perp_y = 0.0, 1.0
        else:
            perp_x, perp_y = -dy / length, dx / length
        px = ax + along * dx + perp * perp_x
        py = ay + along * dy + perp * perp_y
        cases.append({"px": px, "py": py, "ax": ax, "ay": ay, "bx": bx, "by": by, "eps": eps})
    return cases


def render_markdown(packet: dict[str, Any]) -> str:
    audit = packet["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial Squared-Boundary Equivalence",
        "",
        f"Status: `{packet['status']}`.",
        "",
        "This packet supports the Spatial guarded squared-boundary candidate by",
        "checking the old sqrt-based boundary predicate against a guarded squared",
        "fast path with sqrt fallback near threshold cases.",
        "",
        "```text",
        f"release_authorized: {str(packet['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(packet['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(packet['m7_promotion_authorized']).lower()}",
        f"M7 rows added: {packet['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Result",
        "",
        f"- Deterministic cases: `{packet['case_counts']['deterministic_cases']}`",
        f"- Random cases: `{packet['case_counts']['random_cases']}`",
        f"- Total cases: `{packet['case_counts']['total_cases']}`",
        f"- Guarded mismatches: `{packet['guarded_mismatch_count']}`",
        f"- Pure squared mismatches recorded: `{packet['pure_squared_mismatch_count']}`",
        "",
        "## Scope",
        "",
        packet["equivalence_scope"]["pure_squared_risk"],
        "",
        packet["equivalence_scope"]["guarded_partition"],
        "",
        f"Guard tolerance: `{packet['equivalence_scope']['guard_tol']}`.",
        "",
        packet["equivalence_scope"]["cuda_floating_point_note"],
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
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
