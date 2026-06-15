from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COUNTER_SOURCE = ROOT / "src/native/tools/rtdl_cuda_transfer_counter.c"
DEFAULT_COUNTER_LIBRARY = ROOT / "build/librtdl_cuda_transfer_counter.so"

_NUMBA_CUDA_COMPAT_ENV = None


def _ensure_transfer_counter_preloaded(library: Path, source: Path) -> dict[str, object]:
    library = library.resolve()
    source = source.resolve()
    build = _build_transfer_counter(library, source)
    preload = os.environ.get("LD_PRELOAD", "")
    preload_parts = [part for part in preload.split(os.pathsep) if part]
    already_preloaded = str(library) in preload_parts
    os.environ["RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"] = str(library)
    if not already_preloaded:
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
    compiler = os.environ.get("CC", "cc")
    command = [
        compiler,
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


def _apply_numba_cuda_compat_env_before_rtdsl_import() -> dict[str, object]:
    if os.environ.get("RTDL_DISABLE_NUMBA_CUDA_COMPAT") == "1":
        return {"applied": False, "reason": "disabled_by_env"}
    root = _find_packaged_cuda_nvcc_root()
    if root is None:
        return {"applied": False, "reason": "packaged_cuda_nvcc_not_found"}
    nvvm_dir = root / "nvvm" / "lib64"
    bin_dir = root / "bin"
    if not (nvvm_dir / "libnvvm.so").exists():
        return {"applied": False, "reason": "packaged_libnvvm_not_found", "root": str(root)}
    _prepend_env_path("LD_LIBRARY_PATH", str(nvvm_dir))
    if bin_dir.exists():
        _prepend_env_path("PATH", str(bin_dir))
    os.environ["CUDA_HOME"] = str(root)
    os.environ["NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY"] = "0"
    return {
        "applied": True,
        "cuda_home": str(root),
        "ld_library_path_prefix": str(nvvm_dir),
        "path_prefix": str(bin_dir) if bin_dir.exists() else None,
    }


def _find_packaged_cuda_nvcc_root() -> Path | None:
    spec = importlib.util.find_spec("nvidia.cuda_nvcc")
    locations = getattr(spec, "submodule_search_locations", None) if spec is not None else None
    if locations:
        candidate = Path(tuple(locations)[0])
        if (candidate / "nvvm" / "lib64" / "libnvvm.so").exists():
            return candidate
    fallback = Path("/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc")
    if (fallback / "nvvm" / "lib64" / "libnvvm.so").exists():
        return fallback
    return None


def _prepend_env_path(name: str, value: str) -> None:
    current = os.environ.get(name, "")
    parts = [part for part in current.split(os.pathsep) if part]
    if value in parts:
        parts.remove(value)
    os.environ[name] = os.pathsep.join([value, *parts])


_TRANSFER_COUNTER_BOOTSTRAP = _ensure_transfer_counter_preloaded(
    Path(os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_LIBRARY", DEFAULT_COUNTER_LIBRARY)),
    Path(os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_SOURCE", DEFAULT_COUNTER_SOURCE)),
)

_NUMBA_CUDA_COMPAT_ENV = _apply_numba_cuda_compat_env_before_rtdsl_import()
if _NUMBA_CUDA_COMPAT_ENV.get("applied") and os.environ.get("RTDL_NUMBA_CUDA_COMPAT_REEXEC") != "1":
    os.environ["RTDL_NUMBA_CUDA_COMPAT_REEXEC"] = "1"
    os.execvpe(sys.executable, [sys.executable, *sys.argv], os.environ.copy())
if _NUMBA_CUDA_COMPAT_ENV.get("applied"):
    try:
        from numba import cuda

        cuda.get_current_device()
        _NUMBA_CUDA_COMPAT_ENV["numba_preinitialized"] = True
    except Exception as exc:  # pragma: no cover - pod diagnostic path.
        _NUMBA_CUDA_COMPAT_ENV["numba_preinitialized"] = False
        _NUMBA_CUDA_COMPAT_ENV["numba_preinit_error"] = repr(exc)

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M11 no-hidden-copy transfer-counter evidence.")
    parser.add_argument("--point-count", type=int, default=65536)
    parser.add_argument("--radius", type=float, default=1.01)
    parser.add_argument("--component-threshold", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--direct-side-effect", action="store_true")
    parser.add_argument("--hardware", default=None)
    parser.add_argument("--transfer-counter-library", type=Path, default=Path(os.environ["RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"]))
    parser.add_argument("--output", type=Path, default=Path("build/goal4407_v3_0_m11_no_hidden_copy_evidence.json"))
    args = parser.parse_args()

    payload = rt.run_v3_m11_no_hidden_copy_evidence_case(
        transfer_counter_library=args.transfer_counter_library,
        point_count=args.point_count,
        radius=args.radius,
        component_threshold=args.component_threshold,
        warmups=args.warmups,
        repeats=args.repeats,
        hardware=args.hardware or _hardware_label(),
        grouped_union_direct_side_effect=args.direct_side_effect,
    )
    validation = rt.validate_v3_m11_no_hidden_copy_payload(payload)
    payload["runner_numba_cuda_compat_env"] = dict(_NUMBA_CUDA_COMPAT_ENV or {})
    payload["runner_transfer_counter_bootstrap"] = dict(_TRANSFER_COUNTER_BOOTSTRAP)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"validation": validation, "comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


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
