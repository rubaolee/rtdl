# X-HD Midterm Report After Goal5216

Date: 2026-07-09

## Executive Summary

X-HD now has **one strong Level-B same-source representative workload**:
public Stanford Dragon -> HappyBuddha. It is **not** broad Level-B coverage of
the paper and it is **not** full paper reproduction.

Current strongest result:

```text
Workload: public Stanford Dragon -> HappyBuddha
Source points: 437,645
Target points: 543,652
Author re-run HDResult on public data: 0.12572988867759705
Paper-branch log HDResult:            0.12572969496250153
RTDL HDResult on public data:          0.12572988629271128

RTDL vs author re-run diff:            ~2.38e-9
Author re-run vs paper log diff:       ~1.94e-7

RTDL fresh route wall:              ~0.852s
RTDL full gate incl input load:     ~1.531s
RTDL explicit-warm measured route:  ~0.288s
```

This is meaningful representative evidence because the author binary re-run and
RTDL route agree on the same public same-source Dragon/HappyBuddha workload.
The author re-run itself differs from the pinned paper-branch author log by
`~1.94e-7`; that gap is consistent with the standing boundary that the public
files are not proved byte-identical to the author's paper input files.

The current RTDL route is also **exact-value-only** for this directed-Hausdorff
scalar. Goal5211's global-bound early break reports
`global_bound_early_break_count = 409376` out of `437645` sources
(`~93.5%`) and `per_source_witness_exact = false`. Therefore the scalar
directed-HD value is correctness-gated against the author re-run, but
per-source nearest witnesses are approximate for early-aborted sources and must
not be presented as exact X-HD witness output.

It is not Level-C exact paper dataset reproduction because the paper input bytes
from `/local/storage/shared/HDDatasets` are not available, no input hashes are
published, and public artifacts do not provide deterministic byte-identical
reconstruction provenance.

## Core Objective

The long objective remains:

```text
Build an X-HD paper reproduction app where RTDL/Python reproduces the paper
workloads and exposes which reusable RTDL system APIs were forced out by the
paper app.
```

The objective has two parts:

1. **Paper reproduction evidence.**
   Reproduce X-HD results at increasing evidence levels: bounded same-input,
   same-source representative, exact paper dataset, then figure/performance
   reproduction if denominator alignment is possible.

2. **RTDL system improvement.**
   Avoid building an X-HD-only app. Extract reusable nearest/witness/reduction,
   grid-cell, cell-MBR, frontier, and native traversal capabilities into RTDL.

## Evidence Levels

The project uses four levels:

```text
Level A: bounded same-input correctness
Level B: same-source representative reproduction
Level C: exact paper dataset reproduction
Level D: full paper figures / fair performance reproduction
```

Current status:

```text
Level A: complete and externally reviewed through Goal5126
Level B: one Dragon -> HappyBuddha representative workload implemented through
         Goal5216, review pending
Level C: blocked by missing exact input files / hashes / provenance
Level D: not started as full figure/performance reproduction
```

## Plan So Far

The X-HD line followed this sequence:

1. **Provenance scaffold.**
   Pin the paper, author repository, branches, author CLI, and JSON output
   contract. This established that no paper result was being claimed at the
   scaffold stage.

2. **Bounded same-input gates.**
   Build small author/RTDL comparison gates and prove the directed Hausdorff
   definition. Goal5126 added an asymmetric fixture proving author HDResult is
   directed input1 -> input2, not symmetric Hausdorff.

3. **System extraction.**
   Refactor Hausdorff into generic RTDL building blocks:

   ```text
   pairwise L2 candidate rows
   nearest witness
   max-nearest reducer
   grid-cell descriptors
   cell-MBR frontier rows
   nearest-state seed/frontier contracts
   native 3-D cell-MBR traversal/frontier helpers
   global-bound early break for max-nearest reductions
   ```

   Goal5128 added a non-Hausdorff consumer to prove the generic nearest pipeline
   was not merely X-HD in disguise.

4. **One representative public workload.**
   Bridge the author paper-log workload `graphics/dragon.ply` ->
   `graphics/happy_buddha.ply` to public Stanford Dragon/HappyBuddha PLY files.
   The public files match the author-log point counts. The author re-run on
   those public files is close to, but not identical to, the paper-branch log
   HDResult. This remains single-workload Level-B evidence, not broad Level-B
   coverage and not byte identity.

5. **Scalable route construction.**
   Replace infeasible materialized pairwise evaluation with a scalable generic
   grid/cell-MBR route:

   ```text
   public PLY matrix loader
   -> local-grid-cell seed
   -> native cell-MBR inline nearest traversal
   -> max-nearest reduction
   -> author HDResult comparator
   ```

6. **Route improvement and consolidation.**
   Several route-level improvements reduced the Dragon/HappyBuddha
   representative route from multi-second route walls to the current `~0.852s`
   fresh route. The most important late change is Goal5211's generic
   global-bound early break for max-nearest / directed-Hausdorff reductions.
   This optimization preserves the exact directed-HD scalar value but makes most
   per-source witnesses approximate.

## Current Implementation Position

The current X-HD app route is:

```text
public Stanford Dragon points
public Stanford HappyBuddha points
-> app-owned public PLY NumPy matrix loader
-> generic grid/cell descriptors
-> generic local-grid-cell nearest-state seed
-> generic native 3-D cell-MBR inline-nearest traversal
-> optional generic global-bound early break
-> generic max-nearest reduction
-> app-owned author HDResult comparison
```

Current route ingredients:

```text
initial_state = local-grid-cell
max_inline_points = 512
global_bound_early_break = true
source_limits = all
source_subset_selection_contract = all_source_no_copy_view
```

Current representative evidence:

```text
Goal5186 author reference:
  author hd_exec HDResult = 0.12572988867759705
  paper-branch log HDResult = 0.12572969496250153
  author rerun vs paper log abs diff = 1.9371509552001953e-07
  author Running.AvgTime = 7.823 ms

Goal5212/5216 RTDL current route:
  matched author rerun HDResult = true
  RTDL distance = 0.12572988629271128
  RTDL vs author rerun abs diff = 2.3848857610975216e-09
  RTDL vs paper log abs diff ~= 1.9133e-7
  fresh route_wall = 0.8517371863126755s
  fresh full_total_including_load = 1.5306707620620728s
  explicit-warm measured route_wall = 0.2880803421139717s
  per_source_witness_exact = false
  global_bound_early_break_count = 409376 / 437645 (~93.5%)
```

## Completed Big Problems

### 1. Direction Semantics

The project no longer risks comparing symmetric Hausdorff against directed
Hausdorff. Goal5126 proved that the author binary computes directed
input1-to-input2 on a deliberately asymmetric fixture.

### 2. Bounded Correctness

Bounded same-input gates are complete and reviewed through Goal5126. RTDL can
match author JSON on controlled small inputs with explicit tolerance and
directed semantics.

### 3. System Extraction

Hausdorff is no longer treated as a monolithic system primitive. The route is
now expressed using generic nearest/witness/max-nearest, grid/cell, cell-MBR,
frontier, and native traversal contracts. The X-HD app owns paper wrappers and
comparators; RTDL owns reusable spatial/dataflow machinery.

### 4. One Public Representative Route

The full public Stanford Dragon/HappyBuddha route runs all sources against the
full target and matches the author re-run HDResult. This is the current
strongest representative reproduction evidence, but it is one directed graphics
workload, not broad Level-B coverage across the paper's MRI, geospatial, and
graphics workload families.

The route's large-scale correctness is author-agreement evidence. Independent
exact-reference agreement exists for small Level-A/bounded gates, but the full
`437645 x 543652` public workload does not materialize an independent exact
pairwise oracle.

### 5. Exact Dataset Blocker Clarified

The exact dataset blocker is no longer vague. Goals5214 and 5215 show:

```text
/local/storage/shared/HDDatasets is absent in the current POD;
author logs provide paths and HDResult metadata, not input bytes;
public GitHub branches track source/scripts/logs but no exact input datasets;
no hashes or deterministic reconstruction provenance are available.
```

### 6. Warm/Fresh Discipline

Warm route numbers are now explicitly separated. The current `~0.288s` warm
route is useful but cannot replace the `~0.852s` fresh route or the `~1.531s`
full gate including input load.

### 7. Exact-Value / Approximate-Witness Boundary

Goal5211's global-bound early break is valid for the directed-Hausdorff
max-nearest scalar, but not for exact per-source witness output. On the current
Dragon/HappyBuddha route:

```text
global_bound_early_break_count = 409376 / 437645 sources (~93.5%)
per_source_witness_exact = false
```

Therefore the supported large-route correctness claim is:

```text
RTDL matches the author re-run directed-HD scalar value on this public workload.
```

The unsupported claim is:

```text
RTDL reproduces exact per-source nearest witnesses for the full workload.
```

## Still-Unresolved Big Problems

### 1. Exact Paper Dataset Identity

This is the largest unresolved blocker.

The public Dragon/HappyBuddha pair is same-source representative evidence. It
is not proved byte-identical to the author's
`/local/storage/shared/HDDatasets/graphics` files.

To upgrade Level B to Level C, one of these is required:

```text
author input files;
author input hashes;
byte-identical converted point sets;
deterministic author conversion provenance from public sources.
```

Counts, names, public source family, and matching HDResult are not enough.

### 2. Full Figure Reproduction

The paper figures require more than one representative graphics workload. They
also include MRI and geospatial workload families. The paper-branch log index
covers many workloads, but without exact inputs the figures cannot be fully
reproduced.

### 3. Fair Performance Ratio

Current author and RTDL times are different denominators:

```text
author internal Running.AvgTime
author process wall
RTDL route wall
RTDL full gate including input load
RTDL explicit-warm measured route
```

No author-vs-RTDL performance ratio is authorized until dataset, hardware,
phase boundary, and runtime regime align.

### 4. Review Debt

Goals5211-5216 are implemented and documented, but external review is still
pending. They must not be presented as externally approved until review lands.

### 5. Full X-HD Algorithm Parity

The RTDL route is generic and reproduces HDResult on Level-B evidence, but it
is not a literal reimplementation of every author X-HD RT-core strategy. Full
algorithmic parity and figure-level claims remain future work.

## Key Challenges

### Dataset Provenance

This is not a coding problem. Without input files or hashes, exact paper dataset
claims would be dishonest.

### Denominator Alignment

Performance can be made misleading very easily. The project must continue to
report phase-separated timings and refuse ratios when denominators differ.

### Generic System Boundary

The temptation is to build X-HD-specific shortcuts. That remains forbidden.
Every system-level feature must be app-neutral and, where appropriate, have a
non-X-HD consumer or neutral contract.

### Warm-Route Framing

The warm route is real, but it is not the same as a fresh run. Reports must
always show preparation/warmup costs separately.

## Near-Term Plan

### Step 1: Strict Review Packet

Send the following for strict review:

```text
Goal5211: global-bound early break
Goal5212: all-source no-copy selection
Goal5213: initial-state matrix no-go
Goal5214: exact dataset availability refresh
Goal5215: public artifact availability sweep
Goal5216: Level-B representative consolidation
this midterm report
```

Expected result:

```text
Either approve Level-B representative packet,
or require amendments before it can become the stable X-HD handoff.
```

Estimated time:

```text
0.5-1 review cycle
```

### Step 2: Same-POD Performance Matrix

If review asks for clearer performance framing, run a same-POD matrix that
separates:

```text
author internal Running.AvgTime
author process wall
RTDL fresh route wall
RTDL full gate including input load
RTDL explicit-warm measured route
RTDL warmup/preparation cost
```

This should still avoid a ratio unless denominators can be aligned.

Estimated time:

```text
1 goal
```

### Step 3: Level-B Handoff Stabilization

If review approves:

```text
freeze current Level-B summary;
mark current route as Level-B representative, not Level-C exact;
document allowed and forbidden claims in README / manifest / register;
stop route micro-optimization unless new generic evidence appears.
```

Estimated time:

```text
1 goal
```

### Step 4: Level-C Dataset Acquisition Gate

Continue full paper reproduction only if exact input evidence appears:

```text
author provides input files;
author provides hashes;
public dataset reconstruction can be proven byte-identical;
or a deterministic conversion pipeline can be pinned and verified.
```

If none appears, the honest status remains:

```text
one-workload Level-B representative reproduction complete;
Level-C exact paper reproduction blocked.
```

Estimated time:

```text
unknown; depends on external dataset/provenance availability
```

### Step 5: Figure / Performance Reproduction

Only after Level-C is unblocked:

```text
map exact inputs to paper figures;
run author and RTDL on the same machine / same inputs;
separate internal time, process wall, route wall, load/setup costs;
report ratios only when denominators align.
```

Estimated time after data availability:

```text
3-7 focused goals for first figure family;
more for full Figure 5-11 coverage.
```

## Expected Completion Path

The likely path is:

```text
Now:
  review and stabilize the one-workload Level-B representative packet.

Next:
  optional same-POD performance matrix for clearer phase boundaries.

Then:
  wait for or acquire exact dataset provenance.

If exact data appears:
  promote selected workloads to Level-C and begin figure reproduction.

If exact data does not appear:
  close the current phase as one Level-B representative workload plus system
  extraction, while recording exact-paper reproduction as blocked by data.
```

## Current Claim Boundary

Allowed:

```text
RTDL has one Level-B same-source representative X-HD workload on public Stanford
Dragon -> HappyBuddha. The RTDL route matches the author binary re-run on that
public data to `~2.38e-9`. The author re-run differs from the paper-branch log
by `~1.94e-7`, so this must not be described as RTDL matching the paper log or
as exact paper dataset reproduction. The current RTDL fresh route wall is about
0.852s, full gate including input load is about 1.531s, and explicit-warm
measured route wall is about 0.288s with warmup reported separately. The
global-bound route is exact for the directed-HD scalar but has approximate
per-source witnesses for early-aborted sources.
```

Not authorized:

```text
full X-HD paper reproduction is complete;
exact paper dataset reproduction is complete;
author-vs-RTDL performance ratio;
author parity;
warm-only headline;
X-HD-specific RTDL primitive claim;
exact paper figure reproduction.
```

## Bottom Line

The project has achieved a real and useful milestone:

```text
one Level-B representative X-HD workload plus meaningful generic RTDL system
extraction.
```

It has not achieved:

```text
full X-HD paper reproduction.
```

The remaining blocker is not primarily implementation. It is exact paper input
provenance and fair performance denominator alignment.
