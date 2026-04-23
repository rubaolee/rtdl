#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRANCH = "codex/rtx-cloud-run-2026-04-22"
DEFAULT_OPTIX_PREFIX = Path.home() / "vendor" / "optix-dev-9.0.0"
DEFAULT_OPTIX_TAG = "v9.0.0"
DATE = "2026-04-23"


def _cuda_prefix() -> Path:
    for candidate in (Path("/usr/local/cuda"), Path("/usr/lib/cuda"), Path("/usr")):
        if (candidate / "bin" / "nvcc").exists() or (candidate / "include" / "cuda.h").exists():
            return candidate
    return Path("/usr/local/cuda")


def _nvcc(cuda_prefix: Path) -> Path:
    for candidate in (cuda_prefix / "bin" / "nvcc", Path("/usr/bin/nvcc")):
        if candidate.exists():
            return candidate
    return cuda_prefix / "bin" / "nvcc"


def _run(command: list[str], *, env: dict[str, str], dry_run: bool) -> dict[str, Any]:
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    if dry_run:
        return {
            "command": command,
            "status": "dry_run",
            "returncode": 0,
            "started_at": started,
            "elapsed_sec": 0.0,
            "stdout_tail": "",
            "stderr_tail": "",
        }
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "status": "ok" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "started_at": started,
        "elapsed_sec": time.perf_counter() - start,
        "stdout_tail": completed.stdout[-6000:],
        "stderr_tail": completed.stderr[-6000:],
    }


def _step(name: str, command: list[str], *, env: dict[str, str], dry_run: bool) -> dict[str, Any]:
    return {"name": name, "result": _run(command, env=env, dry_run=dry_run)}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _tar_reports(path: Path, *, dry_run: bool) -> dict[str, Any]:
    patterns = (
        "goal759_*_rtx.json",
        "goal761_rtx_cloud_run_all_summary.json",
        "goal762_rtx_cloud_artifact_report.*",
        "goal763_rtx_cloud_bootstrap_check.json",
        "goal769_rtx_pod_one_shot_summary*.json",
    )
    members: list[Path] = []
    for pattern in patterns:
        members.extend(sorted((ROOT / "docs" / "reports").glob(pattern)))
    if dry_run:
        return {"status": "dry_run", "path": str(path), "member_count": len(members)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz") as tar:
        for member in members:
            tar.add(member, arcname=str(member.relative_to(ROOT)))
    return {"status": "ok", "path": str(path), "member_count": len(members)}


def run_one_shot(
    *,
    branch: str,
    optix_prefix: Path,
    optix_tag: str,
    dry_run: bool,
    skip_git_update: bool,
    skip_optix_install: bool,
    output_json: Path,
    artifact_json: Path,
    artifact_md: Path,
    bundle_tgz: Path,
    include_deferred: bool,
    only: tuple[str, ...],
) -> dict[str, Any]:
    cuda_prefix = _cuda_prefix()
    nvcc = _nvcc(cuda_prefix)
    env = {
        **os.environ,
        "PYTHONPATH": "src:.",
        "OPTIX_PREFIX": str(optix_prefix),
        "CUDA_PREFIX": str(cuda_prefix),
        "NVCC": str(nvcc),
        "RTDL_OPTIX_LIB": str(ROOT / "build" / "librtdl_optix.so"),
        "RTDL_OPTIX_PTX_COMPILER": "nvcc",
        "RTDL_NVCC": str(nvcc),
    }
    steps: list[dict[str, Any]] = []
    if not skip_git_update:
        steps.append(_step("git_fetch", ["git", "fetch", "origin", branch], env=env, dry_run=dry_run))
        if steps[-1]["result"]["status"] in {"ok", "dry_run"}:
            steps.append(
                _step(
                    "git_checkout_branch",
                    ["git", "checkout", "-B", branch, f"origin/{branch}"],
                    env=env,
                    dry_run=dry_run,
                )
            )
    optix_header = optix_prefix / "include" / "optix.h"
    if not skip_optix_install and (dry_run or not optix_header.exists()):
        steps.append(
            _step(
                "install_optix_dev_headers",
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    optix_tag,
                    "https://github.com/NVIDIA/optix-dev.git",
                    str(optix_prefix),
                ],
                env=env,
                dry_run=dry_run,
            )
        )

    failed_before_bootstrap = any(step["result"]["status"] == "failed" for step in steps)
    if not failed_before_bootstrap:
        steps.append(
            _step(
                "goal763_bootstrap",
                [
                    sys.executable,
                    "scripts/goal763_rtx_cloud_bootstrap_check.py",
                    "--output-json",
                    "docs/reports/goal763_rtx_cloud_bootstrap_check.json",
                ],
                env=env,
                dry_run=dry_run,
            )
        )
    if not any(step["result"]["status"] == "failed" for step in steps):
        manifest_command = [
            sys.executable,
            "scripts/goal761_rtx_cloud_run_all.py",
            "--output-json",
            "docs/reports/goal761_rtx_cloud_run_all_summary.json",
        ]
        if include_deferred:
            manifest_command.append("--include-deferred")
        for item in only:
            manifest_command.extend(["--only", item])
        steps.append(
            _step(
                "goal761_run_manifest",
                manifest_command,
                env=env,
                dry_run=dry_run,
            )
        )
    if not any(step["result"]["status"] == "failed" for step in steps):
        steps.append(
            _step(
                "goal762_analyze_artifacts",
                [
                    sys.executable,
                    "scripts/goal762_rtx_cloud_artifact_report.py",
                    "--summary-json",
                    "docs/reports/goal761_rtx_cloud_run_all_summary.json",
                    "--output-json",
                    str(artifact_json.relative_to(ROOT)),
                    "--output-md",
                    str(artifact_md.relative_to(ROOT)),
                ],
                env=env,
                dry_run=dry_run,
            )
        )

    payload = {
        "suite": "goal769_rtx_pod_one_shot",
        "date": DATE,
        "repo": str(ROOT),
        "branch": branch,
        "dry_run": dry_run,
        "optix_prefix": str(optix_prefix),
        "cuda_prefix": str(cuda_prefix),
        "nvcc": str(nvcc),
        "include_deferred": include_deferred,
        "only": list(only),
        "steps": steps,
        "status": "ok" if not any(step["result"]["status"] == "failed" for step in steps) else "failed",
        "boundary": (
            "This one-shot runner is an execution bundle for paid RTX pod time. "
            "It does not authorize public RTX speedup claims; generated artifacts still require review."
        ),
    }
    _write_json(output_json, payload)
    bundle = _tar_reports(bundle_tgz, dry_run=dry_run)
    payload["artifact_bundle"] = bundle
    _write_json(output_json, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RTX pod bootstrap, benchmarks, artifact report, and bundle in one pass.")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--optix-prefix", default=str(DEFAULT_OPTIX_PREFIX))
    parser.add_argument("--optix-tag", default=DEFAULT_OPTIX_TAG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-git-update", action="store_true")
    parser.add_argument("--skip-optix-install", action="store_true")
    parser.add_argument("--include-deferred", action="store_true", help="Pass through to Goal761 so one pod run can include deferred readiness gates.")
    parser.add_argument("--only", action="append", default=[], help="Pass through an app or manifest path_name filter to Goal761. May be repeated.")
    parser.add_argument("--output-json", default=f"docs/reports/goal769_rtx_pod_one_shot_summary_{DATE}.json")
    parser.add_argument("--artifact-json", default=f"docs/reports/goal762_rtx_cloud_artifact_report_{DATE}.json")
    parser.add_argument("--artifact-md", default=f"docs/reports/goal762_rtx_cloud_artifact_report_{DATE}.md")
    parser.add_argument("--bundle-tgz", default=f"docs/reports/goal769_rtx_pod_artifacts_{DATE}.tgz")
    args = parser.parse_args(argv)
    payload = run_one_shot(
        branch=args.branch,
        optix_prefix=Path(args.optix_prefix),
        optix_tag=args.optix_tag,
        dry_run=args.dry_run,
        skip_git_update=args.skip_git_update,
        skip_optix_install=args.skip_optix_install,
        output_json=ROOT / args.output_json,
        artifact_json=ROOT / args.artifact_json,
        artifact_md=ROOT / args.artifact_md,
        bundle_tgz=ROOT / args.bundle_tgz,
        include_deferred=args.include_deferred,
        only=tuple(args.only),
    )
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
