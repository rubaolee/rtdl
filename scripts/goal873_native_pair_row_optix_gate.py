#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import hashlib
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

import rtdsl as rt
from examples.reference.rtdl_release_reference import segment_polygon_anyhit_rows_reference
from rtdsl import optix_runtime
from rtdsl.baseline_runner import load_representative_case


GOAL = "Goal873 native bounded pair-row OptiX gate"
DATE = "2026-04-24"


def _row_digest(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    normalized = tuple(
        sorted((int(row["segment_id"]), int(row["polygon_id"])) for row in rows)
    )
    hasher = hashlib.sha256()
    for segment_id, polygon_id in normalized:
        hasher.update(f"{segment_id}\t{polygon_id}\n".encode("utf-8"))
    return {"row_count": len(normalized), "sha256": hasher.hexdigest()}


def _rows_from_native_buffer(buffer, count: int) -> tuple[dict[str, object], ...]:
    return tuple(
        {"segment_id": int(buffer[i].segment_id), "polygon_id": int(buffer[i].polygon_id)}
        for i in range(count)
    )


def _run_cpu_reference(dataset: str) -> tuple[dict[str, object], ...]:
    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    return rt.run_cpu_python_reference(segment_polygon_anyhit_rows_reference, **case.inputs)


def _run_native_bounded(dataset: str, output_capacity: int) -> dict[str, object]:
    case = load_representative_case("segment_polygon_anyhit_rows", dataset)
    packed_segments = optix_runtime.pack_segments(case.inputs["segments"])
    packed_polygons = optix_runtime.pack_polygons(case.inputs["polygons"])
    lib = optix_runtime._load_optix_library()
    symbol = getattr(lib, "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded", None)
    if symbol is None:
        raise RuntimeError("loaded OptiX backend does not export rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded")
    row_array = (
        optix_runtime._RtdlSegmentPolygonAnyHitRow * output_capacity
    )() if output_capacity else None
    emitted = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = symbol(
        packed_segments.records,
        packed_segments.count,
        packed_polygons.refs,
        packed_polygons.polygon_count,
        packed_polygons.vertices_xy,
        packed_polygons.vertex_xy_count,
        row_array,
        output_capacity,
        ctypes.byref(emitted),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    if status != 0:
        detail = error.value.decode("utf-8", "replace")
        raise RuntimeError(detail or f"native bounded OptiX call failed with status {status}")
    copied = min(int(emitted.value), output_capacity)
    rows = _rows_from_native_buffer(row_array, copied) if row_array is not None else ()
    return {
        "emitted_count": int(emitted.value),
        "copied_count": copied,
        "overflowed": int(overflowed.value),
        "row_digest": _row_digest(rows),
    }


def run_gate(*, dataset: str, output_capacity: int, strict: bool = False) -> dict[str, object]:
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")
    records: list[dict[str, object]] = []
    start = time.perf_counter()
    cpu_rows = _run_cpu_reference(dataset)
    cpu_record = {
        "label": "cpu_python_reference",
        "status": "ok",
        "sec": time.perf_counter() - start,
        "row_digest": _row_digest(cpu_rows),
    }
    records.append(cpu_record)

    start = time.perf_counter()
    try:
        native_record = {
            "label": "optix_native_bounded",
            "status": "ok",
            "sec": time.perf_counter() - start,
            **_run_native_bounded(dataset, output_capacity),
        }
    except Exception as exc:  # noqa: BLE001 - optional backend gate records absence.
        native_record = {
            "label": "optix_native_bounded",
            "status": "unavailable_or_failed",
            "sec": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    records.append(native_record)

    strict_failures: list[str] = []
    if native_record["status"] != "ok":
        strict_failures.append("optix_native_bounded did not run")
    else:
        native_record["parity_vs_cpu_python_reference"] = (
            native_record.get("row_digest") == cpu_record["row_digest"]
        )
        if not native_record["parity_vs_cpu_python_reference"]:
            strict_failures.append("optix_native_bounded failed row digest parity")
        if int(native_record["overflowed"]) != 0:
            strict_failures.append("optix_native_bounded overflowed output capacity")

    payload: dict[str, Any] = {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "dataset": dataset,
        "output_capacity": output_capacity,
        "records": records,
        "strict": strict,
        "strict_failures": strict_failures,
        "strict_pass": not strict_failures,
        "status": "pass" if not strict_failures else ("fail" if strict else "non_strict_recorded_gaps"),
        "boundary": (
            "This gate validates the new native bounded pair-row OptiX symbol. "
            "It does not promote the public segment_polygon_anyhit_rows path by itself."
        ),
    }
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the native bounded OptiX pair-row gate.")
    parser.add_argument("--dataset", default="authored_segment_polygon_minimal")
    parser.add_argument("--output-capacity", type=int, default=1024)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs" / "reports" / "goal873_native_pair_row_optix_gate_2026-04-24.json")
    args = parser.parse_args(argv)
    if args.output_capacity <= 0:
        parser.error("--output-capacity must be positive")
    payload = run_gate(dataset=args.dataset, output_capacity=args.output_capacity, strict=args.strict)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "status": payload["status"], "strict_pass": payload["strict_pass"]}, sort_keys=True))
    return 1 if args.strict and not payload["strict_pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
