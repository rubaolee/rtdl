from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from scripts.goal2147_rayjoin_v2_scale_perf import make_case  # noqa: E402
from examples.v2_0.research_benchmarks.spatial_rayjoin import (  # noqa: E402
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)
from rtdsl.optix_runtime import pack_points  # noqa: E402
from rtdsl.optix_runtime import pack_polygons  # noqa: E402
from rtdsl.optix_runtime import pack_segments  # noqa: E402
from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix  # noqa: E402
from rtdsl.optix_runtime import prepare_shape_pair_relation_flags_optix  # noqa: E402


WORKLOAD_FIELDS = {
    "pip": ("point_id", "shape_id", "membership"),
    "lsi": ("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
    "overlay_seed": ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"),
}
CLAIM_BOUNDARY = {
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "device_resident_handoff_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "v2_5_release_authorized": False,
    "native_engine_customization": False,
}


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _sync_partner(partner: str) -> None:
    if partner == "cupy":
        import cupy

        cupy.cuda.runtime.deviceSynchronize()
    elif partner in {"torch", "triton"}:
        import torch

        torch.cuda.synchronize()


def _expected_count(workload: str, inputs: dict[str, tuple[object, ...]]) -> int:
    kernel = rayjoin_app._KERNELS[workload]
    rows = rayjoin_app._run_backend(kernel, "cpu_python_reference", inputs)
    return len(rows)


def _prepare(workload: str, inputs: dict[str, tuple[object, ...]]):
    if workload == "pip":
        packed_points = pack_points(records=inputs["points"], dimension=2)
        packed_polygons = pack_polygons(records=inputs["polygons"])
        prepared = prepare_point_closed_shape_membership_2d_optix(packed_polygons)
        return prepared, packed_points
    if workload == "lsi":
        packed_left = pack_segments(records=inputs["left"])
        prepared = prepare_segment_pair_intersection_optix(inputs["right"])
        return prepared, packed_left
    if workload == "overlay_seed":
        packed_left = pack_polygons(records=inputs["left"])
        packed_right = pack_polygons(records=inputs["right"])
        prepared = prepare_shape_pair_relation_flags_optix(packed_right)
        return prepared, packed_left
    raise ValueError(f"unsupported workload: {workload}")


def _run_raw(prepared, workload: str, query):
    if workload == "pip":
        return prepared.run_raw(query, result_mode="positive_hits")
    return prepared.run_raw(query)


def _count_only(prepared, workload: str, query) -> int:
    if workload in {"pip", "lsi"}:
        return int(prepared.count(query))
    view = _run_raw(prepared, workload, query)
    try:
        return int(view.row_count)
    finally:
        view.close()


def _time_repeats(label: str, fn, *, warmups: int, repeats: int) -> dict[str, object]:
    for index in range(warmups):
        value = fn()
        print(f"[goal2941] warmup {label} {index + 1}/{warmups} value={value}", flush=True)
    seconds: list[float] = []
    values: list[int] = []
    for index in range(repeats):
        start = time.perf_counter()
        value = fn()
        elapsed = time.perf_counter() - start
        seconds.append(elapsed)
        values.append(int(value))
        print(f"[goal2941] repeat {label} {index + 1}/{repeats} value={value} sec={elapsed:.6f}", flush=True)
    return {
        "median_sec": _median(seconds),
        "min_sec": float(min(seconds)),
        "max_sec": float(max(seconds)),
        "values": values,
        "value_consistent": len(set(values)) == 1,
    }


def run_workload(
    workload: str,
    *,
    scale: str,
    partner: str,
    warmups: int,
    repeats: int,
) -> dict[str, Any]:
    inputs = make_case(workload, scale)
    input_counts = {name: len(value) for name, value in inputs.items()}
    expected_count = _expected_count(workload, inputs)
    prepared, query = _prepare(workload, inputs)
    fields = WORKLOAD_FIELDS[workload]
    last_metadata: dict[str, object] = {}
    try:
        count_only = _time_repeats(
            f"{workload}/count_only",
            lambda: _count_only(prepared, workload, query),
            warmups=warmups,
            repeats=repeats,
        )

        def raw_to_partner_columns() -> int:
            nonlocal last_metadata
            view = _run_raw(prepared, workload, query)
            try:
                result = rt.optix_row_view_to_partner_columns(
                    view,
                    fields=fields,
                    partner=partner,
                    return_metadata=True,
                )
                _sync_partner(partner)
                last_metadata = dict(result["metadata"])
                return int(view.row_count)
            finally:
                view.close()

        typed_columns = _time_repeats(
            f"{workload}/typed_columns_{partner}",
            raw_to_partner_columns,
            warmups=warmups,
            repeats=repeats,
        )
    finally:
        prepared.close()

    overhead_ratio = (
        float(typed_columns["median_sec"]) / float(count_only["median_sec"])
        if float(count_only["median_sec"]) > 0.0
        else None
    )
    return {
        "workload": workload,
        "status": (
            "pass"
            if count_only["value_consistent"]
            and typed_columns["value_consistent"]
            and all(value == expected_count for value in count_only["values"] + typed_columns["values"])
            else "fail"
        ),
        "scale": scale,
        "partner": partner,
        "input_counts": input_counts,
        "expected_row_count": int(expected_count),
        "fields": fields,
        "count_only": count_only,
        "typed_columns": typed_columns,
        "typed_columns_over_count_only_ratio": overhead_ratio,
        "python_dict_row_materialization_used": bool(
            last_metadata.get("python_dict_row_materialization_used", True)
        ),
        "last_typed_columns_metadata": last_metadata,
    }


def run_probe(
    *,
    scale: str,
    workloads: tuple[str, ...],
    partner: str,
    warmups: int,
    repeats: int,
) -> dict[str, Any]:
    rows = [
        run_workload(
            workload,
            scale=scale,
            partner=partner,
            warmups=warmups,
            repeats=repeats,
        )
        for workload in workloads
    ]
    return {
        "goal": "Goal2941",
        "schema": "rtdl.goal2941.rayjoin_row_view_partner_columns_scale_probe.v1",
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "scale": scale,
        "partner": partner,
        "warmups": int(warmups),
        "repeats": int(repeats),
        "rows": rows,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _parse_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal2941 RayJoin row-view partner-column scale probe.")
    parser.add_argument("--scale", choices=("quick", "medium", "large"), default="large")
    parser.add_argument("--workloads", default="pip,lsi,overlay_seed")
    parser.add_argument("--partner", choices=("torch", "triton", "cupy"), default="cupy")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    workloads = _parse_csv(args.workloads)
    unknown = sorted(set(workloads) - set(WORKLOAD_FIELDS))
    if unknown:
        raise ValueError(f"unsupported workloads: {unknown}")
    payload = run_probe(
        scale=args.scale,
        workloads=workloads,
        partner=args.partner,
        warmups=args.warmups,
        repeats=args.repeats,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rayjoin_app._json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal2941] wrote {args.output} status={payload['status']}", flush=True)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
