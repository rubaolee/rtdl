from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


V2_13_CREDIBILITY_ROADMAP_VERSION = "rtdl.v2_13.credibility_roadmap.goal4366.v1"

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V2_12_COMPARISON = (
    ROOT / "docs" / "release_reports" / "v2_12" / "public_rt_vs_embree_comparison.json"
)
DEFAULT_RAYJOIN_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13"
    / "summary.json"
)
DEFAULT_PIP_OPTIMIZED_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4368_pip_exact_prepared_points_executor_2026-06-13"
    / "summary.json"
)


ROW_REASONING_BY_CONTRACT: dict[str, dict[str, str]] = {
    "prepared_fixed_radius_node_coverage_threshold_decision": {
        "classification": "reasonable_scoped_rt_core_value",
        "analysis": (
            "Moderate OptiX win is credible because this row is a native node-coverage "
            "threshold decision, not Barnes-Hut force integration."
        ),
        "v2_13_action": "Keep the force-vector and paper-reproduction boundary visible.",
    },
    "native_collect_k_bounded_witness_rows": {
        "classification": "reasonable_embree_faster_tiny_row",
        "analysis": (
            "Embree winning is credible for this tiny bounded collect-k witness row; "
            "launch and orchestration overhead can dominate the RT path."
        ),
        "v2_13_action": "Add a human-scale repeated batch before any public wording.",
    },
    "directed_threshold_prepared_fixed_radius_count": {
        "classification": "reasonable_scoped_rt_core_value",
        "analysis": (
            "The OptiX win is plausible for a prepared threshold count where traversal "
            "dominates more than output materialization."
        ),
        "v2_13_action": "Keep exact-distance and whole-app claims blocked.",
    },
    "generic_prepared_aabb_index_query_2d": {
        "classification": "reasonable_scoped_rt_core_value",
        "analysis": (
            "Large OptiX win is credible after the native Embree AABB route replaced "
            "the old columnar fallback; this is a prepared query median."
        ),
        "v2_13_action": "Scale box/query counts and report prepare amortization separately.",
    },
    "generic_ray_triangle_primitive_grouped_i64_reduction_3d_prepared_count": {
        "classification": "reasonable_scoped_rt_core_value",
        "analysis": (
            "Large OptiX win is credible for a prepared ray/triangle grouped count; "
            "the row is not SQL, DBMS, or typed stream timing."
        ),
        "v2_13_action": "Keep DB wording blocked and add typed hit-stream evidence separately.",
    },
    "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1": {
        "classification": "reasonable_small_total_win",
        "analysis": (
            "Small tail-total OptiX win is credible because the compact-flag contract "
            "is already tiny; traversal wins are partly hidden by fixed overhead."
        ),
        "v2_13_action": "Report native traversal and tail-total side by side.",
    },
    "rt_dbscan_clustered3d_count_threshold_flags_plus_numba_prepared_grid_column_signature": {
        "classification": "reasonable_scoped_rt_core_value",
        "analysis": (
            "Large OptiX win is credible because both rows hold the same Numba "
            "continuation fixed and differ mainly in the RTDL geometric prefilter."
        ),
        "v2_13_action": "Preserve the partner-fixed route and avoid whole-app DBSCAN wording.",
    },
    "prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows": {
        "classification": "reasonable_not_rt_core_claim",
        "analysis": (
            "Near parity is credible and is not an RT-core neighbor-search claim "
            "because the current OptiX row is a prepared ranked-summary route."
        ),
        "v2_13_action": "Either build a true RT-core neighbor-search row or keep this as backend-only.",
    },
    "lsi_same_stream_scalar_count": {
        "classification": "reasonable_strong_rayjoin_rt_core_row",
        "analysis": (
            "Strong OptiX win is credible: same RayJoin-exported stream, scalar count, "
            "exact count match, and no RTDL row materialization."
        ),
        "v2_13_action": "Retain in the Goal4367 authors-code packet with stream hashes.",
    },
    "pip_same_stream_scalar_count": {
        "classification": "reasonable_but_v2_13_optimization_debt",
        "analysis": (
            "Near parity against Embree and slower-than-RayJoin RT are credible because "
            "exact membership refinement and generic front-door overhead dominate the current row."
        ),
        "v2_13_action": "Use Goal4368 as the improved exact baseline, then keep attacking exact refinement.",
    },
    "rt_graph_2a1_generic_ray_triangle_any_hit": {
        "classification": "reasonable_scoped_rt_core_value",
        "analysis": (
            "Large OptiX win is credible for a prepared ray/triangle any-hit count; "
            "this is query/count timing rather than whole application time."
        ),
        "v2_13_action": "Keep prepared-query wording and add larger human-scale repeats.",
    },
}


ROADMAP_GOALS: tuple[dict[str, Any], ...] = (
    {
        "id": "freeze_v2_12_release_boundary",
        "priority": 0,
        "title": "Freeze v2.12 as the bounded release baseline",
        "deliverable": "A stable v2.12 source-tree tag and comparison packet used only as baseline evidence.",
        "acceptance_gate": (
            "Do not move the v2.12 tag without explicit maintainer decision.",
            "All v2.13 wording must distinguish baseline evidence from new claims.",
        ),
        "depends_on": (),
        "output_artifacts": ("docs/release_reports/v2_12/README.md",),
    },
    {
        "id": "rayjoin_authors_code_comparison_packet",
        "priority": 1,
        "title": "Compare against RayJoin authors code on the same streams",
        "deliverable": (
            "A table covering RayJoin grid, LBVH, and RT logs versus RTDL OptiX and RTDL Embree "
            "for LSI and PIP scalar-count contracts."
        ),
        "acceptance_gate": (
            "Same exported query stream schema and hashes are reported.",
            "RayJoin Query ms, build/index ms, and RTDL hot query ms are separate columns.",
            "Each speedup column states which direction is good.",
            "LSI and PIP each have a reasonability paragraph tied to measured phases.",
        ),
        "depends_on": ("freeze_v2_12_release_boundary",),
        "output_artifacts": (
            "docs/reports/goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.md",
            "docs/reports/goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.json",
            "docs/reports/goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13.md",
            "docs/reports/goal4354_rayjoin_original_vs_rtdl_pod/goal4354_rayjoin_original_vs_rtdl_same_stream_summary.md",
        ),
    },
    {
        "id": "pip_exact_membership_optimization",
        "priority": 2,
        "title": "Turn Spatial RayJoin PIP from explanation debt into optimization evidence",
        "deliverable": (
            "A measured PIP packet that either closes the gap to RayJoin RT or proves why "
            "the exact RTDL contract remains dominated by refinement."
        ),
        "acceptance_gate": (
            "Candidate generation, download, exact refinement, and Python/front-door timing are visible.",
            "The row is rejected for public speedup wording unless the observed speedup has a phase-level explanation.",
            "A successful optimization keeps the exact prepared-points count contract and count agreement.",
        ),
        "depends_on": ("rayjoin_authors_code_comparison_packet",),
        "output_artifacts": (
            "docs/reports/goal4368_pip_exact_prepared_points_executor_2026-06-13.md",
            "docs/reports/goal4368_pip_exact_prepared_points_executor_2026-06-13/summary.json",
            "docs/reports/goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13.md",
        ),
    },
    {
        "id": "embree_cpu_fairness_hardening",
        "priority": 3,
        "title": "Harden the Embree CPU side as the serious multicore baseline",
        "deliverable": (
            "A repeatable Embree CPU protocol with thread counts, warmups, repeats, native traversal time, "
            "and fallback detection for every promoted row."
        ),
        "acceptance_gate": (
            "Every compared Embree row uses a native route or explicitly names the partner continuation.",
            "Thread/environment settings are included in each run packet.",
            "Fallback and boundary-limited rows are excluded from release-facing speedups.",
        ),
        "depends_on": ("freeze_v2_12_release_boundary",),
        "output_artifacts": (
            "docs/reports/goal4369_embree_cpu_fairness_hardening_2026-06-13.md",
            "docs/reports/goal4369_embree_cpu_fairness_hardening_2026-06-13.json",
            "docs/reports/goal4369_embree_cpu_fairness_hardening_2026-06-13/v2_11_cpu_partner_threads8.json",
        ),
    },
    {
        "id": "human_scale_timing_packet",
        "priority": 4,
        "title": "Make tiny rows human-scale without changing the contract",
        "deliverable": (
            "A timing packet that reports 1-10 second aggregate batches plus per-query medians for sub-ms rows."
        ),
        "acceptance_gate": (
            "Batching is repeat-only and does not smuggle in unrelated setup work.",
            "Per-query and aggregate timing are both reported.",
            "Contact Manifold, Robot Collision, LibRTS, and triangle-counting tiny rows are included first.",
        ),
        "depends_on": ("embree_cpu_fairness_hardening",),
        "output_artifacts": (
            "docs/reports/goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.md",
            "docs/reports/goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.json",
            "docs/reports/goal4349_human_scale_rt_vs_embree_run/",
        ),
    },
    {
        "id": "public_wording_packet",
        "priority": 5,
        "title": "Produce the public comparison wording only after row-level explanations pass",
        "deliverable": (
            "A publication table where every speedup has a same-contract basis, a direction definition, "
            "and an observed-speedup explanation."
        ),
        "acceptance_gate": (
            "No broad RT-core speedup wording.",
            "No whole-application speedup wording unless end-to-end evidence exists.",
            "No RTDL-beats-RayJoin wording except for exact rows where the authors-code comparison supports it.",
            "Every surprising row has a written explanation or is marked not publishable.",
        ),
        "depends_on": (
            "rayjoin_authors_code_comparison_packet",
            "pip_exact_membership_optimization",
            "human_scale_timing_packet",
        ),
        "output_artifacts": (
            "docs/reports/goal4370_v2_13_public_wording_packet_2026-06-13.md",
            "docs/reports/goal4370_v2_13_public_wording_packet_2026-06-13.json",
        ),
    },
    {
        "id": "amd_gpu_defer_gate",
        "priority": 6,
        "title": "Defer AMD GPU work until the NVIDIA-vs-Embree story is credible",
        "deliverable": "A go/no-go decision for AMD after v2.13 credibility gates pass.",
        "acceptance_gate": (
            "RayJoin authors-code comparison packet is complete.",
            "PIP either improves or has a phase-level explanation accepted for public wording.",
            "The public wording packet passes with zero unexplained speedup rows.",
        ),
        "depends_on": ("public_wording_packet",),
        "output_artifacts": (
            "docs/reports/goal4370_v2_13_public_wording_packet_2026-06-13.md",
            "docs/reports/goal4366_v2_13_credibility_roadmap_2026-06-13.md",
        ),
    },
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _release_row(rows: list[dict[str, Any]], contract: str) -> dict[str, Any]:
    for row in rows:
        if row["contract"] == contract:
            return row
    raise KeyError(contract)


def _rayjoin_backend(summary: dict[str, Any], workload: str, backend: str) -> dict[str, Any]:
    return dict(summary["rtdl"][workload]["backends"][backend])


def _rayjoin_comparison(summary: dict[str, Any], workload: str, backend: str) -> dict[str, Any]:
    for row in summary["comparisons"]:
        if row["workload"] == workload and row["backend"] == backend:
            return dict(row)
    raise KeyError((workload, backend))


def _median_phase_ms(backend: dict[str, Any], phase: str) -> float | None:
    values: list[float] = []
    for run in backend.get("timing", {}).get("runs", []):
        if run.get("is_warmup"):
            continue
        timings = run.get("native_phase_timings") or {}
        if phase in timings:
            values.append(float(timings[phase]) * 1000.0)
    if not values:
        return None
    return float(statistics.median(values))


def _round(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _row_review(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    reviews: list[dict[str, Any]] = []
    for row in rows:
        reasoning = ROW_REASONING_BY_CONTRACT[row["contract"]]
        ratio = float(row["embree_divided_by_optix"])
        reviews.append(
            {
                "row_label": row["row_label"],
                "app": row["app"],
                "contract": row["contract"],
                "embree_divided_by_optix": ratio,
                "faster_backend": row["faster_backend"],
                "classification": reasoning["classification"],
                "reasonable": True,
                "analysis": reasoning["analysis"],
                "v2_13_action": reasoning["v2_13_action"],
            }
        )
    return tuple(reviews)


def v2_13_credibility_roadmap(
    *,
    v2_12_comparison_path: Path | None = None,
    rayjoin_summary_path: Path | None = None,
    pip_optimized_summary_path: Path | None = None,
) -> dict[str, Any]:
    comparison_path = v2_12_comparison_path or DEFAULT_V2_12_COMPARISON
    rayjoin_path = rayjoin_summary_path or DEFAULT_RAYJOIN_SUMMARY
    pip_optimized_path = pip_optimized_summary_path or DEFAULT_PIP_OPTIMIZED_SUMMARY

    comparison = _load_json(comparison_path)
    rayjoin = _load_json(rayjoin_path)
    pip_optimized = _load_json(pip_optimized_path)

    rows = [dict(row) for row in comparison["rows"]]
    lsi_row = _release_row(rows, "lsi_same_stream_scalar_count")
    pip_row = _release_row(rows, "pip_same_stream_scalar_count")
    contact_row = _release_row(rows, "native_collect_k_bounded_witness_rows")
    rtnn_row = _release_row(rows, "prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows")

    lsi_optix = _rayjoin_backend(rayjoin, "lsi", "optix")
    lsi_embree = _rayjoin_backend(rayjoin, "lsi", "embree")
    pip_optix = _rayjoin_backend(pip_optimized, "pip", "optix")
    pip_embree = _rayjoin_backend(pip_optimized, "pip", "embree")
    lsi_vs_rayjoin = _rayjoin_comparison(rayjoin, "lsi", "optix")
    pip_vs_rayjoin = _rayjoin_comparison(pip_optimized, "pip", "optix")
    pip_embree_over_optix = float(pip_embree["hot_median_sec"]) / float(pip_optix["hot_median_sec"])

    pip_phase_ms = {
        "candidate_write_median_ms": _round(_median_phase_ms(pip_optix, "candidate_write_pass")),
        "candidate_download_median_ms": _round(_median_phase_ms(pip_optix, "candidate_download")),
        "exact_refine_median_ms": _round(_median_phase_ms(pip_optix, "exact_refine")),
        "hot_query_median_ms": _round(float(pip_optix["hot_median_sec"]) * 1000.0),
    }

    errors: list[str] = []
    if comparison.get("validation", {}).get("status") != "accept":
        errors.append("v2.12 public comparison is not accepted")
    if comparison.get("summary", {}).get("release_table_row_count") != 11:
        errors.append("v2.12 comparison must contain the eleven scoped rows")
    if float(lsi_row["embree_divided_by_optix"]) <= 40.0:
        errors.append("RayJoin LSI must remain a strong OptiX-over-Embree baseline")
    if float(pip_row["embree_divided_by_optix"]) >= 1.3:
        errors.append("v2.12 RayJoin PIP release row should remain marked as near-parity optimization debt")
    if pip_embree_over_optix <= 2.5:
        errors.append("Goal4368 optimized PIP should show a clear OptiX-over-Embree improvement")
    if float(lsi_vs_rayjoin["rayjoin_rt_over_rtdl"]) <= 1.0:
        errors.append("LSI authors-code comparison should show RTDL OptiX faster than RayJoin RT")
    if float(pip_vs_rayjoin["rayjoin_rt_over_rtdl"]) >= 0.2:
        errors.append("PIP authors-code comparison should remain a visible RTDL optimization debt")
    if not any(goal["id"] == "amd_gpu_defer_gate" for goal in ROADMAP_GOALS):
        errors.append("AMD GPU deferral gate is missing")

    return {
        "version": V2_13_CREDIBILITY_ROADMAP_VERSION,
        "status": "accepted_plan_not_release_packet" if not errors else "rejected_plan",
        "source_artifacts": {
            "v2_12_public_comparison": _relative(comparison_path),
            "rayjoin_same_stream_summary": _relative(rayjoin_path),
            "pip_optimized_summary": _relative(pip_optimized_path),
        },
        "current_baseline": {
            "v2_12_summary": comparison["summary"],
            "rayjoin_same_stream": {
                "lsi": {
                    "count": int(lsi_optix["row_count"]),
                    "optix_hot_ms": _round(float(lsi_optix["hot_median_sec"]) * 1000.0),
                    "embree_hot_ms": _round(float(lsi_embree["hot_median_sec"]) * 1000.0),
                    "embree_divided_by_optix": _round(float(lsi_row["embree_divided_by_optix"]), 2),
                    "rayjoin_rt_query_ms": _round(float(lsi_vs_rayjoin["rayjoin_rt_query_ms"])),
                    "rayjoin_rt_over_rtdl_optix": _round(float(lsi_vs_rayjoin["rayjoin_rt_over_rtdl"]), 2),
                    "readout": "strong RT-core value row and RTDL OptiX faster than RayJoin RT for scalar count",
                },
                "pip": {
                    "count": int(pip_optix["row_count"]),
                    "optix_hot_ms": _round(float(pip_optix["hot_median_sec"]) * 1000.0),
                    "embree_hot_ms": _round(float(pip_embree["hot_median_sec"]) * 1000.0),
                    "embree_divided_by_optix": _round(pip_embree_over_optix, 2),
                    "rayjoin_rt_query_ms": _round(float(pip_vs_rayjoin["rayjoin_rt_query_ms"])),
                    "rayjoin_rt_over_rtdl_optix": _round(float(pip_vs_rayjoin["rayjoin_rt_over_rtdl"]), 3),
                    "rayjoin_rt_faster_than_rtdl_optix": _round(
                        1.0 / float(pip_vs_rayjoin["rayjoin_rt_over_rtdl"]),
                        2,
                    ),
                    "readout": (
                        "clear OptiX-over-Embree improvement, but current RTDL optimization debt versus RayJoin RT"
                    ),
                    "phase_ms": pip_phase_ms,
                },
            },
            "known_mixed_rows": {
                "contact_manifold": {
                    "embree_divided_by_optix": _round(float(contact_row["embree_divided_by_optix"]), 2),
                    "faster_backend": contact_row["faster_backend"],
                    "readout": "reasonable tiny-row Embree win; needs human-scale batching",
                },
                "rtnn": {
                    "embree_divided_by_optix": _round(float(rtnn_row["embree_divided_by_optix"]), 2),
                    "faster_backend": rtnn_row["faster_backend"],
                    "readout": "near-parity backend row; not an RT-core neighbor-search claim",
                },
            },
            "row_review": _row_review(rows),
        },
        "roadmap_goals": ROADMAP_GOALS,
        "execution_order": tuple(goal["id"] for goal in sorted(ROADMAP_GOALS, key=lambda goal: goal["priority"])),
        "amd_gpu_decision": {
            "prepare_amd_gpu_now": False,
            "recommended_timing": (
                "Prepare AMD GPU only after v2.13 has an accepted RayJoin authors-code comparison, "
                "a PIP optimization/explanation packet, and a public wording packet with zero unexplained rows."
            ),
            "reason": (
                "The current scientific question is NVIDIA RT cores versus Embree CPU cores. "
                "Adding AMD now would widen the matrix before the NVIDIA-vs-CPU story is publication-clean."
            ),
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
    }


def _fmt_number(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.3f}".rstrip("0").rstrip(".")


def markdown_v2_13_credibility_roadmap(payload: dict[str, Any]) -> str:
    baseline = payload["current_baseline"]
    rayjoin = baseline["rayjoin_same_stream"]
    known_mixed = baseline["known_mixed_rows"]

    lines = [
        "# RTDL v2.13 Credibility Roadmap",
        "",
        "Status: accepted plan; not a release packet and not new public speedup wording.",
        "",
        "## Current Baseline",
        "",
        "| Evidence | Measurement | Meaning | v2.13 action |",
        "| --- | ---: | --- | --- |",
        (
            "| v2.12 release table | {rows} scoped rows, {apps} promoted apps | "
            "baseline is complete but row-scoped | freeze as the v2.13 starting point |"
        ).format(
            rows=baseline["v2_12_summary"]["release_table_row_count"],
            apps=baseline["v2_12_summary"]["promoted_app_count"],
        ),
        (
            "| RayJoin LSI same stream | OptiX {optix} ms, Embree {embree} ms, "
            "Embree/OptiX {ratio}x, RayJoin RT/RTDL {rayjoin_ratio}x | {readout} | "
            "use Goal4367 as the authors-code comparison baseline |"
        ).format(
            optix=_fmt_number(rayjoin["lsi"]["optix_hot_ms"]),
            embree=_fmt_number(rayjoin["lsi"]["embree_hot_ms"]),
            ratio=_fmt_number(rayjoin["lsi"]["embree_divided_by_optix"]),
            rayjoin_ratio=_fmt_number(rayjoin["lsi"]["rayjoin_rt_over_rtdl_optix"]),
            readout=rayjoin["lsi"]["readout"],
        ),
        (
            "| RayJoin PIP same stream | OptiX {optix} ms, Embree {embree} ms, "
            "Embree/OptiX {ratio}x, RayJoin RT faster {rayjoin_faster}x | {readout} | "
            "Goal4368 improves the exact route; keep optimizing exact refinement |"
        ).format(
            optix=_fmt_number(rayjoin["pip"]["optix_hot_ms"]),
            embree=_fmt_number(rayjoin["pip"]["embree_hot_ms"]),
            ratio=_fmt_number(rayjoin["pip"]["embree_divided_by_optix"]),
            rayjoin_faster=_fmt_number(rayjoin["pip"]["rayjoin_rt_faster_than_rtdl_optix"]),
            readout=rayjoin["pip"]["readout"],
        ),
        (
            "| Contact Manifold | Embree/OptiX {ratio}x, faster backend `{backend}` | "
            "{readout} | include in human-scale timing packet |"
        ).format(
            ratio=_fmt_number(known_mixed["contact_manifold"]["embree_divided_by_optix"]),
            backend=known_mixed["contact_manifold"]["faster_backend"],
            readout=known_mixed["contact_manifold"]["readout"],
        ),
        (
            "| RTNN | Embree/OptiX {ratio}x, faster backend `{backend}` | "
            "{readout} | keep backend-only unless a true RT-core row is built |"
        ).format(
            ratio=_fmt_number(known_mixed["rtnn"]["embree_divided_by_optix"]),
            backend=known_mixed["rtnn"]["faster_backend"],
            readout=known_mixed["rtnn"]["readout"],
        ),
        "",
        "## Row Reasonability Review",
        "",
        "| Row | Embree / OptiX | Faster | Verdict | Explanation | v2.13 action |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for row in baseline["row_review"]:
        lines.append(
            "| {label} | {ratio}x | `{faster}` | `{classification}` | {analysis} | {action} |".format(
                label=row["row_label"],
                ratio=_fmt_number(float(row["embree_divided_by_optix"])),
                faster=row["faster_backend"],
                classification=row["classification"],
                analysis=row["analysis"],
                action=row["v2_13_action"],
            )
        )

    lines.extend(
        [
            "",
            "## PIP Phase Debt",
            "",
            (
                "The current PIP OptiX row is explainable but not satisfying: hot query median "
                "{hot} ms, candidate write median {candidate} ms, candidate download median "
                "{download} ms, and exact refinement median {refine} ms."
            ).format(
                hot=_fmt_number(rayjoin["pip"]["phase_ms"]["hot_query_median_ms"]),
                candidate=_fmt_number(rayjoin["pip"]["phase_ms"]["candidate_write_median_ms"]),
                download=_fmt_number(rayjoin["pip"]["phase_ms"]["candidate_download_median_ms"]),
                refine=_fmt_number(rayjoin["pip"]["phase_ms"]["exact_refine_median_ms"]),
            ),
            "",
            "## V2.13 Goals",
            "",
            "| Priority | Goal | Deliverable | Acceptance gate |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for goal in payload["roadmap_goals"]:
        gate = " ".join(goal["acceptance_gate"])
        lines.append(
            "| {priority} | `{goal_id}`: {title} | {deliverable} | {gate} |".format(
                priority=goal["priority"],
                goal_id=goal["id"],
                title=goal["title"],
                deliverable=goal["deliverable"],
                gate=gate,
            )
        )

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
            "## Completion Contract",
            "",
            (
                "v2.13 is done only when the RayJoin authors-code comparison, PIP optimization or "
                "phase-level explanation, Embree fairness hardening, human-scale timing packet, and "
                "public wording packet all pass. A row with an unexplained speedup is a failed row, "
                "not an excuse."
            ),
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"
