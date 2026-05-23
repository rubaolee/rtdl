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


GOAL2483_MODULE = "tests.goal2483_robot_collision_optix_contract_test"
GOAL2479_TO_2483_MODULES = (
    "tests.goal2479_robot_collision_benchmark_roadmap_test",
    "tests.goal2480_robot_collision_cpu_reference_app_test",
    "tests.goal2481_robot_collision_generic_contract_design_test",
    "tests.goal2482_robot_collision_embree_contract_test",
    GOAL2483_MODULE,
)


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


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    prefix = f"{ROOT / 'src'}:{ROOT}"
    env["PYTHONPATH"] = f"{prefix}:{existing}" if existing else prefix
    return env


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
    env_candidates = []
    for variable in ("OPTIX_PREFIX", "RTDL_OPTIX_PREFIX", "OptiX_INSTALL_DIR"):
        value = os.environ.get(variable)
        if value:
            env_candidates.append(pathlib.Path(value) / "include" / "optix.h")
    candidates = [
        *env_candidates,
        ROOT / "optix" / "include" / "optix.h",
        pathlib.Path("/workspace/vendor/optix-dev/include/optix.h"),
        pathlib.Path("/workspace/vendor/optix-dev-8.0.0/include/optix.h"),
        pathlib.Path("/workspace/vendor/optix-dev-9.0.0/include/optix.h"),
        pathlib.Path("/root/vendor/optix-dev/include/optix.h"),
        pathlib.Path("/root/vendor/optix-sdk/include/optix.h"),
        pathlib.Path("/opt/optix/include/optix.h"),
        pathlib.Path("/usr/local/NVIDIA-OptiX-SDK/include/optix.h"),
        pathlib.Path("/usr/local/NVIDIA-OptiX-SDK-9.0.0-linux64-x86_64/include/optix.h"),
        pathlib.Path.home() / "NVIDIA-OptiX-SDK" / "include" / "optix.h",
        pathlib.Path.home() / "NVIDIA-OptiX-SDK-9.0.0-linux64-x86_64" / "include" / "optix.h",
        pathlib.Path.home() / "Downloads" / "NVIDIA-OptiX-SDK" / "include" / "optix.h",
        pathlib.Path.home() / "Downloads" / "NVIDIA-OptiX-SDK-9.0.0-linux64-x86_64" / "include" / "optix.h",
    ]
    return [str(path) for path in candidates if path.exists()]


def _run_runtime_probe() -> dict[str, object]:
    try:
        from rtdsl import run_optix_grouped_segment_any_hit_flags_3d
        from tests.goal2483_robot_collision_optix_contract_test import (
            EXPECTED_FLAGS,
            GROUP_OFFSETS,
            SEGMENT_ENDS,
            SEGMENT_STARTS,
            TRIANGLES,
        )

        start = time.perf_counter()
        result = run_optix_grouped_segment_any_hit_flags_3d(
            TRIANGLES,
            SEGMENT_STARTS,
            SEGMENT_ENDS,
            GROUP_OFFSETS,
        )
        elapsed = time.perf_counter() - start
        flags_match = list(result.get("flags", ())) == list(EXPECTED_FLAGS)
        return {
            "ok": bool(flags_match),
            "elapsed_sec": elapsed,
            "expected_flags": list(EXPECTED_FLAGS),
            "result": result,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": repr(exc),
            "traceback": traceback.format_exc(),
        }


def collect_goal2483_pod_evidence(
    *,
    output_dir: pathlib.Path,
    build_optix: bool,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {
        "goal": "Goal2483 OptiX contract parity",
        "contract": "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "nvidia_smi": _check_output(["nvidia-smi"]),
        "cuda_nvcc": _nvcc_version_line(),
        "optix_prefix_env": _check_output(["bash", "-lc", "printf '%s' \"${OPTIX_PREFIX:-}\""]),
        "optix_header_candidates": _optix_header_candidates(),
        "commands": {},
        "runtime_probe": None,
        "claim_boundary": {
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim": False,
            "native_app_api": False,
            "exact_solid_contact": False,
            "continuous_swept_support": False,
            "release_action": False,
            "row_witnesses": False,
        },
    }

    commands = summary["commands"]
    if build_optix:
        commands["make_build_optix"] = _run_command(["make", "build-optix"])

    commands["goal2483_py_compile"] = _run_command(
        [
            sys.executable,
            "-m",
            "py_compile",
            "src/rtdsl/optix_runtime.py",
            "src/rtdsl/__init__.py",
            "tests/goal2483_robot_collision_optix_contract_test.py",
        ]
    )
    commands["goal2483_unittest"] = _run_command([sys.executable, "-m", "unittest", GOAL2483_MODULE])
    commands["goal2479_to_2483_unittest"] = _run_command(
        [sys.executable, "-m", "unittest", *GOAL2479_TO_2483_MODULES]
    )
    summary["runtime_probe"] = _run_runtime_probe()

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def _summary_passed(summary: dict[str, object]) -> bool:
    commands = summary.get("commands", {})
    for command in commands.values():
        if int(command.get("returncode", 1)) != 0:
            return False
    runtime_probe = summary.get("runtime_probe")
    return bool(isinstance(runtime_probe, dict) and runtime_probe.get("ok") is True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect Goal2483 OptiX pod validation evidence.")
    parser.add_argument("--output-dir", default="docs/reports/goal2483_optix_contract_pod")
    parser.add_argument("--skip-build-optix", action="store_true")
    args = parser.parse_args(argv)
    summary = collect_goal2483_pod_evidence(
        output_dir=pathlib.Path(args.output_dir),
        build_optix=not args.skip_build_optix,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if _summary_passed(summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
