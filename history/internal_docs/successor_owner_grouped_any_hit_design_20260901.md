# Successor design: app-neutral owner-grouped any-hit

Date: 2026-09-01; updated 2026-09-02
Status: internal OptiX 8 GPU functional gate complete; no performance claim

## Problem exposed by the paper-derived collision case

RTDL V4 can verify and compile callback-local restricted Python, but the
existing public round-linear-curve route has a fixed four-role protocol. Its
compiler-owned any-hit entry point selects one canonical closest contact and
does not invoke a user-authored any-hit role. The paper-derived linear RT-CCD
subset needs every accepted curve intersection to update an output belonging
to that curve's trajectory.

Adding collision, robot, pose, or trajectory vocabulary to the native engine
would violate the app-independent-engine rule. Exposing a raw writable pointer
and `atomicAdd` to callback source would also bypass RTDL's resource, bounds,
delivery, and fail-closed obligations.

## Selected contract

The successor behavior is `OWNER_GROUPED_ANY_HIT` with one initially admitted
algebra, `BOOL_OR`:

```text
accepted event = (query_id, primitive_id)
owner = owner_ids[primitive_id]
owner_hit_bits[owner] |= 1
```

The behavior contract contains no geometry or application identity. The first
physical adapter uses OptiX built-in round-linear curves, but later adapters
may use another geometry family without changing the reduction semantics.

## Language and backend boundary

- Existing Callback IR remains unchanged.
- Restricted Python any-hit returns `accept_continue(payload=payload)`.
- A compiler-recognized proof checks that every any-hit return preserves the
  payload and that the manifest selects `idempotent_monotone` delivery.
- The physical schema binds one read-only primitive-owner U32 column and one
  owner-sized U32 Boolean output.
- The trusted wrapper performs the implementation atomic. Raw atomics and
  writable views are not part of the source language.
- Invalid primitive or owner indices claim device status and make the runtime
  reject before exposing any partial owner vector.
- Event order and duplicate delivery are non-semantic because Boolean OR is
  associative, commutative, idempotent, and monotone.

This is deliberately narrower than arbitrary grouped reduction. Checked counts
would need duplicate-delivery and overflow contracts and are not silently
included in this tranche.

## Collision application boundary

The application will own:

- directed obstacle-edge construction;
- curve-to-trajectory owner IDs;
- scene/query generation;
- the independent finite segment/capsule correctness oracle; and
- interpretation of `owner_hit_bits` as trajectory collision decisions.

The bounded app additionally requires every query edge to be longer than the
maximum diameter of any one swept capsule. This O(P+Q) sufficient condition
excludes a finite edge wholly contained inside a capsule without running the
O(P*Q) collision discovery in Python. Inputs are canonicalized to f32 first;
the implementation compares an outward-rounded query-length lower bound with
an outward-rounded capsule-diameter upper bound. Registered evidence also
requires a positive distance gap from the tangent boundary. General
near-tangent inputs remain outside scope.

The engine and primitive will not contain collision, trajectory, robot, pose,
force, or paper-specific logic.

## Evidence boundary

Local tests may establish schema determinism, Callback-IR admission, proof
rederivation, CPU semantics, generated-source structure, and hostile rejection.
Only a compatible NVIDIA/OptiX pod can establish PTX compilation, native ABI
linkage, true traversal, GPU parity, or performance. The separate Pod report
now establishes the functional items for one exact OptiX 8 profile; performance
and broader provider-version claims remain unauthorized.

## Implemented lifecycle

The implementation now carries the contract through all local layers:

1. The behavior schema recognizes the closed pass-through any-hit callback and
   binds the idempotent Boolean-OR proof.
2. The round-linear-curve physical schema binds typed curve, owner, query,
   result, completion, and status columns.
3. Four restricted-Python callback roles lower to isolated Numba device
   functions and compose with a trusted OptiX wrapper.
4. The native route builds one static round-linear-curve GAS, traces every
   finite query with real `optixTrace`, maps each accepted primitive through
   `owner_ids`, performs `atomicOr`, ignores the intersection, and continues.
5. The prepared runtime validates exact OptiX/compute target identity, static
   host/device fingerprints, descriptor transitions, status-first downloads,
   output fingerprints, and nonce-bound traversal receipts.
6. The app owns a reusable prepared wrapper so repeated executions reuse the
   same static GAS without moving collision semantics into RTDL.

The frozen Goal5835/5836 files remain unchanged. This successor is a separate
transaction and does not rewrite the terminal Goal5836 A1 finding.

## Local evidence and pod handoff

The local receipt covers six semantic edge cases and three deterministic scale
ladders. It proves source generation and independent CPU-oracle agreement only;
its GPU launch count is exactly zero.

This CGO handoff snapshot intentionally has no root `Makefile`. The auditable
fresh builder is `scripts/build_v4_optix_native_snapshot.py`; it compiles the
complete native translation units, inventories the native source snapshot,
records CUDA/OptiX/GPU/Git identities, and rejects a library missing any of the
four new C ABI symbols. The GPU front door is
`scripts/successor_linear_rtccd_owner_grouped_pod_runner.py`. It uses only the
public app lifecycle, emits progress per workload/repeat, checks every result
against the independent oracle, and validates one bound true-OptiX receipt per
execution. The runner now requires the builder manifest and binds the selected
native bytes to the same Git commit, builder hash, and complete native source
inventory. It records an execution-source inventory before launch, rechecks it
after all workloads, publishes the final JSON exclusively, and leaves an
explicit incomplete marker if execution aborts. Explicit CUDA and OptiX
prefixes are required; each supplied include path must resolve to its prefix's
include directory, so toolkit symlinks cannot silently change compiler or
runtime-library discovery.

Before either step, `scripts/successor_owner_grouped_pod_preflight.py` rejects
the wrong OS/architecture, multiple visible GPUs, a requested compute target
that differs from the actual GPU, wrong OptiX headers, dirty Git state, missing
NVRTC/NVVM/libdevice, or failed compilation of the exact four Numba leaves and
trusted NVRTC wrapper. It also compiles a minimal object with the exact
`nvcc`/host-compiler/SM target and runs a temporary zero-launch `optixInit()`
probe to reject an SDK/host-driver ABI mismatch. The builder and runner
independently recheck the same GPU identity and bind exact `nvcc`, its host C++
compiler, CUDA/OptiX header inventories, and runtime compiler-library bytes.
Passing preflight alone remains zero-launch toolchain evidence, not GPU
correctness evidence.

The first Pod exposed why runtime ABI negotiation belongs in preflight: OptiX 9
compiled and linked but driver 550.127.05 rejected it before launch. The route
uses no OptiX 9-specific API, and NVIDIA supports OptiX 8.0 on R535 or newer.
The exact OptiX 8.0/R550/RTX 4000 Ada profile is therefore the internal GPU
functional target, while OptiX 9 is additional version coverage. Preflight v2
confirmed this distinction: OptiX 9 failed early with
`optixInit_result=7801`, while OptiX 8 returned `optixInit_result=0` with zero
launches. At the controlling clean commit, a fresh build passed six semantic
and four scale workloads three times for 30 true-OptiX launches. The largest
scale used 4096 primitives and 1024 queries. Exact evidence and the
non-performance boundary are recorded in
`successor_owner_grouped_pod_20260902/INTERNAL_POD_DIAGNOSTIC_REPORT.md`; the
profile decision is
`successor_owner_grouped_optix_profile_decision_20260902.md`.

All runner timings are diagnostics. `registered_performance_timing_count=0`
and `performance_claimed=false` remain mandatory until a separate benchmark
design and deferred external review are completed.
