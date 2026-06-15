from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import subprocess
from pathlib import Path

_NUMBA_CUDA_COMPAT_ENV = None


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
    os.environ.setdefault("NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY", "1")
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


_NUMBA_CUDA_COMPAT_ENV = _apply_numba_cuda_compat_env_before_rtdsl_import()

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V3.0 M9 OptiX grouped-stream partner evidence.")
    parser.add_argument("--point-count", type=int, default=2048)
    parser.add_argument("--radius", type=float, default=1.01)
    parser.add_argument("--component-threshold", type=int, default=1)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--query-block-size", type=int, default=None)
    parser.add_argument("--direct-side-effect", action="store_true")
    parser.add_argument("--hardware", default=None)
    parser.add_argument("--output", type=Path, default=Path("build/goal4403_v3_0_m9_grouped_stream_partner.json"))
    args = parser.parse_args()

    payload = rt.run_v3_m9_grouped_stream_partner_case(
        point_count=args.point_count,
        radius=args.radius,
        component_threshold=args.component_threshold,
        warmups=args.warmups,
        repeats=args.repeats,
        hardware=args.hardware or _hardware_label(),
        grouped_union_query_block_size=args.query_block_size,
        grouped_union_direct_side_effect=args.direct_side_effect,
    )
    validation = rt.validate_v3_m9_grouped_stream_payload(payload)
    payload["runner_numba_cuda_compat_env"] = dict(_NUMBA_CUDA_COMPAT_ENV or {})
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
