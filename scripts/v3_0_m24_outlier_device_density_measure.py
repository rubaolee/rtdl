from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M24 outlier device-density bridge evidence.")
    parser.add_argument("--copies", type=int, default=8192)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--numba-cuda-home",
        type=Path,
        default=Path(os.environ["RTDL_NUMBA_CUDA_HOME"]) if os.environ.get("RTDL_NUMBA_CUDA_HOME") else None,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4421_v3_0_m24_outlier_device_density_evidence.json"),
    )
    args = parser.parse_args()

    numba_cuda_home = _apply_numba_cuda_home(args.numba_cuda_home)

    from examples.current.apps.ml import rtdl_outlier_detection_app as app

    rows = []
    for partner in ("cupy", "numba"):
        row = app.run_app(
            "optix_device_density",
            copies=args.copies,
            output_mode="density_summary",
            partner=partner,
            query_repeat=args.repeats,
            warmup=args.warmups,
        )
        rows.append(_compact_app_row(row))

    outlier_counts = {int(row["outlier_count"]) for row in rows}
    inlier_counts = {int(row["inlier_count"]) for row in rows}
    payload = {
        "version": "rtdl.v3_0.outlier_device_density.m24",
        "status": "m24_outlier_app_uses_generic_optix_prepared_fixed_radius_device_columns_internal_claims_gated",
        "parameters": {
            "copies": args.copies,
            "point_count": args.copies * 8,
            "radius": app.RADIUS,
            "min_neighbors_including_self": app.MIN_NEIGHBORS_INCLUDING_SELF,
            "warmups": args.warmups,
            "repeats": args.repeats,
            "partners": ("cupy", "numba"),
            "hardware": args.hardware or _hardware_label(),
        },
        "rows": tuple(rows),
        "comparison": {
            "partner_count": len(rows),
            "all_match_oracle": all(row["matches_oracle"] is True for row in rows),
            "outlier_counts_match": len(outlier_counts) == 1,
            "inlier_counts_match": len(inlier_counts) == 1,
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
        raise RuntimeError("M24 outlier device-density bridge failed oracle parity")
    if not payload["comparison"]["outlier_counts_match"]:
        raise RuntimeError("M24 outlier device-density bridge partner outlier counts differ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _compact_app_row(row: dict[str, object]) -> dict[str, object]:
    metadata = dict(row.get("partner_metadata") or {})
    point_count = int(row["point_count"])
    outlier_count = int(row["outlier_count"])
    compact = {
        "app": row["app"],
        "backend": row["backend"],
        "partner": row["partner"],
        "point_count": point_count,
        "copies": row["copies"],
        "radius": row["radius"],
        "min_neighbors_including_self": row["min_neighbors_including_self"],
        "density_row_count": len(row.get("density_rows", ())),
        "native_summary_row_count": row["native_summary_row_count"],
        "outlier_count": outlier_count,
        "inlier_count": point_count - outlier_count,
        "oracle_outlier_count": row["oracle_outlier_count"],
        "matches_oracle": row["matches_oracle"],
        "native_continuation_active": row["native_continuation_active"],
        "native_continuation_backend": row["native_continuation_backend"],
        "partner_reference_contract": row["partner_reference_contract"],
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "hot_device_density_elapsed_sec_median": metadata.get("hot_device_density_elapsed_sec_median"),
        "post_window_row_materialization_sec": metadata.get("post_window_row_materialization_sec"),
        "prepare_sec": metadata.get("prepare_sec"),
        "input_column_build_sec": metadata.get("input_column_build_sec"),
        "prepared_query_repeat_protocol": metadata.get("prepared_query_repeat_protocol"),
        "device_result_materialization_after_hot_window": metadata.get(
            "device_result_materialization_after_hot_window"
        ),
        "materializes_neighbor_rows": metadata.get("materializes_neighbor_rows"),
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
