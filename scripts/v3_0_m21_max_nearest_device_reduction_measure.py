from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COUNTER_SOURCE = ROOT / "src/native/tools/rtdl_cuda_transfer_counter.c"
DEFAULT_COUNTER_LIBRARY = ROOT / "build/librtdl_cuda_transfer_counter.so"


def _ensure_transfer_counter_preloaded(library: Path, source: Path) -> dict[str, object]:
    library = library.resolve()
    source = source.resolve()
    preload = os.environ.get("LD_PRELOAD", "")
    preload_parts = [part for part in preload.split(os.pathsep) if part]
    already_preloaded = str(library) in preload_parts
    os.environ["RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"] = str(library)
    build = {
        "skipped": True,
        "reason": "already_preloaded",
        "library_exists": library.exists(),
    }
    if not already_preloaded:
        build = _build_transfer_counter(library, source)
        os.environ["LD_PRELOAD"] = os.pathsep.join([str(library), *preload_parts])
        os.environ["RTDL_CUDA_TRANSFER_COUNTER_REEXEC"] = "1"
        os.execvpe(sys.executable, [sys.executable, *sys.argv], os.environ.copy())
    return {
        "library": str(library),
        "source": str(source),
        "already_preloaded": already_preloaded,
        "build": build,
        "ld_preload": os.environ.get("LD_PRELOAD", ""),
    }


def _build_transfer_counter(library: Path, source: Path) -> dict[str, object]:
    if not source.exists():
        raise FileNotFoundError(f"transfer counter source not found: {source}")
    library.parent.mkdir(parents=True, exist_ok=True)
    command = [
        os.environ.get("CC", "cc"),
        "-shared",
        "-fPIC",
        "-O2",
        "-std=c11",
        str(source),
        "-ldl",
        "-o",
        str(library),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "failed to build CUDA transfer counter:\n"
            + (completed.stdout or "")
            + (completed.stderr or "")
        )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


_TRANSFER_COUNTER_BOOTSTRAP = _ensure_transfer_counter_preloaded(
    Path(os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_LIBRARY", DEFAULT_COUNTER_LIBRARY)),
    Path(os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_SOURCE", DEFAULT_COUNTER_SOURCE)),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M21 max-nearest device-reduction evidence.")
    parser.add_argument("--point-count", type=int, default=65_536)
    parser.add_argument("--group-axis", type=int, default=64)
    parser.add_argument("--radius", type=float, default=0.025)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--numba-cuda-home",
        type=Path,
        default=Path(os.environ["RTDL_NUMBA_CUDA_HOME"]) if os.environ.get("RTDL_NUMBA_CUDA_HOME") else None,
        help=(
            "Optional CUDA toolkit home for Numba NVVM/ptxas. Use this to match Numba's PTX "
            "emission to the installed driver, e.g. CUDA 12.4 for driver 550."
        ),
    )
    parser.add_argument(
        "--transfer-counter-library",
        type=Path,
        default=Path(os.environ["RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"]),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4418_v3_0_m21_max_nearest_device_reduction_evidence.json"),
    )
    args = parser.parse_args()

    numba_cuda_home = _apply_numba_cuda_home(args.numba_cuda_home)

    import rtdsl as rt

    payload = rt.run_v3_m21_max_nearest_device_reduction_case(
        transfer_counter_library=args.transfer_counter_library,
        point_count=args.point_count,
        group_axis=args.group_axis,
        radius=args.radius,
        warmups=args.warmups,
        repeats=args.repeats,
        hardware=args.hardware or _hardware_label(),
    )
    validation = rt.validate_v3_m21_max_nearest_device_reduction_payload(payload)
    payload["runner_transfer_counter_bootstrap"] = dict(_TRANSFER_COUNTER_BOOTSTRAP)
    payload["runner_numba_cuda_home"] = numba_cuda_home
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"validation": validation, "comparison": payload["comparison"]}, indent=2, sort_keys=True))
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
