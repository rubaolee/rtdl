#!/usr/bin/env python3
"""Development-only fail-closed diagnostic for PTX identity composition."""

from __future__ import annotations

import argparse
import platform
import re

import numba
import numpy as np

from rtdsl.v4_bounded_relation_optix_compiler import generate_bounded_relation_numba_leaf
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_callback_numba_codegen import compile_formal_numba_leaf_isolated
from rtdsl.v4_multiround_spatial_optix_wrapper_codegen import generate_trusted_multiround_spatial_wrapper_v1
from rtdsl.v4_triangle_optix_compiler import _compile_nvrtc
from scripts.goal5761_home_multiround_spatial_validation import _authority
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


def directives(ptx: str):
    return tuple(line.strip() for line in ptx.splitlines()
                 if re.match(r"\s*\.(version|target|address_size)\b", line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-sha", required=True)
    parser.add_argument("--optix-include", required=True)
    parser.add_argument("--cuda-include", required=True)
    args = parser.parse_args()
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=args.native_sha, supports_custom_aabb=True,
        supports_builtin_triangle=True)
    authority, proof = _authority(target)
    for role in CallbackRole:
        generated = generate_bounded_relation_numba_leaf(
            authority.relation, authority.abi, role,
            any_hit_proof_authority=proof)
        artifact = compile_formal_numba_leaf_isolated(
            generated, compute_capability=(6, 1), accepted_ptx_isa=("8.0", "9.0"),
            allowed_external_symbols=frozenset(),
            expected_python_version=platform.python_version(),
            expected_numba_version=numba.__version__,
            expected_numpy_version=np.__version__)
        print(role.value, directives(artifact.ptx))
    wrapper = generate_trusted_multiround_spatial_wrapper_v1(
        authority.relation, authority.relation_contract, authority.abi,
        any_hit_proof_authority=proof)
    options = (
        f"-I{args.optix_include}", f"-I{args.cuda_include}",
        "-I/usr/include", "-I/usr/include/x86_64-linux-gnu", "--std=c++14",
        "--gpu-architecture=compute_61", "--relocatable-device-code=true",
        "-D__x86_64__=1", "-D__LP64__=1")
    ptx, _ = _compile_nvrtc(wrapper.source, options)
    print("wrapper", directives(ptx))


if __name__ == "__main__":
    main()
