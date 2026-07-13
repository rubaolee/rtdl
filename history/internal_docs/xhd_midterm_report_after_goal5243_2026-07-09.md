# X-HD Full Paper Reproduction Midterm Report After Goal5243

Date: 2026-07-09

Status: midterm checkpoint, not full paper reproduction complete.

## 1. Objective

The working objective is:

```text
Reproduce the X-HD paper as fully as evidence permits, while preserving RTDL as
a general language/system rather than turning it into an X-HD-specific app
kernel.
```

This has two linked goals:

1. Paper-app goal:

```text
Build a durable X-HD paper reproduction app with author provenance, same-input
correctness gates, public-data representative workloads, and denominator-clean
performance evaluation.
```

2. Language/system goal:

```text
Extract reusable RTDL system capabilities from the app work: generic nearest
witness pipelines, grid-cell/MBB frontier traversal, native local-grid seed,
and eventually reusable prepared spatial workspaces.
```

## 2. Current Completion Level

### Completed / externally reviewed earlier

The bounded same-input line is complete:

```text
Goals5111-5126:
  author hd_exec JSON gate
  2-D/3-D bounded WKT fixtures
  directed-vs-symmetric HD semantic disambiguation
  RTDL exact public columnar route value match
```

The system extraction line is complete:

```text
Goals5127-5128:
  directed Hausdorff decomposed into app-level composition
  RTDL exposes generic nearest/witness/reduction helpers
  non-Hausdorff consumer validates the helpers as app-neutral
```

### Implemented, pending external review

The large same-source public graphics workload line is implemented through
Goal5243 but not yet externally reviewed as a batch:

```text
Goals5237-5243:
  Dragon -> scaled AsianDragon all-source route
  author rerun HDResult matched
  performance improved from 30.49s to 2.307s route_wall/direction scale
  continuation removed
  generic local-grid seed runtime compile removed
```

### Not completed

The following are not complete:

```text
full paper reproduction
exact paper byte-input identity
Figure 5-11 reproduction
multi-dataset paper target matrix
author internal Running.AvgTime parity
independent proof that public reconstructed data equals paper-input bytes
```

## 3. Evidence Summary

### Bounded correctness

Bounded same-input fixtures:

```text
author binary = hd_exec
variant = rt
RTDL route = public columnar/exact reference route
directed a->b semantics verified by asymmetric fixture
matched = true
```

Important boundary:

```text
This proves value agreement for bounded same-input fixtures.
It does not prove the author X-HD RT-core algorithm is reimplemented.
```

### Single large public workload

Current large workload:

```text
source = Dragon, 437,645 points
target = scaled AsianDragon, 3,609,600 points
direction = Dragon -> scaled AsianDragon
preprocessing = translate each input to min bound
author rerun HDResult = 0.06536787003278732
RTDL route distance = 0.06536787240753439
author_abs_diff = 2.3747470656587666e-09
matched = true
```

Critical caveats:

```text
This is one workload, not all paper categories.
The match is to author rerun on available public data, not exact paper log bytes.
It is exact-value for the directed HD scalar; it is not a claim that every
per-source witness is paper-equivalent across all variants.
```

## 4. Performance Evolution

Same workload, denominator-explicit:

```text
Goal5239 original RTDL all-source route:
  direction_total = 30.49027620255947s
  nearest_continuation = 28.124958105385303s

Goal5240 existing generic auto/numba_parallel continuation:
  direction_total = 9.171282961964607s
  nearest_continuation = 6.6945535987615585s

Goal5241 generic 96x60x72 grid + native CUDA local-grid seed:
  median direction_total = 3.0695155784487724s
  median route_wall = 3.322203427553177s
  median total_wall = 3.8200959116220474s

Goal5242 max_inline_points=1024:
  median direction_total = 2.8061167374253273s
  median route_wall = 3.059376485645771s
  median total_wall = 3.5552977472543716s

Goal5243 precompiled native local-grid seed:
  median direction_total = 2.3074675127863884s
  median route_wall = 2.3075230717658997s
  median total_wall = 3.056991830468178s
```

Improvement from Goal5239 to Goal5243:

```text
direction_total: 30.49027620255947s -> 2.3074675127863884s
improvement = 13.21x
```

Author denominator evidence:

```text
author process wall = 2.6587867364287376s
author internal Running.AvgTime = 83.49680000000001ms
```

Current labelled comparison:

```text
RTDL Goal5243 route_wall / author process wall = 0.868x
RTDL Goal5243 total_wall / author process wall = 1.150x
RTDL Goal5243 direction_total / author internal Running.AvgTime = 27.64x slower
```

Interpretation:

```text
RTDL is now in the same scale as the author's process-wall run for this one
public workload, and route_wall is below that process wall.

RTDL is still far from the author's internal timed-loop AvgTime.
```

## 5. Major Problems Solved

### 5.1 Correct HD semantics

The directed vs symmetric ambiguity is solved by a discriminating fixture:

```text
directed_a_to_b = 0.5
directed_b_to_a = 9.0
symmetric = 9.0
author HDResult = 0.5
```

This proves the author result is directed input1 -> input2 under that gate.

### 5.2 App/system boundary

Hausdorff is kept as an app-level composition. RTDL system assets are generic:

```text
pairwise_l2 candidate rows
nearest witness
max-nearest reduction
grid-cell MBR frontier
local-grid nearest seed
native OptiX/CUDA execution plumbing
```

No RTDL core primitive is named `xhd` or paper-author specific.

### 5.3 Public workload value match

The Dragon -> scaled AsianDragon author rerun value is matched:

```text
author_abs_diff = 2.3747470656587666e-09
```

### 5.4 Nearest continuation bottleneck

The original RTDL route spent about 28s in nearest continuation. That is now
removed:

```text
frontier_rows = 0
nearest_continuation ~= 0.00083s
```

### 5.5 Runtime seed module compile

Goal5243 removed runtime CUDA module compile/load from native local-grid seed:

```text
module_ensure_sec: 0.496675326s -> 0.0s
seed_native_total: 0.698966517s -> 0.202945411s
```

## 6. Major Problems Not Yet Solved

### 6.1 Exact paper data provenance

The current public-data workload is not proven to be the exact paper input byte
stream. The remaining paper-log mismatch is a dataset provenance signal.

Required discipline:

```text
matching statistics or point counts is not exact dataset identity
exact Level-C paper reproduction requires file/hash/provenance proof
```

### 6.2 Multi-workload coverage

The current large public result is one workload:

```text
Dragon -> scaled AsianDragon
```

It is not yet a full Level-B matrix across paper categories or multiple
graphics/medical/spatial datasets.

### 6.3 Author internal AvgTime gap

The current RTDL route is still much slower than the author internal
`Running.AvgTime` denominator:

```text
RTDL direction_total / author internal AvgTime = 27.64x slower
```

This denominator likely measures only the author's repeated internal RT-core
algorithm phase, not the same boundary as RTDL route_wall or total_wall.

### 6.4 Remaining RTDL route floor

After Goal5243:

```text
frontier phase ~= 1.31s
  frontier OptiX launch ~= 1.17s

grid_cell_mbr prep ~= 0.61s

local-grid seed outer ~= 0.35s
```

The next hard engineering questions are:

```text
Why does the native frontier/inline-nearest path cost ~=1.31s even with
frontier_rows=0?

Can target grid/device workspace be prepared and reused in a general RTDL API?

Does this route generalize beyond Dragon -> scaled AsianDragon?
```

## 7. Architecture Assessment

### What RTDL gained

The X-HD work has created and tested reusable system machinery:

```text
generic nearest/witness/reduction pipeline
generic public 2-D/3-D columnar Hausdorff wrappers as app composition
generic grid-cell MBR frontier path
generic local-grid seed path
generic precompiled CUDA helper packaging for OptiX backend
native phase timing hooks for seed/frontier decomposition
```

### What remains app-owned

Still app-owned:

```text
author hd_exec wrapper
paper data provenance
input-type and preprocessing contract
X-HD fixture selection
paper tolerance selection
performance denominator interpretation
claim boundary
```

### Was the app/system principle broken?

Current answer:

```text
No major break is visible. The latest performance work is generic local-grid
seed and grid/frontier machinery. It is used by X-HD, but not named after X-HD
and not restricted to Hausdorff.
```

Risk to keep watching:

```text
If future work hard-codes author X-HD grid growth, heavy-cell offload, or
paper-specific pruning into RTDL core, the principle would be broken. Those must
either be generic spatial operators or remain app-owned.
```

## 8. Next Work Plan

### Goal5244 - Frontier/Inline Nearest Phase Decomposition

Purpose:

```text
Break down the remaining ~=1.31s frontier phase.
```

Questions:

```text
Is the cost true OptiX traversal/payload work?
Is it acceleration build?
Is it per-query launch/state overhead?
Why is it large when emitted frontier_rows=0?
```

Exit:

```text
frontier_dominated_by_traversal
frontier_dominated_by_accel_build
frontier_dominated_by_payload_inline_nearest
frontier_not_attackable_without_fusion
```

Expected duration:

```text
one focused POD measurement goal
```

### Goal5245 - Generic Prepared Target Grid Workspace

Purpose:

```text
Convert repeated target-side grid structures into a prepared, reusable RTDL
workspace where product regime allows it.
```

Target phases:

```text
grid_cell_mbr prep ~=0.61s
part of seed upload/prep
part of frontier device upload/build
```

Boundary:

```text
generic target-grid workspace, not X-HD-specific state
```

Expected duration:

```text
one design/contract goal + one implementation/benchmark goal
```

### Goal5246 - Second Level-B Workload

Purpose:

```text
Test whether the current grid/threshold strategy generalizes.
```

Options:

```text
another public graphics pair from author logs if available
another paper-table public source where input provenance can be documented
```

Exit:

```text
route_generalizes_to_second_workload
route_is_workload_specific
blocked_on_dataset_provenance
```

Expected duration:

```text
one data-provenance goal + one benchmark goal
```

### Goal5247 - Author Denominator and Phase Boundary Audit

Purpose:

```text
Explain exactly what author process wall and author internal Running.AvgTime
include/exclude.
```

Reason:

```text
RTDL is near author process-wall scale for one workload, but still 27.6x behind
author internal AvgTime. The project cannot claim parity until the denominator
boundary is explicit.
```

Expected duration:

```text
one source audit + one same-POD timing run if needed
```

## 9. Expected Completion Path

Minimum honest next milestone:

```text
externally reviewed Level-B single-workload result:
  Dragon -> scaled AsianDragon
  author rerun value matched
  route_wall ~=2.31s
  exact caveats and denominators explicit
```

Preferred next milestone:

```text
two Level-B public workloads matched
frontier/grid workspace phases reduced or accepted as floor
author denominator boundary audited
```

Full paper reproduction remains conditional:

```text
exact paper input provenance available
Figure target matrix reconstructed
author/RTDL denominator aligned
algorithmic X-HD RT-core gap either implemented generically or honestly scoped
out
```

## 10. Allowed Summary

Allowed:

```text
RTDL now has a generic X-HD-relevant route that exactly matches the author
rerun HDResult on one large public Dragon -> scaled AsianDragon workload and
has improved from 30.49s to 2.31s route_wall/direction scale through generic
system work. This is a strong Level-B single-workload result, not full paper
reproduction and not author internal AvgTime parity.
```

Forbidden:

```text
X-HD full paper reproduction is complete
RTDL matches the paper log
RTDL reproduces Figure 5-11
RTDL has author internal performance parity
RTDL reimplemented the author X-HD RT-core
This result generalizes to all X-HD paper workloads
```
