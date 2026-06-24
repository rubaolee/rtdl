# Goal1255 Codex Roadmap: v1.1 through v1.5

Date: 2026-05-04

Author: Codex

Status: accepted by 3-AI consensus

## Purpose

This document narrows the post-v1.0 roadmap. RTDL v1.0 is released as the
app-shaped proof release. The next work should not jump directly into a broad
v2.0-style ecosystem rewrite. It should move through a controlled v1.1-v1.4
sequence that prepares v1.5 generic primitives while improving the only active
performance lane: Embree plus NVIDIA OptiX.

## Controlling Decisions

1. v1.5 remains the generic traversal-plus-reduction primitive target accepted
   by Goal1042 and Goal1227.
2. v1.1-v1.4 are the preparation and migration ladder toward v1.5.
3. Before v2.1, RTDL should not spend implementation effort on Vulkan, HIPRT,
   or Apple RT. Their existing proof surfaces stay documented and preserved,
   but they are not active roadmap targets.
4. The active backend lane is Embree and OptiX.
5. NVIDIA RT performance is the top priority. Embree remains the CPU RT
   baseline, fallback, and same-contract comparison engine.
6. Public claims remain bounded by reviewed exact sub-path evidence. Faster
   engineering results do not become public wording until reviewed.

## Why This Scope Is Correct

v1.0 already proved that RTDL can express app-shaped non-rendering workloads and
connect them to real RT-capable backends. The remaining problem is not proving
that every vendor backend can run some path. That is already sufficient for the
foundation release. The next problem is that the NVIDIA OptiX path must become
faster, less app-specific, and easier to reason about against Embree.

Vulkan, HIPRT, and Apple RT work can resume later, but touching them now would
dilute the main release goal. The highest-value path is to make OptiX/RTX
performance compelling for the app sub-paths that v1.0 already made visible.

## v1.1: Post-Release Hardening And Performance Triage

### Goal

Make `main` a clean post-v1.0 development base and identify the exact OptiX
performance targets for v1.2.

### Work

- Keep release docs, tutorials, front page, app docs, and support matrices
  aligned with `v1.0`.
- Fix user-facing command defects found by fresh-clone sanity checks.
- Preserve source-tree usage until packaging metadata is intentionally added.
- Build a short OptiX-vs-Embree triage list from the current app inventory:
  reviewed fast rows, blocked rows, not-reviewed rows, and rows where the
  baseline contract is still weak.
- Prioritize same-contract timing for:
  `graph_analytics`, `polygon_pair_overlap_area_rows`,
  `database_analytics`, and `polygon_set_jaccard`, plus any reviewed rows whose
  public wording depends on fragile evidence.
- Document which v1.0 native continuations are performance-critical and which
  are only historical proof machinery.

### Exit Criteria

- Fresh clone of `main` and `v1.0` has truthful first-run instructions.
- A current Embree/OptiX performance triage report exists.
- Every candidate v1.2 optimization has an app, sub-path, baseline, command,
  and success metric.
- No Vulkan, HIPRT, or Apple RT implementation scope is added.

## v1.2: NVIDIA OptiX Performance Push

### Goal

Improve or explain OptiX performance against Embree for the highest-priority
v1.0 app sub-paths.

### Work

- Focus on prepared OptiX execution, batching, data layout, launch overhead,
  compact summaries, and host/device transfer boundaries.
- For blocked rows, determine whether OptiX is genuinely slower than Embree or
  whether the current path is dominated by avoidable setup, transfer,
  materialization, or Python continuation overhead.
- For not-reviewed rows, produce same-contract Embree and OptiX evidence before
  any public wording proposal.
- Keep row-returning and compact-summary modes separate. Do not use compact
  summary timing to claim row-output speedup.
- Keep Python continuation timing separate from native traversal timing.

### Exit Criteria

- Each prioritized app has one of these outcomes:
  `optix_improved`, `optix_still_slower_with_reason`,
  `baseline_contract_incomplete`, or `not_worth_v1_2`.
- Any public wording promotion candidate has a review packet, not just raw
  timing.
- Embree remains the comparison baseline; OptiX is not compared against a weak
  or mismatched CPU path.
- No non-NVIDIA backend work is added.

## v1.3: Primitive Contract And Lowering Matrix

### Goal

Turn the accepted v1.5 direction into implementable contracts without rewriting
the engine broadly.

### Work

- Write the primitive ABI contract for the Goal1042 primitive set:
  `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`,
  `REDUCE_INT(COUNT|SUM)`, and experimental `COLLECT_K_BOUNDED`.
- Define geometry schemas, payload schemas, result shapes, grouping semantics,
  overflow behavior, tolerance rules, and deterministic fallback behavior.
- Write a per-app lowering matrix mapping current v1.0 app endpoints to v1.5
  primitive calls.
- Define migration gates for each app-specific native continuation.
- Define exactly which claims survive migration and which claims must be
  re-reviewed.
- Write the public wording contract for generic primitive support, making clear
  that primitive availability is not automatic public speedup wording.

### Exit Criteria

- Primitive ABI and app-lowering matrix are externally reviewed.
- Public wording contract for generic primitive support is externally reviewed.
- The first migration slice is selected.
- Retirement gates are explicit: correctness parity, result-shape parity,
  performance parity or accepted overhead, fallback behavior, and preserved
  public claim boundaries.
- The active implementation scope remains Embree plus OptiX.

## v1.4: Compatibility Wrapper And First Migration Slice

### Goal

Implement the smallest useful v1.5 migration slice behind compatibility wrappers
while keeping v1.0 behavior intact.

### Work

- Implement `ANY_HIT` and `COUNT_HITS` first for one already-proven geometry
  pair in Embree and OptiX.
- Route one or two prepared fixed-radius summary apps through the generic
  primitive wrapper while retaining the old v1.0 endpoint during comparison.
- Compare old-vs-new correctness, result shape, overflow behavior, and timing.
- Keep public docs conservative: generic primitive support is not automatically
  public speedup wording.

### Exit Criteria

- First generic primitive wrapper passes old-vs-new parity tests.
- Embree and OptiX both support the first slice.
- OptiX performance is not silently regressed.
- Old app-specific endpoints remain available until review accepts retirement.
- v1.5 scope can begin with evidence instead of hope.

## v1.5: Generic Traversal-Plus-Reduction Primitive Release

### Goal

Reduce app-specific native-engine technical debt while preserving v1.0 app
behavior and improving the NVIDIA RT performance story where possible.

### Stable Target Primitive Set

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`

### Experimental Only

- `COLLECT_K_BOUNDED`, after scalar primitives are stable and after bounded
  output-capacity behavior is reviewed.
- DLPack or zero-copy candidate/hit-buffer handoff only where schema, lifetime,
  stream, capacity, and fallback contracts are documented.

### Non-Goals

- No broad v2.0 compute partnership implementation.
- No magic Python compiler.
- No user-injected PTX/SPIR-V plugin as a stable public feature.
- No public whole-app speedup claims from generic primitive support alone.
- No Vulkan, HIPRT, or Apple RT implementation push before v2.1.

### Release Gate

v1.5 should not release until selected v1.0 app-specific endpoints have been
migrated or wrapped through generic primitives with:

- correctness parity under defined schema/tolerance;
- result-shape parity where rows or compact summaries are contractual;
- performance parity or explicitly accepted overhead;
- stable Embree fallback;
- OptiX timing that does not weaken the NVIDIA RT performance story;
- external review and consensus.

## v2.1 Backend Re-Opening Rule

Vulkan, HIPRT, and Apple RT should remain frozen for new implementation work
until v2.1 or later. Re-opening them should require a specific design reason:

- the Embree/OptiX v1.5 primitive model is stable;
- the backend can implement the same primitive ABI without special casing;
- there is a clear user or platform reason to invest;
- adding the backend does not distract from NVIDIA RT performance work.

Until then, existing Vulkan, HIPRT, and Apple RT docs remain historical/current
support documentation, not active performance-roadmap commitments.

## Immediate Next Step

Before implementation, obtain external review of this v1.1-v1.5 sequencing and
the pre-v2.1 backend freeze. After external responses, produce a true 3-AI
consensus record. Do not claim 3-AI consensus before the external reviews are
available.
