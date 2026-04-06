# RTDL v0.2 Workload Scope Charter

Date: 2026-04-05
Status: accepted

## Purpose

This charter defines which workload families belong in RTDL v0.2, which are
experimental, and which are explicitly out of scope.

The point is to prevent v0.2 from becoming an accumulation of unrelated demos.

## Classification rule

A workload family belongs in **in_scope** for v0.2 only if all of the
following are true:

1. it fits RTDL’s candidate-generation plus refine/aggregation structure
2. RT candidate search is central to the workload’s computational advantage,
   not only a decorative framing
3. it has a plausible backend story on the current hardware base
4. it can be verified with a realistic correctness boundary
5. it strengthens RTDL as a language/runtime rather than only as a benchmark

A workload family belongs in **experimental** if it is plausible but not yet
strong enough to define the release.

A workload family belongs in **out_of_scope** if it currently requires
unsupported hardware, unclear semantics, or a much larger system commitment
than v0.2 can carry.

## Priority rule

Only one in-scope workload family may act as the release-defining v0.2
expansion at a time.

Other plausible families remain experimental until the flagship family is
closed end to end.

## In-scope workload family

### 1. Additional spatial filter/refine workloads

Status: `in_scope`

Examples:

- stronger `lsi`
- distance-threshold or nearest-filter workloads
- more general candidate-generation plus exact-refine geometric filters

Why:

- this is the closest legitimate expansion from the v0.1 RayJoin-centered
  base
- the semantics are still coherent with RTDL’s current runtime model
- Embree/OptiX/Vulkan stories remain understandable here

## Experimental workload families

### 2. Programmable counting/ranking kernels with geometric candidate structure

Status: `experimental`

Examples:

- rank/count kernels like the sorting demo
- deterministic hit-count style reductions
- compact non-join workloads where the RT structure is still central

Why:

- this broadens RTDL beyond joins without breaking the project’s identity
- but this category is too easy to abuse as a novelty-demo bucket if treated
  as core scope
- it remains experimental until one specific family proves it is central
  enough to RTDL

### 3. Ray/path/filter/count kernels beyond classic joins

Status: `experimental`

Examples:

- generalized ray/path counting
- scene-style filter workloads
- small geometric kernels that are not obviously “database” tasks

Why:

- these may be valuable, but they need stronger evidence that they belong to
  one coherent RTDL story

### 4. Small graph/geometric counting kernels

Status: `experimental`

Examples:

- graph-inspired counting kernels that use RT candidate search
- limited graph/geometric hybrids

Why:

- potentially exciting, but the conceptual bridge from v0.1 is weaker
- this can easily turn into “interesting demo sprawl” if not controlled

## Out-of-scope workload families

### 5. Full exact polygon overlay materialization

Status: `out_of_scope`

Why:

- this is still a much larger geometry-system commitment than v0.2 should
  absorb

### 6. Distributed or multi-GPU execution

Status: `out_of_scope`

Why:

- too large a systems jump relative to the current stack

### 7. Native AMD GPU backend

Status: `out_of_scope`

Why:

- no AMD hardware access for serious closure work

### 8. Native Intel GPU backend

Status: `out_of_scope`

Why:

- no Intel GPU hardware access for serious closure work

### 9. Arbitrary “AI-generated workload demos”

Status: `out_of_scope`

Why:

- this would erase scope discipline
- v0.2 must not become a miscellaneous demo release

## Explicit gray-area non-examples

These are **not in scope by default** unless a later charter revision proves
otherwise:

- sorting-like tasks justified only by geometric storytelling
- graph/geometric hybrids where RT candidate search is not clearly the central
  computational advantage
- scene-style novelty demos whose main value is surprise rather than RTDL
  language/runtime growth
- workloads that are mostly generic reduction/counting tasks with only a thin
  RT wrapper

## Entry criteria for adding a new in-scope family

A new workload family may move from experimental to in-scope only if:

1. one user-visible problem statement is written down
2. one correctness boundary is defined
3. one realistic backend story exists on current hardware
4. one concrete success metric is named
5. the family strengthens RTDL’s identity rather than diluting it
6. it is more central to RTDL’s identity than the next most plausible
   alternative family currently being considered

## Separate governance note

Generate-only mode is not a workload family and should not be governed by this
charter alone.

It remains a separate experimental product-mode effort under the Goal 107
gates.

## Recommended v0.2 execution consequence

This charter implies:

- Goal 110 should target the single in-scope family above
- Goal 111 remains a separate experimental product-mode effort until it proves
  real value
- performance work should support the chosen in-scope family, not roam freely
