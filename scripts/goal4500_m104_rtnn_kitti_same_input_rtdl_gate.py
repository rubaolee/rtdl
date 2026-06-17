from __future__ import annotations

from dataclasses import asdict
import argparse
import contextlib
import io
import json
from argparse import Namespace
import os
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtnn_kitti_same_input_rtdl_gate.goal4500.v1"
OUT_JSON = Path("docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.md")
DEFAULT_SOURCE_ROOT_CANDIDATES = (
    "/workspace/data/kitti/extracted",
    "/workspace/data/kitti",
    "/data/kitti",
    "data/kitti",
)
DEFAULT_WORK_DIR = Path(os.environ.get("RTDL_KITTI_M104_WORK_DIR", "/workspace/data/kitti/rtdl_goal4500"))


def _source_root_candidates(explicit: str | Path | None) -> tuple[str, ...]:
    candidates: list[str] = []
    if explicit is not None:
        candidates.append(str(explicit))
    env_root = os.environ.get("RTDL_KITTI_SOURCE_ROOT")
    if env_root:
        candidates.append(env_root)
    candidates.extend(DEFAULT_SOURCE_ROOT_CANDIDATES)
    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return tuple(unique)


def _resolve_first_ready_source_root(explicit: str | Path | None) -> Path | None:
    for candidate in _source_root_candidates(explicit):
        resolved = rt.resolve_kitti_source_root(candidate)
        if resolved is None:
            continue
        try:
            if rt.discover_kitti_velodyne_frames(resolved):
                return resolved
        except RuntimeError:
            continue
    return None


def _run_rtdl_backend(
    *,
    backend: str,
    point_file: Path,
    radius: float,
    k_max: int,
    query_batch_size: int,
    repeat: int,
) -> dict[str, Any]:
    from scripts import goal2348_rtnn_v2_2_external_runner as rtnn_runner

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        payload = rtnn_runner.run_rtdl_batched_3d_neighbors(
            Namespace(
                point_file=point_file,
                query_file=None,
                radius=radius,
                k_max=k_max,
                backend=backend,
                query_batch_size=query_batch_size,
                result_mode="ranked-summary-aggregate",
                aggregate_request_count=1,
                aggregate_radius_multipliers=None,
                aggregate_k_values=None,
                repeat=repeat,
                row_label=f"goal4500_kitti_1m_{backend}_ranked_summary_aggregate",
            )
        )
    return {
        "runner_stdout": tuple(line for line in stdout.getvalue().splitlines() if line.strip()),
        "payload": payload,
    }


def _signature(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("ranked_aggregate_summary") or {}
    return {
        "row_count": int(summary.get("row_count", 0)),
        "bounded_neighbor_count": int(summary.get("bounded_neighbor_count", 0)),
        "nearest_id_checksum": int(summary.get("nearest_id_checksum", 0)),
        "kth_id_checksum": int(summary.get("kth_id_checksum", 0)),
        "sum_distance": float(summary.get("sum_distance", 0.0)),
    }


def _signatures_match(optix_payload: dict[str, Any] | None, embree_payload: dict[str, Any] | None) -> bool:
    if optix_payload is None or embree_payload is None:
        return False
    optix = _signature(optix_payload)
    embree = _signature(embree_payload)
    int_fields = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    if any(optix[field] != embree[field] for field in int_fields):
        return False
    return abs(float(optix["sum_distance"]) - float(embree["sum_distance"])) <= max(
        1e-6,
        abs(float(embree["sum_distance"])) * 1e-9,
    )


def _tie_stable_signatures_match(
    optix_payload: dict[str, Any] | None,
    embree_payload: dict[str, Any] | None,
) -> bool:
    if optix_payload is None or embree_payload is None:
        return False
    optix = _signature(optix_payload)
    embree = _signature(embree_payload)
    int_fields = ("row_count", "bounded_neighbor_count", "nearest_id_checksum")
    if any(optix[field] != embree[field] for field in int_fields):
        return False
    return abs(float(optix["sum_distance"]) - float(embree["sum_distance"])) <= max(
        1e-6,
        abs(float(embree["sum_distance"])) * 1e-9,
    )


def _signature_delta(
    optix_payload: dict[str, Any] | None,
    embree_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    if optix_payload is None or embree_payload is None:
        return {}
    optix = _signature(optix_payload)
    embree = _signature(embree_payload)
    return {
        key: optix[key] - embree[key]
        for key in ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum", "sum_distance")
    }


def build_packet(
    *,
    source_root: str | Path | None = None,
    work_dir: str | Path = DEFAULT_WORK_DIR,
    target_handle: str = "kitti_1m",
    target_point_count: int | None = None,
    radius: float = 0.10,
    k_max: int = 50,
    query_batch_size: int = 65_536,
    optix_repeat: int = 20,
    embree_repeat: int = 3,
    run_live: bool = False,
) -> dict[str, Any]:
    resolved_source_root = _resolve_first_ready_source_root(source_root)
    work_dir = Path(work_dir)
    point_file = work_dir / f"{target_handle}_points.csv"
    export = None
    optix_result = None
    embree_result = None
    export_error = ""
    live_error = ""

    if resolved_source_root is not None:
        try:
            export = rt.write_kitti_paper_family_recipe_csv(
                point_file,
                target_handle=target_handle,
                source_root=resolved_source_root,
                target_point_count=target_point_count,
            )
        except Exception as exc:  # pragma: no cover - host data dependent
            export_error = repr(exc)

    if run_live and export is not None:
        try:
            optix_result = _run_rtdl_backend(
                backend="optix",
                point_file=point_file,
                radius=radius,
                k_max=k_max,
                query_batch_size=query_batch_size,
                repeat=optix_repeat,
            )
            embree_result = _run_rtdl_backend(
                backend="embree",
                point_file=point_file,
                radius=radius,
                k_max=k_max,
                query_batch_size=query_batch_size,
                repeat=embree_repeat,
            )
        except Exception as exc:  # pragma: no cover - hardware dependent
            live_error = repr(exc)

    optix_payload = None if optix_result is None else optix_result["payload"]
    embree_payload = None if embree_result is None else embree_result["payload"]
    both_ok = bool(
        optix_payload
        and embree_payload
        and optix_payload.get("ok")
        and embree_payload.get("ok")
    )
    speedup = None
    if both_ok:
        optix_median = float(optix_payload["elapsed_median_sec"])
        embree_median = float(embree_payload["elapsed_median_sec"])
        speedup = embree_median / optix_median if optix_median > 0 else None
    strict_signature_match = _signatures_match(optix_payload, embree_payload)
    tie_stable_signature_match = _tie_stable_signatures_match(optix_payload, embree_payload)

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4500 / V3 M104",
        "status": (
            "kitti_same_input_rtdl_optix_embree_live_strict"
            if both_ok and strict_signature_match
            else "kitti_same_input_rtdl_optix_embree_live_tie_caveat"
            if both_ok and tie_stable_signature_match
            else "kitti_same_input_csv_export_only"
            if export is not None
            else "kitti_same_input_source_not_ready"
        ),
        "date": "2026-06-17",
        "source_probe": {
            "candidate_roots": _source_root_candidates(source_root),
            "resolved_source_root": "" if resolved_source_root is None else str(resolved_source_root),
        },
        "input": {
            "target_handle": target_handle,
            "target_point_count_override": target_point_count,
            "csv_export": None if export is None else asdict(export),
            "csv_export_error": export_error,
            "query_equals_search": True,
            "point_file_committed": False,
        },
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "result_mode": "ranked-summary-aggregate",
            "exact": True,
            "precision": "float64",
            "radius": radius,
            "k_max": k_max,
            "query_batch_size": query_batch_size,
            "optix_repeat": optix_repeat,
            "embree_repeat": embree_repeat,
            "same_input_csv": export is not None,
            "backend_variable_only": both_ok,
        },
        "results": {
            "optix": optix_result,
            "embree": embree_result,
            "live_error": live_error,
            "strict_signature_match": strict_signature_match,
            "tie_stable_signature_match": tie_stable_signature_match,
            "signature_delta_optix_minus_embree": _signature_delta(optix_payload, embree_payload),
            "optix_over_embree_speedup": speedup,
        },
        "summary": {
            "source_ready": resolved_source_root is not None,
            "csv_export_ready": export is not None,
            "live_rtdl_pair_ready": both_ok,
            "strict_signature_match": strict_signature_match,
            "tie_stable_signature_match": tie_stable_signature_match,
            "optix_over_embree_speedup": speedup,
            "author_rtnn_included": False,
            "next_step": "build and run author RTNN on the same CSV input",
        },
        "claim_boundary": {
            "paper_family_dataset": True,
            "exact_paper_recipe": False,
            "same_input_rtdl_optix_embree_comparison": both_ok,
            "strict_output_signature_match": strict_signature_match,
            "tie_sensitive_kth_mismatch": both_ok and tie_stable_signature_match and not strict_signature_match,
            "author_rtnn_comparison": False,
            "paper_reproduction_wording_allowed": False,
            "public_speedup_claim_authorized": False,
        },
    }


def _write_report(packet: dict[str, Any]) -> None:
    export = packet["input"]["csv_export"]
    optix = packet["results"]["optix"]
    embree = packet["results"]["embree"]
    rows = [
        "| Backend | OK | Median Sec | Prepare Sec | Bounded Neighbors | Row Count |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, result in (("OptiX", optix), ("Embree", embree)):
        if result is None:
            rows.append(f"| {label} | no |  |  |  |  |")
            continue
        payload = result["payload"]
        signature = _signature(payload)
        rows.append(
            "| "
            f"{label} | {str(bool(payload.get('ok'))).lower()} | "
            f"{float(payload.get('elapsed_median_sec', 0.0)):.6f} | "
            f"{float(payload.get('execution_prepare_sec', 0.0)):.6f} | "
            f"{signature['bounded_neighbor_count']:,} | "
            f"{signature['row_count']:,} |"
        )

    speedup = packet["summary"]["optix_over_embree_speedup"]
    strict_signature_match = bool(packet["summary"]["strict_signature_match"])
    tie_stable_signature_match = bool(packet["summary"]["tie_stable_signature_match"])
    if speedup is None:
        conclusion = "M104 exported a same-input KITTI CSV, but did not complete the live RTDL OptiX/Embree pair."
    elif strict_signature_match:
        conclusion = (
            f"M104 runs RTDL OptiX and Embree on the same bounded KITTI CSV with matching "
            f"strict exact aggregate signatures; OptiX is {float(speedup):.2f}x faster by median query time."
        )
    elif tie_stable_signature_match:
        conclusion = (
            f"M104 runs RTDL OptiX and Embree on the same bounded KITTI CSV. Count, nearest-id "
            f"checksum, and distance-sum signatures match, but the tie-sensitive kth-id checksum "
            f"differs; OptiX is {float(speedup):.2f}x faster by median query time under this "
            f"bounded gate."
        )
    else:
        conclusion = (
            f"M104 runs RTDL OptiX and Embree on the same bounded KITTI CSV, but output "
            f"signatures do not match strongly enough for a same-contract claim."
        )

    export_line = "not exported" if export is None else (
        f"`{export['paper_label']}` with {int(export['point_count']):,} points at `{export['path']}`"
    )
    report = "\n".join(
        [
            "# Goal4500 / V3 M104 RTNN KITTI Same-Input RTDL Gate",
            "",
            "## Conclusion",
            "",
            conclusion,
            "",
            "The input is a bounded KITTI-family recipe, not an exact RTNN paper row. This packet only compares RTDL OptiX and RTDL Embree on the same CSV; author RTNN is the next gate.",
            "",
            "## Input",
            "",
            f"- Export: {export_line}",
            f"- Radius: `{packet['contract']['radius']}`",
            f"- K max: `{packet['contract']['k_max']}`",
            f"- Query/search contract: same CSV, ranked-summary aggregate, exact float64",
            "",
            "## RTDL Matrix",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- Same-input RTDL OptiX/Embree timing is valid only when both rows are `ok`; strict same-output wording additionally requires strict signature match.",
            "- A tie-sensitive kth-id checksum mismatch must be reported separately from count/nearest/distance agreement.",
            "- Author RTNN is not included in this packet.",
            "- Paper-reproduction and public speedup wording remain blocked.",
            "",
            "Artifacts:",
            "",
            f"- `{OUT_JSON.as_posix()}`",
        ]
    )
    OUT_REPORT.write_text(report + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)
    parser.add_argument("--target-handle", default="kitti_1m")
    parser.add_argument("--target-point-count", type=int, default=None)
    parser.add_argument("--radius", type=float, default=0.10)
    parser.add_argument("--k-max", type=int, default=50)
    parser.add_argument("--query-batch-size", type=int, default=65_536)
    parser.add_argument("--optix-repeat", type=int, default=20)
    parser.add_argument("--embree-repeat", type=int, default=3)
    parser.add_argument("--run-live", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(
        source_root=args.source_root,
        work_dir=args.work_dir,
        target_handle=args.target_handle,
        target_point_count=args.target_point_count,
        radius=args.radius,
        k_max=args.k_max,
        query_batch_size=args.query_batch_size,
        optix_repeat=args.optix_repeat,
        embree_repeat=args.embree_repeat,
        run_live=args.run_live,
    )
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    _write_report(packet)
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
