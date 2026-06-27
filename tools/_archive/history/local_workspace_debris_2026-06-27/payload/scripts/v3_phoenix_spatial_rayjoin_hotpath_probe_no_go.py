#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT / "docs/rebuild/v3/evidence/phoenix_v3_spatial_hotpath_probe_20260621"
)
AUTHOR_BASIS_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
)
OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.md"

STATUS = "spatial_rayjoin_hotpath_probe_no_go_author_gap_not_closed"
EXPECTED_EXACT_COUNT = 47262


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 Spatial RayJoin hotpath no-go packet from POD sweep evidence."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_payload() -> dict[str, Any]:
    route_rows = _load_route_rows()
    author_basis = _load_json(AUTHOR_BASIS_JSON)
    best_legal = _best_legal_route(route_rows)
    device_filtered_failure = _parse_device_filtered_failure()

    author_query_ms = float(author_basis["author_run"]["query_ms"])
    best_query_ms = best_legal["prepared_query_ms"] if best_legal else None
    author_speedup_vs_best = None
    if best_query_ms is not None and author_query_ms > 0.0:
        author_speedup_vs_best = best_query_ms / author_query_ms

    checks = {
        "evidence_dir_exists": EVIDENCE_DIR.exists(),
        "route_rows_present": len(route_rows) >= 5,
        "author_basis_exists": AUTHOR_BASIS_JSON.exists(),
        "author_query_ms_expected": abs(author_query_ms - 1.86566) < 0.00001,
        "all_legal_routes_keep_claim_flags_false": all(
            row["release_authorized"] is False
            and row["m7_promotion_authorized"] is False
            and row["public_speedup_claim_authorized"] is False
            and row["rtdl_beats_rayjoin_claim_authorized"] is False
            for row in route_rows
        ),
        "legal_routes_preserve_exact_count": all(
            row["row_count"] == EXPECTED_EXACT_COUNT and row["row_count_consistent"] is True
            for row in route_rows
        ),
        "best_legal_route_is_relation_status_y_then_x": (
            best_legal is not None
            and best_legal["count_mode"] == "relation_status_corrected_executor_validated"
            and best_legal["point_order_mode"] == "y_then_x"
        ),
        "best_legal_route_still_slower_than_author_query": (
            author_speedup_vs_best is not None and author_speedup_vs_best > 2.8
        ),
        "exact_prepared_executor_remains_slower_than_relation_status": any(
            row["count_mode"] == "exact_prepared_points_executor"
            and row["prepared_query_ms"] > 20.0
            for row in route_rows
        ),
        "device_filtered_failure_recorded": (
            device_filtered_failure.get("observed_count") == 47570
            and device_filtered_failure.get("exact_count") == EXPECTED_EXACT_COUNT
        ),
        "device_filtered_excluded_from_legal_routes": all(
            row["count_mode"] != "device_filtered_prepared_points_validated"
            for row in route_rows
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]

    status = "fail" if failed_checks else STATUS
    return {
        "tool": "v3_phoenix_spatial_rayjoin_hotpath_probe_no_go",
        "status": status,
        "generic_capability": "point_location_topology_stream",
        "dataset": "data/rayjoin_public_cdb/br_county.cdb",
        "pod": {
            "host": "213.173.108.14:11592",
            "remote_repo": "/root/rtdl_v3_rebuild_20260620/current",
            "gpu": "NVIDIA RTX 4000 Ada Generation, 550.127.05",
        },
        "protocol": {
            "query_repeat": 50,
            "warmup": 5,
            "sample_repeat": 2,
            "expected_exact_count": EXPECTED_EXACT_COUNT,
            "same_dataset_author_query_ms": author_query_ms,
            "author_result_count_printed": author_basis.get("author_result_count_printed"),
            "author_result_count_parity_verified": author_basis.get(
                "author_result_count_parity_verified"
            ),
        },
        "route_rows": route_rows,
        "best_legal_route": best_legal,
        "same_dataset_author_gap": {
            "author_basis": _rel(AUTHOR_BASIS_JSON),
            "author_query_ms": author_query_ms,
            "best_legal_rtdl_query_ms": best_query_ms,
            "rayjoin_author_speedup_vs_best_legal_rtdl_hotpath": author_speedup_vs_best,
            "interpretation": (
                "The best exact RTDL hotpath remains slower than the same-dataset RayJoin author "
                "Query timer, so the Spatial topology-stream gap is not closed."
            ),
        },
        "device_filtered_rejected_route": device_filtered_failure,
        "hotpath_interpretation": (
            "The legal relation-status route is exact and device-resident, but the measured hot query "
            "time is dominated by the native OptiX candidate-count traversal. The failing device-filtered "
            "route is excluded because it over-counts the public county workload."
        ),
        "required_before_m7": [
            "A same-contract route with exact stable row count 47262 that is not slower than the RayJoin author Query basis.",
            "Author result-count parity or public wording that explicitly refuses count-equivalence claims.",
            "External AI review and Codex consensus after any new promotable evidence.",
            "Public wording review that keeps paper reproduction and RTDL-beats-RayJoin claims false unless the same-dataset basis supports them.",
        ],
        "release_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Keep Spatial RayJoin point-location topology stream as no-go for Phoenix V3 after "
                "fresh same-POD hotpath sweep."
            ),
            "was_i_foolish": (
                "No. I used the verified POD, same dataset, exact count authority, and did not "
                "promote a route that failed the author-speed or exactness bar."
            ),
            "foolish_actions": (
                "The foolish actions would be to call a 5.4 ms route a success against a 1.86566 ms "
                "author timer, or to hide the device-filtered 47570 != 47262 mismatch."
            ),
            "other_path": (
                "I could have jumped to a new app family immediately, but this remaining release-breadth "
                "gap had a concrete reopen bar and needed one bounded re-test."
            ),
            "different_path_now": (
                "Stop spending V3 release confidence on this Spatial route unless a real generic traversal "
                "optimization is designed; move to the next engine target or record this as future research."
            ),
        },
    }


def _load_route_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(EVIDENCE_DIR.glob("*.json")):
        payload = _load_json(path)
        summary = payload.get("summary", {})
        phases = summary.get("m3_phase_sec_medians", {}) or {}
        if payload.get("failed_checks"):
            continue
        prepared_query_sec = summary.get("prepared_query_sec_median")
        row = {
            "source": _rel(path),
            "status": payload.get("status"),
            "count_mode": payload.get("count_mode"),
            "point_order_mode": payload.get("point_order_mode"),
            "row_count": summary.get("row_count"),
            "row_count_consistent": summary.get("row_count_consistent"),
            "prepared_query_ms": None
            if prepared_query_sec is None
            else round(float(prepared_query_sec) * 1000.0, 6),
            "rt_traversal_ms": None
            if phases.get("rt_traversal_sec") is None
            else round(float(phases["rt_traversal_sec"]) * 1000.0, 6),
            "runner_wall_ms": None
            if summary.get("runner_wall_sec_median") is None
            else round(float(summary["runner_wall_sec_median"]) * 1000.0, 6),
            "release_authorized": payload.get("release_authorized"),
            "m7_promotion_authorized": payload.get("m7_promotion_authorized"),
            "public_speedup_claim_authorized": payload.get("public_speedup_claim_authorized"),
            "rtdl_beats_rayjoin_claim_authorized": payload.get("rtdl_beats_rayjoin_claim_authorized"),
        }
        if row["prepared_query_ms"] is not None:
            rows.append(row)
    return rows


def _best_legal_route(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    legal_rows = [
        row
        for row in rows
        if row["row_count"] == EXPECTED_EXACT_COUNT
        and row["row_count_consistent"] is True
        and row["prepared_query_ms"] is not None
    ]
    if not legal_rows:
        return None
    return min(legal_rows, key=lambda row: float(row["prepared_query_ms"]))


def _parse_device_filtered_failure() -> dict[str, Any]:
    log_path = EVIDENCE_DIR / "device_filtered_prepared_points_validated_y_then_x_sample2.log"
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    match = re.search(
        r"did not match exact prepared count:\s*(\d+)\s*!=\s*(\d+)",
        re.sub(r"\x1b\[[0-9;]*m", "", text),
    )
    observed = int(match.group(1)) if match else None
    exact = int(match.group(2)) if match else None
    return {
        "source": _rel(log_path),
        "count_mode": "device_filtered_prepared_points_validated",
        "point_order_mode": "y_then_x",
        "failure_class": "validated_candidate_exactness_mismatch",
        "observed_count": observed,
        "exact_count": exact,
        "candidate_minus_exact": None if observed is None or exact is None else observed - exact,
        "excluded_from_m7": True,
        "interpretation": (
            "This route is not legal V3 evidence because the validated device-side count "
            "does not equal the exact prepared count."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    gap = payload["same_dataset_author_gap"]
    best = payload["best_legal_route"] or {}
    rejected = payload["device_filtered_rejected_route"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial RayJoin Hotpath Probe No-Go",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet records a fresh same-POD hotpath sweep for the Spatial RayJoin "
        "point-location topology-stream gap. It does not promote M7 and does not "
        "authorize any public speedup claim.",
        "",
        "## Protocol",
        "",
        f"- Dataset: `{payload['dataset']}`",
        f"- GPU: `{payload['pod']['gpu']}`",
        f"- Query repeat: `{payload['protocol']['query_repeat']}`",
        f"- Warmup: `{payload['protocol']['warmup']}`",
        f"- Sample repeat: `{payload['protocol']['sample_repeat']}`",
        f"- Exact authority count: `{payload['protocol']['expected_exact_count']}`",
        f"- Same-dataset RayJoin author Query timer: `{payload['protocol']['same_dataset_author_query_ms']:.6f} ms`",
        "",
        "## Legal Route Sweep",
        "",
        "| Route | Point order | Count | Hot query ms | RT traversal ms | M7 |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["route_rows"]:
        lines.append(
            "| {count_mode} | {point_order_mode} | {row_count} | {query:.6f} | {rt:.6f} | no |".format(
                count_mode=row["count_mode"],
                point_order_mode=row["point_order_mode"],
                row_count=row["row_count"],
                query=float(row["prepared_query_ms"]),
                rt=float(row["rt_traversal_ms"]),
            )
        )
    lines.extend(
        [
            "",
            "## Best Legal Route",
            "",
            f"- Route: `{best.get('count_mode')}`",
            f"- Point order: `{best.get('point_order_mode')}`",
            f"- Hot query: `{float(best.get('prepared_query_ms', 0.0)):.6f} ms`",
            f"- Same-dataset author Query: `{gap['author_query_ms']:.6f} ms`",
            "- RayJoin author speedup vs best legal RTDL hotpath: "
            f"`{float(gap['rayjoin_author_speedup_vs_best_legal_rtdl_hotpath']):.3f}x`",
            "",
            "Interpretation: the best exact RTDL route is still slower than the same-dataset "
            "RayJoin author Query timer, so the Spatial gap remains open.",
            "",
            "## Rejected Route",
            "",
            f"- Route: `{rejected['count_mode']}`",
            f"- Failure: `{rejected['failure_class']}`",
            f"- Observed count: `{rejected['observed_count']}`",
            f"- Exact count: `{rejected['exact_count']}`",
            f"- Delta: `{rejected['candidate_minus_exact']}`",
            "",
            rejected["interpretation"],
            "",
            "## Claim Boundary",
            "",
            f"- `release_authorized: {str(payload['release_authorized']).lower()}`",
            f"- `m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}`",
            f"- `m7_qualified_release_rows_added: {payload['m7_qualified_release_rows_added']}`",
            f"- `rtdl_beats_rayjoin_claim_authorized: {str(payload['rtdl_beats_rayjoin_claim_authorized']).lower()}`",
            f"- `paper_reproduction_claim_authorized: {str(payload['paper_reproduction_claim_authorized']).lower()}`",
            "",
            "## Required Before M7",
            "",
        ]
    )
    for item in payload["required_before_m7"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on one idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
