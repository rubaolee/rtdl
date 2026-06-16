from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M26 facility exact top-k partner dual-path evidence."
    )
    parser.add_argument("--copies", type=int, default=2048)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--partners", default="cupy,numba")
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--numba-cuda-home",
        type=Path,
        default=Path(os.environ["RTDL_NUMBA_CUDA_HOME"]) if os.environ.get("RTDL_NUMBA_CUDA_HOME") else None,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4423_v3_0_m26_facility_partner_dual_evidence.json"),
    )
    args = parser.parse_args()

    if args.copies < 1:
        raise ValueError("--copies must be at least 1")
    if args.warmups < 0:
        raise ValueError("--warmups must be non-negative")
    if args.repeats < 1:
        raise ValueError("--repeats must be at least 1")

    partners = tuple(partner.strip() for partner in args.partners.split(",") if partner.strip())
    if not partners:
        raise ValueError("--partners must include at least one partner")
    unsupported = sorted(set(partners) - {"cupy", "numba", "torch"})
    if unsupported:
        raise ValueError(f"unsupported partner(s): {', '.join(unsupported)}")

    numba_cuda_home = _apply_numba_cuda_home(args.numba_cuda_home)

    from examples.current.apps.geospatial import rtdl_facility_knn_assignment as app

    rows = []
    for partner in partners:
        rows.append(
            _measure_partner(
                app=app,
                partner=partner,
                copies=args.copies,
                warmups=args.warmups,
                repeats=args.repeats,
            )
        )

    signatures = {json.dumps(row["signature"], sort_keys=True) for row in rows}
    payload = {
        "version": "rtdl.v3_0.facility_partner_dual.m26",
        "status": "m26_facility_exact_topk_exposes_best_and_no_cpp_partner_paths",
        "parameters": {
            "copies": args.copies,
            "customer_count": args.copies * 4,
            "depot_count": args.copies * 4,
            "logical_pair_count": (args.copies * 4) * (args.copies * 4),
            "k": 1,
            "output_mode": "summary",
            "warmups": args.warmups,
            "repeats": args.repeats,
            "partners": partners,
            "hardware": args.hardware or _hardware_label(),
        },
        "rows": tuple(rows),
        "comparison": {
            "partner_count": len(rows),
            "signature_match": len(signatures) == 1,
            "best_observed_partner_by_full_app_median": min(
                rows,
                key=lambda row: float(row["full_app_wall_seconds_median"]),
            )["partner"],
            "rt_core_accelerated": False,
            "native_engine_customization": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
        "claim_boundary": {
            "exact_partner_reference_path": True,
            "best_partner_and_numba_reference_exposed": {"cupy", "numba"}.issubset(set(partners)),
            "required_dual_partners": ("cupy", "numba"),
            "native_engine_customization": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "runner_numba_cuda_home": numba_cuda_home,
    }
    if not payload["comparison"]["signature_match"]:
        raise RuntimeError("facility partner exact top-k signatures differ across partners")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": payload["comparison"], "rows": rows}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _measure_partner(*, app, partner: str, copies: int, warmups: int, repeats: int) -> dict[str, object]:
    for _ in range(warmups):
        app.run_case("partner_exact", copies=copies, output_mode="summary", partner=partner)
    timings: list[float] = []
    payloads: list[dict[str, object]] = []
    for _ in range(repeats):
        start = time.perf_counter()
        payload = app.run_case("partner_exact", copies=copies, output_mode="summary", partner=partner)
        timings.append(time.perf_counter() - start)
        payloads.append(payload)

    payload = payloads[-1]
    metadata = dict(payload.get("partner_metadata") or {})
    return {
        "partner": partner,
        "full_app_wall_seconds": timings,
        "full_app_wall_seconds_median": _median(timings),
        "full_app_wall_seconds_min": min(timings),
        "full_app_wall_seconds_max": max(timings),
        "customer_count": payload["customer_count"],
        "depot_count": payload["depot_count"],
        "row_count": payload["row_count"],
        "partner_reference_contract": payload["partner_reference_contract"],
        "metadata_partner": metadata.get("partner"),
        "metadata_adapter": metadata.get("adapter"),
        "metadata_v2_5_partner_continuation_operation": metadata.get("v2_5_partner_continuation_operation"),
        "metadata_numba_status": metadata.get("v2_11_numba_preview_kernel_status"),
        "metadata_numba_device_rank_used": metadata.get("numba_grouped_topk_device_rank_used"),
        "metadata_numba_score_row_count": metadata.get("numba_score_row_count"),
        "metadata_host_rank_materialization_used": metadata.get("host_rank_materialization_used"),
        "rt_core_accelerated": payload["rt_core_accelerated"],
        "native_continuation_active": payload["native_continuation_active"],
        "signature": _signature(payload),
    }


def _signature(payload: dict[str, object]) -> dict[str, int]:
    primary_depot_load = {
        int(depot_id): int(load) for depot_id, load in dict(payload["primary_depot_load"]).items()
    }
    return {
        "row_count": int(payload["row_count"]),
        "assigned_customer_count": sum(primary_depot_load.values()),
        "depot_load_key_count": len(primary_depot_load),
        "depot_load_checksum": sum(depot_id * load for depot_id, load in primary_depot_load.items()),
        "depot_load_weighted_checksum": sum(
            (index + 1) * depot_id * load
            for index, (depot_id, load) in enumerate(sorted(primary_depot_load.items()))
        ),
    }


def _median(values: list[float]) -> float:
    ordered = sorted(float(value) for value in values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


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
