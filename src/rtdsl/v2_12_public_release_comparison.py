from __future__ import annotations

import json
from pathlib import Path
from typing import Any


V2_12_PUBLIC_RELEASE_COMPARISON_VERSION = "rtdl.v2_12.public_release_comparison.goal4365.v1"

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPTIMIZED_PACKET = (
    ROOT / "docs" / "reports" / "goal4359_optimized_embree_optix_comparison_packet_v2_12_2026-06-13.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _fmt(value: float) -> str:
    if abs(value) >= 1000.0 or (value != 0.0 and abs(value) < 0.0001):
        return f"{value:.6g}"
    return f"{value:.9f}".rstrip("0").rstrip(".")


def _row_status(*, faster_backend: str, ratio: float, row: dict[str, Any]) -> str:
    if faster_backend == "embree":
        return "embree_faster_scoped_row"
    if row.get("app") == "rtnn":
        return "near_parity_not_rt_core_claim"
    if ratio < 1.2:
        return "near_parity_scoped_engineering_row"
    return "scoped_rt_core_value_row"


def _row(
    *,
    app: str,
    row_label: str,
    contract: str,
    metric_name: str,
    metric_unit: str,
    embree_metric: float,
    optix_metric: float,
    ratio: float,
    faster_backend: str,
    evidence_kind: str,
    ratio_authorization: str,
    scope: str,
    source: str,
) -> dict[str, Any]:
    row = {
        "app": app,
        "row_label": row_label,
        "contract": contract,
        "metric_name": metric_name,
        "metric_unit": metric_unit,
        "embree_metric": float(embree_metric),
        "optix_metric": float(optix_metric),
        "embree_divided_by_optix": float(ratio),
        "faster_backend": faster_backend,
        "evidence_kind": evidence_kind,
        "ratio_authorization": ratio_authorization,
        "scope": scope,
        "source": source,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    row["release_wording_status"] = _row_status(
        faster_backend=faster_backend,
        ratio=float(ratio),
        row=row,
    )
    return row


def _measured_pair_row(pair: dict[str, Any], source: str) -> dict[str, Any]:
    embree = pair["embree_cpu_optimized"]
    optix = pair["optix_rt"]
    return _row(
        app=str(pair["app"]),
        row_label="LibRTS prepared AABB query",
        contract=str(pair["contract"]),
        metric_name="query_median_sec",
        metric_unit="sec",
        embree_metric=float(embree["query_median_sec"]),
        optix_metric=float(optix["query_median_sec"]),
        ratio=float(pair["optix_query_median_faster_than_optimized_embree"]),
        faster_backend="optix",
        evidence_kind="fully_optimized_same_contract_measured_pair",
        ratio_authorization="internal_same_contract_query_median_only_not_whole_app_claim",
        scope=(
            "same 1024x1024 prepared AABB query shape; query median only; scene prepare "
            "and elapsed totals are reported separately"
        ),
        source=source,
    )


def _scale_row(row: dict[str, Any], source: str) -> dict[str, Any]:
    return _row(
        app=str(row["app"]),
        row_label=str(row["app"]),
        contract=str(row["contract"]),
        metric_name=str(row["metric_name"]),
        metric_unit=str(row["metric_unit"]),
        embree_metric=float(row["embree_metric"]),
        optix_metric=float(row["optix_metric"]),
        ratio=float(row["embree_metric_divided_by_optix_metric"]),
        faster_backend=str(row["faster_backend_for_metric"]),
        evidence_kind="clean_internal_query_ratio",
        ratio_authorization=str(row["ratio_authorization"]),
        scope="prepared query/count phase only; not whole-application timing",
        source=source,
    )


def _same_stream_row(row: dict[str, Any], source: str) -> dict[str, Any]:
    return _row(
        app=str(row["app"]),
        row_label=f"Spatial RayJoin {str(row['workload']).upper()} same-stream scalar count",
        contract=str(row["contract"]),
        metric_name=str(row["metric_name"]),
        metric_unit=str(row["metric_unit"]),
        embree_metric=float(row["embree_metric"]),
        optix_metric=float(row["optix_metric"]),
        ratio=float(row["embree_metric_divided_by_optix_metric"]),
        faster_backend=str(row["faster_backend_for_metric"]),
        evidence_kind="same_stream_scalar_count_pair",
        ratio_authorization=str(row["ratio_authorization"]),
        scope=(
            "RayJoin-exported same stream, scalar count output only; not RayJoin whole-system "
            "or paper-reproduction wording"
        ),
        source=source,
    )


def _same_contract_backend_row(row: dict[str, Any], source: str) -> dict[str, Any]:
    scope_by_app = {
        "rtnn": (
            "same raw-row ranked-summary contract; this row is explicitly not an RT-core "
            "neighbor-search claim"
        ),
        "rt_dbscan": "same RTDL+Numba configured route with the Numba continuation held fixed",
        "barnes_hut": "same native node-coverage threshold contract; not force-vector or paper reproduction",
        "robot_collision": "same prepared-buffer compact flag contract; not continuous collision or planner timing",
        "raydb_style": "same prepared grouped-reduction contract; not SQL, DBMS, or typed hit-stream handoff timing",
    }
    return _row(
        app=str(row["app"]),
        row_label=str(row["app"]),
        contract=str(row["contract"]),
        metric_name=str(row["metric_name"]),
        metric_unit=str(row["metric_unit"]),
        embree_metric=float(row["embree_metric"]),
        optix_metric=float(row["optix_metric"]),
        ratio=float(row["embree_metric_divided_by_optix_metric"]),
        faster_backend=str(row["faster_backend_for_metric"]),
        evidence_kind="same_contract_backend_pair",
        ratio_authorization=str(row["ratio_authorization"]),
        scope=scope_by_app[str(row["app"])],
        source=source,
    )


def v2_12_public_release_comparison(
    *,
    optimized_packet_path: Path | None = None,
) -> dict[str, Any]:
    packet_path = optimized_packet_path or DEFAULT_OPTIMIZED_PACKET
    packet = _load_json(packet_path)
    summary = dict(packet["summary"])
    source = _relative(packet_path)

    rows = [
        _measured_pair_row(dict(packet["measured_pairs"][0]), source),
        *[_scale_row(dict(row), source) for row in packet["scale_comparison_rows"]],
        *[_same_stream_row(dict(row), source) for row in packet["same_stream_comparison_rows"]],
        *[
            _same_contract_backend_row(dict(row), source)
            for row in packet["same_contract_backend_comparison_rows"]
        ],
    ]
    rows = sorted(rows, key=lambda row: (row["app"], row["row_label"], row["contract"]))

    errors: list[str] = []
    if packet.get("validation", {}).get("status") != "accept":
        errors.append("optimized packet validation is not accept")
    if summary.get("boundary_limited_phase_ratio_count") != 0:
        errors.append("optimized packet still has active boundary-limited rows")
    if summary.get("contract_split_pair_required_count") != 0:
        errors.append("optimized packet still has contract-choice blockers")
    if summary.get("same_contract_scale_pair_required_count") != 0:
        errors.append("optimized packet still needs same-contract scale pairs")
    if len({row["app"] for row in rows}) != 10:
        errors.append("release table must cover ten promoted benchmark apps")
    if len(rows) != 11:
        errors.append("release table must contain eleven scoped rows including RayJoin LSI/PIP split")
    if not any(row["app"] == "contact_manifold" and row["faster_backend"] == "embree" for row in rows):
        errors.append("contact_manifold Embree-faster row must stay explicit")
    if not any(row["app"] == "rtnn" and row["release_wording_status"] == "near_parity_not_rt_core_claim" for row in rows):
        errors.append("RTNN near-parity non-RT-core status must stay explicit")

    optix_faster = [row for row in rows if row["faster_backend"] == "optix"]
    embree_faster = [row for row in rows if row["faster_backend"] == "embree"]
    strong_rows = [
        row for row in rows if row["release_wording_status"] == "scoped_rt_core_value_row"
    ]

    return {
        "version": V2_12_PUBLIC_RELEASE_COMPARISON_VERSION,
        "status": "release_facing_scoped_comparison_not_broad_speedup_claim",
        "source_artifacts": {
            "optimized_packet": source,
            "campaign_closeout": "docs/reports/goal4345_backend_comparison_campaign_closeout_2026-06-11.md",
        },
        "claim_boundary": (
            "RTDL v2.12 authorizes a source-tree release marker and row-scoped "
            "OptiX/RT-core versus Embree CPU comparison wording. It does not "
            "authorize broad RT-core speedup, whole-application speedup, package "
            "install, automatic partner selection, RTDL-beats-RayJoin, paper "
            "reproduction, Intel GPU, or general zero-copy/device-residency claims."
        ),
        "fairness_policy": (
            "Rows are compared only when the output contract is scoped and the "
            "optimized packet accepts the evidence. Partner work is named and held "
            "fixed where used; RT-DBSCAN uses the same Numba continuation on both "
            "sides. Contact Manifold and RTNN stay explicitly mixed rather than "
            "being folded into a broad RT-core win."
        ),
        "allowed_public_wording": (
            "RTDL v2.12 provides a source-tree, row-scoped comparison of NVIDIA "
            "OptiX/RT-core paths against Embree CPU paths for the promoted benchmark "
            "portfolio. The accepted optimized packet has no active boundary-limited "
            "rows and no contract-choice blockers; performance wording must cite the "
            "exact row and artifact."
        ),
        "blocked_wording": (
            "Do not say that RT cores make every benchmark app faster, that RTDL "
            "beats RayJoin as a whole system, that the RayJoin paper is reproduced, "
            "or that these rows are whole-application speedups."
        ),
        "rows": tuple(rows),
        "summary": {
            "promoted_app_count": len({row["app"] for row in rows}),
            "release_table_row_count": len(rows),
            "optix_faster_row_count": len(optix_faster),
            "embree_faster_row_count": len(embree_faster),
            "scoped_rt_core_value_row_count": len(strong_rows),
            "near_parity_row_count": sum(
                1 for row in rows if row["release_wording_status"].startswith("near_parity")
            ),
            "boundary_limited_phase_ratio_count": int(summary["boundary_limited_phase_ratio_count"]),
            "contract_choice_blocker_count": int(summary["contract_split_pair_required_count"]),
            "same_contract_scale_pair_required_count": int(summary["same_contract_scale_pair_required_count"]),
            "optimized_packet_internal_query_median_ratio_count": int(
                summary["internal_query_median_ratio_count"]
            ),
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "release_marker_authorized": True,
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
    }


def markdown_v2_12_public_release_comparison(payload: dict[str, Any]) -> str:
    lines = [
        "# RTDL v2.12 Scoped RT-Core vs Embree CPU Comparison",
        "",
        "Status: release-facing scoped comparison; not broad speedup wording.",
        "",
        "## Allowed Wording",
        "",
        str(payload["allowed_public_wording"]),
        "",
        "## Comparison Table",
        "",
        "| App / Row | Contract | Metric | Embree | OptiX | Embree / OptiX | Faster | Reading |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {label} | `{contract}` | `{metric}` | {embree} {unit} | {optix} {unit} | {ratio:.2f}x | `{faster}` | {status}; {scope} |".format(
                label=row["row_label"],
                contract=row["contract"],
                metric=row["metric_name"],
                embree=_fmt(float(row["embree_metric"])),
                optix=_fmt(float(row["optix_metric"])),
                unit=row["metric_unit"],
                ratio=float(row["embree_divided_by_optix"]),
                faster=row["faster_backend"],
                status=row["release_wording_status"],
                scope=row["scope"],
            )
        )

    summary = dict(payload["summary"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Promoted apps covered: `{summary['promoted_app_count']}`.",
            f"- Scoped table rows: `{summary['release_table_row_count']}`.",
            f"- OptiX-faster scoped rows: `{summary['optix_faster_row_count']}`.",
            f"- Embree-faster scoped rows: `{summary['embree_faster_row_count']}`.",
            f"- Active boundary-limited rows: `{summary['boundary_limited_phase_ratio_count']}`.",
            f"- Contract-choice blockers: `{summary['contract_choice_blocker_count']}`.",
            "",
            "## Fairness",
            "",
            str(payload["fairness_policy"]),
            "",
            "## Blocked Wording",
            "",
            str(payload["blocked_wording"]),
            "",
            "## Claim Boundary",
            "",
            str(payload["claim_boundary"]),
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"

