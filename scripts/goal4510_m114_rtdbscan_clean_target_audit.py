from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.rtdbscan_clean_target_audit.goal4510.v1"
OUT_JSON = Path("docs/reports/goal4510_v3_0_m114_rtdbscan_clean_target_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4510_v3_0_m114_rtdbscan_clean_target_audit_2026-06-17.md")

COMPACT_EVIDENCE = (
    Path("docs/reports/goal4484_v3_0_m88_rtdbscan_compact_signature_matrix_2026-06-16.json"),
    Path("docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.json"),
)
POINT_COLUMN_ROAD_EVIDENCE = Path(
    "docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.json"
)
POINT_COLUMN_PROFILE_EVIDENCE = Path(
    "docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.json"
)

TARGET_POINT_COUNTS = (524_288, 1_048_576)
TARGET_DATASETS = ("clustered3d", "road3d", "ngsim_dense")
TARGET_PROTOCOLS = ("one_shot_no_warmup", "warmed_replay")
TARGET_MODES = ("grouped_numba", "grouped_cupy", "predicate_direct_status")


def _load(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _signature_key(row: dict[str, Any]) -> str:
    return json.dumps(row["signature"], sort_keys=True, separators=(",", ":"))


def _protocol_metric(protocol: str) -> str:
    if protocol == "one_shot_no_warmup":
        return "prepare_plus_replay_sec"
    if protocol == "warmed_replay":
        return "elapsed_sec"
    raise ValueError(f"Unsupported RT-DBSCAN audit protocol: {protocol}")


def _compact_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for evidence_path in COMPACT_EVIDENCE:
        packet = _load(root, evidence_path)
        for row in packet["rows"]:
            case = row["case"]
            if case.get("point_count") not in TARGET_POINT_COUNTS:
                continue
            if case.get("dataset") not in TARGET_DATASETS:
                continue
            if case.get("protocol") not in TARGET_PROTOCOLS:
                continue
            if case.get("mode_key") not in TARGET_MODES:
                continue
            rows.append(row)
    return rows


def _build_compact_matrix(root: Path) -> list[dict[str, Any]]:
    rows = _compact_rows(root)
    matrix: list[dict[str, Any]] = []
    for point_count in TARGET_POINT_COUNTS:
        for dataset in TARGET_DATASETS:
            for protocol in TARGET_PROTOCOLS:
                group = [
                    row
                    for row in rows
                    if row["case"]["point_count"] == point_count
                    and row["case"]["dataset"] == dataset
                    and row["case"]["protocol"] == protocol
                ]
                by_mode = {row["case"]["mode_key"]: row for row in group}
                missing = sorted(set(TARGET_MODES) - set(by_mode))
                if missing:
                    raise RuntimeError(
                        f"Missing RT-DBSCAN rows for {point_count}/{dataset}/{protocol}: {missing}"
                    )
                metric = _protocol_metric(protocol)
                seconds_by_mode = {
                    mode: float(by_mode[mode][metric]) for mode in TARGET_MODES
                }
                winner_mode = min(seconds_by_mode, key=seconds_by_mode.__getitem__)
                signatures_same = len({_signature_key(row) for row in by_mode.values()}) == 1
                predicate_sec = seconds_by_mode["predicate_direct_status"]
                matrix.append(
                    {
                        "point_count": point_count,
                        "dataset": dataset,
                        "protocol": protocol,
                        "metric": metric,
                        "winner_mode": winner_mode,
                        "winner_sec": seconds_by_mode[winner_mode],
                        "grouped_numba_sec": seconds_by_mode["grouped_numba"],
                        "grouped_cupy_sec": seconds_by_mode["grouped_cupy"],
                        "predicate_direct_status_sec": predicate_sec,
                        "predicate_speedup_vs_grouped_numba": seconds_by_mode[
                            "grouped_numba"
                        ]
                        / predicate_sec,
                        "predicate_speedup_vs_grouped_cupy": seconds_by_mode[
                            "grouped_cupy"
                        ]
                        / predicate_sec,
                        "same_contract_signatures": signatures_same,
                    }
                )
    return matrix


def _build_two_m_boundary(root: Path) -> dict[str, Any]:
    road = _load(root, POINT_COLUMN_ROAD_EVIDENCE)
    profiles = _load(root, POINT_COLUMN_PROFILE_EVIDENCE)
    profile_rows = {row["dataset"]: row for row in profiles["rows"]}
    road_summary = road["summary"]
    road_comparisons = {row["protocol"]: row for row in road["comparisons"]}
    return {
        "point_count": 2_097_152,
        "road3d": {
            "primitive_prepare_speedup_if_columns_already_owned": float(
                road_summary["primitive_prepare_speedup_if_columns_already_owned"]
            ),
            "primitive_prepare_phase_speedup_if_columns_already_owned": float(
                road_summary["primitive_prepare_phase_speedup_if_columns_already_owned"]
            ),
            "one_shot_app_total_speedup_vs_charged_columns": float(
                road_comparisons["one_shot"][
                    "prepare_plus_replay_speedup_vs_charged_columns"
                ]
            ),
            "warm_replay_app_total_speedup_vs_charged_columns": float(
                road_comparisons["warm_replay"][
                    "prepare_plus_replay_speedup_vs_charged_columns"
                ]
            ),
            "decision": road_comparisons["one_shot"]["decision"],
            "scope": "full count-threshold app route for road3d only",
        },
        "clustered3d": {
            "prepare_speedup_if_columns_already_owned": float(
                profile_rows["clustered3d"]["prepare_speedup_if_columns_already_owned"]
            ),
            "prepare_phase_speedup_if_columns_already_owned": float(
                profile_rows["clustered3d"][
                    "prepare_phase_speedup_if_columns_already_owned"
                ]
            ),
            "point_column_build_sec": float(profile_rows["clustered3d"]["point_column_build_sec"]),
            "column_prepare_sec": float(profile_rows["clustered3d"]["column_prepare_sec"]),
            "scope": "isolated direct-status prepare profile, not full app route",
        },
        "ngsim_dense": {
            "prepare_speedup_if_columns_already_owned": float(
                profile_rows["ngsim_dense"]["prepare_speedup_if_columns_already_owned"]
            ),
            "prepare_phase_speedup_if_columns_already_owned": float(
                profile_rows["ngsim_dense"][
                    "prepare_phase_speedup_if_columns_already_owned"
                ]
            ),
            "point_column_build_sec": float(profile_rows["ngsim_dense"]["point_column_build_sec"]),
            "column_prepare_sec": float(profile_rows["ngsim_dense"]["column_prepare_sec"]),
            "scope": "isolated direct-status prepare profile, not full app route",
        },
        "claim_boundary": {
            "caller_owned_column_speedup_requires_existing_device_columns": True,
            "app_constructed_column_build_must_be_charged": True,
            "true_zero_copy_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "route_promotion_authorized_from_2m_prepare_profiles": False,
        },
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    compact_matrix = _build_compact_matrix(root)
    two_m_boundary = _build_two_m_boundary(root)
    predicate_wins_all_targets = all(
        row["winner_mode"] == "predicate_direct_status" for row in compact_matrix
    )
    same_contract_all_targets = all(row["same_contract_signatures"] for row in compact_matrix)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4510 / V3 M114",
        "app": "rt_dbscan",
        "evidence_inputs": [str(path) for path in COMPACT_EVIDENCE]
        + [str(POINT_COLUMN_ROAD_EVIDENCE), str(POINT_COLUMN_PROFILE_EVIDENCE)],
        "compact_signature_matrix": compact_matrix,
        "compact_signature_summary": {
            "target_row_count": len(compact_matrix),
            "predicate_direct_status_wins_all_targets": predicate_wins_all_targets,
            "same_contract_signatures_all_targets": same_contract_all_targets,
            "current_best_route": (
                "OptiX fixed-radius count-threshold status producer plus explicit "
                "CuPy predicate direct-status compact component-signature continuation"
            ),
            "numba_role": (
                "same-contract grouped-stream fallback/reference and no-C++ Python-source "
                "partner path, not the fastest measured compact-signature route"
            ),
            "full_rows_role": "explicit slower output contract when per-point Python cluster rows are required",
        },
        "two_m_point_column_boundary": two_m_boundary,
        "m113_applicability": {
            "current_route_should_use_m113": False,
            "reason": (
                "The current winning RT-DBSCAN compact-signature route is not a "
                "prepared graph chunk plus same-stream partner-reduction route. It "
                "is a prepared self-query count-threshold status producer followed "
                "by a direct-status CuPy component-signature continuation."
            ),
            "m113_future_use": (
                "Use plan_v3_prepared_graph_chunk_executor only if a future "
                "RT-DBSCAN contract genuinely needs bounded prepared chunks, "
                "per-chunk handles, and explicit partner continuation before host "
                "materialization."
            ),
            "forcing_m113_now_would_be": "route confusion, not optimization",
        },
        "readiness": {
            "internal_v3_clean_target_closed": True,
            "current_route_evidence_bounded": True,
            "paper_reproduction_claim_authorized": False,
            "public_broad_dbscan_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "automatic_output_contract_selection_authorized": False,
            "non_road3d_2m_full_app_total_complete": False,
        },
        "remaining_debt": [
            {
                "item": "exact RT-DBSCAN paper reproduction",
                "status": "blocked_for_public_claim",
                "reason": "paper-code/dataset reproduction remains outside the checked-in evidence packet",
            },
            {
                "item": "non-road3d 2M full app-total point-column route",
                "status": "optional",
                "reason": (
                    "Goal4496 already proves isolated caller-owned coordinate handoff. "
                    "Run full app totals only if they can change the route decision."
                ),
            },
            {
                "item": "automatic partner/output selection",
                "status": "blocked_by_policy",
                "reason": "V3 keeps explicit app-visible route and output-contract choices",
            },
        ],
        "conclusion": (
            "RT-DBSCAN is closed as an internal V3 clean target under an evidence-bounded "
            "compact-signature contract: predicate direct-status plus CuPy wins all "
            "524k/1M same-contract rows, Numba remains the reference/no-C++ fallback, "
            "and 2M point-column reuse is useful only when the caller already owns "
            "device coordinate columns. M113 is reusable infrastructure, but it is "
            "not the current RT-DBSCAN performance path."
        ),
    }


def _fmt_sec(value: float) -> str:
    return f"{value:.3f}s"


def _fmt_x(value: float) -> str:
    return f"{value:.2f}x"


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4510 / V3 M114 RT-DBSCAN Clean-Target Audit",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Compact-Signature Winner Matrix",
        "",
        "| Points | Dataset | Protocol | Metric | Winner | Predicate direct-status | Speedup vs grouped Numba | Speedup vs grouped CuPy |",
        "| ---: | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in packet["compact_signature_matrix"]:
        lines.append(
            "| "
            f"{row['point_count']:,} | "
            f"{row['dataset']} | "
            f"{row['protocol']} | "
            f"`{row['metric']}` | "
            f"`{row['winner_mode']}` | "
            f"{_fmt_sec(row['predicate_direct_status_sec'])} | "
            f"{_fmt_x(row['predicate_speedup_vs_grouped_numba'])} | "
            f"{_fmt_x(row['predicate_speedup_vs_grouped_cupy'])} |"
        )

    boundary = packet["two_m_point_column_boundary"]
    lines.extend(
        [
            "",
            "## 2M Point-Column Boundary",
            "",
            "| Dataset | Scope | Caller-owned-column speedup | Charged app-total result | Decision |",
            "| --- | --- | ---: | --- | --- |",
            (
                "| road3d | full count-threshold app route | "
                f"{_fmt_x(boundary['road3d']['primitive_prepare_speedup_if_columns_already_owned'])} prepare | "
                f"one-shot {_fmt_x(boundary['road3d']['one_shot_app_total_speedup_vs_charged_columns'])}, "
                f"warm {_fmt_x(boundary['road3d']['warm_replay_app_total_speedup_vs_charged_columns'])} | "
                "`reuse_columns_only` |"
            ),
            (
                "| clustered3d | isolated direct-status prepare only | "
                f"{_fmt_x(boundary['clustered3d']['prepare_speedup_if_columns_already_owned'])} prepare | "
                "not full app-total evidence | `reuse only if caller owns columns` |"
            ),
            (
                "| ngsim_dense | isolated direct-status prepare only | "
                f"{_fmt_x(boundary['ngsim_dense']['prepare_speedup_if_columns_already_owned'])} prepare | "
                "not full app-total evidence | `reuse only if caller owns columns` |"
            ),
            "",
            "The point-column optimization is real but narrow: it removes redundant coordinate extraction/upload when the caller already owns device `x/y/z` columns. If the app constructs temporary columns solely for this route, that construction cost is charged and the app-total result is effectively flat on the measured 2M `road3d` row.",
            "",
            "## M113 Applicability",
            "",
            f"- Current route should use M113: `{packet['m113_applicability']['current_route_should_use_m113']}`.",
            f"- Reason: {packet['m113_applicability']['reason']}",
            f"- Future use: {packet['m113_applicability']['m113_future_use']}",
            "",
            "## Closed",
            "",
            "- Predicate direct-status plus CuPy is the measured best compact-signature route on all 524k/1M same-contract rows.",
            "- Numba remains a same-contract grouped-stream fallback/reference and no-C++ partner path.",
            "- Full Python rows remain an explicit slower output contract, not the default compact-summary route.",
            "- Caller-owned coordinate-column reuse is validated at 2M scale, with the charged-column boundary documented.",
            "",
            "## Still Blocked",
            "",
            "- Exact RT-DBSCAN paper reproduction and paper-level speedup wording.",
            "- Public broad DBSCAN acceleration wording.",
            "- Hidden automatic partner or output-contract selection.",
            "- Treating M113 as the current RT-DBSCAN performance path.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["compact_signature_summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
