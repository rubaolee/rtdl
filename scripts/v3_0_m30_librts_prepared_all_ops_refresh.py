from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


DEFAULT_REPEATS = {
    "embree": 240,
    "optix": 3200,
}

EXPECTED_PRIMITIVE = "AABB_INDEX_QUERY_2D"
EXPECTED_CONTRACT = "generic_prepared_aabb_index_query_2d"
OPERATIONS = ("point_contains", "range_contains", "range_intersects")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M30 LibRTS prepared AABB all-ops refresh evidence."
    )
    parser.add_argument("--box-count", type=int, default=1_000_000)
    parser.add_argument("--query-count", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--max-box-width", type=float, default=0.005)
    parser.add_argument("--max-box-height", type=float, default=0.005)
    parser.add_argument("--max-query-width", type=float, default=0.005)
    parser.add_argument("--max-query-height", type=float, default=0.005)
    parser.add_argument("--operation", default="all", choices=("all", *OPERATIONS))
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument(
        "--repeat-overrides",
        default="embree=240,optix=3200",
        help="Comma-separated backend=repeat entries.",
    )
    parser.add_argument(
        "--validate-cpu-reference",
        action="store_true",
        help="Run O(n*m) CPU oracle. Intended only for tiny local diagnostics.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4427_v3_0_m30_librts_prepared_all_ops_refresh.json"),
    )
    args = parser.parse_args()

    _validate_args(args)
    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    if not backends:
        raise ValueError("--backends must include at least one backend")
    unsupported = sorted(set(backends) - set(DEFAULT_REPEATS))
    if unsupported:
        raise ValueError(f"unsupported backend(s): {', '.join(unsupported)}")

    repeat_overrides = _parse_repeat_overrides(args.repeat_overrides)
    planned_rows = tuple(
        {
            "backend": backend,
            "box_count": int(args.box_count),
            "query_count": int(args.query_count),
            "operation": args.operation,
            "warmup": int(args.warmup),
            "repeat": int(repeat_overrides.get(backend, DEFAULT_REPEATS[backend])),
        }
        for backend in backends
    )

    if args.dry_run:
        payload = _base_payload(args=args, backends=backends)
        payload.update(
            {
                "status": "dry_run",
                "planned_rows": planned_rows,
                "rows": (),
                "comparison": {
                    "all_counts_match_cross_backend": None,
                    "same_contract_backend_pair": None,
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": payload["status"], "planned_rows": planned_rows}, indent=2))
        return 0

    from examples.current.research_benchmarks.librts_spatial_index import (
        rtdl_librts_spatial_index_benchmark_app as librts,
    )

    fixture = librts.make_uniform_fixture(
        box_count=int(args.box_count),
        query_count=int(args.query_count),
        seed=int(args.seed),
        max_box_width=float(args.max_box_width),
        max_box_height=float(args.max_box_height),
        max_query_width=float(args.max_query_width),
        max_query_height=float(args.max_query_height),
    )

    rows = []
    for planned in planned_rows:
        backend = str(planned["backend"])
        if backend == "embree":
            result = librts.run_embree_aabb_counts(
                fixture,
                str(args.operation),
                query_repeat=int(planned["repeat"]),
                warmup=int(planned["warmup"]),
                validate_reference=bool(args.validate_cpu_reference),
            )
        elif backend == "optix":
            result = librts.run_optix_aabb_counts(
                fixture,
                str(args.operation),
                prepared_queries=True,
                query_repeat=int(planned["repeat"]),
                warmup=int(planned["warmup"]),
                validate_reference=bool(args.validate_cpu_reference),
            )
        else:
            raise AssertionError(f"unreachable backend: {backend}")
        rows.append(_compact_row(result, backend=backend))

    comparison = _compare_rows(rows)
    payload = _base_payload(args=args, backends=backends)
    payload.update(
        {
            "status": "ok",
            "planned_rows": planned_rows,
            "rows": tuple(rows),
            "comparison": comparison,
        }
    )
    if not comparison["all_counts_match_cross_backend"]:
        raise RuntimeError("M30 LibRTS prepared all-ops refresh found cross-backend count mismatch")
    if not comparison["all_same_contract"]:
        raise RuntimeError("M30 LibRTS prepared all-ops refresh found contract mismatch")
    _write_payload(payload, args.output)
    print(json.dumps({"status": payload["status"], "comparison": comparison, "rows": rows}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.box_count <= 0:
        raise ValueError("--box-count must be positive")
    if args.query_count <= 0:
        raise ValueError("--query-count must be positive")
    for name in ("max_box_width", "max_box_height", "max_query_width", "max_query_height"):
        if float(getattr(args, name)) <= 0.0:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")


def _base_payload(*, args: argparse.Namespace, backends: tuple[str, ...]) -> dict[str, object]:
    return {
        "version": "rtdl.v3_0.librts_prepared_all_ops_refresh.m30",
        "goal": "Goal4427 V3.0 M30 LibRTS prepared AABB all-ops refresh",
        "parameters": {
            "dataset": "uniform",
            "paper_like_widths": True,
            "box_count": int(args.box_count),
            "query_count": int(args.query_count),
            "seed": int(args.seed),
            "max_box_width": float(args.max_box_width),
            "max_box_height": float(args.max_box_height),
            "max_query_width": float(args.max_query_width),
            "max_query_height": float(args.max_query_height),
            "operation": args.operation,
            "backends": backends,
            "warmup": int(args.warmup),
            "validate_cpu_reference": bool(args.validate_cpu_reference),
        },
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "primitive_first_no_partner_needed": True,
            "partner_continuation_required": False,
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
            "authors_code_comparison": False,
            "paper_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
    }


def _compact_row(result: dict[str, object], *, backend: str) -> dict[str, object]:
    phases = dict(result["run_phases"])
    repeat_protocol = dict(result.get("repeat_protocol") or {})
    query_prepare = phases.get("query_prepare_sec", {})
    query_sec = phases.get("query_sec", {})
    if not isinstance(query_prepare, dict):
        query_prepare = {}
    if not isinstance(query_sec, dict):
        query_sec = {str(result["operation"]): float(query_sec)}
    fixture = dict(result["fixture"])
    counts = {name: int(value) for name, value in dict(result["counts"]).items()}
    return {
        "backend": backend,
        "mode": result["mode"],
        "operation": result["operation"],
        "generic_primitive": result["generic_primitive"],
        "primitive_contract": result["primitive_contract"],
        "counts": counts,
        "counts_signature": json.dumps(counts, sort_keys=True),
        "matches_cpu_reference": result["matches_cpu_reference"],
        "cpu_reference_skipped": bool(result["cpu_reference_skipped"]),
        "fixture": fixture,
        "box_count": int(fixture["box_count"]),
        "point_query_count": int(fixture["point_query_count"]),
        "box_query_count": int(fixture["box_query_count"]),
        "scene_prepare_sec": float(phases.get("scene_prepare_sec", 0.0)),
        "query_prepare_sec": {name: float(value) for name, value in query_prepare.items()},
        "query_sec": {name: float(value) for name, value in query_sec.items()},
        "query_median_sec": float(phases["query_median_sec"]),
        "query_summed_median_sec": float(phases["query_summed_median_sec"]),
        "query_total_sec": float(phases["query_total_sec"]),
        "query_repeat": int(phases["query_repeat"]),
        "query_warmup": int(phases["query_warmup"]),
        "repeat_protocol": repeat_protocol,
        "elapsed_cold_plus_hot_median_sec": float(result["elapsed_sec"]),
        "prepared_queries": bool(result.get("prepared_queries", backend == "embree")),
        "multi_operation_native_used": bool(result.get("multi_operation_native_used", backend == "embree")),
        "rt_core_accelerated": bool(result["rt_core_accelerated"]),
        "native_engine_customization": bool(result["native_engine_customization"]),
        "partner_continuation_required": False,
        "public_speedup_claim_authorized": False,
    }


def _compare_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_backend = {str(row["backend"]): row for row in rows}
    count_signatures = {str(row["counts_signature"]) for row in rows}
    all_same_contract = all(
        row["generic_primitive"] == EXPECTED_PRIMITIVE and row["primitive_contract"] == EXPECTED_CONTRACT
        for row in rows
    )
    pair = None
    optix = by_backend.get("optix")
    embree = by_backend.get("embree")
    if optix is not None and embree is not None:
        optix_query = float(optix["query_median_sec"])
        embree_query = float(embree["query_median_sec"])
        pair = {
            "embree_query_median_sec": embree_query,
            "optix_query_median_sec": optix_query,
            "embree_over_optix_query_median": embree_query / optix_query if optix_query > 0.0 else None,
            "embree_query_total_sec": float(embree["query_total_sec"]),
            "optix_query_total_sec": float(optix["query_total_sec"]),
            "embree_repeat": int(embree["query_repeat"]),
            "optix_repeat": int(optix["query_repeat"]),
            "same_contract": embree["primitive_contract"] == optix["primitive_contract"],
            "same_counts": embree["counts_signature"] == optix["counts_signature"],
            "same_dataset": embree["fixture"] == optix["fixture"],
            "comparison_scope": "internal_same_contract_prepared_aabb_all_ops_refresh_not_public_speedup",
        }
    return {
        "all_counts_match_cross_backend": len(count_signatures) == 1,
        "all_same_contract": all_same_contract,
        "all_primitive_first_no_partner": all(not bool(row["partner_continuation_required"]) for row in rows),
        "all_public_speedup_disabled": all(not bool(row["public_speedup_claim_authorized"]) for row in rows),
        "same_contract_backend_pair": pair,
        "public_speedup_claim_authorized": False,
    }


def _parse_repeat_overrides(raw: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    if not raw:
        return parsed
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        backend, value = item.split("=", 1)
        backend = backend.strip()
        if backend not in DEFAULT_REPEATS:
            raise ValueError(f"unsupported repeat override backend: {backend}")
        repeat = int(value)
        if repeat <= 0:
            raise ValueError("repeat override values must be positive")
        parsed[backend] = repeat
    return parsed


def _environment_snapshot() -> dict[str, object]:
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "git_head": _run_text(["git", "rev-parse", "HEAD"], cwd=ROOT).strip(),
        "nvidia_smi": _run_text(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            cwd=ROOT,
        ).strip(),
    }


def _run_text(command: list[str], *, cwd: Path) -> str:
    try:
        completed = subprocess.run(command, cwd=str(cwd), check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


def _write_payload(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
