#!/usr/bin/env python3
"""Compile the accepted Goal5750 reference program into seven audited PTX leaves.

This is a compiler preflight, not a CUDA/OptiX execution or performance test.
It intentionally uses the same reference source/manifest as the frozen CPU
semantic oracle while exercising only product frontend/IR/ABI/codegen modules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numba
import numpy as np

from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_callback_numba_codegen import (
    compile_formal_numba_leaf_isolated,
    generate_formal_numba_leaf,
)
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cc-major", type=int, required=True)
    parser.add_argument("--cc-minor", type=int, required=True)
    parser.add_argument("--ptx-min", default="8.0")
    parser.add_argument("--ptx-max", default="9.0")
    parser.add_argument("--expected-python", required=True)
    parser.add_argument("--expected-numba", required=True)
    parser.add_argument("--expected-numpy", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to replace evidence: {args.output}")

    verified = compile_callback_source(SOURCE, manifest())
    delivery = verified.program.manifest.any_hit_delivery
    if delivery is None:
        raise RuntimeError("reference program lacks its any-hit delivery contract")
    proof = AnyHitProofAuthority(
        callback_ir_sha256=verified.ir_sha256,
        effect_digest=verified.effect_digest,
        delivery_contract=delivery,
        proof_sha256="a" * 64,
        proof_kind="external_machine_checked_order_independence_v1",
    )
    abi = compile_callback_abi(verified, any_hit_proof_authority=proof)
    role_rows: list[dict[str, object]] = []
    for role in CallbackRole:
        leaf = generate_formal_numba_leaf(
            verified,
            abi,
            role,
            any_hit_proof_authority=proof,
        )
        artifact = compile_formal_numba_leaf_isolated(
            leaf,
            compute_capability=(args.cc_major, args.cc_minor),
            accepted_ptx_isa=(args.ptx_min, args.ptx_max),
            allowed_external_symbols=frozenset(),
            expected_python_version=args.expected_python,
            expected_numba_version=args.expected_numba,
            expected_numpy_version=args.expected_numpy,
        )
        role_rows.append({
            "role": role.value,
            "abi_name": artifact.abi_name,
            "generated_source_sha256": artifact.generated_source_sha256,
            "ptx_sha256": artifact.ptx_sha256,
            "ptx_version": artifact.ptx_version,
            "ptx_target": artifact.ptx_target,
            "ptx_byte_count": len(artifact.ptx.encode("utf-8")),
            "external_symbols": list(artifact.external_symbols),
            "nonce_word": artifact.nonce_word,
        })

    payload = {
        "schema": "rtdl.goal5751.formal_numba_ptx_preflight.v1",
        "purpose": "compiler_only__no_cuda_or_optix_execution__no_performance",
        "callback_ir_sha256": verified.ir_sha256,
        "callback_effect_digest": verified.effect_digest,
        "callback_abi_sha256": abi.abi_sha256,
        "any_hit_proof_sha256": proof.proof_sha256,
        "compute_capability": [args.cc_major, args.cc_minor],
        "toolchain": {
            "python": platform.python_version(),
            "numba": numba.__version__,
            "numpy": np.__version__,
        },
        "role_count": len(role_rows),
        "all_roles_compiled": len(role_rows) == len(CallbackRole),
        "all_ptx_externals_empty": all(not row["external_symbols"] for row in role_rows),
        "roles": role_rows,
        "claims": {
            "gpu_execution_performed": False,
            "optix_pipeline_built": False,
            "device_interpreter_equivalence_claimed": False,
            "performance_claimed": False,
            "goal5751_complete": False,
        },
        "input_file_sha256": {
            "script": _sha256(Path(__file__).resolve()),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
