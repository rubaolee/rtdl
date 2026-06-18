from __future__ import annotations

import argparse
import importlib
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


PACKET_VERSION = "rtdl.v3_0.toolchain_support_matrix.goal4604.v1"
OUT_JSON = Path("docs/reports/goal4604_v3_0_m205_toolchain_support_matrix_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4604_v3_0_m205_toolchain_support_matrix_2026-06-17.md")
TOOLCHAIN_DOC = Path("docs/learn/v3_0_toolchain_support_matrix.md")
LEARN_README = Path("docs/learn/README.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
GOAL4546_REPORT = Path("docs/reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.json")
GOAL4603_REPORT = Path("docs/reports/goal4603_v3_0_m204_embeddability_delivery_archive_cmake_refresh_2026-06-17.json")


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _run_command(command: list[str]) -> dict[str, Any]:
    executable = shutil.which(command[0])
    result: dict[str, Any] = {
        "command": command,
        "executable": executable,
        "ok": False,
        "returncode": None,
        "stdout_tail": (),
        "stderr_tail": (),
    }
    if executable is None:
        return result
    completed = subprocess.run(
        [executable, *command[1:]],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    result.update(
        {
            "command": [executable, *command[1:]],
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout_tail": _tail(completed.stdout),
            "stderr_tail": _tail(completed.stderr),
        }
    )
    return result


def _import_package(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        return {"ok": False, "version": None, "error": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, "version": getattr(module, "__version__", None), "error": None}


def _cupy_runtime_version() -> dict[str, Any]:
    try:
        import cupy

        return {"ok": True, "runtime_version": cupy.cuda.runtime.runtimeGetVersion(), "error": None}
    except Exception as exc:
        return {"ok": False, "runtime_version": None, "error": f"{type(exc).__name__}: {exc}"}


def run_probe(root: Path) -> dict[str, Any]:
    commands = {
        "cc": _run_command(["cc", "--version"]),
        "make": _run_command(["make", "--version"]),
        "cmake": _run_command(["cmake", "--version"]),
        "pkg_config": _run_command(["pkg-config", "--version"]),
        "nvidia_smi": _run_command(["nvidia-smi", "--query-gpu=driver_version,name", "--format=csv,noheader"]),
        "nvcc": _run_command(["nvcc", "--version"]),
    }
    packages = {name: _import_package(name) for name in ("numpy", "cupy", "numba")}
    libraries = {
        "rtdl_optix": (root / "build" / "librtdl_optix.so").exists()
        or (root / "build" / "librtdl_optix.dll").exists(),
        "rtdl_embree": (root / "build" / "librtdl_embree.so").exists()
        or (root / "build" / "rtdl_embree.dll").exists()
        or (root / "build" / "librtdl_embree.dll").exists(),
        "rtdl_c_api": (root / "build" / "librtdl_c_api.so").exists()
        or (root / "build" / "rtdl_c_api.dll").exists()
        or (root / "build" / "librtdl_c_api.dll").exists(),
        "c_api_stage_archive": (root / "build" / "rtdl-c-api-stage-0.1.3.tar.gz").exists(),
    }
    return {
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "commands": commands,
        "packages": packages,
        "cupy_runtime": _cupy_runtime_version(),
        "libraries": libraries,
    }


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_packet(root: Path = Path("."), *, run_live_probe: bool = False) -> dict[str, Any]:
    doc = (root / TOOLCHAIN_DOC).read_text(encoding="utf-8")
    learn = (root / LEARN_README).read_text(encoding="utf-8")
    doctor = (root / DOCTOR).read_text(encoding="utf-8")
    doctor_doc = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    goal4546 = _load_json(root, GOAL4546_REPORT)
    goal4603 = _load_json(root, GOAL4603_REPORT)
    probe = run_probe(root) if run_live_probe else None
    checks = {
        "toolchain_doc_exists_and_sets_boundary": "observed on this pod" in doc
        and "not a release support guarantee" in doc
        and "`nvcc` in `PATH` is not required" in doc,
        "learn_readme_links_toolchain_matrix": "V3.0 Toolchain Support Matrix" in learn,
        "doctor_requires_toolchain_doc": "v3_0_toolchain_support_matrix.md" in doctor,
        "doctor_doc_names_toolchain_support": "toolchain support" in doctor_doc,
        "v3_current_report_is_goal4603_ready": goal4546["suite_run"]["ok"]
        and goal4546["suite_run"]["module_count"] >= 93,
        "embeddability_delivery_goal4603_accepts": tuple(goal4603["failed_checks"]) == (),
    }
    if probe is not None:
        checks.update(
            {
                "python_probe_available": bool(probe["python"]["version"]),
                "cc_available": probe["commands"]["cc"]["ok"],
                "make_available": probe["commands"]["make"]["ok"],
                "cmake_available": probe["commands"]["cmake"]["ok"],
                "pkg_config_available": probe["commands"]["pkg_config"]["ok"],
                "nvidia_smi_available": probe["commands"]["nvidia_smi"]["ok"],
                "numpy_importable": probe["packages"]["numpy"]["ok"],
                "cupy_importable": probe["packages"]["cupy"]["ok"],
                "numba_importable": probe["packages"]["numba"]["ok"],
                "cupy_cuda_runtime_observed": probe["cupy_runtime"]["ok"],
                "optix_library_present": probe["libraries"]["rtdl_optix"],
                "embree_library_present": probe["libraries"]["rtdl_embree"],
                "c_api_library_present": probe["libraries"]["rtdl_c_api"],
                "c_api_stage_archive_present": probe["libraries"]["c_api_stage_archive"],
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4604 / V3 M205",
        "status": "toolchain_support_matrix_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "live_probe": probe,
        "claim_boundary": {
            "pod_toolchain_observation_authorized": run_live_probe and not failed,
            "stable_platform_support_authorized": False,
            "packaged_sdk_authorized": False,
            "system_install_authorized": False,
            "stable_abi_authorized": False,
            "public_performance_claim_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4604 adds a V3 toolchain support matrix and, when run on the pod, "
            "records the live Python/C compiler/make/CMake/pkg-config/NVIDIA/CuPy/"
            "Numba/native-library observations needed to interpret current V3 "
            "embeddability evidence. This is pod-specific source-tree evidence, not "
            "a stable platform support promise, packaged SDK, system install, stable "
            "ABI, performance claim, or release authorization."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    probe = packet["live_probe"] or {}
    commands = probe.get("commands", {})
    packages = probe.get("packages", {})
    libraries = probe.get("libraries", {})
    lines = [
        "# Goal4604 / V3 M205 Toolchain Support Matrix",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Live Probe",
        "",
        f"- Python: `{(probe.get('python') or {}).get('version')}`",
        f"- NVIDIA: `{'; '.join(commands.get('nvidia_smi', {}).get('stdout_tail', ()))}`",
        f"- CuPy: `{(packages.get('cupy') or {}).get('version')}`; runtime `{(probe.get('cupy_runtime') or {}).get('runtime_version')}`",
        f"- Numba: `{(packages.get('numba') or {}).get('version')}`",
        f"- NVCC in PATH: `{commands.get('nvcc', {}).get('ok')}`",
        "",
        "## Native Artifacts",
        "",
        "| Artifact | Present |",
        "| --- | --- |",
    ]
    for name, present in libraries.items():
        lines.append(f"| `{name}` | `{present}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a pod-specific source-tree support observation.",
            "- It does not authorize stable platform support, packaged SDK, system install, stable ABI, public performance claims, or release wording.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-live-probe", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_live_probe=not args.no_live_probe)
    if not args.no_write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
