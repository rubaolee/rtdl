from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M23 DBSCAN component-label bridge evidence.")
    parser.add_argument("--copies", type=int, default=8192)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--grouped-union-query-block-size", type=int, default=None)
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--numba-cuda-home",
        type=Path,
        default=Path(os.environ["RTDL_NUMBA_CUDA_HOME"]) if os.environ.get("RTDL_NUMBA_CUDA_HOME") else None,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4420_v3_0_m23_dbscan_component_bridge_evidence.json"),
    )
    args = parser.parse_args()

    numba_cuda_home = _apply_numba_cuda_home(args.numba_cuda_home)

    from examples.current.apps.ml import rtdl_dbscan_clustering_app as app

    rows = []
    for partner in ("cupy", "numba"):
        row = app.run_app(
            "optix_grouped_stream_components",
            copies=args.copies,
            partner=partner,
            query_repeat=args.repeats,
            warmup=args.warmups,
            grouped_union_query_block_size=args.grouped_union_query_block_size,
        )
        rows.append(_compact_app_row(row))

    cluster_signatures = {json.dumps(row["cluster_size_signature"], sort_keys=True) for row in rows}
    noise_counts = {int(row["noise_count"]) for row in rows}
    core_counts = {int(row["core_count"]) for row in rows}
    payload = {
        "version": "rtdl.v3_0.dbscan_component_bridge.m23",
        "status": "m23_dbscan_app_uses_generic_optix_grouped_stream_component_front_door_internal_claims_gated",
        "parameters": {
            "copies": args.copies,
            "point_count": args.copies * 8,
            "epsilon": app.EPSILON,
            "min_points": app.MIN_POINTS,
            "warmups": args.warmups,
            "repeats": args.repeats,
            "partners": ("cupy", "numba"),
            "grouped_union_query_block_size": args.grouped_union_query_block_size,
            "hardware": args.hardware or _hardware_label(),
        },
        "rows": tuple(rows),
        "comparison": {
            "partner_count": len(rows),
            "all_match_oracle": all(row["matches_oracle"] is True for row in rows),
            "cluster_size_signatures_match": len(cluster_signatures) == 1,
            "noise_counts_match": len(noise_counts) == 1,
            "core_counts_match": len(core_counts) == 1,
            "rt_core_accelerated": all(bool(row["rt_core_accelerated"]) for row in rows),
            "native_continuation_active": all(bool(row["native_continuation_active"]) for row in rows),
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "runner_numba_cuda_home": numba_cuda_home,
    }
    if not payload["comparison"]["all_match_oracle"]:
        raise RuntimeError("M23 DBSCAN grouped-stream bridge failed oracle parity")
    if not payload["comparison"]["cluster_size_signatures_match"]:
        raise RuntimeError("M23 DBSCAN grouped-stream bridge partner cluster-size signatures differ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _compact_app_row(row: dict[str, object]) -> dict[str, object]:
    metadata = dict(row.get("partner_metadata") or {})
    compact = {
        "app": row["app"],
        "backend": row["backend"],
        "partner": row["partner"],
        "point_count": row["point_count"],
        "copies": row["copies"],
        "epsilon": row["epsilon"],
        "min_points": row["min_points"],
        "cluster_size_signature": _cluster_size_signature(row["cluster_sizes"]),
        "noise_count": len(row.get("noise_point_ids", ())),
        "core_count": row["core_count"],
        "cluster_row_count": len(row.get("cluster_rows", ())),
        "oracle_cluster_row_count": len(row.get("oracle_cluster_rows", ())),
        "matches_oracle": row["matches_oracle"],
        "native_continuation_active": row["native_continuation_active"],
        "native_continuation_backend": row["native_continuation_backend"],
        "partner_reference_contract": row["partner_reference_contract"],
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "hot_component_label_elapsed_sec_median": metadata.get("hot_component_label_elapsed_sec_median"),
        "post_window_row_materialization_sec": metadata.get("post_window_row_materialization_sec"),
        "prepare_sec": metadata.get("prepare_sec"),
        "prepared_query_repeat_protocol": metadata.get("prepared_query_repeat_protocol"),
        "device_result_materialization_after_hot_window": metadata.get(
            "device_result_materialization_after_hot_window"
        ),
        "materializes_neighbor_rows": metadata.get("materializes_neighbor_rows"),
        "materializes_directed_adjacency_stream": metadata.get("materializes_directed_adjacency_stream"),
        "materializes_python_rows": metadata.get("materializes_python_rows"),
        "app_specific_native_engine_logic_allowed": metadata.get("app_specific_native_engine_logic_allowed"),
        "automatic_partner_selection_authorized": metadata.get("automatic_partner_selection_authorized"),
        "public_speedup_claim_authorized": metadata.get("public_speedup_claim_authorized"),
        "rt_core_speedup_claim_authorized": metadata.get("rt_core_speedup_claim_authorized"),
        "whole_app_speedup_claim_authorized": metadata.get("whole_app_speedup_claim_authorized"),
        "true_zero_copy_claim_authorized": metadata.get("true_zero_copy_claim_authorized"),
        "native_execution_path": metadata.get("native_execution_path"),
        "native_engine_summary_contract": metadata.get("native_engine_summary_contract"),
    }
    return compact


def _cluster_size_signature(cluster_sizes: object) -> dict[str, object]:
    if not isinstance(cluster_sizes, dict):
        raise TypeError("cluster_sizes must be a dictionary")
    histogram: dict[str, int] = {}
    cluster_count = 0
    clustered_point_count = 0
    min_size: int | None = None
    max_size: int | None = None
    for value in cluster_sizes.values():
        size = int(value)
        cluster_count += 1
        clustered_point_count += size
        min_size = size if min_size is None else min(min_size, size)
        max_size = size if max_size is None else max(max_size, size)
        key = str(size)
        histogram[key] = histogram.get(key, 0) + 1
    return {
        "cluster_count": cluster_count,
        "clustered_point_count": clustered_point_count,
        "size_histogram": dict(sorted(histogram.items(), key=lambda item: int(item[0]))),
        "min_size": min_size,
        "max_size": max_size,
    }


def _apply_numba_cuda_home(cuda_home: Path | None) -> dict[str, object]:
    if cuda_home is None:
        return {
            "configured": False,
            "reason": "not_requested",
            "cuda_home": os.environ.get("CUDA_HOME"),
            "cuda_path": os.environ.get("CUDA_PATH"),
        }
    home = cuda_home.resolve()
    nvvm_dir = home / "nvvm" / "lib64"
    bin_dir = home / "bin"
    if not (nvvm_dir / "libnvvm.so").exists() and not any(nvvm_dir.glob("libnvvm.so*")):
        raise FileNotFoundError(f"Numba CUDA home is missing NVVM library under {nvvm_dir}")
    if not (home / "nvvm" / "libdevice" / "libdevice.10.bc").exists():
        raise FileNotFoundError(f"Numba CUDA home is missing libdevice.10.bc under {home / 'nvvm/libdevice'}")
    os.environ["CUDA_HOME"] = str(home)
    os.environ["CUDA_PATH"] = str(home)
    os.environ["PATH"] = os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")])
    os.environ["LD_LIBRARY_PATH"] = os.pathsep.join([str(nvvm_dir), os.environ.get("LD_LIBRARY_PATH", "")])
    return {
        "configured": True,
        "cuda_home": str(home),
        "nvvm_dir": str(nvvm_dir),
        "bin_dir": str(bin_dir),
        "ptxas_version": _run_text([str(bin_dir / "ptxas"), "--version"]),
    }


def _hardware_label() -> str:
    gpu = _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,pci.bus_id",
            "--format=csv,noheader",
        ]
    ).strip()
    if gpu:
        return gpu.splitlines()[0]
    return f"{platform.platform()} / {platform.processor() or platform.machine()}"


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


if __name__ == "__main__":
    raise SystemExit(main())
