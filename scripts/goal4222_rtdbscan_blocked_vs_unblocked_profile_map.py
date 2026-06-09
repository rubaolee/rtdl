from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"

UNBLOCKED_MODE = "optix_rt_core_grouped_stream_numba_column_signature_3d"
BLOCKED_MODE = "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d"

CLAIM_BOUNDARY = {
    "release_authorized": False,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "rt_dbscan_paper_reproduction_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "automatic_partner_selection_authorized": False,
    "app_specific_native_engine_logic_allowed": False,
}


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _run_command(cmd: list[str], *, env: dict[str, str], timeout_sec: int) -> tuple[int, str, str, float]:
    started = perf_counter()
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr, perf_counter() - started


def _build_command(
    *,
    python: str,
    mode: str,
    dataset: str,
    point_count: int,
    repeat: int,
    warmup: int,
    block_size: int,
) -> list[str]:
    cmd = [
        python,
        str(APP),
        "--mode",
        mode,
        "--dataset",
        dataset,
        "--point-count",
        str(point_count),
        "--repeat",
        str(repeat),
        "--warmup",
        str(warmup),
        "--no-validation",
    ]
    if mode == BLOCKED_MODE:
        cmd.extend(["--grouped-union-query-block-size", str(block_size)])
    return cmd


def _summarize_payload(payload: dict[str, Any], *, mode: str) -> dict[str, Any]:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    native = metadata.get("native_grouped_stream_metadata")
    if not isinstance(native, dict):
        native = {}
    return {
        "mode": mode,
        "dataset": payload.get("dataset"),
        "point_count": payload.get("point_count"),
        "elapsed_sec": payload.get("elapsed_sec"),
        "matches_reference": payload.get("matches_reference"),
        "signature": payload.get("signature"),
        "partner": metadata.get("partner"),
        "boundary_assignment_policy": metadata.get("boundary_assignment_policy"),
        "boundary_assignment_canonical_policy": metadata.get("boundary_assignment_canonical_policy"),
        "grouped_stream_continuation_pass_count": metadata.get("grouped_stream_continuation_pass_count"),
        "native_elapsed_sec": native.get("native_elapsed_sec"),
        "claim_boundary": {
            "release_authorized": metadata.get("release_authorized", False),
            "public_speedup_claim_authorized": metadata.get("public_speedup_claim_authorized", False),
            "whole_app_speedup_claim_authorized": metadata.get("whole_app_speedup_claim_authorized", False),
            "true_zero_copy_claim_authorized": metadata.get("true_zero_copy_claim_authorized", False),
        },
    }


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return float(numerator) / float(denominator)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = _join_pythonpath(args.extra_pythonpath, "src", ".")
    if args.rtdl_optix_library:
        env["RTDL_OPTIX_LIBRARY"] = str(args.rtdl_optix_library)
        env["RTDL_OPTIX_LIB"] = str(args.rtdl_optix_library)

    started = perf_counter()
    manifest: dict[str, Any] = {
        "goal": "Goal4222",
        "status": "running",
        "schema": "rtdl.goal4222.rtdbscan_blocked_vs_unblocked_profile_map.v1",
        "source_commit": _git("rev-parse", "--short", "HEAD"),
        "source_dirty": _git("status", "--short", "--untracked-files=no").splitlines(),
        "gpu": _nvidia_smi(),
        "artifact_root": str(output_dir),
        "datasets": tuple(args.datasets),
        "point_counts": tuple(args.point_counts),
        "repeat": args.repeat,
        "warmup": args.warmup,
        "block_size": args.block_size,
        "rows": [],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write(output_dir / "summary.json", manifest)
    print(
        f"[goal4222] start datasets={args.datasets} point_counts={args.point_counts} "
        f"repeat={args.repeat} warmup={args.warmup}",
        flush=True,
    )
    for dataset in args.datasets:
        for point_count in args.point_counts:
            print(f"[goal4222] pair begin dataset={dataset} point_count={point_count}", flush=True)
            pair: dict[str, Any] = {
                "dataset": dataset,
                "point_count": point_count,
                "unblocked": None,
                "blocked": None,
                "blocked_vs_unblocked_elapsed_ratio": None,
                "recommended_default_shape": None,
                "claim_boundary": CLAIM_BOUNDARY,
            }
            for mode in (UNBLOCKED_MODE, BLOCKED_MODE):
                label = "unblocked" if mode == UNBLOCKED_MODE else "blocked"
                stdout_path = output_dir / f"{dataset}_{point_count}_{label}.stdout.json"
                stderr_path = output_dir / f"{dataset}_{point_count}_{label}.stderr.txt"
                cmd = _build_command(
                    python=args.python,
                    mode=mode,
                    dataset=dataset,
                    point_count=point_count,
                    repeat=args.repeat,
                    warmup=args.warmup,
                    block_size=args.block_size,
                )
                print(f"[goal4222] {label} run start dataset={dataset} point_count={point_count}", flush=True)
                returncode, stdout, stderr, elapsed = _run_command(cmd, env=env, timeout_sec=args.step_timeout)
                stdout_path.write_text(stdout, encoding="utf-8")
                stderr_path.write_text(stderr, encoding="utf-8")
                if returncode != 0:
                    pair[label] = {
                        "status": "fail",
                        "returncode": returncode,
                        "wrapper_elapsed_sec": elapsed,
                        "stdout_path": str(stdout_path.relative_to(ROOT)),
                        "stderr_path": str(stderr_path.relative_to(ROOT)),
                    }
                    manifest["rows"].append(pair)
                    manifest["status"] = "fail"
                    _write(output_dir / "summary.json", manifest)
                    print(f"[goal4222] {label} fail returncode={returncode}", flush=True)
                    return returncode or 1
                payload = json.loads(stdout)
                summary = _summarize_payload(payload, mode=mode)
                summary.update(
                    {
                        "status": "pass",
                        "returncode": returncode,
                        "wrapper_elapsed_sec": elapsed,
                        "stdout_path": str(stdout_path.relative_to(ROOT)),
                        "stderr_path": str(stderr_path.relative_to(ROOT)),
                    }
                )
                pair[label] = summary
                print(
                    f"[goal4222] {label} done elapsed={summary['elapsed_sec']} "
                    f"passes={summary['grouped_stream_continuation_pass_count']}",
                    flush=True,
                )
            unblocked = pair["unblocked"] or {}
            blocked = pair["blocked"] or {}
            ratio = _ratio(blocked.get("elapsed_sec"), unblocked.get("elapsed_sec"))
            pair["blocked_vs_unblocked_elapsed_ratio"] = ratio
            pair["recommended_default_shape"] = (
                "unblocked" if ratio is not None and ratio >= 1.0 else "blocked"
            )
            manifest["rows"].append(pair)
            _write(output_dir / "summary.json", manifest)
            print(
                f"[goal4222] pair done dataset={dataset} point_count={point_count} "
                f"blocked_vs_unblocked={ratio}",
                flush=True,
            )
    manifest["status"] = "pass"
    manifest["elapsed_sec"] = perf_counter() - started
    _write(output_dir / "summary.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True), flush=True)
    print("[goal4222] complete", flush=True)
    return 0


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _join_pythonpath(*parts: str) -> str:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(token for token in str(part).split(os.pathsep) if token)
    return os.pathsep.join(dict.fromkeys(tokens))


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare RT-DBSCAN blocked and unblocked grouped-stream profiles.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable or "python3")
    parser.add_argument("--rtdl-optix-library", type=Path, default=os.environ.get("RTDL_OPTIX_LIBRARY"))
    parser.add_argument("--extra-pythonpath", default=os.environ.get("PYTHONPATH", ""))
    parser.add_argument("--datasets", nargs="+", default=("clustered3d", "road3d", "ngsim_dense"))
    parser.add_argument("--point-counts", nargs="+", type=int, default=(65536, 262144))
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--block-size", type=int, default=4096)
    parser.add_argument("--step-timeout", type=int, default=900)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
