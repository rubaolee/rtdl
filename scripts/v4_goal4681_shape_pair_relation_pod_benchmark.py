#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


VERSION = "rtdl.v4.goal4681.shape_pair_relation_focused_pod_benchmark.v1"
ROOT = Path(__file__).resolve().parents[1]
APP_MODULE = "examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _python(_root: Path) -> str:
    return os.environ.get("RTDL_GOAL4681_PYTHON", "/root/rtdl_v4_venv/bin/python")


def _cuda_prefix() -> Path:
    return Path(
        os.environ.get(
            "RTDL_GOAL4681_CUDA_PREFIX",
            "/root/rtdl_v4_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc",
        )
    )


def _versions() -> dict[str, dict[str, Any]]:
    return {
        "v2_14": {
            "root": Path(os.environ.get("RTDL_GOAL4681_V2_ROOT", "/root/rtdl_v2_14_tag")),
            "route": "prepared_optix_shape_pair_active_count",
            "tag_native_optix_build": False,
        },
        "v3_0_2": {
            "root": Path(os.environ.get("RTDL_GOAL4681_V3_ROOT", "/root/rtdl_v3_0_2_tag")),
            "route": "prepared_optix_shape_pair_active_count",
            "tag_native_optix_build": False,
        },
        "v4_current": {
            "root": Path(os.environ.get("RTDL_GOAL4681_V4_ROOT", "/root/rtdl_v4_candidate_pod")),
            "route": "v4_shape_pair_relation_active_count_wrapper",
            "tag_native_optix_build": True,
        },
    }


def _profile_values(profile: str) -> dict[str, Any]:
    if profile == "smoke":
        return {
            "grid": 32,
            "shape_count": 1024,
            "repeat": 3,
            "warmup": 1,
            "correctness_grid": 32,
            "correctness_shape_count": 1024,
            "timeout_sec": 1200,
        }
    if profile == "serious":
        return {
            "grid": 64,
            "shape_count": 4096,
            "repeat": 7,
            "warmup": 2,
            "correctness_grid": 32,
            "correctness_shape_count": 1024,
            "timeout_sec": 3600,
        }
    raise ValueError(f"unknown profile {profile!r}")


def _dataset_for_shape_count(shape_count: int) -> str:
    return f"generated_square_grid_shape_pair_count{int(shape_count)}"


def _make_square_grid_cdb(
    *,
    name: str,
    grid: int,
    spacing: float,
    side: float,
    offset_x: float,
    offset_y: float,
    face_base: int,
):
    from rtdsl.datasets import CdbChain
    from rtdsl.datasets import CdbDataset
    from rtdsl.datasets import CdbPoint

    chains: list[Any] = []
    next_point_id = 1
    next_chain_id = 1
    for row in range(grid):
        for col in range(grid):
            x0 = col * spacing + offset_x
            y0 = row * spacing + offset_y
            points = (
                CdbPoint(x=x0, y=y0),
                CdbPoint(x=x0 + side, y=y0),
                CdbPoint(x=x0 + side, y=y0 + side),
                CdbPoint(x=x0, y=y0 + side),
            )
            chains.append(
                CdbChain(
                    chain_id=next_chain_id,
                    point_count=len(points),
                    first_point_id=next_point_id,
                    last_point_id=next_point_id + len(points) - 1,
                    left_face_id=face_base + next_chain_id,
                    right_face_id=0,
                    points=points,
                )
            )
            next_chain_id += 1
            next_point_id += len(points)
    return CdbDataset(name=name, chains=tuple(chains))


def _write_generated_pair(out_dir: Path, *, run_kind: str, grid: int) -> dict[str, Any]:
    from rtdsl.datasets import write_cdb

    dataset_dir = out_dir / "datasets"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    left = _make_square_grid_cdb(
        name=f"goal4681_left_square_grid_{grid}",
        grid=grid,
        spacing=1.0,
        side=0.72,
        offset_x=0.0,
        offset_y=0.0,
        face_base=1000000,
    )
    right = _make_square_grid_cdb(
        name=f"goal4681_right_square_grid_{grid}",
        grid=grid,
        spacing=1.0,
        side=0.72,
        offset_x=0.35,
        offset_y=0.35,
        face_base=2000000,
    )
    left_path = write_cdb(left, dataset_dir / f"goal4681_{run_kind}_left_grid{grid}.cdb")
    right_path = write_cdb(right, dataset_dir / f"goal4681_{run_kind}_right_grid{grid}.cdb")
    dataset = f"{left_path} + {right_path}"
    return {
        "dataset": dataset,
        "left_cdb": str(left_path),
        "right_cdb": str(right_path),
        "grid": int(grid),
        "shape_count_per_side": int(grid * grid),
        "generated_input": True,
        "generated_input_note": (
            "Focused same-primitive shape-pair relation benchmark input. This is "
            "not RayJoin paper input and does not authorize paper/app-level claims."
        ),
    }


def _split_dataset_paths(dataset: str) -> tuple[Path, ...]:
    return tuple(Path(part.strip()) for part in dataset.split("+") if part.strip())


def _load_overlay_polygons(dataset: str) -> tuple[tuple[object, ...], tuple[object, ...]]:
    from rtdsl.datasets import chains_to_polygons
    from rtdsl.datasets import load_cdb

    paths = _split_dataset_paths(dataset)
    if len(paths) != 2:
        raise ValueError("shape-pair relation benchmark requires `left.cdb + right.cdb`")
    left = chains_to_polygons(load_cdb(paths[0]))
    right = chains_to_polygons(load_cdb(paths[1]))
    return left, right


def _env_for(root: Path, *, tag_native_optix_build: bool) -> dict[str, str]:
    env = os.environ.copy()
    cuda_prefix = _cuda_prefix()
    env["PYTHONPATH"] = f"{root / 'src'}:{ROOT}"
    env["CUDA_HOME"] = str(cuda_prefix)
    env["CUDA_PATH"] = str(cuda_prefix)
    env["NUMBA_CUDA_PREFIX"] = str(cuda_prefix)
    env["NUMBA_CUDA_NVVM"] = str(cuda_prefix / "nvvm" / "lib64" / "libnvvm.so")
    env["LD_LIBRARY_PATH"] = f"{cuda_prefix / 'nvvm' / 'lib64'}:{env.get('LD_LIBRARY_PATH', '')}"
    optix = root / "build" / ("librtdl_optix.so" if tag_native_optix_build else "librtdl_optix.v4compat.so")
    embree = root / "build" / "librtdl_embree.so"
    env["RTDL_OPTIX_LIBRARY"] = str(optix)
    env["RTDL_OPTIX_LIB"] = str(optix)
    env["RTDL_EMBREE_LIBRARY"] = str(embree)
    env["RTDL_EMBREE_LIB"] = str(embree)
    return env


def _copy_compat_libraries(versions: dict[str, dict[str, Any]]) -> None:
    v4_optix = versions["v4_current"]["root"] / "build" / "librtdl_optix.so"
    if not v4_optix.exists():
        return
    for name in ("v2_14", "v3_0_2"):
        root = versions[name]["root"]
        target = root / "build" / "librtdl_optix.v4compat.so"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.stat().st_size != v4_optix.stat().st_size:
            target.write_bytes(v4_optix.read_bytes())


def _median(rows: list[dict[str, float]], field: str) -> float:
    return float(statistics.median(float(row[field]) for row in rows))


def _phase_time(phases: dict[str, float], label: str, fn):
    start = time.perf_counter()
    value = fn()
    phases[label] = float(time.perf_counter() - start)
    return value


def _run_v4_worker(args: argparse.Namespace) -> dict[str, object]:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    import rtdsl.v4 as v4
    from rtdsl.optix_runtime import prepare_shape_pair_relation_flags_optix
    from rtdsl.optix_runtime import prepare_shape_pair_relation_left_set_optix

    left_polygons, right_polygons = _load_overlay_polygons(args.dataset)
    phases: dict[str, float] = {}
    prepared_relation = _phase_time(
        phases,
        "prepare_right_scene_seconds",
        lambda: prepare_shape_pair_relation_flags_optix(right_polygons),
    )
    prepared_left = _phase_time(
        phases,
        "prepare_left_set_seconds",
        lambda: prepare_shape_pair_relation_left_set_optix(left_polygons),
    )
    executor = _phase_time(
        phases,
        "prepare_executor_seconds",
        lambda: prepared_relation.prepare_active_count_prepared_left_executor(prepared_left),
    )
    runner = v4.V4ShapePairRelationActiveCount2DPreparedLeftExecutor(
        prepared_relation=prepared_relation,
        prepared_left=prepared_left,
        executor=executor,
    )
    repeats: list[dict[str, float]] = []
    last_result: dict[str, object] | None = None
    try:
        for _ in range(int(args.warmup)):
            runner.run()
        for repeat_index in range(int(args.repeat)):
            start = time.perf_counter()
            result = runner.run()
            elapsed = float(time.perf_counter() - start)
            repeats.append(
                {
                    "repeat_index": float(repeat_index),
                    "hot_seconds": elapsed,
                    "wall_seconds": float(phases["prepare_executor_seconds"] + elapsed),
                    "active_count": float(result["active_count"]),
                }
            )
            last_result = result
    finally:
        runner.close()
    if last_result is None:
        raise RuntimeError("V4 worker produced no measured repeats")
    active_values = {int(row["active_count"]) for row in repeats}
    if len(active_values) != 1:
        raise RuntimeError("V4 active-count repeat changed result identity")
    metadata = dict(last_result.get("metadata", {}))
    return {
        "schema": VERSION,
        "version": "v4_current",
        "route": "v4_shape_pair_relation_active_count_wrapper",
        "app": "spatial_rayjoin",
        "workload": "overlay_active_count_probe_only",
        "dataset": args.dataset,
        "row_count": int(last_result["active_count"]),
        "summary": {"active_seed_count": int(last_result["active_count"])},
        "hot_repeats": repeats,
        "phases_sec": {
            **phases,
            "active_count_hot_seconds": _median(repeats, "hot_seconds"),
            "active_count_wall_seconds": _median(repeats, "wall_seconds"),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
        },
        "medians": {
            "hot_seconds": _median(repeats, "hot_seconds"),
            "wall_seconds": _median(repeats, "wall_seconds"),
        },
        "v4_wrapper_metadata": metadata,
        "claim_flags": {
            "same_primitive_contract": True,
            "v4_frontdoor_wrapper": True,
            "host_row_stream_materialization_in_hot_path": bool(
                metadata.get("host_materialization_in_hot_path", True)
            ),
            "partner_migration_counts_as_speed": False,
            "app_identity_kernel": False,
        },
    }


def _run_worker(args: argparse.Namespace) -> int:
    if args.route != "v4_shape_pair_relation_active_count_wrapper":
        raise ValueError(f"unsupported worker route {args.route!r}")
    payload = _run_v4_worker(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _run_command(
    *,
    version: str,
    run_kind: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    out_dir: Path,
    timeout_sec: int,
) -> dict[str, Any]:
    stem = f"{version}_{run_kind}"
    stdout_path = out_dir / f"{stem}.json"
    stderr_path = out_dir / f"{stem}.stderr.txt"
    started = time.time()
    started_perf = time.perf_counter()
    print(f"[goal4681] BEGIN {stem}", flush=True)
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                text=True,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_sec,
                check=False,
            )
            rc = int(completed.returncode)
            timed_out = False
            error = None
        except subprocess.TimeoutExpired as exc:
            rc = 124
            timed_out = True
            error = f"timeout after {exc.timeout} seconds"
    elapsed = time.perf_counter() - started_perf
    print(f"[goal4681] END {stem} rc={rc} elapsed={elapsed:.3f}s", flush=True)
    return {
        "version": version,
        "run_kind": run_kind,
        "command": command,
        "cwd": str(cwd),
        "stdout_json": str(stdout_path),
        "stderr": str(stderr_path),
        "returncode": rc,
        "timed_out": timed_out,
        "error": error,
        "runner_elapsed_sec": elapsed,
        "started_unix": started,
        "ended_unix": time.time(),
    }


def _read_payload(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _app_payload_metrics(payload: dict[str, Any] | None) -> dict[str, float | int] | None:
    if not payload:
        return None
    phases = payload.get("phases_sec")
    if not isinstance(phases, dict):
        return None
    hot = phases.get("prepared_query_sec", phases.get("active_count_hot_seconds"))
    prepare_executor = phases.get("prepare_active_count_executor_sec", phases.get("prepare_executor_seconds", 0.0))
    if not isinstance(hot, (int, float)) or not isinstance(prepare_executor, (int, float)):
        return None
    row_count = payload.get("row_count", payload.get("summary", {}).get("active_seed_count"))
    return {
        "hot_seconds": float(hot),
        "wall_seconds": float(prepare_executor) + float(hot),
        "active_count": int(row_count),
    }


def _ratio(denominator: float | None, numerator: float | None) -> float | None:
    if denominator is None or numerator is None or numerator <= 0.0:
        return None
    return float(denominator) / float(numerator)


def _metric(metrics: dict[str, float | int] | None, field: str) -> float | None:
    if not metrics:
        return None
    value = metrics.get(field)
    return float(value) if isinstance(value, (int, float)) else None


def _active_count(payload: dict[str, Any] | None) -> int | None:
    metrics = _app_payload_metrics(payload)
    if metrics is None:
        return None
    return int(metrics["active_count"])


def _host_materialization(payload: dict[str, Any] | None) -> bool | None:
    if not payload:
        return None
    flags = payload.get("claim_flags")
    if not isinstance(flags, dict):
        return None
    value = flags.get("host_row_stream_materialization_in_hot_path")
    return bool(value) if isinstance(value, bool) else None


def _analyze(executions: list[dict[str, Any]], profile: str, dataset: str) -> dict[str, Any]:
    payloads: dict[tuple[str, str], dict[str, Any] | None] = {}
    metrics: dict[tuple[str, str], dict[str, float | int] | None] = {}
    for execution in executions:
        key = (execution["version"], execution["run_kind"])
        payloads[key] = _read_payload(Path(execution["stdout_json"]))
        metrics[key] = _app_payload_metrics(payloads[key])

    serious_v2 = metrics.get(("v2_14", "serious"))
    serious_v3 = metrics.get(("v3_0_2", "serious"))
    serious_v4 = metrics.get(("v4_current", "serious"))
    correctness_counts = [
        _active_count(payloads.get(("v2_14", "correctness"))),
        _active_count(payloads.get(("v3_0_2", "correctness"))),
        _active_count(payloads.get(("v4_current", "correctness"))),
    ]
    serious_counts = [
        _active_count(payloads.get(("v2_14", "serious"))),
        _active_count(payloads.get(("v3_0_2", "serious"))),
        _active_count(payloads.get(("v4_current", "serious"))),
    ]
    ratios = {
        "v4_hot_over_v2_14_same_primitive": _ratio(
            _metric(serious_v2, "hot_seconds"),
            _metric(serious_v4, "hot_seconds"),
        ),
        "v4_wall_over_v2_14_same_primitive": _ratio(
            _metric(serious_v2, "wall_seconds"),
            _metric(serious_v4, "wall_seconds"),
        ),
        "v4_hot_over_v3_0_2_control": _ratio(
            _metric(serious_v3, "hot_seconds"),
            _metric(serious_v4, "hot_seconds"),
        ),
    }
    all_returncodes_ok = all(int(item["returncode"]) == 0 for item in executions)
    correctness_parity = None not in correctness_counts and len(set(correctness_counts)) == 1
    serious_parity = None not in serious_counts and len(set(serious_counts)) == 1
    no_v4_host_materialization = _host_materialization(payloads.get(("v4_current", "serious"))) is False
    pass_fail = {
        "all_subprocesses_returned_zero": all_returncodes_ok,
        "correctness_companion_ok": bool(correctness_parity),
        "serious_active_count_parity": bool(serious_parity),
        "v4_hot_bar_pass": (
            ratios["v4_hot_over_v2_14_same_primitive"] is not None
            and ratios["v4_hot_over_v2_14_same_primitive"] >= 1.20
        ),
        "v4_wall_bar_pass": (
            ratios["v4_wall_over_v2_14_same_primitive"] is not None
            and ratios["v4_wall_over_v2_14_same_primitive"] >= 1.10
        ),
        "v4_v3_parity_floor_pass": (
            ratios["v4_hot_over_v3_0_2_control"] is not None
            and ratios["v4_hot_over_v3_0_2_control"] >= 0.98
        ),
        "v4_host_row_stream_materialization_in_hot_path": _host_materialization(
            payloads.get(("v4_current", "serious"))
        ),
        "partner_migration_counted_as_speed": False,
        "same_primitive_denominator_used": True,
    }
    pass_fail["goal4681_speed_credit_pass"] = (
        all_returncodes_ok
        and correctness_parity
        and serious_parity
        and bool(pass_fail["v4_hot_bar_pass"])
        and bool(pass_fail["v4_wall_bar_pass"])
        and bool(pass_fail["v4_v3_parity_floor_pass"])
        and no_v4_host_materialization
    )
    return {
        "schema": VERSION,
        "profile": profile,
        "dataset": dataset,
        "executions": executions,
        "metrics": {f"{key[0]}_{key[1]}": value for key, value in metrics.items()},
        "ratios": ratios,
        "active_counts": {
            "correctness": correctness_counts,
            "serious": serious_counts,
        },
        "pass_fail": pass_fail,
        "decision_label": (
            "goal4681_pass_shape_pair_relation_material_same_primitive_improvement"
            if pass_fail["goal4681_speed_credit_pass"]
            else "goal4681_no_speed_credit_productization_or_reclassify"
        ),
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_high_performance_wording_authorized": False,
            "broad_v4_over_v2_v3_wording_authorized": False,
            "app_identity_kernel_authorized": False,
            "partner_migration_counts_as_speed": False,
        },
    }


def _print_plan(profile: str) -> dict[str, Any]:
    values = _profile_values(profile)
    return {
        "schema": VERSION,
        "mode": "plan",
        "profile": profile,
        "values": values,
        "serious_dataset": _dataset_for_shape_count(int(values["shape_count"])),
        "correctness_dataset": _dataset_for_shape_count(int(values["correctness_shape_count"])),
        "dataset_source": (
            "generated focused square-grid CDB pair; not RayJoin paper input and "
            "not app-level release evidence"
        ),
        "versions": {
            name: {"root": str(row["root"]), "route": row["route"]}
            for name, row in _versions().items()
        },
        "bars": {
            "v4_hot_over_v2_14_same_primitive_min_for_speed_credit": 1.20,
            "v4_wall_over_v2_14_same_primitive_min_for_speed_credit": 1.10,
            "v4_hot_over_v3_0_2_parity_floor": 0.98,
            "partner_migration_counts_as_speed": False,
            "host_row_stream_materialization_allowed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4681 shape-pair focused POD benchmark.")
    parser.add_argument("--profile", choices=("smoke", "serious"), default="serious")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--print-plan", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--route")
    parser.add_argument("--dataset")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    args = parser.parse_args()

    if args.print_plan:
        print(json.dumps(_print_plan(args.profile), indent=2, sort_keys=True))
        return 0
    if args.worker:
        return _run_worker(args)

    values = _profile_values(args.profile)
    versions = _versions()
    _copy_compat_libraries(versions)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or ROOT / "future" / "v4" / "evidence" / f"v4_goal4681_shape_pair_pod_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    executions: list[dict[str, Any]] = []
    generated_inputs = {
        "serious": _write_generated_pair(out_dir, run_kind="serious", grid=int(values["grid"])),
        "correctness": _write_generated_pair(
            out_dir,
            run_kind="correctness",
            grid=int(values["correctness_grid"]),
        ),
    }
    run_plan = (
        ("serious", int(values["repeat"]), int(values["warmup"])),
        ("correctness", 1, 0),
    )
    for run_kind, repeat, warmup in run_plan:
        dataset = str(generated_inputs[run_kind]["dataset"])
        for version, version_info in versions.items():
            root = Path(version_info["root"])
            env = _env_for(root, tag_native_optix_build=bool(version_info["tag_native_optix_build"]))
            if version == "v4_current":
                command = [
                    _python(root),
                    str(Path(__file__).resolve()),
                    "--worker",
                    "--route",
                    str(version_info["route"]),
                    "--dataset",
                    dataset,
                    "--repeat",
                    str(repeat),
                    "--warmup",
                    str(warmup),
                ]
                cwd = ROOT
            else:
                command = [
                    _python(root),
                    "-m",
                    APP_MODULE,
                    "--workload",
                    "overlay_seed",
                    "--execution-route",
                    "prepared_optix_shape_pair_active_count",
                    "--dataset",
                    dataset,
                    "--repeat",
                    str(repeat),
                    "--warmup",
                    str(warmup),
                    "--no-rows",
                ]
                cwd = root
            executions.append(
                _run_command(
                    version=version,
                    run_kind=run_kind,
                    command=command,
                    cwd=cwd,
                    env=env,
                    out_dir=out_dir,
                    timeout_sec=int(values["timeout_sec"]),
                )
            )
    summary = _analyze(executions, args.profile, str(generated_inputs["serious"]["dataset"]))
    summary["generated_inputs"] = generated_inputs
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if all(int(item["returncode"]) == 0 for item in executions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
