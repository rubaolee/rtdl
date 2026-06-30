# Goal 107 RTDL v0.2 Critique And Rebuttal

Date: 2026-04-05
Status: complete

## Purpose

This report records the strongest objections to the proposed v0.2 roadmap and
the rebuttals that survived those objections.

The point is not to make the roadmap look smooth. The point is to stress it.

## Critique 1: “Broader workloads” is too vague

### Criticism

If “more workloads” is not sharply defined, v0.2 will become a dumping ground
for unrelated demos.

### Rebuttal

The roadmap only survives if v0.2 begins with a formal scope charter:

- in scope
- experimental
- out of scope

That is why Goal 108 is first.

## Critique 2: generate-only mode could become fake value

### Criticism

A code generator that emits unverified code is not a product. It is template
spam.

### Rebuttal

The roadmap therefore requires:

- a generate-only MVP
- then a generated-code verification goal

The output must be runnable and reviewable, not only syntactically generated.

## Critique 3: performance work could consume the whole release again

### Criticism

If performance remains a standing obsession, v0.2 will again collapse into
backend-specific tuning and miss product expansion.

### Rebuttal

Performance is only one of three pillars in the roadmap, and it is explicitly
ordered *after* scope and generate-only mode.

That keeps performance important without letting it dominate the release.

## Critique 4: AMD/Intel absence weakens the roadmap

### Criticism

If v0.2 still centers NVIDIA hardware, it risks looking vendor-bound.

### Rebuttal

The honest answer is that unsupported hardware promises are worse than vendor
asymmetry.

So the roadmap keeps:

- OptiX as primary real GPU performance path
- Vulkan as portable backend
- AMD/Intel native backends deferred until hardware is available

## Critique 5: non-join kernels may dilute RTDL’s identity

### Criticism

RTDL may become conceptually messy if it mixes spatial-join and non-join
examples without a strong theory.

### Rebuttal

The common thread is not “join.” The common thread is:

- non-graphical ray-tracing kernels
- hierarchical candidate generation
- exact refine or deterministic aggregation

That is a coherent identity if the scope charter is explicit.

## Critique 6: the roadmap lacks a single user-visible win

### Criticism

If v0.2 cannot name one primary user and one release-defining win, it will
sound strategic but execute diffusely.

### Rebuttal

The roadmap therefore now names:

- one primary user:
  - advanced technical users who want to express one non-graphical RT kernel
    without first hand-writing backend-specific implementations
- one release-defining bet:
  - close one additional workload family beyond the v0.1 RayJoin-centered
    slice

## Critique 7: codegen should not be co-equal with workload expansion

### Criticism

Generate-only mode is too risky to be treated as a co-equal release pillar.

### Rebuttal

The roadmap now demotes code generation to a constrained secondary bet:

- one kernel family
- one output contract
- explicit kill criteria if the output is not genuinely useful

## Surviving roadmap position

After criticism, the roadmap still stands, but only in this stricter form:

- start with scope discipline
- make workload expansion the release-defining bet
- keep generate-only mode constrained and killable
- broaden workloads selectively, not theatrically
- keep performance work tied to real hardware evidence
- defer unsupported native GPU promises

## Final recommendation

The roadmap is promising, but only under a disciplined reading.

The strongest failure mode for v0.2 is not lack of ambition. It is loss of
scope discipline.
