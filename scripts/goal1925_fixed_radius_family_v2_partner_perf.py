#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path

from rtdsl.optix_runtime import prepare_optix_fixed_radius_count_threshold_2d
from rtdsl.partner_adapters import allocate_fixed_radius_count_threshold_2d_partner_device_output_columns
from rtdsl.partner_adapters import fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns
from rtdsl.partner_adapters import prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene
from rtdsl.reference import Point


@dataclass(frozen=True)
class FixedRadiusScenario:
    app: str
    query_count: int
    search_count: int
    query_spacing: float
    search_spacing: float
    radius: float
    threshold: int
    result_kind: str
    bidirectional: bool = False
    search_y_offset: float = 0.0


SCENARIOS = {
    "facility_knn_assignment": FixedRadiusScenario(
        app="facility_knn_assignment",
        query_count=4096,
        search_count=1024,
        query_spacing=2.0,
        search_spacing=8.0,
        radius=1.1,
        threshold=1,
        result_kind="coverage_threshold_decision",
    ),
    "hausdorff_distance": FixedRadiusScenario(
        app="hausdorff_distance",
        query_count=4096,
        search_count=2048,
        query_spacing=2.0,
        search_spacing=4.0,
        radius=1.5,
        threshold=1,
        result_kind="bidirectional_threshold_decision",
        bidirectional=True,
        search_y_offset=1.0,
    ),
    "ann_candidate_search": FixedRadiusScenario(
        app="ann_candidate_search",
        query_count=4096,
        search_count=8192,
        query_spacing=2.0,
        search_spacing=1.0,
        radius=0.1,
        threshold=1,
        result_kind="candidate_coverage_threshold_decision",
    ),
    "outlier_detection": FixedRadiusScenario(
        app="outlier_detection",
        query_count=4096,
        search_count=4096,
        query_spacing=1.0,
        search_spacing=1.0,
        radius=1.1,
        threshold=3,
        result_kind="scalar_outlier_count",
    ),
    "dbscan_clustering": FixedRadiusScenario(
        app="dbscan_clustering",
        query_count=4096,
        search_count=4096,
        query_spacing=1.0,
        search_spacing=1.0,
        radius=1.1,
        threshold=3,
        result_kind="scalar_core_count",
    ),
    "barnes_hut_force_app": FixedRadiusScenario(
        app="barnes_hut_force_app",
        query_count=4096,
        search_count=1024,
        query_spacing=4.0,
        search_spacing=16.0,
        radius=1.1,
        threshold=1,
        result_kind="node_coverage_threshold_decision",
    ),
}


def _points(count: int, *, spacing: float, y_offset: float = 0.0) -> tuple[Point, ...]:
    return tuple(Point(index + 1, float(index) * spacing, y_offset) for index in range(count))


def _partner_columns(points: tuple[Point, ...], partner: str) -> dict[str, object]:
    if partner == "torch":
        import torch

        device = torch.device("cuda:0")
        return {
            "ids": torch.tensor([point.id for point in points], dtype=torch.uint32, device=device),
            "x": torch.tensor([point.x for point in points], dtype=torch.float64, device=device),
            "y": torch.tensor([point.y for point in points], dtype=torch.float64, device=device),
        }
    if partner == "cupy":
        import cupy

        return {
            "ids": cupy.asarray([point.id for point in points], dtype=cupy.uint32),
            "x": cupy.asarray([point.x for point in points], dtype=cupy.float64),
            "y": cupy.asarray([point.y for point in points], dtype=cupy.float64),
        }
    raise ValueError("partner must be 'torch' or 'cupy'")


def _sync(partner: str) -> None:
    if partner == "torch":
        import torch

        torch.cuda.synchronize()
    elif partner == "cupy":
        import cupy

        cupy.cuda.runtime.deviceSynchronize()


def _to_host_uint32(values, partner: str) -> list[int]:
    if partner == "torch":
        return [int(item) for item in values.detach().cpu().tolist()]
    if partner == "cupy":
        import cupy

        return [int(item) for item in cupy.asnumpy(values).tolist()]
    raise ValueError("partner must be 'torch' or 'cupy'")


def _summarize_counts(app: str, counts: list[int], threshold: int) -> dict[str, int]:
    reached = sum(1 for count in counts if int(count) >= int(threshold))
    if app == "outlier_detection":
        return {"threshold_reached_count": reached, "outlier_count": len(counts) - reached}
    if app == "dbscan_clustering":
        return {"threshold_reached_count": reached, "core_count": reached}
    return {"threshold_reached_count": reached, "not_reached_count": len(counts) - reached}


def _stats(samples: list[float]) -> dict[str, float]:
    return {
        "min_s": min(samples),
        "median_s": statistics.median(samples),
        "max_s": max(samples),
    }


def _time(label: str, repeat: int, fn, *, partner: str | None = None):
    samples = []
    last = None
    print(f"[goal1925] timing {label} repeat={repeat}", flush=True)
    for index in range(repeat):
        start = time.perf_counter()
        last = fn()
        if partner:
            _sync(partner)
        elapsed = time.perf_counter() - start
        samples.append(elapsed)
        print(f"[goal1925] {label} iter={index + 1} elapsed_s={elapsed:.6f}", flush=True)
    return _stats(samples), last


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _gpu_name() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _run_one_direction(scenario: FixedRadiusScenario, query_points, search_points, *, repeat: int, partner: str):
    query_cols = _partner_columns(query_points, partner)
    search_cols = _partner_columns(search_points, partner)
    prepared_v1 = prepare_optix_fixed_radius_count_threshold_2d(search_points, max_radius=scenario.radius)
    prepared_v2 = prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(
        search_cols,
        max_radius=scenario.radius,
        partner=partner,
    )
    output_cols = allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(
        len(query_points),
        partner=partner,
    )
    try:
        v1_stats, v1_rows = _time(
            f"{scenario.app}:v1_8_prepared_optix:{partner}",
            repeat,
            lambda: prepared_v1.run(query_points, radius=scenario.radius, threshold=scenario.threshold),
        )
        v2_stats, v2_result = _time(
            f"{scenario.app}:v2_prepared_partner:{partner}",
            repeat,
            lambda: fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
                prepared_v2,
                query_cols,
                radius=scenario.radius,
                threshold=scenario.threshold,
                partner=partner,
                output_columns=output_cols,
                return_metadata=True,
            ),
            partner=partner,
        )
        v1_counts = [int(row["neighbor_count"]) for row in v1_rows]
        v2_counts = _to_host_uint32(v2_result["columns"]["neighbor_counts"], partner)
        return {
            "v1_8_prepared_optix": v1_stats,
            "v2_prepared_native_optix_partner": v2_stats,
            "v2_vs_v1_8_prepared_ratio": (
                v2_stats["median_s"] / v1_stats["median_s"] if v1_stats["median_s"] > 0.0 else None
            ),
            "parity": {
                "counts_match": tuple(v1_counts) == tuple(v2_counts),
                "summary_match": _summarize_counts(scenario.app, v1_counts, scenario.threshold)
                == _summarize_counts(scenario.app, v2_counts, scenario.threshold),
            },
            "summary": _summarize_counts(scenario.app, v2_counts, scenario.threshold),
            "output_contract": "partner_owned_fixed_radius_count_threshold_columns",
        }
    finally:
        prepared_v1.close()
        prepared_v2.close()


def run_case(scenario: FixedRadiusScenario, *, repeat: int, partner: str) -> dict[str, object]:
    print(f"[goal1925] start app={scenario.app} partner={partner}", flush=True)
    query_points = _points(scenario.query_count, spacing=scenario.query_spacing)
    search_points = _points(
        scenario.search_count,
        spacing=scenario.search_spacing,
        y_offset=scenario.search_y_offset,
    )
    forward = _run_one_direction(scenario, query_points, search_points, repeat=repeat, partner=partner)
    result = {
        "app": scenario.app,
        "partner": partner,
        "query_count": scenario.query_count,
        "search_count": scenario.search_count,
        "radius": scenario.radius,
        "threshold": scenario.threshold,
        "result_kind": scenario.result_kind,
        "forward": forward,
        "status": "pass" if forward["parity"]["counts_match"] and forward["parity"]["summary_match"] else "fail",
    }
    if scenario.bidirectional:
        reverse = _run_one_direction(scenario, search_points, query_points, repeat=repeat, partner=partner)
        result["reverse"] = reverse
        result["status"] = (
            "pass"
            if result["status"] == "pass"
            and reverse["parity"]["counts_match"]
            and reverse["parity"]["summary_match"]
            else "fail"
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1925 fixed-radius v2 partner family performance harness.")
    parser.add_argument("--apps", default=",".join(SCENARIOS))
    parser.add_argument("--partners", default="cupy,torch")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument(
        "--query-count-override",
        type=int,
        default=None,
        help="Override every scenario's query count for large-scale pod runs.",
    )
    parser.add_argument(
        "--search-count-override",
        type=int,
        default=None,
        help="Override every scenario's search count for large-scale pod runs.",
    )
    parser.add_argument("--output", default="docs/reports/goal1925_fixed_radius_family_v2_partner_perf.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested_apps = [item.strip() for item in args.apps.split(",") if item.strip()]
    partners = [item.strip() for item in args.partners.split(",") if item.strip()]
    results = []
    for app in requested_apps:
        if app not in SCENARIOS:
            raise SystemExit(f"unknown app {app!r}; expected one of {', '.join(SCENARIOS)}")
        scenario = SCENARIOS[app]
        if args.query_count_override is not None or args.search_count_override is not None:
            scenario = replace(
                scenario,
                query_count=args.query_count_override
                if args.query_count_override is not None
                else scenario.query_count,
                search_count=args.search_count_override
                if args.search_count_override is not None
                else scenario.search_count,
            )
        for partner in partners:
            results.append(run_case(scenario, repeat=args.repeat, partner=partner))
    commit = _git_commit()
    payload = {
        "goal": "Goal1925",
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "git_commit": commit,
        "source_commit_label": commit,
        "gpu": _gpu_name(),
        "results": results,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "package_install_claim_authorized": False,
            "fixed_radius_family_true_zero_copy_authorized": False,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
