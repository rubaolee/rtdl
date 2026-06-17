from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.barnes_hut_clean_target_audit.goal4512.v1"
OUT_JSON = Path("docs/reports/goal4512_v3_0_m116_barnes_hut_clean_target_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4512_v3_0_m116_barnes_hut_clean_target_audit_2026-06-17.md")

RT_NATIVE_FEASIBILITY = Path(
    "docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.json"
)


def _load(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _route_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in packet["rows"]:
        rows.append(
            {
                "body_count": int(row["body_count"]),
                "source_goal": row["source_goal"],
                "fastest_route_id": row["fastest_route_id"],
                "best_current_route_s": float(row["best_current_route_s"]),
                "cpu_numba_s": float(row["cpu_numba_s"]),
                "numba_cuda_s": float(row["numba_cuda_s"]),
                "optix_numba_s": float(row["optix_numba_s"]),
                "optix_cupy_s": float(row["optix_cupy_s"]),
                "optix_numba_slower_than_best_current_route": float(
                    row["optix_numba_slower_than_best_current_route"]
                ),
                "rt_core_route_faster_than_best_current_route": bool(
                    row["rt_core_route_faster_than_best_current_route"]
                ),
                "optix_frontier_traversal_s": row.get("optix_frontier_traversal_s"),
                "optix_partner_numba_s": row.get("optix_partner_numba_s"),
                "contribution_rows": row.get("contribution_rows"),
            }
        )
    return rows


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    feasibility = _load(root, RT_NATIVE_FEASIBILITY)
    rows = _route_rows(feasibility)
    small_rows = [row for row in rows if row["source_goal"] == "Goal4458"]
    large_rows = [row for row in rows if row["source_goal"] == "Goal4483"]
    future_contract = feasibility["candidate_contract"]
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4512 / V3 M116",
        "app": "barnes_hut",
        "evidence_inputs": [str(RT_NATIVE_FEASIBILITY)]
        + list(feasibility.get("source_artifacts", ())),
        "current_route_policy": {
            "small_scale_route": "fused_frontier_force_sum_bucketized_cpu_numba",
            "large_scale_route": "fused_frontier_force_sum_bucketized_numba_cuda",
            "rt_evidence_route": "prepared_aggregate_frontier_weighted_vector_optix --partner numba",
            "rows": rows,
            "fastest_route_by_scale": feasibility["summary"]["fastest_route_by_scale"],
            "prepared_optix_numba_loses_all_rows": bool(
                feasibility["summary"]["prepared_optix_numba_loses_all_rows"]
            ),
            "optix_numba_slower_than_best_range": feasibility["summary"][
                "optix_numba_slower_than_best_range"
            ],
            "small_scale_fastest_all_cpu_numba": all(
                row["fastest_route_id"] == "cpu_numba_fused" for row in small_rows
            ),
            "large_scale_fastest_all_numba_cuda": all(
                row["fastest_route_id"] == "numba_cuda_fused" for row in large_rows
            ),
        },
        "future_rt_native_fused_primitive": {
            "required": True,
            "implemented": bool(
                feasibility["claim_boundary"]["rt_native_fused_primitive_implemented"]
            ),
            "proposed_contract": future_contract["proposed_contract"],
            "purpose": future_contract["purpose"],
            "must_avoid": future_contract["must_avoid"],
            "implementation_requirements": future_contract["implementation_requirements"],
            "why_numba_cuda_is_not_rt_core": future_contract[
                "why_numba_or_cupy_alone_is_insufficient"
            ],
        },
        "m113_applicability": {
            "current_route_should_use_m113": False,
            "reason": (
                "Barnes-Hut does not need a prepared graph chunk executor for the "
                "current bottleneck. It needs a fused weighted-vector RT-native "
                "primitive that combines traversal, opening acceptance, exact "
                "fallback, and vector accumulation without aggregate-frontier row "
                "emission."
            ),
        },
        "readiness": {
            "internal_v3_clean_target_closed": True,
            "rt_core_acceleration_closed": False,
            "current_route_evidence_bounded": True,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
            "pod_needed_next_only_if_rt_native_fused_primitive_is_pursued": True,
        },
        "remaining_debt": [
            {
                "item": "RT-core Barnes-Hut acceleration",
                "status": "requires_new_generic_primitive",
                "reason": future_contract["proposed_contract"],
            },
            {
                "item": "aggregate-frontier row-emission route",
                "status": "not_final_rt_core_shape",
                "reason": "Prepared OptiX+Numba loses all measured rows to fused CPU/Numba or fused Numba CUDA.",
            },
            {
                "item": "automatic route/partner selection",
                "status": "blocked_by_policy",
                "reason": "Scale-dependent routes remain explicit user choices.",
            },
        ],
        "conclusion": (
            "Barnes-Hut is closed as a current V3 route-policy target, not as an "
            "RT-core acceleration success. Use fused CPU/Numba for the tested "
            "8192/16384/32768 rows, fused Numba CUDA for the tested 65536/131072 "
            "rows, and prepared RTDL/OptiX+Numba only as RT-core aggregate-frontier "
            "device-column evidence. A real Barnes-Hut RT-core win requires the "
            "future app-agnostic RT-native fused weighted-vector primitive from "
            "Goal4497."
        ),
    }


def _fmt_sec(value: float) -> str:
    return f"{value:.6f}s"


def _fmt_x(value: float) -> str:
    return f"{value:.2f}x"


def write_report(packet: dict[str, Any], path: Path) -> None:
    policy = packet["current_route_policy"]
    lines = [
        "# Goal4512 / V3 M116 Barnes-Hut Clean-Target Audit",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Current Route Matrix",
        "",
        "| Bodies | Source | Fastest route | Best time | OptiX+Numba time | OptiX+Numba slower than best |",
        "| ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for row in policy["rows"]:
        lines.append(
            "| "
            f"{row['body_count']:,} | "
            f"{row['source_goal']} | "
            f"`{row['fastest_route_id']}` | "
            f"{_fmt_sec(row['best_current_route_s'])} | "
            f"{_fmt_sec(row['optix_numba_s'])} | "
            f"{_fmt_x(row['optix_numba_slower_than_best_current_route'])} |"
        )

    future = packet["future_rt_native_fused_primitive"]
    lines.extend(
        [
            "",
            "## Route Policy",
            "",
            f"- Small tested rows: `{policy['small_scale_route']}`.",
            f"- Large tested rows: `{policy['large_scale_route']}`.",
            f"- RT evidence row: `{policy['rt_evidence_route']}`.",
            "- Prepared RTDL/OptiX+Numba loses all measured rows to the current fused route.",
            "- Fused Numba CUDA is no-C++ Python-source GPU partner evidence; it is not RT-core evidence.",
            "",
            "## Future RT-Native Primitive",
            "",
            f"- Required contract: `{future['proposed_contract']}`.",
            f"- Implemented now: `{future['implemented']}`.",
            f"- Purpose: {future['purpose']}",
            "- Must avoid: aggregate-frontier row emission, host frontier materialization, host contribution materialization, app-specific native callbacks, and automatic partner dispatch.",
            "",
            "## M113 Applicability",
            "",
            f"- Current route should use M113: `{packet['m113_applicability']['current_route_should_use_m113']}`.",
            f"- Reason: {packet['m113_applicability']['reason']}",
            "",
            "## Closed",
            "",
            "- Scale-dependent current route guidance is explicit and evidence-bounded.",
            "- Prepared RTDL/OptiX+Numba is correctly scoped as RT-core device-column evidence.",
            "- More aggregate-frontier row-emission tuning is not the final RT-core Barnes-Hut path.",
            "",
            "## Still Blocked",
            "",
            "- Public Barnes-Hut RT-core speedup wording.",
            "- Whole-application speedup wording.",
            "- Automatic route or partner selection.",
            "- Claiming V3 already has the future RT-native fused weighted-vector primitive.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["readiness"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
