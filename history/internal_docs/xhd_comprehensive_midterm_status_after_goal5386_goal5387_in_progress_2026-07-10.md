# X-HD Comprehensive Midterm Status After Goal5386 / Goal5387 In Progress

Date: 2026-07-10

## Executive Summary

The X-HD line is in a strong but not-finished state.

What is solid:

```text
bounded same-input X-HD scalar correctness is complete and externally reviewed;
generic nearest / witness / max-nearest system extraction is complete and reviewed;
Level-B public representative correctness on Dragon -> HappyBuddha is strong;
the RTDL route has improved from multi-second route time to sub-second scalar route time;
the unresolved author -lb / heavy-offload problem is now isolated to status-machine semantics.
```

What is not done:

```text
full X-HD paper reproduction is not complete;
exact paper dataset identity is not proven;
Figure-level reproduction is not complete;
author-vs-RTDL performance parity or speedup is not authorized;
explicit author -lb support is not implemented in RTDL.
```

The current hard blocker is the `-lb` status-machine denominator.  The author
oracle says Dragon -> AsianDragon with `lb=256` emits:

```text
ActiveInQueueSize              = 437645
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
```

Current RTDL surfaces do not match that denominator:

```text
Goal5381 bridge offload rows       = 2188225
Goal5383 active-initial-best rows  = 2188225
row_count_parity                   = false
```

Goal5386 has completed the author trace v2 patch-plan / hook-validation step.
Goal5387 has just started: an author-tree patcher file exists in the worktree,
but Goal5387 is not yet validated, not yet built on POD, and not yet a completed
goal.

## Current Source Of Truth

This report supersedes the following day-to-day handoff report:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5385_2026-07-10.md
```

Older reports remain historical evidence and should not be deleted.

Current durable-memory anchors:

```text
AGENTS.md
memory/project-facts.md
memory/architecture.md
memory/decisions.md
memory/progress.md
memory/todo.md
memory/known-bugs.md
memory/roadmap.md
```

## Overall Goal

The active goal remains:

```text
complete an honest X-HD paper reproduction as far as evidence allows,
while extracting reusable RTDL system features and keeping paper-specific
logic in the paper app.
```

That goal has two separate axes:

1. Reproduction evidence:

```text
bounded same-input correctness -> done;
same-source Level-B representative correctness -> strong;
exact paper dataset reproduction -> not done;
figure/performance reproduction -> not done.
```

2. System extraction:

```text
nearest/witness/max-nearest primitives -> done/reviewed;
grid/cell-MBR/frontier route assets -> implemented/review pending;
active-query/status-machine reference assets -> implemented/review pending;
author-like -lb native/status-stream parity -> not done.
```

## Completed And Externally Reviewed

### Bounded X-HD Correctness

Goals5111-5126 close the bounded same-input X-HD scalar value line.

Key meaning:

```text
RTDL can match author HDResult on bounded same-input fixtures.
Goal5126 proves the author contract is directed input1 -> input2, not symmetric.
```

Key non-meaning:

```text
not full paper reproduction;
not exact paper dataset identity;
not author RT-core algorithm parity;
not a performance claim.
```

### Generic Nearest / Witness / Max-Nearest Extraction

Goals5127-5128 are reviewed and approved.

System assets:

```text
pairwise_l2_distance_candidate_rows
nearest_witness
max_nearest_distance_witness
non-Hausdorff facility/service-radius consumer
```

Architectural point:

```text
Hausdorff is an app-level composition.
RTDL owns generic nearest/witness/reduction primitives.
```

## Implemented / Review Pending

The X-HD line has a large implemented backlog from Goals5130-5386.  Do not mark
these goals externally approved until review files exist.

Important implemented categories:

```text
paper target matrix and dataset provenance work;
Stanford graphics Level-B acquisition and route gates;
generic grid-cell and cell-MBR descriptors;
native 3-D cell-MBR frontier producers;
route-local performance improvements;
Figure 5/7/8/9/10/11 audits and no-go / blocked decisions;
active-query and status-machine references;
author -lb oracle and RTDL mismatch assessments;
author trace v2 schema and patch-plan.
```

## Best Current Correctness Evidence

The strongest Level-B public representative case is still:

```text
source = Stanford Dragon public PLY
target = Stanford HappyBuddha public PLY
source points = 437645
target points = 543652
```

Value evidence:

```text
author hd_exec HDResult = 0.12572988867759705
RTDL route distance     = 0.12572988629271128
absolute difference     ~= 2.38e-9
```

This is strong same-source evidence.  It is not exact paper dataset reproduction
because author paper input bytes / hashes are still not available.

## Performance Evolution

The route-local Dragon -> HappyBuddha scalar route has improved substantially:

```text
Goal5188 initial scalable route      ~= 7.30s
Goal5191 inline512 route             ~= 3.65s
Goal5195 intersection-prune route    ~= 2.6s
Goal5196 dense local-grid route      ~= 2.26s
Goal5203 matrix-input route          ~= 1.24s
Goal5204 linear max reducer route    ~= 1.17-1.18s
Goal5211 global-bound fresh route    ~= 0.849s
Goal5211 explicit-warm route median  ~= 0.362s
Goal5212 full total including load   ~= 1.531s
Goal5212 warm measured case total    ~= 0.288s
```

Critical caveat:

```text
Goal5211/5212 are exact for the final directed HD scalar value, not for every
per-source nearest witness.

per_source_witness_exact = false
early_aborted_sources    = 409376 / 437645
```

Therefore the fast route is a directed-HD / max-nearest scalar route.  It must
not be marketed as an exact nearest-witness route.

No author-vs-RTDL performance ratio is authorized.  The author internal
`Running.AvgTime`, author process wall, RTDL route wall, RTDL total, cold
process, warm process, and prepared/replay regimes are different denominators.

## Figure And Dataset Status

### Exact Paper Inputs

Status:

```text
not acquired / not proven
```

Rules:

```text
matching counts, MBRs, Gini, logs, or scalar HDResult is not exact dataset identity;
exact paper input status requires file/hash provenance or accepted deterministic regeneration.
```

### Figure 5

Status:

```text
partial Level-B scalar candidates exist;
no full Figure 5 reproduction;
no performance ratio.
```

Dragon -> HappyBuddha is the strongest current graphics candidate.

### Figures 7 And 11

Status:

```text
blocked by -lb / heavy-offload status-machine semantics.
```

Author memory and worklist denominators are not aligned with RTDL's current
frontier-row / worklist telemetry.

### Figures 8 / 9 / 10

Status:

```text
author source/scripts/logs audited;
current checked-in log denominators are incomplete or missing;
not reproduced.
```

## The Main Solved Problems

### 1. Directed-vs-Symmetric Ambiguity

Resolved by a discriminating fixture:

```text
directed a -> b = 0.5
directed b -> a = 9.0
symmetric       = 9.0
author matches directed a -> b
```

### 2. Naive Pairwise Explosion

The old materialized pairwise path is not viable for full public inputs:

```text
Dragon x HappyBuddha pair count = 237926579540
```

The scalable route avoids materializing all pairs.

### 3. Generic System Extraction

X-HD pressure produced reusable RTDL features:

```text
generic nearest / witness / max-nearest primitives;
coordinate matrix front doors;
grid-cell and cell-MBR descriptors;
native 3-D cell-MBR frontier rows;
active-query and status-machine reference contracts.
```

### 4. Wrong `-lb` Explanations Eliminated

Rejected explanations include:

```text
scalar radius mismatch alone;
host materialization / sort artifact;
raw no-inline kind2 rows;
existing global-bound early break as author cmax2 abort;
heavy-before-inline-prune branch-order variant;
active-initial-best single-pass prune variant.
```

These no-go results are useful because they isolate the remaining problem as a
real status-machine / multi-round feedback issue.

## The Main Unsolved Problems

### 1. Explicit Author `-lb` Semantics

Author `lb=256` offload rows:

```text
27133990
```

Current RTDL bridge rows:

```text
2188225
```

This is not a performance issue first.  It is a denominator / semantic mismatch.
Making the current bridge faster would still leave the wrong row count.

### 2. Strong Author Trace Needed

Goal5374 gives a count oracle, but Goal5385/5386 show that a stronger trace is
needed to validate a real multi-round RTDL status stream:

```text
cmin2/current-best hashes and samples;
raw offload row hash and sample;
miss/completed status counts;
cmax2 before/after;
loadBalanceProcessing feedback counts.
```

### 3. Native RTDL Status Stream

RTDL has generic active-query status-machine reference contracts, but no native
status stream has matched the author oracle.  Explicit `-lb` remains fail-closed.

### 4. Exact Dataset Provenance

Even if RTDL matches public candidates, full paper reproduction still needs
exact input provenance or accepted regeneration.

## Goal5386 Status

Goal5386 is implemented / review pending.

Files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5386_author_trace_v2_patch_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5386_author_trace_v2_patch_plan.json
tests/goal5386_author_trace_v2_patch_plan_test.py
history/internal_docs/goal5386_xhd_author_trace_v2_patch_plan_result_2026-07-10.md
history/internal_docs/call_for_review_goal5386_xhd_author_trace_v2_patch_plan_2026-07-10.md
```

Result:

```text
exit_label = author_trace_v2_patch_plan_ready__implementation_next
all_hooks_found = true
all_required_fields_covered = true
missing_files = []
missing_hooks = []
uncovered_fields = []
```

Focused validation:

```text
py -m unittest tests.goal5386_author_trace_v2_patch_plan_test tests.goal5385_author_trace_v2_spec_test tests.goal5384_multiround_status_requirements_test tests.goal5384_multiround_active_query_status_test
Ran 16 tests OK
```

Boundary:

```text
Goal5386 is a dry-run hook-validation artifact.
It does not implement the author v2 trace.
It does not execute the author v2 trace on POD.
```

## Goal5387 Current In-Progress State

Goal5387 is not complete.

Current worktree state:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace_v2.py
```

This file is an initial author-tree patcher for the trace-v2 schema.  It still
needs:

```text
local instrumentation tests;
patch-on-clean-author-source verification;
POD author-tree inspection / clean patch path;
POD author build;
Dragon -> AsianDragon lb=256 author run;
result artifact;
goal report;
call-for-review;
memory update.
```

Until those pass, do not describe Goal5387 as implemented.

## Next Planned Work

### Goal5387 - Author Trace V2 Execution

Purpose:

```text
apply app-owned author trace v2 instrumentation;
build author hd_exec on POD;
run Dragon -> AsianDragon lb=256;
emit rtdl.goal5385.author.lb_status_trace.v2;
compare basic counts against Goal5374.
```

Required validation:

```text
active_in_queue_size = 437645
raw_offload_rows_before_sort_reduce = 27133990
StatusOffloadingAppendCount = 27133990
trace schema = rtdl.goal5385.author.lb_status_trace.v2
```

Required new fields:

```text
cmin2_initial_hash / samples
cmin2_after_ray_hash / samples
cmin2_after_load_balance_hash / samples
raw_offload_row_hash / sample point ids / sample cell ids
status_count_miss
status_count_completed
cmax2_before_ray
cmax2_after_ray
cmax2_after_load_balance
load_balance_group_count
load_balance_feedback_update_count
```

Forbidden claims:

```text
explicit -lb support;
RTDL row-count parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core parity;
performance ratio;
full X-HD paper reproduction.
```

### Goal5388 - RTDL Counterpart Decision

Only after Goal5387 succeeds, decide whether to:

```text
implement native generic multi-round status stream;
compare RTDL raw stream to author trace v2;
or close explicit -lb as fail-closed for the current line.
```

Do not optimize the CPU bridge before the row denominator is right.

### Goal5389 - Native Status-Stream Prototype Or Closeout

If Goal5388 authorizes implementation, Goal5389 should be the first native
generic multi-round status-stream prototype.  It must compare:

```text
raw offload row count;
row identity hash / sample;
cmin2/current-best state hash / sample;
miss/completed/offload/aborted counts;
load-balance feedback counts.
```

If it cannot be kept generic, the correct result is fail-closed closeout, not an
X-HD-specific core primitive.

## POD Usage Expectations

Use POD only when native/author build or large data execution is required.

For Goal5387, POD is required because the author patch must compile and run
against Dragon -> AsianDragon `lb=256`.

Use only the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Do not use naked SSH.

Before calling the POD broken:

```text
run wrapper preflight;
verify the pinned key path;
inspect remote author tree state;
record the actual failure.
```

Known remote caveat:

```text
/tmp/rtdl_goal5364 is not a git checkout.
Changed files must be uploaded and native/OptiX artifacts rebuilt explicitly.
```

Goal5387 may need either:

```text
a clean remote author tree; or
a fresh copy / reset of the author tree before applying trace v2;
```

because older author instrumentation may already exist in the POD tree.

## Review Status And Debt

Externally reviewed:

```text
Goals5111-5128 core bounded/system extraction line.
```

Implemented / review pending:

```text
large X-HD Level-B route and figure/dataset/audit body through Goal5386.
```

Immediate review packet candidates:

```text
Goals5381-5386 as the current -lb/status-machine packet;
Goal5387 separately after POD execution, if completed.
```

Do not mark review-pending goals as approved until actual review files exist.

## Claim Boundary

Allowed summary:

```text
X-HD has a reviewed bounded same-input correctness line, reviewed generic
nearest/witness system extraction, strong Level-B public representative scalar
evidence, and a sharply isolated unresolved -lb status-machine problem.
Goal5386 makes author trace v2 implementation ready. Goal5387 is the next
author-POD execution step.
```

Forbidden summaries:

```text
full X-HD paper reproduction is complete;
RTDL matches author X-HD RT-core algorithm;
RTDL supports explicit -lb;
RTDL reproduces Figure 7 or Figure 11;
RTDL has author performance parity;
Goal5387 is done;
Goal5211 exacts all per-source witnesses;
public Stanford files are exact paper input files.
```

## Expected Path To Completion

Short term:

```text
finish Goal5387 author trace v2 execution on POD;
write Goal5387 result + call-for-review;
update memory;
send Goals5381-5387 for strict review.
```

Middle term:

```text
use the stronger author v2 trace to choose between:
  native generic multi-round status stream;
  further author oracle expansion;
  explicit fail-closed -lb closeout.
```

Long term:

```text
continue exact dataset acquisition / provenance work;
do not claim figure-level reproduction until exact inputs and denominator
alignment are established;
keep extracting generic RTDL APIs only when non-app semantics are proven.
```

Rough effort expectation:

```text
Goal5387 local patcher tests: one focused local goal.
Goal5387 POD build/run: one POD goal, sensitive to author tree cleanliness.
RTDL native status-stream counterpart: at least one design goal plus one or
more POD implementation goals.
Full paper reproduction: still blocked by exact inputs and figure denominators;
not a one-goal finish from the current state.
```
