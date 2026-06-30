# Goal 68 Vulkan Scalability Design Options

Date: `2026-04-04`

## Purpose

This memo defines the next credible Vulkan scalability directions after the
rejected Goal 67 tiling proposal.

## Constraints

Any accepted next Vulkan design must:

- preserve the current accepted correctness boundary
- avoid dead GPU work
- avoid recomputing the full Cartesian exact `lsi` space on the host when the
  GPU has already done candidate traversal work
- preserve explicit memory guardrails
- remain honest that Vulkan is still provisional until a larger package is
  actually closed

## Option 1: Candidate-only GPU output

### Idea

The GPU emits only candidate pair ids such as:

- `left_id`
- `right_id`

Final exact intersection points are computed only for those candidates on the
host.

### Pros

- immediately removes the full-final-row GPU output contract
- aligns GPU work with the actual host exact refine stage
- simpler than a full two-pass redesign

### Cons

- still needs a bounded candidate-output strategy
- may still overflow on large dense candidate sets if done in one monolithic
  pass

## Option 2: Count-then-materialize two-pass traversal

### Idea

Use two GPU passes:

1. count candidate hits
2. allocate exact candidate output size and materialize only the needed rows

Then refine those candidates exactly on the host.

### Pros

- strongest long-term output-capacity design
- avoids conservative over-allocation
- most defensible path for larger packages

### Cons

- highest implementation complexity
- requires more intrusive pipeline and buffer-management changes
- not the best first repair if the goal is the next realistic engineering step

## Option 3: Chunked candidate/refine pipeline

### Idea

Partition the build side into tiles.

For each tile:

1. run Vulkan traversal
2. read back real candidate rows
3. refine only those candidates exactly on the host
4. append final exact rows

### Pros

- preserves explicit bounded memory use
- turns chunking into semantically real work instead of dead work
- much easier to land in the current codebase than a full count/materialize
  redesign
- likely the best next step for the current repo

### Cons

- still not the cleanest long-term architecture
- host exact refine remains in the loop
- may still need dedup/order handling across chunks

## Recommended Next Direction

The recommended next implementation direction is:

**Option 3 first: chunked candidate/refine pipeline**

Reason:

- it is the first design that actually addresses the current problem honestly
- it reuses the current accepted correctness model
- it can reduce the large-package allocation cliff without pretending Vulkan is
  already a strong standalone exact backend

## What Should Not Be Done

Do not revive the rejected Goal 67 design:

- tiled traversal that discards GPU rows
- followed by full host-side exact Cartesian recomputation

That path does not produce a credible maturity improvement.
