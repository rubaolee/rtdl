# Goal2657: v2.4/v2.5 Partner Roadmap With Benchmark Performance Gates

Status: proposal for review.

Date: 2026-05-27

## Purpose

RTDL's user-facing purpose is to make RT-core programming easier from Python
without forcing users to maintain custom C++/CUDA/OptiX code for every app.
The next partner work should move toward that purpose, but ease of use must not
erase the performance evidence established by the current promoted benchmark
suite.

The rule for v2.4/v2.5 is therefore:

```text
Make RT cores easier to use, but keep the current 10 benchmark apps as the
performance basis. A friendlier partner path is not acceptable as a promoted
performance path if it significantly loses the measured RT-vs-Embree advantage.
```

This document is a roadmap boundary, not a new release claim. It does not widen
public performance wording.

## Current Performance Basis

The current v2.3-family basis is the 10 promoted benchmark apps documented in:

- `docs/release_reports/v2_3/benchmark_app_performance.md`
- `docs/release_reports/v2_3/benchmark_app_performance_3ai_consensus.md`
- `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- `docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md`

The primary rows are exact-subpath internal evidence, not public whole-app
claims.

| Benchmark app | Current primary OptiX-vs-Embree basis |
| --- | ---: |
| Hausdorff / X-HD-style | 3.29x |
| Spatial RayJoin-style | 38.36x |
| RT-DBSCAN-style | 12.71x |
| Robot collision | 5.29x |
| RayDB-style grouped aggregate | 27.67x count; 104.00x sum |
| Barnes-Hut / RT-BarnesHut-style | 4.55x |
| LibRTS-style spatial index | 29.95x |
| RTNN neighbor search | 172.14x |
| Triangle counting | 107.16x |
| Bounded contact witness / contact-manifold | 26.29x |

RayDB has two primary rows because grouped `count` and grouped `sum` are
distinct reduction contracts.

## Performance Gates

The following gates should apply before any v2.4/v2.5 path becomes the default
or becomes eligible for performance wording.

1. The accepted RT-vs-Embree rows above remain the regression basis. If a new
   partner path changes one of these rows, it must rerun the same-contract
   comparison and record the backend, hardware, commit, command, workload, and
   phase timing.
2. A promoted partner path should preserve the current best supported path
   within roughly 10 percent for the measured exact subpath, or improve it. A
   larger loss can be kept as learner, compatibility, or preview functionality,
   but not as the promoted performance path.
3. If a new path is 10 to 20 percent slower but materially easier to use, it
   may be accepted only as an opt-in path with explicit performance wording
   that points to the faster path. It must not replace the benchmark row.
4. If a new path is more than 20 percent slower, it is not a performance path
   unless there is a specific and reviewed reason, such as debugability,
   portability, or missing hardware support.
5. Triton or Numba must not replace OptiX RT traversal for RT-core claims.
   Native OptiX/librtdl remains responsible for GAS-backed `optixTrace`
   traversal. Partners own preparation, typed buffers, continuation,
   reductions, compaction, and finalization around RTDL primitives.
6. All performance reports must split setup, scene build, transfer, query
   preparation, RT traversal, continuation/reduction, materialization, and
   download whenever those phases exist.
7. No app-specific semantics may enter the native engine to recover
   performance. If performance requires specialization, first express it as a
   generic primitive or partner continuation contract.

## v2.4: Partner-Ready Runtime Cleanup

v2.4 should not start by adding a new partner. It should first remove the
runtime debts that would make a Triton or Numba partner app-specific, fragile,
or slower than the current benchmark basis.

### Goals

1. Stabilize typed host/device buffer descriptors.
   The descriptor needs dtype, shape, stride, ownership, lifetime, device id,
   stream, mutability, alignment, and output-capacity semantics. It should
   support DLPack and CUDA array interface style handoff where available, but
   must not require a specific partner library.

2. Stabilize prepared sessions.
   A prepared session should separate reusable scene/table descriptors,
   reusable query buffers, reusable output buffers, and per-run payloads. This
   is the mechanism that made RayDB much faster after prepared query work, and
   it must become a general runtime concept.

3. Standardize segmented and chunked row streaming.
   Dense row-heavy apps such as triangle counting, RT-DBSCAN, contact witness,
   and fixed-radius workloads need CSR-style offsets, chunk ids, fail-closed
   overflow behavior, and bounded materialization contracts.

4. Define partner continuation primitives without naming CuPy, Triton, Numba,
   or app domains.
   Candidate contracts include segmented count/sum/min/max, compact/filter,
   bounded collect finalize, top-k or ranked summary, grouped candidate
   argmin, grouped union, and aggregate-frontier continuation.

5. Make phase timing mandatory for benchmark reports.
   Every benchmark row should clearly identify whether the number is traversal
   only, prepared query, continuation included, or whole app. This prevents a
   friendlier path from hiding slow Python work behind a fast RT traversal.

6. Audit native-engine vocabulary.
   Native engines should expose generic primitive names and generic descriptors.
   Benchmark apps may use domain names such as DBSCAN, RayDB, contact, or
   Barnes-Hut in Python, but native symbols should not.

7. Preserve CuPy as a compatibility and conformance partner, not the long-term
   primary ease-of-use story.
   CuPy is useful today, especially for RawKernel-friendly experiments, but
   RawKernel strings are too close to asking users to write CUDA kernels by
   hand. The v2.4 contracts should make CuPy optional, not central.

### Deliverables

- A runtime-level typed buffer protocol and conformance tests.
- A prepared-session protocol used by at least RayDB plus two additional
  benchmark apps.
- A segmented/chunked row streaming protocol with fail-closed overflow tests.
- A partner continuation protocol with no partner-specific naming.
- A benchmark regression runner that can compare current best paths against
  new partner-ready paths.
- Updated partner documentation explaining `Python + RTDL` and
  `Python + partner + RTDL` without implying arbitrary partner-program
  acceleration.

### Exit Gate

v2.4 is done only when the 10 promoted benchmark apps still retain their
accepted RT-vs-Embree basis, and any new partner-ready path is labeled as one
of:

- promoted performance path;
- optional compatibility path;
- learner/preview path;
- rejected for performance or boundary reasons.

## v2.5: Triton-First Partner, Numba Secondary

v2.5 should introduce the first new high-level partner path. The recommended
first target is Triton. Numba should be secondary or exploratory.

### Why Triton First

Triton is the better first v2.5 target because it is designed for GPU tensor
kernels, integrates well with PyTorch-owned data, avoids requiring users to
write CUDA C++ or CuPy RawKernel strings, and can express the reductions,
compaction, tiling, and row-finalization work that currently causes partner
friction.

Triton should not be treated as a replacement for OptiX. The intended pipeline
is:

```text
Python app
  -> partner prepares typed columns
  -> RTDL/OptiX performs RT-core traversal through generic primitives
  -> Triton performs generic continuation/reduction/finalization
  -> Python consumes compact results
```

### Why Numba Second

Numba is attractive because it keeps the user in Python syntax and may be easier
for some users to approach. It should be explored after the buffer and
continuation protocol is stable, because its performance and deployment profile
are less predictable for the high-throughput segmented GPU continuation work
that currently matters most.

### Initial Triton Partner Scope

The first Triton adapter should implement only generic continuation work around
RTDL results:

- compact/filter/mask columns;
- segmented count and sum;
- segmented min/max where needed;
- bounded collect finalization;
- grouped candidate argmin or top-k;
- row-stream chunk finalization;
- simple component/frontier helpers where the contract is generic.

The first Triton partner must not add RayDB-specific, DBSCAN-specific,
Barnes-Hut-specific, graph-specific, or collision-specific native engine logic.

### Candidate App Pilots

| App | Triton/Numba opportunity | Performance guard |
| --- | --- | --- |
| RayDB-style grouped aggregate | Query/payload preparation and grouped finalization around prepared RT traversal | Must preserve the prepared-query OptiX advantage over Embree; no whole-DB claim. |
| RT-DBSCAN-style | Core thresholding, adjacency chunks, component continuation | Must not introduce DBSCAN-native engine ABI. |
| Triangle counting | Segmented/chunked row streaming and summary finalization | Must not replace the RT-core triangle-count path with a pure GPU graph kernel for RTDL claims. |
| Barnes-Hut | Aggregate-frontier continuation and app-owned force reduction | Force math remains app/partner code, not engine code. |
| Bounded contact witness | Candidate filtering and bounded witness finalization | No contact/collision native ABI. |

### v2.5 Exit Gate

v2.5 should not claim success just because a Triton or Numba adapter exists.
The exit gate should require:

- at least three promoted benchmark apps with a Triton partner path;
- each promoted Triton path either improves the current best path or stays
  within the accepted performance tolerance;
- no accepted v2.3 benchmark row regresses without an explicit replacement row;
- no native engine app-specific vocabulary added for the partner path;
- a user-effort comparison showing fewer custom kernel lines, no C++ build, no
  CuPy RawKernel requirement, and a clear time-to-first-working-example
  improvement.

## Non-Goals

- v2.4/v2.5 are not a promise that RTDL accelerates arbitrary PyTorch, CuPy,
  Triton, or Numba programs.
- v2.4/v2.5 are not a promise that every whole app becomes faster.
- Triton/Numba partner work must not be used to weaken the RT-core requirement.
- Convenience paths must not be promoted over faster RTDL paths without clear
  labeling and review.

## Recommended Immediate Next Work

1. Freeze this roadmap after 3-AI review.
2. Add a small partner-protocol design doc for typed buffers, prepared sessions,
   and generic continuations.
3. Implement the v2.4 typed buffer/session layer in a narrow slice, starting
   with RayDB plus one row-heavy app and one bounded-collection app.
4. Add a regression runner that reports current best path vs partner-ready path
   for every promoted benchmark app.
5. Start Triton only after the protocol is stable enough that Triton is an
   adapter, not a set of app-specific scripts.

## Codex Position

Codex recommends this ordering:

```text
v2.4 = performance-preserving protocol cleanup.
v2.5 = Triton-first partner.
Numba = exploratory secondary partner after the protocol is stable.
```

The reason is pragmatic: current RTDL evidence is strong because OptiX beats
same-contract Embree across the promoted benchmark portfolio. The next partner
should reduce user effort around preparation and continuation, but the default
performance path must continue to use RT cores where the benchmark evidence
depends on RT cores.
