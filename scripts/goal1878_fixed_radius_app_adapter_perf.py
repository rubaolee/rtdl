from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from rtdsl.optix_runtime import prepare_optix_fixed_radius_count_threshold_2d
from rtdsl.partner_adapters import allocate_fixed_radius_count_threshold_2d_partner_device_output_columns
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


def _skipped(reason: str) -> dict[str, object]:
    return {"status": "skipped", "reason": reason}


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


def _v1_reused_service(prepared, households, *, radius: float):
    rows = prepared.run(households, radius=radius, threshold=1)
    return tuple(1 - int(row["threshold_reached"]) for row in rows)


def _v1_reused_hotspot(prepared, events, *, radius: float, hotspot_threshold: int):
    rows = prepared.run(events, radius=radius, threshold=hotspot_threshold + 1)
    return tuple(int(row["threshold_reached"]) for row in rows)


def run_case(size: int, *, repeat: int, partner: str, max_reference_pairs: int | None = None) -> dict[str, object]:
    print(f"[goal1878] start case partner={partner} size={size}", flush=True)
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
    v1_service_prepared = prepare_optix_fixed_radius_count_threshold_2d(clinics, max_radius=radius)
    v1_hotspot_prepared = prepare_optix_fixed_radius_count_threshold_2d(events, max_radius=hotspot_radius)
    service_outputs = allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(
        len(households),
        partner=partner,
    )
    hotspot_outputs = allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(
        len(events),
        partner=partner,
    )

    print(f"[goal1878] timing v1.8 host-packed OptiX partner={partner} size={size}", flush=True)
    v1_service = _time(lambda: _v1_service(households, clinics, radius=radius), repeat=repeat)
    v1_hotspot = _time(lambda: _v1_hotspot(events, radius=hotspot_radius, hotspot_threshold=1), repeat=repeat)
    print(f"[goal1878] timing v1.8 reused prepared OptiX partner={partner} size={size}", flush=True)
    v1_reused_service = _time(
        lambda: _v1_reused_service(v1_service_prepared, households, radius=radius),
        repeat=repeat,
    )
    v1_reused_hotspot = _time(
        lambda: _v1_reused_hotspot(v1_hotspot_prepared, events, radius=hotspot_radius, hotspot_threshold=1),
        repeat=repeat,
    )
    service_pairs = len(households) * len(clinics)
    hotspot_pairs = len(events) * len(events)
    if max_reference_pairs is not None and service_pairs > max_reference_pairs:
        ref_service = _skipped(f"dense partner reference would materialize {service_pairs} pairs")
    else:
        print(f"[goal1878] timing dense partner reference service partner={partner} size={size}", flush=True)
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
    if max_reference_pairs is not None and hotspot_pairs > max_reference_pairs:
        ref_hotspot = _skipped(f"dense partner reference would materialize {hotspot_pairs} pairs")
    else:
        print(f"[goal1878] timing dense partner reference hotspot partner={partner} size={size}", flush=True)
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
    print(f"[goal1878] timing unprepared v2 native OptiX partner={partner} size={size}", flush=True)
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
    print(f"[goal1878] timing prepared v2 native OptiX with reusable outputs partner={partner} size={size}", flush=True)
    prepared_native_service = _time(
        lambda: service_coverage_gap_flags_optix_prepared_partner_device_columns(
            service_prepared,
            household_cols,
            radius=radius,
            partner=partner,
            fixed_radius_output_columns=service_outputs,
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
            fixed_radius_output_columns=hotspot_outputs,
        ),
        repeat=repeat,
        partner=partner,
    )
    service_prepared.close()
    hotspot_prepared.close()
    v1_service_prepared.close()
    v1_hotspot_prepared.close()
    print(f"[goal1878] done case partner={partner} size={size}", flush=True)
    return {
        "size": size,
        "partner": partner,
        "service_coverage_gaps": {
            "v1_8_prepared_optix": v1_service,
            "v1_8_reused_prepared_optix": v1_reused_service,
            "goal1873_partner_reference": ref_service,
            "goal1877_v2_native_optix_partner": native_service,
            "goal1879_v2_prepared_native_optix_partner": prepared_native_service,
        },
        "event_hotspot_screening": {
            "v1_8_prepared_optix": v1_hotspot,
            "v1_8_reused_prepared_optix": v1_reused_hotspot,
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
    parser.add_argument("--max-reference-pairs", type=int, default=None)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    sizes = [int(item) for item in args.sizes.split(",") if item.strip()]
    partners = ("torch", "cupy") if args.partner == "both" else (args.partner,)
    results = [
        run_case(
            size,
            repeat=args.repeat,
            partner=partner,
            max_reference_pairs=args.max_reference_pairs,
        )
        for partner in partners
        for size in sizes
    ]
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
