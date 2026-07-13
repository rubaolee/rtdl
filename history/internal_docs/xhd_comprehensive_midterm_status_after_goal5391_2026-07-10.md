# X-HD Comprehensive Midterm Status After Goal5391

Date: 2026-07-10

## Status Label

```text
level_b_scalar_strong__system_extraction_real__explicit_lb_denominator_unresolved__full_paper_not_complete
```

## Executive Summary

X-HD full paper reproduction is not complete.

The project has nevertheless reached a strong intermediate state:

1. Bounded X-HD same-input value reproduction is complete and externally
   reviewed through Goal5126.
2. X-HD has produced real RTDL system assets: generic nearest/witness/max-nearest
   primitives, generic grid/cell-MBR descriptors, native 3-D cell-MBR frontier
   collection, active-query status references, multi-round status references,
   and trace-summary helpers.
3. On the strongest current Level-B representative workload, public Stanford
   Dragon -> HappyBuddha, RTDL matches the author directed HD scalar value:

```text
author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
abs diff        ~= 2.38e-9
```

4. The scalar route has been improved substantially, but it is still a
   representative route measurement, not an author-vs-RTDL paper performance
   ratio.
5. The current hard blocker is explicit X-HD `-lb` behavior. Goal5390 and
   Goal5391 prove that the current full-source RTDL bridge stream does not
   match the author raw offload/status stream.

The current `-lb` headline is:

```text
active query count parity = true
author raw offload rows   = 27,133,990
RTDL bridge offload rows  = 2,188,225
row/hash parity           = false
```

Goal5391 derives the aggregate fanout mismatch:

```text
author rows / active = 62
RTDL rows / active   = 5
```

This proves that bridge runtime optimization is not the next main fix. A faster
bridge would still emit the wrong row stream.

One important post-Goal5391 correction must be carried forward: the 5-vs-62
number is the current bridge-materialized offload surface, not the only RTDL
raw-denominator surface seen in the history. Earlier raw-kind2 / full-cover
surfaces are closer to the author denominator and must be reconciled before the
next native implementation target is chosen.

## Governing Principle

RTDL is a general spatial/dataflow language. X-HD is a paper reproduction app
and a pressure test for system APIs.

```text
RTDL core owns:
  generic spatial/dataflow primitives;
  generic descriptors and row schemas;
  generic native traversal / frontier / status contracts;
  generic partner-facing execution contracts.

X-HD app owns:
  paper inputs and provenance;
  author hd_exec wrappers and patched-author instrumentation;
  paper figure labels;
  comparator logic and tolerances;
  route selection and claim boundaries.
```

Do not promote paper-specific X-HD behavior into `src/rtdsl` or `src/native`
unless it is redesigned as a generic API and proved outside X-HD.

## Completion Levels

### Level A: Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

Meaning:

```text
author hd_exec JSON gates work;
RTDL matches directed input1 -> input2 HDResult;
directed vs symmetric Hausdorff ambiguity is resolved;
bounded correctness is not full paper reproduction.
```

### Level B: Same-Source Representative Correctness

Status:

```text
strong scalar evidence, but not full paper reproduction
```

Strongest current representative scalar workload:

```text
source = public Stanford Dragon
source point count = 437,645
target = public Stanford HappyBuddha
target point count = 543,652
```

Current scalar value evidence:

```text
author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
abs diff        ~= 2.38e-9
```

This is strong Level-B evidence. It is still not exact paper dataset
reproduction because public files, point counts, MBRs, statistics, or HDResult
values do not prove exact author input bytes/hashes.

### Level C: Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Exact paper dataset status requires file/hash provenance or an externally
accepted deterministic reconstruction. Matching statistics is necessary
evidence, not sufficient proof.

### Level D: Figure-Level / Performance Reproduction

Status:

```text
not complete
```

Current figure disposition:

```text
Figure 5:
  Level-B graphics and bounded geo scalar candidates exist.
  Full matrix and denominator-aligned performance are not complete.

Figure 7:
  explicit -lb behavior is not reproduced.

Figure 8:
  radius strategy matrix is missing.

Figure 9:
  auto-tune variant denominator is missing.

Figure 10:
  scalability / overlap matrix is missing.

Figure 11:
  memory denominator is not aligned.
```

### Level E: RTDL System Extraction

Status:

```text
real progress
```

X-HD has produced reusable, app-neutral RTDL assets:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest reducer;
non-Hausdorff facility-service-radius consumer;
grid cell descriptors;
cell-MBR candidate / frontier rows;
nearest-state seed contracts;
native 3-D cell-MBR OptiX frontier producer;
inline nearest payload state;
active-query status reference;
multi-round active-query status reference;
generic trace-summary helper.
```

Hausdorff remains an app-level composition over generic primitives. It is not a
hard-coded RTDL core primitive.

## Review Status

### Externally Reviewed / Approved

```text
Goal5110:
  X-HD scaffold / provenance.

Goals5111-5126:
  bounded same-input correctness, including directed-vs-symmetric gate.

Goals5127-5128:
  generic nearest/witness/max-nearest extraction and non-Hausdorff consumer.

Goal5129:
  full-reproduction plan after amendment.
```

### Implemented / Review Pending

Major implemented but review-pending groups:

```text
Goals5130-5212:
  target matrix, dataset provenance, scalable Level-B route, scalar route
  performance evolution, global-bound early-break caveat.

Goals5272-5309:
  figure / dataset / memory / geo / graphics provenance and bounded figure
  diagnostics.

Goals5363-5391:
  explicit -lb status-machine investigation, author trace v2,
  generic status summaries, full-source mismatch gate, fanout diagnostic.
```

Do not silently upgrade any implemented / review-pending goal to externally
approved.

## Scalar Route Progress

On the full public Dragon -> HappyBuddha Level-B scalar route, RTDL moved from a
slow scalable route to a much faster route-local directed-HD value computation:

```text
initial scalable all-source route       ~= 7.30s
inline-nearest threshold 512            ~= 3.65s
intersection-stage current-best pruning ~= 2.6s
dense local-grid lookup                 ~= 2.26s
NumPy matrix input front door           ~= 1.24s
linear max-nearest reduction            ~= 1.17-1.18s
global-bound early-break fresh route    ~= 0.849s
explicit warm route median              ~= 0.362s
Goal5212 warm measured case total       ~= 0.288s
```

Claim boundary:

```text
These are RTDL route-local measurements under specific regimes.
They are not author-vs-RTDL speedup / slowdown ratios.
```

Goal5211 / Goal5212 caveat:

```text
per_source_witness_exact = false
early-aborted sources    = 409,376 / 437,645
```

The fast scalar route is valid for directed Hausdorff / max-nearest scalar value
under an explicit early-break contract. It is not the default for generic exact
nearest-witness APIs because most per-source witnesses may be approximate.

## Current Hard Problem: Explicit `-lb`

The current blocker is no longer scalar directed HD correctness. RTDL can match
representative directed HD scalar values. The blocker is:

```text
Can RTDL reproduce the author explicit -lb status-machine stream through a
generic RTDL active-query / multi-round status model?
```

### Author Trace V2 Oracle

Goal5387 author instrumentation reports:

```text
active_in_queue_size                = 437645
raw_offload_rows_before_sort_reduce = 27133990
status_count_offloading_append      = 27133990
raw_offload_row_hash                = 4333109858711462591
raw_offload_row_sample_point_ids    = [11168, 210712, 437119]
raw_offload_row_sample_cell_ids     = [2924, 17, 17]
load_balance_feedback_update_count  = 294
```

This is an author-side oracle. It does not prove RTDL support.

### Current RTDL Full-Source Bridge Surface

Goal5390 runs the full-source RTDL bridge with no source limit:

```text
source_limit         = null
source_limit_applied = false
active_query_count   = 437645
row_count            = 2188225
raw_offload_row_hash = 10510374331443640811
sample source_ids    = [18080, 219488, 437599]
sample cell_ids      = [6279, 6286, 6145]
```

Comparison:

```text
active_query_count_parity = true
row_count_parity          = false
hash_parity               = false
row delta                 = 24,945,765
row ratio RTDL / author   = 0.08064516129032258
```

Goal5391 derives:

```text
RTDL bridge rows / active   = 2,188,225 / 437,645 = 5
author rows / active        = 27,133,990 / 437,645 = 62
```

This cleanly rejects source-limit explanations and bridge-formatting
explanations for the current bridge surface.

### Important Denominator Correction

Goal5391 is true for the current bridge-materialized offload rows. It is not
the entire denominator history.

Earlier RTDL surfaces show:

```text
author raw offload rows = 27,133,990

current bridge materialized offload rows:
  2,188,225
  ratio = 0.0806451613
  aggregate = 5 rows / active query

default / inline raw kind2 count:
  21,006,960
  ratio = 0.7741935484
  aggregate = 48 rows / active query

full-cover lb256 behavior gate surface:
  24,508,120
  ratio = 0.9032258065
  aggregate = 56 rows / active query

heavy-before-inline-prune raw kind2 count:
  304,981,889
  ratio = 11.2398467384
  aggregate ~= 697 rows / active query
```

Implication:

```text
Do not implement the next native stream against the 5x bridge count alone.
The next step must reconcile the denominator surfaces and choose the correct
raw author-comparable target.
```

The bridge surface proves one failure mode. The raw-kind2 and full-cover
surfaces show that RTDL already has closer-but-still-wrong generic telemetry
surfaces. The next implementation should target author-compatible raw status
semantics, not just post-bridge materialized rows.

## Problems Already Solved

```text
1. Directed vs symmetric Hausdorff ambiguity.
2. Bounded same-input author JSON / RTDL route correctness.
3. Hausdorff demoted to app-level composition over generic primitives.
4. Non-Hausdorff consumer proving nearest/max-nearest helper generality.
5. Naive all-pair exact route rejected at full-public scale.
6. Scalable Level-B scalar route built and substantially improved.
7. Multiple false optimization paths closed as no-go.
8. Author -lb oracle upgraded from count-only to trace v2 with hashes/samples.
9. RTDL generic active-query status and trace-summary APIs exist.
10. Full-source RTDL trace-summary comparison now exists and confirms mismatch.
11. Goal5391 converts current bridge mismatch into a crisp fanout diagnostic.
```

## Major Problems Still Open

```text
1. Exact paper input bytes / hashes / deterministic reconstruction.
2. Explicit -lb status-machine parity.
3. Correct denominator-surface selection for the next -lb implementation.
4. Figure 7 load-balance reproduction.
5. Figure 11 same-denominator memory reproduction.
6. Same-denominator author-vs-RTDL performance comparison.
7. Exact per-source witness semantics under global-bound early-break.
8. External review debt for the latest implemented X-HD goals.
```

## Planned Work

### P0: Strict Review Packet

Review packets already exist for the latest `-lb` trace line:

```text
history/internal_docs/call_for_review_goals5386_5390_xhd_lb_trace_packet_2026-07-10.md
history/internal_docs/call_for_review_goal5391_xhd_lb_fanout_semantics_2026-07-10.md
```

Review questions:

```text
1. Does Goal5390 prove the current full-source bridge surface is not
   author-compatible?
2. Does Goal5391 correctly reject bridge runtime optimization as the next main
   path?
3. Does the 5-vs-62 aggregate fanout diagnostic need the denominator-surface
   correction before native implementation?
```

### P1: Goal5392 Denominator Surface Reconciliation

Purpose:

```text
Reconcile all known RTDL -lb denominator surfaces before choosing a native
implementation target.
```

Inputs:

```text
Goal5387 author trace v2:
  author raw offload rows = 27,133,990

Goal5390 / Goal5391 bridge surface:
  materialized bridge offload rows = 2,188,225

Goal5371 / Goal5377 default raw-kind2 surface:
  raw kind2 rows = 21,006,960

Goal5375 full-cover surface:
  rows = 24,508,120

Goal5377 heavy-before-inline-prune surface:
  raw kind2 rows = 304,981,889
```

Expected output:

```text
surface table;
ratio to author;
aggregate rows per active query;
classification of each surface;
decision whether the next target is raw-kind2 semantics, full-cover semantics,
multi-round status feedback, or fail-closed closeout.
```

POD:

```text
not expected; use existing artifacts.
```

### P2: Generic Native Status-Stream Design / Prototype

Only after P1 chooses the correct target:

```text
Implement or prototype a generic native status stream that can emit
author-comparable raw active/offload/miss/completed/aborted transitions.
```

Minimum generic fields:

```text
active_query_count;
active_queue_index or query id;
cell id;
status code;
raw offload row count;
raw offload row hash;
sampled source/query ids;
sampled cell ids;
miss / completed / aborted counters;
feedback update accounting or explicit not-applicable field.
```

Forbidden shortcuts:

```text
hard-code 62 rows per active query;
hard-code X-HD option names into RTDL core;
use author-specific paper figure semantics in native generic code;
claim explicit -lb support before row/hash parity.
```

POD:

```text
required for native build and full Dragon -> AsianDragon probe.
```

### P3: Full Row / Hash Parity Gate

Gate target:

```text
active_query_count = 437645
raw offload rows comparable to 27,133,990
hash/sample comparable to Goal5387 author trace v2
status counters comparable or explicitly explained
```

Exit labels:

```text
native_status_stream_row_hash_parity_established
native_status_stream_denominator_still_mismatch__lb_fail_closed
```

If row/hash parity fails, do not continue performance work on explicit `-lb`.

### P4: Explicit `-lb` Closeout Or Figure Refresh

If parity is established:

```text
refresh Figure 7 / Figure 11 / performance-denominator plan under the new
generic status-stream evidence.
```

If parity is not established:

```text
close explicit -lb as unsupported under the current RTDL model, while preserving
the scalar Level-B route and generic system APIs as completed progress.
```

### P5: Dataset / Figure Work After `-lb` Decision

After the `-lb` line is advanced or fail-closed, refresh:

```text
Figure 5 Level-B scalar status;
Figure 7 load-balance status;
Figure 8 radius strategy blocker;
Figure 9 auto-tune blocker;
Figure 10 scalability blocker;
Figure 11 memory denominator blocker;
exact input acquisition matrix.
```

## POD Use Plan

Use only the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Last verified:

```text
POD_OK
container = 45c502cfccb5
GPU       = NVIDIA RTX 4000 Ada Generation
driver    = 550.127.05
```

Expected POD usage:

```text
P0 review packet:
  no POD.

P1 denominator-surface reconciliation:
  no POD unless reviewers request rerun.

P2 native status-stream prototype:
  POD required.

P3 full row/hash parity gate:
  POD required.

P4/P5 documentation / claim matrix:
  no POD unless new figure gates are run.
```

Do not use POD for:

```text
more source-limited smoke;
bridge runtime optimization before row/hash semantics change;
performance comparison before denominator alignment;
repeating known no-go surfaces without a new transition hypothesis.
```

## Expected Process And Timing

This is goal-count scheduling, not a calendar promise.

```text
Batch 1:
  review / denominator reconciliation / requirements correction
  expected goals: 1-2
  POD: no

Batch 2:
  native generic status-stream prototype
  expected goals: 1-3
  POD: yes

Batch 3:
  full row/hash parity gate and decision
  expected goals: 1-2
  POD: yes

Batch 4:
  closeout / figure matrix refresh / memory update
  expected goals: 1-2
  POD: no unless new gates are added
```

Fast path:

```text
If denominator reconciliation shows no generic target can approach author raw
status semantics without X-HD-specific logic, move directly to fail-closed
closeout instead of spending more goals on performance.
```

## Forbidden Summaries

Do not say:

```text
X-HD full paper reproduction is complete.
RTDL supports X-HD -lb.
RTDL reproduces Figure 7.
RTDL reproduces Figure 11.
RTDL has same-denominator author memory parity.
RTDL has author-vs-RTDL performance ratio evidence.
RTDL matches author RT-core algorithm behavior.
Goal5390 establishes row-count parity.
Goal5390 establishes hash/sample parity.
Goal5391 proves every active query emits exactly 62 author rows.
Goal5391 proves the only possible RTDL denominator target is the 5x bridge surface.
Global-bound early-break gives exact per-source witnesses.
Public files are exact paper datasets.
```

## Allowed Summary

```text
X-HD bounded correctness and generic system extraction are strong. RTDL matches
representative directed HD scalar values on full public Level-B inputs and has
reduced the scalar route substantially. Full paper reproduction is still open:
exact paper input provenance, figure denominators, and explicit -lb behavior
are not complete. The current full-source bridge gate aligns active-query count
but fails author raw offload row and hash/sample parity: the bridge emits
2,188,225 offload rows while author emits 27,133,990. Goal5391 turns that into
a 5-vs-62 aggregate fanout diagnostic for the bridge surface. Before writing
the next native implementation, the project must reconcile older raw-kind2 /
full-cover denominator surfaces against the author trace, then either build a
generic native status stream that changes the denominator or fail-close explicit
-lb under the current RTDL execution model.
```
