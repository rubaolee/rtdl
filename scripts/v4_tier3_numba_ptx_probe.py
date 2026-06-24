from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _custom_scalar_reduce(hit_distance, weight, state):
    return state + hit_distance * weight


def _configure_numba_legacy_nvvm_env(toolchain: dict[str, object]) -> dict[str, object]:
    configured: dict[str, object] = {
        "numba_legacy_nvvm_env_configured": False,
        "numba_legacy_libdevice_env_configured": False,
    }
    nvvm_lib_dir = toolchain.get("nvvm_lib_dir")
    if isinstance(nvvm_lib_dir, str):
        libnvvm = Path(nvvm_lib_dir) / ("nvvm64_40_0.dll" if os.name == "nt" else "libnvvm.so")
        if libnvvm.exists():
            os.environ.setdefault("NUMBAPRO_NVVM", str(libnvvm))
            configured["numba_legacy_nvvm_env_configured"] = True
            configured["numba_legacy_nvvm"] = os.environ.get("NUMBAPRO_NVVM")
    prefix = toolchain.get("numba_cuda_prefix")
    if isinstance(prefix, str):
        libdevice_dir = Path(prefix) / "nvvm" / "libdevice"
        if libdevice_dir.exists():
            os.environ.setdefault("NUMBAPRO_LIBDEVICE", str(libdevice_dir))
            configured["numba_legacy_libdevice_env_configured"] = True
            configured["numba_legacy_libdevice"] = os.environ.get("NUMBAPRO_LIBDEVICE")
    return configured


def _maybe_reexec_with_nvvm_ld_path(toolchain: dict[str, object]) -> dict[str, object]:
    if os.name == "nt":
        return {"reexec_supported": False, "reason": "windows"}
    nvvm_lib_dir = toolchain.get("nvvm_lib_dir")
    if not isinstance(nvvm_lib_dir, str) or not Path(nvvm_lib_dir).exists():
        return {"reexec_supported": True, "reexec_required": False, "reason": "nvvm_lib_dir_missing"}
    if os.environ.get("RTDL_V4_TIER3_NVVM_REEXEC") == "1":
        parts = [part for part in os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep) if part]
        return {
            "reexec_supported": True,
            "reexec_required": False,
            "reexeced": True,
            "nvvm_lib_dir_in_ld_library_path": nvvm_lib_dir in parts,
        }
    parts = [part for part in os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep) if part]
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = os.pathsep.join((nvvm_lib_dir, *parts)) if parts else nvvm_lib_dir
    env["RTDL_V4_TIER3_NVVM_REEXEC"] = "1"
    os.execvpe(sys.executable, [sys.executable, *sys.argv], env)
    raise RuntimeError("unreachable after exec")


def _run_probe(dry_run: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "rtdl.v4.tier3_numba_ptx_probe.v1",
        "status": "dry_run" if dry_run else "unknown",
        "probe": "numba_device_scalar_reduce_to_ptx",
        "tier": "tier3_spike_only_not_v4_0_release_surface",
        "ptx_generated": False,
        "optix_module_link_attempted": False,
        "optix_module_link_succeeded": None,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }
    if dry_run:
        payload["reason"] = "dry_run_does_not_import_numba_or_require_cuda"
        return payload

    try:
        from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment

        toolchain = configure_numba_cuda_toolchain_environment()
        payload["numba_toolchain_environment"] = toolchain
        payload["numba_nvvm_reexec_environment"] = _maybe_reexec_with_nvvm_ld_path(toolchain)
        payload["numba_legacy_nvvm_environment"] = _configure_numba_legacy_nvvm_env(toolchain)
        from numba import cuda, types
    except Exception as exc:
        payload.update(
            {
                "status": "blocked",
                "blocked_stage": "import_or_toolchain",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        return payload

    try:
        payload["cuda_available"] = bool(cuda.is_available())
    except Exception as exc:
        payload.update(
            {
                "status": "blocked",
                "blocked_stage": "cuda_availability",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        return payload

    try:
        ptx, return_type = cuda.compile_ptx(
            _custom_scalar_reduce,
            (types.float64, types.float64, types.float64),
            device=True,
            fastmath=False,
        )
        payload.update(
            {
                "status": "ptx_generated",
                "ptx_generated": True,
                "ptx_length": len(ptx),
                "return_type": str(return_type),
                "contains_func_directive": ".func" in ptx,
                "contains_visible_func_directive": ".visible .func" in ptx,
                "contains_callback_name": "_custom_scalar_reduce" in ptx,
                "ptx_header": "\n".join(ptx.splitlines()[:8]),
                "next_stage": "build_a_hole_left_optix_shell_and_attempt_module_link",
            }
        )
    except Exception as exc:
        payload.update(
            {
                "status": "blocked",
                "blocked_stage": "numba_compile_ptx",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
    return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Tier-3 Numba PTX Probe",
        "",
        "Status: generated spike evidence, not Tier-3 support and not a release authorization",
        "",
        f"- status: `{payload['status']}`",
        f"- PTX generated: `{payload['ptx_generated']}`",
        f"- OptiX module link attempted: `{payload['optix_module_link_attempted']}`",
        "",
        "## Boundary",
        "",
        "This probe only checks whether a scalar Numba device callback can produce PTX. It does not prove OptiX module linking, callable overhead, correctness inside traversal, or public Tier-3 support.",
        "",
        "## Non-Authorization",
        "",
        "This probe does not authorize V4 release, Tier-3 callback/PTX support claims, raw OptiX callbacks, broad speedup wording, or app-specific native kernels.",
        "",
    ]
    if payload.get("status") == "blocked":
        lines.extend(
            [
                "## Blocked Stage",
                "",
                f"- blocked stage: `{payload.get('blocked_stage')}`",
                f"- error type: `{payload.get('error_type')}`",
                f"- error: `{payload.get('error')}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe V4 Tier-3 Numba device callback PTX generation.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    payload = _run_probe(bool(args.dry_run))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"dry_run", "ptx_generated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
