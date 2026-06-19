#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int = 120,
) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "ok": completed.returncode == 0,
    }


def _git_value(*args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_failed_from_missing_ensurepip(command: dict[str, Any]) -> bool:
    text = f"{command.get('stdout', '')}\n{command.get('stderr', '')}"
    return "ensurepip is not" in text or "python3-venv" in text


def _create_venv(
    *,
    venv_dir: Path,
    outside_cwd: Path,
    env: dict[str, str],
    system_site_packages: bool,
) -> tuple[list[dict[str, Any]], str | None]:
    commands: list[dict[str, Any]] = []
    venv_command = [sys.executable, "-m", "venv"]
    if system_site_packages:
        venv_command.append("--system-site-packages")
    venv_command.append(str(venv_dir))
    commands.append(_run(venv_command, cwd=outside_cwd, env=env))
    if commands[-1]["ok"]:
        return commands, "stdlib_venv"
    if not _venv_failed_from_missing_ensurepip(commands[-1]):
        return commands, None

    if venv_dir.exists():
        shutil.rmtree(venv_dir, ignore_errors=True)
    fallback = [sys.executable, "-m", "venv"]
    if system_site_packages:
        fallback.append("--system-site-packages")
    fallback.extend(["--without-pip", str(venv_dir)])
    commands.append(_run(fallback, cwd=outside_cwd, env=env))
    if commands[-1]["ok"]:
        return commands, "stdlib_venv_without_pip_targeted_by_system_pip"
    return commands, None


def _pip_install_command(*, python: Path, creation_method: str | None) -> list[str]:
    if creation_method == "stdlib_venv_without_pip_targeted_by_system_pip":
        return [
            sys.executable,
            "-m",
            "pip",
            "--python",
            str(python),
            "install",
            "-e",
            str(ROOT),
        ]
    return [str(python), "-m", "pip", "install", "-e", str(ROOT)]


def _clean_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env.pop("RTDL_OPTIX_LIB", None)
    return env


def _inspection_code(*, run_v4_smoke: bool) -> str:
    smoke = "True" if run_v4_smoke else "False"
    return f"""
from __future__ import annotations
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys

repo = Path({str(ROOT)!r}).resolve()
payload = {{
    "python": sys.version,
    "executable": sys.executable,
    "cwd": os.getcwd(),
    "pythonpath_present": "PYTHONPATH" in os.environ,
    "repo": str(repo),
}}

import rtdsl
payload["package"] = {{
    "distribution_name": "rtdl-source-tree",
    "version": metadata.version("rtdl-source-tree"),
    "module_file": str(Path(rtdsl.__file__).resolve()),
}}
payload["package"]["module_under_repo_src"] = (
    Path(rtdsl.__file__).resolve().is_relative_to(repo / "src" / "rtdsl")
)
payload["package"]["module_loaded_from_checkout_editable"] = payload["package"]["module_under_repo_src"]

from rtdsl import optix_runtime
try:
    native_path = optix_runtime._find_optix_library()
    payload["native_library"] = {{
        "status": "found",
        "path": str(Path(native_path).resolve()) if not str(native_path).startswith("lib") else str(native_path),
        "under_repo_build": (
            Path(native_path).resolve().is_relative_to(repo / "build")
            if Path(native_path).is_absolute() or Path(native_path).exists()
            else False
        ),
        "env_rtdl_optix_lib_present": "RTDL_OPTIX_LIB" in os.environ,
    }}
except Exception as exc:
    payload["native_library"] = {{
        "status": "missing",
        "error": type(exc).__name__ + ": " + str(exc),
        "env_rtdl_optix_lib_present": "RTDL_OPTIX_LIB" in os.environ,
    }}

payload["v4_smoke"] = {{"requested": {smoke}, "status": "not_run"}}
if {smoke} and payload["native_library"]["status"] != "found":
    payload["v4_smoke"] = {{
        "requested": True,
        "status": "blocked_missing_native_library",
        "native_library_status": payload["native_library"]["status"],
        "native_library_error": payload["native_library"].get("error"),
    }}
elif {smoke}:
    import cupy as cp

    search = {{
        "ids": cp.asarray([10, 11, 12], dtype=cp.uint32),
        "x": cp.asarray([0.0, 3.0, 0.0], dtype=cp.float64),
        "y": cp.asarray([0.0, 0.0, 4.0], dtype=cp.float64),
    }}
    query = {{
        "ids": cp.asarray([1, 2, 3], dtype=cp.uint32),
        "x": cp.asarray([0.0, 3.0, 9.0], dtype=cp.float64),
        "y": cp.asarray([0.0, 0.0, 9.0], dtype=cp.float64),
    }}
    outputs = {{
        "query_ids": cp.zeros((3,), dtype=cp.uint32),
        "neighbor_counts": cp.zeros((3,), dtype=cp.uint32),
        "threshold_flags": cp.zeros((3,), dtype=cp.uint32),
    }}
    stream = cp.cuda.Stream(non_blocking=True)
    with stream:
        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=1.1,
            threshold=1,
            partner="cupy",
            output_columns=outputs,
            stream=stream.ptr,
            return_metadata=True,
        )
    stream.synchronize()
    observed = {{name: outputs[name].get().tolist() for name in outputs}}
    expected = {{
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }}
    if observed != expected:
        raise AssertionError(f"unexpected V4 fixed-radius output: {{observed!r}}")
    meta = result["metadata"]
    payload["v4_smoke"] = {{
        "requested": True,
        "status": "pass",
        "observed": observed,
        "expected": expected,
        "caller_stream_handle_nonzero": int(stream.ptr) != 0,
        "native_synchronized_before_return": bool(meta["native_synchronized_before_return"]),
        "native_async_ready": bool(meta["native_async_ready"]),
        "native_async_ready_is_metadata_only": True,
        "native_async_claim_authorized": False,
        "public_true_zero_copy_authorized": bool(meta["v4_true_zero_copy_claim_authorized"]),
    }}

print(json.dumps(payload, sort_keys=True))
"""


def build_payload(*, run_v4_smoke: bool, system_site_packages: bool, keep_venv: bool) -> dict[str, Any]:
    temp_root = Path(tempfile.mkdtemp(prefix="rtdl_v4_editable_install_"))
    venv_dir = temp_root / "venv"
    outside_cwd = temp_root / "outside_cwd"
    outside_cwd.mkdir(parents=True, exist_ok=True)
    env = _clean_env()
    commands: list[dict[str, Any]] = []
    failures: list[str] = []
    creation_method: str | None = None

    try:
        venv_commands, creation_method = _create_venv(
            venv_dir=venv_dir,
            outside_cwd=outside_cwd,
            env=env,
            system_site_packages=system_site_packages,
        )
        commands.extend(venv_commands)
        if not creation_method:
            failures.append("venv_create_failed")
            return _payload(
                temp_root,
                venv_dir,
                outside_cwd,
                commands,
                failures,
                system_site_packages,
                run_v4_smoke,
                creation_method=creation_method,
            )

        python = _venv_python(venv_dir)
        install = _run(
            _pip_install_command(python=python, creation_method=creation_method),
            cwd=outside_cwd,
            env=env,
            timeout=300,
        )
        commands.append(install)
        if not install["ok"]:
            failures.append("editable_install_failed")
            return _payload(
                temp_root,
                venv_dir,
                outside_cwd,
                commands,
                failures,
                system_site_packages,
                run_v4_smoke,
                creation_method=creation_method,
            )

        inspect = _run(
            [str(python), "-c", _inspection_code(run_v4_smoke=run_v4_smoke)],
            cwd=outside_cwd,
            env=env,
            timeout=180,
        )
        commands.append(inspect)
        inspection: dict[str, Any] | None = None
        if inspect["ok"]:
            try:
                inspection = json.loads(inspect["stdout"])
            except json.JSONDecodeError as exc:
                failures.append(f"inspection_json_decode_failed:{exc}")
        else:
            failures.append("inspection_failed")

        payload = _payload(
            temp_root,
            venv_dir,
            outside_cwd,
            commands,
            failures,
            system_site_packages,
            run_v4_smoke,
            inspection=inspection,
            creation_method=creation_method,
        )

        if inspection:
            package = inspection.get("package", {})
            if package.get("version") != "3.0.2":
                payload["failures"].append("unexpected_distribution_version")
            if not package.get("module_loaded_from_checkout_editable"):
                payload["failures"].append("module_not_loaded_from_checkout_editable")
            if inspection.get("pythonpath_present"):
                payload["failures"].append("pythonpath_leaked_into_probe")
            if run_v4_smoke and inspection.get("v4_smoke", {}).get("status") != "pass":
                payload["failures"].append("v4_smoke_not_passed")
        payload["ok"] = not payload["failures"]
        payload["status"] = "pass" if payload["ok"] else "fail"
        return payload
    finally:
        if not keep_venv:
            shutil.rmtree(temp_root, ignore_errors=True)


def _payload(
    temp_root: Path,
    venv_dir: Path,
    outside_cwd: Path,
    commands: list[dict[str, Any]],
    failures: list[str],
    system_site_packages: bool,
    run_v4_smoke: bool,
    *,
    inspection: dict[str, Any] | None = None,
    creation_method: str | None = None,
) -> dict[str, Any]:
    return {
        "report_id": "v4_0_editable_install_runtime_probe_2026-06-19",
        "status": "fail" if failures else "pass",
        "ok": not failures,
        "repo": str(ROOT),
        "git": {
            "head": _git_value("rev-parse", "HEAD"),
            "tree": _git_value("rev-parse", "HEAD^{tree}"),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "temp_root": str(temp_root),
        "venv_dir": str(venv_dir),
        "outside_cwd": str(outside_cwd),
        "system_site_packages": system_site_packages,
        "venv_creation_method": creation_method,
        "run_v4_smoke": run_v4_smoke,
        "commands": commands,
        "inspection": inspection,
        "failures": failures,
        "claim_boundaries": {
            "editable_source_tree_install_hygiene_evidence": not failures,
            "v4_distribution_artifact": False,
            "package_install_claim_authorized": False,
            "pypi_claim_authorized": False,
            "wheel_claim_authorized": False,
            "stable_sdk_claim_authorized": False,
            "generated_binding_package_claim_authorized": False,
            "v4_current_front_door_authorized": False,
            "async_claim_authorized": False,
            "native_async_claim_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
        },
        "notes": [
            "This validates local editable source-tree import hygiene only.",
            "It does not authorize PyPI, wheel, stable SDK, generated binding, or V4 distribution wording.",
            "The probe intentionally runs from outside the repository with PYTHONPATH unset.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe V4 editable-install runtime hygiene.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    parser.add_argument("--run-v4-smoke", action="store_true", help="Run a minimal CuPy V4 M1 route smoke.")
    parser.add_argument(
        "--system-site-packages",
        action="store_true",
        help="Create the temporary venv with access to existing GPU framework installs.",
    )
    parser.add_argument("--keep-venv", action="store_true", help="Keep the temporary venv for debugging.")
    args = parser.parse_args()

    payload = build_payload(
        run_v4_smoke=args.run_v4_smoke,
        system_site_packages=args.system_site_packages,
        keep_venv=args.keep_venv,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
