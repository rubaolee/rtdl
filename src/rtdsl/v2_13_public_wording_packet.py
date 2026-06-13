from __future__ import annotations

import json
from pathlib import Path
from typing import Any


V2_13_PUBLIC_WORDING_PACKET_VERSION = "rtdl.v2_13.public_wording.goal4370.v1"

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_SCALE = ROOT / "docs" / "reports" / "goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.json"
DEFAULT_EMBREE_FAIRNESS = ROOT / "docs" / "reports" / "goal4369_embree_cpu_fairness_hardening_2026-06-13.json"
DEFAULT_RAYJOIN_AUTHORS = ROOT / "docs" / "reports" / "goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.json"
DEFAULT_PIP_OPTIMIZED = (
    ROOT
    / "docs"
    / "reports"
    / "goal4368_pip_exact_prepared_points_executor_2026-06-13"
    / "summary.json"
)


BLOCKED_WORDING = (
    "Do not say RT cores make every benchmark app faster.",
    "Do not say these are whole-application speedups.",
    "Do not say RTDL reproduces the RayJoin paper.",
    "Do not say RTDL beats RayJoin as a whole system.",
    "Do not say RTNN is an RT-core neighbor-search speedup.",
    "Do not say partner selection is automatic or universally Numba-based.",
    "Do not say Intel GPU or AMD GPU performance is covered by this packet.",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _round(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _status_for_row(row: dict[str, Any]) -> str:
    status = str(row["comparison_status"])
    ratio = float(row["speedup_embree_per_iter_div_optix_per_iter"])
    if row["app"] == "rtnn":
        return "blocked_not_rt_core_neighbor_search_claim"
    if ratio < 1.0:
        return "ready_row_scoped_embree_faster_wording"
    if ratio < 1.2:
        return "ready_near_parity_scoped_engineering_wording"
    if status == "clean_backend_swap_prepared_phase":
        return "ready_row_scoped_prepared_phase_wording"
    if status == "clean_backend_swap_traversal_phase_only":
        return "ready_traversal_phase_only_wording"
    if status.startswith("mostly_clean"):
        return "ready_with_explicit_output_surface_caveat"
    return "internal_only"


def _public_authorized(status: str) -> bool:
    return status.startswith("ready_")


def _allowed_wording(row: dict[str, Any], status: str) -> str:
    speedup = float(row["speedup_embree_per_iter_div_optix_per_iter"])
    if status == "blocked_not_rt_core_neighbor_search_claim":
        return (
            "Do not publish RTNN as an RT-core neighbor-search speedup. Keep it as engineering evidence until "
            "the release has an end-to-end RTNN claim boundary that reviewers explicitly approve."
        )
    if speedup < 1.0:
        inverse = 1.0 / speedup
        return (
            f"For `{row['app']}` under `{row['contract']}`, the row-scoped Embree CPU prepared "
            f"measurement is {inverse:.2f}x faster per iteration than the RTDL OptiX prepared "
            "measurement for this scoped protocol. Publish this as a near-parity or Embree-faster row, "
            "not as an RT-core speedup."
        )
    base = (
        f"For `{row['app']}` under `{row['contract']}`, the row-scoped RTDL OptiX prepared "
        f"measurement is {speedup:.2f}x faster per iteration than the best measured Embree CPU row "
        f"for the same scoped contract/protocol."
    )
    if status == "ready_near_parity_scoped_engineering_wording":
        return base + " Word this as near parity engineering evidence, not as a material RT-core speedup."
    if status == "ready_traversal_phase_only_wording":
        return base + " Word this only as a traversal-phase result, not as a full hot-loop or app speedup."
    if status == "ready_with_explicit_output_surface_caveat":
        return base + " Include the output-surface caveat from the packet; do not present it as a pure backend swap."
    return base + " Keep the prepared-query/row-scoped contract in the sentence."


def v2_13_public_wording_packet(
    *,
    human_scale_path: Path | None = None,
    embree_fairness_path: Path | None = None,
    rayjoin_authors_path: Path | None = None,
    pip_optimized_path: Path | None = None,
) -> dict[str, Any]:
    human_path = human_scale_path or DEFAULT_HUMAN_SCALE
    fairness_path = embree_fairness_path or DEFAULT_EMBREE_FAIRNESS
    rayjoin_path = rayjoin_authors_path or DEFAULT_RAYJOIN_AUTHORS
    pip_path = pip_optimized_path or DEFAULT_PIP_OPTIMIZED

    human = _load_json(human_path)
    fairness = _load_json(fairness_path)
    rayjoin = _load_json(rayjoin_path)
    pip = _load_json(pip_path)

    rows: list[dict[str, Any]] = []
    for row in human["rows"]:
        status = _status_for_row(row)
        authorized = _public_authorized(status)
        rows.append(
            {
                "app": row["app"],
                "contract": row["contract"],
                "comparison_status": row["comparison_status"],
                "public_wording_status": status,
                "row_scoped_public_wording_authorized": authorized,
                "speedup_embree_per_iter_div_optix_per_iter": row["speedup_embree_per_iter_div_optix_per_iter"],
                "optix_total_sec": row["optix_total_sec"],
                "embree_total_sec": row["embree_total_sec"],
                "best_embree_threads": row["best_embree_threads"],
                "reasonability_verdict": row["reasonability_verdict"],
                "only_material_diff_claim": row["only_material_diff_claim"],
                "speedup_explanation": row["speedup_explanation"],
                "allowed_wording": _allowed_wording(row, status),
                "blocked_wording_note": row["public_wording"],
                "whole_app_speedup_claim_authorized": False,
            }
        )

    errors: list[str] = []
    if human.get("validation", {}).get("status") != "accept":
        errors.append("human-scale timing packet is not accepted")
    if fairness.get("validation", {}).get("status") != "accept":
        errors.append("Embree CPU fairness packet is not accepted")
    if rayjoin.get("validation", {}).get("status") != "accept":
        errors.append("RayJoin authors-code packet is not accepted")
    if not pip.get("rtdl", {}).get("pip", {}).get("correctness", {}).get("cross_backend_counts_match"):
        errors.append("Goal4368 PIP optimized packet does not record cross-backend count agreement")
    if any("divided by" not in row["speedup_explanation"] for row in rows):
        errors.append("every row must explain the observed speedup as a measured ratio")
    if any(row["row_scoped_public_wording_authorized"] and not row["allowed_wording"] for row in rows):
        errors.append("authorized rows must have explicit allowed wording")
    if any(row["whole_app_speedup_claim_authorized"] for row in rows):
        errors.append("whole-application speedup wording must remain blocked")
    if any(
        row["row_scoped_public_wording_authorized"]
        and float(row["speedup_embree_per_iter_div_optix_per_iter"]) < 1.0
        and "Embree CPU" not in row["allowed_wording"]
        for row in rows
    ):
        errors.append("Embree-faster rows must not be worded as OptiX speedups")

    authorized_rows = [row for row in rows if row["row_scoped_public_wording_authorized"]]
    blocked_rows = [row for row in rows if not row["row_scoped_public_wording_authorized"]]
    rayjoin_lsi = next(row for row in rows if row["app"] == "spatial_rayjoin_lsi")
    rayjoin_pip = next(row for row in rows if row["app"] == "spatial_rayjoin_pip")

    return {
        "version": V2_13_PUBLIC_WORDING_PACKET_VERSION,
        "status": "accept_public_wording_packet" if not errors else "reject",
        "source_artifacts": {
            "human_scale": _relative(human_path),
            "embree_fairness": _relative(fairness_path),
            "rayjoin_authors_code": _relative(rayjoin_path),
            "pip_optimized": _relative(pip_path),
        },
        "summary": {
            "row_count": len(rows),
            "row_scoped_public_wording_authorized_count": len(authorized_rows),
            "blocked_row_count": len(blocked_rows),
            "zero_unexplained_rows": not any("divided by" not in row["speedup_explanation"] for row in rows),
            "broad_rt_core_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "rayjoin_whole_system_claim_authorized": False,
            "rayjoin_lsi_row_scoped_speedup": _round(rayjoin_lsi["speedup_embree_per_iter_div_optix_per_iter"], 2),
            "rayjoin_pip_row_scoped_speedup": _round(rayjoin_pip["speedup_embree_per_iter_div_optix_per_iter"], 2),
            "rtnn_public_rt_core_claim_authorized": False,
            "prepare_amd_gpu_now": False,
            "prepare_amd_gpu_after_v2_13_close": True,
        },
        "rows": rows,
        "allowed_portfolio_wording": (
            "RTDL v2.13 has row-scoped evidence that selected prepared OptiX/RT-core paths can outperform "
            "same-contract or explicitly caveated Embree CPU baselines across the promoted benchmark suite. "
            "Each published sentence must name the benchmark row, contract, speedup direction, and caveat."
        ),
        "blocked_wording": BLOCKED_WORDING,
        "amd_gpu_decision": {
            "prepare_amd_gpu_now": False,
            "recommended_timing": "Prepare AMD GPU after v2.13 is closed/tagged, not before the NVIDIA-vs-Embree packet is frozen.",
            "reason": "The NVIDIA RT-core versus Embree CPU story is now packetized; AMD should be a separate v2.14-style matrix, not mixed into v2.13 closeout.",
        },
        "validation": {"status": "accept" if not errors else "reject", "errors": errors},
        "broad_rt_core_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rayjoin_whole_system_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "intel_gpu_performance_claim_authorized": False,
        "amd_gpu_performance_claim_authorized": False,
    }


def _fmt(value: Any, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}".rstrip("0").rstrip(".")


def markdown_v2_13_public_wording_packet(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal4370 v2.13 Public Wording Packet",
        "",
        "Status: accepted row-scoped wording packet; broad speedup wording remains blocked.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Validation | `{payload['validation']['status']}` |",
        f"| Rows reviewed | {payload['summary']['row_count']} |",
        f"| Row-scoped wording authorized | {payload['summary']['row_scoped_public_wording_authorized_count']} |",
        f"| Blocked rows | {payload['summary']['blocked_row_count']} |",
        f"| Zero unexplained rows | {payload['summary']['zero_unexplained_rows']} |",
        f"| Broad RT-core wording authorized | {payload['summary']['broad_rt_core_claim_authorized']} |",
        f"| Whole-app speedup wording authorized | {payload['summary']['whole_app_speedup_claim_authorized']} |",
        f"| Prepare AMD GPU now | {payload['summary']['prepare_amd_gpu_now']} |",
        "",
        "## Allowed Portfolio Wording",
        "",
        payload["allowed_portfolio_wording"],
        "",
        "## Row Wording Table",
        "",
        "| App | Status | Speedup | Allowed wording |",
        "| --- | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {app} | `{status}` | {speedup}x | {wording} |".format(
                app=row["app"],
                status=row["public_wording_status"],
                speedup=_fmt(row["speedup_embree_per_iter_div_optix_per_iter"]),
                wording=row["allowed_wording"],
            )
        )

    lines.extend(
        [
            "",
            "## Blocked Wording",
            "",
        ]
    )
    for item in payload["blocked_wording"]:
        lines.append(f"- {item}")

    amd = payload["amd_gpu_decision"]
    lines.extend(
        [
            "",
            "## AMD GPU Decision",
            "",
            f"Prepare AMD GPU now: `{amd['prepare_amd_gpu_now']}`.",
            "",
            amd["recommended_timing"],
            "",
            amd["reason"],
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"
