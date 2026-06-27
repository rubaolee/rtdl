#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
TOPOLOGY_CONTRACT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.json"
)
SAME_STREAM_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4354_rayjoin_original_vs_rtdl_pod"
    / "goal4354_rayjoin_original_vs_rtdl_same_stream_summary.json"
)
LARGE_PIP_DEFAULT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4374_rayjoin_exact_paper_suite_2026-06-13"
    / "pip_county_zipcode_rtdl_optix_fixed8_default_final_w5r60.json"
)
LARGE_PIP_DEVICE_RESIDENT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4374_rayjoin_exact_paper_suite_2026-06-13"
    / "pip_county_zipcode_rtdl_optix_device_resident_w5r60.json"
)


M3_PHASES = (
    "static_scene_prepare_sec",
    "query_stream_prepare_sec",
    "device_transfer_or_residency_sec",
    "rt_traversal_sec",
    "topology_continuation_sec",
    "host_return_or_scalar_materialization_sec",
)


def build_payload() -> dict[str, Any]:
    topology = _read_json(TOPOLOGY_CONTRACT)
    same_stream = _read_json(SAME_STREAM_SUMMARY)
    large_default = _read_json(LARGE_PIP_DEFAULT)
    large_device = _read_json(LARGE_PIP_DEVICE_RESIDENT)

    same_stream_pip_optix = same_stream["rtdl"]["pip"]["backends"]["optix"]
    same_stream_pip_embree = same_stream["rtdl"]["pip"]["backends"]["embree"]
    default_optix = large_default["results"]["optix"]
    device_optix = large_device["results"]["optix_device_resident"]

    default_native = _native_medians(default_optix["runs"])
    device_native = _native_medians(device_optix["runs"])
    default_wall = float(default_optix["hot_median_sec"])
    device_wall = float(device_optix["hot_median_sec"])
    default_transfer = default_native["point_upload_median_sec"] + default_native["row_download_median_sec"]
    device_transfer = device_native["point_upload_median_sec"] + device_native["row_download_median_sec"]
    default_residual = max(0.0, default_wall - default_native["traversal_median_sec"] - default_transfer)
    device_residual = max(0.0, device_wall - device_native["traversal_median_sec"] - device_transfer)

    counts_match = int(default_optix["count"]) == int(device_optix["count"])
    device_wall_speedup = _speedup(default_wall, device_wall)
    residual_reduction = _speedup(default_residual, device_residual)
    same_stream_optix_embree_speedup = _speedup(
        float(same_stream_pip_embree["hot_median_sec"]),
        float(same_stream_pip_optix["hot_median_sec"]),
    )
    same_stream_author_gap = next(
        row
        for row in same_stream["comparisons"]
        if row["workload"] == "pip" and row["backend"] == "optix"
    )
    rayjoin_author_over_rtdl = _speedup(
        float(same_stream_pip_optix["hot_median_sec"]),
        float(same_stream_author_gap["rayjoin_rt_query_ms"]) / 1000.0,
    )

    checks = {
        "topology_contract_not_m7": topology["status"]
        == "spatial_rayjoin_topology_stream_contract_candidate_not_m7",
        "same_stream_optix_beats_embree": same_stream_optix_embree_speedup > 1.0,
        "same_stream_author_remains_faster": rayjoin_author_over_rtdl > 1.0,
        "large_default_and_device_counts_match": counts_match,
        "large_device_resident_clears_material_speedup": device_wall_speedup >= 2.0,
        "device_transfer_is_effectively_removed": device_native["point_upload_median_sec"] == 0.0,
        "device_resident_residual_is_near_native": device_residual < 0.005,
        "all_public_claim_flags_false": True,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "spatial_rayjoin_m3_gap_analysis_not_m7"

    return {
        "tool": "v3_phoenix_spatial_rayjoin_m3_gap_analysis",
        "version": "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026_06_21",
        "status": status,
        "generic_capability": "point_location_topology_stream",
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
        "source_packets": {
            "topology_contract": _rel(TOPOLOGY_CONTRACT),
            "same_stream_author_comparison": _rel(SAME_STREAM_SUMMARY),
            "large_pip_default": _rel(LARGE_PIP_DEFAULT),
            "large_pip_device_resident": _rel(LARGE_PIP_DEVICE_RESIDENT),
        },
        "same_stream_pip_100k": {
            "contract": same_stream_pip_optix["output_contract"],
            "query_count": int(same_stream["rtdl"]["pip"]["query_count"]),
            "optix_hot_median_sec": float(same_stream_pip_optix["hot_median_sec"]),
            "embree_hot_median_sec": float(same_stream_pip_embree["hot_median_sec"]),
            "optix_over_embree_wall_speedup": same_stream_optix_embree_speedup,
            "rayjoin_author_query_sec": float(same_stream_author_gap["rayjoin_rt_query_ms"]) / 1000.0,
            "rayjoin_author_over_rtdl_optix_wall_speedup": rayjoin_author_over_rtdl,
            "exact_backend_counts_match": bool(
                same_stream["rtdl"]["pip"]["correctness"]["cross_backend_counts_match"]
            ),
            "reading": (
                "RTDL OptiX is much faster than RTDL Embree on this exact scalar-count "
                "same-stream contract, but RayJoin author RT is still faster than RTDL OptiX."
            ),
        },
        "large_pip_device_resident_delta": {
            "contract": large_default["program_contract"],
            "query_points": int(large_default["input_shape"]["query_points"]),
            "count": int(default_optix["count"]),
            "counts_match": counts_match,
            "default_host_points": {
                "wall_median_sec": default_wall,
                "rt_traversal_median_sec": default_native["traversal_median_sec"],
                "point_upload_median_sec": default_native["point_upload_median_sec"],
                "row_download_median_sec": default_native["row_download_median_sec"],
                "visible_residual_after_native_transfer_sec": default_residual,
            },
            "device_resident_points": {
                "wall_median_sec": device_wall,
                "rt_traversal_median_sec": device_native["traversal_median_sec"],
                "point_upload_median_sec": device_native["point_upload_median_sec"],
                "row_download_median_sec": device_native["row_download_median_sec"],
                "visible_residual_after_native_transfer_sec": device_residual,
            },
            "device_resident_wall_speedup_vs_default": device_wall_speedup,
            "visible_residual_reduction_vs_default": residual_reduction,
            "reading": (
                "The old large-PIP evidence shows the useful V3 direction: keep the "
                "query point stream resident inside RTDL's prepared route and the hot "
                "wall time moves close to native traversal. This is internal V3 "
                "topology-stream residency evidence, not a true zero-copy product claim."
            ),
        },
        "m3_public_row_gap": {
            "required_phases": M3_PHASES,
            "current_state": "partial_m3_gap_analysis_not_public_row",
            "available_now": [
                "same-contract RTDL OptiX/Embree wall timing",
                "same-stream RayJoin author timer basis",
                "native traversal and point-upload medians for large PIP route",
                "device-resident internal route delta",
            ],
            "missing_or_not_public_row_ready": [
                "single fresh runner that emits all M3 phases together",
                "static scene prepare for the large device-resident route in the same packet",
                "query-stream prepare separated from device transfer/residency",
                "topology continuation separated from RT traversal",
                "host scalar return separated from Python dispatch",
                "fresh external public-row review plus Codex consensus",
            ],
            "next_engine_target": (
                "Build or repair a reusable topology-stream prepared handle/runner that "
                "keeps query columns resident, emits the full M3 phase table, and proves "
                "the same contract against Embree and RayJoin author timing without "
                "RayJoin-specific native logic."
            ),
        },
        "forbidden_shortcuts": [
            "Do not call the device-resident internal delta true zero-copy.",
            "Do not claim RTDL beats RayJoin from the same-stream PIP evidence.",
            "Do not publish Spatial RayJoin M7 wording until a fresh full-M3 public row passes review.",
            "Do not implement a RayJoin-only native shortcut; the target is a reusable topology-stream prepared route.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Use old and current RayJoin evidence to define a V3 topology-stream M3 "
                "gap and optimization target, not to promote Spatial RayJoin."
            ),
            "was_i_foolish": (
                "No. This converts the confusing RayJoin evidence into a reusable V3 "
                "engine target and keeps every release/public flag false."
            ),
            "foolish_actions": (
                "The foolish action would be to quote either the 1.920x OptiX/Embree row "
                "or the 2x device-resident delta as a public Spatial RayJoin win while "
                "hiding the RayJoin-author gap and incomplete M3 table."
            ),
            "other_path": (
                "Keep rerunning author comparisons. That may produce more tables, but it "
                "does not itself reduce RTDL host/query staging or make V3 user-responsible."
            ),
            "different_path_now": (
                "Treat resident topology-stream columns and full phase accounting as the "
                "next generic V3 engine task."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    same = payload["same_stream_pip_100k"]
    large = payload["large_pip_device_resident_delta"]
    gap = payload["m3_public_row_gap"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial RayJoin M3 Gap Analysis",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This is an optimization-target packet, not a release row. It answers why",
        "Spatial RayJoin remains useful for V3: it exposes a reusable",
        "`point_location_topology_stream` host-staging and phase-accounting problem.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"rtdl_beats_rayjoin_claim_authorized: {str(payload['rtdl_beats_rayjoin_claim_authorized']).lower()}",
        f"true_zero_copy_claim_authorized: {str(payload['true_zero_copy_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Same-Stream PIP 100k",
        "",
        f"- Query count: `{same['query_count']}`",
        f"- RTDL OptiX / RTDL Embree wall speedup: `{same['optix_over_embree_wall_speedup']:.3f}x`",
        f"- RayJoin author / RTDL OptiX wall speedup: `{same['rayjoin_author_over_rtdl_optix_wall_speedup']:.3f}x`",
        f"- Backend exact counts match: `{str(same['exact_backend_counts_match']).lower()}`",
        "",
        same["reading"],
        "",
        "## Large PIP Device-Resident Delta",
        "",
        f"- Query points: `{large['query_points']}`",
        f"- Counts match: `{str(large['counts_match']).lower()}`",
        f"- Default host-points wall: `{large['default_host_points']['wall_median_sec']:.6f}s`",
        f"- Device-resident points wall: `{large['device_resident_points']['wall_median_sec']:.6f}s`",
        f"- Device-resident wall speedup vs default: `{large['device_resident_wall_speedup_vs_default']:.3f}x`",
        f"- Default visible residual after native transfer: `{large['default_host_points']['visible_residual_after_native_transfer_sec']:.6f}s`",
        f"- Device-resident visible residual after native transfer: `{large['device_resident_points']['visible_residual_after_native_transfer_sec']:.6f}s`",
        "",
        large["reading"],
        "",
        "## M3 Public-Row Gap",
        "",
        "Required phases:",
        "",
    ]
    lines.extend(f"- `{phase}`" for phase in gap["required_phases"])
    lines.extend(["", "Available now:", ""])
    lines.extend(f"- {item}" for item in gap["available_now"])
    lines.extend(["", "Missing or not public-row ready:", ""])
    lines.extend(f"- {item}" for item in gap["missing_or_not_public_row_ready"])
    lines.extend(
        [
            "",
            "Next engine target:",
            "",
            gap["next_engine_target"],
            "",
            "## Forbidden Shortcuts",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["forbidden_shortcuts"])
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on that idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit the Phoenix V3 RayJoin M3 gap analysis.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0 if payload["status"] == "spatial_rayjoin_m3_gap_analysis_not_m7" else 2


def _native_medians(runs: Iterable[dict[str, Any]]) -> dict[str, float]:
    measured = [row for row in runs if not row.get("is_warmup")]
    if not measured:
        raise ValueError("native median calculation needs measured non-warmup rows")
    return {
        "traversal_median_sec": _median_native(measured, "traversal"),
        "point_upload_median_sec": _median_native(measured, "point_upload"),
        "row_download_median_sec": _median_native(measured, "row_download"),
    }


def _median_native(rows: Iterable[dict[str, Any]], key: str) -> float:
    values = [float(row["native_timings"][key]) for row in rows]
    return float(statistics.median(values))


def _speedup(baseline_sec: float, candidate_sec: float) -> float:
    if baseline_sec <= 0.0 or candidate_sec <= 0.0:
        raise ValueError("speedup inputs must be positive")
    return float(baseline_sec) / float(candidate_sec)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
