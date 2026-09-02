# Internal hostile self-review: successor owner-grouped any-hit

Date: 2026-09-01; updated 2026-09-02
Review type: internal hostile self-review only
External review count: 0, deferred by the owner
Verdict: `ACCEPT_INTERNAL_OPTIX8_GPU_FUNCTIONAL_GATE__BLOCK_PERFORMANCE_AND_EXTERNAL_PROMOTION`

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

This review authorizes the local source implementation and exact-profile
OptiX 8 internal GPU functional evidence on one RTX 4000 Ada Pod. It does not
authorize performance, full paper reproduction, Paper App status,
benchmark-app promotion, broad OptiX-version support, or external-consensus
wording.

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

### R12, P1: compile-only preflight overclaimed runtime readiness

The first Pod preflight compiled every callback and wrapper successfully under
OptiX 9, and the native library built, but the host's NVIDIA 550.127.05 driver
rejected the OptiX 9 ABI during the first prepare, before any launch. The old
status `READY_FOR_NATIVE_BUILD_AND_GPU_RUN` therefore exceeded its evidence.
Preflight v2 now compiles and runs a temporary `optixInit()` program before the
callback stack, records its binary and output hashes, and still performs zero
OptiX launches. An ABI mismatch now fails before the expensive native build.
The schema changed from `pod_preflight.v1` to `pod_preflight.v2` so old
compile-only artifacts cannot be confused with new runtime-ABI evidence.
Pod confirmation at commit `5ee0e94` rejected OptiX 9 with
`optixInit_result=7801` before callback compilation/native build and accepted
OptiX 8 with `optixInit_result=0` and zero launches.

### R13, P1: OptiX 9 was treated as a mandatory gate without a semantic reason

Source inspection and a complete OptiX 8 build show that the route uses no
OptiX 9-specific API. No frozen successor authority selected 9.0.0 as the only
valid provider profile; it was a CLI/documentation default. NVIDIA requires
R570 or newer for OptiX 9, while OptiX 8.0 requires R535 or newer. The current
R550 host is therefore a supported OptiX 8 profile and an unsupported OptiX 9
profile. The exact OptiX 8 profile is accepted for internal functional
completion; OptiX 9 is separate portability coverage. Both successor CLI
entrypoints now require an explicit SDK version rather than silently choosing
one.

## Open promotion blockers

### O1, P3: OptiX 9 portability coverage is absent

The current Pod's driver rejected OptiX 9 before launch, exactly as NVIDIA's
R570 minimum predicts. This blocks any OptiX 9 or broad cross-version wording,
but it does not block the exact OptiX 8 internal functional result. A future
R570-or-newer run is useful environment-diversity evidence, not unfinished app
semantics.

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

- Successor tests: 51/51 pass.
- Goal5833--Goal5836 frozen/relevant regressions: 168/168 pass.
- Stored local receipt: 9/9 semantic/scale cases match the independent oracle.
- Receipt SHA-256: `291a3e2ff23ba027084ca06f594a6fb1fc9d760c20aaa6e6f960140e6767faef`.
- `scripts/audit_goal5835_goal5836.py --verify-stored`: pass.
- `scripts/goal5836_a1_build_source_fidelity.py --verify-stored`: pass.
- Python compile-all and `git diff --check`: pass.

## Internal Pod functional evidence

The internal report is
`successor_owner_grouped_pod_20260902/INTERNAL_POD_DIAGNOSTIC_REPORT.md`.
At commit `2c48337`, OptiX 9 compiled and linked but failed ABI negotiation on
driver 550.127.05 before launch. At controlling commit `7ec6b67`, preflight v2
correctly split the SDK outcomes and a fresh official OptiX 8 build completed
six semantic plus four scale workloads three times: 30/30 true-OptiX launches,
oracle parity, and prepared reuse all passed. The largest scale used 512 owners,
4096 primitives, 1024 queries, 4,194,304 oracle evaluations, and 1024
intersecting pairs. Mac and Pod regressions both passed at 51/51 successor and
168/168 frozen tests. Timings are diagnostic only; registered performance
count and external review count both remain zero.

## Next separate gates

1. Complete the owner-deferred external review before any consensus or public
   promotion wording.
2. Use R570-or-newer hardware only if OptiX 9 portability is to be claimed.
3. Preregister an Embree baseline and timing protocol before any benchmark or
   speedup claim.

The correct current status is
`INTERNAL_OPTIX8_GPU_FUNCTIONAL_GATE_COMPLETE__PERFORMANCE_AND_EXTERNAL_PROMOTION_DEFERRED`.
