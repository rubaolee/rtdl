# X-HD Comprehensive Midterm Status After Goal5381

Date: 2026-07-10

Status:

```text
full_xhd_paper_reproduction_not_complete
bounded_same_input_value_reproduction_complete_and_reviewed_through_goal5126
generic_system_extraction_complete_and_reviewed_through_goal5128
level_b_public_representative_scalar_route_strong_but_not_exact_paper_dataset
explicit_lb_author_status_machine_not_supported
goal5379_goal5380_goal5381_implemented_review_pending
next_required_work_native_status_machine_stream_design_or_fail_closed_lb_closeout
```

This report supersedes the handoff role of:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5380_goal5381_in_progress_2026-07-10.md
```

while preserving that file and earlier goal reports as historical evidence.

## Executive Summary

The X-HD line has advanced substantially, but it is not finished.

RTDL now has strong evidence for:

```text
bounded same-input HDResult reproduction;
directed input1 -> input2 Hausdorff contract;
generic nearest / witness / max-nearest system extraction;
Level-B same-source public Stanford graphics scalar HDResult matching;
large route performance improvement on the representative Dragon -> HappyBuddha pair.
```

The remaining hard blocker is different:

```text
RTDL does not yet reproduce the author's explicit -lb / heavy-offload status
machine denominator.
```

Goal5381 made this concrete. On Dragon -> AsianDragon `lb=256`, active query
count aligns with the author oracle:

```text
437645 == 437645
```

but the offload row denominator does not:

```text
RTDL bridge offload rows = 2188225
author offload rows      = 27133990
RTDL / author ratio      = 0.08064516129032258
```

Therefore the current generic native frontier stream plus CPU bridge is not
the author's raw status-machine stream. Explicit `-lb` remains unsupported.

## Current Objective

The active objective remains:

```text
Complete full X-HD paper reproduction, or close it honestly with precise
evidence about what is reproduced, what is representative only, and what is
blocked.
```

Completion requires all of the following before any full-paper claim:

```text
exact input provenance or an explicit representative label;
author contract alignment;
RTDL route matching author output;
author option / figure semantics where claimed;
phase-denominator alignment before any performance ratio;
external review before implemented evidence becomes approved evidence.
```

## Completed And Externally Reviewed Work

### Goal5110-5126: Bounded X-HD Same-Input Reproduction

Completed and externally reviewed:

```text
author hd_exec build / run gates;
bounded 2-D and 3-D author JSON gates;
bounded 2-D and 3-D RTDL route gates;
directed-vs-symmetric discriminating fixture;
author HDResult proven to be directed input1 -> input2 for the tested contract.
```

Allowed claim:

```text
RTDL reproduces bounded same-input HDResult values under the tested author
JSON contract.
```

Forbidden claim:

```text
full paper reproduction;
author RT-core algorithm parity;
performance parity;
exact paper dataset reproduction.
```

### Goal5127-5128: Generic System Extraction

Completed and externally reviewed:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest distance witness;
non-Hausdorff facility-service-radius consumer.
```

This is a real RTDL system gain. Hausdorff is now expressed as a composition
of generic primitives rather than a paper-specific core primitive.

### Goal5129: Full-Reproduction Plan

Reviewed with amendments. Durable decision:

```text
matching counts / statistics / paper log labels is not enough to prove exact
input identity;
exact paper dataset status requires file/hash or equivalent provenance;
public reconstructed inputs remain representative Level-B evidence unless
exact identity is proven.
```

## Implemented / Review-Pending Work Since Then

The following work is implemented and recorded, but not all of it is externally
reviewed. Do not silently upgrade it to "approved".

### Level-B Stanford Dragon -> HappyBuddha Representative Route

Strongest same-source public scalar evidence:

```text
source points = 437645
target points = 543652
author hd_exec HDResult ~= 0.12572988867759705
RTDL route distance    ~= 0.12572988629271128
abs diff               ~= 2.38e-9
```

This is strong Level-B representative correctness. It is not exact paper input
reproduction because exact author input bytes / hashes are not proven.

### Route Performance Evolution

Representative route-local evolution on Dragon -> HappyBuddha:

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
Goal5212 fresh full total incl. load     ~= 1.531s
Goal5212 explicit-warm measured total   ~= 0.288s
```

Important caveat:

```text
Goal5211 is exact-value-only for directed HD / max-nearest.
per_source_witness_exact = false.
409376 / 437645 sources, about 93.5 percent, early-aborted in the recorded
route, so per-source witnesses may be approximate.
```

Allowed claim:

```text
The route matches the final directed-HD scalar value against the author rerun
on the representative public input.
```

Forbidden claim:

```text
exact witness reproduction;
paper-log exact input reproduction;
author performance parity.
```

### Figure / Dataset Status

Current figure-level status:

```text
Figure 5:
  Level-B public graphics and geo scalar matches exist.
  Exact paper input identity remains unproved.
  No denominator-aligned performance ratio is authorized.

Figure 7:
  author lb=0 / lb=256 diagnostic pair exists.
  explicit -lb row-denominator parity is not proven.

Figure 8:
  author radius-strategy source/scripts identified.
  checked-in logs are insufficient for full figure reproduction.

Figure 9:
  author logs/scripts audited.
  missing variant denominator prevents reproduction under current evidence.

Figure 10:
  scalability / overlap scripts identified.
  required logs / inputs are missing under current evidence.

Figure 11:
  author memory semantics audited.
  RTDL has shape-like offload telemetry, but denominator alignment is false.
```

## Already Solved Problems

### 1. Directed HD Semantics

Closed by a discriminating fixture:

```text
HDResult = directed input1 -> input2, not symmetric Hausdorff.
```

### 2. Exact Pairwise Route Rejected At Scale

For Dragon -> HappyBuddha:

```text
437645 * 543652 = 237926579540 point pairs
```

Materializing exact pairwise candidate rows is infeasible. This forced the
generic grid / cell-MBR / native-frontier route, which is the right system
direction.

### 3. Hausdorff Kept As App-Level Composition

The system-level extraction is generic:

```text
grid cell descriptors;
cell-MBR descriptors;
native 3-D cell-MBR frontier rows;
nearest-state seed;
inline nearest in traversal;
max-nearest scalar reduction;
optional global-bound early break for directed-HD / max-nearest.
```

No X-HD-specific primitive has been promoted into RTDL core.

### 4. Load-Balance Discussion Has A Real Oracle

Goal5374 produced the author-side `lb=256` oracle for Dragon -> AsianDragon:

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

This eliminated several weaker explanations and made the next task concrete.

## Goal5379-5381 Status

### Goal5379: Generic Active-Query Status-Machine Reference

Implemented / review pending:

```text
src/rtdsl/active_query_status.py
tests/goal5379_active_query_status_machine_reference_test.py
```

Contract:

```text
generic active query state;
multiple offload rows per active query;
miss / completed / aborted counts;
no X-HD names or author-specific identities.
```

Important correction:

```text
The reference now preserves multiple offload rows for one active query.
This is required because author OffloadingSize counts raw appended rows, not
one terminal status per active query.
```

### Goal5380: Frontier Row Bridge

Implemented / review pending:

```text
ACTIVE_QUERY_FRONTIER_BRIDGE_CONTRACT
active_query_status_from_frontier_row_table_numpy_columns
tests/goal5380_active_query_frontier_bridge_test.py
```

Purpose:

```text
map generic cell-MBR frontier row tables into the generic active-query status
reference;
prove the bridge contract is app-neutral and fail-closed.
```

### Goal5381: Full POD Active-Query Bridge Probe

Implemented / review pending.

Files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
tests/goal5381_active_query_frontier_bridge_probe_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_source64_bridge_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_source4096_bridge_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_full_bridge_probe_pod.json
history/internal_docs/goal5381_active_query_frontier_bridge_probe_result_2026-07-10.md
history/internal_docs/call_for_review_goal5381_active_query_frontier_bridge_probe_2026-07-10.md
```

Exit label:

```text
active_query_bridge_mismatch_classified__native_author_status_machine_needed
```

Local validation:

```text
py -m py_compile src/rtdsl/active_query_status.py src/rtdsl/__init__.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py

py -m unittest \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test
```

Observed:

```text
Ran 19 tests OK
```

POD preflight:

```text
POD_OK
container = 45c502cfccb5
GPU       = NVIDIA RTX 4000 Ada Generation
driver    = 550.127.05
```

Full Dragon -> AsianDragon `lb=256` probe:

```text
active_query_count        = 437645
candidate_row_count       = 13129392
bridge_offload_row_count  = 2188225
author_offload_rows       = 27133990
row_count_parity          = false
row_ratio_rtdl_div_author = 0.08064516129032258
author_width_byte_parity  = false
```

Timing:

```text
load_inputs          ~= 0.380s
grid_cell_mbrs       ~= 1.081s
frontier_rows        ~= 11.371s
active_query_bridge  ~= 19.957s
total                ~= 32.794s
```

Interpretation:

```text
The native frontier -> generic active-query bridge path runs at full scale, and
active query count matches the author oracle. However, the current native
frontier stream plus bridge is not the author-compatible -lb status-machine
denominator.
```

This is a useful negative result. It says the next problem is not another
scalar-radius guess and not merely Python bridge runtime. A vectorized bridge
may reduce time, but it will not solve the row-count mismatch by itself.

## Major Unresolved Problems

### 1. Explicit `-lb` Semantics

Current status:

```text
unsupported
```

Reason:

```text
current RTDL native frontier rows do not expose the same raw status-machine
stream as author `-lb`.
```

### 2. Exact Paper Inputs

Current status:

```text
not proven
```

Public and ACM-supplement artifacts support Level-B representative evidence,
but exact paper input file/hash identity has not been established.

### 3. Figure-Level Reproduction

Current status:

```text
partial audits only
```

Several figure scripts/logs were mapped, but full Figure 5/7/8/9/10/11
reproduction is not complete.

### 4. Performance Ratio

Current status:

```text
unauthorized
```

Reason:

```text
author internal Running.AvgTime / ReportedTime;
author process wall;
RTDL route wall;
RTDL total;
cold process vs warm process;
and exact-input vs representative-input denominators are not aligned.
```

## Next Planned Work

### Goal5381 Review

Send for strict review:

```text
history/internal_docs/call_for_review_goal5381_active_query_frontier_bridge_probe_2026-07-10.md
```

Review question:

```text
Does Goal5381 correctly conclude that the current native frontier stream plus
active-query bridge fails author OffloadingSize parity, without overclaiming
explicit -lb support?
```

### Goal5382: Native Status-Machine Stream Design

Recommended next implementation boundary:

```text
design/decision goal first, not another scalar probe.
```

Goal5382 should define a generic, app-neutral native stream contract for
active-query status transitions. Candidate contract:

```text
generic_active_query_status_stream_v1
```

Expected fields:

```text
active_queue_index;
query_row_id;
query_point_id;
cell_id;
point_begin_offset;
point_count;
min_distance;
max_distance;
current_best_distance;
status_code;
```

Expected status concepts:

```text
offload;
completed;
miss;
aborted;
inline;
pruned;
```

Critical semantic requirement:

```text
emit at the same denominator level as raw active-query status transitions,
before the current RTDL frontier stream drops, collapses, or filters rows in a
way that loses author-comparable offload counts.
```

Goal5382 deliverables:

```text
design JSON artifact;
native/Python ABI proposal;
claim-boundary report;
focused tests for app-neutral schema and forbidden app names;
explicit decision: implement native stream next, or close explicit -lb
fail-closed for this release line.
```

### Goal5383: Native Stream Prototype Or Fail-Closed Closeout

If Goal5382 authorizes implementation:

```text
add a new generic native status-stream mode or symbol;
do not name it after X-HD or author paper terms;
surface row-count telemetry through optix_runtime.py;
run bounded and full Dragon -> AsianDragon probes against Goal5374;
require row-count parity before claiming explicit -lb support.
```

If Goal5382 does not authorize implementation:

```text
close explicit -lb as unsupported;
record that RTDL reproduces value-level Level-B routes but not author -lb
offload/status-machine denominators.
```

### Goal5384: Bridge Runtime Optimization Only After Denominator Parity

The Goal5381 bridge took about 19.96s. That is slow, but it is not the primary
semantic blocker. Optimize this only after the native stream denominator is
correct.

Allowed later work:

```text
vectorized active-query bridge;
device-resident offload row compaction;
native prefix/grouped active-query status packing.
```

Not allowed:

```text
using bridge runtime optimization to imply explicit -lb correctness.
```

### Goal5385: Updated X-HD Claim Matrix

After Goal5382/5383:

```text
refresh allowed / forbidden claims;
update memory and X-HD manifest status;
separate value reproduction, Level-B representative route, explicit-lb status,
and full-paper status.
```

## POD Usage Plan

Use the wrapper only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Current known POD:

```text
host      = 213.173.108.24
port      = 13502
container = 45c502cfccb5
GPU       = NVIDIA RTX 4000 Ada Generation
driver    = 550.127.05
```

Remote workspace caveat:

```text
/tmp/rtdl_goal5364 is not a git checkout.
Sync changed files and rebuild OptiX before native route probes.
```

Expected POD usage:

```text
Goal5382:
  none required if design-only, except optional native source inspection.

Goal5383:
  required for native build and Dragon -> AsianDragon row-parity probes.

Goal5384:
  required only if runtime optimization follows semantic parity.
```

## Completion Forecast

Short path if Goal5382 decides to close explicit `-lb` fail-closed:

```text
Goal5381 review;
Goal5382 decision;
Goal5385 status matrix;
close current X-HD line as value/Level-B representative only, not full paper.
```

Long path if native status stream is implemented:

```text
Goal5381 review;
Goal5382 design;
Goal5383 native stream implementation and POD row-parity gate;
Goal5384 runtime optimization if parity succeeds;
Goal5385 updated claim matrix;
additional figure-specific gates only after explicit -lb semantics are proven.
```

Estimated engineering effort:

```text
design-only closeout path: 1-2 focused goals;
native status-stream path: at least 3-5 focused goals, plus POD build time and
strict review.
```

## Final Midterm Conclusion

The project is not stuck on "what is Hausdorff?" anymore. It solved that.

It is now blocked on a narrower and more serious systems question:

```text
Can RTDL expose a generic active-query status stream whose row denominator
matches the author's explicit load-balance/offload state machine?
```

Until that is solved:

```text
full X-HD paper reproduction remains incomplete;
explicit -lb remains unsupported;
Figure 7 / Figure 11 reproduction remains unauthorized;
performance parity remains unauthorized.
```

But the work has produced real RTDL system value:

```text
generic nearest/max-nearest extraction;
generic cell-MBR frontier traversal;
generic inline nearest and global-bound max-nearest reduction;
generic heavy/offload telemetry;
generic active-query status-machine reference and bridge.
```

The next decision is therefore sharp:

```text
either build the generic native active-query status stream, or honestly close
the explicit -lb path as unsupported for this X-HD reproduction line.
```
