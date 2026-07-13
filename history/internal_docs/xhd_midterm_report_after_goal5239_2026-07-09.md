# X-HD Midterm Report After Goal5239

Date: 2026-07-09

## Verdict

`midterm__level_b_single_workload_correctness_closed__performance_gap_exposed__full_paper_not_complete`

This report summarizes the X-HD paper-reproduction line after Goal5239.

The current position is strong but bounded:

```text
RTDL now matches the author rerun HDResult for one large same-source graphics
workload candidate:

  Dragon -> scaled AsianDragon
  source = 437,645 points
  target = 3,609,600 points
  RTDL route distance = 0.06536787240753439
  author scaled HDResult = 0.06536787003278732
  abs diff = 2.3747470656587666e-09
  matched = true
```

This is **not** full X-HD paper reproduction. It is a Level-B same-source
single-workload scalar-value reproduction against an author rerun on a public
candidate input. Exact paper input byte identity, Figure reproduction, and
author-performance parity remain open.

## Core Objective

The long-term objective remains:

```text
Build a Python/RTDL/partner implementation that can reproduce X-HD paper
results against the author's C++/CUDA/OptiX implementation, with correctness
and performance evidence under explicitly aligned phase/regime boundaries.
```

The project has two equally important goals:

1. **Paper app goal**: reproduce the X-HD paper to the greatest defensible
   extent, without pretending public reconstructed inputs are exact paper bytes.
2. **System goal**: convert reusable app discoveries into generic RTDL language
   and runtime capabilities, not X-HD-specific core shortcuts.

## Current Completion Level

### Level A: bounded same-input gates

Status:

```text
complete and externally reviewed
```

Completed evidence includes:

- author `hd_exec` build/run gates on tiny, bounded2D, and bounded3D fixtures;
- directed input1-to-input2 semantics disambiguated by an asymmetric fixture;
- RTDL public 2D/3D column routes matching author/exact bounded values;
- generic nearest pipeline extraction:
  `pairwise_l2_distance_candidate_rows -> nearest_witness -> max_nearest_distance`;
- non-Hausdorff consumer proof using facility-service-radius / worst-served demand.

Boundary:

```text
bounded same-input value reproduction only;
not X-HD RT-core algorithm reproduction;
not performance reproduction.
```

### Level B: same-source representative / public candidate

Status:

```text
partially complete for one major graphics workload:
Dragon -> scaled AsianDragon
```

Completed work:

- acquired Stanford graphics public inputs;
- built app-owned PLY loading and author-compatible preprocessing;
- identified that raw public AsianDragon scale is wrong for the paper log;
- created `asian_dragon_scaled_1e-3.ply`;
- showed author rerun on the scaled public candidate matches the paper-branch
  log within `1e-6`;
- ran bounded RTDL local and POD OptiX gates;
- ran a full all-source RTDL route-only gate;
- audited author source to prove PLY loader min-bound translation contract;
- built a same-POD performance matrix against the author rerun.

Boundary:

```text
single workload only;
same-source candidate only;
exact paper input byte identity unproved;
Figure 6 not reproduced.
```

### Level C: exact paper dataset reproduction

Status:

```text
not complete
```

Reason:

```text
The exact paper input files/hashes are not available in current evidence.
Public reconstructed/same-source inputs can match statistics or paper logs,
but statistics and near-matching scalar values are not file/hash provenance.
```

### Level D: performance / figure reproduction

Status:

```text
not complete
```

Goal5239 finally provides a denominator-explicit performance matrix for the
large Dragon -> scaled AsianDragon candidate. The result is correct but much
slower than the author.

## Evidence Chain

### Goals5110-5128: scaffold, bounded gates, and system extraction

These goals established the paper app scaffold, author provenance, bounded
same-input correctness gates, directed semantics, and generic nearest pipeline
system extraction.

Key design decision:

```text
Hausdorff is an app-level composition over generic nearest/witness/reduction
helpers. RTDL core does not gain an X-HD-specific primitive.
```

### Goals5129-5131: full-reproduction plan and dataset provenance

These goals reframed the task as a full-reproduction feasibility path:

- first extract paper targets and datasets;
- then classify exact / same-source / unavailable inputs;
- only then implement more routes.

The critical finding was:

```text
exact paper datasets are unavailable in current evidence;
Level-B same-source representative work is the honest next path.
```

### Goals5132-5136: Stanford graphics path

These goals acquired public Stanford Dragon/HappyBuddha inputs, added app-owned
PLY support, and established bounded sample correctness gates.

They also exposed that exact-reference all-pairs routes were not enough for
large performance reproduction, which motivated generic X-HD-style route work.

### Goals5137-5169: generic cell-MBR route and optimization track

These goals extracted and optimized generic RTDL capabilities:

- grid-cell MBR descriptors;
- nearest-state frontier splitting;
- native/OptiX 3-D AABB broadphase;
- native/OptiX 3-D cell-MBR frontier row producer;
- generic frontier nearest continuation;
- seeded nearest-cell-MBR initialization;
- vectorized and Numba executors;
- active-row-only native frontier emission.

This track is system work, not X-HD app customization. The route stayed
app-neutral at the RTDL layer and was consumed by the X-HD app.

### Goals5233-5239: Dragon -> scaled AsianDragon large workload

This is the current major midpoint.

#### Goal5234: scale discovery

Author rerun showed:

```text
raw public AsianDragon HDResult = 52.453487396240234
paper-log HDResult             = 0.06536811590194702
raw matched                    = false

scaled public AsianDragon HDResult = 0.06536787003278732
paper-log HDResult                 = 0.06536811590194702
scaled diff                        = 2.4586915969848633e-07
scaled matched                     = true
```

Interpretation:

```text
The public candidate must be scaled by 0.001 to match the paper-branch log
within 1e-6, but this still does not prove exact paper input byte identity.
```

#### Goal5236: current-source POD OptiX bounded gates

Current source was uploaded and rebuilt on POD:

```text
remote source root = /tmp/rtdl_goal5236
rebuilt library = /tmp/rtdl_goal5236/build/librtdl_optix.so
sha256 = e29f6b523530fa8a5e382f3bb2d64fc93f2f14868a9bf1b9005fde8c649ab1bb
```

Bounded OptiX routes for 256 and 1024 source points matched exact subset
oracles with `route_abs_diff=0.0`.

#### Goal5237: all-source RTDL route correctness

Passing mode:

```text
preprocessing = translate_each_input_to_min_bound
global_bound_early_break = false
source_count = 437,645
target_count = 3,609,600
frontier_row_capacity = 5,000,000
full_pairwise_rows_materialized = false
per_source_witness_exact = true
```

Result:

```text
RTDL route distance = 0.06536787240753439
author scaled HDResult = 0.06536787003278732
author_abs_diff = 2.3747470656587666e-09
matched = true
```

No-go diagnostics:

```text
without min-bound translation:
  matched = false
  route distance = 0.1597462345977575

with translation but global-bound early break:
  matched = false
  route distance = 0.06647010360490425
  per_source_witness_exact = false
```

This means:

```text
Exact scalar reproduction for this workload requires author-compatible PLY
min-bound translation and exact mode with global-bound early break disabled.
```

#### Goal5238: author PLY loader contract

Author source audit found:

```text
main.cpp:
  --input-type ply -> InputType::kPLY

run_hausdorff_distance.cu:
  points_a = LoadPLY(...)
  points_b = LoadPLY(...)

loaders/ply_loader.h:
  v[i] = (v[i] - vmin[i])
```

Therefore the successful RTDL `translate_each_input_to_min_bound` preprocessing
is not arbitrary normalization. It mirrors the author PLY loader's app-level
input contract.

#### Goal5239: same-POD performance matrix

Author measurement:

```text
process_wall_sec = 2.6587867364287376
internal Running.AvgTime = 83.49680000000001 ms
first_repeat_sum_RTTime = 81.019 ms
first_repeat_BVHBuildTime = 0.656 ms
first_repeat_grid_BuildTime = 1.51 ms
```

RTDL measurement:

```text
full_app_wall_sec = 31.252301812171936
route_direction_total_sec = 30.49027620255947
nearest_continuation = 28.124958105385303
frontier_rows = 3,306,122
candidate_distance_evaluations = 6,417,800,660
```

Diagnostic denominator-explicit ratios:

```text
RTDL full app wall / author process wall = 11.75434696735015x slower
RTDL route direction / author internal AvgTime = 365.1670028379467x slower
RTDL nearest continuation / author internal AvgTime = 336.83875436406305x
```

These are diagnostic ratios, not paper speedup/parity claims.

## Major Problems Solved

### 1. X-HD app provenance and bounded correctness

Solved:

- author repository and build route identified;
- bounded same-input gates run against author JSON;
- directed semantics proved by discriminating fixture;
- tolerance and comparator discipline established.

### 2. Hausdorff kept as app composition, not RTDL core identity

Solved:

- `directed_hausdorff_*` wrappers are now compositions over generic nearest
  helpers;
- non-Hausdorff consumer proves those helpers are not merely X-HD-shaped.

### 3. Public graphics data path

Solved for one workload:

- public Dragon / AsianDragon inputs acquired;
- scale mismatch identified;
- scaled public candidate produced;
- author rerun matches paper-branch log within `1e-6`;
- author PLY loader min-bound preprocessing audited and mirrored.

### 4. Full all-source route correctness for one large workload

Solved:

- RTDL route matches the author scaled-public HDResult for all source points;
- full pairwise row materialization avoided;
- per-source witness exactness retained in the passing exact mode.

### 5. Performance denominator clarity

Solved:

- author process wall and author internal `Running.AvgTime` are separated;
- RTDL full app wall and route timing are separated;
- no performance ratio is allowed without explicit denominator labels.

## Major Problems Not Yet Solved

### 1. Full paper reproduction is not complete

Still open:

- exact paper input byte identity;
- all paper datasets / all paper figures;
- full Table/Figure performance reproduction;
- exact author environment/hardware reproduction for all workloads.

### 2. Only one large Level-B workload is closed

The Dragon -> scaled AsianDragon result is important, but it is one workload.
It must not be summarized as broad Level-B completion across all X-HD paper
categories.

### 3. Performance gap remains very large

The bottleneck is not loading, grid MBR construction, frontier row production,
or max reduction.

Current dominant cost:

```text
nearest_continuation = 28.124958105385303s
```

The route performs:

```text
6,417,800,660 candidate distance evaluations
```

This is the real performance mountain.

### 4. Exact mode disables the attractive early-break shortcut

`global_bound_early_break=true` gives a faster-looking mode but is not exact:

```text
matched = false
per_source_witness_exact = false
```

Therefore it cannot be used for exact-value reproduction claims.

### 5. Generic continuation is correct but not fused enough

Current RTDL route:

```text
native/generic cell-MBR frontier rows
-> partner continuation over row tables
-> max-nearest reduction
```

Author route:

```text
fused RT radius-growth / pruning / payload-state iterations
```

The remaining gap is a real architecture gap, not a small Python I/O issue.

## Key Challenges

### Data provenance challenge

The public scaled Dragon -> AsianDragon candidate matches author rerun and
paper log closely, but exact paper bytes are still unproved. The same pattern
may repeat for other paper workloads.

### Algorithmic challenge

The author route prunes and updates nearest state inside a fused RT-style
iteration. RTDL currently lowers the route into a generic frontier table plus a
separate continuation. This preserves system cleanliness but costs too much.

### System-design challenge

Any performance fix must remain generic:

```text
allowed:
  generic nearest-continuation primitive
  generic fused point-to-cell-MBR nearest update
  generic row-buffer/device continuation API

forbidden:
  X-HD-only native primitive
  hard-coded Dragon/AsianDragon route
  app-specific paper shortcut in RTDL core
```

### Review / claim challenge

The reports must keep four statements separate:

1. author rerun match;
2. paper-log closeness;
3. exact input identity;
4. performance parity.

Only the first is strongly established for Dragon -> scaled AsianDragon.

## Current Claim Boundary

Allowed summary:

```text
For the Dragon -> scaled AsianDragon same-source public candidate, RTDL now
matches the author rerun HDResult in all-source route-only exact mode under the
author PLY loader min-bound preprocessing contract. The route is correct but
substantially slower; the dominant cost is nearest continuation.
```

Forbidden summaries:

```text
Full X-HD paper reproduction is complete.
Exact paper input byte identity is proved.
Figure 6 is reproduced.
RTDL matches author performance.
The result generalizes to all paper workloads.
Global-bound early break is exact.
RTDL has reproduced the author's fused RT-core algorithm.
```

## Next Work Plan

### Immediate next goal: Goal5240

Objective:

```text
Diagnose and, if safe, reduce the 28.1s nearest-continuation bottleneck.
```

Steps:

1. Inspect current `frontier_nearest_executor` implementations:
   `numba`, `numba_parallel`, and any vectorized/NumPy fallback.
2. Run a same-input all-source executor matrix on POD:
   - same Dragon -> scaled AsianDragon input;
   - same min-bound translation;
   - `global_bound_early_break=false`;
   - same author HDResult comparator;
   - no exact oracle full-pair materialization.
3. If `numba_parallel` or another existing generic executor wins while
   preserving exactness, promote it behind a conservative route flag.
4. If no existing executor wins, close Goal5240 as a no-go diagnostic and move
   to a new generic fused-continuation design.

Expected duration:

```text
0.5 to 1 POD session.
```

Exit labels:

```text
nearest_continuation_executor_win_promote_generic
nearest_continuation_executor_no_go__requires_fused_generic_primitive
```

### Next performance implementation goal: Goal5241 / Goal5242

Only if Goal5240 shows current executors are insufficient:

Objective:

```text
Design and implement a generic fused nearest-continuation primitive that moves
more nearest-state update work into a native/GPU-resident path without becoming
an X-HD-specific primitive.
```

Candidate scope:

- consume generic cell-MBR frontier rows;
- consume target cell point spans;
- update nearest witness per query;
- preserve deterministic tie-break semantics;
- expose metadata for candidate evals, pruning, and exactness;
- provide a non-Hausdorff consumer test.

Expected duration:

```text
1 to 3 focused goals, depending on whether the implementation can reuse the
existing native cell-MBR frontier ABI or needs a new native symbol.
```

### Correctness re-run goal: Goal5243

After any continuation change:

Objective:

```text
Re-run Dragon -> scaled AsianDragon all-source exact-value route and verify
the same author HDResult match.
```

Required:

- `matched=true`;
- `author_abs_diff <= 1e-6`;
- `per_source_witness_exact=true`;
- `global_bound_early_break=false`;
- denominator-explicit timing matrix refreshed.

Expected duration:

```text
0.5 POD session.
```

### Breadth goal: Goal5244

Objective:

```text
Decide the next paper workload after Dragon -> scaled AsianDragon.
```

Possible choices:

1. another Stanford graphics pair if paper logs / same-source candidates are
   available;
2. ModelNet40 or another public dataset if provenance is stronger;
3. stop broadening and attack exact-data provenance if no reliable candidate
   exists.

Expected duration:

```text
0.5 to 1 day, mostly provenance work.
```

### Review / checkpoint goal: Goal5245

Objective:

```text
Bundle Goals5233-5244 for strict external review.
```

Review should decide:

- whether the Level-B single-workload claim is correctly bounded;
- whether the performance bottleneck interpretation is right;
- whether the next mountain is continuation fusion or data breadth.

Expected duration:

```text
one review packet after Goal5240 or after Goal5243, depending on whether a
performance change lands.
```

## Expected Path To Completion

The full X-HD project is not one remaining step. The realistic path is:

```text
Stage 1: close Dragon -> scaled AsianDragon correctness and performance
         diagnosis.  Status: correctness closed; performance diagnosis open.

Stage 2: reduce or explain the 28s nearest-continuation bottleneck using a
         generic RTDL system primitive.  Status: next immediate work.

Stage 3: repeat the Level-B workflow on at least one more paper-relevant
         workload family.  Status: not started.

Stage 4: if exact paper files/hashes become available, upgrade Level-B
         same-source evidence to Level-C exact-dataset evidence.  Status:
         currently blocked by provenance.

Stage 5: only after same-input, same-phase, same-hardware denominators align,
         produce any paper-level performance ratio or figure reproduction.
         Status: not authorized today.
```

## Schedule Estimate

Assuming POD access remains usable:

```text
Goal5240 executor diagnosis:
  same day / one POD session.

Goal5241-5243 generic continuation improvement and rerun:
  1-3 working days if the native API shape is small;
  longer if a new native fused traversal symbol is required.

Goal5244 workload-breadth / provenance decision:
  0.5-1 working day.

Next major review packet:
  after Goal5240 if no-go, or after Goal5243 if a performance change lands.
```

Risk:

```text
The performance gap may require an in-traversal/fused continuation primitive.
If so, it is a real RTDL language/runtime investment, not a RayJoin-style app
micro-optimization.
```

## Final Midterm Conclusion

The X-HD project has crossed an important correctness threshold:

```text
one large same-source graphics workload now matches the author rerun HDResult
with all sources and without materializing full pairwise rows.
```

But the project has not reached full paper reproduction. The next honest
technical battle is not another formatting or wrapper task. It is the
`nearest_continuation` mountain:

```text
28.1s in RTDL versus 83.5ms author internal AvgTime for the same candidate
matrix context.
```

The right next step is to attack that bottleneck as a generic RTDL continuation
problem, while preserving the paper-app boundary and refusing any claim of
full X-HD reproduction until exact data and broader workload evidence exist.
