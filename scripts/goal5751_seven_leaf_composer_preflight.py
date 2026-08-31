#!/usr/bin/env python3
"""Exercise the closed composer with all seven real formal Numba PTX leaves."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_callback_numba_codegen import (
    compile_formal_numba_leaf_isolated,
    generate_formal_numba_leaf,
)
from rtdsl.v4_callback_ptx_composer import compose_callback_ptx
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-python", required=True)
    parser.add_argument("--expected-numba", required=True)
    parser.add_argument("--expected-numpy", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to replace evidence: {args.output}")
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
    leaves = []
    symbols: dict[str, str] = {}
    for role in CallbackRole:
        generated = generate_formal_numba_leaf(
            verified, abi, role, any_hit_proof_authority=proof
        )
        artifact = compile_formal_numba_leaf_isolated(
            generated,
            compute_capability=(6, 1),
            accepted_ptx_isa=("8.0", "9.0"),
            allowed_external_symbols=frozenset(),
            expected_python_version=args.expected_python,
            expected_numba_version=args.expected_numba,
            expected_numpy_version=args.expected_numpy,
        )
        leaves.append(artifact)
        symbols[artifact.role] = artifact.abi_name
    externs = "".join(
        f".extern .func {symbols[role.value]}\n(\n);\n" for role in CallbackRole
    )
    wrapper = (
        ".version 8.0\n.target sm_61\n.address_size 64\n"
        + externs
        + ".visible .func rtdl_v4_trusted_wrapper_preflight() {\n ret;\n}\n"
    )
    composed = compose_callback_ptx(
        wrapper, leaves, exact_symbols_by_role=symbols
    )
    payload = {
        "schema": "rtdl.goal5751.seven_leaf_composer_preflight.v1",
        "purpose": "composition_only__not_an_optix_module_or_execution_claim",
        "callback_ir_sha256": verified.ir_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "leaf_count": len(leaves),
        "leaf_bindings": [list(item) for item in composed.leaf_bindings],
        "compiler_function_counts": {
            leaf.role: leaf.compiler_function_count for leaf in leaves
        },
        "stripped_wrapper_extern_count": len(composed.stripped_wrapper_externs),
        "stripped_numba_environment_count": len(composed.stripped_numba_environments),
        "wrapper_ptx_sha256": composed.wrapper_ptx_sha256,
        "composed_ptx_sha256": composed.ptx_sha256,
        "composed_ptx_byte_count": len(composed.ptx.encode("utf-8")),
        "ptx_version": composed.ptx_version,
        "ptx_target": composed.ptx_target,
        "address_size": composed.address_size,
        "claims": {
            "optix_module_built": False,
            "gpu_execution_performed": False,
            "behavioral_traversal_claimed": False,
            "performance_claimed": False,
            "goal5751_complete": False
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
