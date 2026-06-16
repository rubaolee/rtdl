from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M34 Barnes-Hut aggregate-frontier native-lowering refresh."
    )
    parser.add_argument("--point-count", type=int, default=8192)
    parser.add_argument("--bucket-size", type=int, default=64)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--hardware", default="rtx4000ada_pod")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4431_v3_0_m34_barnes_hut_frontier_lowering_refresh.json"),
    )
    args = parser.parse_args()
    _validate_args(args)

    if args.dry_run:
        payload = _base_payload(args)
        payload.update(
            {
                "status": "dry_run",
                "planned": _planned(args),
                "comparison": {
                    "same_contract_backends": ("embree", "optix"),
                    "same_contract": "generic_aggregate_frontier_collect_2d_v1",
                    "host_materialized_frontier_rows_expected": True,
                    "clean_device_continuation_expected": False,
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": "dry_run", "planned": payload["planned"]}, indent=2))
        return 0

    from rtdsl.v3_0_m8_measured_lowering import run_v3_m8_aggregate_frontier_lowering_case

    m8_payload = run_v3_m8_aggregate_frontier_lowering_case(
        point_count=int(args.point_count),
        bucket_size=int(args.bucket_size),
        theta=float(args.theta),
        warmups=int(args.warmup),
        repeats=int(args.repeat),
        hardware=str(args.hardware),
    )
    comparison = _compare_m8_payload(m8_payload)
    payload = _base_payload(args)
    payload.update(
        {
            "status": "ok",
            "planned": _planned(args),
            "m8_payload": _json_ready(m8_payload),
            "comparison": comparison,
        }
    )
    if not comparison["all_rows_match_reference"]:
        raise RuntimeError("M34 Barnes-Hut frontier lowering found backend/reference mismatch")
    if comparison["clean_device_continuation_claim_authorized"]:
        raise RuntimeError("M34 must not authorize clean device-continuation claims")
    _write_payload(payload, args.output)
    print(json.dumps({"status": "ok", "comparison": comparison}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if int(args.point_count) <= 0:
        raise ValueError("--point-count must be positive")
    if int(args.bucket_size) <= 0:
        raise ValueError("--bucket-size must be positive")
    if float(args.theta) <= 0.0:
        raise ValueError("--theta must be positive")
    if int(args.warmup) < 0:
        raise ValueError("--warmup must be non-negative")
    if int(args.repeat) <= 0:
        raise ValueError("--repeat must be positive")


def _base_payload(args: argparse.Namespace) -> dict[str, object]:
    return {
        "version": "rtdl.v3_0.barnes_hut_frontier_lowering_refresh.m34",
        "goal": "Goal4431 V3.0 M34 Barnes-Hut aggregate-frontier lowering refresh",
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "benchmark_app": "barnes_hut",
            "same_contract_native_lowering_refresh": True,
            "native_contract": "generic_aggregate_frontier_collect_2d_v1",
            "host_materialized_frontier_rows": True,
            "device_resident_partner_handoff_proven": False,
            "clean_device_continuation_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "full_rt_barneshut_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def _planned(args: argparse.Namespace) -> dict[str, object]:
    return {
        "point_count": int(args.point_count),
        "bucket_size": int(args.bucket_size),
        "theta": float(args.theta),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "hardware": str(args.hardware),
        "backends": ("embree", "optix"),
        "same_contract": "generic_aggregate_frontier_collect_2d_v1",
        "timed_window": "native wrapper call including host frontier-row materialization",
    }


def _compare_m8_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    rows = tuple(payload.get("backend_rows", ()))
    by_backend = {str(row["backend"]): row for row in rows if isinstance(row, Mapping)}
    embree = by_backend["embree"]
    optix = by_backend["optix"]
    embree_median = float(embree["median_seconds"])
    optix_median = float(optix["median_seconds"])
    frontier_row_count = int(payload["fixture_summary"]["frontier_row_count"])
    return {
        "same_contract_backends": tuple(sorted(by_backend)),
        "same_contract": payload["contract"],
        "native_abi_contract": payload["native_abi_contract"],
        "frontier_row_count": frontier_row_count,
        "all_rows_match_reference": all(bool(row["rows_match_reference"]) for row in by_backend.values()),
        "all_native_engine_app_specific_false": all(
            not bool(row["native_engine_app_specific"]) for row in by_backend.values()
        ),
        "winner": "optix" if optix_median < embree_median else "embree",
        "embree_median_seconds": embree_median,
        "optix_median_seconds": optix_median,
        "embree_over_optix_median": embree_median / optix_median if optix_median else None,
        "optix_over_embree_median": optix_median / embree_median if embree_median else None,
        "host_materialized_frontier_rows": True,
        "host_materialized_row_count": frontier_row_count,
        "device_resident_partner_handoff_proven": False,
        "clean_device_continuation_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
    }


def _environment_snapshot() -> dict[str, object]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_head": _git_head(),
    }


def _git_head() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None
    return completed.stdout.strip()


def _json_ready(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _write_payload(payload: Mapping[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
