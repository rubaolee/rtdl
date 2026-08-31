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
DEFAULT_RAYJOIN_DATA_DIR = Path("/root/rtdl/data/rayjoin_public_cdb")
DEFAULT_OUTPUT_DIR = Path("/root/goal3927_combined_perf_artifacts")
RTDBSCAN_MODES = (
    "optix_rt_core_grouped_stream_numba_column_signature_3d",
    "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
)
CLAIM_BOUNDARY = {
    "release_authorized": False,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "automatic_partner_selection_authorized": False,
    "app_specific_native_engine_logic_allowed": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
    "rt_dbscan_paper_reproduction_claim_authorized": False,
}


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    started = perf_counter()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "rayjoin").mkdir(exist_ok=True)
    (output_dir / "rtdbscan").mkdir(exist_ok=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = _join_pythonpath(args.extra_pythonpath, "src", ".")
    if args.rtdl_optix_library:
        env["RTDL_OPTIX_LIBRARY"] = str(args.rtdl_optix_library)
        env["RTDL_OPTIX_LIB"] = str(args.rtdl_optix_library)

    source_commit = _git("rev-parse", "--short", "HEAD")
    source_dirty = _git("status", "--short", "--untracked-files=no").splitlines()
    manifest: dict[str, Any] = {
        "goal": "Goal3927",
        "status": "dry_run" if args.dry_run else "running",
        "artifact_root": str(output_dir),
        "source_commit": source_commit,
        "source_commit_label": args.source_commit_label or source_commit,
        "source_dirty": source_dirty,
        "dry_run": bool(args.dry_run),
        "rayjoin": {},
        "rtdbscan": [],
        "planned_commands": [],
        "elapsed_sec": None,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(output_dir / "summary_manifest.json", manifest)

    print(f"[goal3927] start artifact_root={output_dir}", flush=True)
    if args.dry_run:
        manifest["planned_commands"] = _planned_commands(args, env)
        manifest["status"] = "dry_run"
        manifest["elapsed_sec"] = perf_counter() - started
        _write_json(output_dir / "summary_manifest.json", manifest)
        print(json.dumps(manifest, indent=2, sort_keys=True), flush=True)
        print("[goal3927] dry-run complete", flush=True)
        return 0

    _require_prerequisites(args)

    rayjoin_path = output_dir / "rayjoin" / "summary.json"
    rayjoin_log = output_dir / "rayjoin" / "run.stderr.txt"
    rayjoin_cmd = _rayjoin_command(args)
    print("[goal3927] RayJoin subprobe begin", flush=True)
    _run_step(rayjoin_cmd, env=env, stdout_path=rayjoin_path, stderr_path=rayjoin_log, timeout_sec=args.step_timeout)
    print("[goal3927] RayJoin subprobe done", flush=True)
    manifest["rayjoin"] = _summarize_rayjoin(rayjoin_path)
    _write_json(output_dir / "summary_manifest.json", manifest)

    for mode in RTDBSCAN_MODES:
        stdout_path = output_dir / "rtdbscan" / f"{mode}.json"
        stderr_path = output_dir / "rtdbscan" / f"{mode}.stderr.txt"
        cmd = _rtdbscan_command(args, mode)
        print(f"[goal3927] RTDBSCAN mode={mode} begin", flush=True)
        _run_step(cmd, env=env, stdout_path=stdout_path, stderr_path=stderr_path, timeout_sec=args.step_timeout)
        print(f"[goal3927] RTDBSCAN mode={mode} done", flush=True)
        manifest["rtdbscan"].append(_summarize_rtdbscan(stdout_path))
        _write_json(output_dir / "summary_manifest.json", manifest)

    manifest["status"] = "pass"
    manifest["elapsed_sec"] = perf_counter() - started
    _write_json(output_dir / "summary_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True), flush=True)
    print("[goal3927] complete", flush=True)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3927 combined pod performance queue")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--rayjoin-data-dir", type=Path, default=DEFAULT_RAYJOIN_DATA_DIR)
    parser.add_argument("--rtdl-optix-library", type=Path, default=os.environ.get("RTDL_OPTIX_LIBRARY"))
    parser.add_argument("--extra-pythonpath", default=os.environ.get("PYTHONPATH", ""))
    parser.add_argument("--python", default=sys.executable or "python3")
    parser.add_argument("--step-timeout", type=int, default=900)
    parser.add_argument("--source-commit-label", default="")
    parser.add_argument("--rayjoin-repeat", type=int, default=50)
    parser.add_argument("--rayjoin-warmup", type=int, default=5)
    parser.add_argument("--pip-batch-single-repeat", type=int, default=12)
    parser.add_argument("--pip-batch-repeat", type=int, default=8)
    parser.add_argument("--pip-batch-request-counts", type=int, nargs="+", default=(1, 100))
    parser.add_argument("--rtdbscan-point-count", type=int, default=65_536)
    parser.add_argument("--rtdbscan-repeat", type=int, default=5)
    parser.add_argument("--rtdbscan-warmup", type=int, default=1)
    parser.add_argument("--grouped-union-query-block-size", type=int, default=4096)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _join_pythonpath(*parts: str) -> str:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(token for token in str(part).split(os.pathsep) if token)
    return os.pathsep.join(dict.fromkeys(tokens))


def _require_prerequisites(args: argparse.Namespace) -> None:
    if args.rtdl_optix_library is None or not Path(args.rtdl_optix_library).is_file():
        raise FileNotFoundError(f"RTDL OptiX library not found: {args.rtdl_optix_library}")
    for name in ("br_county_start256_count512.cdb", "br_soil_start256_count512.cdb"):
        path = args.rayjoin_data_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"RayJoin public CDB fixture missing: {path}")


def _rayjoin_command(args: argparse.Namespace) -> list[str]:
    cmd = [
        args.python,
        "scripts/goal3866_rayjoin_representative_scale_profile.py",
        "--data-dir",
        str(args.rayjoin_data_dir),
        "--repeat",
        str(args.rayjoin_repeat),
        "--warmup",
        str(args.rayjoin_warmup),
        "--pip-batch-single-repeat",
        str(args.pip_batch_single_repeat),
        "--pip-batch-repeat",
        str(args.pip_batch_repeat),
        "--pip-batch-request-counts",
    ]
    cmd.extend(str(value) for value in args.pip_batch_request_counts)
    return cmd


def _rtdbscan_command(args: argparse.Namespace, mode: str) -> list[str]:
    return [
        args.python,
        "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
        "--mode",
        mode,
        "--dataset",
        "clustered3d",
        "--point-count",
        str(args.rtdbscan_point_count),
        "--repeat",
        str(args.rtdbscan_repeat),
        "--warmup",
        str(args.rtdbscan_warmup),
        "--grouped-union-query-block-size",
        str(args.grouped_union_query_block_size),
        "--no-validation",
    ]


def _planned_commands(args: argparse.Namespace, env: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "name": "rayjoin_subprobe",
            "command": _rayjoin_command(args),
            "timeout_sec": int(args.step_timeout),
            "env_keys": sorted(key for key in ("PYTHONPATH", "RTDL_OPTIX_LIBRARY", "RTDL_OPTIX_LIB") if key in env),
        },
        *(
            {
                "name": f"rtdbscan_{mode}",
                "command": _rtdbscan_command(args, mode),
                "timeout_sec": int(args.step_timeout),
                "env_keys": sorted(
                    key for key in ("PYTHONPATH", "RTDL_OPTIX_LIBRARY", "RTDL_OPTIX_LIB") if key in env
                ),
            }
            for mode in RTDBSCAN_MODES
        ),
    ]


def _run_step(
    cmd: list[str],
    *,
    env: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
    timeout_sec: int,
) -> None:
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
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"step failed returncode={completed.returncode}: {' '.join(cmd)}; stderr={stderr_path}"
        )


def _summarize_rayjoin(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "gpu": data.get("gpu"),
        "wrapper_phase_timing_sec": data.get("wrapper_phase_timing_sec"),
        "cases": [
            {
                "workload": case.get("workload"),
                "loaded_case_reuse_enabled": case.get("loaded_case_reuse_enabled"),
                "rtdl_optix_execution_route": case.get("rtdl_optix_execution_route"),
                "subprobe_wrapper_phase_timing_sec": case.get("subprobe_wrapper_phase_timing_sec"),
            }
            for case in data.get("cases", [])
        ],
    }


def _summarize_rtdbscan(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    return {
        "path": str(path),
        "mode": data.get("mode", path.stem),
        "elapsed_sec": data.get("elapsed_sec"),
        "partner": meta.get("partner"),
        "path_label": meta.get("path"),
        "blocked": meta.get("grouped_union_query_blocked_candidate"),
        "block_size": meta.get("grouped_union_query_block_size"),
        "signature": meta.get("column_signature_strategy"),
        "claim_boundary": {
            "release_authorized": bool(meta.get("release_authorized", False)),
            "public_speedup_claim_authorized": bool(meta.get("public_speedup_claim_authorized", False)),
            "whole_app_speedup_claim_authorized": bool(meta.get("whole_app_speedup_claim_authorized", False)),
            "true_zero_copy_claim_authorized": bool(meta.get("true_zero_copy_claim_authorized", False)),
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception:
        return ""
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
