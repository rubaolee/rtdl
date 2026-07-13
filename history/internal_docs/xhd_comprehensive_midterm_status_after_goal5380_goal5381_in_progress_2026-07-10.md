# X-HD Comprehensive Midterm Status After Goal5380 / Goal5381 In Progress

Date: 2026-07-10

Status:

```text
full_xhd_paper_reproduction_not_complete
bounded_value_reproduction_complete_and_reviewed_through_goal5126
generic_system_extraction_complete_and_reviewed_through_goal5128
level_b_representative_route_strong_but_not_exact_paper_dataset
explicit_lb_support_not_authorized
goal5379_goal5380_implemented_review_pending
goal5381_in_progress
```

This is the current handoff / midterm status report for the X-HD line. It
supersedes the earlier day-to-day handoff reports after Goals5375, 5376, 5377,
and 5379 while preserving them as historical evidence.

## Executive Summary

The X-HD line has made real progress on two fronts:

1. **Paper-app evidence**: RTDL can reproduce bounded and representative
   X-HD scalar HDResult values under carefully labeled regimes.
2. **System extraction**: the work has pushed reusable RTDL primitives for
   nearest/witness/max-nearest, grid/cell-MBR traversal, native frontier rows,
   heavy/offload telemetry, and now active-query/status-machine state.

But the core objective is not complete:

```text
RTDL does not yet fully reproduce the X-HD paper.
RTDL does not yet support author-compatible explicit -lb semantics.
Exact paper input identity is still not proven.
Author-vs-RTDL performance parity or speedup ratios remain unauthorized.
```

The current hard problem is no longer "can RTDL compute a directed HD value?".
That part is strong. The current hard problem is:

```text
Can RTDL model the author's X-HD load-balance / heavy-offload status machine
well enough to match the author OffloadingSize denominator?
```

The next active goal is Goal5381: run a native/OptiX active-query row-parity
probe against the Goal5374 author oracle.

## Current Objective

The active objective remains:

```text
Complete full X-HD paper reproduction, or close it honestly with precise
evidence about what is reproduced, what is representative only, and what is
blocked.
```

The stricter interpretation of "complete" requires:

- author input provenance, or an explicit same-source representative label;
- author contract / directed-HD semantics alignment;
- RTDL route matching author output;
- figure/option semantics where claimed;
- fair phase/performance denominator alignment before any ratio;
- external review before upgrading implemented evidence to approved evidence.

## What Is Completed And Externally Reviewed

### Bounded X-HD Same-Input Reproduction

Completed and reviewed through Goal5126:

```text
bounded same-input author JSON gates;
bounded 2-D and 3-D RTDL route gates;
directed-vs-symmetric discriminating fixture;
author HDResult proven to be directed input1 -> input2 on the tested contract.
```

Important boundary:

```text
This is bounded same-input value reproduction.
It is not full paper reproduction.
It is not author RT-core algorithm parity.
It is not performance parity.
```

### Generic Nearest/Witness/Max-Nearest Extraction

Completed and reviewed through Goals5127-5128:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest distance witness;
non-Hausdorff consumer proving the max-nearest helper is not X-HD-specific.
```

This is a genuine RTDL system gain. Hausdorff is now expressed as a composition
of generic primitives, not as a paper-specific RTDL core primitive.

### Full-Reproduction Plan

Goal5129 was reviewed with amendments. The durable decision is:

```text
statistics/counts/log paths do not prove exact input identity;
exact paper dataset status requires file/hash or equivalent provenance;
representative public inputs must remain Level B unless exact identity is proven.
```

## Major Implemented Work Since Then

Most later X-HD goals are implemented / review pending. They are valuable
engineering evidence, but they must not be silently upgraded to externally
approved status.

### Level-B Public Graphics Route

The strongest representative evidence is still the Stanford public
Dragon -> HappyBuddha line:

```text
source points = 437645
target points = 543652
author hd_exec HDResult ~= 0.12572988867759705
RTDL route distance    ~= 0.12572988629271128
abs diff               ~= 2.38e-9
```

This is strong Level-B same-source scalar evidence. It is not exact paper input
reproduction because the exact author input bytes / hashes are not proven.

### Route Performance Evolution

The route evolved from a slow all-cell/frontier path into a much stronger
generic cell-MBR / inline-nearest / global-bound route.

Representative route-local numbers:

```text
Goal5188 baseline RTDL route wall        ~= 7.30s
Goal5189 local-grid seed                 ~= 5.98s
Goal5191 inline512 empty-frontier route  ~= 3.65s
Goal5195 intersection current-best prune ~= 2.6s
Goal5196 dense local-grid lookup         ~= 2.26s
Goal5203 matrix input front door         ~= 1.24s
Goal5204 linear max-nearest reducer      ~= 1.17-1.18s
Goal5211 global-bound early break        ~= 0.849s fresh route
Goal5211 explicit-warm route median      ~= 0.362s
Goal5212 fresh full total incl. load      ~= 1.531s
Goal5212 explicit-warm measured total    ~= 0.288s
```

These are RTDL route-local / regime-labeled numbers. They are not
author-vs-RTDL speedup ratios because the author internal timing, author process
wall, RTDL route wall, and RTDL total are different denominators.

Critical caveat for Goal5211:

```text
The global-bound route is exact for the final max-nearest / directed-HD scalar
value, but many per-source witnesses are approximate after early abort.
It is therefore a directed-HD/max-nearest contract, not a default exact
nearest-witness API.
```

### Figure / Dataset Audit Status

Current figure-level status:

```text
Figure 5:
  several Level-B graphics / geo scalar matches exist;
  exact paper input identity remains unproved;
  no denominator-aligned performance ratio authorized.

Figure 7:
  author lb=0/lb=256 diagnostic pair exists;
  RTDL behavior-level offload evidence exists;
  explicit -lb row-denominator parity is not proven.

Figure 8:
  author radius-strategy source/scripts identified;
  checked-in logs are insufficient for full figure reproduction.

Figure 9:
  author logs/scripts audited;
  missing variant denominator prevents reproduction under current evidence.

Figure 10:
  scalability/overlap scripts identified;
  required logs / inputs are missing under current evidence.

Figure 11:
  author memory semantics audited;
  RTDL has shape-like offload telemetry, but denominator alignment is false.
```

## Major Problems Already Solved

### 1. Directed HD Semantics

The directed-vs-symmetric ambiguity was closed with a discriminating fixture.
The project now knows the author contract for the bounded route:

```text
HDResult = directed input1 -> input2, not symmetric Hausdorff.
```

### 2. Exact Pairwise Route Was Rejected At Scale

The public Dragon/HappyBuddha pair has:

```text
437645 * 543652 = 237,926,579,540 point pairs
```

Materializing exact pairwise candidates is infeasible. This forced the current
generic grid/cell-MBR/native-frontier route, which is the right system direction.

### 3. The RTDL Route Became A Generic System Route

The current route is not a one-off X-HD primitive. It uses generic RTDL pieces:

```text
grid cell descriptors;
cell-MBR descriptors;
native 3-D cell-MBR frontier rows;
nearest-state seed;
inline nearest in traversal;
max-nearest scalar reduction;
optional global-bound early break for directed-HD/max-nearest.
```

### 4. The Load-Balance Problem Was Narrowed To A Real Oracle

Many simpler explanations were tested and rejected:

```text
scalar radius mismatch;
host materialization / sort artifact;
raw kind2 rows alone;
existing global-bound as author cmax2 abort;
heavy-before-inline-prune branch order.
```

Goal5374 produced the first strong author-side oracle for the Dragon ->
AsianDragon `lb=256` status-machine denominator:

```text
ActiveInQueueSize              = 437645
StatusInitCount                = 437645
OffloadingSize                 = 27133990
RawOffloadRowsBeforeSortReduce = 27133990
StatusOffloadingAppendCount    = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
StatusCmax2MbrAbortCount       = 0
StatusPointLoopEarlyBreakCount = 0
```

That oracle is now the target for the next RTDL row-parity probe.

### 5. POD Access Procedure Is Stable

The current POD preflight works through the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Observed in the latest check:

```text
POD_OK
container = 45c502cfccb5
GPU       = NVIDIA RTX 4000 Ada Generation
driver    = 550.127.05
```

Use the wrapper. Do not use naked SSH.

## Current Hard Problem: Explicit `-lb`

The author `-lb` path is not just "emit heavy cells". It is a traversal/status
machine:

```text
active in_queue index;
dynamic per-query cmin2 / current-best state;
offload rows keyed by active_queue_index;
miss / completed / aborted status;
loadBalanceProcessing feedback into later work;
author-width raw offload rows before sort/reduce.
```

Current RTDL surfaces fail the author oracle:

```text
author oracle rows                  = 27133990
RTDL author-radius inline kind2      = 21006960
RTDL inline + global-bound kind2     = 21006960
RTDL author-radius no-inline kind2   = 304981889
old full-cover lb256 behavior gate   = 24508120
```

None has row-count parity.

## Goal5379: Generic Active-Query Status-Machine Reference

Implemented / review pending.

Files:

```text
src/rtdsl/active_query_status.py
tests/goal5379_active_query_status_machine_reference_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5379_active_query_status_machine_reference.json
history/internal_docs/goal5379_active_query_status_machine_reference_result_2026-07-10.md
history/internal_docs/call_for_review_goal5379_active_query_status_machine_reference_2026-07-10.md
```

Public contract:

```text
generic_active_query_status_machine_reference_v1
```

It models:

```text
active queries;
current_best_sq by active_queue_index;
multiple offload rows per active query;
miss rows;
completed rows;
aborted rows;
continuation feedback into current-best state;
overflow fail-closed behavior.
```

Important correction:

```text
The reference now preserves multiple offload rows for a single active query.
Earlier semantics stopped after the first offload row, which would be wrong for
author OffloadingSize, because the author raw append count can contain many
offload rows per active query.
```

Validation just rerun:

```text
py -m py_compile src\rtdsl\active_query_status.py src\rtdsl\__init__.py

py -m unittest \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test

Ran 19 tests OK
```

The known Windows Python warning appeared:

```text
Could not find platform independent libraries <prefix>
```

It did not affect test success.

## Goal5380: Active-Query Frontier Bridge

Implemented / review pending.

Files:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5380_active_query_frontier_bridge_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5380_active_query_frontier_bridge.json
history/internal_docs/goal5380_active_query_frontier_bridge_result_2026-07-10.md
history/internal_docs/call_for_review_goal5380_active_query_frontier_bridge_2026-07-10.md
```

New public contract:

```text
generic_active_query_status_from_frontier_rows_v1
```

Purpose:

```text
generic cell-MBR frontier row table
  -> active-query candidate stream
  -> generic active-query status-machine reference
```

The bridge consumes app-neutral frontier columns:

```text
query_row_ids
cell_ids
point_counts
min_distances
max_distances
optional frontier_kind_codes
```

It lowers them into the Goal5379 active-query reference. This is still CPU/NumPy
and still not native author `-lb` support.

## Goal5381: In Progress

Current Goal5381 work:

```text
app-owned native/OptiX active-query row-parity probe runner
```

Added locally:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
tests/goal5381_active_query_frontier_bridge_probe_test.py
```

The runner:

1. loads real X-HD inputs;
2. builds grid/cell-MBR state;
3. calls the generic native OptiX cell-MBR frontier row producer;
4. feeds the returned row table through Goal5380's active-query bridge;
5. compares bridge offload rows against the Goal5374 author oracle:

```text
author raw offload rows  = 27133990
author-width raw bytes   = 217071920
active in_queue size     = 437645
```

Local tests for the runner pass as part of the 19-test set above.

Current status:

```text
Goal5381 is not complete.
No full POD row-parity artifact exists yet.
No explicit -lb support is claimed.
```

## POD Use Expectations

Current POD endpoint:

```text
host = 213.173.108.24
port = 13502
container = 45c502cfccb5
GPU = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Required command form:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Remote workspace caveat:

```text
/tmp/rtdl_goal5364 exists but is not a git checkout.
Changed files must be synced explicitly.
Native rebuilds must be explicit when native files change.
```

Goal5381 remote expectation:

1. Confirm remote synced Python reference semantics:

```text
active_query_status_machine_reference should emit 2 offload rows for a tiny
one-query/two-heavy-candidate smoke case.
```

2. Run a bounded smoke if full row volume is too high.
3. Attempt full Dragon -> AsianDragon `lb=256` bridge probe only after smoke.
4. If the CPU bridge is too slow over tens of millions of rows, classify that
   as evidence that a vectorized/native active-query bridge is required.

Important row-volume caution:

```text
author oracle rows                  = 27,133,990
current inline RTDL candidate rows   = 21,006,960
no-inline raw rows                   = 304,981,889
```

The CPU/NumPy reference is valuable as a semantic baseline, but the full-scale
bridge may be too slow if it loops over every materialized candidate row in
Python. That would not be a failure of the concept; it would identify the next
system implementation target.

## Planned Work

### Goal5381 - Native/OptiX Active-Query Row-Parity Probe

Immediate steps:

```text
1. Re-check POD sync with a tiny offload-row smoke.
2. Run the app-owned probe on Dragon -> AsianDragon lb=256 inputs.
3. Compare RTDL bridge rows to Goal5374 author oracle.
4. Emit artifact, result report, and call-for-review.
```

Required output fields:

```text
active_query_count
candidate_row_count
offload_row_count
completed_row_count
miss_row_count
aborted_row_count
author_raw_offload_rows_before_sort_reduce
row_delta_author_minus_rtdl
row_ratio_rtdl_div_author
row_count_parity
author_width_byte_parity
```

Allowed exit labels:

```text
active_query_bridge_matches_author_oracle__explicit_lb_review_required
active_query_bridge_mismatch_classified__native_status_machine_needed
active_query_bridge_cpu_reference_not_scalable__vectorized_or_native_bridge_needed
```

### Goal5382 - Vectorized / Native Active-Query Bridge If Needed

If Goal5381 shows that the CPU reference cannot scale to full row volume, the
next goal should not pretend the semantic bridge is done. It should implement a
faster generic bridge:

```text
vectorized count/parity bridge for row-count telemetry; or
native active-query bridge that keeps status transitions near the frontier row
producer.
```

It must remain app-neutral:

```text
active query;
status rows;
offload rows;
current-best feedback;
```

Not:

```text
X-HD-specific OffloadingSize primitive;
Figure 7 primitive;
Figure 11 primitive;
author-only queue clone in RTDL core.
```

### Goal5383 - Explicit `-lb` Decision Gate

After Goal5381/5382:

```text
if row parity is achieved:
  design explicit -lb option surface with review, still separating Figure 7/11
  claims from behavior support;

if row parity is not achieved:
  keep explicit -lb fail-closed and document the remaining denominator gap.
```

### Review Node

Goals5374-5381 should be sent as a strict review packet once Goal5381 produces
either a full result or a justified no-go / scalability result.

The review packet should ask:

```text
1. Is Goal5374 author oracle valid and sufficient?
2. Do Goals5375-5377 correctly reject old RTDL surfaces?
3. Is Goal5378's active-query direction justified?
4. Is Goal5379 generic and app-neutral?
5. Does Goal5380 correctly bridge frontier rows into active-query semantics?
6. Does Goal5381 establish row parity, or correctly identify why it does not?
```

## What Must Not Be Claimed

Do not claim:

```text
full X-HD paper reproduction;
exact paper dataset reproduction;
author-vs-RTDL performance parity or speedup;
explicit author-compatible -lb support;
Figure 7 reproduction;
Figure 11 reproduction;
same-denominator memory parity;
author RT-core algorithm parity;
native backend completion for active-query status-machine support.
```

Allowed current summary:

```text
RTDL has complete reviewed bounded X-HD value reproduction and generic
nearest/witness system extraction.  On representative public Stanford graphics
inputs, RTDL matches author scalar HDResult under explicit Level-B boundaries.
The route has been optimized substantially, but performance ratios remain
unauthorized because denominators differ.  The current hard blocker for fuller
X-HD functional coverage is explicit -lb / heavy-offload semantics.  The author
status-machine oracle is available, current RTDL row surfaces fail it, and RTDL
now has a generic CPU active-query status-machine reference plus a frontier-row
bridge.  The next step is the Goal5381 POD row-parity probe.
```

Forbidden summary:

```text
X-HD paper reproduction is complete.
RTDL matches the X-HD author algorithm.
RTDL supports -lb.
RTDL reproduces Figure 7 or Figure 11.
RTDL is faster/slower than author by a published ratio.
Goal5379/5380 proves native status-machine support.
```

## Current Worktree / Hygiene Note

The worktree contains many paper-app artifacts, tests, reports, and system
changes from the broader paper-reproduction project. This report does not try
to clean or classify the full tree. For the current active line, the relevant
new/changed files are:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5379_active_query_status_machine_reference_test.py
tests/goal5380_active_query_frontier_bridge_test.py
tests/goal5381_active_query_frontier_bridge_probe_test.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5380_active_query_frontier_bridge.json
history/internal_docs/goal5380_active_query_frontier_bridge_result_2026-07-10.md
history/internal_docs/call_for_review_goal5380_active_query_frontier_bridge_2026-07-10.md
```

## Bottom Line

The project is in a much better place than at the start of X-HD:

```text
bounded value reproduction: done and reviewed;
generic nearest system extraction: done and reviewed;
Level-B representative scalar route: strong;
route performance: dramatically improved, but no ratio authorized;
exact paper input provenance: still open;
explicit -lb / heavy-offload semantics: current hard blocker;
Goal5379/5380: implemented semantic bridge;
Goal5381: active POD row-parity probe is the next decisive step.
```

The right next move is not another scalar-radius or raw-count guess. It is the
Goal5381 active-query/status-machine probe, followed by a vectorized/native
bridge only if the CPU reference proves too slow at full row volume.
