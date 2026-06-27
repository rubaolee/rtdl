#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any


VERSION = "rtdl.v4.goal4670.rt_dbscan_second_win_diagnostics.v1"

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"

CLAIM_BOUNDARY = {
    "release_authorized": False,
    "public_speedup_claim_authorized": False,
    "whole_app_high_performance_claim_authorized": False,
    "rt_core_speedup_claim_authorized": False,
    "paper_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "automatic_partner_selection_authorized": False,
    "app_specific_native_engine_logic_allowed": False,
}

BASELINE = {
    "source": "Goal4669 serious same-hardware app-level rerun",
    "app": "rt_dbscan",
    "v2_14_hot_sec": 1.6791960280388594,
    "v3_0_2_hot_sec": 1.674543371424079,
    "v4_current_hot_sec": 1.5634950418025255,
    "v4_vs_v2_14_hot_speedup": 1.086127902760864,
    "v4_vs_v3_0_2_hot_speedup": 1.083118498208389,
    "formal_speedup_bar": 1.20,
    "no_regression_floor": 0.98,
}

VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "id": "v4_default_numba_signature",
        "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
        "partner": "numba",
        "classification": "candidate_true_v4_runtime_route",
        "purpose": "current V4 productized grouped-stream component-signature route",
        "extra": (),
    },
    {
        "id": "v4_direct_side_effect_probe",
        "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
        "partner": "numba",
        "classification": "generic_native_toggle_probe_not_pre_promoted",
        "purpose": "recheck native grouped-union direct side-effect toggle on the Goal4669 shape",
        "extra": ("--enable-grouped-union-direct-side-effect",),
    },
    {
        "id": "v4_direct_side_effect_no_culling_probe",
        "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
        "partner": "numba",
        "classification": "generic_native_toggle_probe_not_pre_promoted",
        "purpose": (
            "test whether direct side effects plus disabled same-root culling "
            "trade root-read culling for faster generic atomic union"
        ),
        "extra": (
            "--enable-grouped-union-direct-side-effect",
            "--disable-grouped-union-same-root-culling",
        ),
    },
    {
        "id": "v4_no_same_root_culling_negative_probe",
        "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
        "partner": "numba",
        "classification": "negative_control",
        "purpose": "confirm same-root culling remains useful on the Goal4669 shape",
        "extra": ("--disable-grouped-union-same-root-culling",),
    },
    {
        "id": "v4_blocked_grouped_stream_negative_probe",
        "mode": "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
        "partner": "numba",
        "classification": "negative_control_historical_blocked_shape",
        "purpose": "confirm blocked grouped-stream remains slower; not a promotion target",
        "extra": ("--grouped-union-query-block-size", "8192"),
    },
    {
        "id": "v4_cupy_column_signature_historical_route",
        "mode": "optix_rt_core_grouped_stream_cupy_column_signature_3d",
        "partner": "cupy",
        "classification": "historical_partner_route_not_new_v4_win",
        "purpose": "compare historical CuPy component-label front door under current tree",
        "extra": (),
    },
    {
        "id": "v4_measured_all_true_direct_status",
        "mode": "optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d",
        "partner": "cupy",
        "classification": "explicit_all_predicate_route_requires_measured_all_true",
        "purpose": "probe existing all-predicate direct-status route; not automatic default",
        "extra": ("--partition-cell-factor", "0.25"),
    },
    {
        "id": "v4_declared_all_items_direct_status",
        "mode": "partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d",
        "partner": "cupy",
        "classification": "external_proof_required_historical_route_not_rt_core_win",
        "purpose": "probe explicit all-items direct-status route that requires caller proof",
        "extra": ("--partition-cell-factor", "0.25"),
    },
)


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


def _join_pythonpath(*parts: str) -> str:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(token for token in str(part).split(os.pathsep) if token)
    return os.pathsep.join(dict.fromkeys(tokens))


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


def _nested_dict(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict):
            return {}
        value = value.get(key)
    return value if isinstance(value, dict) else {}


def _first_number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _summarize_payload(payload: dict[str, Any], *, variant: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    timing = _nested_dict(metadata, "benchmark_timing_breakdown")
    host = _nested_dict(timing, "host_observed_sec")
    derived = _nested_dict(timing, "derived_sec")
    native = _nested_dict(metadata, "native_grouped_stream_metadata")
    count_native = _nested_dict(metadata, "count_metadata", "native_metadata")
    hot_sec = _first_number(
        payload.get("elapsed_sec"),
        host.get("prepared_runner_steady_state_sec"),
        host.get("adapter_run_sec"),
        native.get("native_elapsed_sec"),
    )
    v2_speedup = _ratio(BASELINE["v2_14_hot_sec"], hot_sec)
    v3_speedup = _ratio(BASELINE["v3_0_2_hot_sec"], hot_sec)
    return {
        "variant": variant["id"],
        "mode": variant["mode"],
        "partner": metadata.get("partner", variant["partner"]),
        "classification": variant["classification"],
        "purpose": variant["purpose"],
        "return_payload_app": payload.get("app"),
        "dataset": payload.get("dataset"),
        "point_count": payload.get("point_count"),
        "elapsed_sec": hot_sec,
        "matches_reference": payload.get("matches_reference"),
        "signature": payload.get("signature"),
        "v4_variant_vs_goal4669_v2_14_hot_speedup": v2_speedup,
        "v4_variant_vs_goal4669_v3_0_2_hot_speedup": v3_speedup,
        "passes_formal_second_win_bar": bool(
            v2_speedup is not None
            and v3_speedup is not None
            and v2_speedup >= BASELINE["formal_speedup_bar"]
            and v3_speedup >= BASELINE["formal_speedup_bar"]
            and variant["classification"] == "candidate_true_v4_runtime_route"
        ),
        "would_be_fast_but_not_true_v4_win": bool(
            v2_speedup is not None
            and v3_speedup is not None
            and v2_speedup >= BASELINE["formal_speedup_bar"]
            and v3_speedup >= BASELINE["formal_speedup_bar"]
            and variant["classification"] != "candidate_true_v4_runtime_route"
        ),
        "native_grouped_stream_sec": native.get("native_elapsed_sec"),
        "count_native_sec": count_native.get("native_elapsed_sec"),
        "host_observed_sec": host,
        "derived_sec": derived,
        "path": metadata.get("path"),
        "all_core_flags_true": metadata.get("all_core_flags_true"),
        "column_signature_strategy": metadata.get("column_signature_strategy"),
        "grouped_union_query_block_count": metadata.get("grouped_union_query_block_count"),
        "grouped_union_query_block_size": metadata.get("grouped_union_query_block_size"),
        "grouped_union_same_root_culling_enabled": metadata.get("grouped_union_same_root_culling_enabled"),
        "grouped_union_direct_side_effect_enabled": metadata.get("grouped_union_direct_side_effect_enabled"),
        "component_union_policy": metadata.get("component_union_policy"),
        "boundary_assignment_policy": metadata.get("boundary_assignment_policy"),
        "rt_count_threshold_executed": metadata.get("rt_count_threshold_executed"),
        "uses_generic_all_items_direct_status_signature": metadata.get(
            "uses_generic_all_items_direct_status_signature"
        ),
        "rt_core_accelerated": metadata.get("rt_core_accelerated"),
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "row_release_authorized": bool(metadata.get("release_authorized", False)),
            "row_public_speedup_claim_authorized": bool(
                metadata.get("public_speedup_claim_authorized", False)
            ),
            "row_whole_app_speedup_claim_authorized": bool(
                metadata.get("whole_app_speedup_claim_authorized", False)
            ),
        },
    }


def _command(args: argparse.Namespace, variant: dict[str, Any]) -> list[str]:
    cmd = [
        args.python,
        str(APP),
        "--mode",
        str(variant["mode"]),
        "--dataset",
        args.dataset,
        "--point-count",
        str(args.point_count),
        "--radius",
        str(args.radius),
        "--min-neighbors",
        str(args.min_neighbors),
        "--partner",
        str(variant["partner"]),
        "--repeat",
        str(args.repeat),
        "--warmup",
        str(args.warmup),
        "--no-validation",
    ]
    cmd.extend(str(token) for token in variant["extra"])
    return cmd


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal4670 RTDBSCAN second-win diagnostic runner.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable or "python3")
    parser.add_argument("--extra-pythonpath", default=os.environ.get("PYTHONPATH", ""))
    parser.add_argument("--rtdl-optix-library", type=Path, default=os.environ.get("RTDL_OPTIX_LIBRARY"))
    parser.add_argument("--dataset", default="clustered3d")
    parser.add_argument("--point-count", type=int, default=262144)
    parser.add_argument("--radius", type=float, default=3.0)
    parser.add_argument("--min-neighbors", type=int, default=4)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=1200)
    args = parser.parse_args(argv)

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = _join_pythonpath(args.extra_pythonpath, "src", ".")
    if args.rtdl_optix_library:
        env["RTDL_OPTIX_LIBRARY"] = str(args.rtdl_optix_library)
        env["RTDL_OPTIX_LIB"] = str(args.rtdl_optix_library)

    started = perf_counter()
    manifest: dict[str, Any] = {
        "goal": "Goal4670",
        "schema": VERSION,
        "status": "running",
        "source_commit": _git("rev-parse", "--short", "HEAD"),
        "source_dirty": _git("status", "--short", "--untracked-files=no").splitlines(),
        "gpu": _nvidia_smi(),
        "baseline": BASELINE,
        "dataset": args.dataset,
        "point_count": args.point_count,
        "radius": args.radius,
        "min_neighbors": args.min_neighbors,
        "repeat": args.repeat,
        "warmup": args.warmup,
        "claim_boundary": CLAIM_BOUNDARY,
        "rows": [],
    }
    (output_dir / "summary.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"[goal4670] start dataset={args.dataset} point_count={args.point_count} "
        f"repeat={args.repeat} warmup={args.warmup}",
        flush=True,
    )

    for variant in VARIANTS:
        label = str(variant["id"])
        stdout_path = output_dir / f"{label}.stdout.json"
        stderr_path = output_dir / f"{label}.stderr.txt"
        command = _command(args, variant)
        print(f"[goal4670] run start {label}", flush=True)
        returncode, stdout, stderr, wrapper_elapsed = _run_command(
            command,
            env=env,
            timeout_sec=args.timeout_sec,
        )
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        row: dict[str, Any] = {
            "variant": label,
            "command": command,
            "returncode": returncode,
            "stdout_path": _display_path(stdout_path),
            "stderr_path": _display_path(stderr_path),
            "wrapper_elapsed_sec": wrapper_elapsed,
        }
        if returncode == 0:
            try:
                payload = json.loads(stdout)
                row.update(_summarize_payload(payload, variant=variant))
                print(
                    f"[goal4670] run done {label} elapsed={row.get('elapsed_sec')} "
                    f"v4v2={row.get('v4_variant_vs_goal4669_v2_14_hot_speedup')} "
                    f"v4v3={row.get('v4_variant_vs_goal4669_v3_0_2_hot_speedup')}",
                    flush=True,
                )
            except Exception as exc:
                row["json_parse_error"] = repr(exc)
                print(f"[goal4670] parse fail {label}: {exc!r}", flush=True)
        else:
            print(f"[goal4670] run fail {label} returncode={returncode}", flush=True)
        manifest["rows"].append(row)
        (output_dir / "summary.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    true_win_rows = [
        row for row in manifest["rows"] if row.get("passes_formal_second_win_bar") is True
    ]
    fast_non_v4_rows = [
        row for row in manifest["rows"] if row.get("would_be_fast_but_not_true_v4_win") is True
    ]
    candidate_rows = [
        row for row in manifest["rows"] if row.get("classification") == "candidate_true_v4_runtime_route"
    ]
    manifest["status"] = "pass" if all(int(row.get("returncode", -1)) == 0 for row in manifest["rows"]) else "partial"
    manifest["elapsed_sec"] = perf_counter() - started
    manifest["true_v4_second_win_found"] = bool(true_win_rows)
    manifest["fast_non_v4_rows_observed"] = [row["variant"] for row in fast_non_v4_rows]
    manifest["candidate_true_v4_runtime_rows"] = [row["variant"] for row in candidate_rows]
    manifest["decision_label"] = (
        "rt_dbscan_second_true_v4_win_found"
        if true_win_rows
        else "rt_dbscan_diagnostics_complete_no_second_true_v4_win_yet"
    )
    manifest["next_action"] = (
        "document and request external review before app-level promotion"
        if true_win_rows
        else "do not claim V4 high performance; inspect native grouped-union or choose another target"
    )
    (output_dir / "summary.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True), flush=True)
    print("[goal4670] complete", flush=True)
    return 0 if manifest["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
