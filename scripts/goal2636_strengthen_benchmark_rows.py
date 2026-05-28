#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any

try:
    from goal2626_benchmark_embree_optix_baseline import BenchmarkCase
    from goal2626_benchmark_embree_optix_baseline import _base_env
    from goal2626_benchmark_embree_optix_baseline import _py
    from goal2626_benchmark_embree_optix_baseline import collect_environment_probe
    from goal2626_benchmark_embree_optix_baseline import compute_ratios
    from goal2626_benchmark_embree_optix_baseline import run_case
except ModuleNotFoundError:  # pragma: no cover - import path differs under unittest
    from scripts.goal2626_benchmark_embree_optix_baseline import BenchmarkCase
    from scripts.goal2626_benchmark_embree_optix_baseline import _base_env
    from scripts.goal2626_benchmark_embree_optix_baseline import _py
    from scripts.goal2626_benchmark_embree_optix_baseline import collect_environment_probe
    from scripts.goal2626_benchmark_embree_optix_baseline import compute_ratios
    from scripts.goal2626_benchmark_embree_optix_baseline import run_case


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2636_strengthened_rows_pod"

WEAK_ROW_APPS = (
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rtnn",
    "barnes_hut",
    "triangle_counting",
)


def _values(tier: str, *, smoke: tuple[int, ...], standard: tuple[int, ...], stress: tuple[int, ...]) -> tuple[int, ...]:
    if tier == "smoke":
        return smoke
    if tier == "standard":
        return standard
    if tier == "stress":
        return stress
    raise ValueError(f"unknown tier: {tier}")


def _case_json_path(artifact_dir: Path, case_id: str) -> Path:
    return artifact_dir / f"{case_id}.json"


def _hausdorff_cases(tier: str, artifact_dir: Path) -> list[BenchmarkCase]:
    app = "examples/v2_0/research_benchmarks/hausdorff_xhd"
    cases: list[BenchmarkCase] = []
    for copies in _values(
        tier,
        smoke=(128,),
        standard=(4096, 16384, 65536),
        stress=(16384, 65536, 262144),
    ):
        group = f"hausdorff_threshold_copies_{copies}"
        cases.extend(
            [
                BenchmarkCase(
                    case_id=f"hausdorff_embree_threshold_copies_{copies}",
                    app_id="hausdorff_xhd",
                    app_name="Hausdorff / X-HD-style",
                    comparison_group=group,
                    backend="embree",
                    command=_py(
                        f"{app}/rtdl_hausdorff_distance_app.py",
                        "--backend",
                        "embree",
                        "--copies",
                        copies,
                        "--optix-summary-mode",
                        "directed_threshold_prepared",
                        "--hausdorff-threshold",
                        "0.4",
                    ),
                    primary_metric_path=("run_phases", "query_fixed_radius_threshold_reached_count_sec"),
                    notes="Scale ladder for the same prepared threshold-decision contract as Goal2634.",
                ),
                BenchmarkCase(
                    case_id=f"hausdorff_optix_threshold_copies_{copies}",
                    app_id="hausdorff_xhd",
                    app_name="Hausdorff / X-HD-style",
                    comparison_group=group,
                    backend="optix",
                    command=_py(
                        f"{app}/rtdl_hausdorff_distance_app.py",
                        "--backend",
                        "optix",
                        "--copies",
                        copies,
                        "--optix-summary-mode",
                        "directed_threshold_prepared",
                        "--hausdorff-threshold",
                        "0.4",
                        "--require-rt-core",
                    ),
                    primary_metric_path=("run_phases", "query_fixed_radius_threshold_reached_count_sec"),
                    notes="Scale ladder for the same prepared threshold-decision contract as Goal2634.",
                ),
            ]
        )
    for points in _values(
        tier,
        smoke=(256,),
        standard=(8192, 32768),
        stress=(32768, 131072),
    ):
        cases.append(
            BenchmarkCase(
                case_id=f"hausdorff_optix_exact_grouped_seeded_pruned_points_{points}",
                app_id="hausdorff_xhd",
                app_name="Hausdorff / X-HD-style",
                comparison_group=f"hausdorff_exact_witness_points_{points}",
                backend="optix",
                command=_py(
                    f"{app}/rtdl_hausdorff_v2_function.py",
                    "--points-a",
                    points,
                    "--points-b",
                    points,
                    "--method",
                    "rtdl_rt_grouped_seeded_pruned_nearest_witness",
                    "--seed-sample-count",
                    min(points, 8192),
                    "--json-out",
                    _case_json_path(artifact_dir, f"hausdorff_optix_exact_grouped_seeded_pruned_points_{points}"),
                ),
                json_out=_case_json_path(artifact_dir, f"hausdorff_optix_exact_grouped_seeded_pruned_points_{points}"),
                primary_metric_path=("primary", "elapsed_sec"),
                notes=(
                    "Exact witness OptiX-only ladder. It validates the stronger Hausdorff path, "
                    "but it is not ratioed against Embree because there is no same exact-witness Embree route."
                ),
            )
        )
    return cases


def _rayjoin_cases(tier: str, _artifact_dir: Path) -> list[BenchmarkCase]:
    app = "examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
    tile_suffix = {"smoke": "x64", "standard": "x512", "stress": "x2048"}[tier]
    workloads = (
        ("pip", f"derived/authored_pip_square_tiled_{tile_suffix}"),
        ("lsi", f"derived/authored_lsi_crossing_tiled_{tile_suffix}"),
        ("overlay_seed", f"derived/authored_overlay_squares_tiled_{tile_suffix}"),
    )
    cases: list[BenchmarkCase] = []
    for workload, dataset in workloads:
        group = f"rayjoin_{workload}_authored_tiled_{tile_suffix}"
        cases.extend(
            [
                BenchmarkCase(
                    case_id=f"rayjoin_embree_{workload}_tiled_{tile_suffix}",
                    app_id="spatial_rayjoin",
                    app_name="Spatial RayJoin-style",
                    comparison_group=group,
                    backend="embree",
                    command=_py(
                        app,
                        "--workload",
                        workload,
                        "--backend",
                        "embree",
                        "--dataset",
                        dataset,
                        "--no-rows",
                    ),
                    primary_metric_path=("elapsed_sec",),
                    notes=(
                        "Authored nonzero tiled workload to avoid the tiny/zero-row all-route fixture. "
                        "Rows are omitted; summary/count contract remains checked by the app."
                    ),
                ),
                BenchmarkCase(
                    case_id=f"rayjoin_optix_prepared_{workload}_tiled_{tile_suffix}",
                    app_id="spatial_rayjoin",
                    app_name="Spatial RayJoin-style",
                    comparison_group=group,
                    backend="optix",
                    command=_py(
                        app,
                        "--workload",
                        workload,
                        "--execution-route",
                        "prepared_optix",
                        "--result-mode",
                        "count",
                        "--dataset",
                        dataset,
                        "--no-rows",
                    ),
                    primary_metric_path=("phases_sec", "prepared_query_sec"),
                    notes=(
                        "Prepared OptiX per-workload route over nontrivial authored tiled data. "
                        "This is still not full polygon overlay materialization."
                    ),
                ),
            ]
        )
    return cases


def _rtnn_cases(tier: str, artifact_dir: Path) -> list[BenchmarkCase]:
    runner = "scripts/goal2348_rtnn_v2_2_external_runner.py"
    distributions = ("uniform",) if tier == "smoke" else ("uniform", "clustered", "shell")
    point_counts = _values(tier, smoke=(4096,), standard=(65536,), stress=(65536, 262144))
    cases: list[BenchmarkCase] = []
    for point_count in point_counts:
        for distribution in distributions:
            point_file = artifact_dir / f"rtnn_{distribution}_{point_count}.csv"
            gen_json = artifact_dir / f"rtnn_generate_{distribution}_{point_count}.json"
            setup = (
                _py(
                    runner,
                    "generate",
                    "--point-file",
                    point_file,
                    "--point-count",
                    point_count,
                    "--dimension",
                    3,
                    "--distribution",
                    distribution,
                    "--json-out",
                    gen_json,
                ),
            )
            group = f"rtnn_{distribution}_{point_count}_ranked_summary"
            for backend in ("embree", "optix"):
                case_id = f"rtnn_{backend}_{distribution}_{point_count}_ranked_summary"
                cases.append(
                    BenchmarkCase(
                        case_id=case_id,
                        app_id="rtnn",
                        app_name="RTNN neighbor search",
                        comparison_group=group,
                        backend=backend,
                        setup_commands=setup,
                        command=_py(
                            runner,
                            "run-rtdl-batched-3d-neighbors",
                            "--point-file",
                            point_file,
                            "--radius",
                            "0.02",
                            "--k-max",
                            "50",
                            "--backend",
                            backend,
                            "--query-batch-size",
                            min(point_count, 65536),
                            "--result-mode",
                            "ranked-summary-raw",
                            "--repeat",
                            "3",
                            "--json-out",
                            _case_json_path(artifact_dir, case_id),
                        ),
                        json_out=_case_json_path(artifact_dir, case_id),
                        primary_metric_path=("elapsed_sec",),
                        notes=(
                            "Distribution ladder for the prepared 3-D ranked-summary contract. "
                            "Clustered rows are the density-risk check."
                        ),
                    )
                )
    return cases


def _barnes_hut_cases(tier: str, _artifact_dir: Path) -> list[BenchmarkCase]:
    app = "examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
    cases: list[BenchmarkCase] = []
    for body_count in _values(tier, smoke=(1024,), standard=(8192, 32768), stress=(32768, 131072)):
        group = f"barnes_hut_node_coverage_bodies_{body_count}"
        cases.extend(
            [
                BenchmarkCase(
                    case_id=f"barnes_hut_embree_node_coverage_bodies_{body_count}",
                    app_id="barnes_hut",
                    app_name="Barnes-Hut / RT-BarnesHut-style",
                    comparison_group=group,
                    backend="embree",
                    command=_py(
                        app,
                        "--mode",
                        "embree_node_coverage_prepared",
                        "--body-count",
                        body_count,
                        "--skip-validation",
                    ),
                    primary_metric_path=("node_coverage", "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
                    notes="Same-contract node-coverage scale ladder; not full force aggregation.",
                ),
                BenchmarkCase(
                    case_id=f"barnes_hut_optix_node_coverage_bodies_{body_count}",
                    app_id="barnes_hut",
                    app_name="Barnes-Hut / RT-BarnesHut-style",
                    comparison_group=group,
                    backend="optix",
                    command=_py(
                        app,
                        "--mode",
                        "optix_node_coverage_prepared",
                        "--body-count",
                        body_count,
                        "--skip-validation",
                        "--require-rt-core",
                    ),
                    primary_metric_path=("node_coverage", "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
                    notes="Same-contract node-coverage scale ladder; not full force aggregation.",
                ),
            ]
        )
    return cases


def _triangle_cases(tier: str, artifact_dir: Path) -> list[BenchmarkCase]:
    app = "examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
    cases: list[BenchmarkCase] = []
    for cliques in _values(tier, smoke=(16,), standard=(5000, 20000), stress=(20000, 80000)):
        edge_file = artifact_dir / f"triangle_k4_cliques_{cliques}.edge"
        setup = (
            _py(
                "scripts/goal2631_generate_triangle_k4_binary.py",
                "--output",
                edge_file,
                "--cliques",
                cliques,
            ),
        )
        group = f"triangle_count_rt_graph_2a1_cliques_{cliques}"
        cases.extend(
            [
                BenchmarkCase(
                    case_id=f"triangle_counting_embree_rt_graph_2a1_cliques_{cliques}",
                    app_id="triangle_counting",
                    app_name="Triangle counting",
                    comparison_group=group,
                    backend="embree",
                    setup_commands=setup,
                    command=_py(
                        app,
                        "--mode",
                        "rt_graph_2a1_generic_rt",
                        "--backend",
                        "embree",
                        "--edge-file",
                        edge_file,
                        "--edge-format",
                        "binary",
                        "--detail",
                        "summary",
                        "--warmup",
                        "2",
                        "--repeat",
                        "12",
                    ),
                    primary_metric_path=("timing_ms", "query_median_ms"),
                    notes="Synthetic K4 scale ladder for the generic RT-Graph 2A1 backend-query subpath.",
                ),
                BenchmarkCase(
                    case_id=f"triangle_counting_optix_rt_graph_2a1_cliques_{cliques}",
                    app_id="triangle_counting",
                    app_name="Triangle counting",
                    comparison_group=group,
                    backend="optix",
                    setup_commands=setup,
                    command=_py(
                        app,
                        "--mode",
                        "rt_graph_2a1_generic_rt",
                        "--backend",
                        "optix",
                        "--edge-file",
                        edge_file,
                        "--edge-format",
                        "binary",
                        "--detail",
                        "summary",
                        "--partner",
                        "cupy",
                        "--warmup",
                        "2",
                        "--repeat",
                        "12",
                    ),
                    primary_metric_path=("timing_ms", "query_median_ms"),
                    notes=(
                        "Synthetic K4 scale ladder for the generic RT-Graph 2A1 backend-query subpath. "
                        "Paper datasets still need segmented/streamed lowering."
                    ),
                ),
            ]
        )
    return cases


def build_cases(tier: str, artifact_dir: Path) -> tuple[BenchmarkCase, ...]:
    return tuple(
        [
            *_hausdorff_cases(tier, artifact_dir),
            *_rayjoin_cases(tier, artifact_dir),
            *_rtnn_cases(tier, artifact_dir),
            *_barnes_hut_cases(tier, artifact_dir),
            *_triangle_cases(tier, artifact_dir),
        ]
    )


def _filter_cases(
    cases: tuple[BenchmarkCase, ...],
    *,
    only_app: tuple[str, ...],
    only_case: tuple[str, ...],
) -> tuple[BenchmarkCase, ...]:
    selected = cases
    if only_app:
        allowed = set(only_app)
        selected = tuple(case for case in selected if case.app_id in allowed)
    if only_case:
        allowed_cases = set(only_case)
        selected = tuple(case for case in selected if case.case_id in allowed_cases)
    return selected


def _render_markdown(payload: dict[str, Any]) -> str:
    rows = payload["rows"]
    ratios = payload["ratios"]
    lines = [
        "# Goal2636 Strengthened Benchmark Rows",
        "",
        "This artifact strengthens the weaker Goal2634 rows with scale ladders or larger fixtures.",
        "It is internal engineering evidence only, not public speedup wording.",
        "",
        f"- Tier: `{payload['tier']}`",
        f"- Case repeat: `{payload['case_repeat']}`",
        f"- Generated: `{payload['generated_at']}`",
        "",
        "## Ratios",
        "",
        "| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for ratio in ratios:
        lines.append(
            "| {app} | {group} | {embree:.6g} | {optix:.6g} | {speedup:.3g}x | `{sources}` |".format(
                app=ratio["app_id"],
                group=ratio["comparison_group"],
                embree=ratio["embree_sec"],
                optix=ratio["optix_sec"],
                speedup=ratio["optix_speedup_vs_embree"],
                sources=json.dumps(ratio["metric_sources"], sort_keys=True),
            )
        )
    if not ratios:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| App | Case | Backend | Status | Primary sec | Source or reason |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in rows:
        primary = row.get("primary_metric_sec")
        primary_text = "n/a" if primary is None else f"{float(primary):.6g}"
        source = row.get("primary_metric_source") or row.get("unsupported_reason") or row.get("stage") or ""
        lines.append(
            f"| {row['app_id']} | {row['case_id']} | {row['backend']} | "
            f"{row['status']} | {primary_text} | `{source}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Hausdorff exact-witness rows are OptiX-only and are not ratioed.",
            "- Spatial RayJoin rows use derived tiled fixtures, but still do not materialize full polygon overlay.",
            "- RTNN rows are distribution-sensitive; clustered rows are the density-risk signal.",
            "- Barnes-Hut rows are node-coverage only, not force aggregation.",
            "- Triangle-counting rows are synthetic RT-2A1 backend-query ladders; paper datasets still require segmented/streamed lowering.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_outputs(payload: dict[str, Any], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "summary.md").write_text(_render_markdown(payload), encoding="utf-8")


def _run_process(command: tuple[str, ...], *, env: dict[str, str], timeout_sec: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        check=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run strengthened scale/workload rows for weak Goal2634 benchmark apps.")
    parser.add_argument("--tier", choices=("smoke", "standard", "stress"), default="standard")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--case-repeat", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=1200)
    parser.add_argument("--only-app", action="append", default=[])
    parser.add_argument("--only-case", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--build-native", action="store_true")
    args = parser.parse_args(argv)

    env = _base_env()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    if args.build_native and not args.dry_run:
        for command in (("make", "build-embree"), ("make", "build-optix")):
            completed = _run_process(command, env=env, timeout_sec=args.timeout_sec)
            if completed.returncode != 0:
                print(completed.stdout, end="")
                print(completed.stderr, end="", file=sys.stderr)
                return completed.returncode
        env = _base_env()

    cases = _filter_cases(
        build_cases(args.tier, args.artifact_dir),
        only_app=tuple(args.only_app),
        only_case=tuple(args.only_case),
    )
    rows: list[dict[str, Any]] = []
    for case in cases:
        print(f"[goal2636] {case.case_id} ({case.backend})", flush=True)
        rows.append(
            run_case(
                case,
                env=env,
                timeout_sec=args.timeout_sec,
                repeat=args.case_repeat,
                dry_run=args.dry_run,
            )
        )

    payload: dict[str, Any] = {
        "runner": "goal2636_strengthen_benchmark_rows",
        "tier": args.tier,
        "case_repeat": args.case_repeat,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "weak_row_apps": list(WEAK_ROW_APPS),
        "environment": collect_environment_probe(env),
        "rows": rows,
        "ratios": compute_ratios(rows),
    }
    ok_metrics = [
        float(row["primary_metric_sec"])
        for row in rows
        if row.get("status") == "ok" and row.get("primary_metric_sec") is not None
    ]
    if ok_metrics:
        payload["primary_metric_summary"] = {
            "count": len(ok_metrics),
            "median_sec": statistics.median(ok_metrics),
            "max_sec": max(ok_metrics),
        }
    _write_outputs(payload, args.artifact_dir)
    print(f"[goal2636] wrote {args.artifact_dir / 'summary.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
