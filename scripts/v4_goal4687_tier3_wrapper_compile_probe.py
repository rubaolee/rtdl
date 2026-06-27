from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import extract_numba_callback_symbol_from_ptx
from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import specialize_semantic_wrapper_source
from rtdsl.v4_goal4687_tier3_wrapper_compile_probe import validate_v4_goal4687_tier3_wrapper_compile_probe_contract


PTX_PROBE = ROOT / "scripts" / "v4_tier3_numba_ptx_probe.py"


def _base_payload(dry_run: bool) -> dict[str, Any]:
    return {
        "schema": "rtdl.v4.goal4687_tier3_wrapper_compile_probe.v1",
        "status": "dry_run" if dry_run else "unknown",
        "dry_run": dry_run,
        "numba_ptx_generated": False,
        "symbol_probe": None,
        "wrapper_source_generated": False,
        "wrapper_compile_attempted": False,
        "wrapper_compile_succeeded": None,
        "optix_module_link_attempted": False,
        "pipeline_launch_attempted": False,
        "pod_authorized": False,
        "tier3_public_support_authorized": False,
        "raw_optix_callback_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "app_identity_kernel_authorized": False,
    }


def _first_existing_path(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def _find_optix_include() -> Path | None:
    env = os.environ.get("RTDL_OPTIX_INCLUDE_DIR") or os.environ.get("OPTIX_INCLUDE_DIR")
    if env:
        path = Path(env)
        if (path / "optix.h").exists() and (path / "optix_device.h").exists():
            return path
    return _first_existing_path(
        [
            Path("/root/vendor/optix-dev/include"),
            Path("/usr/local/optix/include"),
            Path("/opt/optix/include"),
        ]
    )


def _find_nvcc() -> str | None:
    for name in (
        os.environ.get("RTDL_NVCC"),
        os.environ.get("NVCC"),
        "/usr/local/cuda/bin/nvcc",
        "/usr/local/cuda-12/bin/nvcc",
        "nvcc",
    ):
        if name and shutil.which(name):
            return str(shutil.which(name))
        if name and Path(name).exists():
            return str(Path(name))
    return None


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_probe(dry_run: bool) -> dict[str, Any]:
    payload = _base_payload(dry_run)
    contract = validate_v4_goal4687_tier3_wrapper_compile_probe_contract()
    payload["contract_validation"] = contract
    if dry_run:
        payload["status"] = "dry_run_contract_passed" if contract["status"] == "passed" else "dry_run_contract_failed"
        return payload

    optix_include = _find_optix_include()
    nvcc = _find_nvcc()
    payload["toolchain"] = {
        "optix_include": str(optix_include) if optix_include else None,
        "nvcc": nvcc,
    }
    missing = [name for name, value in {"optix_include": optix_include, "nvcc": nvcc}.items() if value is None]
    if missing:
        payload.update({"status": "blocked", "blocked_stage": "toolchain_discovery", "missing": missing})
        return payload

    with tempfile.TemporaryDirectory(prefix="rtdl-v4-goal4687-tier3-wrapper-") as tmp:
        tmp_path = Path(tmp)
        callback_ptx = tmp_path / "callback.ptx"
        ptx_json = tmp_path / "callback.json"
        ptx_proc = _run(
            [
                sys.executable,
                str(PTX_PROBE),
                "--json-out",
                str(ptx_json),
                "--ptx-out",
                str(callback_ptx),
            ],
            cwd=ROOT,
        )
        payload["ptx_probe"] = {
            "returncode": ptx_proc.returncode,
            "stdout": ptx_proc.stdout.strip()[:4000],
            "stderr": ptx_proc.stderr.strip()[:4000],
        }
        if ptx_json.exists():
            payload["ptx_probe_payload"] = json.loads(ptx_json.read_text(encoding="utf-8"))
        if ptx_proc.returncode != 0 or not callback_ptx.exists():
            payload.update({"status": "blocked", "blocked_stage": "numba_ptx_generation"})
            return payload
        payload["numba_ptx_generated"] = True
        ptx_text = callback_ptx.read_text(encoding="utf-8")
        symbol_probe = extract_numba_callback_symbol_from_ptx(ptx_text)
        payload["symbol_probe"] = symbol_probe.as_dict()
        if symbol_probe.status != "symbol_extracted" or not symbol_probe.symbol:
            payload.update({"status": "blocked", "blocked_stage": "callback_symbol_extraction"})
            return payload
        if not symbol_probe.c_identifier_compatible:
            payload.update({"status": "blocked", "blocked_stage": "callback_symbol_not_c_identifier"})
            return payload

        wrapper_source = specialize_semantic_wrapper_source(symbol_probe.symbol)
        wrapper_cu = tmp_path / "tier3_wrapper.cu"
        wrapper_ptx = tmp_path / "tier3_wrapper.ptx"
        wrapper_cu.write_text(wrapper_source + "\n", encoding="utf-8")
        payload["wrapper_source_generated"] = True
        payload["wrapper_source_preview"] = wrapper_source[:2000]

        compile_command = [
            str(nvcc),
            "-ptx",
            "-std=c++17",
            "-I",
            str(optix_include),
            str(wrapper_cu),
            "-o",
            str(wrapper_ptx),
        ]
        payload["wrapper_compile_attempted"] = True
        compile_proc = _run(compile_command, cwd=tmp_path)
        payload["wrapper_compile"] = {
            "command": compile_command,
            "returncode": compile_proc.returncode,
            "stdout": compile_proc.stdout.strip()[:4000],
            "stderr": compile_proc.stderr.strip()[:4000],
        }
        if compile_proc.returncode != 0 or not wrapper_ptx.exists():
            payload.update(
                {
                    "status": "blocked",
                    "blocked_stage": "semantic_wrapper_compile",
                    "wrapper_compile_succeeded": False,
                }
            )
            return payload
        payload.update(
            {
                "status": "semantic_wrapper_compile_passed_no_module_link",
                "wrapper_compile_succeeded": True,
                "wrapper_ptx_length": wrapper_ptx.stat().st_size,
                "next_stage": "Goal4688 optixModuleCreate/program-group/pipeline probe",
            }
        )
    return payload


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V4 Goal4687 Tier-3 Wrapper Compile Probe",
        "",
        "Status: compile probe only, not Tier-3 support and not release authorization",
        "",
        f"- status: `{payload['status']}`",
        f"- Numba PTX generated: `{payload['numba_ptx_generated']}`",
        f"- wrapper source generated: `{payload['wrapper_source_generated']}`",
        f"- wrapper compile attempted: `{payload['wrapper_compile_attempted']}`",
        f"- wrapper compile succeeded: `{payload['wrapper_compile_succeeded']}`",
        f"- OptiX module link attempted: `{payload['optix_module_link_attempted']}`",
        "",
        "## Boundary",
        "",
        "This probe may generate Numba PTX and compile a semantic wrapper shape. It does not link an OptiX module, create program groups, launch a pipeline, measure overhead, or authorize Tier-3 support.",
        "",
        "## Non-Authorization",
        "",
        "No release, no Tier-3 public support, no raw OptiX callback support, no public speedup wording, no whole-app claim, and no app-specific native kernels.",
        "",
    ]
    if payload.get("status") == "blocked":
        lines.extend(["## Blocked Stage", "", f"- blocked stage: `{payload.get('blocked_stage')}`", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe V4 Goal4687 Tier-3 wrapper symbol extraction and compile shape.")
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
    return 0 if payload["status"] in {"dry_run_contract_passed", "semantic_wrapper_compile_passed_no_module_link"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
