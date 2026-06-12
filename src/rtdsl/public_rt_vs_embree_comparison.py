from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


PUBLIC_RT_VS_EMBREE_COMPARISON_VERSION = "rtdl.goal4348.public_grade_rt_vs_embree_comparison.v1"

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_COMPARISON = (
    ROOT / "docs" / "reports" / "goal4347_fair_rt_vs_embree_professional_comparison_2026-06-12.json"
)
DEFAULT_CONTACT_BROADPHASE_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4348_public_grade_rt_vs_embree_run"
    / "contact_broadphase_sweep"
    / "summary.json"
)
DEFAULT_CONTACT_NATIVE_COLLECT_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4348_public_grade_rt_vs_embree_run"
    / "contact_native_collect_long_repeat"
    / "summary.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _fmt(value: float) -> str:
    if abs(value) >= 1000.0 or (value != 0.0 and abs(value) < 0.0001):
        return f"{value:.6g}"
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _public_status(row: dict[str, Any]) -> str:
    ratio = float(row["embree_divided_by_optix"])
    if row["faster_backend"] != "optix":
        return "cpu_wins_this_metric"
    if ratio < 1.2:
        return "engineering_only_margin_below_1_20x"
    return "public_review_ready_prepared_phase_wording"


def _normalize_base_ratio_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "app": str(row["app"]),
        "contract": str(row["contract"]),
        "metric_unit": str(row["metric_unit"]),
        "optix_metric": float(row["optix_metric"]),
        "best_embree_metric": float(row["best_embree_metric"]),
        "best_embree_threads": row.get("best_embree_threads"),
        "embree_divided_by_optix": float(row["embree_divided_by_optix"]),
        "faster_backend": str(row["faster_backend"]),
        "status": str(row.get("status", "ratio_eligible")),
        "note": str(row.get("note", "")),
        "source": str(row.get("source", "")),
        "comparison_scope": (
            "prepared query/count/traversal phase; not whole-app unless stated in note"
        ),
    }
    normalized["public_wording_status"] = _public_status(normalized)
    return normalized


def _contact_broadphase_rows(summary: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    rows = tuple(summary.get("rows", ()))
    grids = sorted({int(row["grid_count"]) for row in rows if row.get("returncode") == 0})
    output: list[dict[str, Any]] = []
    for grid in grids:
        optix = next(
            row for row in rows
            if row.get("returncode") == 0 and row.get("backend") == "optix" and int(row["grid_count"]) == grid
        )
        embree_candidates = [
            row for row in rows
            if row.get("returncode") == 0 and row.get("backend") == "embree" and int(row["grid_count"]) == grid
        ]
        best_embree = min(
            embree_candidates,
            key=lambda row: float(row["emit_aabb_intersection_pair_rows_2d_median_sec"]),
        )
        optix_metric = float(optix["emit_aabb_intersection_pair_rows_2d_median_sec"])
        embree_metric = float(best_embree["emit_aabb_intersection_pair_rows_2d_median_sec"])
        ratio = embree_metric / optix_metric
        output.append(
            {
                "app": "contact_manifold",
                "contract": f"generic_aabb_broadphase_contact_candidates_2d_grid{grid}",
                "grid_count": grid,
                "valid_count": int(optix["valid_count"]),
                "all_pairs_count": int(optix["all_pairs_count"]),
                "metric_unit": "sec",
                "metric_name": "emit_aabb_intersection_pair_rows_2d_median_sec",
                "optix_metric": optix_metric,
                "best_embree_metric": embree_metric,
                "best_embree_threads": best_embree.get("threads"),
                "embree_divided_by_optix": ratio,
                "faster_backend": "optix" if ratio > 1.0 else ("embree" if ratio < 1.0 else "tie"),
                "optix_prepare_aabb_index_2d_sec": float(optix["prepare_aabb_index_2d_sec"]),
                "best_embree_prepare_aabb_index_2d_sec": float(best_embree["prepare_aabb_index_2d_sec"]),
                "repeat_count": int(summary["repeat"]),
                "warmup_count": int(summary["warmup"]),
                "matches_cpu_reference": bool(optix["matches_cpu_reference"] and best_embree["matches_cpu_reference"]),
                "complete_candidate_coverage": bool(
                    optix["complete_candidate_coverage"] and best_embree["complete_candidate_coverage"]
                ),
                "comparison_scope": (
                    "prepared generic AABB broadphase query median; app exact refinement and contact "
                    "interpretation are common host-side continuation"
                ),
                "public_wording_status": "public_review_ready_prepared_phase_wording"
                if ratio >= 1.2 and ratio > 1.0
                else "engineering_only_tiny_or_low_margin_contact_scale",
                "source": _relative(DEFAULT_CONTACT_BROADPHASE_SUMMARY),
            }
        )
    return tuple(output)


def _contact_native_collect_diagnostics(summary: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    diagnostics = []
    for row in summary.get("rows", ()):
        if row.get("returncode") != 0:
            continue
        diagnostics.append(
            {
                "case": row["case"],
                "backend": row["backend"],
                "threads": row.get("threads"),
                "dataset": row["dataset"],
                "repeat_count": int(row["repeat_count"]),
                "valid_count": int(row["valid_count"]),
                "median_sec": float(row["native_collect_elapsed_sec"]),
                "p05_sec": float(row["p05_sec"]),
                "p95_sec": float(row["p95_sec"]),
                "total_sec": float(row["native_collect_total_sec"]),
                "matches_cpu_reference": bool(row["matches_cpu_reference"]),
                "complete_candidate_coverage": bool(row["complete_candidate_coverage"]),
                "scope": (
                    "generic COLLECT_K_BOUNDED micro-kernel over already-known Python oracle rows; "
                    "not an RT traversal comparison"
                ),
            }
        )
    return tuple(diagnostics)


def public_rt_vs_embree_comparison_packet(
    *,
    base_comparison_path: Path | None = None,
    contact_broadphase_summary_path: Path | None = None,
    contact_native_collect_summary_path: Path | None = None,
) -> dict[str, Any]:
    base_path = base_comparison_path or DEFAULT_BASE_COMPARISON
    broadphase_path = contact_broadphase_summary_path or DEFAULT_CONTACT_BROADPHASE_SUMMARY
    native_collect_path = contact_native_collect_summary_path or DEFAULT_CONTACT_NATIVE_COLLECT_SUMMARY
    base = _load_json(base_path)
    broadphase = _load_json(broadphase_path)
    native_collect = _load_json(native_collect_path)

    contact_rows = _contact_broadphase_rows(broadphase)
    selected_contact = next(row for row in contact_rows if row["grid_count"] == max(r["grid_count"] for r in contact_rows))
    base_rows = [
        _normalize_base_ratio_row(row)
        for row in base["ratio_rows"]
        if row["app"] != "contact_manifold"
    ]
    main_rows = tuple(base_rows + [selected_contact])
    main_rows = tuple(sorted(main_rows, key=lambda row: (row["app"], row["contract"])))

    old_contact_rows = tuple(
        _normalize_base_ratio_row(row)
        for row in base["ratio_rows"]
        if row["app"] == "contact_manifold"
    )
    diagnostics = _contact_native_collect_diagnostics(native_collect)
    optix_wins = sum(1 for row in main_rows if row["faster_backend"] == "optix")
    review_ready = sum(
        1 for row in main_rows
        if row["public_wording_status"] == "public_review_ready_prepared_phase_wording"
    )
    ratios = [float(row["embree_divided_by_optix"]) for row in main_rows if row["faster_backend"] == "optix"]

    errors: list[str] = []
    if not base.get("optix_scale_status", {}).get("all_pass"):
        errors.append("base OptiX scale status is not all-pass")
    if old_contact_rows and any(row["contract"] == "native_collect_k_bounded_witness_rows" for row in main_rows):
        errors.append("old contact native_collect_k row leaked into main comparison table")
    if len(contact_rows) != 4:
        errors.append("contact broadphase sweep must contain four grid scales")
    for row in contact_rows:
        if not row["matches_cpu_reference"] or not row["complete_candidate_coverage"]:
            errors.append(f"contact broadphase grid {row['grid_count']} failed correctness/coverage")
    for row in main_rows:
        if row["status"] != "ratio_eligible" if "status" in row else False:
            errors.append(f"{row['app']}: row is not ratio eligible")
        if float(row["optix_metric"]) <= 0.0 or float(row["best_embree_metric"]) <= 0.0:
            errors.append(f"{row['app']}: non-positive comparison metric")

    return {
        "version": PUBLIC_RT_VS_EMBREE_COMPARISON_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "hardware": base["hardware"],
        "source_artifacts": {
            "base_comparison": _relative(base_path),
            "contact_broadphase_summary": _relative(broadphase_path),
            "contact_native_collect_summary": _relative(native_collect_path),
        },
        "fairness_policy": (
            "Only matched output contracts are ratioed. The compared values are prepared "
            "query/count/traversal phase medians unless a row explicitly says otherwise. "
            "Partner continuations are held constant where used; RT-DBSCAN uses the same "
            "Numba continuation on both sides. Rows with mismatched output contracts remain "
            "evidence-only."
        ),
        "optimization_status": {
            "nvidia_rt_core_side": "all current OptiX scale rows pass after CUDA 12.8/Numba toolchain pinning",
            "embree_cpu_side": (
                "Embree 4.3.0 built on the pod, native AABB count path used, native prepared "
                "AABB row output added for contact broadphase, Embree thread sweeps retained "
                "where measured"
            ),
            "intel_gpu_side": "not measured and intentionally out of scope",
            "intel_cpu_note": "hardware here is AMD EPYC 7702 running Intel Embree, not an Intel CPU",
        },
        "main_rows": main_rows,
        "contact_broadphase_scale_rows": contact_rows,
        "contact_native_collect_diagnostics": diagnostics,
        "evidence_only_rows": tuple(base.get("non_ratio_rows", ())),
        "excluded_main_ratio_rows": old_contact_rows,
        "summary": {
            "main_ratio_row_count": len(main_rows),
            "optix_faster_row_count": optix_wins,
            "public_review_ready_prepared_phase_row_count": review_ready,
            "min_optix_speedup_vs_embree_on_optix_win_rows": min(ratios) if ratios else None,
            "max_optix_speedup_vs_embree_on_optix_win_rows": max(ratios) if ratios else None,
            "whole_app_speedup_claim_authorized": False,
            "broad_unqualified_rt_core_claim_authorized": False,
            "prepared_phase_wording_ready": review_ready == len(main_rows) and optix_wins == len(main_rows),
        },
        "allowed_public_wording": (
            "On an RTX 4000 Ada GPU versus Embree 4.3.0 on the pod's AMD EPYC 7702 CPU, "
            "RTDL's matched prepared query/count/traversal phases were faster with OptiX "
            "on every ratio-eligible benchmark contract in this packet. The measured "
            "OptiX-vs-best-Embree phase ratios range from "
            f"{min(ratios):.2f}x to {max(ratios):.2f}x. These are prepared phase results, "
            "not whole-application speedups."
        ) if ratios else "",
    }


def markdown_public_rt_vs_embree_comparison(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal4348: Public-Grade RT Core vs Embree CPU Comparison Packet",
        "",
        "Date: 2026-06-12",
        "",
        "## Verdict",
        "",
        payload["allowed_public_wording"],
        "",
        "This packet compares NVIDIA RT hardware through OptiX with Embree CPU traversal on "
        "the pod. It is not Intel GPU evidence, and this pod CPU is AMD EPYC running Intel Embree.",
        "",
        "## Prepared Phase Table",
        "",
        "| App / Contract | OptiX Metric | Best Embree Metric | Embree Threads | Embree / OptiX | Faster | Scope |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["main_rows"]:
        threads = "" if row.get("best_embree_threads") is None else str(row["best_embree_threads"])
        lines.append(
            "| `{app}` / `{contract}` | {optix} {unit} | {embree} {unit} | {threads} | {ratio:.2f}x | `{faster}` | {scope} |".format(
                app=row["app"],
                contract=row["contract"],
                optix=_fmt(float(row["optix_metric"])),
                embree=_fmt(float(row["best_embree_metric"])),
                unit=row["metric_unit"],
                threads=threads,
                ratio=float(row["embree_divided_by_optix"]),
                faster=row["faster_backend"],
                scope=row["comparison_scope"],
            )
        )

    lines.extend(
        [
            "",
            "## Contact Manifold",
            "",
            "The old reversed row was a 64-row `native_collect_k` micro-kernel over already-known "
            "Python oracle rows, so it is excluded from the main RT-hardware table. The replacement "
            "row uses generic prepared AABB broadphase rows on both OptiX and Embree, then the same "
            "host refinement/collect continuation.",
            "",
            "| Grid | OptiX Broadphase Median | Best Embree Broadphase Median | Embree Threads | Embree / OptiX | Faster | OptiX Prepare | Best Embree Prepare |",
            "| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for row in payload["contact_broadphase_scale_rows"]:
        lines.append(
            "| {grid} | {optix} s | {embree} s | {threads} | {ratio:.2f}x | `{faster}` | {oprep} s | {eprep} s |".format(
                grid=row["grid_count"],
                optix=_fmt(float(row["optix_metric"])),
                embree=_fmt(float(row["best_embree_metric"])),
                threads=row["best_embree_threads"],
                ratio=float(row["embree_divided_by_optix"]),
                faster=row["faster_backend"],
                oprep=_fmt(float(row["optix_prepare_aabb_index_2d_sec"])),
                eprep=_fmt(float(row["best_embree_prepare_aabb_index_2d_sec"])),
            )
        )

    lines.extend(
        [
            "",
            "Long-repeat diagnostic for the excluded 64-row collector:",
            "",
            "| Case | Median | p05 | p95 | Repeats | Scope |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["contact_native_collect_diagnostics"]:
        lines.append(
            "| `{case}` | {median} s | {p05} s | {p95} s | {repeat} | {scope} |".format(
                case=row["case"],
                median=_fmt(float(row["median_sec"])),
                p05=_fmt(float(row["p05_sec"])),
                p95=_fmt(float(row["p95_sec"])),
                repeat=row["repeat_count"],
                scope=row["scope"],
            )
        )

    lines.extend(
        [
            "",
            "## Excluded Evidence",
            "",
        ]
    )
    for row in payload["evidence_only_rows"]:
        lines.append(f"- `{row['app']}` / `{row['contract']}`: {row['reason']}")
    for row in payload["excluded_main_ratio_rows"]:
        lines.append(
            f"- `{row['app']}` / `{row['contract']}`: excluded from the main RT table because it is "
            "a tiny generic collector over precomputed oracle rows, not a traversal/broadphase comparison."
        )

    lines.extend(
        [
            "",
            "## Fairness",
            "",
            payload["fairness_policy"],
            "",
            "Optimization status:",
            "",
            f"- NVIDIA RT side: {payload['optimization_status']['nvidia_rt_core_side']}.",
            f"- Embree CPU side: {payload['optimization_status']['embree_cpu_side']}.",
            f"- Intel GPU side: {payload['optimization_status']['intel_gpu_side']}.",
            f"- CPU note: {payload['optimization_status']['intel_cpu_note']}.",
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"
