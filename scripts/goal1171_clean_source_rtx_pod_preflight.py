#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes.util
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1171 clean-source RTX pod preflight"
DEFAULT_OUTPUT = ROOT / "docs/reports/goal1171_clean_source_rtx_pod_preflight_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1171_clean_source_rtx_pod_preflight_2026-04-30.md"
DEFAULT_MANIFEST = ROOT / "docs/reports/goal1170_clean_source_rtx_batch_manifest_2026-04-30.json"
DEFAULT_RUNNER = ROOT / "scripts/goal1170_clean_source_rtx_batch_runner.sh"


def _probe(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "output_tail": completed.stdout[-4000:],
        }
    except Exception as exc:
        return {"command": command, "returncode": -1, "output_tail": str(exc)}


def _cuda_prefix() -> Path:
    if os.environ.get("CUDA_PREFIX"):
        return Path(os.environ["CUDA_PREFIX"])
    return Path("/usr/local/cuda")


def _nvcc(cuda_prefix: Path) -> Path:
    if os.environ.get("NVCC"):
        return Path(os.environ["NVCC"])
    return cuda_prefix / "bin" / "nvcc"


def _optix_library() -> Path:
    value = os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB")
    if value:
        return Path(value)
    return ROOT / "build/librtdl_optix.so"


def _geos_status() -> dict[str, Any]:
    pkg_config = shutil.which("pkg-config")
    package = None
    probes: dict[str, Any] = {}
    if pkg_config:
        for candidate in ("geos", "geos_c"):
            probe = _probe([pkg_config, "--libs", candidate])
            probes[candidate] = probe
            if probe["returncode"] == 0 and package is None:
                package = candidate
    library = ctypes.util.find_library("geos_c")
    return {
        "pkg_config": pkg_config,
        "pkg_config_geos_package": package,
        "pkg_config_probes": probes,
        "geos_c_library": library,
        "install_hint": "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config",
    }


def run_preflight(
    *,
    dry_run: bool,
    manifest_path: Path = DEFAULT_MANIFEST,
    runner_path: Path = DEFAULT_RUNNER,
) -> dict[str, Any]:
    cuda_prefix = _cuda_prefix()
    nvcc = _nvcc(cuda_prefix)
    optix_library = _optix_library()
    manifest_exists = manifest_path.exists()
    manifest: dict[str, Any] = {}
    if manifest_exists:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    git_status = _probe(["git", "status", "--short"])
    dirty = bool(git_status["output_tail"].strip())
    geos = _geos_status()
    checks = {
        "manifest_exists": manifest_exists,
        "runner_exists": runner_path.exists(),
        "manifest_has_eight_rows": len(manifest.get("rows", [])) == 8,
        "runner_refuses_dirty_tree": (
            runner_path.exists()
            and "Refusing claim-grade run: git working tree is dirty." in runner_path.read_text(encoding="utf-8")
        ),
        "source_clean": dry_run or not dirty,
        "nvidia_smi_available": dry_run or shutil.which("nvidia-smi") is not None,
        "cuda_prefix_exists": dry_run or cuda_prefix.exists(),
        "nvcc_exists": dry_run or nvcc.exists(),
        "optix_library_exists": dry_run or optix_library.exists(),
        "geos_pkg_config_available": dry_run or geos["pkg_config_geos_package"] is not None,
        "geos_c_library_available": dry_run or geos["geos_c_library"] is not None,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "goal": GOAL,
        "date": DATE,
        "dry_run": dry_run,
        "valid": not blockers,
        "checks": checks,
        "blockers": blockers,
        "manifest_path": str(manifest_path),
        "runner_path": str(runner_path),
        "environment": {
            "cuda_prefix": str(cuda_prefix),
            "nvcc": str(nvcc),
            "optix_library": str(optix_library),
            "nvidia_smi": _probe(["nvidia-smi"]) if shutil.which("nvidia-smi") else None,
            "nvcc_version": _probe([str(nvcc), "--version"]) if nvcc.exists() else None,
            "git_head": _probe(["git", "rev-parse", "HEAD"]),
            "git_status_short": git_status,
            "geos": geos,
        },
        "boundary": (
            "This preflight checks readiness for the clean-source Goal1170 RTX batch. "
            "It does not run benchmarks and does not authorize public speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1171 Clean-Source RTX Pod Preflight",
        "",
        f"Date: {payload['date']}",
        "",
        f"Dry run: `{payload['dry_run']}`",
        f"Valid: `{payload['valid']}`",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for name, result in payload["checks"].items():
        lines.append(f"| `{name}` | `{result}` |")
    lines.extend(["", "## Blockers", ""])
    if payload["blockers"]:
        for blocker in payload["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("None.")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight the clean-source Goal1170 RTX pod batch.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = run_preflight(dry_run=args.dry_run, manifest_path=args.manifest, runner_path=args.runner)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
