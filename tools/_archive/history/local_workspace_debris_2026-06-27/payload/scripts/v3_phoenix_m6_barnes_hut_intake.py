#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


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


def _check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _median_seconds_ms(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value) * 1000.0, 3)


def _checksum_tolerance(values: list[float]) -> float:
    max_abs = max((abs(value) for value in values), default=0.0)
    return max(CHECKSUM_ABS_TOL, CHECKSUM_REL_TOL * max_abs)


def _checksum_delta(values: list[float]) -> float:
    if not values:
        return math.inf
    return max(values) - min(values)


def _claim_flags_false(payload: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(payload.get(key) is False for key in keys)


def _rows_by_body(payload: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    by_body: dict[int, list[dict[str, Any]]] = {}
    for row in payload.get("rows", []):
        by_body.setdefault(int(row["body_count"]), []).append(dict(row))
    return by_body


def _route(row: dict[str, Any]) -> str:
    return str(row.get("route_id"))


def _body_summary(body_count: int, rows: list[dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    by_route = {_route(row): row for row in rows}
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

    for route_id, row in by_route.items():
        _check(
            row.get("public_speedup_claim_authorized") is False,
            f"{body_count}/{route_id}: public speedup claim flag is not false",
            failures,
        )
        _check(
            row.get("rt_core_speedup_claim_authorized") is False,
            f"{body_count}/{route_id}: RT-core speedup claim flag is not false",
            failures,
        )
        _check(
            row.get("frontier_rows_materialized_on_host") is False,
            f"{body_count}/{route_id}: frontier rows materialized on host",
            failures,
        )
        _check(
            row.get("contribution_rows_materialized_on_host") is False,
            f"{body_count}/{route_id}: contribution rows materialized on host",
            failures,
        )
        if route_id.startswith("optix_"):
            _check(
                row.get("rt_core_accelerated_metadata") is True,
                f"{body_count}/{route_id}: OptiX route lacks RT metadata",
                failures,
            )
            _check(
                row.get("frontier_traversal_median_seconds") is not None,
                f"{body_count}/{route_id}: OptiX frontier traversal timing missing",
                failures,
            )
            _check(
                row.get("partner_wall_median_seconds") is not None,
                f"{body_count}/{route_id}: OptiX partner timing missing",
                failures,
            )
        else:
            _check(
                row.get("rt_core_accelerated_metadata") is False,
                f"{body_count}/{route_id}: fused partner route incorrectly marked RT-core",
                failures,
            )
    if "numba_cuda_fused" in by_route:
        _check(
            by_route["numba_cuda_fused"].get("hot_time_kind") == "cuda_event_kernel",
            f"{body_count}/numba_cuda_fused: expected CUDA event timing",
            failures,
        )

    fastest = min(rows, key=lambda row: float(row["hot_median_seconds"])) if rows else {}
    optix_numba = by_route.get("optix_numba_prepared_frontier", {})
    best_seconds = float(fastest.get("hot_median_seconds", math.nan)) if fastest else math.nan
    optix_numba_seconds = float(optix_numba.get("hot_median_seconds", math.nan)) if optix_numba else math.nan
    return {
        "body_count": body_count,
        "route_count": len(rows),
        "contribution_row_count": contribution_counts[0] if contribution_counts else None,
        "fastest_route_id": fastest.get("route_id"),
        "fastest_ms": _median_seconds_ms(best_seconds) if math.isfinite(best_seconds) else None,
        "optix_numba_ms": _median_seconds_ms(optix_numba_seconds) if math.isfinite(optix_numba_seconds) else None,
        "optix_numba_over_fastest": (
            optix_numba_seconds / best_seconds
            if math.isfinite(optix_numba_seconds) and math.isfinite(best_seconds) and best_seconds > 0.0
            else None
        ),
        "checksum_delta_x": delta_x,
        "checksum_delta_y": delta_y,
        "checksum_tolerance_x": tolerance_x,
        "checksum_tolerance_y": tolerance_y,
        "route_parity_passed": (
            not missing
            and not extra
            and len(set(contribution_counts)) == 1
            and delta_x <= tolerance_x
            and delta_y <= tolerance_y
        ),
    }


def build_payload(rerank_json: Path) -> dict[str, Any]:
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

    summaries = [
        _body_summary(body_count, rows, failures)
        for body_count, rows in sorted(_rows_by_body(source).items())
    ]
    _check(bool(summaries), "rerank artifact contains no rows", failures)
    serious_body_counts = [row["body_count"] for row in summaries if int(row["body_count"]) >= 32768]
    _check(bool(serious_body_counts), "no body count at or above 32768", failures)

    fastest_by_scale = {str(row["body_count"]): row["fastest_route_id"] for row in summaries}
    optix_fastest_scales = [
        int(row["body_count"])
        for row in summaries
        if str(row.get("fastest_route_id", "")).startswith("optix_")
    ]
    route_parity_passed = all(bool(row["route_parity_passed"]) for row in summaries)
    status = "pass" if not failures else "fail"
    if optix_fastest_scales:
        headline = (
            "M6 Barnes-Hut found prepared OptiX fastest on at least one scale; "
            "evidence remains internal until M7 review."
        )
    else:
        headline = (
            "M6 Barnes-Hut confirms the current fastest route is fused CPU/Numba "
            "or fused Numba CUDA, while prepared OptiX remains bounded device-column evidence."
        )

    return {
        "tool": "v3_phoenix_m6_barnes_hut_intake",
        "artifact": str(rerank_json),
        "status": status,
        "overall_status": "internal_m6_route_parity_evidence" if status == "pass" else "fail",
        "generic_capability": "aggregate_frontier_vector_accumulation",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "phoenix_m7_qualified_release_rows": 0,
        "timing_basis_mixed": True,
        "failures": failures,
        "headline": headline,
        "checks": {
            "serious_scale_present": bool(serious_body_counts),
            "route_parity_passed": route_parity_passed,
            "top_level_claim_flags_false": _claim_flags_false(source.get("claim_flags", {}), CLAIM_FLAG_KEYS),
            "all_body_counts_have_four_routes": all(int(row["route_count"]) == len(EXPECTED_ROUTES) for row in summaries),
        },
        "methodology": {
            "body_counts": source.get("body_counts"),
            "repeat": source.get("repeat"),
            "warmup": source.get("warmup"),
            "theta": source.get("theta"),
            "bucket_size": source.get("bucket_size"),
            "max_depth": source.get("max_depth"),
            "routes": EXPECTED_ROUTES,
            "timing_note": (
                "Fused Numba CUDA uses CUDA-event kernel timing when available; "
                "CPU/Numba and prepared OptiX routes use the runner's hot median. "
                "The route ratios therefore compare CUDA-event kernel time against "
                "wall-clock hot median; they are not kernel-to-kernel comparisons. "
                "Large rows are route-parity evidence, not full exact-force oracle rows."
            ),
        },
        "fastest_by_scale": fastest_by_scale,
        "optix_fastest_scales": optix_fastest_scales,
        "body_summaries": summaries,
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    rows = [
        "| Bodies | Fastest route | Fastest | OptiX+Numba | OptiX+Numba / fastest | Contribution rows | Checksum parity |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in payload["body_summaries"]:
        ratio = row["optix_numba_over_fastest"]
        rows.append(
            "| "
            f"{int(row['body_count']):,} | `{row['fastest_route_id']}` | "
            f"{row['fastest_ms']:.3f} ms | "
            f"{row['optix_numba_ms']:.3f} ms | "
            f"{ratio:.3f}x | "
            f"{int(row['contribution_row_count']):,} | "
            f"{'pass' if row['route_parity_passed'] else 'fail'} |"
        )
    lines = [
        "# Phoenix V3 M6 Barnes-Hut Intake",
        "",
        f"Status: {payload['overall_status']}",
        "",
        payload["headline"],
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "rt_core_speedup_claim_authorized: false",
        "Phoenix M7-qualified release rows: 0",
        "```",
        "",
        "## Route Matrix",
        "",
        *rows,
        "",
        "Ratios in this table use mixed timing bases: fused Numba CUDA uses CUDA-event",
        "kernel time when available, while CPU/Numba and prepared OptiX routes use",
        "the runner's wall-clock hot median. These ratios are internal route guidance,",
        "not kernel-to-kernel comparisons.",
        "",
        "## Methodology",
        "",
        f"- Repeat: {payload['methodology']['repeat']}",
        f"- Warmup: {payload['methodology']['warmup']}",
        f"- Theta: {payload['methodology']['theta']}",
        f"- Bucket size: {payload['methodology']['bucket_size']}",
        f"- Timing note: {payload['methodology']['timing_note']}",
        "",
        "## Failures",
        "",
    ]
    if payload["failures"]:
        lines.extend(f"- {failure}" for failure in payload["failures"])
    else:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phoenix V3 M6 Barnes-Hut rerank artifacts.")
    parser.add_argument("--rerank-json", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.rerank_json)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        write_markdown(args.md_out, payload)
    print(text)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
