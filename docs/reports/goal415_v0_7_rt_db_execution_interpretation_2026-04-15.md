# Goal 415 Report: v0.7 RT DB Execution Interpretation

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_415_v0_7_rt_db_execution_interpretation.md`
Inputs:
- `/Users/rl2025/Downloads/2024-rtscan.pdf`
- `/Users/rl2025/Downloads/2025-raydb.pdf`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal412_rt_db_workload_analysis_for_next_version_2026-04-15.md`

## Question

What should RTDL's DB kernels mean operationally before any RT backend
implementation is claimed?

## Executive answer

The current `v0.7` DB family must be interpreted as **bounded analytical RT
workloads with separate semantic and RT execution layers**.

That means:

- `cpu_python_reference`, `cpu`, and `postgresql` define correctness
- Embree, OptiX, and Vulkan will only be valid after they implement an explicit
  RT candidate-discovery contract
- RTDL is not turning database queries into arbitrary ray tracing by analogy;
  it is defining a bounded family of query shapes that can be lowered into RT
  traversal plus bounded refine/merge work

## Current honesty boundary

Today the DB family has three kinds of engines:

1. semantic truth
   - `cpu_python_reference`
2. bounded native oracle
   - `cpu`
3. external correctness anchor
   - `postgresql`

None of them are RT engines yet.

This is acceptable so far because the system first needed:

- kernel syntax
- data objects
- semantic closure
- native bounded oracle
- PostgreSQL-backed correctness

It is not acceptable to claim Embree/OptiX/Vulkan support until RTDL defines
what an RT execution of these kernels actually is.

## Meaning of the DB inputs

### `DenormTable`

`DenormTable` means:

- a bounded flat record array
- already denormalized or pre-joined
- with typed scalar columns that can be:
  - encoded into RT coordinates
  - or stored as payload/refine attributes

It does not mean:

- a live database table
- a query planner input
- a transactional table abstraction

### `PredicateSet`

`PredicateSet` means:

- a bounded conjunctive filter over scalar columns
- first-wave forms:
  - equality
  - closed/open ranges
  - conjunction only

It does not mean:

- arbitrary boolean logic
- general disjunction
- nested subqueries

### `GroupedQuery`

`GroupedQuery` means:

- one bounded grouped analytical query
- built from:
  - a `PredicateSet`
  - one group key
  - one supported aggregate kind

It does not mean:

- arbitrary SQL grouping semantics
- multi-stage analytic plans
- arbitrary expression trees

## Meaning of the execution stages

### Build

For the DB family, `build` means:

- choose a bounded RT layout for the kernel family
- encode selected scalar columns into RT coordinates
- attach exact scalar payload needed for refine and output
- build a backend-specific acceleration structure over those primitives

Build is closer to:

- preparing a workload-specific RT index

and not:

- building a general database index hierarchy

### Probe

`probe` means:

- convert a `PredicateSet` or `GroupedQuery` into bounded query metadata
- choose which clauses are handled by RT candidate discovery
- prepare remaining exact refine checks
- prepare ray-launch parameters for the chosen layout

### Traverse

`traverse(..., mode=\"db_scan\")` means:

- use RT traversal to find candidate rows in the spatially encoded query region

`traverse(..., mode=\"db_group\")` means:

- use RT traversal to find candidate rows and emit bounded grouped partials

In both cases, the RT part is first and foremost:

- candidate discovery over a pre-built RT structure

### Refine

`refine` means:

- exact scalar clause checking for any scan conditions not fully captured by the
  primary RT coordinates
- exact payload decoding where needed
- bounded host-side or shader-side confirmation

This follows the RTScan/RayDB pattern:

- RT narrows the work
- exactness comes from bounded refine logic

### Emit

For `conjunctive_scan`, `emit` returns:

- row ids
- or bounded projected rows later if RTDL adds projection

For grouped kernels, `emit` returns:

- grouped partials
- or final grouped rows after bounded merge

## First-wave support interpretation

The first RT backend wave should mean:

- `conjunctive_scan`
  - RT-driven candidate discovery
  - exact refine
  - row-id emit
- `grouped_count`
  - RT-driven candidate discovery
  - bounded grouped partial accumulation
  - bounded merge
- `grouped_sum`
  - same as `grouped_count` with exact numeric accumulation

The first wave should not mean:

- full query plans on RT cores
- online joins
- `having`
- `order by`
- arbitrary `group by` arity

## Execution split across engine families

### Semantic engines

Python truth, native oracle, and PostgreSQL all execute the full kernel
semantics directly.

They are used to answer:

- what the query means
- what exact rows or grouped results must be returned

### RT engines

Embree, OptiX, and Vulkan should execute only after the following split is
accepted:

- RT handles:
  - acceleration structure traversal
  - candidate discovery
  - bounded per-hit payload access
  - bounded partial emission/accumulation
- non-RT bounded logic handles:
  - exact refine for secondary clauses
  - partial merge
  - host-side decomposition for over-boundary cases

## Result

Goal 415 accepts the following interpretation:

- RTDL DB kernels are bounded analytical workload kernels
- current non-RT engines define correctness only
- future RT backends must implement candidate-discovery-style execution, not
  just another direct row scanner
- the first-wave DB family remains:
  - denormalized
  - conjunctive
  - grouped-analytical
  - bounded
