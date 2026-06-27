#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time
from typing import Any

try:
    from goal2626_benchmark_embree_optix_baseline import BenchmarkCase
    from goal2626_benchmark_embree_optix_baseline import _base_env
    from goal2626_benchmark_embree_optix_baseline import _py
    from goal2626_benchmark_embree_optix_baseline import collect_environment_probe
    from goal2626_benchmark_embree_optix_baseline import compute_ratios
    from goal2626_benchmark_embree_optix_baseline import run_case
    from goal2626_benchmark_embree_optix_baseline import build_cases as build_goal2626_cases
    from goal2636_strengthen_benchmark_rows import build_cases as build_goal2636_cases
except ModuleNotFoundError:  # pragma: no cover - package import path under unittest
    from scripts.goal2626_benchmark_embree_optix_baseline import BenchmarkCase
    from scripts.goal2626_benchmark_embree_optix_baseline import _base_env
    from scripts.goal2626_benchmark_embree_optix_baseline import _py
    from scripts.goal2626_benchmark_embree_optix_baseline import collect_environment_probe
    from scripts.goal2626_benchmark_embree_optix_baseline import compute_ratios
    from scripts.goal2626_benchmark_embree_optix_baseline import run_case
    from scripts.goal2626_benchmark_embree_optix_baseline import build_cases as build_goal2626_cases
    from scripts.goal2636_strengthen_benchmark_rows import build_cases as build_goal2636_cases


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_claim_grade_all_benchmarks_20260620"

PROMOTED_APPS = (
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
    "contact_manifold",
)

APP_POLICY: dict[str, dict[str, str]] = {
    "hausdorff_xhd": {
        "contract": "same prepared fixed-radius threshold decision",
        "claim_status": "candidate_row_scoped_optix_speedup_if_passes",
        "public_boundary": "Decision subproblem only; not full exact Hausdorff witness materialization.",
    },
    "spatial_rayjoin": {
        "contract": "authored non-tiny tiled PIP/LSI/overlay scalar-count routes",
        "claim_status": "qualified_route_speedup_not_whole_rayjoin",
        "public_boundary": "Derived tiled rows only; not full RayJoin paper reproduction or polygon overlay materialization.",
    },
    "rt_dbscan": {
        "contract": "cluster signature on clustered 3-D fixed-radius workload",
        "claim_status": "candidate_route_speedup_with_cupy_partner_gate",
        "public_boundary": "Cluster-signature route, not a full paper reproduction claim.",
    },
    "robot_collision": {
        "contract": "prepared collision-flag query over scaled poses and obstacles",
        "claim_status": "candidate_row_scoped_optix_speedup_if_passes",
        "public_boundary": "Collision flags only; not a full robot-planning system benchmark.",
    },
    "raydb_style": {
        "contract": "grouped count/sum query over repeated records",
        "claim_status": "candidate_route_speedup_with_torch_partner_gate",
        "public_boundary": "Partner-resident query route; requires Torch CUDA gate.",
    },
    "barnes_hut": {
        "contract": "node-coverage threshold decision",
        "claim_status": "candidate_row_scoped_optix_speedup_if_passes",
        "public_boundary": "Node-coverage subproblem only; not full force aggregation.",
    },
    "librts_spatial_index": {
        "contract": "generic prepared AABB index count-only route",
        "claim_status": "measured_negative_or_unproven_until_same_contract_win_exists",
        "public_boundary": "Generic RTDL AABB-index route, not LibRTS authors-code or paper-equivalent dataset timing.",
    },
    "rtnn": {
        "contract": "3-D ranked nearest-neighbor summary",
        "claim_status": "distribution_specific_candidate",
        "public_boundary": "Distribution-sensitive; uniform rows may not favor OptiX.",
    },
    "triangle_counting": {
        "contract": "RT-Graph 2A1 triangle-summary backend-query subpath",
        "claim_status": "candidate_row_scoped_optix_speedup_if_passes",
        "public_boundary": "Synthetic K4/clique ladder; not a full graph-database or paper-dataset reproduction.",
    },
    "contact_manifold": {
        "contract": "generic 2-D AABB broadphase collect-k",
        "claim_status": "candidate_row_scoped_optix_speedup_if_passes",
        "public_boundary": "Broadphase collect-k only; not a full physics/contact solver.",
    },
}


def _select_goal2626_calibrated(artifact_dir: Path) -> list[BenchmarkCase]:
    selected_apps = {"rt_dbscan", "robot_collision", "raydb_style", "contact_manifold"}
    return [case for case in build_goal2626_cases("standard", artifact_dir) if case.app_id in selected_apps]


def _select_goal2636_calibrated(artifact_dir: Path) -> list[BenchmarkCase]:
    stress_apps = {"hausdorff_xhd", "spatial_rayjoin", "barnes_hut", "triangle_counting"}
    standard_apps = {"rtnn"}
    return [
        *(case for case in build_goal2636_cases("stress", artifact_dir) if case.app_id in stress_apps),
        *(case for case in build_goal2636_cases("standard", artifact_dir) if case.app_id in standard_apps),
    ]


def _librts_large_cases() -> list[BenchmarkCase]:
    app = "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py"
    common = (
        "--dataset",
        "uniform",
        "--box-count",
        "32768",
        "--query-count",
        "32768",
        "--operation",
        "all",
        "--repeat",
        "5",
        "--warmup",
        "2",
        "--skip-counts",
    )
    return [
        BenchmarkCase(
            case_id="librts_embree_aabb_index_large_32768",
            app_id="librts_spatial_index",
            app_name="LibRTS-style spatial index",
            comparison_group="aabb_index_all_count_only_large_32768",
            backend="embree",
            command=_py(app, "--mode", "embree_aabb_index", *common),
            primary_metric_path=("run_phases", "query_median_sec"),
            notes=(
                "Large synthetic same-contract generic AABB-index route. This is not LibRTS authors-code "
                "or a paper-equivalent dataset."
            ),
        ),
        BenchmarkCase(
            case_id="librts_optix_aabb_index_large_32768",
            app_id="librts_spatial_index",
            app_name="LibRTS-style spatial index",
            comparison_group="aabb_index_all_count_only_large_32768",
            backend="optix",
            command=_py(app, "--mode", "optix_aabb_index", *common),
            primary_metric_path=("run_phases", "query_median_sec"),
            notes=(
                "Large synthetic same-contract generic AABB-index route. This is not LibRTS authors-code "
                "or a paper-equivalent dataset."
            ),
        ),
    ]


def build_cases(artifact_dir: Path) -> tuple[BenchmarkCase, ...]:
    cases = [
        *_select_goal2636_calibrated(artifact_dir),
        *_select_goal2626_calibrated(artifact_dir),
        *_librts_large_cases(),
    ]
    order = {app: index for index, app in enumerate(PROMOTED_APPS)}
    return tuple(sorted(cases, key=lambda case: (order[case.app_id], case.comparison_group, case.backend, case.case_id)))


def _case_count_by_app(cases: tuple[BenchmarkCase, ...]) -> dict[str, int]:
    counts = {app: 0 for app in PROMOTED_APPS}
    for case in cases:
        counts[case.app_id] += 1
    return counts


def _annotate_ratio(ratio: dict[str, Any]) -> dict[str, Any]:
    app_id = str(ratio["app_id"])
    speedup = float(ratio["optix_speedup_vs_embree"])
    metric_sources = ratio.get("metric_sources", {})
    same_metric_source = metric_sources.get("embree") == metric_sources.get("optix")
    policy = APP_POLICY[app_id]
    if speedup <= 1.0:
        verdict = "negative_or_mixed_no_speedup_claim"
    elif not same_metric_source and app_id == "spatial_rayjoin":
        verdict = "qualified_hot_route_not_whole_app_claim"
    elif app_id in {"rt_dbscan", "raydb_style"}:
        verdict = "partner_gated_route_speedup_candidate"
    else:
        verdict = "row_scoped_speedup_candidate"
    return {
        **ratio,
        "same_metric_source": same_metric_source,
        "claim_status": policy["claim_status"],
        "public_boundary": policy["public_boundary"],
        "verdict": verdict,
        "public_speedup_claim_authorized": False,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# V3 Claim-Grade All-Benchmark OptiX vs Embree Run",
        "",
        "Status: serious V3 evidence candidate, not release authorization.",
        "",
        "This artifact is the V3 rebuild answer to: can every promoted benchmark app",
        "be evaluated with a non-toy OptiX-vs-Embree route that a user can inspect?",
        "",
        "Rules for this run:",
        "",
        "- all ten promoted benchmark apps are included;",
        "- tiny sanity fixtures are excluded from headline speedup rows;",
        "- every row records the exact command and raw JSON payload;",
        "- `public_speedup_claim_authorized` stays false until external review;",
        "- negative and mixed rows remain visible.",
        "- scales are calibrated per app so one CPU-heavy baseline cannot block the all-app suite.",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Artifact directory: `{payload['artifact_dir']}`",
        f"- Case repeat wrapper: `{payload['case_repeat']}`",
        f"- Timeout seconds: `{payload['timeout_sec']}`",
        "",
        "## App Coverage",
        "",
        "| App | Case count | Contract | Boundary |",
        "| --- | ---: | --- | --- |",
    ]
    for app in PROMOTED_APPS:
        policy = APP_POLICY[app]
        lines.append(
            f"| `{app}` | {payload['case_count_by_app'][app]} | {policy['contract']} | {policy['public_boundary']} |"
        )

    lines.extend(
        [
            "",
            "## Ratios",
            "",
            "| App | Row group | Embree sec | OptiX sec | OptiX speedup vs Embree | Verdict | Metric source |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for ratio in payload["annotated_ratios"]:
        lines.append(
            "| {app} | {group} | {embree:.6g} | {optix:.6g} | {speedup:.3f}x | {verdict} | `{sources}` |".format(
                app=ratio["app_id"],
                group=ratio["comparison_group"],
                embree=float(ratio["embree_sec"]),
                optix=float(ratio["optix_sec"]),
                speedup=float(ratio["optix_speedup_vs_embree"]),
                verdict=ratio["verdict"],
                sources=json.dumps(ratio["metric_sources"], sort_keys=True),
            )
        )
    if not payload["annotated_ratios"]:
        lines.append("| n/a | n/a | n/a | n/a | n/a | no successful pairs | n/a |")

    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| App | Case | Backend | Status | Primary sec | Metric source |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in payload["rows"]:
        primary = row.get("primary_metric_sec")
        primary_text = "" if primary is None else f"{float(primary):.6g}"
        source = row.get("primary_metric_source") or row.get("unsupported_reason") or row.get("stage") or ""
        lines.append(
            f"| `{row['app_id']}` | `{row['case_id']}` | `{row['backend']}` | {row['status']} | {primary_text} | `{source}` |"
        )

    failures = [row for row in payload["rows"] if row.get("status") != "ok"]
    lines.extend(["", "## Failures", ""])
    if failures:
        for row in failures:
            lines.append(f"- `{row['case_id']}`: `{row.get('status')}` / `{row.get('stage', '')}`")
    else:
        lines.append("No failed rows in this run.")

    lines.extend(
        [
            "",
            "## Release Boundary",
            "",
            "This run may support row-scoped candidate wording after review. It does not",
            "authorize broad V3 speedup wording, paper reproduction wording, automatic",
            "backend choice, or release publication.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_outputs(payload: dict[str, Any], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "summary.md").write_text(_render_markdown(payload) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the V3 all-benchmark claim-grade OptiX-vs-Embree suite.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--case-repeat", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=1800)
    parser.add_argument("--only-app", action="append", default=[])
    parser.add_argument("--only-case", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    env = _base_env()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    cases = build_cases(args.artifact_dir)
    if args.only_app:
        allowed_apps = set(args.only_app)
        cases = tuple(case for case in cases if case.app_id in allowed_apps)
    if args.only_case:
        allowed_cases = set(args.only_case)
        cases = tuple(case for case in cases if case.case_id in allowed_cases)

    rows: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        print(f"[v3-claim-grade] {index}/{len(cases)} {case.app_id}/{case.case_id} ({case.backend})", flush=True)
        rows.append(
            run_case(
                case,
                env=env,
                timeout_sec=args.timeout_sec,
                repeat=args.case_repeat,
                dry_run=args.dry_run,
            )
        )

    ratios = compute_ratios(rows)
    annotated = [_annotate_ratio(ratio) for ratio in ratios]
    ok_metrics = [
        float(row["primary_metric_sec"])
        for row in rows
        if row.get("status") == "ok" and isinstance(row.get("primary_metric_sec"), (int, float))
    ]
    payload: dict[str, Any] = {
        "tool": "v3_claim_grade_all_benchmarks",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact_dir": str(args.artifact_dir),
        "case_repeat": args.case_repeat,
        "timeout_sec": args.timeout_sec,
        "dry_run": args.dry_run,
        "promoted_apps": list(PROMOTED_APPS),
        "case_count_by_app": _case_count_by_app(cases),
        "environment": collect_environment_probe(env) if not args.dry_run else {"repo_root": str(ROOT)},
        "rows": rows,
        "ratios": ratios,
        "annotated_ratios": annotated,
        "public_speedup_claim_authorized": False,
        "release_authorized": False,
        "claim_policy": APP_POLICY,
    }
    if ok_metrics:
        payload["primary_metric_summary"] = {
            "count": len(ok_metrics),
            "median_sec": statistics.median(ok_metrics),
            "max_sec": max(ok_metrics),
        }
    _write_outputs(payload, args.artifact_dir)
    print(f"[v3-claim-grade] wrote {args.artifact_dir / 'summary.json'}", flush=True)
    print(f"[v3-claim-grade] wrote {args.artifact_dir / 'summary.md'}", flush=True)
    failures = [row for row in rows if row.get("status") != "ok"]
    return 0 if args.dry_run or not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
