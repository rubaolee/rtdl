#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPO_URL = "https://github.com/rubaolee/rtdl.git"
DEFAULT_WORKDIR = Path("/workspace/rtdl_goal1661_comprehensive")
DEFAULT_OPTIX_REF = "v8.0.0"
CURRENT_LABEL = "v1_6_11"
BASELINE_LABEL = "v1_0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        command,
        cwd=cwd,
        env=merged,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def _run_logged(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    log_path: Path,
    timeout: int | None,
) -> dict[str, Any]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    started_at = _now()
    try:
        result = _run(command, cwd=cwd, env=env, timeout=timeout)
        timed_out = False
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        returncode = 124
    elapsed = time.perf_counter() - started
    payload = {
        "command": command,
        "cwd": str(cwd),
        "elapsed_sec": elapsed,
        "env_overrides": {key: env[key] for key in sorted(env) if key.startswith("RTDL_") or key in {"PYTHONPATH", "OPTIX_PREFIX", "CUDA_PREFIX", "NVCC"}},
        "returncode": returncode,
        "started_at": started_at,
        "timed_out": timed_out,
    }
    log_path.write_text(
        "\n".join(
            [
                json.dumps(payload, indent=2, sort_keys=True),
                "",
                "===== STDOUT =====",
                stdout[-20000:],
                "",
                "===== STDERR =====",
                stderr[-20000:],
                "",
            ]
        ),
        encoding="utf-8",
    )
    payload["stdout_tail"] = stdout[-4000:]
    payload["stderr_tail"] = stderr[-4000:]
    payload["log"] = str(log_path)
    return payload


def _git_clone(repo_url: str, ref: str, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    clone = _run(["git", "clone", "--no-single-branch", repo_url, str(target)], cwd=target.parent)
    if clone.returncode != 0:
        raise RuntimeError(f"git clone failed for {target}: {clone.stderr}")
    checkout = _run(["git", "checkout", ref], cwd=target)
    if checkout.returncode != 0:
        raise RuntimeError(f"git checkout {ref} failed in {target}: {checkout.stderr}")


def _ensure_optix(prefix: Path, ref: str) -> dict[str, Any]:
    header = prefix / "include" / "optix.h"
    if header.exists():
        return {"status": "present", "prefix": str(prefix)}
    prefix.parent.mkdir(parents=True, exist_ok=True)
    if prefix.exists():
        shutil.rmtree(prefix)
    result = _run(["git", "clone", "--depth", "1", "--branch", ref, "https://github.com/NVIDIA/optix-dev.git", str(prefix)])
    return {
        "status": "ok" if result.returncode == 0 and header.exists() else "failed",
        "prefix": str(prefix),
        "returncode": result.returncode,
        "stderr_tail": result.stderr[-4000:],
    }


def _install_system_deps() -> dict[str, Any]:
    commands = [
        ["apt-get", "update"],
        [
            "apt-get",
            "install",
            "-y",
            "build-essential",
            "git",
            "cmake",
            "pkg-config",
            "libgeos-dev",
            "libembree-dev",
            "python3-dev",
            "python3-pip",
        ],
    ]
    results = []
    for command in commands:
        completed = _run(command, cwd=Path("/"))
        results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout_tail": completed.stdout[-2000:],
                "stderr_tail": completed.stderr[-2000:],
            }
        )
        if completed.returncode != 0:
            break
    return {"status": "ok" if all(row["returncode"] == 0 for row in results) else "failed", "steps": results}


def _build_checkout(checkout: Path, output_dir: Path, optix_prefix: Path, timeout: int) -> list[dict[str, Any]]:
    env = {
        "PYTHONPATH": "src:.",
        "OPTIX_PREFIX": str(optix_prefix),
    }
    steps = []
    for label, command in (
        ("build_embree", ["make", "build-embree"]),
        ("build_optix", ["make", "build-optix", f"OPTIX_PREFIX={optix_prefix}"]),
    ):
        log = output_dir / "build_logs" / f"{checkout.name}_{label}.log"
        payload = _run_logged(command, cwd=checkout, env=env, log_path=log, timeout=timeout)
        payload["label"] = label
        payload["checkout"] = checkout.name
        steps.append(payload)
    return steps


def _manifest(current_checkout: Path, output_dir: Path) -> dict[str, Any]:
    json_out = output_dir / "goal1661_source_manifest.json"
    md_out = output_dir / "goal1661_source_manifest.md"
    env = {"PYTHONPATH": "src:."}
    result = _run(
        [
            "python3",
            "scripts/goal1660_v1_6_11_vs_v1_0_perf_matrix.py",
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ],
        cwd=current_checkout,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Goal1660 manifest generation failed: {result.stderr}")
    return json.loads(json_out.read_text(encoding="utf-8"))


def _artifact_from_command(command: list[str], cwd: Path) -> Path | None:
    for flag in ("--output-json", "--json-out", "--output"):
        if flag in command:
            index = command.index(flag) + 1
            if index < len(command):
                path = Path(command[index])
                return path if path.is_absolute() else cwd / path
    return None


def _copy_artifact(artifact: Path | None, target_dir: Path, label: str) -> str | None:
    if artifact is None or not artifact.exists():
        return None
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = artifact.suffix or ".json"
    target = target_dir / f"{label}{suffix}"
    shutil.copy2(artifact, target)
    return str(target)


def _without_backend_flag(command: list[str]) -> list[str]:
    converted = list(command)
    if "--backend" not in converted:
        return converted
    index = converted.index("--backend")
    del converted[index : min(index + 2, len(converted))]
    return converted


def _baseline_command_status(command: list[str], mode: str) -> tuple[str, list[str] | None, str | None]:
    if mode == "embree_1t" or mode == "embree_auto":
        return (
            "unsupported",
            None,
            "v1.0 profiler command has no stable Embree selector for this app; do not treat the current --backend embree label as a real v1.0 Embree command",
        )
    if mode == "optix":
        return "run", _without_backend_flag(command), None
    return "run", command, None


def _engine_modes(row: dict[str, Any]) -> list[dict[str, Any]]:
    if row["engine"] == "embree":
        return [
            {"mode": "embree_1t", "env": {"RTDL_EMBREE_THREADS": "1"}},
            {"mode": "embree_auto", "env": {"RTDL_EMBREE_THREADS": "auto"}},
        ]
    if row["engine"] == "optix":
        return [{"mode": "optix", "env": {}}]
    return []


def _safe_label(*parts: str) -> str:
    return "_".join(part.replace("-", "_").replace("/", "_") for part in parts)


def _execute_rows(
    manifest: dict[str, Any],
    *,
    current_checkout: Path,
    baseline_checkout: Path,
    output_dir: Path,
    optix_prefix: Path,
    row_timeout: int,
) -> list[dict[str, Any]]:
    base_env = {
        "PYTHONPATH": "src:.",
        "OPTIX_PREFIX": str(optix_prefix),
    }
    records: list[dict[str, Any]] = []
    for row in manifest["rows"]:
        modes = _engine_modes(row)
        if row["status"] != "planned":
            for mode in modes or [{"mode": row["engine"], "env": {}}]:
                records.append(
                    {
                        "app": row["app"],
                        "engine": row["engine"],
                        "mode": mode["mode"],
                        "status": "unsupported",
                        "reason": row.get("reason") or row["status"],
                        "source_status": row["status"],
                    }
                )
            continue
        for version_label, checkout, command_key in (
            (CURRENT_LABEL, current_checkout, "v1_6_11_command"),
            (BASELINE_LABEL, baseline_checkout, "v1_0_command"),
        ):
            command = row[command_key]
            for mode in modes:
                label = _safe_label(version_label, row["app"], mode["mode"])
                actual_command = list(command)
                if version_label == BASELINE_LABEL and row["app"] != "database_analytics":
                    command_status, adapted_command, reason = _baseline_command_status(command, mode["mode"])
                    if command_status == "unsupported":
                        records.append(
                            {
                                "app": row["app"],
                                "engine": row["engine"],
                                "mode": mode["mode"],
                                "reason": reason,
                                "source_status": row["status"],
                                "status": "unsupported",
                                "version": version_label,
                            }
                        )
                        continue
                    if adapted_command is not None:
                        actual_command = adapted_command
                env = dict(base_env)
                env.update(mode["env"])
                log_path = output_dir / "logs" / f"{label}.log"
                run = _run_logged(actual_command, cwd=checkout, env=env, log_path=log_path, timeout=row_timeout)
                artifact = _artifact_from_command(actual_command, checkout)
                copied = _copy_artifact(artifact, output_dir / "artifacts", label)
                records.append(
                    {
                        "app": row["app"],
                        "artifact": copied,
                        "command": actual_command,
                        "manifest_command": command,
                        "elapsed_sec": run["elapsed_sec"],
                        "engine": row["engine"],
                        "log": run["log"],
                        "mode": mode["mode"],
                        "returncode": run["returncode"],
                        "status": "ok" if run["returncode"] == 0 else "failed",
                        "stderr_tail": run["stderr_tail"],
                        "stdout_tail": run["stdout_tail"],
                        "timed_out": run["timed_out"],
                        "version": version_label,
                    }
                )
    return records


def _speedup(old: float | None, new: float | None) -> float | None:
    if old is None or new is None or new <= 0:
        return None
    return old / new


def _summaries(records: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [row for row in records if row["status"] == "ok"]
    failed = [row for row in records if row["status"] == "failed"]
    unsupported = [row for row in records if row["status"] == "unsupported"]
    by_key = {
        (row.get("version"), row["app"], row["mode"]): row
        for row in ok
        if row.get("version")
    }
    cross_version = []
    backend = []
    apps = sorted({row["app"] for row in records})
    for app in apps:
        for mode in ("embree_1t", "embree_auto", "optix"):
            baseline = by_key.get((BASELINE_LABEL, app, mode))
            current = by_key.get((CURRENT_LABEL, app, mode))
            if baseline and current:
                cross_version.append(
                    {
                        "app": app,
                        "mode": mode,
                        "v1_0_sec": baseline["elapsed_sec"],
                        "v1_6_11_sec": current["elapsed_sec"],
                        "speedup_v1_6_11_over_v1_0": _speedup(baseline["elapsed_sec"], current["elapsed_sec"]),
                    }
                )
        for version in (BASELINE_LABEL, CURRENT_LABEL):
            optix = by_key.get((version, app, "optix"))
            for embree_mode in ("embree_1t", "embree_auto"):
                embree = by_key.get((version, app, embree_mode))
                if embree and optix:
                    backend.append(
                        {
                            "app": app,
                            "version": version,
                            "embree_mode": embree_mode,
                            "embree_sec": embree["elapsed_sec"],
                            "optix_sec": optix["elapsed_sec"],
                            "speedup_optix_over_embree": _speedup(embree["elapsed_sec"], optix["elapsed_sec"]),
                        }
                    )
    return {
        "ok_count": len(ok),
        "failed_count": len(failed),
        "unsupported_count": len(unsupported),
        "cross_version": cross_version,
        "backend": backend,
        "failed": failed,
        "unsupported": unsupported,
    }


def _format_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def _markdown(payload: dict[str, Any]) -> str:
    summaries = payload["summaries"]
    lines = [
        "# Goal1661 Comprehensive Pod Backend Comparison",
        "",
        "## Verdict",
        "",
        "`measured_evidence_only_no_release_claim`",
        "",
        "This artifact compares the current v1.6.11 candidate against v1.0 where commands are runnable, and compares Embree single-thread, Embree auto-thread, and OptiX within each version where accepted rows exist.",
        "",
        "## Environment",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Host: `{payload['environment'].get('hostname', '')}`",
        f"- Platform: `{payload['environment'].get('platform', '')}`",
        f"- Current ref: `{payload['current_ref']}`",
        f"- Baseline ref: `{payload['baseline_ref']}`",
        f"- Current commit: `{payload['current_commit']}`",
        f"- Baseline commit: `{payload['baseline_commit']}`",
        "",
        "## Counts",
        "",
        f"- OK rows: `{summaries['ok_count']}`",
        f"- Failed rows: `{summaries['failed_count']}`",
        f"- Unsupported rows: `{summaries['unsupported_count']}`",
        "",
        "## Cross-Version Timing",
        "",
        "| App | Mode | v1.0 sec | v1.6.11 sec | Speedup |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in summaries["cross_version"]:
        lines.append(
            f"| `{row['app']}` | `{row['mode']}` | {_format_float(row['v1_0_sec'])} | {_format_float(row['v1_6_11_sec'])} | {_format_float(row['speedup_v1_6_11_over_v1_0'])} |"
        )
    lines.extend(
        [
            "",
            "## Backend Timing",
            "",
            "| App | Version | Embree mode | Embree sec | OptiX sec | OptiX/Embree speedup |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in summaries["backend"]:
        lines.append(
            f"| `{row['app']}` | `{row['version']}` | `{row['embree_mode']}` | {_format_float(row['embree_sec'])} | {_format_float(row['optix_sec'])} | {_format_float(row['speedup_optix_over_embree'])} |"
        )
    lines.extend(["", "## Failing", ""])
    if summaries["failed"]:
        lines.append("| App | Version | Mode | Return code | Log |")
        lines.append("| --- | --- | --- | ---: | --- |")
        for row in summaries["failed"]:
            lines.append(f"| `{row['app']}` | `{row.get('version', '')}` | `{row['mode']}` | {row['returncode']} | `{row['log']}` |")
    else:
        lines.append("No failed executed rows.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This report is measured evidence only. It does not publish v1.6.11, authorize a tag, or authorize public speedup wording. Unsupported rows remain unsupported rather than being counted as wins or losses.",
            "",
        ]
    )
    return "\n".join(lines)


def _environment() -> dict[str, Any]:
    commands = {
        "nvidia_smi": ["nvidia-smi"],
        "nvcc": ["nvcc", "--version"],
        "python": ["python3", "--version"],
        "gcc": ["gcc", "--version"],
        "embree_pkg_config": ["pkg-config", "--modversion", "embree4"],
    }
    out: dict[str, Any] = {
        "generated_at": _now(),
        "hostname": platform.node(),
        "platform": platform.platform(),
    }
    for key, command in commands.items():
        result = _run(command, cwd=Path("/"))
        out[key] = {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[-4000:],
            "stderr": result.stderr.strip()[-4000:],
        }
    return out


def _commit(checkout: Path) -> str:
    return _run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run comprehensive v1.0/v1.6.11 Embree/OptiX pod comparison.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    parser.add_argument("--current-ref", default="main")
    parser.add_argument("--baseline-ref", default="v1.0")
    parser.add_argument("--optix-prefix", type=Path, default=Path("/opt/optix"))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--install-system-deps", action="store_true")
    parser.add_argument("--row-timeout", type=int, default=1800)
    parser.add_argument("--build-timeout", type=int, default=900)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args(argv)

    workdir = args.workdir
    output_dir = args.output_dir or workdir / "results"
    current_checkout = workdir / "rtdl_current"
    baseline_checkout = workdir / "rtdl_v1_0"
    output_dir.mkdir(parents=True, exist_ok=True)

    setup: dict[str, Any] = {"install_system_deps": None, "optix": None, "builds": []}
    if args.install_system_deps:
        setup["install_system_deps"] = _install_system_deps()
    setup["optix"] = _ensure_optix(args.optix_prefix, DEFAULT_OPTIX_REF)

    _git_clone(args.repo_url, args.current_ref, current_checkout)
    _git_clone(args.repo_url, args.baseline_ref, baseline_checkout)

    if not args.skip_build:
        setup["builds"].extend(_build_checkout(current_checkout, output_dir, args.optix_prefix, args.build_timeout))
        setup["builds"].extend(_build_checkout(baseline_checkout, output_dir, args.optix_prefix, args.build_timeout))

    manifest = _manifest(current_checkout, output_dir)
    records = _execute_rows(
        manifest,
        current_checkout=current_checkout,
        baseline_checkout=baseline_checkout,
        output_dir=output_dir,
        optix_prefix=args.optix_prefix,
        row_timeout=args.row_timeout,
    )
    payload = {
        "goal": "Goal1661 comprehensive pod backend comparison",
        "generated_at": _now(),
        "repo_url": args.repo_url,
        "current_ref": args.current_ref,
        "baseline_ref": args.baseline_ref,
        "current_commit": _commit(current_checkout),
        "baseline_commit": _commit(baseline_checkout),
        "environment": _environment(),
        "setup": setup,
        "manifest": manifest,
        "records": records,
        "summaries": _summaries(records),
        "release_authorized": False,
        "tag_authorized": False,
        "public_claim_authorized": False,
    }
    raw_json = output_dir / "goal1661_comprehensive_backend_pod_results.json"
    summary_md = output_dir / "goal1661_comprehensive_backend_pod_summary.md"
    raw_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_md.write_text(_markdown(payload), encoding="utf-8")
    print(json.dumps({"raw_json": str(raw_json), "summary_md": str(summary_md), "ok": payload["summaries"]["ok_count"], "failed": payload["summaries"]["failed_count"]}, sort_keys=True))
    return 0 if payload["summaries"]["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
