#!/usr/bin/env python3
"""Run repeated Goal1579 OptiX collect-k validation sessions and aggregate them.

This runner is for validation logistics only. It does not promote
COLLECT_K_BOUNDED, does not change default behavior, and does not authorize
public speedup claims.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TARGET_COUNTS = (49153, 65536, 65537)


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_text(cmd: list[str]) -> str:
    try:
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return "unavailable"
    if completed.returncode != 0:
        return "unavailable"
    return completed.stdout.strip()


def _gpu_metadata(device_label: str | None) -> dict[str, Any]:
    query = _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version",
            "--format=csv,noheader",
        ]
    )
    smi_banner = _run_text(["nvidia-smi"])
    cuda_version = "unavailable"
    marker = "CUDA Version:"
    if marker in smi_banner:
        cuda_version = smi_banner.split(marker, 1)[1].split("|", 1)[0].strip()
    devices = []
    if query != "unavailable":
        for line in query.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) == 2:
                devices.append(
                    {
                        "name": parts[0],
                        "driver_version": parts[1],
                        "cuda_version": cuda_version,
                    }
                )
    return {
        "device_label": device_label,
        "nvidia_smi_query": query,
        "nvidia_smi_cuda_version": cuda_version,
        "devices": devices,
    }


def _parse_cuda_version(text: str) -> tuple[int, int] | None:
    match = re.search(r"(\d+)\.(\d+)", text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _toolkit_version(cuda_prefix: str | None) -> tuple[str, tuple[int, int] | None]:
    candidates: list[Path] = []
    if cuda_prefix:
        candidates.append(Path(cuda_prefix) / "bin" / "nvcc")
    candidates.extend([Path("/usr/local/cuda/bin/nvcc"), Path("/usr/bin/nvcc")])
    for nvcc in candidates:
        if not nvcc.exists():
            continue
        output = _run_text([str(nvcc), "--version"])
        parsed = _parse_cuda_version(output)
        if parsed:
            return str(nvcc), parsed
    return "unavailable", None


def _preflight_cuda_toolchain(*, cuda_prefix: str | None, ld_library_path: str | None, skip: bool) -> dict[str, Any]:
    metadata = _gpu_metadata(None)
    driver_cuda = _parse_cuda_version(metadata.get("nvidia_smi_cuda_version", ""))
    nvcc_path, toolkit_cuda = _toolkit_version(cuda_prefix)
    ld_path = ld_library_path or os.environ.get("LD_LIBRARY_PATH", "")
    has_compat = any("compat" in part for part in ld_path.split(os.pathsep))
    result = {
        "driver_cuda": driver_cuda,
        "nvcc_path": nvcc_path,
        "toolkit_cuda": toolkit_cuda,
        "ld_library_path": ld_path,
        "has_cuda_compat_path": has_compat,
        "skipped": skip,
    }
    if skip or not driver_cuda or not toolkit_cuda:
        return result
    if toolkit_cuda > driver_cuda and not has_compat:
        raise RuntimeError(
            "RTDL OptiX CUDA preflight failed: nvcc reports CUDA "
            f"{toolkit_cuda[0]}.{toolkit_cuda[1]}, but nvidia-smi reports driver CUDA "
            f"{driver_cuda[0]}.{driver_cuda[1]} and LD_LIBRARY_PATH has no CUDA compat directory. "
            "Use a driver-compatible CUDA toolkit, add the appropriate CUDA compat library path first in "
            "LD_LIBRARY_PATH, or pass --skip-cuda-toolchain-preflight only for diagnostic runs."
        )
    if has_compat and toolkit_cuda <= driver_cuda:
        raise RuntimeError(
            "RTDL OptiX CUDA preflight failed: LD_LIBRARY_PATH contains a CUDA compat directory, "
            f"but nvidia-smi reports driver CUDA {driver_cuda[0]}.{driver_cuda[1]} and nvcc reports CUDA "
            f"{toolkit_cuda[0]}.{toolkit_cuda[1]}. Remove the compat directory so RTDL loads the installed "
            "driver's libcuda, or pass --skip-cuda-toolchain-preflight only for diagnostic runs."
        )
    return result


def _case_map(data: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(case["candidate_count"]): case for case in data.get("cases", [])}


def _targeted_rows(prefix: Path) -> list[dict[str, Any]]:
    targeted_baseline = _case_map(_load(prefix.with_name(f"{prefix.name}_targeted_baseline.json")))
    targeted_alias = _case_map(_load(prefix.with_name(f"{prefix.name}_targeted_alias.json")))
    candidate_preset = _case_map(_load(prefix.with_name(f"{prefix.name}_candidate_preset.json")))
    rows: list[dict[str, Any]] = []
    for count in TARGET_COUNTS:
        baseline = targeted_baseline[count]
        alias = targeted_alias[count]
        candidate = candidate_preset[count]
        baseline_ms = float(baseline["stage_profile"]["stage_median_ms"]["total_ms"])
        alias_ms = float(alias["stage_profile"]["stage_median_ms"]["total_ms"])
        candidate_ms = float(candidate["stage_profile"]["stage_median_ms"]["total_ms"])
        rows.append(
            {
                "candidate_count": count,
                "baseline_total_ms": baseline_ms,
                "alias_total_ms": alias_ms,
                "candidate_preset_total_ms": candidate_ms,
                "alias_delta_ms": alias_ms - baseline_ms,
                "candidate_preset_delta_ms": candidate_ms - baseline_ms,
                "baseline_payload_copies": int(baseline["stage_profile"]["topology"]["carry_payload_copies"]),
                "alias_payload_copies": int(alias["stage_profile"]["topology"]["carry_payload_copies"]),
                "candidate_preset_payload_copies": int(candidate["stage_profile"]["topology"]["carry_payload_copies"]),
                "baseline_parity": bool(baseline["same_candidate_rows"]),
                "alias_parity": bool(alias["same_candidate_rows"]),
                "candidate_preset_parity": bool(candidate["same_candidate_rows"]),
            }
        )
    return rows


def _aggregate_session(session_index: int, prefix: Path) -> dict[str, Any]:
    summary = _load(prefix.with_name(f"{prefix.name}_summary.json"))
    sweep_targets = [
        row
        for row in summary.get("rows", [])
        if int(row.get("candidate_count", -1)) in TARGET_COUNTS
    ]
    return {
        "session": session_index,
        "prefix": str(prefix),
        "summary_acceptance": {
            key: bool(summary[key])
            for key in (
                "baseline_accepted",
                "alias_accepted",
                "baseline_parity",
                "alias_parity",
                "baseline_topology",
                "alias_topology",
            )
        },
        "candidate_preset_json": summary.get("candidate_preset_json"),
        "sweep_targets": sweep_targets,
        "targeted": _targeted_rows(prefix),
    }


def _write_markdown(aggregate: dict[str, Any], md_path: Path) -> None:
    lines = [
        "# Goal 1586: OptiX Collect-K Multi-Session Validation",
        "",
        "## Verdict",
        "",
        "`goal1586_multi_session_validation_recorded`",
        "",
        "## Scope",
        "",
        f"- Commit: `{aggregate['commit']}`",
        f"- Sessions: `{aggregate['session_count']}`",
        f"- Output prefix: `{aggregate['output_prefix']}`",
        f"- Device label: `{aggregate['gpu_metadata'].get('device_label')}`",
        f"- GPU query: `{aggregate['gpu_metadata'].get('nvidia_smi_query')}`",
        f"- CUDA preflight: `{aggregate['cuda_preflight']}`",
        "",
        "## Targeted Reruns",
        "",
        "| Session | Count | Baseline ms | Alias ms | Candidate preset ms | Alias delta ms | Candidate delta ms | Payload copies baseline/alias/candidate |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for session in aggregate["sessions"]:
        for row in session["targeted"]:
            lines.append(
                "| {session} | {candidate_count} | {baseline_total_ms:.6f} | {alias_total_ms:.6f} | "
                "{candidate_preset_total_ms:.6f} | {alias_delta_ms:.6f} | {candidate_preset_delta_ms:.6f} | "
                "{baseline_payload_copies}/{alias_payload_copies}/{candidate_preset_payload_copies} |".format(
                    session=session["session"], **row
                )
            )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This runner records repeated validation sessions only. It does not authorize public speedup wording, "
            "true zero-copy wording, stable primitive promotion, whole-application claims, or release action.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions", type=int, default=3, help="Number of independent Goal1579 sessions")
    parser.add_argument("--library", default="build/librtdl_optix.so", help="Path to librtdl_optix.so")
    parser.add_argument("--output-prefix", default="/tmp/goal1586_multi_session", help="Output artifact prefix")
    parser.add_argument("--repeats", type=int, default=5, help="Sweep repeats per session")
    parser.add_argument("--targeted-repeats", type=int, default=9, help="Targeted rerun repeats per session")
    parser.add_argument("--candidate-preset-repeats", type=int, default=5, help="Candidate preset repeats per session")
    parser.add_argument("--device-label", default=None, help="Optional human label for the GPU/architecture under test")
    parser.add_argument("--cuda-prefix", default=os.environ.get("CUDA_PREFIX"), help="CUDA toolkit prefix used for preflight")
    parser.add_argument(
        "--skip-cuda-toolchain-preflight",
        action="store_true",
        help="Skip CUDA driver/toolkit compatibility preflight for diagnostic runs",
    )
    parser.add_argument(
        "--ld-library-path",
        default=os.environ.get("LD_LIBRARY_PATH"),
        help="LD_LIBRARY_PATH to use while loading CUDA/OptiX runtime libraries",
    )
    args = parser.parse_args()

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    cuda_preflight = _preflight_cuda_toolchain(
        cuda_prefix=args.cuda_prefix,
        ld_library_path=args.ld_library_path,
        skip=args.skip_cuda_toolchain_preflight,
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = f"src{os.pathsep}."
    if args.ld_library_path:
        env["LD_LIBRARY_PATH"] = args.ld_library_path

    sessions: list[dict[str, Any]] = []
    for session_index in range(1, args.sessions + 1):
        session_prefix = output_prefix.with_name(f"{output_prefix.name}_session{session_index}")
        _run(
            [
                sys.executable,
                "scripts/goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py",
                "--library",
                args.library,
                "--output-prefix",
                str(session_prefix),
                "--repeats",
                str(args.repeats),
                "--targeted-repeats",
                str(args.targeted_repeats),
                "--candidate-preset-smoke",
                "--candidate-preset-repeats",
                str(args.candidate_preset_repeats),
                "--ld-library-path",
                args.ld_library_path or "",
            ],
            env=env,
        )
        sessions.append(_aggregate_session(session_index, session_prefix))

    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.strip()
    aggregate = {
        "status": "goal1586_multi_session_validation_recorded",
        "commit": git_commit,
        "gpu_metadata": _gpu_metadata(args.device_label),
        "cuda_preflight": cuda_preflight,
        "session_count": args.sessions,
        "output_prefix": str(output_prefix),
        "sessions": sessions,
    }
    json_path = output_prefix.with_name(f"{output_prefix.name}_summary.json")
    md_path = output_prefix.with_name(f"{output_prefix.name}_summary.md")
    json_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(aggregate, md_path)
    print(json.dumps({"status": aggregate["status"], "summary_json": str(json_path), "summary_md": str(md_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
