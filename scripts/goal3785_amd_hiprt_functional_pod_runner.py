from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v2_10_amd_hiprt_benchmark_parity import (  # noqa: E402
    summarize_v2_10_amd_hiprt_benchmark_parity,
    validate_v2_10_amd_hiprt_benchmark_parity,
)
from rtdsl.v2_10_amd_hiprt_functional_validation import (  # noqa: E402
    AMD_FUNCTIONAL_ARTIFACT,
    CLAIM_BOUNDARY,
    V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
    build_v2_10_amd_hiprt_functional_validation_runbook,
    validate_v2_10_amd_hiprt_functional_artifact,
)


DEFAULT_OUTPUT = ROOT / AMD_FUNCTIONAL_ARTIFACT
DEFAULT_NON_AMD_OUTPUT = ROOT / "docs" / "reports" / "goal3785_non_amd_hiprt_functional_runner_control.json"
FALLBACK_HIPRT_PREFIX = "~/vendor/hiprt-official/hiprtSdk-2.2.0e68f54"


def hiprt_prefix_candidate_patterns() -> tuple[str, ...]:
    home = str(Path.home())
    return (
        os.environ.get("HIPRT_PREFIX", ""),
        f"{home}/vendor/hiprt-official/hiprtSdk-2.2.0e68f54",
        f"{home}/vendor/hiprt-official/hiprtSdk-*",
        f"{home}/vendor/hiprtsdk",
        f"{home}/vendor/HIPRT",
        "/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54",
        "/root/vendor/hiprt-official/hiprtSdk-*",
        "/opt/hiprt",
        "/opt/hiprtSdk",
        "/usr/local/hiprt",
        "/usr/local/hiprtSdk",
    )


def _expand_path(value: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(value)))


def expand_hiprt_prefix_candidates(patterns: tuple[str, ...] | None = None) -> tuple[str, ...]:
    expanded: list[str] = []
    seen: set[str] = set()
    for raw in patterns if patterns is not None else hiprt_prefix_candidate_patterns():
        if not raw:
            continue
        matches = sorted(glob.glob(_expand_path(raw))) if any(token in raw for token in "*?[") else [_expand_path(raw)]
        for candidate in matches:
            if candidate not in seen:
                expanded.append(candidate)
                seen.add(candidate)
    return tuple(expanded)


def hiprt_header_exists(prefix: str) -> bool:
    return (Path(prefix) / "hiprt" / "hiprt.h").is_file()


def find_valid_hiprt_prefix(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if hiprt_header_exists(candidate):
            return candidate
    return None


def resolve_hiprt_prefix(requested: str | None = None) -> dict[str, Any]:
    if requested:
        prefix = _expand_path(requested)
        return {
            "hiprt_prefix": prefix,
            "source": "explicit_or_environment",
            "valid_header": hiprt_header_exists(prefix),
            "candidates": (),
        }

    candidates = expand_hiprt_prefix_candidates()
    discovered = find_valid_hiprt_prefix(candidates)
    if discovered is not None:
        return {
            "hiprt_prefix": discovered,
            "source": "auto_discovered",
            "valid_header": True,
            "candidates": candidates,
        }

    fallback = _expand_path(FALLBACK_HIPRT_PREFIX)
    return {
        "hiprt_prefix": fallback,
        "source": "fallback_default_missing_header",
        "valid_header": False,
        "candidates": candidates,
    }


def _run(command: list[str], *, env: dict[str, str] | None = None, timeout: int = 300) -> dict[str, Any]:
    print(f"[goal3785] run: {' '.join(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    print(f"[goal3785] exit {completed.returncode}: {' '.join(command[:2])}", flush=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
    }


def _command_stdout(command: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip()


def classify_hardware_vendor(gpu_text: str, rocm_text: str = "") -> str:
    combined = f"{gpu_text}\n{rocm_text}".lower()
    if "nvidia" in combined:
        return "nvidia"
    if any(token in combined for token in ("amd", "radeon", "instinct", "gfx")):
        return "amd"
    return "unknown"


def probe_hardware() -> dict[str, str]:
    nvidia = _command_stdout(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"])
    rocm = _command_stdout(["rocm-smi", "--showproductname", "--showdriverversion"])
    rocminfo = "" if rocm else _command_stdout(["rocminfo"])
    gpu_text = rocm or rocminfo or nvidia or "unknown"
    return {
        "hardware_vendor": classify_hardware_vendor(gpu_text, rocm or rocminfo),
        "gpu": gpu_text,
        "nvidia_smi": nvidia,
        "rocm_smi": rocm,
        "rocminfo_tail": rocminfo[-1000:],
    }


def build_non_amd_control_artifact(
    *,
    hardware_vendor: str,
    gpu: str,
    git_commit: str,
    reason: str,
) -> dict[str, Any]:
    runbook = build_v2_10_amd_hiprt_functional_validation_runbook()
    return {
        "goal": "Goal3785",
        "version": V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
        "status": "reject_non_amd_hardware",
        "hardware_vendor": hardware_vendor,
        "gpu": gpu,
        "driver": "not-applicable",
        "backend_route": "non-AMD control path; not AMD hardware evidence",
        "hiprt_sdk": "",
        "hiprt_library": "",
        "git_commit": git_commit,
        "build_command": "",
        "focused_test_modules": runbook["focused_test_modules"],
        "focused_tests_passed": False,
        "stage_counts": runbook["stage_counts"],
        "ready_for_amd_functional_pod_apps": runbook["ready_for_amd_functional_pod_apps"],
        "functional_results_by_app": {
            app: "not_run_non_amd_hardware" for app in runbook["ready_for_amd_functional_pod_apps"]
        },
        "parity_validation": validate_v2_10_amd_hiprt_benchmark_parity(),
        "scoped_source_dirty": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "rejection_reason": reason,
    }


def build_amd_functional_artifact(
    *,
    gpu: str,
    driver: str,
    hiprt_sdk: str,
    hiprt_library: str,
    git_commit: str,
    build_command: str,
    focused_tests_passed: bool,
    command_results: list[dict[str, Any]],
    scoped_source_dirty: bool = False,
) -> dict[str, Any]:
    runbook = build_v2_10_amd_hiprt_functional_validation_runbook()
    apps = tuple(runbook["ready_for_amd_functional_pod_apps"])
    return {
        "goal": "Goal3784",
        "version": V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
        "status": "amd_functional_pass" if focused_tests_passed else "amd_functional_fail",
        "hardware_vendor": "amd",
        "gpu": gpu,
        "driver": driver,
        "backend_route": "AMD HIPRT functional pod evidence",
        "hiprt_sdk": hiprt_sdk,
        "hiprt_library": hiprt_library,
        "git_commit": git_commit,
        "build_command": build_command,
        "focused_test_modules": runbook["focused_test_modules"],
        "focused_tests_passed": focused_tests_passed,
        "stage_counts": runbook["stage_counts"],
        "ready_for_amd_functional_pod_apps": apps,
        "functional_results_by_app": {app: "pass" if focused_tests_passed else "fail" for app in apps},
        "parity_validation": validate_v2_10_amd_hiprt_benchmark_parity(),
        "scoped_source_dirty": scoped_source_dirty,
        "claim_boundary": CLAIM_BOUNDARY,
        "command_results": command_results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Goal3784 AMD HIPRT functional validation gate.")
    parser.add_argument("--hiprt-prefix", default=os.environ.get("HIPRT_PREFIX"))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--non-amd-output", default=str(DEFAULT_NON_AMD_OUTPUT))
    parser.add_argument("--allow-non-amd-control", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args(argv)

    hiprt_resolution = resolve_hiprt_prefix(args.hiprt_prefix)
    hiprt_prefix = str(hiprt_resolution["hiprt_prefix"])
    print(
        f"[goal3785] HIPRT_PREFIX={hiprt_prefix} "
        f"source={hiprt_resolution['source']} valid_header={hiprt_resolution['valid_header']}",
        flush=True,
    )

    print("[goal3785] probe hardware", flush=True)
    hardware = probe_hardware()
    git_commit = _command_stdout(["git", "rev-parse", "HEAD"]) or "unknown"
    if hardware["hardware_vendor"] != "amd":
        artifact = build_non_amd_control_artifact(
            hardware_vendor=hardware["hardware_vendor"],
            gpu=hardware["gpu"],
            git_commit=git_commit,
            reason="actual AMD hardware is required before Goal3784 can produce an accepted artifact",
        )
        artifact["hiprt_prefix_resolution"] = hiprt_resolution
        output = Path(args.non_amd_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[goal3785] wrote non-AMD control artifact: {output}", flush=True)
        verdict = validate_v2_10_amd_hiprt_functional_artifact(artifact)
        print(f"[goal3785] AMD validator status for control artifact: {verdict['status']}", flush=True)
        return 0 if args.allow_non_amd_control else 2

    runbook = build_v2_10_amd_hiprt_functional_validation_runbook()
    build_command = f"make build-hiprt HIPRT_PREFIX={hiprt_prefix}"
    commands: list[dict[str, Any]] = []
    commands.append(_run(["make", "build-hiprt", f"HIPRT_PREFIX={hiprt_prefix}"], timeout=args.timeout_seconds))

    hiprt_library = str(ROOT / "build" / "librtdl_hiprt.so")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    env["RTDL_HIPRT_LIBRARY"] = hiprt_library
    test_command = [sys.executable, "-m", "unittest", *runbook["focused_test_modules"]]
    commands.append(_run(test_command, env=env, timeout=args.timeout_seconds))
    focused_tests_passed = all(result["returncode"] == 0 for result in commands)

    artifact = build_amd_functional_artifact(
        gpu=hardware["gpu"],
        driver=hardware["rocm_smi"] or "recorded-by-rocm-probe",
        hiprt_sdk=hiprt_prefix,
        hiprt_library=hiprt_library,
        git_commit=git_commit,
        build_command=build_command,
        focused_tests_passed=focused_tests_passed,
        command_results=commands,
        scoped_source_dirty=bool(_command_stdout(["git", "status", "--short"])),
    )
    artifact["hiprt_prefix_resolution"] = hiprt_resolution
    artifact["validation"] = validate_v2_10_amd_hiprt_functional_artifact(artifact)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal3785] wrote AMD functional artifact: {output}", flush=True)
    return 0 if artifact["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
