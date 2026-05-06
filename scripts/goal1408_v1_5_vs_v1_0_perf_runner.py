#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "reports" / "goal1408_v1_5_vs_v1_0_perf"
DEFAULT_V1_0_WORKTREE = ROOT / "build" / "goal1408_v1_0_worktree"


@dataclass(frozen=True)
class Profile:
    app: str
    backend: str
    command_template: tuple[str, ...]
    metric_hints: tuple[str, ...]
    boundary: str


PROFILES: tuple[Profile, ...] = (
    Profile(
        "database_analytics",
        "embree",
        (
            "python3",
            "scripts/goal756_db_prepared_session_perf.py",
            "--backend",
            "embree",
            "--scenario",
            "sales_risk",
            "--copies",
            "{copies}",
            "--iterations",
            "{iterations}",
            "--output-mode",
            "compact_summary",
            "--output-json",
            "{output_json}",
        ),
        ("median_sec", "query", "compact"),
        "DB compact-summary only; no SQL/DBMS or row-materialization speedup claim.",
    ),
    Profile(
        "database_analytics",
        "optix",
        (
            "python3",
            "scripts/goal756_db_prepared_session_perf.py",
            "--backend",
            "optix",
            "--scenario",
            "sales_risk",
            "--copies",
            "{copies}",
            "--iterations",
            "{iterations}",
            "--output-mode",
            "compact_summary",
            "--output-json",
            "{output_json}",
        ),
        ("median_sec", "query", "compact"),
        "DB compact-summary only; no SQL/DBMS or row-materialization speedup claim.",
    ),
    Profile(
        "graph_analytics",
        "optix",
        (
            "python3",
            "scripts/goal889_graph_visibility_optix_gate.py",
            "--copies",
            "{copies}",
            "--output-mode",
            "summary",
            "--validation-mode",
            "analytic_summary",
            "--chunk-copies",
            "0",
            "--strict",
            "--output-json",
            "{output_json}",
        ),
        ("optix", "query", "median_sec"),
        "Graph visibility/count subpath only; graph-system analytics remain outside.",
    ),
    Profile(
        "service_coverage_gaps",
        "embree",
        (
            "python3",
            "scripts/goal724_service_coverage_summary_perf.py",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("gap_summary_sec",),
        "Service coverage gap summary only; no whole service-optimization claim.",
    ),
    Profile(
        "event_hotspot_screening",
        "embree",
        (
            "python3",
            "scripts/goal723_event_hotspot_summary_perf.py",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("count_summary_sec",),
        "Hotspot count summary only; no whole hotspot-analytics claim.",
    ),
    Profile(
        "facility_knn_assignment",
        "embree",
        (
            "python3",
            "scripts/goal730_facility_knn_compact_output_perf.py",
            "--backend",
            "embree",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Coverage-threshold/compact output only; ranked KNN remains outside.",
    ),
    Profile(
        "facility_knn_assignment",
        "optix",
        (
            "python3",
            "scripts/goal887_prepared_decision_phase_profiler.py",
            "--scenario",
            "facility_service_coverage",
            "--mode",
            "optix",
            "--copies",
            "{copies}",
            "--iterations",
            "{iterations}",
            "--radius",
            "1.0",
            "--skip-validation",
            "--output-json",
            "{output_json}",
        ),
        ("optix_query_sec.median_sec",),
        "Prepared facility coverage-threshold query only; ranked KNN remains outside.",
    ),
    Profile(
        "road_hazard_screening",
        "embree",
        (
            "python3",
            "scripts/goal729_road_hazard_compact_output_perf.py",
            "--backend",
            "embree",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Compact hazard summary only; GIS/routing and default-app behavior remain outside.",
    ),
    Profile(
        "road_hazard_screening",
        "optix",
        (
            "python3",
            "scripts/goal729_road_hazard_compact_output_perf.py",
            "--backend",
            "optix",
            "--optix-mode",
            "native",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Compact hazard summary only; GIS/routing and default-app behavior remain outside.",
    ),
    Profile(
        "segment_polygon_hitcount",
        "embree",
        (
            "python3",
            "scripts/goal726_segment_polygon_compact_summary_perf.py",
            "--backend",
            "embree",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Compact hit-count summary only; pair-row output remains outside.",
    ),
    Profile(
        "segment_polygon_hitcount",
        "optix",
        (
            "python3",
            "scripts/goal726_segment_polygon_compact_summary_perf.py",
            "--backend",
            "optix",
            "--optix-mode",
            "native",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Compact hit-count summary only; pair-row output remains outside.",
    ),
    Profile(
        "polygon_pair_overlap_area_rows",
        "embree",
        (
            "python3",
            "scripts/goal732_polygon_pair_summary_output_perf.py",
            "--backend",
            "embree",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Candidate discovery plus exact-area summary only; broad polygon overlay remains outside.",
    ),
    Profile(
        "polygon_pair_overlap_area_rows",
        "optix",
        (
            "python3",
            "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
            "--app",
            "pair_overlap",
            "--mode",
            "optix",
            "--copies",
            "{copies}",
            "--output-mode",
            "summary",
            "--validation-mode",
            "analytic_summary",
            "--chunk-copies",
            "100",
            "--output-json",
            "{output_json}",
        ),
        ("optix", "candidate", "median_sec"),
        "Candidate discovery plus exact-area summary only; broad polygon overlay remains outside.",
    ),
    Profile(
        "hausdorff_distance",
        "embree",
        (
            "python3",
            "scripts/goal722_embree_hausdorff_summary_perf.py",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Threshold decision/directed summary only; exact Hausdorff rows remain outside.",
    ),
    Profile(
        "hausdorff_distance",
        "optix",
        (
            "python3",
            "scripts/goal887_prepared_decision_phase_profiler.py",
            "--scenario",
            "hausdorff_threshold",
            "--mode",
            "optix",
            "--copies",
            "{copies}",
            "--iterations",
            "{iterations}",
            "--radius",
            "0.4",
            "--skip-validation",
            "--output-json",
            "{output_json}",
        ),
        ("optix_query_sec.median_sec",),
        "Threshold decision only; exact Hausdorff rows remain outside.",
    ),
    Profile(
        "ann_candidate_search",
        "embree",
        (
            "python3",
            "scripts/goal735_ann_candidate_compact_output_perf.py",
            "--copies",
            "{copies}",
            "--quality-copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Candidate-coverage/compact output only; full ANN ranking/indexing remains outside.",
    ),
    Profile(
        "ann_candidate_search",
        "optix",
        (
            "python3",
            "scripts/goal887_prepared_decision_phase_profiler.py",
            "--scenario",
            "ann_candidate_coverage",
            "--mode",
            "optix",
            "--copies",
            "{copies}",
            "--iterations",
            "{iterations}",
            "--radius",
            "0.2",
            "--skip-validation",
            "--output-json",
            "{output_json}",
        ),
        ("optix_query_sec.median_sec",),
        "Candidate-coverage decision only; full ANN ranking/indexing remains outside.",
    ),
    Profile(
        "outlier_detection",
        "embree",
        (
            "python3",
            "scripts/goal718_embree_prepared_app_batch_perf.py",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--warmups",
            "1",
            "--output",
            "{output_json}",
        ),
        ("outlier.prepared_run_only.median_sec",),
        "Density count summary only; per-point labels remain outside.",
    ),
    Profile(
        "dbscan_clustering",
        "embree",
        (
            "python3",
            "scripts/goal718_embree_prepared_app_batch_perf.py",
            "--copies",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--warmups",
            "1",
            "--output",
            "{output_json}",
        ),
        ("dbscan.prepared_run_only.median_sec",),
        "Core-count summary only; cluster expansion remains outside.",
    ),
    Profile(
        "robot_collision_screening",
        "embree",
        (
            "python3",
            "scripts/goal736_robot_collision_scaled_perf.py",
            "--pose-counts",
            "{copies}",
            "--obstacle-count",
            "16",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Robot any-hit/pose summary only; full robot planning remains outside.",
    ),
    Profile(
        "robot_collision_screening",
        "optix",
        (
            "python3",
            "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
            "--mode",
            "optix",
            "--pose-count",
            "{copies}",
            "--obstacle-count",
            "16",
            "--iterations",
            "{iterations}",
            "--input-mode",
            "packed_arrays",
            "--result-mode",
            "pose_count",
            "--skip-validation",
            "--output-json",
            "{output_json}",
        ),
        ("prepared_pose_flags_warm_query_sec.median_sec", "optix_query_sec.median_sec"),
        "Prepared pose-count query only; full robot planning remains outside.",
    ),
    Profile(
        "barnes_hut_force_app",
        "embree",
        (
            "python3",
            "scripts/goal734_barnes_hut_compact_output_perf.py",
            "--body-counts",
            "{copies}",
            "--repeats",
            "{iterations}",
            "--output",
            "{output_json}",
        ),
        ("median_sec",),
        "Node-coverage/candidate summary only; force-vector reduction remains outside.",
    ),
    Profile(
        "barnes_hut_force_app",
        "optix",
        (
            "python3",
            "scripts/goal887_prepared_decision_phase_profiler.py",
            "--scenario",
            "barnes_hut_node_coverage",
            "--mode",
            "optix",
            "--body-count",
            "{copies}",
            "--iterations",
            "{iterations}",
            "--radius",
            "0.1",
            "--barnes-tree-depth",
            "4",
            "--hit-threshold",
            "4",
            "--skip-validation",
            "--output-json",
            "{output_json}",
        ),
        ("optix_query_sec.median_sec",),
        "Node-coverage decision only; force-vector reduction remains outside.",
    ),
)

EXCLUDED_APPS = {
    "apple_rt_demo": "excluded from v1.5 active Embree+OptiX scope; Apple RT frozen before v2.1",
    "hiprt_ray_triangle_hitcount": "excluded from v1.5 active Embree+OptiX scope; HIPRT frozen before v2.1",
    "polygon_set_jaccard": "excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1",
    "segment_polygon_anyhit_rows": "excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1",
}


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str], timeout_sec: int) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "elapsed_sec": time.perf_counter() - started,
            "error": f"timeout after {timeout_sec}s",
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
        }
    return {
        "status": "ok" if completed.returncode == 0 else "error",
        "returncode": completed.returncode,
        "elapsed_sec": time.perf_counter() - started,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def _git(cwd: Path, args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _ensure_v1_0_worktree(path: Path) -> None:
    if path.exists():
        if not (path / ".git").exists():
            raise ValueError(f"existing path is not a git worktree: {path}")
        _git(path, ["checkout", "--detach", "v1.0"])
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["git", "worktree", "add", "--detach", str(path), "v1.0"], cwd=ROOT)


def _format_command(profile: Profile, output_json: Path, copies: int, iterations: int) -> list[str]:
    return [
        part.format(copies=str(copies), iterations=str(iterations), output_json=str(output_json))
        for part in profile.command_template
    ]


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_numbers(value: Any, prefix: str = "") -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_walk_numbers(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            rows.extend(_walk_numbers(item, child))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        rows.append((prefix, float(value)))
    return rows


def _hint_score(path: str, hints: tuple[str, ...]) -> int:
    normalized = path.lower()
    score = 0
    for hint in hints:
        parts = tuple(part for part in hint.lower().split(".") if part)
        if hint.lower() in normalized:
            score += 20
        if all(part in normalized for part in parts):
            score += 5
    if "median_sec" in normalized:
        score += 4
    if normalized.endswith("sec") or normalized.endswith("median_sec"):
        score += 2
    if "samples" in normalized or "min_sec" in normalized or "max_sec" in normalized:
        score -= 3
    return score


def _select_metric(payload: Any, hints: tuple[str, ...]) -> dict[str, Any] | None:
    candidates = [
        (path, value)
        for path, value in _walk_numbers(payload)
        if value > 0.0 and ("sec" in path.lower() or "median" in path.lower())
    ]
    if not candidates:
        return None
    scored = sorted(
        ((_hint_score(path, hints), path, value) for path, value in candidates),
        key=lambda item: (item[0], -len(item[1])),
        reverse=True,
    )
    score, path, value = scored[0]
    return {"metric_path": path, "seconds": value, "score": score}


def _version_env(cwd: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    env["RTDL_SOURCE_COMMIT"] = _git(cwd, ["rev-parse", "HEAD"])
    return env


def _run_profile(
    profile: Profile,
    *,
    label: str,
    cwd: Path,
    output_dir: Path,
    copies: int,
    iterations: int,
    timeout_sec: int,
) -> dict[str, Any]:
    profile_dir = output_dir / label / profile.app / profile.backend
    profile_dir.mkdir(parents=True, exist_ok=True)
    output_json = profile_dir / "result.json"
    command = _format_command(profile, output_json, copies, iterations)
    run = _run(command, cwd=cwd, env=_version_env(cwd), timeout_sec=timeout_sec)
    payload = _load_json(output_json)
    metric = _select_metric(payload, profile.metric_hints) if payload is not None else None
    return {
        "label": label,
        "commit": _git(cwd, ["rev-parse", "HEAD"]),
        "app": profile.app,
        "backend": profile.backend,
        "command": command,
        "output_json": str(output_json),
        "run": run,
        "metric": metric,
        "boundary": profile.boundary,
    }


def _compare(v1_0: dict[str, Any], v1_5: dict[str, Any]) -> dict[str, Any]:
    old_metric = v1_0.get("metric")
    new_metric = v1_5.get("metric")
    if not old_metric or not new_metric:
        return {
            "status": "not_comparable",
            "reason": "missing metric from one or both versions",
        }
    old_sec = float(old_metric["seconds"])
    new_sec = float(new_metric["seconds"])
    if new_sec <= 0.0:
        return {"status": "not_comparable", "reason": "v1.5 metric is non-positive"}
    ratio = old_sec / new_sec
    if ratio > 1.05:
        classification = "v1_5_faster"
    elif ratio < 0.95:
        classification = "v1_5_slower"
    else:
        classification = "roughly_equal"
    return {
        "status": "compared",
        "v1_0_sec": old_sec,
        "v1_5_sec": new_sec,
        "v1_0_over_v1_5_ratio": ratio,
        "classification": classification,
    }


def run_suite(
    *,
    output_dir: Path,
    v1_0_worktree: Path,
    copies: int,
    iterations: int,
    timeout_sec: int,
    backends: tuple[str, ...],
    apps: tuple[str, ...],
) -> dict[str, Any]:
    _ensure_v1_0_worktree(v1_0_worktree)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_profiles = [
        profile
        for profile in PROFILES
        if profile.backend in backends and (not apps or profile.app in apps)
    ]
    rows = []
    for profile in selected_profiles:
        v1_0 = _run_profile(
            profile,
            label="v1_0",
            cwd=v1_0_worktree,
            output_dir=output_dir,
            copies=copies,
            iterations=iterations,
            timeout_sec=timeout_sec,
        )
        v1_5 = _run_profile(
            profile,
            label="v1_5",
            cwd=ROOT,
            output_dir=output_dir,
            copies=copies,
            iterations=iterations,
            timeout_sec=timeout_sec,
        )
        rows.append(
            {
                "app": profile.app,
                "backend": profile.backend,
                "boundary": profile.boundary,
                "v1_0": v1_0,
                "v1_5": v1_5,
                "comparison": _compare(v1_0, v1_5),
            }
        )
    return {
        "schema": "goal1408_v1_5_vs_v1_0_perf_v1",
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "current_commit": _git(ROOT, ["rev-parse", "HEAD"]),
        "v1_0_commit": _git(v1_0_worktree, ["rev-parse", "HEAD"]),
        "copies": copies,
        "iterations": iterations,
        "timeout_sec": timeout_sec,
        "profiles_requested": len(selected_profiles),
        "rows": rows,
        "excluded_apps": EXCLUDED_APPS,
        "boundary": (
            "Same command and same scale are run against v1.0 and current v1.5 candidate. "
            "Cells with backend errors are unavailable, not zero-speedup results. "
            "This runner does not authorize public speedup wording by itself."
        ),
    }


def _fmt_sec(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6f}"


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1408 v1.5 vs v1.0 Performance Comparison",
        "",
        f"- current commit: `{payload['current_commit']}`",
        f"- v1.0 commit: `{payload['v1_0_commit']}`",
        f"- copies: `{payload['copies']}`",
        f"- iterations: `{payload['iterations']}`",
        "",
        payload["boundary"],
        "",
        "| App | Backend | Status | v1.0 sec | v1.5 sec | v1.0/v1.5 | Boundary |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["rows"]:
        comparison = row["comparison"]
        if comparison["status"] == "compared":
            status = comparison["classification"]
            old_sec = _fmt_sec(comparison["v1_0_sec"])
            new_sec = _fmt_sec(comparison["v1_5_sec"])
            ratio = f"{float(comparison['v1_0_over_v1_5_ratio']):.3f}x"
        else:
            status = comparison["reason"]
            old_metric = row["v1_0"].get("metric") or {}
            new_metric = row["v1_5"].get("metric") or {}
            old_sec = _fmt_sec(old_metric.get("seconds"))
            new_sec = _fmt_sec(new_metric.get("seconds"))
            ratio = "n/a"
        lines.append(
            f"| `{row['app']}` | `{row['backend']}` | {status} | {old_sec} | {new_sec} | {ratio} | {row['boundary']} |"
        )
    lines.extend(["", "## Excluded Apps", ""])
    for app, reason in payload["excluded_apps"].items():
        lines.append(f"- `{app}`: {reason}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run v1.5-vs-v1.0 same-command app perf comparisons.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--v1-0-worktree", default=str(DEFAULT_V1_0_WORKTREE))
    parser.add_argument("--copies", type=int, default=512)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--apps", default="", help="Comma-separated app filter.")
    parser.add_argument("--remove-existing-v1-0-worktree", action="store_true")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    v1_0_worktree = Path(args.v1_0_worktree)
    if args.remove_existing_v1_0_worktree and v1_0_worktree.exists():
        shutil.rmtree(v1_0_worktree)
    payload = run_suite(
        output_dir=output_dir,
        v1_0_worktree=v1_0_worktree,
        copies=args.copies,
        iterations=args.iterations,
        timeout_sec=args.timeout_sec,
        backends=tuple(item for item in args.backends.split(",") if item),
        apps=tuple(item for item in args.apps.split(",") if item),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "summary.json"
    md_path = output_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "markdown": str(md_path), "rows": len(payload["rows"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
