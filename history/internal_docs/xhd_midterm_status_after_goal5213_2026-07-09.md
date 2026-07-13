# X-HD Midterm Status After Goal5213

Date: 2026-07-09

## Executive Summary

The X-HD line has reached a strong midterm point, but it is not yet a full
paper reproduction.

What is solid:

```text
Level A bounded same-input correctness is complete and externally reviewed.
Level B same-source public Stanford Dragon -> HappyBuddha correctness is
established against the author `hd_exec` HDResult.
The RTDL route has been repeatedly improved through generic system primitives,
not X-HD-specific core shortcuts.
```

Current strongest Level-B route-local evidence:

```text
dataset/regime = public Stanford Dragon -> HappyBuddha, all sources
author reference = Goal5186 author hd_exec HDResult
RTDL route = generic nearest pipeline + cell-MBR frontier + inline nearest
             + global-bound early break + all-source no-copy input selection
matched = true
fresh route wall ~= 0.852s
fresh case total ~= 0.852s
fresh full gate total including input load ~= 1.531s
explicit-warm measured route ~= 0.288s
```

What is not complete:

```text
exact paper dataset identity is not proved;
full X-HD paper reproduction is not complete;
author-vs-RTDL performance ratio is not authorized;
Goals5211-5213 are implemented but still review pending.
```

## Original Objectives

The workstream has two core objectives.

### Objective 1: Build a Paper Reproduction App

The app should reproduce X-HD paper behavior as far as evidence allows. The
completion levels are:

| Level | Meaning | Status |
|---|---|---|
| A | bounded same-input correctness against author binary | complete and externally reviewed through Goal5126 |
| B | same-source representative public-data route | implemented, strongest current line; review pending for latest route changes |
| C | exact paper dataset reproduction | blocked by dataset provenance / availability |
| D | full paper figures and performance | not complete; depends on C plus phase/hardware denominator alignment |

### Objective 2: Improve RTDL As A General System

X-HD is treated as an app and pressure test. Any durable RTDL improvement must
be generic:

```text
RTDL owns generic nearest / witness / reduction / spatial traversal primitives.
X-HD app owns author wrappers, fixtures, tolerances, comparator gates, data
provenance, and paper-specific claims.
```

This principle has mostly held. The major route work since Goal5127 has
improved or extracted generic system capabilities rather than embedding an
X-HD-only primitive in RTDL core.

## Completed Work

### Bounded Correctness And System Extraction

Completed and externally reviewed:

```text
Goal5110 scaffold / provenance
Goals5111-5126 bounded same-input X-HD value reproduction
Goal5127 generic nearest pipeline extraction
Goal5128 non-Hausdorff consumer proving extracted helpers are generic
```

Key outcomes:

```text
author HDResult is directed input1 -> input2, not symmetric;
RTDL bounded routes match author HDResult on 2D and 3D fixtures;
Hausdorff is represented as an app-level composition of generic primitives:
  pairwise L2 candidate rows
  nearest witness
  max-nearest reduction
the extracted max-nearest reducer has a non-Hausdorff facility-service-radius
consumer, so it is not only an X-HD helper in disguise.
```

### Level-B Public Stanford Evidence

The current representative line uses public Stanford graphics inputs:

```text
source = Dragon
target = HappyBuddha
source_limit = all
reference = Goal5186 author hd_exec HDResult
```

Major milestones:

| Goal | Main result |
|---|---|
| Goal5186 | author `hd_exec` full public Dragon -> HappyBuddha reference captured |
| Goal5187 | RTDL all-source route matches author HDResult |
| Goal5188 | phase-boundary matrix refuses invalid author-vs-RTDL ratio |
| Goal5189-5190 | seed strategy tests; local-grid remains better than grid-branch-bound |
| Goal5191 | inline frontier threshold raised; empty frontier passthrough |
| Goal5192 | telemetry shows real inline point-scan work |
| Goal5193 | bounded grid-cell seed no-go |
| Goal5194 | payload-current-best pruning in native inline nearest |
| Goal5195 | intersection-stage prune before `optixReportIntersection` |
| Goal5196 | dense encoded-cell lookup for seed helpers |
| Goal5197 | lazy row-only distance cleanup |
| Goal5198 | grid-shape matrix; keep 32^3 |
| Goal5199 | trace `tmax` no-go, reverted |
| Goal5200 | native CUDA seed no-go |
| Goal5201 | frontier phase timing |
| Goal5202 | packed coordinate matrix reuse |
| Goal5203 | app-owned NumPy matrix front door |
| Goal5204 | linear max-nearest reduction |
| Goal5205 | fast ASCII PLY matrix loader |
| Goal5206 | first-use vs same-process warm diagnostic |
| Goal5207 | explicit warmup protocol |
| Goal5208 | lower inline thresholds no-go |
| Goal5209 | static cell order no-go |
| Goal5210 | disable closest-hit flag; neutral cleanup |
| Goal5211 | generic global-bound early-break route win |
| Goal5212 | all-source no-copy selection |
| Goal5213 | heavier initial-state strategies no-go; keep local-grid |

## Performance Evolution

All numbers below are route-local or gate-local Level-B evidence on public
Dragon -> HappyBuddha, not a full paper performance comparison.

| Stage | Main regime | Route / total evidence |
|---|---|---:|
| early all-source route around Goal5187 | fresh route | several seconds; later optimized |
| Goal5191 | fresh route | ~= 3.65s |
| Goal5195 | fresh route | ~= 2.6s |
| Goal5196 | fresh route | ~= 2.26s |
| Goal5202 | fresh route | ~= 2.03s |
| Goal5203 | fresh route | ~= 1.24s |
| Goal5204/5205 | fresh route | ~= 1.16-1.18s |
| Goal5207 | explicit warm measured route | ~= 0.626s, warmup separately reported |
| Goal5211 | fresh route with global bound | ~= 0.849s |
| Goal5211 | explicit warm median route | ~= 0.362s |
| Goal5212 | fresh full gate after no-copy | route ~= 0.852s; total incl load ~= 1.531s |
| Goal5212 | explicit warm measured | route/case ~= 0.288s |

Interpretation:

```text
The largest route change is Goal5211: generic global-bound early break.
Goal5212 improves the app runner / full gate total by removing a pointless
all-source matrix copy; it is not a native route speedup.
Goal5213 confirms heavier initial states are not the next path.
```

## Solved Major Problems

### 1. App/System Boundary

X-HD no longer needs to be treated as an RTDL core primitive. The system now has
a generic nearest/witness/max-nearest pipeline, and X-HD is an app-level
composition.

### 2. Bounded Directed Semantics

The directed vs symmetric Hausdorff ambiguity has been closed with an
asymmetric fixture:

```text
directed a->b = 0.5
directed b->a = 9.0
symmetric = 9.0
author HDResult = 0.5
RTDL directed a->b = 0.5
```

### 3. Invalid Performance Ratios

The project now keeps separate:

```text
author internal Running.AvgTime / ReportedTime
author process wall
RTDL route time
RTDL full gate total
cold process
warm long-lived process
prepared/replay diagnostics
```

No author-vs-RTDL ratio is currently authorized.

### 4. Repeated Micro-Tuning Dead Ends

Several tempting directions have been tested and closed:

```text
lower inline threshold
static cell ordering
scalar trace extent / tmax
native CUDA seed wrapper
finer grid shapes
prepared accel build caching
heavier initial states under global bound
```

## Remaining Major Problems

### 1. Exact Paper Dataset Identity

This is the largest paper-reproduction blocker. The current Level-B line uses
same-source public Stanford data, not proven exact paper inputs. Count or
statistical similarity is not enough.

Needed evidence for Level C:

```text
actual paper input files, hashes, or author-provenance equivalence;
or an explicit conclusion that exact paper inputs are unavailable.
```

### 2. Full Paper Algorithm Reproduction

The current RTDL route is a correct generic route for the representative
dataset, but it is not necessarily the author X-HD RT-core algorithm. Remaining
algorithmic gaps may include:

```text
author grid grouping / radius growth details;
nearest-cell traversal strategy;
heavy-cell offload;
paper-specific adaptive behavior;
internal timing boundaries.
```

### 3. Review Debt

Goals5211-5213 are implemented and documented but not externally reviewed.
They should not be used as release claims until reviewed.

### 4. Exact Performance Denominator

Even for public data, author-vs-RTDL performance comparison still requires a
single aligned denominator:

```text
same data;
same phase;
same hardware;
same warm/cold regime;
same inclusion or exclusion of input load and setup.
```

## Goal5213 Result

Goal5213 tested whether, after global-bound early break, more expensive
initial-state strategies could unlock enough extra early breaking to beat
local-grid.

Result:

| initial state | matched | seed | route wall |
|---|---:|---:|---:|
| local-grid-cell | true | 0.219s | 0.852s |
| nearest-cell-mbr | true | 4.792s | 5.410s |
| grid-cell-budget | true | 6.671s | 7.283s |
| grid-branch-bound | true | 9.435s | 10.049s |

Decision:

```text
keep initial_state = local-grid-cell
stop initial-state retesting for this route
```

This is a no-go for heavier seed strategies, not a negative result for the
Goal5211 global-bound route.

## Next Plan

### Phase 1: Review And Stabilize Current Route

Goal count: 1-2.

1. Send Goals5211-5213 for strict review.
2. If approved, declare the current Level-B default route:

```text
local-grid-cell
max_inline_points = 512
global_bound_early_break = true
all-source no-copy selection in the app runner
```

Acceptance:

```text
review approves global-bound contract and approximate-witness boundary;
review approves all-source no-copy app-runner behavior;
review approves Goal5213 no-go and local-grid default.
```

### Phase 2: Consolidated Level-B Performance Packet

Goal count: 1.

Produce a single packet that includes:

```text
fresh route and full gate total;
explicit warm protocol;
input load;
author HDResult match;
forbidden performance ratios;
review status;
exact dataset status.
```

Acceptance:

```text
no hidden warm-only headline;
no author-vs-RTDL ratio;
all reported numbers have exact artifact paths and regime labels.
```

### Phase 3: Dataset Provenance / Level-C Decision

Goal count: 1-3.

Tasks:

```text
try to locate exact paper inputs or author logs;
record file hashes or provenance if found;
otherwise mark exact-paper dataset unavailable and keep Level-B as representative.
```

Acceptance:

```text
Level C only if exact files / hashes / author-provenance evidence exist;
statistics-only matching remains Level B.
```

### Phase 4: Algorithm Gap Decision

Goal count: 1-2.

If Level-C data is available, decide whether to implement missing X-HD algorithm
pieces as generic RTDL features or stop at evidence-backed Level-B.

Allowed:

```text
generic RTDL spatial primitive;
generic prepared/warm API;
generic traversal/reduction contract.
```

Forbidden:

```text
X-HD-specific RTDL core primitive;
author shortcut that only matches one paper fixture;
performance claim without denominator alignment.
```

## Expected Completion Path

Best-case path:

```text
5211-5213 review passes
-> Level-B route packet closes
-> exact datasets found
-> phase-aligned author comparison designed
-> full paper reproduction attempted
```

Likely path:

```text
5211-5213 review passes
-> Level-B representative line becomes stable
-> exact paper inputs remain unavailable
-> project reports bounded + representative reproduction, not full paper
```

Stop condition:

```text
If exact paper input provenance cannot be established, do not claim Level-C or
full X-HD paper reproduction. Close as Level-B representative reproduction plus
generic RTDL system extraction.
```

## Time / Work Estimate

Expressed as work packages rather than wall-clock time:

| Package | Goals | Expected effort |
|---|---:|---|
| Review Goals5211-5213 | 1-2 | short, mostly document review |
| Consolidated Level-B packet | 1 | short |
| Dataset provenance push | 1-3 | medium, depends on availability / licenses |
| Phase-aligned performance plan | 1-2 | medium |
| Additional generic system implementation | 0-3 | only if dataset / algorithm evidence justifies it |

No further route micro-tuning is recommended before the review and provenance
steps.

## Current Claim Boundary

Allowed summary:

```text
RTDL has a representative X-HD Level-B route on public Stanford
Dragon -> HappyBuddha that matches the author HDResult and now runs in about
0.85s route wall / 1.53s full gate total including input load in a fresh
long-lived process. Under an explicit warm protocol, the measured route is
about 0.29s. The route uses generic RTDL nearest/traversal/reduction machinery
and app-owned X-HD wrappers.
```

Forbidden summary:

```text
full X-HD paper reproduction is complete;
RTDL matches or beats author X-HD performance;
the exact paper dataset has been reproduced;
warm numbers are the default headline;
X-HD needed a paper-specific RTDL core primitive.
```
