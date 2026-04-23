#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_event_hotspot_screening as event_app
from examples import rtdl_service_coverage_gaps as service_app


GOAL = "Goal811 spatial OptiX prepared-summary phase profiler"
DATE = "2026-04-23"


def _time_call(fn):
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _service_summary_from_count_rows(case: dict[str, tuple[object, ...]], count_rows) -> dict[str, object]:
    household_ids = tuple(int(point.id) for point in case["households"])
    covered = {
        int(row["query_id"])
        for row in count_rows
        if int(row.get("threshold_reached", 0)) != 0
    }
    uncovered = [household_id for household_id in household_ids if household_id not in covered]
    return {
        "household_count": len(case["households"]),
        "clinic_count": len(case["clinics"]),
        "covered_household_count": len(covered),
        "uncovered_household_count": len(uncovered),
        "uncovered_household_ids": uncovered,
        "native_summary_row_count": len(tuple(count_rows)),
    }


def _event_summary_from_count_rows(case: dict[str, tuple[object, ...]], count_rows) -> dict[str, object]:
    neighbor_counts = {
        int(row["query_id"]): max(0, int(row["neighbor_count"]) - 1)
        for row in count_rows
    }
    hotspots = [
        {"event_id": event_id, "neighbor_count": count}
        for event_id, count in neighbor_counts.items()
        if count >= event_app.HOTSPOT_THRESHOLD
    ]
    hotspots.sort(key=lambda item: (-int(item["neighbor_count"]), int(item["event_id"])))
    return {
        "event_count": len(case["events"]),
        "hotspot_count": len(hotspots),
        "hotspots": hotspots,
        "native_summary_row_count": len(tuple(count_rows)),
    }


def _run_service(*, mode: str, copies: int) -> dict[str, object]:
    case, input_sec = _time_call(lambda: service_app.make_service_coverage_case(copies=copies))
    if mode == "dry-run":
        payload, reference_sec = _time_call(lambda: service_app.run_case("cpu_python_reference", copies=copies))
        return {
            "scenario": "service_coverage_gaps",
            "mode": mode,
            "timings_sec": {
                "input_build": input_sec,
                "cpu_reference_total": reference_sec,
            },
            "result": {
                "household_count": payload["household_count"],
                "clinic_count": payload["clinic_count"],
                "covered_household_count": payload["covered_household_count"],
                "uncovered_household_count": len(payload["uncovered_household_ids"]),
                "uncovered_household_ids": payload["uncovered_household_ids"],
            },
        }

    prepared, prepare_sec = _time_call(
        lambda: service_app.rt.prepare_optix_fixed_radius_count_threshold_2d(
            case["clinics"],
            max_radius=service_app.RADIUS,
        )
    )
    try:
        count_rows, query_sec = _time_call(
            lambda: prepared.run(
                case["households"],
                radius=service_app.RADIUS,
                threshold=1,
            )
        )
        result, postprocess_sec = _time_call(lambda: _service_summary_from_count_rows(case, count_rows))
    finally:
        close = getattr(prepared, "close", None)
        if callable(close):
            close()
    return {
        "scenario": "service_coverage_gaps",
        "mode": mode,
        "timings_sec": {
            "input_build": input_sec,
            "optix_prepare": prepare_sec,
            "optix_query": query_sec,
            "python_postprocess": postprocess_sec,
        },
        "result": result,
    }


def _run_event(*, mode: str, copies: int) -> dict[str, object]:
    case, input_sec = _time_call(lambda: event_app.make_event_hotspot_case(copies=copies))
    if mode == "dry-run":
        payload, reference_sec = _time_call(lambda: event_app.run_case("cpu_python_reference", copies=copies))
        return {
            "scenario": "event_hotspot_screening",
            "mode": mode,
            "timings_sec": {
                "input_build": input_sec,
                "cpu_reference_total": reference_sec,
            },
            "result": {
                "event_count": payload["event_count"],
                "hotspot_count": len(payload["hotspots"]),
                "hotspots": payload["hotspots"],
            },
        }

    prepared, prepare_sec = _time_call(
        lambda: event_app.rt.prepare_optix_fixed_radius_count_threshold_2d(
            case["events"],
            max_radius=event_app.RADIUS,
        )
    )
    try:
        count_rows, query_sec = _time_call(
            lambda: prepared.run(
                case["events"],
                radius=event_app.RADIUS,
                threshold=0,
            )
        )
        result, postprocess_sec = _time_call(lambda: _event_summary_from_count_rows(case, count_rows))
    finally:
        close = getattr(prepared, "close", None)
        if callable(close):
            close()
    return {
        "scenario": "event_hotspot_screening",
        "mode": mode,
        "timings_sec": {
            "input_build": input_sec,
            "optix_prepare": prepare_sec,
            "optix_query": query_sec,
            "python_postprocess": postprocess_sec,
        },
        "result": result,
    }


def run_profile(*, scenario: str, mode: str, copies: int) -> dict[str, object]:
    if scenario == "service_coverage_gaps":
        scenario_payload = _run_service(mode=mode, copies=copies)
    elif scenario == "event_hotspot_screening":
        scenario_payload = _run_event(mode=mode, copies=copies)
    else:
        raise ValueError("scenario must be 'service_coverage_gaps' or 'event_hotspot_screening'")
    return {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "copies": copies,
        "scenario": scenario_payload,
        "boundary": (
            "This profiler separates input construction, OptiX preparation, "
            "prepared query, and Python postprocess for compact spatial summaries. "
            "It does not authorize an RTX speedup claim without a real RTX run and review."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile spatial app prepared OptiX summary phases.")
    parser.add_argument(
        "--scenario",
        choices=("service_coverage_gaps", "event_hotspot_screening"),
        required=True,
    )
    parser.add_argument("--mode", choices=("dry-run", "optix"), default="dry-run")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_profile(scenario=args.scenario, mode=args.mode, copies=args.copies)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "scenario": args.scenario,
                "mode": args.mode,
                "output_json": str(args.output_json),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
