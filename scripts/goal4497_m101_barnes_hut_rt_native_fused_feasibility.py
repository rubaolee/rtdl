from __future__ import annotations

import json
from pathlib import Path


PACKET_VERSION = "rtdl.v3_0.barnes_hut_rt_native_fused_feasibility.goal4497.v1"
OUT_JSON = Path("docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.jsonl")
OUT_REPORT = Path("docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.md")
M62_PACKET = Path("docs/reports/goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.json")
M87_PACKET = Path("docs/reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_packet_2026-06-16.json")
M87_RAW = Path("docs/reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_2026-06-16.json")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _round_ms(seconds: float | None) -> float | None:
    if seconds is None:
        return None
    return round(float(seconds) * 1000.0, 3)


def _m62_rows(packet: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for comparison in packet["comparisons"]:  # type: ignore[index]
        row = dict(comparison)
        rows.append(
            {
                "source_goal": "Goal4458",
                "body_count": int(row["body_count"]),
                "fastest_route_id": str(row["fastest_route_id"]),
                "cpu_numba_s": float(row["cpu_numba_seconds"]),
                "numba_cuda_s": float(row["numba_cuda_seconds"]),
                "optix_numba_s": float(row["optix_numba_seconds"]),
                "optix_cupy_s": float(row["optix_cupy_seconds"]),
                "optix_frontier_traversal_s": None,
                "optix_partner_numba_s": None,
                "rt_core_route_faster_than_best_current_route": False,
                "best_current_route_s": min(
                    float(row["cpu_numba_seconds"]),
                    float(row["numba_cuda_seconds"]),
                    float(row["optix_numba_seconds"]),
                    float(row["optix_cupy_seconds"]),
                ),
                "optix_numba_slower_than_best_current_route": _ratio(
                    float(row["optix_numba_seconds"]),
                    min(
                        float(row["cpu_numba_seconds"]),
                        float(row["numba_cuda_seconds"]),
                        float(row["optix_numba_seconds"]),
                        float(row["optix_cupy_seconds"]),
                    ),
                ),
            }
        )
    return rows


def _m87_rows(packet: dict[str, object], raw: dict[str, object]) -> list[dict[str, object]]:
    raw_rows = {
        (int(row["body_count"]), str(row["route_id"])): dict(row)
        for row in raw["rows"]  # type: ignore[index]
    }
    rows: list[dict[str, object]] = []
    for packet_row in packet["rows"]:  # type: ignore[index]
        row = dict(packet_row)
        body_count = int(row["body_count"])
        optix_numba = raw_rows[(body_count, "optix_numba_prepared_frontier")]
        best_current_route_s = min(
            float(row["cpu_numba_s"]),
            float(row["numba_cuda_s"]),
            float(row["optix_numba_s"]),
            float(row["optix_cupy_s"]),
        )
        rows.append(
            {
                "source_goal": "Goal4483",
                "body_count": body_count,
                "fastest_route_id": str(row["fastest_route_id"]),
                "contribution_rows": int(row["contribution_rows"]),
                "cpu_numba_s": float(row["cpu_numba_s"]),
                "numba_cuda_s": float(row["numba_cuda_s"]),
                "optix_numba_s": float(row["optix_numba_s"]),
                "optix_cupy_s": float(row["optix_cupy_s"]),
                "optix_frontier_traversal_s": float(optix_numba["frontier_traversal_median_seconds"]),
                "optix_partner_numba_s": float(optix_numba["partner_wall_median_seconds"]),
                "rt_core_route_faster_than_best_current_route": False,
                "best_current_route_s": best_current_route_s,
                "optix_numba_slower_than_best_current_route": _ratio(float(row["optix_numba_s"]), best_current_route_s),
            }
        )
    return rows


def _candidate_contract() -> dict[str, object]:
    return {
        "proposed_contract": "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
        "purpose": (
            "Fuse aggregate-tree traversal, opening-rule acceptance, exact leaf fallback, "
            "and weighted vector accumulation inside an RT-native/device execution path."
        ),
        "generic_inputs": (
            "source weighted point columns",
            "target weighted point columns",
            "DFS/resume-index aggregate tree columns",
            "leaf membership columns",
            "theta",
            "softening",
        ),
        "outputs": (
            "source_ids",
            "vector_x",
            "vector_y",
            "visited_counts",
            "aggregate_counts",
            "exact_counts",
        ),
        "must_avoid": (
            "aggregate-frontier row emission",
            "host frontier materialization",
            "host contribution materialization",
            "app-specific native engine callbacks",
            "automatic partner dispatch",
        ),
        "implementation_requirements": (
            "native RT program or equivalent payload accumulation",
            "device-resident output columns",
            "same force-summary contract as Goal4458 and Goal4483",
            "comparison against fused CPU/Numba and fused Numba CUDA partner routes",
        ),
        "why_numba_or_cupy_alone_is_insufficient": (
            "CuPy and Numba can implement the fused partner lane, but they do not drive "
            "RT cores. The current Numba CUDA fused route is therefore the best no-C++ "
            "GPU partner route, not RT-core acceleration evidence."
        ),
    }


def _write_report(packet: dict[str, object]) -> None:
    rows = packet["rows"]  # type: ignore[index]
    table_lines = [
        "| Bodies | Source | Fastest route | CPU/Numba | Numba CUDA | OptiX+Numba | OptiX+CuPy | OptiX slower than best |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:  # type: ignore[assignment]
        row = dict(row)
        table_lines.append(
            "| "
            f"{row['body_count']:,} | {row['source_goal']} | `{row['fastest_route_id']}` | "
            f"{_round_ms(float(row['cpu_numba_s'])):.3f}ms | "
            f"{_round_ms(float(row['numba_cuda_s'])):.3f}ms | "
            f"{_round_ms(float(row['optix_numba_s'])):.3f}ms | "
            f"{_round_ms(float(row['optix_cupy_s'])):.3f}ms | "
            f"{float(row['optix_numba_slower_than_best_current_route']):.2f}x |"
        )

    report = "\n".join(
        [
            "# Goal4497 / V3 M101 Barnes-Hut RT-Native Fused Feasibility",
            "",
            "## Conclusion",
            "",
            "Barnes-Hut should stay mixed explicit for current V3 guidance. The fastest measured route is scale-dependent: fused CPU/Numba wins the Goal4458 smaller rows, and fused Numba CUDA wins the Goal4483 larger rows. The RTDL/OptiX route is real RT-core aggregate-frontier device-column evidence, but it is not a Barnes-Hut RT-core speedup route because its hot contract still emits aggregate-frontier rows before vector accumulation.",
            "",
            "A competitive RT-core Barnes-Hut path requires a new app-agnostic native primitive, tentatively `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`, that fuses traversal, opening-rule acceptance, exact fallback, and weighted vector accumulation into device output columns. More tuning of the current frontier-row contract is not the right next optimization.",
            "",
            "## Evidence Matrix",
            "",
            *table_lines,
            "",
            "## Required Primitive Boundary",
            "",
            "- It must be generic aggregate-tree weighted-vector math, not Barnes-Hut app-specific native code.",
            "- It must output per-source vector/count columns directly and avoid aggregate-frontier row emission.",
            "- It must be compared against Goal4458 small-row fused CPU/Numba and Goal4483 large-row fused Numba CUDA under the same force-summary contract.",
            "- Until this primitive exists, no Barnes-Hut RT-core speedup, whole-app acceleration, public speedup, automatic partner selection, or app-specific native-engine claim is authorized.",
            "",
            "## Current Decision",
            "",
            str(packet["decision"]),
            "",
            "Artifacts:",
            "",
            f"- `{OUT_JSON.as_posix()}`",
            f"- `{OUT_JSONL.as_posix()}`",
        ]
    )
    OUT_REPORT.write_text(report + "\n", encoding="utf-8")


def build_packet() -> dict[str, object]:
    m62 = _load_json(M62_PACKET)
    m87 = _load_json(M87_PACKET)
    m87_raw = _load_json(M87_RAW)
    rows = _m62_rows(m62) + _m87_rows(m87, m87_raw)
    optix_losses = [float(row["optix_numba_slower_than_best_current_route"]) for row in rows]
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4497 / V3 M101",
        "status": "rt_native_fused_primitive_required_not_currently_implemented",
        "date": "2026-06-17",
        "source_artifacts": (
            M62_PACKET.as_posix(),
            M87_PACKET.as_posix(),
            M87_RAW.as_posix(),
        ),
        "summary": {
            "scale_rows": len(rows),
            "fastest_route_by_scale": {
                str(row["body_count"]): row["fastest_route_id"]
                for row in rows
            },
            "prepared_optix_numba_loses_all_rows": all(
                float(row["optix_numba_slower_than_best_current_route"]) > 1.0
                for row in rows
            ),
            "optix_numba_slower_than_best_range": {
                "min": min(optix_losses),
                "max": max(optix_losses),
            },
            "current_fastest_route_reading": "scale_dependent_fused_cpu_numba_or_fused_numba_cuda",
            "rt_core_route_reading": "valid_device_column_evidence_but_under_fused",
        },
        "candidate_contract": _candidate_contract(),
        "decision": (
            "Keep Barnes-Hut as mixed explicit current guidance. If RT-core acceleration "
            "for Barnes-Hut remains a V3 target, implement the proposed app-agnostic "
            "RT-native fused weighted-vector primitive and compare it against the current "
            "fused CPU/Numba and fused Numba CUDA force-summary routes. Do not spend more "
            "V3 effort optimizing the aggregate-frontier row-emission route as if it were "
            "the final RT-core Barnes-Hut shape."
        ),
        "claim_boundary": {
            "feasibility_gate_only": True,
            "route_changed": False,
            "rt_native_fused_primitive_implemented": False,
            "prepared_optix_remains_rt_core_device_column_evidence": True,
            "numba_cuda_fused_route_uses_rt_cores": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "rows": rows,
    }
    return packet


def main() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    OUT_JSONL.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in packet["rows"]) + "\n",
        encoding="utf-8",
    )
    _write_report(packet)
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    main()
