from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from rtdsl.optix_runtime import prepare_optix_fixed_radius_count_threshold_2d
from rtdsl.partner_adapters import event_hotspot_flags_optix_partner_device_columns
from rtdsl.partner_adapters import event_hotspot_flags_optix_prepared_partner_device_columns
from rtdsl.partner_adapters import event_hotspot_flags_partner_columns
from rtdsl.partner_adapters import prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene
from rtdsl.partner_adapters import service_coverage_gap_flags_optix_partner_device_columns
from rtdsl.partner_adapters import service_coverage_gap_flags_optix_prepared_partner_device_columns
from rtdsl.partner_adapters import service_coverage_gap_flags_partner_columns
from rtdsl.reference import Point


def _points(count: int, *, spacing: float, y_offset: float = 0.0) -> tuple[Point, ...]:
    return tuple(Point(i, float(i) * spacing, y_offset) for i in range(count))


def _torch_columns(points):
    import torch

    return {
        "ids": torch.tensor([p.id for p in points], dtype=torch.uint32, device="cuda"),
        "x": torch.tensor([p.x for p in points], dtype=torch.float64, device="cuda"),
        "y": torch.tensor([p.y for p in points], dtype=torch.float64, device="cuda"),
    }


def _cupy_columns(points):
    import cupy

    return {
        "ids": cupy.asarray([p.id for p in points], dtype=cupy.uint32),
        "x": cupy.asarray([p.x for p in points], dtype=cupy.float64),
        "y": cupy.asarray([p.y for p in points], dtype=cupy.float64),
    }


def _sync(partner: str) -> None:
    if partner == "torch":
        import torch

        torch.cuda.synchronize()
    elif partner == "cupy":
        import cupy

        cupy.cuda.runtime.deviceSynchronize()


def _median(times: list[float]) -> float:
    return float(statistics.median(times)) if times else 0.0


def _time(call, *, repeat: int, partner: str | None = None) -> dict[str, float]:
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        call()
        if partner:
            _sync(partner)
        times.append(time.perf_counter() - start)
    return {
        "median_s": _median(times),
        "min_s": float(min(times)),
        "max_s": float(max(times)),
        "repeat": repeat,
    }


def _v1_service(households, clinics, *, radius: float):
    prepared = prepare_optix_fixed_radius_count_threshold_2d(clinics, max_radius=radius)
    try:
        rows = prepared.run(households, radius=radius, threshold=1)
        return tuple(1 - int(row["threshold_reached"]) for row in rows)
    finally:
        prepared.close()


def _v1_hotspot(events, *, radius: float, hotspot_threshold: int):
    prepared = prepare_optix_fixed_radius_count_threshold_2d(events, max_radius=radius)
    try:
        rows = prepared.run(events, radius=radius, threshold=hotspot_threshold + 1)
        return tuple(int(row["threshold_reached"]) for row in rows)
    finally:
        prepared.close()


def run_case(size: int, *, repeat: int, partner: str) -> dict[str, object]:
    radius = 1.1
    hotspot_radius = 2.1
    households = _points(size, spacing=2.0)
    clinics = _points(max(1, size // 2), spacing=4.0)
    events = _points(size, spacing=2.0)
    make_columns = _torch_columns if partner == "torch" else _cupy_columns
    household_cols = make_columns(households)
    clinic_cols = make_columns(clinics)
    event_cols = make_columns(events)
    service_prepared = prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(
        clinic_cols,
        max_radius=radius,
        partner=partner,
    )
    hotspot_prepared = prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(
        event_cols,
        max_radius=hotspot_radius,
        partner=partner,
    )

    v1_service = _time(lambda: _v1_service(households, clinics, radius=radius), repeat=repeat)
    v1_hotspot = _time(lambda: _v1_hotspot(events, radius=hotspot_radius, hotspot_threshold=1), repeat=repeat)
    ref_service = _time(
        lambda: service_coverage_gap_flags_partner_columns(
            household_cols,
            clinic_cols,
            radius=radius,
            partner=partner,
        ),
        repeat=repeat,
        partner=partner,
    )
    ref_hotspot = _time(
        lambda: event_hotspot_flags_partner_columns(
            event_cols,
            radius=hotspot_radius,
            hotspot_threshold=1,
            partner=partner,
        ),
        repeat=repeat,
        partner=partner,
    )
    native_service = _time(
        lambda: service_coverage_gap_flags_optix_partner_device_columns(
            household_cols,
            clinic_cols,
            radius=radius,
            partner=partner,
        ),
        repeat=repeat,
        partner=partner,
    )
    native_hotspot = _time(
        lambda: event_hotspot_flags_optix_partner_device_columns(
            event_cols,
            radius=hotspot_radius,
            hotspot_threshold=1,
            partner=partner,
        ),
        repeat=repeat,
        partner=partner,
    )
    prepared_native_service = _time(
        lambda: service_coverage_gap_flags_optix_prepared_partner_device_columns(
            service_prepared,
            household_cols,
            radius=radius,
            partner=partner,
        ),
        repeat=repeat,
        partner=partner,
    )
    prepared_native_hotspot = _time(
        lambda: event_hotspot_flags_optix_prepared_partner_device_columns(
            hotspot_prepared,
            event_cols,
            radius=hotspot_radius,
            hotspot_threshold=1,
            partner=partner,
        ),
        repeat=repeat,
        partner=partner,
    )
    service_prepared.close()
    hotspot_prepared.close()
    return {
        "size": size,
        "partner": partner,
        "service_coverage_gaps": {
            "v1_8_prepared_optix": v1_service,
            "goal1873_partner_reference": ref_service,
            "goal1877_v2_native_optix_partner": native_service,
            "goal1879_v2_prepared_native_optix_partner": prepared_native_service,
        },
        "event_hotspot_screening": {
            "v1_8_prepared_optix": v1_hotspot,
            "goal1873_partner_reference": ref_hotspot,
            "goal1877_v2_native_optix_partner": native_hotspot,
            "goal1879_v2_prepared_native_optix_partner": prepared_native_hotspot,
        },
        "claim_boundaries": {
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="256,1024")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--partner", choices=("torch", "cupy", "both"), default="both")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    sizes = [int(item) for item in args.sizes.split(",") if item.strip()]
    partners = ("torch", "cupy") if args.partner == "both" else (args.partner,)
    results = [run_case(size, repeat=args.repeat, partner=partner) for partner in partners for size in sizes]
    payload = {
        "goal": 1878,
        "status": "measurement",
        "date": "2026-05-13",
        "results": results,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
