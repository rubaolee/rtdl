#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_segment_polygon_hitcount as app


GOAL = "Goal807 segment/polygon OptiX native-mode gate"
DATE = "2026-04-23"


def _row_digest(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    normalized = tuple(
        sorted(
            (
                int(row["segment_id"]),
                int(row["hit_count"]),
            )
            for row in rows
        )
    )
    hasher = hashlib.sha256()
    for segment_id, hit_count in normalized:
        hasher.update(f"{segment_id}\t{hit_count}\n".encode("utf-8"))
    return {"row_count": len(normalized), "sha256": hasher.hexdigest()}


def _timed_payload(label: str, fn: Callable[[], dict[str, object]]) -> dict[str, object]:
    start = time.perf_counter()
    try:
        payload = fn()
    except Exception as exc:  # noqa: BLE001 - benchmark gates must record optional backend absence.
        return {
            "label": label,
            "status": "unavailable_or_failed",
            "sec": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    rows = tuple(payload.get("rows", ()))
    record = {
        "label": label,
        "status": "ok",
        "sec": time.perf_counter() - start,
        "backend": payload.get("backend"),
        "optix_mode": payload.get("optix_mode"),
        "row_digest": payload.get("row_digest", _row_digest(rows)),
        "optix_performance": payload.get("optix_performance"),
    }
    for key in ("postgis_query_sec",):
        if key in payload:
            record[key] = payload[key]
    return record


def _postgis_record(dataset: str, db_name: str, db_user: str | None) -> dict[str, object]:
    from rtdsl.goal114_segment_polygon_postgis import run_postgis_segment_polygon_hitcount

    start = time.perf_counter()
    rows, query_sec = run_postgis_segment_polygon_hitcount(
        db_name=db_name,
        db_user=db_user,
        dataset=dataset,
    )
    return {
        "label": "postgis",
        "status": "ok",
        "sec": time.perf_counter() - start,
        "postgis_query_sec": query_sec,
        "row_digest": _row_digest(tuple(rows)),
    }


def _attach_parity(records: list[dict[str, object]], baseline_label: str) -> None:
    baseline = next(
        (record for record in records if record["label"] == baseline_label and record["status"] == "ok"),
        None,
    )
    baseline_digest = baseline.get("row_digest") if baseline else None
    for record in records:
        if record["status"] != "ok":
            record["parity_vs_cpu_python_reference"] = False
            continue
        record["parity_vs_cpu_python_reference"] = record.get("row_digest") == baseline_digest


def run_gate(
    *,
    dataset: str,
    include_postgis: bool = False,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
    strict: bool = False,
) -> dict[str, object]:
    records = [
        _timed_payload(
            "cpu_python_reference",
            lambda: app.run_case("cpu_python_reference", dataset),
        ),
        _timed_payload(
            "optix_host_indexed",
            lambda: app.run_case("optix", dataset, optix_mode="host_indexed"),
        ),
        _timed_payload(
            "optix_native",
            lambda: app.run_case("optix", dataset, optix_mode="native"),
        ),
    ]
    if include_postgis:
        records.append(
            _timed_payload(
                "postgis",
                lambda: _postgis_record(dataset, db_name, db_user),
            )
        )

    _attach_parity(records, "cpu_python_reference")
    by_label = {str(record["label"]): record for record in records}
    strict_failures: list[str] = []
    if by_label["cpu_python_reference"]["status"] != "ok":
        strict_failures.append("cpu_python_reference did not run")
    if by_label["optix_host_indexed"]["status"] != "ok":
        strict_failures.append("optix_host_indexed did not run")
    if by_label["optix_native"]["status"] != "ok":
        strict_failures.append("optix_native did not run")
    for label in ("optix_host_indexed", "optix_native"):
        record = by_label[label]
        if record["status"] == "ok" and not record["parity_vs_cpu_python_reference"]:
            strict_failures.append(f"{label} failed parity against CPU reference")
    if include_postgis:
        postgis = by_label["postgis"]
        if postgis["status"] != "ok":
            strict_failures.append("postgis did not run")
        elif not postgis["parity_vs_cpu_python_reference"]:
            strict_failures.append("postgis failed parity against CPU reference")

    payload: dict[str, Any] = {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "dataset": dataset,
        "include_postgis": include_postgis,
        "records": records,
        "strict": strict,
        "strict_pass": not strict_failures,
        "strict_failures": strict_failures,
        "activation_rule": (
            "segment_polygon_hitcount can only move from deferred RTX candidate "
            "to active RTX benchmark target after optix_native and optix_host_indexed "
            "both run, match the CPU reference, and are reviewed against the PostGIS "
            "baseline where PostGIS is available."
        ),
        "boundary": (
            "This gate makes the native custom-AABB OptiX mode replayable. It does "
            "not authorize a public NVIDIA RT-core speedup claim by itself."
        ),
    }
    if strict and strict_failures:
        payload["status"] = "fail"
    else:
        payload["status"] = "pass" if not strict_failures else "non_strict_recorded_gaps"
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate segment/polygon OptiX native mode against reference paths.")
    parser.add_argument(
        "--dataset",
        default="authored_segment_polygon_minimal",
        help="Representative dataset name, including derived/..._tiled_xN forms.",
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=None,
        help="Shortcut for derived/br_county_subset_segment_polygon_tiled_xN.",
    )
    parser.add_argument("--include-postgis", action="store_true")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    dataset = (
        app.rt.segment_polygon_large_dataset_name(copies=args.copies)
        if args.copies is not None
        else args.dataset
    )
    payload = run_gate(
        dataset=dataset,
        include_postgis=args.include_postgis,
        db_name=args.db_name,
        db_user=args.db_user,
        strict=args.strict,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output_json": str(args.output_json)}, sort_keys=True))
    return 1 if args.strict and payload["strict_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
