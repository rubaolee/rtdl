from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time


def run_command(argv: list[str], timeout: int = 10) -> dict[str, object]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            argv,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "seconds": time.perf_counter() - started,
        }
    except FileNotFoundError as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "seconds": time.perf_counter() - started,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": "timeout",
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
            "seconds": time.perf_counter() - started,
        }


def find_paths(names: tuple[str, ...], roots: tuple[Path, ...]) -> list[str]:
    matches: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for name in names:
            direct = root / name
            if direct.exists():
                matches.append(str(direct))
        # Keep this probe bounded; recursive filesystem search is too expensive
        # on large developer machines.
        for child in root.iterdir():
            child_name = child.name.lower()
            if any(name.lower() in child_name for name in names):
                matches.append(str(child))
    return sorted(set(matches))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe whether a host has enough HIP RT/CUDA/HIP pieces for an RTDL HIP RT feasibility test."
    )
    parser.add_argument("--machine", default=platform.node() or "unknown")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    commands = {
        "nvidia_smi_path": shutil.which("nvidia-smi"),
        "nvcc_path": shutil.which("nvcc"),
        "hipcc_path": shutil.which("hipcc"),
        "hipconfig_path": shutil.which("hipconfig"),
    }

    command_results = {}
    if commands["nvidia_smi_path"]:
        command_results["nvidia_smi_query"] = run_command(
            [
                commands["nvidia_smi_path"],
                "--query-gpu=name,driver_version,compute_cap",
                "--format=csv,noheader",
            ]
        )
    if commands["nvcc_path"]:
        command_results["nvcc_version"] = run_command([commands["nvcc_path"], "--version"])
    if commands["hipcc_path"]:
        command_results["hipcc_version"] = run_command([commands["hipcc_path"], "--version"])
    if commands["hipconfig_path"]:
        command_results["hipconfig"] = run_command([commands["hipconfig_path"], "--full"], timeout=15)

    library_probe = {}
    if shutil.which("ldconfig"):
        library_probe["ldconfig_hiprt"] = run_command(
            [
                "/bin/sh",
                "-lc",
                "ldconfig -p | grep -Ei 'hiprt|libamdhip|libcuda[^a-z]|libcudart' | head -80",
            ]
        )

    extra_roots = []
    for env_name in ("HIPRT_ROOT", "RTDL_HIPRT_ROOT"):
        env_value = os.environ.get(env_name)
        if env_value:
            extra_roots.append(Path(env_value))

    home = Path.home()
    roots = tuple(
        Path(path)
        for path in (
            "/usr/include",
            "/usr/local/include",
            "/usr/local/cuda/include",
            "/opt",
            str(home / "vendor" / "HIPRT" / "hiprt"),
            str(home / "vendor" / "hiprtsdk" / "hiprt"),
            str(home),
        )
    ) + tuple(extra_roots)
    headers = find_paths(("hiprt.h", "hiprt"), roots)
    libs = find_paths(
        ("libhiprt.so", "libhiprt", "hiprt"),
        tuple(
            Path(path)
            for path in (
                "/usr/lib",
                "/usr/local/lib",
                "/usr/local/cuda/lib64",
                "/opt",
                str(home / "vendor" / "HIPRT" / "dist" / "bin" / "Release"),
                str(home / "vendor" / "HIPRT" / "build"),
                str(home / "vendor" / "hiprtsdk" / "hiprt" / "linux64"),
                str(home),
            )
        )
        + tuple(extra_roots),
    )

    has_cuda_gpu = bool(commands["nvidia_smi_path"] and command_results.get("nvidia_smi_query", {}).get("returncode") == 0)
    has_cuda_toolchain = bool(commands["nvcc_path"])
    has_hip_toolchain = bool(commands["hipcc_path"] or commands["hipconfig_path"])
    ldconfig_stdout = str(
        library_probe.get("ldconfig_hiprt", {}).get("stdout", "")
    ).lower()
    has_hiprt_artifacts = bool(headers or libs or "hiprt" in ldconfig_stdout)

    payload = {
        "machine": args.machine,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "cwd": os.getcwd(),
        },
        "commands": commands,
        "command_results": command_results,
        "library_probe": library_probe,
        "headers_or_dirs": headers[:100],
        "libraries_or_dirs": libs[:100],
        "summary": {
            "has_cuda_gpu": has_cuda_gpu,
            "has_cuda_toolchain": has_cuda_toolchain,
            "has_hip_toolchain": has_hip_toolchain,
            "has_hiprt_artifacts": has_hiprt_artifacts,
            "can_attempt_hiprt_cuda_smoke_test": bool(has_cuda_gpu and has_cuda_toolchain and has_hiprt_artifacts),
            "can_validate_amd_gpu_backend": False,
            "reason_amd_gpu_backend_false": "This probe only checks host artifacts; AMD GPU validation requires an AMD GPU host.",
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
