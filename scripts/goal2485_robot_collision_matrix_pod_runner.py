from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
import traceback


ROOT = next(parent for parent in pathlib.Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    prefix = f"{ROOT / 'src'}:{ROOT}"
    env["PYTHONPATH"] = f"{prefix}:{existing}" if existing else prefix
    return env


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            args,
            cwd=ROOT,
            env=_subprocess_env(),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _run_command(args: list[str]) -> dict[str, object]:
    start = time.perf_counter()
    completed = subprocess.run(
        args,
        cwd=ROOT,
        env=_subprocess_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "args": args,
        "returncode": completed.returncode,
        "elapsed_sec": time.perf_counter() - start,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _nvcc_version_line() -> str | None:
    output = _check_output(["nvcc", "--version"])
    if not output:
        return None
    lines = output.splitlines()
    return lines[-1] if lines else None


def _optix_header_candidates() -> list[str]:
    candidates = []
    for variable in ("OPTIX_PREFIX", "RTDL_OPTIX_PREFIX", "OptiX_INSTALL_DIR"):
        value = os.environ.get(variable)
        if value:
            candidates.append(pathlib.Path(value) / "include" / "optix.h")
    candidates.extend(
        [
            pathlib.Path("/workspace/vendor/optix-dev/include/optix.h"),
            pathlib.Path("/workspace/vendor/optix-dev-8.0.0/include/optix.h"),
            pathlib.Path("/opt/optix/include/optix.h"),
            pathlib.Path("/usr/local/NVIDIA-OptiX-SDK/include/optix.h"),
        ]
    )
    return [str(path) for path in candidates if path.exists()]


def _collect_matrix(*, pose_count: int, obstacle_count: int, link_count: int, repeats: int, warmup: int) -> dict[str, object]:
    from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
        run_performance_matrix,
    )

    return run_performance_matrix(
        dataset="scaled",
        pose_count=pose_count,
        obstacle_count=obstacle_count,
        link_count=link_count,
        repeats=repeats,
        warmup=warmup,
        include_optix=True,
    )


def collect_goal2485_pod_evidence(
    *,
    output_dir: pathlib.Path,
    build_optix: bool,
    pose_count: int,
    obstacle_count: int,
    link_count: int,
    repeats: int,
    warmup: int,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {
        "goal": "Goal2485 robot collision performance matrix",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "nvidia_smi": _check_output(["nvidia-smi"]),
        "cuda_nvcc": _nvcc_version_line(),
        "optix_prefix_env": _check_output(["bash", "-lc", "printf '%s' \"${OPTIX_PREFIX:-}\""]),
        "optix_header_candidates": _optix_header_candidates(),
        "commands": {},
        "matrix": None,
        "claim_boundary": {
            "internal_evidence_only": True,
            "public_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "authors_code_comparison_claim_authorized": False,
            "exact_solid_collision_claim_authorized": False,
            "continuous_collision_supported": False,
        },
    }
    commands = summary["commands"]
    if build_optix:
        commands["make_build_optix"] = _run_command(["make", "build-optix"])
    commands["goal2484_2485_py_compile"] = _run_command(
        [
            sys.executable,
            "-m",
            "py_compile",
            "examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py",
            "scripts/goal2485_robot_collision_matrix_pod_runner.py",
            "tests/goal2484_robot_collision_prepared_reuse_test.py",
            "tests/goal2485_robot_collision_performance_matrix_test.py",
        ]
    )
    try:
        summary["matrix"] = _collect_matrix(
            pose_count=pose_count,
            obstacle_count=obstacle_count,
            link_count=link_count,
            repeats=repeats,
            warmup=warmup,
        )
    except Exception as exc:
        summary["matrix"] = {
            "status": "error",
            "error": repr(exc),
            "traceback": traceback.format_exc(),
        }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def _summary_passed(summary: dict[str, object]) -> bool:
    for command in summary.get("commands", {}).values():
        if int(command.get("returncode", 1)) != 0:
            return False
    matrix = summary.get("matrix")
    if not isinstance(matrix, dict):
        return False
    rows = matrix.get("rows", [])
    return any(row.get("mode") == "optix_prepared" and row.get("status") == "ok" for row in rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect Goal2485 robot-collision pod performance matrix.")
    parser.add_argument("--output-dir", default="docs/reports/goal2485_robot_collision_perf_matrix_pod")
    parser.add_argument("--skip-build-optix", action="store_true")
    parser.add_argument("--pose-count", type=int, default=256)
    parser.add_argument("--obstacle-count", type=int, default=32)
    parser.add_argument("--link-count", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=9)
    parser.add_argument("--warmup", type=int, default=2)
    args = parser.parse_args(argv)
    summary = collect_goal2485_pod_evidence(
        output_dir=pathlib.Path(args.output_dir),
        build_optix=not args.skip_build_optix,
        pose_count=args.pose_count,
        obstacle_count=args.obstacle_count,
        link_count=args.link_count,
        repeats=args.repeats,
        warmup=args.warmup,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if _summary_passed(summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
