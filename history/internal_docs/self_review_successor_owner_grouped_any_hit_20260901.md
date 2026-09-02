# Internal hostile self-review: successor owner-grouped any-hit

Date: 2026-09-01; updated 2026-09-02
Review type: internal hostile self-review only
External review count: 0, deferred by the owner
Verdict: `ACCEPT_LOCAL_IMPLEMENTATION__BLOCK_GPU_PROMOTION`

## Exact claim boundary

The reviewed successor implements an app-neutral `OWNER_GROUPED_ANY_HIT / BOOL_OR`
behavior and one OptiX built-in round-linear-curve physical adapter. Accepted
`(query_id, primitive_id)` events map through a read-only `owner_ids` column and
perform `owner_hit_bits[owner] |= 1` before continuing traversal. Restricted
Python still expresses only `accept_continue(payload=payload)`; raw writable
pointers and atomics are not added to Callback IR.

The collision case study owns trajectory, sphere, segment, obstacle-edge,
orientation, oracle, and result interpretation. No collision, robot, pose,
trajectory, or RT-CCD vocabulary appears in the successor RTDL modules. The
frozen Goal5835/5836 transaction was not modified or reinterpreted.

This review authorizes only the local source implementation and local evidence.
It does not authorize claims of native compilation, Numba PTX compilation,
NVRTC composition, true OptiX execution, GPU correctness, performance, full
paper reproduction, Paper App status, or benchmark-app promotion.

## Resolved findings

### R1, P1: surface-only traversal could miss a fully contained finite query

A finite query edge wholly inside one capsule overlaps the capsule volume but
need not cross the OptiX curve surface. Reversing the query does not repair that
case. The app now requires an O(P+Q) sufficient certificate:
`minimum_query_length > maximum_capsule_diameter`. This excludes fully contained
queries without performing the O(PxQ) collision discovery in Python. Registered
workloads also have an independently measured surface gap of at least `2^-10`.

### R2, P1: native execution was not bound to its fresh build evidence

The first pod runner accepted only a `.so` path. It now requires the native
builder manifest and rejects any mismatch in native bytes, byte count, absolute
path, Git commit, builder SHA-256, complete native source inventory, required
symbols, or dirty-build authorization. Exported symbols are parsed as exact
dynamic defined names from `nm`, not substring matches.

### R3, P1: reference and GPU output commitments used different framing

The CPU reference and prepared runtime now share
`OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA` and
`owner_grouped_any_hit_output_sha256`. Equal Boolean owner vectors therefore
produce the same canonical commitment across implementations.

### R4, P2: cleanup could mask the primary failure

Failed prepare validation now preserves both the descriptor failure and native
destroy failure. Generic and app-owned context managers preserve both a body
failure and a cleanup failure. Generic prepared `close()` is now idempotent.

### R5, P2: correctness-runner parameters could create unbounded host work

The deterministic scale generator now bounds primitive count, directed-query
count, and the O(PxQ) independent-oracle pair count. The runner also bounds the
number of custom scales and total repeated executions. Oversized inputs fail
before materialization or GPU launch.

### R6, P2: output and artifact paths admitted ambiguous partial evidence

Build outputs and GPU result/artifact paths must be distinct and non-nested.
Native and JSON result files are published exclusively from temporary files.
The GPU artifact directory contains `RUN_INCOMPLETE.json` until the complete
result is published. The runner rejects Git/status/source drift during a run.

### R7, P2: behavior and physical schema closure was sampled rather than exhaustive

Tests now mutate every behavior-schema and physical-schema dataclass field.
Canonical fields must reject drift; the one admitted capacity mutation must
change schema and authority identities.

### R8, P1: pod toolchain and native build identity were not closed end to end

The original runner recorded an ambient PATH `nvcc`, did not require the
requested compute capability to equal the visible GPU, and did not rederive
the native `build_id`. The candidate now has a zero-launch preflight that
compiles a minimal exact-`nvcc`/host-compiler object, all four actual isolated
Numba leaves, and the trusted NVRTC wrapper. Preflight and runner self-reexec
with exact NVRTC/NVVM/libdevice paths and clear loader, Numba-target, old
provider, and formal-cache overrides. The builder binds the visible GPU,
exact `nvcc`, exact host compiler, and complete CUDA/OptiX header inventories.
The runner rehashes those inputs, recomputes `build_id`, and requires that same
ID from the executed native descriptor before accepting any workload.

### R9, P2: the surface-crossing certificate had no explicit rounding policy

Application objects already canonicalized all coordinates and radii to f32,
but the O(P+Q) length certificate used ordinary binary64 length calculations.
It now compares an outward-rounded query-length lower bound against an
outward-rounded capsule-diameter upper bound using `fsum`, `sqrt`, and
`nextafter`, and records the positive certified margin and policy in its v2
admission receipt.

### R10, P2: fresh-checkout entrypoints implicitly required `PYTHONPATH`

The first pre-pod audit found that the preflight, GPU runner, and local receipt
generator could fail during imports when invoked directly without
`PYTHONPATH=src:.`. Each entrypoint now derives the repository root from its
own resolved path and bootstraps only that root plus `src` before project
imports. A subprocess regression clears `PYTHONPATH` and requires all three
`--help` front doors to succeed.

### R11, P1: runner derived a false CUDA prefix through an include symlink

The first clean-pod runner attempt stopped before any OptiX launch because
`/usr/local/cuda-12.8/include` resolves into
`targets/x86_64-linux/include`; taking the resolved include's parent therefore
produced a false CUDA prefix and hid NVRTC. The runner now requires explicit
CUDA and OptiX prefixes, verifies that each supplied include resolves to its
prefix's include directory, preserves the logical include path used by the
native manifest, and locates `nvcc` from the explicit CUDA prefix. A symlinked
CUDA-layout regression covers this exact failure mode.

## Open promotion blockers

### O1, P1: no compatible GPU execution exists

This Mac cannot compile the isolated Numba leaves for CUDA, compile the trusted
wrapper with NVRTC, build/link the OptiX native library, or launch the route.
The checked-in receipt records `native_library_built=false`,
`numba_ptx_compiled=false`, `optix_launch_count=0`, and
`gpu_correctness_evidence_count=0`. A compatible NVIDIA/OptiX pod is mandatory.

### O2, P1: arbitrary near-boundary inputs are outside the proved app domain

The O(P+Q) length certificate excludes fully contained queries but cannot prove
distance from tangency without pairwise geometry work. Registered workloads are
far from the boundary under the independent oracle; arbitrary tangent or
near-tangent inputs remain outside the claim. This is a deliberate bounded
subset, not general RT-CCD correctness.

### O3, P2: per-execution query bytes are not read back from the device

Static curve and owner columns are uploaded and read back once during prepare,
then compared by canonical fingerprint. Each query batch has a canonical host
fingerprint and checked CUDA uploads, but the six device query columns are not
downloaded again solely for evidence. Adding six D2H copies to every execution
would contaminate the intended performance path. Current evidence therefore
trusts successful CUDA copies and the bound launch; it is not a per-execution
device-content rehash claim.

### O4, P2: the containment certificate is conservative

Many valid surface-crossing inputs have query lengths below the maximum capsule
diameter and are rejected. This trades completeness for a cheap, app-owned,
fail-closed admission. Cross-app evidence would be required before moving a
more expressive containment treatment into RTDL.

### O5, P2: this is not the complete author benchmark

The successor preserves the paper/code insight of primitive-to-pose grouped
any-hit accumulation and continued traversal, but uses Boolean OR rather than
author hit counts. It does not reproduce Franka kinematics, 62-sphere data,
mesh-loop preprocessing, all collision predicates, author-code execution, or a
same-input performance comparison.

### O6, P2: no same-contract Embree/performance row exists

The pod runner collects only diagnostic phase times and explicitly records
`registered_performance_timing_count=0` and `performance_claimed=false`.
An Embree adapter and preregistered performance design are future work, not a
condition for the current local language/runtime proof.

### O7, P3: external review is intentionally absent

The owner deferred external review while traveling. No consensus wording is
authorized until that review is separately requested and completed.

## Local evidence

- Successor tests: 49/49 pass.
- Goal5833--Goal5836 frozen/relevant regressions: 168/168 pass.
- Stored local receipt: 9/9 semantic/scale cases match the independent oracle.
- Receipt SHA-256: `997c95845f4e1bc59a107ad706e5b88501e31fda8c037950ca4e70a72aaec0e2`.
- `scripts/audit_goal5835_goal5836.py --verify-stored`: pass.
- `scripts/goal5836_a1_build_source_fidelity.py --verify-stored`: pass.
- Python compile-all and `git diff --check`: pass.

## Exact next evidence step

On one clean, compatible NVIDIA/OptiX checkout:

1. Run `scripts/successor_owner_grouped_pod_preflight.py`; preserve its
   zero-launch result and require both compiler probes to pass.
2. Build with `scripts/build_v4_optix_native_snapshot.py` and save its manifest.
3. Run `scripts/successor_linear_rtccd_owner_grouped_pod_runner.py` with the
   exact `.so` and `--native-manifest` from step 2.
4. Require all nine default workloads, repeated prepared execution, independent
   oracle parity, descriptor transitions, and true-OptiX receipts to pass.
5. Preserve the preflight result, build log, native manifest, materialized
   artifacts, and final result JSON. Treat all timing fields as diagnostics
   only.

Until that step passes, the correct status remains
`LOCAL_IMPLEMENTATION_COMPLETE__GPU_VALIDATION_REQUIRED`.
