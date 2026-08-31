#!/usr/bin/env python3
"""Generate and NVRTC-compile the trusted seven-role OptiX wrapper."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from goal5749_nvrtc_wrapper_preflight import _compile
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_optix_wrapper_codegen import generate_trusted_optix_wrapper_v1
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--cc", choices=("61", "89"), required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    verified = compile_callback_source(SOURCE, manifest())
    delivery = verified.program.manifest.any_hit_delivery
    assert delivery is not None
    proof = AnyHitProofAuthority(
        verified.ir_sha256,
        verified.effect_digest,
        delivery,
        "a" * 64,
        "external_machine_checked_order_independence_v1",
    )
    abi = compile_callback_abi(verified, any_hit_proof_authority=proof)
    wrapper = generate_trusted_optix_wrapper_v1(
        verified, abi, any_hit_proof_authority=proof
    )
    options = [
        f"-I{args.optix_include.resolve()}",
        f"-I{args.cuda_include.resolve()}",
        "-I/usr/include",
        "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        f"--gpu-architecture=compute_{args.cc}",
        "--relocatable-device-code=true",
        "-D__x86_64__=1",
        "-D__LP64__=1",
    ]
    ptx, log = _compile(wrapper.source, options)
    source_path = args.output / "TRUSTED_WRAPPER.cu"
    ptx_path = args.output / "TRUSTED_WRAPPER.ptx"
    log_path = args.output / "NVRTC.log"
    source_path.write_text(wrapper.source)
    ptx_path.write_text(ptx)
    log_path.write_text(log)
    role_symbols = dict(wrapper.role_symbols)
    entries = ["raygen", "intersection", "anyhit", "closesthit", "miss"]
    result = {
        "schema": "rtdl.goal5751.optix_wrapper_preflight.v1",
        "callback_ir_sha256": verified.ir_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "physical_template": wrapper.physical_template,
        "wrapper_source_sha256": wrapper.source_sha256,
        "wrapper_ptx_sha256": hashlib.sha256(ptx.encode()).hexdigest(),
        "wrapper_ptx_byte_count": len(ptx.encode()),
        "ptx_version": re.search(r"(?m)^\s*\.version\s+(\S+)", ptx).group(1),
        "ptx_target": re.search(r"(?m)^\s*\.target\s+(\S+)", ptx).group(1),
        "all_seven_exact_leaf_externs_present": all(
            symbol in ptx for symbol in role_symbols.values()
        ),
        "all_five_optix_entry_points_present": all(
            f"__{entry}__rtdl_v4_formal" in ptx for entry in entries
        ),
        "atomic_first_error_present": "atom.global.cas.b32" in ptx,
        "role_symbols": role_symbols,
        "claims": {
            "nvrtc_compile_only": True,
            "optix_module_built": False,
            "gpu_execution_performed": False,
            "performance_claimed": False,
            "goal5751_complete": False
        }
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    manifest_rows = []
    for path in sorted(item for item in args.output.iterdir() if item.is_file()):
        manifest_rows.append({
            "path": path.name,
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        })
    (args.output / "MANIFEST.json").write_text(
        json.dumps(manifest_rows, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
