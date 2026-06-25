#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


DEFAULT_QUERY_COUNTS = (32768, 131072)
MEASURED_GATE_STATUS = "measured_on_v4_goal4618_pod_optix8"


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _require_torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch with CUDA is required for this V4 point-group measured gate") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is not available")
    return torch


def _parse_counts(raw: str | None) -> tuple[int, ...]:
    if not raw:
        return DEFAULT_QUERY_COUNTS
    counts = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not counts or any(count <= 0 for count in counts):
        raise ValueError("query counts must be positive")
    return counts


def _make_fixture(torch, query_count: int, *, device, fixture_variant: str = "mixed4") -> dict[str, object]:
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if fixture_variant not in {"mixed4", "mixed6"}:
        raise ValueError("fixture_variant must be one of: mixed4, mixed6")
    ids_i64 = torch.arange(query_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    search_x = ids_i64.to(torch.float64) * 2.0
    x = search_x.clone()
    y = torch.zeros((query_count,), dtype=torch.float64, device=device)
    pattern_mod = 4 if fixture_variant == "mixed4" else 6
    pattern = torch.remainder(ids_i64, pattern_mod)
    x = torch.where(pattern == 1, x + 0.30, x)
    x = torch.where(pattern == 3, x - 0.25, x)
    if fixture_variant == "mixed6":
        x = torch.where(pattern == 4, x + 0.30, x)
        y = torch.where(pattern == 4, torch.full_like(y, 0.20), y)
        x = torch.where(pattern == 5, x + 0.45, x)
        y = torch.where(pattern == 5, torch.full_like(y, 0.45), y)
    y = torch.where(pattern == 2, torch.full_like(y, 10.0), y)
    no_hit_neighbor_i64 = torch.full((query_count,), 0xFFFFFFFF, dtype=torch.int64, device=device)
    no_hit_mask = pattern == 2
    if fixture_variant == "mixed6":
        no_hit_mask = torch.logical_or(no_hit_mask, pattern == 5)
    expected_neighbor_ids = torch.where(no_hit_mask, no_hit_neighbor_i64, ids_i64).to(torch.uint32).contiguous()
    dx = x.to(torch.float32) - search_x.to(torch.float32)
    dy = y.to(torch.float32)
    expected_distances = torch.sqrt(dx * dx + dy * dy).to(torch.float64)
    expected_distances = torch.where(
        no_hit_mask,
        torch.full_like(expected_distances, float(np.finfo(np.float32).max)),
        expected_distances,
    ).contiguous()
    host_ids = list(range(query_count))
    search_points = tuple(
        {"id": int(i), "x": float(i * 2.0), "y": 0.0}
        for i in host_ids
    )
    point_groups = tuple(
        {
            "id": int(i),
            "point_offset": int(i),
            "point_count": 1,
            "min_x": float(i * 2.0),
            "min_y": 0.0,
            "max_x": float(i * 2.0),
            "max_y": 0.0,
        }
        for i in host_ids
    )
    return {
        "search_points": search_points,
        "point_groups": point_groups,
        "query_points": tuple(
            {"id": int(i), "x": float(x_value), "y": float(y_value)}
            for i, x_value, y_value in zip(
                host_ids,
                x.detach().cpu().tolist(),
                y.detach().cpu().tolist(),
            )
        ),
        "query_columns": {
            "ids": ids,
            "x": x,
            "y": y,
        },
        "expected_query_ids": ids,
        "expected_neighbor_ids": expected_neighbor_ids,
        "expected_distances": expected_distances,
        "fixture_shape": {
            "variant": fixture_variant,
            "pattern": (
                "exact_match/x_positive_hit/y_axis_no_hit/x_negative_hit"
                if fixture_variant == "mixed4"
                else "exact_match/x_positive_hit/y_axis_no_hit/x_negative_hit/diagonal_hit/diagonal_no_hit"
            ),
            "exact_match_count": int(torch.count_nonzero(pattern == 0).item()),
            "positive_offset_count": int(torch.count_nonzero(pattern == 1).item()),
            "y_axis_no_hit_count": int(torch.count_nonzero(pattern == 2).item()),
            "negative_offset_count": int(torch.count_nonzero(pattern == 3).item()),
            "diagonal_hit_count": int(torch.count_nonzero(pattern == 4).item()) if fixture_variant == "mixed6" else 0,
            "diagonal_no_hit_count": int(torch.count_nonzero(pattern == 5).item()) if fixture_variant == "mixed6" else 0,
            "no_hit_count": int(torch.count_nonzero(no_hit_mask).item()),
            "no_hit_neighbor_id": 0xFFFFFFFF,
            "no_hit_distance": float(np.finfo(np.float32).max),
        },
    }


def _measure(callable_obj, *, torch, repeat: int, warmup: int, progress: bool, label: str) -> dict[str, Any]:
    for index in range(warmup):
        _progress(progress, f"[warmup] {label} {index + 1}/{warmup}")
        callable_obj()
        torch.cuda.synchronize()

    timings: list[float] = []
    payload = None
    for index in range(repeat):
        _progress(progress, f"[repeat-start] {label} {index + 1}/{repeat}")
        start = time.perf_counter()
        payload = callable_obj()
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        _progress(progress, f"[repeat-done] {label} {index + 1}/{repeat} elapsed_s={elapsed:.6f}")
    return {
        "timings_s": timings,
        "median_s": _median(timings),
        "min_s": min(timings) if timings else 0.0,
        "max_s": max(timings) if timings else 0.0,
        "payload": payload,
    }


def _check_device_parity(torch, output_columns: dict[str, object], fixture: dict[str, object]) -> dict[str, object]:
    query_ids_match = bool(torch.equal(output_columns["query_ids"], fixture["expected_query_ids"]))
    neighbor_ids_match = bool(torch.equal(output_columns["neighbor_ids"], fixture["expected_neighbor_ids"]))
    distances_match = bool(
        torch.allclose(
            output_columns["distances"],
            fixture["expected_distances"],
            rtol=1e-5,
            atol=1e-5,
        )
    )
    return {
        "query_ids_match": query_ids_match,
        "neighbor_ids_match": neighbor_ids_match,
        "distances_match": distances_match,
        "passed": query_ids_match and neighbor_ids_match and distances_match,
    }


def _check_legacy_rows(rows: tuple[dict[str, object], ...], fixture: dict[str, object]) -> dict[str, object]:
    query_count = int(fixture["expected_query_ids"].shape[0])
    row_count_match = len(rows) == query_count
    expected_query_ids = fixture["expected_query_ids"].detach().cpu().numpy().astype(np.uint32, copy=False)
    expected_neighbor_ids = fixture["expected_neighbor_ids"].detach().cpu().numpy().astype(np.uint32, copy=False)
    expected_distances = fixture["expected_distances"].detach().cpu().numpy().astype(np.float64, copy=False)
    actual_query_ids = np.asarray([int(row["query_id"]) for row in rows], dtype=np.uint32)
    actual_neighbor_ids = np.asarray([int(row["neighbor_id"]) for row in rows], dtype=np.uint32)
    actual_distances = np.asarray([float(row["distance"]) for row in rows], dtype=np.float64)
    query_ids_match = bool(row_count_match and np.array_equal(actual_query_ids, expected_query_ids))
    neighbor_ids_match = bool(row_count_match and np.array_equal(actual_neighbor_ids, expected_neighbor_ids))
    distances_match = bool(
        row_count_match
        and np.allclose(actual_distances, expected_distances, rtol=1e-5, atol=1e-5)
    )
    return {
        "row_count": len(rows),
        "row_count_match": row_count_match,
        "query_ids_match": query_ids_match,
        "neighbor_ids_match": neighbor_ids_match,
        "distances_match": distances_match,
        "sample": rows[:8],
        "passed": row_count_match and query_ids_match and neighbor_ids_match and distances_match,
    }


def _measure_size(
    query_count: int,
    *,
    repeat: int,
    warmup: int,
    progress: bool,
    fixture_variant: str,
) -> dict[str, Any]:
    import rtdsl.v4_point_group as pg_v4

    torch = _require_torch()
    device = torch.device("cuda:0")
    fixture = _make_fixture(torch, query_count, device=device, fixture_variant=fixture_variant)
    torch.cuda.synchronize()

    prepare_start = time.perf_counter()
    with pg_v4.prepare_point_group_nearest_witness_2d_device_arrays_v4(
        fixture["search_points"],
        fixture["point_groups"],
        max_radius=0.5,
        partner="torch",
    ) as session:
        prepare_seconds = time.perf_counter() - prepare_start
        output_columns = session.allocate_outputs(fixture["query_columns"])

        def run_device_frontdoor() -> dict[str, object]:
            return session.run(
                fixture["query_columns"],
                radius=0.5,
                output_columns=output_columns,
                return_metadata=True,
            )

        def run_legacy_host_rows() -> tuple[dict[str, object], ...]:
            return session.prepared.nearest_witness_rows(fixture["query_points"], radius=0.5)

        device_measure = _measure(
            run_device_frontdoor,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"device_query_output/query_count={query_count}",
        )
        legacy_measure = _measure(
            run_legacy_host_rows,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"legacy_host_rows/query_count={query_count}",
        )

    device_payload = device_measure["payload"]
    legacy_rows = tuple(legacy_measure["payload"] or ())
    parity = {
        "device_outputs": _check_device_parity(torch, output_columns, fixture),
        "legacy_rows": _check_legacy_rows(legacy_rows, fixture),
    }
    parity["passed"] = bool(parity["device_outputs"]["passed"] and parity["legacy_rows"]["passed"])
    device_median = float(device_measure["median_s"])
    legacy_median = float(legacy_measure["median_s"])
    ratio = legacy_median / device_median if device_median > 0 else None
    metadata = dict(device_payload["metadata"])
    return {
        "query_count": int(query_count),
        "search_count": int(query_count),
        "group_count": int(query_count),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "fixture_shape": fixture["fixture_shape"],
        "prepare_seconds": prepare_seconds,
        "direct_device_output": {
            "median_s": device_median,
            "min_s": float(device_measure["min_s"]),
            "max_s": float(device_measure["max_s"]),
            "timings_s": device_measure["timings_s"],
            "native_elapsed_sec_last": metadata.get("native_elapsed_sec"),
            "metadata": metadata,
        },
        "legacy_host_rows": {
            "median_s": legacy_median,
            "min_s": float(legacy_measure["min_s"]),
            "max_s": float(legacy_measure["max_s"]),
            "timings_s": legacy_measure["timings_s"],
            "row_count": len(legacy_rows),
            "row_sample": legacy_rows[:8],
        },
        "same_contract_ratio_legacy_host_rows_over_direct_device_output": ratio,
        "parity": parity,
    }


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Point-Group Nearest-Witness Device-Output Gate",
        "",
        "Status: generated measured-surface evidence, not a release authorization",
        "",
        f"- surface status: `{payload['surface_status']}`",
        f"- status: `{payload['status']}`",
        f"- fixture variant: `{payload['fixture_variant']}`",
        f"- release authorized: `{payload['release_claim_authorized']}`",
        "",
        "| queries | direct device-output median | legacy host-row median | ratio | parity |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in payload["results"]:
        lines.append(
            "| {query_count:,} | {device:.6f}s | {legacy:.6f}s | {ratio:.3f}x | {parity} |".format(
                query_count=row["query_count"],
                device=row["direct_device_output"]["median_s"],
                legacy=row["legacy_host_rows"]["median_s"],
                ratio=row["same_contract_ratio_legacy_host_rows_over_direct_device_output"] or 0.0,
                parity=row["parity"]["passed"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a same-contract measured-surface comparison between the existing host-row materialization route and the V4 direct device-query/device-output route. It is not broad V4 speedup evidence and does not authorize release wording.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the V4 point-group nearest-witness measured device-output surface."
    )
    parser.add_argument("--query-counts", default=",".join(str(value) for value in DEFAULT_QUERY_COUNTS))
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--fixture-variant", choices=("mixed4", "mixed6"), default="mixed4")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    counts = _parse_counts(args.query_counts)
    if args.repeat <= 0:
        raise ValueError("repeat must be positive")
    if args.warmup < 0:
        raise ValueError("warmup must be non-negative")

    payload: dict[str, Any] = {
        "schema": "rtdl.v4.point_group_nearest_witness_device_outputs_gate.v1",
        "surface": "v4_point_group_nearest_witness_2d_device_arrays",
        "surface_status": (
            "measured_surface_dry_run"
            if args.dry_run
            else MEASURED_GATE_STATUS
        ),
        "status": "dry_run" if args.dry_run else "pending",
        "query_counts": counts,
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "fixture_variant": str(args.fixture_variant),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "results": [],
    }
    if not args.dry_run:
        payload["results"] = [
            _measure_size(
                count,
                repeat=args.repeat,
                warmup=args.warmup,
                progress=bool(args.progress),
                fixture_variant=str(args.fixture_variant),
            )
            for count in counts
        ]
        payload["status"] = (
            "passed"
            if all(row["parity"]["passed"] for row in payload["results"])
            else "failed"
        )

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(text)
    return 0 if payload["status"] in {"dry_run", "passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
