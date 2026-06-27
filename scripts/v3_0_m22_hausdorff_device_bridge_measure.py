from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M22 Hausdorff app device-bridge evidence.")
    parser.add_argument("--copies", type=int, default=16_384)
    parser.add_argument("--radius", type=float, default=0.4)
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
        default=Path("build/goal4419_v3_0_m22_hausdorff_device_bridge_evidence.json"),
    )
    args = parser.parse_args()

    numba_cuda_home = _apply_numba_cuda_home(args.numba_cuda_home)

    from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_distance_app as app

    rows = []
    for partner in ("cupy", "numba"):
        rows.append(
            app.run_app(
                "optix_device_max_nearest",
                copies=args.copies,
                partner=partner,
                hausdorff_threshold=args.radius,
                query_repeat=args.repeats,
                warmup=args.warmups,
                require_rt_core=True,
            )
        )
    distances = {round(float(row["hausdorff_distance"]), 9) for row in rows}
    payload = {
        "version": "rtdl.v3_0.hausdorff_device_bridge.m22",
        "status": "m22_hausdorff_app_uses_m21_device_query_bridge_internal_claims_gated",
        "parameters": {
            "copies": args.copies,
            "point_count_per_set": args.copies * 4,
            "radius": args.radius,
            "warmups": args.warmups,
            "repeats": args.repeats,
            "partners": ("cupy", "numba"),
            "hardware": args.hardware or _hardware_label(),
        },
        "rows": tuple(rows),
        "comparison": {
            "partner_count": len(rows),
            "all_match_oracle": all(bool(row["matches_oracle"]) for row in rows),
            "distance_match": len(distances) == 1,
            "rt_core_accelerated": all(bool(row["rt_core_accelerated"]) for row in rows),
            "native_continuation_active": all(bool(row["native_continuation_active"]) for row in rows),
            "device_result_materialization_after_hot_window": all(
                bool(row["directed_a_to_b"]["device_result_materialization_after_hot_window"])
                and bool(row["directed_b_to_a"]["device_result_materialization_after_hot_window"])
                for row in rows
            ),
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "paper_or_author_parity_claim_authorized": False,
        },
        "runner_numba_cuda_home": numba_cuda_home,
    }
    if not payload["comparison"]["all_match_oracle"]:
        raise RuntimeError("M22 Hausdorff device bridge failed oracle parity")
    if not payload["comparison"]["distance_match"]:
        raise RuntimeError("M22 Hausdorff device bridge partner distances differ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


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
