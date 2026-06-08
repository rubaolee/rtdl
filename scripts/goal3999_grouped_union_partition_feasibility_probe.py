#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import pathlib
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    DEFAULT_DATASET_CONFIG,
    make_rt_dbscan_points,
)


@dataclass(frozen=True)
class CellSummary:
    key: tuple[int, int, int]
    count: int
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _cell_key(x: float, y: float, z: float, cell_size: float) -> tuple[int, int, int]:
    return (
        math.floor(x / cell_size),
        math.floor(y / cell_size),
        math.floor(z / cell_size),
    )


def _summarize_cells(profile: str, *, point_count: int, seed: int, cell_size: float) -> list[CellSummary]:
    cells: dict[tuple[int, int, int], list[float]] = {}
    for point in make_rt_dbscan_points(profile, point_count=point_count, seed=seed):
        key = _cell_key(point.x, point.y, point.z, cell_size)
        entry = cells.get(key)
        if entry is None:
            cells[key] = [1.0, point.x, point.y, point.z, point.x, point.y, point.z]
        else:
            entry[0] += 1.0
            entry[1] = min(entry[1], point.x)
            entry[2] = min(entry[2], point.y)
            entry[3] = min(entry[3], point.z)
            entry[4] = max(entry[4], point.x)
            entry[5] = max(entry[5], point.y)
            entry[6] = max(entry[6], point.z)
    return [
        CellSummary(
            key=key,
            count=int(values[0]),
            min_x=values[1],
            min_y=values[2],
            min_z=values[3],
            max_x=values[4],
            max_y=values[5],
            max_z=values[6],
        )
        for key, values in sorted(cells.items())
    ]


def _pair_upper(left_count: int, right_count: int, *, same_cell: bool) -> int:
    if same_cell:
        return left_count * (left_count - 1) // 2
    return left_count * right_count


def _aabb_min_distance_sq(left: CellSummary, right: CellSummary) -> float:
    total = 0.0
    for min_left, max_left, min_right, max_right in (
        (left.min_x, left.max_x, right.min_x, right.max_x),
        (left.min_y, left.max_y, right.min_y, right.max_y),
        (left.min_z, left.max_z, right.min_z, right.max_z),
    ):
        if max_left < min_right:
            delta = min_right - max_left
        elif max_right < min_left:
            delta = min_left - max_right
        else:
            delta = 0.0
        total += delta * delta
    return total


def _aabb_max_distance_sq(left: CellSummary, right: CellSummary) -> float:
    dx = max(abs(left.max_x - right.min_x), abs(right.max_x - left.min_x))
    dy = max(abs(left.max_y - right.min_y), abs(right.max_y - left.min_y))
    dz = max(abs(left.max_z - right.min_z), abs(right.max_z - left.min_z))
    return dx * dx + dy * dy + dz * dz


def _offsets(max_offset: int) -> Iterable[tuple[int, int, int]]:
    for dx in range(-max_offset, max_offset + 1):
        for dy in range(-max_offset, max_offset + 1):
            for dz in range(-max_offset, max_offset + 1):
                yield dx, dy, dz


def _analyze_cell_size(
    profile: str,
    *,
    point_count: int,
    radius: float,
    seed: int,
    cell_size: float,
    cell_size_label: str,
) -> dict[str, object]:
    cells = _summarize_cells(profile, point_count=point_count, seed=seed, cell_size=cell_size)
    by_key = {cell.key: ordinal for ordinal, cell in enumerate(cells)}
    radius_sq = radius * radius
    total_pair_upper = point_count * (point_count - 1) // 2
    total_cell_pairs = len(cells) * (len(cells) + 1) // 2
    max_offset = int(math.ceil(radius / cell_size)) + 1

    enumerated_cell_pairs = 0
    enumerated_pair_upper = 0
    safe_full_cell_pairs = 0
    safe_full_pair_upper = 0
    safe_skip_cell_pairs = 0
    safe_skip_pair_upper = 0
    ambiguous_cell_pairs = 0
    ambiguous_pair_upper = 0
    empty_same_cell_pairs = 0

    offsets = tuple(_offsets(max_offset))
    for left_ordinal, left in enumerate(cells):
        lx, ly, lz = left.key
        for dx, dy, dz in offsets:
            right_ordinal = by_key.get((lx + dx, ly + dy, lz + dz))
            if right_ordinal is None or right_ordinal < left_ordinal:
                continue
            right = cells[right_ordinal]
            same_cell = left_ordinal == right_ordinal
            pair_upper = _pair_upper(left.count, right.count, same_cell=same_cell)
            if pair_upper == 0:
                empty_same_cell_pairs += 1
                continue

            enumerated_cell_pairs += 1
            enumerated_pair_upper += pair_upper
            if _aabb_max_distance_sq(left, right) <= radius_sq:
                safe_full_cell_pairs += 1
                safe_full_pair_upper += pair_upper
            elif _aabb_min_distance_sq(left, right) > radius_sq:
                safe_skip_cell_pairs += 1
                safe_skip_pair_upper += pair_upper
            else:
                ambiguous_cell_pairs += 1
                ambiguous_pair_upper += pair_upper

    far_safe_skip_cell_pairs = total_cell_pairs - enumerated_cell_pairs - empty_same_cell_pairs
    far_safe_skip_pair_upper = total_pair_upper - enumerated_pair_upper
    if far_safe_skip_pair_upper < 0:
        raise RuntimeError("partition accounting produced a negative far skip pair count")
    safe_skip_cell_pairs += max(0, far_safe_skip_cell_pairs)
    safe_skip_pair_upper += far_safe_skip_pair_upper
    decided_pair_upper = safe_full_pair_upper + safe_skip_pair_upper

    def ratio(value: int, denominator: int) -> float:
        return float(value / denominator) if denominator else 0.0

    near_pair_upper = safe_full_pair_upper + ambiguous_pair_upper
    return {
        "cell_size_label": cell_size_label,
        "cell_size": cell_size,
        "enumeration_strategy": "compressed_occupied_key_bounded_offsets",
        "dense_cell_pair_matrix_materialized": False,
        "max_neighbor_offset": max_offset,
        "bounded_offset_count": len(offsets),
        "occupied_cells": len(cells),
        "total_cell_pairs": total_cell_pairs,
        "total_pair_upper": total_pair_upper,
        "enumerated_cell_pairs": enumerated_cell_pairs,
        "enumerated_pair_upper": enumerated_pair_upper,
        "far_safe_skip_cell_pairs": far_safe_skip_cell_pairs,
        "far_safe_skip_pair_upper": far_safe_skip_pair_upper,
        "safe_full_cell_pairs": safe_full_cell_pairs,
        "safe_skip_cell_pairs": safe_skip_cell_pairs,
        "ambiguous_cell_pairs": ambiguous_cell_pairs,
        "safe_full_pair_upper": safe_full_pair_upper,
        "safe_skip_pair_upper": safe_skip_pair_upper,
        "ambiguous_pair_upper": ambiguous_pair_upper,
        "near_pair_upper": near_pair_upper,
        "decided_pair_upper": decided_pair_upper,
        "safe_full_pair_ratio": ratio(safe_full_pair_upper, total_pair_upper),
        "safe_skip_pair_ratio": ratio(safe_skip_pair_upper, total_pair_upper),
        "ambiguous_pair_ratio": ratio(ambiguous_pair_upper, total_pair_upper),
        "decided_pair_ratio": ratio(decided_pair_upper, total_pair_upper),
        "enumerated_cell_pair_ratio": ratio(enumerated_cell_pairs, total_cell_pairs),
        "enumerated_pair_upper_ratio": ratio(enumerated_pair_upper, total_pair_upper),
        "far_safe_skip_pair_ratio": ratio(far_safe_skip_pair_upper, total_pair_upper),
        "ambiguous_of_near_pair_ratio": ratio(ambiguous_pair_upper, near_pair_upper),
        "safe_full_of_near_pair_ratio": ratio(safe_full_pair_upper, near_pair_upper),
        "feasibility_summary": (
            "strong_partition_signal"
            if near_pair_upper and ratio(safe_full_pair_upper, near_pair_upper) >= 0.50
            else "weak_or_boundary_heavy_partition_signal"
        ),
    }


def _profile_radius(profile: str, override_radius: float | None) -> float:
    if override_radius is not None:
        return float(override_radius)
    return float(DEFAULT_DATASET_CONFIG[profile]["radius"])


def _run_profile(
    profile: str,
    *,
    point_count: int,
    radius: float,
    seed: int,
    cell_factors: list[float],
    purpose: str,
) -> dict[str, object]:
    print(
        f"[goal3999] profile={profile} point_count={point_count} radius={radius} purpose={purpose}",
        flush=True,
    )
    rows = []
    for factor in cell_factors:
        cell_size = radius * factor
        if cell_size <= 0.0:
            raise ValueError("cell factors must produce positive cell sizes")
        label = f"radius_x_{factor:g}"
        print(f"[goal3999]   cell_size={cell_size:.8f} label={label}", flush=True)
        rows.append(
            _analyze_cell_size(
                profile,
                point_count=point_count,
                radius=radius,
                seed=seed,
                cell_size=cell_size,
                cell_size_label=label,
            )
        )
    best_by_ambiguous = min(rows, key=lambda row: float(row["ambiguous_pair_ratio"]))
    best_by_full_near = max(rows, key=lambda row: float(row["safe_full_of_near_pair_ratio"]))
    return {
        "profile": profile,
        "point_count": point_count,
        "radius": radius,
        "seed": seed,
        "purpose": purpose,
        "cell_factor_rows": rows,
        "best_ambiguous_pair_ratio": best_by_ambiguous,
        "best_safe_full_of_near_pair_ratio": best_by_full_near,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Goal3999 CPU feasibility probe for partition-assisted grouped union."
    )
    parser.add_argument("--profiles", default="clustered3d,road3d,ngsim_dense")
    parser.add_argument("--point-count", type=int, default=65536)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--cell-factors", default="1.0,0.5,0.25")
    parser.add_argument("--goal", default="Goal3999")
    parser.add_argument("--include-stress", action="store_true")
    parser.add_argument("--stress-profile", default="clustered3d")
    parser.add_argument("--stress-radius", type=float, default=0.5)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("docs/reports/goal3999_grouped_union_partition_feasibility.json"),
    )
    args = parser.parse_args()

    profiles = [part.strip() for part in args.profiles.split(",") if part.strip()]
    cell_factors = [float(part) for part in args.cell_factors.split(",") if part.strip()]
    if not profiles:
        raise ValueError("--profiles must include at least one profile")
    if args.point_count < 2:
        raise ValueError("--point-count must be at least 2")
    if not cell_factors:
        raise ValueError("--cell-factors must include at least one value")
    for profile in profiles:
        if profile not in DEFAULT_DATASET_CONFIG:
            raise ValueError(f"unknown profile: {profile}")

    started = time.perf_counter()
    profile_rows = [
        _run_profile(
            profile,
            point_count=args.point_count,
            radius=_profile_radius(profile, None),
            seed=args.seed,
            cell_factors=cell_factors,
            purpose="current_benchmark_default_radius",
        )
        for profile in profiles
    ]
    if args.include_stress:
        profile_rows.append(
            _run_profile(
                args.stress_profile,
                point_count=args.point_count,
                radius=args.stress_radius,
                seed=args.seed,
                cell_factors=cell_factors,
                purpose="stress_radius_not_current_benchmark_default",
            )
        )

    payload = {
        "goal": args.goal,
        "status": "pass",
        "source_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "elapsed_sec": time.perf_counter() - started,
        "point_count": args.point_count,
        "profiles": profiles,
        "cell_factors": cell_factors,
        "rows": profile_rows,
        "interpretation_boundary": {
            "cpu_feasibility_probe_only": True,
            "native_abi_added": False,
            "performance_claim_authorized": False,
            "release_authorized": False,
            "stress_radius_separate_from_current_benchmark_defaults": bool(args.include_stress),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
