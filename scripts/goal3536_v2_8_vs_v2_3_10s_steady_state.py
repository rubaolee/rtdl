#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3536_v2_8_vs_v2_3_10s_steady_state_pod"
DEFAULT_SEED_ARTIFACT = ROOT / "docs" / "reports" / "goal3524_pod_artifacts" / "goal3524_compact_results.json"
SCHEMA = "rtdl.goal3536.v2_8_vs_v2_3_10s_steady_state.v1"


def _claim_boundary() -> dict[str, bool]:
    return {
        "internal_results_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "package_install_claim_authorized": False,
    }


def _command_output(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _load_runner(source_root: Path, lane: str) -> ModuleType:
    path = source_root / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"
    if not path.exists():
        raise FileNotFoundError(path)
    module_name = f"goal3536_goal2626_runner_{lane}_{abs(hash(str(source_root)))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_seed_metrics(path: Path) -> dict[str, dict[str, dict[str, float]]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict[str, dict[str, float]]] = {"v23": {}, "v28": {}}
    if payload.get("schema") == SCHEMA and isinstance(payload.get("rows"), list):
        for row in payload["rows"]:
            lane = str(row.get("lane", ""))
            case_id = str(row.get("case_id", ""))
            if lane not in result or not case_id:
                continue
            execution = row.get("execution", {})
            metric = execution.get("primary_metric_sec") if isinstance(execution, dict) else None
            if isinstance(metric, (int, float)) and metric > 0:
                result[lane].setdefault(case_id, {})["primary_metric_sec"] = float(metric)
            plan = row.get("plan", {})
            wall = plan.get("seed_wall_median_sec") if isinstance(plan, dict) else None
            if isinstance(wall, (int, float)) and wall > 0:
                result[lane].setdefault(case_id, {})["wall_median_sec"] = float(wall)
        return result
    compact_inputs = payload.get("compact_inputs", {})
    for lane, key in (("v23", "v23_standard"), ("v28", "v28_standard")):
        rows = compact_inputs.get(key, {}).get("rows", [])
        for row in rows:
            if row.get("backend") != "optix":
                continue
            metric = row.get("primary_metric_sec")
            wall = row.get("wall_median_sec")
            if isinstance(metric, (int, float)) and metric > 0:
                result[lane].setdefault(str(row.get("case_id")), {})["primary_metric_sec"] = float(metric)
            if isinstance(wall, (int, float)) and wall > 0:
                result[lane].setdefault(str(row.get("case_id")), {})["wall_median_sec"] = float(wall)
    return result


def _int_after(args: tuple[str, ...], flag: str) -> int | None:
    try:
        index = args.index(flag)
    except ValueError:
        return None
    if index + 1 >= len(args):
        return None
    try:
        return int(args[index + 1])
    except ValueError:
        return None


def _replace_flag_value(args: tuple[str, ...], flag: str, value: int) -> tuple[str, ...]:
    mutable = list(args)
    try:
        index = mutable.index(flag)
    except ValueError:
        raise ValueError(f"{flag} not in command")
    if index + 1 >= len(mutable):
        raise ValueError(f"{flag} has no value")
    mutable[index + 1] = str(int(value))
    return tuple(mutable)


def _repeat_knob(args: tuple[str, ...]) -> tuple[str, int] | None:
    # Prefer the metric-specific contact knob over generic process repeat flags.
    for flag in ("--discovery-repeat", "--repeat", "--repeats", "--iterations"):
        value = _int_after(args, flag)
        if value is not None and value > 0:
            return flag, value
    return None


def _planned_case(
    case: Any,
    *,
    lane: str,
    seed_metric_sec: float | None,
    seed_wall_sec: float | None,
    target_measured_sec: float,
    repeat_safety_factor: float,
    max_internal_repeat: int,
    max_wrapper_repeat: int,
    max_estimated_wall_sec: float,
) -> dict[str, Any]:
    command = tuple(case.command or ())
    knob = _repeat_knob(command)
    seed = seed_metric_sec if seed_metric_sec and seed_metric_sec > 0 else None
    if seed is None:
        return {
            "lane": lane,
            "case_id": case.case_id,
            "app_id": case.app_id,
            "backend": case.backend,
            "method": "calibration_required",
            "planned_command": list(command),
            "target_measured_sec": target_measured_sec,
            "repeat_planning_target_sec": target_measured_sec * repeat_safety_factor,
            "target_met_by_plan": False,
            "reason": "No positive seed metric was available.",
            "claim_boundary": _claim_boundary(),
        }
    if knob is not None:
        flag, base_repeat = knob
        repeat_planning_target = target_measured_sec * repeat_safety_factor
        planned_repeat = min(max_internal_repeat, max(base_repeat, math.ceil(repeat_planning_target / seed)))
        planned_command = _replace_flag_value(command, flag, planned_repeat)
        planned_measured = seed * planned_repeat
        estimated_wall = seed_wall_sec + max(0, planned_repeat - base_repeat) * seed if seed_wall_sec else None
        if estimated_wall is not None and estimated_wall > max_estimated_wall_sec:
            return {
                "lane": lane,
                "case_id": case.case_id,
                "app_id": case.app_id,
                "backend": case.backend,
                "method": "partial_base_repeat_wall_guard",
                "repeat_flag": flag,
                "base_repeat": base_repeat,
                "planned_repeat": base_repeat,
                "planned_command": list(command),
                "seed_primary_metric_sec": seed,
                "seed_wall_median_sec": seed_wall_sec,
                "target_measured_sec": target_measured_sec,
                "repeat_planning_target_sec": repeat_planning_target,
                "estimated_measured_sec": seed * base_repeat,
                "estimated_wall_sec": seed_wall_sec,
                "target_met_by_plan": False,
                "reason": (
                    "A repeat knob exists, but scaling it to the 10s hot-query target would exceed "
                    "the wall-time guard according to prior evidence; run the base row once and mark "
                    "this as partial diagnostic evidence."
                ),
                "claim_boundary": _claim_boundary(),
            }
        return {
            "lane": lane,
            "case_id": case.case_id,
            "app_id": case.app_id,
            "backend": case.backend,
            "method": "internal_repeat_knob",
            "repeat_flag": flag,
            "base_repeat": base_repeat,
            "planned_repeat": planned_repeat,
            "planned_command": list(planned_command),
            "seed_primary_metric_sec": seed,
            "seed_wall_median_sec": seed_wall_sec,
            "target_measured_sec": target_measured_sec,
            "repeat_planning_target_sec": repeat_planning_target,
            "estimated_measured_sec": planned_measured,
            "estimated_wall_sec": estimated_wall,
            "target_met_by_plan": planned_measured >= target_measured_sec * 0.95,
            "reason": "Existing app-level repeat knob can stretch the hot query loop.",
            "claim_boundary": _claim_boundary(),
        }
    repeat_planning_target = target_measured_sec * repeat_safety_factor
    wrapper_repeats = max(1, min(max_wrapper_repeat, math.ceil(repeat_planning_target / seed)))
    estimated_measured = seed * wrapper_repeats
    estimated_wall = (seed_wall_sec or 0.0) * wrapper_repeats
    if seed_wall_sec and estimated_wall > max_estimated_wall_sec:
        wrapper_repeats = 1
        estimated_measured = seed
        estimated_wall = seed_wall_sec
        method = "partial_one_shot_no_repeat_knob"
        reason = (
            "No app repeat knob exists and wrapper repetition would exceed the wall-time guard; "
            "run one diagnostic shot and report target not met."
        )
    else:
        method = "wrapper_repeat_subprocess"
        reason = "No app repeat knob exists; wrapper repeats whole subprocess while reporting setup separately."
    return {
        "lane": lane,
        "case_id": case.case_id,
        "app_id": case.app_id,
        "backend": case.backend,
        "method": method,
        "wrapper_repeats": wrapper_repeats,
        "planned_command": list(command),
        "seed_primary_metric_sec": seed,
        "seed_wall_median_sec": seed_wall_sec,
        "target_measured_sec": target_measured_sec,
        "repeat_planning_target_sec": repeat_planning_target,
        "estimated_measured_sec": estimated_measured,
        "estimated_wall_sec": estimated_wall,
        "target_met_by_plan": estimated_measured >= target_measured_sec * 0.95,
        "reason": reason,
        "claim_boundary": _claim_boundary(),
    }


def _patched_case(case: Any, command: tuple[str, ...]) -> Any:
    try:
        return case.__class__(
            case_id=case.case_id,
            app_id=case.app_id,
            app_name=case.app_name,
            comparison_group=case.comparison_group,
            backend=case.backend,
            command=command,
            primary_metric_path=case.primary_metric_path,
            setup_commands=case.setup_commands,
            json_out=case.json_out,
            unsupported_reason=case.unsupported_reason,
            notes=case.notes,
        )
    except TypeError:
        # Older evidence runners have the same dataclass shape in practice, but
        # this fallback keeps dry planning robust if a local field drifts.
        return case


def _run_one(
    runner: ModuleType,
    case: Any,
    *,
    env: dict[str, str],
    timeout_sec: int,
    dry_run: bool,
) -> dict[str, Any]:
    return runner.run_case(
        case,
        env=env,
        timeout_sec=timeout_sec,
        repeat=1,
        dry_run=dry_run,
    )


def _execute_plan_row(
    runner: ModuleType,
    case: Any,
    plan: dict[str, Any],
    *,
    env: dict[str, str],
    timeout_sec: int,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        return {
            "status": "dry_run",
            "case_id": case.case_id,
            "app_id": case.app_id,
            "primary_metric_sec": None,
            "observed_measured_sec": 0.0,
            "runs": [],
        }
    runs: list[dict[str, Any]] = []
    if plan["method"] in {"internal_repeat_knob", "calibration_required", "partial_base_repeat_wall_guard"}:
        planned_command = tuple(plan.get("planned_command") or case.command or ())
        patched = _patched_case(case, planned_command)
        runs.append(_run_one(runner, patched, env=env, timeout_sec=timeout_sec, dry_run=False))
    else:
        for _ in range(int(plan.get("wrapper_repeats", 1))):
            runs.append(_run_one(runner, case, env=env, timeout_sec=timeout_sec, dry_run=False))
    ok_metrics = [
        float(row["primary_metric_sec"])
        for row in runs
        if row.get("status") == "ok" and isinstance(row.get("primary_metric_sec"), (int, float))
    ]
    if ok_metrics:
        primary = statistics.median(ok_metrics)
        if plan["method"] == "internal_repeat_knob":
            observed_measured = primary * int(plan.get("planned_repeat", 1))
            observed_method = "median_primary_metric_times_planned_internal_repeat"
        elif plan["method"] == "partial_base_repeat_wall_guard":
            observed_measured = primary * int(plan.get("base_repeat", 1))
            observed_method = "median_primary_metric_times_base_repeat_partial"
        else:
            observed_measured = sum(ok_metrics)
            observed_method = "sum_of_wrapper_primary_metrics"
        status = "ok" if len(ok_metrics) == len(runs) else "partial"
    else:
        primary = None
        observed_measured = 0.0
        observed_method = "no_successful_primary_metrics"
        status = "failed"
    return {
        "status": status,
        "case_id": case.case_id,
        "app_id": case.app_id,
        "primary_metric_sec": primary,
        "observed_measured_sec": observed_measured,
        "observed_measured_sec_method": observed_method,
        "target_met_by_observed_sum": observed_measured >= float(plan["target_measured_sec"]) * 0.95,
        "runs": [
            {
                "status": row.get("status"),
                "primary_metric_sec": row.get("primary_metric_sec"),
                "primary_metric_source": row.get("primary_metric_source"),
                "wall_median_sec": row.get("wall_median_sec"),
                "stderr_tail": row.get("runs", [{}])[-1].get("stderr_tail") if row.get("runs") else "",
            }
            for row in runs
        ],
    }


def _lane_rows(
    *,
    lane: str,
    source_root: Path,
    scale: str,
    seed_metrics: dict[str, dict[str, dict[str, float]]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    runner = _load_runner(source_root, lane)
    lane_artifacts = args.artifact_dir / lane
    lane_artifacts.mkdir(parents=True, exist_ok=True)
    env = runner._base_env()
    cases = runner.build_cases(scale, lane_artifacts)
    selected = []
    for case in cases:
        if case.backend != "optix":
            continue
        if args.only_app and case.app_id not in set(args.only_app):
            continue
        if args.only_case and case.case_id not in set(args.only_case):
            continue
        selected.append(case)
    rows: list[dict[str, Any]] = []
    for index, case in enumerate(selected, start=1):
        seed = seed_metrics.get(lane, {}).get(case.case_id, {})
        plan = _planned_case(
            case,
            lane=lane,
            seed_metric_sec=seed.get("primary_metric_sec"),
            seed_wall_sec=seed.get("wall_median_sec"),
            target_measured_sec=args.target_measured_sec,
            repeat_safety_factor=args.repeat_safety_factor,
            max_internal_repeat=args.max_internal_repeat,
            max_wrapper_repeat=args.max_wrapper_repeat,
            max_estimated_wall_sec=args.max_estimated_wall_sec,
        )
        print(
            f"[goal3536] {lane} {index}/{len(selected)} {case.case_id}: "
            f"{plan['method']} target_plan={plan.get('target_met_by_plan')}",
            flush=True,
        )
        execution = _execute_plan_row(
            runner,
            case,
            plan,
            env=env,
            timeout_sec=args.timeout_sec,
            dry_run=args.dry_run,
        )
        rows.append(
            {
                "lane": lane,
                "source_root": str(source_root),
                "source_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=source_root),
                "case_id": case.case_id,
                "app_id": case.app_id,
                "comparison_group": case.comparison_group,
                "backend": case.backend,
                "plan": plan,
                "execution": execution,
                "claim_boundary": _claim_boundary(),
            }
        )
    return rows


def _comparisons(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (row["app_id"], row["case_id"], row["comparison_group"])
        by_key.setdefault(key, {})[row["lane"]] = row
    comparisons = []
    for (app_id, case_id, group), lanes in sorted(by_key.items()):
        v23 = lanes.get("v23")
        v28 = lanes.get("v28")
        if not v23 or not v28:
            continue
        v23_sec = v23["execution"].get("primary_metric_sec")
        v28_sec = v28["execution"].get("primary_metric_sec")
        speedup = None
        if isinstance(v23_sec, (int, float)) and isinstance(v28_sec, (int, float)) and v28_sec > 0:
            speedup = float(v23_sec) / float(v28_sec)
        comparisons.append(
            {
                "app_id": app_id,
                "case_id": case_id,
                "comparison_group": group,
                "v23_primary_metric_sec": v23_sec,
                "v28_primary_metric_sec": v28_sec,
                "v28_speedup_vs_v23": speedup,
                "v23_observed_measured_sec": v23["execution"].get("observed_measured_sec"),
                "v28_observed_measured_sec": v28["execution"].get("observed_measured_sec"),
                "v23_target_met_by_plan": v23["plan"].get("target_met_by_plan"),
                "v28_target_met_by_plan": v28["plan"].get("target_met_by_plan"),
                "v23_target_met_by_observed_sum": v23["execution"].get("target_met_by_observed_sum"),
                "v28_target_met_by_observed_sum": v28["execution"].get("target_met_by_observed_sum"),
                "measurement_boundary": (
                    "Internal comparison only. Rows with target_met=false are diagnostic and must not be "
                    "used as final 10s steady-state evidence."
                ),
                "claim_boundary": _claim_boundary(),
            }
        )
    return comparisons


def _summary(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    speedups = [
        float(row["v28_speedup_vs_v23"])
        for row in comparisons
        if isinstance(row.get("v28_speedup_vs_v23"), (int, float))
    ]
    fully_targeted = [
        row
        for row in comparisons
        if row.get("v23_target_met_by_plan") and row.get("v28_target_met_by_plan")
    ]
    observed_targeted = [
        row
        for row in comparisons
        if row.get("v23_target_met_by_observed_sum") and row.get("v28_target_met_by_observed_sum")
    ]
    observed_misses = [
        {
            "case_id": row["case_id"],
            "v23_target_met_by_observed_sum": row.get("v23_target_met_by_observed_sum"),
            "v28_target_met_by_observed_sum": row.get("v28_target_met_by_observed_sum"),
            "v23_observed_measured_sec": row.get("v23_observed_measured_sec"),
            "v28_observed_measured_sec": row.get("v28_observed_measured_sec"),
        }
        for row in comparisons
        if not (row.get("v23_target_met_by_observed_sum") and row.get("v28_target_met_by_observed_sum"))
    ]
    return {
        "row_count": len(comparisons),
        "ratio_count": len(speedups),
        "target_met_by_plan_pair_count": len(fully_targeted),
        "target_met_by_observed_pair_count": len(observed_targeted),
        "observed_target_miss_count": len(observed_misses),
        "observed_target_misses": observed_misses,
        "median_speedup": statistics.median(speedups) if speedups else None,
        "geomean_speedup": math.prod(speedups) ** (1.0 / len(speedups)) if speedups else None,
        "min_speedup": min(speedups) if speedups else None,
        "max_speedup": max(speedups) if speedups else None,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    seeds = _load_seed_metrics(args.seed_artifact)
    rows = []
    for lane, source_root in (("v23", args.v23_root), ("v28", args.v28_root)):
        rows.extend(
            _lane_rows(
                lane=lane,
                source_root=source_root,
                scale=args.scale,
                seed_metrics=seeds,
                args=args,
            )
        )
    comparisons = _comparisons(rows)
    return {
        "schema": SCHEMA,
        "goal": 3536,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_measured_sec": float(args.target_measured_sec),
        "repeat_safety_factor": float(args.repeat_safety_factor),
        "scale": args.scale,
        "dry_run": bool(args.dry_run),
        "seed_artifact": str(args.seed_artifact),
        "v23_root": str(args.v23_root),
        "v28_root": str(args.v28_root),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
        "rows": rows,
        "comparisons": comparisons,
        "summary": _summary(comparisons),
        "claim_boundary": _claim_boundary(),
        "boundary": (
            "Goal3536 is an internal 10-second steady-state measurement protocol. It separates "
            "target-compliant rows from partial diagnostics and does not authorize public release "
            "or speedup claims."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal3536 v2.8 vs v2.3 10s Steady-State Protocol",
        "",
        "This is an internal measurement packet. It does not authorize release or public speedup wording.",
        "",
        f"- Target measured query time per side: `{payload['target_measured_sec']}` sec",
        f"- Scale: `{payload['scale']}`",
        f"- GPU: `{payload.get('gpu', '')}`",
        f"- Summary: `{json.dumps(payload['summary'], sort_keys=True)}`",
        "",
        "## Comparison Rows",
        "",
        "| App | Case | v2.3 sec | v2.8 sec | v2.8/v2.3 | Target plan met? | Target observed met? |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["comparisons"]:
        v23 = row["v23_primary_metric_sec"]
        v28 = row["v28_primary_metric_sec"]
        speedup = row["v28_speedup_vs_v23"]
        target_plan = f"{row['v23_target_met_by_plan']}/{row['v28_target_met_by_plan']}"
        target_observed = (
            f"{row['v23_target_met_by_observed_sum']}/{row['v28_target_met_by_observed_sum']}"
        )
        lines.append(
            "| {app} | {case} | {v23} | {v28} | {speedup} | {target_plan} | {target_observed} |".format(
                app=row["app_id"],
                case=row["case_id"],
                v23=f"{float(v23):.6g}" if isinstance(v23, (int, float)) else "",
                v28=f"{float(v28):.6g}" if isinstance(v28, (int, float)) else "",
                speedup=f"{float(speedup):.3f}x" if isinstance(speedup, (int, float)) else "",
                target_plan=target_plan,
                target_observed=target_observed,
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- A row is final 10s evidence only when both sides report `target_met_by_plan = true` and the execution succeeds.",
            "- Rows without a repeat knob are reported as partial diagnostics when wrapper repetition would exceed the wall-time guard.",
            "- Setup, packing, and validation are kept out of the primary hot-query metric unless the underlying app exposes only a total metric.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3536 v2.8 vs v2.3 10s steady-state comparison harness.")
    parser.add_argument("--v23-root", type=Path, default=Path("/root/rtdl_goal3524/v23_evidence"))
    parser.add_argument("--v28-root", type=Path, default=Path("/root/rtdl_goal3524/v28_current"))
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT_DIR / "summary.json")
    parser.add_argument("--seed-artifact", type=Path, default=DEFAULT_SEED_ARTIFACT)
    parser.add_argument("--scale", choices=("quick", "standard", "large"), default="standard")
    parser.add_argument("--target-measured-sec", type=float, default=10.0)
    parser.add_argument(
        "--repeat-safety-factor",
        type=float,
        default=1.0,
        help="Plan repeats against target*factor while judging target_met against target.",
    )
    parser.add_argument("--max-internal-repeat", type=int, default=50000)
    parser.add_argument("--max-wrapper-repeat", type=int, default=12)
    parser.add_argument("--max-estimated-wall-sec", type=float, default=900.0)
    parser.add_argument("--timeout-sec", type=int, default=1800)
    parser.add_argument("--only-app", action="append", default=[])
    parser.add_argument("--only-case", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output.parent / "summary.md").write_text(render_markdown(payload), encoding="utf-8")
    print(f"[goal3536] wrote {args.output}", flush=True)
    print(f"[goal3536] wrote {args.output.parent / 'summary.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
