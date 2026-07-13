# X-HD Current Midterm Report After Goal5390

Date: 2026-07-10

## Status Label

```text
level_b_scalar_strong__generic_system_extraction_real__lb_status_stream_mismatch_open__full_paper_not_complete
```

## Executive Summary

X-HD is not fully reproduced yet.

The project has made substantial progress in two real ways:

1. RTDL now has strong bounded and Level-B same-source directed Hausdorff scalar
   correctness evidence.
2. X-HD pressure has produced reusable RTDL system assets: generic nearest /
   witness / max-nearest reduction, grid/cell-MBR descriptors, native 3-D
   cell-MBR frontier collection, active-query status references, and generic
   status-trace summaries.

The current hard blocker is explicit X-HD `-lb` behavior. Goal5390 proves the
full-source RTDL trace reaches the same active-query count as the author trace,
but not the same raw offload row stream:

```text
active_query_count parity = true
RTDL offload rows         = 2,188,225
author offload rows       = 27,133,990
row_count_parity          = false
hash_parity               = false
```

Therefore explicit `-lb`, Figure 7, Figure 11, author RT-core parity,
same-denominator memory, and full X-HD paper reproduction remain unclaimed.

## Project Goal

The active goal is a full X-HD paper reproduction line that also improves RTDL
as a general spatial/dataflow language.

The governing principle remains:

```text
RTDL core exposes generic spatial/dataflow primitives.
The X-HD app owns author wrappers, paper inputs, comparators, tolerances,
figure labels, and claim boundaries.
```

No paper-specific X-HD primitive should be promoted into `src/rtdsl` or
`src/native` unless it is first redesigned as app-neutral system API and proved
outside X-HD.

## Completion Levels

### Level A: Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

Meaning:

```text
author hd_exec JSON gate works;
RTDL matches directed input1 -> input2 HDResult;
directed vs symmetric Hausdorff ambiguity is resolved;
bounded correctness is not full paper reproduction.
```

### Level B: Same-Source Representative Correctness

Status:

```text
strong scalar evidence, not full paper reproduction
```

Strongest current representative scalar case:

```text
source = public Stanford Dragon
source point count = 437,645
target = public Stanford HappyBuddha
target point count = 543,652

author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
abs diff        ~= 2.38e-9
```

This is useful evidence, but it remains Level B. Public files matching point
counts or author-log values do not prove exact paper input bytes/hashes.

### Level C: Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Exact paper input status requires file/hash provenance or an externally
accepted deterministic reconstruction. Counts, MBRs, Gini, and HDResult values
are necessary evidence but not sufficient.

### Level D: Figure-Level / Performance Reproduction

Status:

```text
not complete
```

Current figure disposition:

```text
Figure 5: Level-B scalar candidates exist; full matrix and denominator-aligned
          performance are not complete.
Figure 7: explicit -lb support is not complete.
Figure 8: radius strategy matrix is missing.
Figure 9: auto-tune variant denominator is missing.
Figure 10: scalability / overlap matrix is missing.
Figure 11: memory denominator is not aligned.
```

### Level E: RTDL System Extraction

Status:

```text
real progress
```

X-HD has yielded app-neutral RTDL assets, including:

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

Hausdorff remains an app-level composition over generic primitives, not a
hard-coded core primitive.

## Review Status

### Externally Reviewed / Approved

```text
Goal5110: X-HD scaffold / provenance
Goals5111-5126: bounded same-input correctness, including directed-vs-symmetric gate
Goals5127-5128: generic nearest/witness/max-nearest extraction and non-Hausdorff consumer
Goal5129: full-reproduction plan after amendment
```

### Implemented / Review Pending

The major implemented but review-pending arc covers Goals5130-5390.

Important review-pending groups:

```text
Goals5130-5212:
  target matrix, dataset provenance, scalable Level-B route, and scalar
  performance evolution.

Goals5272-5309:
  figure / dataset / memory / geo / graphics provenance and bounded figure
  diagnostics.

Goals5363-5390:
  explicit -lb status-machine investigation, author trace v2, RTDL trace summary,
  and full-source row/hash mismatch.
```

Do not silently upgrade any of these to externally approved until real review
exists.

## Scalar Route Performance Evolution

On the full public Dragon -> HappyBuddha Level-B scalar route, RTDL moved from
a slow scalable route to a fast route-local directed-HD value computation:

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
nearest-witness APIs.

## Current Hard Problem: Explicit `-lb`

The current blocker is no longer "can RTDL compute the directed HD scalar?".
It can for representative public inputs. The blocker is:

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

This is an author-side oracle. It does not by itself prove RTDL support.

### RTDL Full-Source Trace Summary

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

Important derived observation:

```text
RTDL rows / active queries   = 2,188,225 / 437,645 = 5
author rows / active queries = 27,133,990 / 437,645 = 62
```

This points to a status-stream fanout / transition semantics mismatch, not a
source-limit artifact and not merely bridge formatting.

## Problems Already Solved

```text
1. Directed vs symmetric Hausdorff ambiguity.
2. Bounded same-input author JSON / RTDL route correctness.
3. Hausdorff demoted to app-level composition over generic primitives.
4. Non-Hausdorff consumer proving nearest/max-nearest helper generality.
5. Naive all-pair exact route rejected at full-public scale.
6. Scalable Level-B scalar route built and substantially improved.
7. Many false optimization paths closed as no-go.
8. Author -lb oracle upgraded from count-only to trace v2 with hashes/samples.
9. RTDL generic active-query status and trace-summary APIs exist.
10. Full-source RTDL trace-summary comparison now exists and confirms the mismatch.
```

## Major Problems Still Open

```text
1. Exact paper input bytes / hashes / deterministic reconstruction.
2. Explicit -lb status-machine parity.
3. Figure 7 load-balance reproduction.
4. Figure 11 same-denominator memory reproduction.
5. Same-denominator author-vs-RTDL performance comparison.
6. Exact per-source witness semantics under global-bound early-break.
7. External review debt for the latest implemented X-HD goals.
```

## Planned Work

### P0: Review Goals5386-5390

Current packet:

```text
history/internal_docs/call_for_review_goals5386_5390_xhd_lb_trace_packet_2026-07-10.md
```

Review question:

```text
Does Goal5390 justify the conclusion that current explicit -lb support remains
unsupported unless a genuinely new native multi-round status stream is
implemented?
```

Expected outcome:

```text
approve_goals5386_5390_xhd_lb_trace_packet__full_denominator_mismatch_confirmed
```

or required amendments before further `-lb` implementation.

### P1: Goal5391 Fanout / Transition Semantics Diagnostic

Purpose:

```text
Turn the Goal5390 mismatch into a crisp requirements artifact:
RTDL currently emits 5 rows per active query; author emits 62 rows per active
query.  The next implementation must change status-stream fanout semantics,
not merely optimize bridge runtime.
```

Expected artifact:

```text
author rows per active;
RTDL rows per active;
row/hash mismatch classification;
minimum generic status-stream requirements for the next native implementation;
forbidden paths: source-limited smoke, bridge vectorization, X-HD-specific constants.
```

This can be done locally. No POD required unless the report needs an additional
full-source confirmation run.

### P2: Native Generic Multi-Round Status Stream Design / Prototype

Purpose:

```text
Implement or prototype a generic native stream that can emit multiple
status/offload transitions per active query and compare against the author v2
oracle.
```

Generic requirements:

```text
app-neutral contract and symbol names;
active_queue_index / query id / cell id / status code columns;
current-best state per active query;
miss / completed / offload / aborted counters;
feedback update accounting or explicit not-applicable field;
fail-closed row capacity;
no X-HD hard-coded fanout such as "62 rows".
```

POD expected:

```text
yes, for native build and full Dragon -> AsianDragon row/hash probe.
```

### P3: Row / Hash Parity Gate

Gate target:

```text
active_query_count = 437645
raw offload rows -> 27133990
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

After the `-lb` line is either advanced or fail-closed, refresh:

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
P0 review packet: no POD.
P1 fanout diagnostic: likely no POD; use existing Goal5387/5390 artifacts.
P2 native stream prototype: POD required for build / OptiX execution.
P3 full row/hash parity gate: POD required.
P4/P5 documentation / claim matrix: no POD unless new figure gates are run.
```

Do not use POD for:

```text
more source-limited smoke;
bridge runtime optimization before row/hash semantics change;
performance comparison before denominator alignment.
```

## Expected Process And Timing

This is goal-count scheduling, not a calendar promise.

```text
Batch 1:
  review / requirements / fanout diagnostic
  expected goals: 1-2
  POD: no, unless revalidation is requested

Batch 2:
  native generic multi-round status stream prototype
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
If P1 and P2 show the generic native stream cannot be made denominator-aligned
without app-specific X-HD logic, move directly to fail-closed closeout instead
of spending more goals on performance.
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
Global-bound early-break gives exact per-source witnesses.
Public files are exact paper datasets.
```

## Allowed Summary

```text
X-HD bounded correctness and generic system extraction are strong. RTDL matches
representative directed HD scalar values on full public Level-B inputs and has
reduced the scalar route substantially. Full paper reproduction is still open:
exact paper input provenance, figure denominators, and explicit -lb behavior
are not complete. The current Goal5390 full-source gate aligns active-query
count but fails author raw offload row and hash/sample parity: RTDL emits
2,188,225 offload rows while author emits 27,133,990. The next work is either
a genuinely generic native multi-round status stream that changes this
denominator, or an honest fail-closed closeout for explicit -lb under the
current RTDL execution model.
```
