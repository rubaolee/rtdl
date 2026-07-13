# X-HD Comprehensive Midterm Status After Goal5385

Date: 2026-07-10

## Executive Summary

The X-HD paper-reproduction line has made strong progress, but it is not full
paper reproduction yet.

The project has achieved:

```text
bounded same-input X-HD scalar correctness;
reviewed generic nearest / witness / max-nearest system extraction;
strong Level-B public representative scalar correctness on Dragon -> HappyBuddha;
substantial route-local performance improvement on that representative route;
an app-owned hd_exec-compatible value surface for supported bounded routes;
generic active-query / status-machine reference contracts for the unresolved -lb line.
```

The current strongest X-HD evidence is still the Level-B public Stanford
Dragon -> HappyBuddha route:

```text
source points = 437645
target points = 543652
author hd_exec HDResult ~= 0.12572988867759705
RTDL route distance    ~= 0.12572988629271128
absolute difference    ~= 2.38e-9
```

The best scalar-value route has moved far from the original multi-second route:

```text
Goal5188 initial scalable route      ~= 7.30s
Goal5191 inline512 route             ~= 3.65s
Goal5195 intersection-prune route    ~= 2.6s
Goal5196 dense local-grid route      ~= 2.26s
Goal5203 matrix-input route          ~= 1.24s
Goal5204 linear max reducer route    ~= 1.17-1.18s
Goal5211 global-bound fresh route    ~= 0.849s
Goal5211 explicit-warm route median  ~= 0.362s
Goal5212 full total incl load        ~= 1.531s
Goal5212 warm measured case total    ~= 0.288s
```

But that fast route has a strict correctness boundary:

```text
final directed HD scalar value exact against author rerun;
per-source witness exactness not guaranteed;
per_source_witness_exact = false;
early-aborted sources = 409376 / 437645.
```

The current hardest unresolved technical problem is explicit author `-lb` /
heavy-cell offload behavior.  Goal5374 gives a real author count oracle, but
Goals5381 and 5383 show the current RTDL frontier/status surfaces do not match
the author raw offload denominator:

```text
Goal5374 author lb=256 oracle:
  ActiveInQueueSize              = 437645
  RawOffloadRowsBeforeSortReduce = 27133990
  RawOffloadRowsAuthorWidthBytes = 217071920

Goal5381 current frontier bridge:
  active_query_count             = 437645
  bridge_offload_row_count       = 2188225
  row_ratio_rtdl_div_author      = 0.08064516129032258
  row_count_parity               = false

Goal5383 active-initial-best probe:
  bridge_offload_row_count       = 2188225
  row_ratio_rtdl_div_author      = 0.08064516129032258
  row_count_parity               = false
```

Goal5384 moves the line to a generic multi-round active-query status reference.
Goal5385 then defines the stronger author trace v2 oracle needed before the
next native parity attempt.  Neither goal claims explicit `-lb` support.

## Current Reproduction Status

### Level A - Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

Meaning:

```text
RTDL and author agree on bounded same-input HDResult values.
Goal5126 proves the author contract is directed input1 -> input2, not symmetric.
```

Not implied:

```text
full paper reproduction;
exact paper dataset identity;
author RT-core algorithm parity;
performance parity.
```

### Level B - Same-Source Representative Correctness

Status:

```text
strongest active line; implemented extensively; later goals largely review pending
```

Main evidence:

```text
Dragon -> HappyBuddha public Stanford route matches author rerun scalar.
Several additional graphics / geo / ModelNet-style Level-B candidates exist.
```

Current strongest route:

```text
Dragon source points      = 437645
HappyBuddha target points = 543652
author HDResult           ~= 0.12572988867759705
RTDL distance             ~= 0.12572988629271128
```

Key caveat:

```text
same-source representative evidence is not exact paper dataset reproduction.
```

### Level C - Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Reason:

```text
exact paper input files / hashes are still unavailable;
matching counts, MBRs, logs, or scalar values is not enough;
public data can be Level B only unless file/hash provenance or accepted
deterministic regeneration is obtained.
```

### Level D - Figure / Performance Reproduction

Status:

```text
not complete
```

Current position:

```text
Figure 5: partial Level-B scalar coverage; no denominator-aligned ratio.
Figure 6: pruning diagnostics exist; no full figure reproduction.
Figure 7: blocked by explicit -lb / heavy-cell status-machine parity.
Figure 8: radius/tune-radius semantics partly mapped; figure not closed.
Figure 9: author log denominator incomplete for expected auto-tune variants.
Figure 10: checked-in scalability matrix unavailable.
Figure 11: memory denominator not aligned; RTDL worklist telemetry is not author WL / WL Heavy Peak parity.
```

No author-vs-RTDL performance ratio is currently authorized.

## Completed Work

### 1. Scaffold, Provenance, And Claim Boundaries

Completed:

```text
X-HD paper-app scaffold;
author repository / CLI / JSON contract provenance;
manifest status model;
separation from the old hausdorff_xhd benchmark line.
```

Key decision:

```text
old benchmark assets may inform implementation, but are not automatically paper reproduction.
```

### 2. Bounded Correctness And Directed Semantics

Completed:

```text
author hd_exec build/run gates;
bounded 2-D / 3-D author JSON gates;
bounded RTDL route gates;
directed-vs-symmetric discriminator.
```

The discriminator matters because it prevents silently comparing a directed
author output against a symmetric RTDL route.

### 3. Generic RTDL System Extraction

Completed / implemented:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest witness / reducer;
non-Hausdorff facility/service-radius consumer;
grid-cell candidate descriptors;
cell-MBR descriptors;
nearest-state frontier APIs;
native 3-D cell-MBR frontier front doors;
coordinate-matrix front doors;
linear finite max-nearest reducer;
active-query status-machine CPU/reference layer;
multi-round active-query status reference.
```

This is the main language/system payoff from X-HD: Hausdorff remains an app
composition, while the reusable parts become RTDL primitives.

### 4. Scalable Level-B Route

Completed / implemented:

```text
full public Dragon -> HappyBuddha route;
native cell-MBR frontier route;
local-grid seed;
inline-nearest native payload;
payload-current-best pruning;
intersection-stage pruning;
dense cell lookup;
matrix input loading;
linear max-nearest reduction;
explicit warmup protocol;
global-bound early break for max-nearest / directed-HD scalar.
```

Important boundary:

```text
Goal5211 / Goal5212 are exact for the final directed HD value, not exact
per-source witnesses.
```

### 5. Author-Compatible App Entrypoint Surface

Completed / implemented:

```text
app-owned hd_exec-compatible wrapper;
author-like JSON fields for supported value route;
explicit fail-closed behavior for unsupported options.
```

Boundary:

```text
This is app compatibility, not author RT-core parity.
```

### 6. `-lb` / Heavy-Offload Investigation

Completed / implemented through Goal5385:

```text
author source audit;
author count oracle Goal5374;
RTDL status candidate telemetry;
frontier bridge Goal5381;
native status-stream design Goal5382;
active-initial-best no-go Goal5383;
multi-round active-query reference Goal5384;
author trace v2 specification Goal5385.
```

The line is now correctly focused on status-machine semantics rather than
another one-pass prune tweak.

## Major Problems Solved

### S1. Directed Hausdorff Definition

The project no longer assumes the author computes symmetric HD.  Goal5126
proves the tested author contract is directed input1-to-input2.

### S2. Generic System Extraction

The X-HD pressure test has produced real generic RTDL APIs instead of an
X-HD-only core primitive.

### S3. Pairwise Materialization Avoidance

The route no longer depends on materializing hundreds of billions of point
pairs for large public graphics candidates.

### S4. Route-Local Performance

The main Level-B scalar route moved from several seconds to sub-second route
time for the exact final scalar value, while keeping claim boundaries explicit.

### S5. Failed Hypotheses Were Killed

Rejected with data:

```text
lower inline thresholds;
static cell order;
trace tmax scalar bound;
native CUDA seed wrapper;
prepared cell-MBR accel-build caching;
scalar-radius-only -lb;
raw kind2 -lb;
heavy-before-inline-prune;
active-initial-best prune.
```

## Major Problems Still Open

### U1. Exact Paper Dataset Provenance

Full paper reproduction cannot be claimed until exact paper inputs are obtained
or accepted deterministic regeneration is proven.

### U2. Full Figure Matrix

The paper figures are not reproduced.  The project has partial Level-B value
evidence and several figure-specific audits, not a full figure matrix.

### U3. Performance Denominator Alignment

A performance ratio is still not fair because the denominators differ:

```text
author internal Running.AvgTime;
author process wall;
RTDL route time;
RTDL total / case total;
cold process;
warm long-lived process;
prepared / explicit warmup route.
```

### U4. Explicit `-lb` / Heavy-Offload Parity

This is the current hard technical blocker.  Author `-lb` is not a simple
frontier-row count.  It depends on dynamic status-machine state:

```text
active in_queue indices;
per-source cmin2 / current-best state;
kInit / kOffloading / kAborted status transitions;
cmax2 MBR abort;
miss queue behavior;
raw offload append before sort/reduce;
loadBalanceProcessing feedback.
```

Goal5384 provides a generic multi-round reference.  Goal5385 specifies the
stronger author oracle needed next.  The actual author v2 trace is not yet
implemented or executed.

### U5. Review Debt

Only the early X-HD bounded and system-extraction work is externally reviewed.
Many later goals are implemented / review pending.  Do not upgrade them to
approved without a real review.

## Current Review Status

Externally reviewed and approved:

```text
Goal5110;
Goals5111-5126;
Goals5127-5128;
Goal5129 plan with amendment incorporated.
```

Implemented / review pending:

```text
Goals5130-5385, unless a separate review file says otherwise.
```

Immediate review packet for the active `-lb` line:

```text
history/internal_docs/call_for_review_goal5381_active_query_frontier_bridge_probe_2026-07-10.md
history/internal_docs/call_for_review_goal5382_xhd_native_status_machine_stream_design_2026-07-10.md
history/internal_docs/call_for_review_goal5383_active_initial_best_status_probe_2026-07-10.md
history/internal_docs/call_for_review_goal5384_xhd_multiround_active_query_status_2026-07-10.md
history/internal_docs/call_for_review_goal5385_xhd_author_trace_v2_spec_2026-07-10.md
```

## POD Status And Usage Expectations

Use the wrapper only:

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

Remote workspace:

```text
/tmp/rtdl_goal5364
```

Caveat:

```text
the remote workspace is not a git checkout;
changed files must be uploaded explicitly;
native OptiX must be rebuilt with make build-optix before native route probes.
```

POD is needed for:

```text
author v2 trace execution;
native RTDL status-stream probes;
Dragon -> AsianDragon lb=256 row-parity comparison;
any OptiX route validation.
```

POD is not needed for:

```text
documentation;
schema/spec goals;
local CPU/reference tests.
```

## Planned Work

### P0. Review Current `-lb` Packet

Send Goals5381-5385 for strict review.

Reviewer questions:

```text
Did Goal5381 correctly show active-query count aligns but offload-row count fails?
Did Goal5382 correctly reject bridge runtime as the semantic fix?
Did Goal5383 correctly kill active-initial-best classification?
Does Goal5384 define the right generic multi-round reference?
Does Goal5385 specify a sufficient author v2 oracle?
```

### P1. Goal5386 - Author Trace V2 Patch Plan / Hook Validation

Recommended immediate next work.

Purpose:

```text
turn Goal5385's author trace v2 schema into a fail-closed source-hook plan
against the pinned author source before attempting a live POD patch.
```

Expected output:

```text
validate author source hook anchors;
map each Goal5385 required field to a concrete author source hook;
record patch targets and marker;
emit dry-run patch-plan artifact;
do not claim author v2 trace implemented or executed.
```

Exit labels:

```text
author_trace_v2_patch_plan_ready__implementation_next
author_trace_v2_hook_gap_found__revise_spec_or_fail_closed
```

### P2. Goal5387 - Author Trace V2 Implementation / POD Run

Only after P1 hook validation.

Purpose:

```text
apply app-owned instrumentation to the external author tree;
run Dragon -> AsianDragon lb=256;
produce author trace v2 JSON;
compare v2 row/hash/sample fields against Goal5374 count oracle.
```

Success requirements:

```text
active_in_queue_size = 437645;
raw_offload_rows_before_sort_reduce = 27133990;
status/offload counts consistent with Goal5374;
cmin2 hashes/samples present;
raw offload row hash/sample present;
loadBalanceProcessing group / feedback counts present.
```

### P3. Goal5388 - Native Generic Multi-Round Status Stream

Only after either Goal5387 exists or a reviewed decision accepts a weaker
oracle.

Purpose:

```text
implement a native generic active-query status stream;
compare raw offload row count and state hashes/samples to the author v2 oracle;
keep X-HD names out of RTDL core;
keep explicit -lb fail-closed unless parity is achieved and reviewed.
```

### P4. Goal5389 - Explicit `-lb` Decision

Possible outcomes:

```text
explicit_lb_supported_for_bounded_level_b_diagnostic_after_review
explicit_lb_fail_closed_author_status_denominator_not_reproduced
native_status_stream_needs_more_author_trace
```

This goal should refresh the claim matrix and decide whether Figure 7 / Figure
11 work can progress or must remain blocked.

### P5. Resume Broader Full-Paper Plan

After `-lb` is resolved or closed:

```text
continue exact input acquisition;
extend figure-level candidate matrix only where input provenance exists;
keep performance ratio forbidden until denominators align;
prepare a consolidated review packet for Goals5130-5389.
```

## Rough Schedule

This is a planning estimate, not a promise.

```text
0.5 day:
  Goal5386 hook validation / dry-run patch plan;
  local tests and report.

0.5-1 day with POD:
  Goal5387 author v2 patch application and Dragon -> AsianDragon run;
  artifact download and validation.

1-2 days:
  Goal5388 native generic multi-round status stream, if author v2 oracle is good.

0.5 day:
  Goal5389 decision / claim-matrix refresh.

unknown:
  exact paper input acquisition;
  full figure matrix;
  denominator-aligned performance reproduction.
```

## Allowed Summary

Allowed:

```text
X-HD is a strong Level-B same-source representative reproduction and system
extraction line.  RTDL matches author rerun scalar HDResult on the main public
Dragon -> HappyBuddha route and has extracted reusable nearest / witness /
max-nearest / grid-cell / cell-MBR / active-query status primitives.  The
fastest route is exact for the final directed HD value but not exact for all
per-source witnesses.  Exact paper input reproduction and figure-level
performance reproduction remain open.  The main current technical blocker is
explicit author -lb / heavy-offload status-machine parity; Goal5384/5385 set up
the generic multi-round reference and stronger author trace v2 oracle needed
for the next attempt.
```

Forbidden:

```text
full X-HD paper reproduction is complete;
RTDL matches author performance;
RTDL supports explicit author -lb;
Figure 7 / Figure 11 are reproduced;
public Stanford files are exact paper inputs;
Goal5211 proves exact per-source witnesses;
Goal5384/5385 prove row-count parity;
Goal5385 implemented or executed author v2 tracing.
```

## Immediate Command Checklist

Before any POD work:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Before any performance or parity claim:

```text
state dataset identity level;
state runtime regime;
state phase denominator;
state review status;
state per_source_witness_exact true/false;
state explicit -lb support as fail-closed unless row parity is proven.
```
