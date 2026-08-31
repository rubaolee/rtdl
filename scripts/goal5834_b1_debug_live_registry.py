#!/usr/bin/env python3
"""Zero-launch diagnostic for Goal5834-B1 executable registry failures."""

from pathlib import Path

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_curve import V4CurveTarget, curve_any_contact_boolean_source
import rtdsl.v4_curve_optix_compiler as compiler


native = Path("build_b1/librtdl_optix.so")
target = V4CurveTarget.from_native(
    native, optix_sdk="9.0.0", compute_capability="6.1")
toolchain = V4Toolchain.current(
    compute_capability=(6, 1),
    optix_include=Path("/home/lestat/vendor/optix-dev/include"),
    cuda_include=Path("/usr/lib/cuda/include"),
)
program = curve_any_contact_boolean_source().compile(target=target)
materialized = program.materialize(toolchain=toolchain)
executable = materialized.executable
print("id", id(executable))
print("sealed", executable.executable_sha256)
print("registry", compiler._LIVE_EXECUTABLES)
print("rederived", compiler.rederive_verified_curve_executable_sha256(
    executable, program.authority, program.authority.canonical_plan,
    program.abi))
second = program.materialize(toolchain=toolchain).executable
print("second_id", id(second))
print("second_sealed", second.executable_sha256)
print("same_wrapper", executable.wrapper == second.wrapper)
print("same_wrapper_ptx", executable.wrapper_ptx_sha256 == second.wrapper_ptx_sha256)
print("same_generated", executable.generated_leaves == second.generated_leaves)
print("compiled_first", [row.ptx_sha256 for row in executable.compiled_leaves])
print("compiled_second", [row.ptx_sha256 for row in second.compiled_leaves])
print("same_composed", executable.composed.ptx_sha256 == second.composed.ptx_sha256)
print("log_first", executable.nvrtc_log_sha256)
print("log_second", second.nvrtc_log_sha256)
import difflib
for line in list(difflib.unified_diff(
        executable.wrapper_ptx.splitlines(), second.wrapper_ptx.splitlines(),
        fromfile="first", tofile="second", n=2))[:80]:
    print(line)
