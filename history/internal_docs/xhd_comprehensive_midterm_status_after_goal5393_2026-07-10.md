# X-HD Comprehensive Midterm Status After Goal5393

Date: 2026-07-10

## Status Label

```text
level_b_scalar_strong__generic_system_extraction_real__explicit_lb_denominator_target_selected__full_paper_not_complete
```

## Executive Summary

X-HD full paper reproduction is still **not complete**.

The project has, however, reached a strong and useful intermediate point:

1. Bounded X-HD same-input value reproduction is complete and externally
   reviewed through Goal5126.
2. The X-HD app has already forced real RTDL system extraction: generic
   nearest/witness/max-nearest primitives, grid/cell-MBR descriptors,
   native 3-D cell-MBR frontier collection, global-bound max-nearest early
   break, active-query status references, multi-round status references, and
   author/RTDL status-trace comparison helpers.
3. The strongest current Level-B scalar correctness line is public Stanford
   Dragon -> HappyBuddha:

```text
source points = 437,645
target points = 543,652

author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
abs diff        ~= 2.38e-9
```

4. The scalar route has been accelerated substantially while preserving the
   author HDResult on that Level-B workload. With the explicit global-bound
   early-break route:

```text
fresh route wall             ~= 0.849s
fresh full total incl. load  ~= 1.531s after Goal5212
explicit-warm route median   ~= 0.362s after Goal5211
explicit-warm case total     ~= 0.288s after Goal5212
```

These numbers are route/regime specific and are **not** author-vs-RTDL paper
speedup ratios.

5. The current hard blocker is explicit X-HD `-lb` behavior. The author
   instrumented trace v2 is now strong enough to expose the denominator:

```text
active query count           = 437,645
author raw offload rows      = 27,133,990
author rows / active         = 62
```

Current RTDL surfaces still do not match that author status stream. Goal5392
reconciled the known surfaces, and Goal5393 selected the next target:

```text
current bridge rows          =  2,188,225 =  5 * active_count
default / inline raw kind2   = 21,006,960 = 48 * active_count
full-cover lb256 surface     = 24,508,120 = 56 * active_count
author rows                  = 27,133,990 = 62 * active_count
remaining full-cover delta   =  2,625,870 =  6 * active_count
```

The selected next gate is:

```text
generic_full_cover_delta_status_probe
```

This is a target-selection result, not explicit `-lb` support.

## Governing Principle

RTDL is a general spatial/dataflow language. X-HD is a paper reproduction app
and a stress test for RTDL system abstractions.

```text
RTDL core owns:
  generic spatial/dataflow primitives;
  generic columnar descriptors and row schemas;
  generic native traversal / frontier / status contracts;
  generic partner-facing execution contracts.

X-HD app owns:
  paper inputs and provenance;
  author hd_exec wrappers and patched-author instrumentation;
  paper figure labels;
  comparator logic and tolerances;
  route choices and claim boundaries.
```

No X-HD-specific option, paper figure, author JSON field, or paper-only
tolerance may become RTDL core semantics unless it is redesigned as a generic
API and validated outside the X-HD app.

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
directed-vs-symmetric Hausdorff ambiguity is resolved;
bounded correctness is not full paper reproduction.
```

### Level B: Same-Source Representative Correctness

Status:

```text
strong scalar evidence, not full paper reproduction
```

Strongest graphics workload:

```text
public Stanford Dragon -> HappyBuddha
source points = 437,645
target points = 543,652
author rerun HDResult = 0.12572988867759705
RTDL HDResult         = 0.12572988629271128
abs diff              ~= 2.38e-9
```

Important caveat:

```text
Goal5211/5212 fast scalar route is exact-value-only.
per_source_witness_exact = false
early-aborted sources = 409,376 / 437,645
```

The route is valid for directed-Hausdorff / max-nearest scalar value. It is not
valid as an exact per-source nearest-witness table for every source.

Other Level-B evidence exists for graphics and geo candidates, including
WaterBodies -> BlockGroups with a corrected `n_points_cell=8` author
denominator. Those lines remain Level-B because exact paper input bytes/hashes
are not available.

### Level C: Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Exact dataset status requires author input files/hashes, byte-identical
regeneration, or externally accepted deterministic public-source equivalence.
Matching point counts, MBRs, statistics, paths, paper-log HDResult, or author
rerun value is evidence, but not exact input identity.

Current strongest exact-provenance facts:

```text
graphics:
  several public Stanford candidates match paper-log / author values, but
  author input file hashes and exact preprocessing are unavailable.

geo:
  WaterBodies -> BlockGroups is the strongest public candidate after
  n_points_cell=8 correction, but exact author WKT hashes are still missing.

BrATS / Census / OSM:
  remain acquisition or provenance blocked.
```

### Level D: Figure-Level And Performance Reproduction

Status:

```text
not complete
```

Figure disposition:

```text
Figure 5:
  Level-B graphics and bounded/full-public geo scalar evidence exist.
  Exact inputs and full matrix are not complete.
  No denominator-aligned author-vs-RTDL performance ratio is authorized.

Figure 7:
  explicit -lb / load-balance behavior is not reproduced.
  Current work is trying to align the author raw offload/status denominator.

Figure 8:
  author radius-tuning matrix/log denominator is missing.

Figure 9:
  author logs/scripts do not provide the full variant denominator required.

Figure 10:
  author scale/overlap logs are not available as a reproducible matrix.

Figure 11:
  memory denominator remains not aligned. Generic worklist telemetry exists,
  but author WL / WL Heavy Peak equivalence is not established.
```

## System Assets Extracted From X-HD

X-HD has not only produced an app route. It has pushed reusable RTDL system
surface forward.

### Generic Nearest / Witness / Reduction

Extracted and reviewed through Goals5127-5128:

```text
pairwise_l2_distance_candidate_rows
nearest_witness
max_nearest_distance_witness
```

The non-Hausdorff facility/service-radius consumer in Goal5128 closed the
genericity loop.

### Generic Grid / Cell-MBR Route

Implemented through the 5138-5212 line:

```text
grid cell descriptors;
cell-MBR candidate rows;
nearest-state frontier split;
native 3-D cell-MBR frontier collection;
row-table-only / active-row-only streaming modes;
native inline-nearest payload;
payload-current-best pruning;
intersection-stage current-best pruning;
OptiX attribute min_sq reuse;
packed coordinate-matrix front doors;
linear finite max-nearest reduction;
global-bound early-break for max-nearest / directed-HD scalar.
```

The critical architectural outcome is that RTDL can express a generic
cell-MBR / nearest-witness / max-nearest route without making Hausdorff or X-HD
a core primitive.

### Generic Status / Worklist Infrastructure

Implemented through the 5279-5393 line:

```text
generic heavy/offload worklist reference;
native offload telemetry ABI;
generic active-query status machine CPU reference;
generic multi-round active-query status reference;
status-trace summary helpers;
author trace v2 instrumentation plan and execution;
denominator surface reconciliation;
status-stream target selection.
```

This is the system extraction behind the explicit `-lb` investigation. It is
not yet native `-lb` support.

## Performance Evolution And Current Meaning

The main Level-B Dragon -> HappyBuddha scalar route evolved approximately as:

```text
Goal5187 all-source initial route      ~= 7.30s route wall
Goal5189 local-grid seed              ~= 5.98s
Goal5191 inline512 empty-frontier      ~= 3.65s
Goal5195 intersection pruning          ~= 2.6s
Goal5196 dense local-grid lookup       ~= 2.26s
Goal5203 matrix input front door       ~= 1.24s
Goal5204 linear max-nearest reducer    ~= 1.17-1.18s
Goal5211 global-bound early-break      ~= 0.849s fresh route
Goal5212 no all-source subset copy     ~= 1.531s fresh full total incl. load
Goal5211 explicit-warm route           ~= 0.362s
Goal5212 explicit-warm case total      ~= 0.288s
```

Interpretation:

```text
This is real route-local RTDL progress.
This is not a paper performance ratio.
This is not exact paper dataset reproduction.
This is not exact per-source witness output under early-break.
```

Reasons a ratio remains unauthorized:

```text
author Running.AvgTime, author process wall, RTDL route wall, RTDL full total,
load costs, route warmup, and app comparator costs are different denominators;
hardware and runtime regimes differ;
exact paper inputs are not available.
```

## Review Status

Externally reviewed / approved:

```text
Goal5110
Goals5111-5126
Goals5127-5128
Goal5129 plan, with amendment incorporated
```

Implemented / review pending:

```text
Goals5130-5393, unless a later register explicitly marks individual goals
externally reviewed.
```

Current implemented review-pending packets include:

```text
history/internal_docs/call_for_review_goals5386_5390_xhd_lb_trace_packet_2026-07-10.md
history/internal_docs/call_for_review_goal5391_xhd_lb_fanout_semantics_2026-07-10.md
history/internal_docs/call_for_review_goal5392_xhd_lb_denominator_surface_reconciliation_2026-07-10.md
history/internal_docs/call_for_review_goal5393_xhd_lb_status_stream_target_design_2026-07-10.md
```

Do not silently upgrade implemented / review-pending goals to reviewed.

## Current Hard Problem: Explicit `-lb`

The current `-lb` problem is not ordinary scalar HDResult correctness. RTDL
already matches strong Level-B scalar values. The problem is reproducing the
author load-balance / status-machine denominator.

Author trace v2 says:

```text
active_in_queue_size = 437,645
raw offload rows     = 27,133,990
rows / active        = 62
row hash             = 4333109858711462591
```

RTDL evidence says:

```text
current bridge rows        = 2,188,225  = 5x active
default raw kind2 rows     = 21,006,960 = 48x active
full-cover behavior rows   = 24,508,120 = 56x active
heavy-before rows          = 304,981,889 = overcount
```

Goal5392 decision:

```text
The bridge surface is not the sole target.
The full-cover surface is closest but is not correctness.
```

Goal5393 decision:

```text
Start from full-cover-like semantics.
Investigate the remaining 6 rows per active as a generic status-stream delta.
Do not hard-code 6, 62, X-HD option names, or author constants into RTDL core.
```

## Current Workspace Note

At the time of this report:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5394_full_cover_delta_status_probe.py
```

exists in the workspace, but the Goal5394 result artifact, test, result report,
and call-for-review are not present yet:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5394_full_cover_delta_status_probe.json
tests/goal5394_full_cover_delta_status_probe_test.py
history/internal_docs/goal5394_xhd_full_cover_delta_status_probe_result_2026-07-10.md
history/internal_docs/call_for_review_goal5394_xhd_full_cover_delta_status_probe_2026-07-10.md
```

Therefore Goal5394 is not counted as complete in this report.

## Immediate Planned Work

### Goal5394: Generic Full-Cover Delta Status Probe

Purpose:

```text
Turn the Goal5393 target into a concrete generic probe/spec:
  base full-cover-like status rows = 56 * active
  remaining author delta           =  6 * active
  author target                    = 62 * active
```

Allowed:

```text
generic multi-round status reference/probe;
explicit comparison requirements for row count, samples/hash, status counts,
miss/completed/aborted counters, and feedback count;
fail-closed decision if the delta requires app-specific constants.
```

Not allowed:

```text
native implementation if the goal remains a spec/prototype artifact;
hard-coding 6 rows per active or 62 rows per active in RTDL core;
claiming explicit -lb support;
claiming row/hash parity;
claiming Figure 7/11 reproduction;
claiming same-denominator memory or performance ratio;
claiming full X-HD paper reproduction.
```

POD expectation:

```text
No POD required if Goal5394 stays as a design/prototype/spec artifact.
POD required if Goal5394 changes native OptiX code or runs a full
Dragon -> AsianDragon row/hash parity gate.
```

### Goal5395: Native Generic Status-Stream Probe

Only after Goal5394 pins the generic probe contract:

```text
implement or instrument a native generic status stream;
compare row_count against 27,133,990;
compare hash or deterministic row samples when comparable;
compare status_count_offloading and feedback counters;
keep explicit -lb fail-closed unless row/hash parity is true.
```

POD expectation:

```text
POD required for native build and full Dragon -> AsianDragon status-stream
probe. Use scripts/current_pod_ssh.py only.
```

### Goal5396: Decision / Closeout Gate

After Goal5395:

```text
If row/hash parity moves toward author under a generic contract, continue the
native status-stream line.

If parity still fails and the only path is X-HD-specific logic, close explicit
-lb as unsupported under the current RTDL model.
```

## Broader Planned Work After `-lb`

The next workstreams remain:

```text
1. strict review of the implemented / review-pending X-HD packets;
2. exact paper dataset provenance where possible;
3. Figure-level matrix completion only where author inputs and denominators
   can be aligned;
4. denominator-aligned performance only after dataset, phase, hardware, and
   runtime regime are explicit;
5. system extraction only when genericity can be proved outside X-HD.
```

## POD Usage Plan

Current known POD endpoint:

```text
host = 213.173.108.24
port = 13502
```

Use only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Expected POD use:

```text
Goal5394 spec-only: no POD expected.
Goal5395 native status stream: POD required.
Any author hd_exec rerun or patched-author trace: POD required.
Any OptiX/native ABI change: POD required.
Pure report/matrix/reconciliation artifacts: no POD required.
```

Do not declare the POD broken before running wrapper preflight. Past failures
were caused by wrong local SSH key usage, not necessarily by POD failure.

## Risks And Open Challenges

### R1. Exact Dataset Provenance

Exact paper dataset reproduction remains blocked without author input bytes,
hashes, or externally accepted deterministic reconstruction.

### R2. Explicit `-lb` Status Semantics

RTDL has not reproduced the author raw offload/status stream:

```text
author = 62 rows / active
closest RTDL surface = 56 rows / active
bridge = 5 rows / active
```

The next work must explain the remaining delta with generic status semantics or
fail closed.

### R3. Performance Denominators

No author-vs-RTDL ratio is authorized until denominator, hardware, input,
phase, and runtime regime are aligned.

### R4. Review Debt

Many implemented goals after Goal5129 are review pending. This is manageable
only if docs continue to preserve the distinction between implemented evidence
and externally reviewed evidence.

### R5. Genericity Drift

The pressure to match author status-machine behavior must not leak X-HD option
names or paper-specific constants into RTDL core. Any system primitive must use
app-neutral names and should have synthetic or non-X-HD coverage when possible.

## Allowed Summary

```text
X-HD is not fully reproduced.  RTDL has completed externally reviewed bounded
same-input X-HD value reproduction and has strong Level-B same-source scalar
evidence on public Stanford Dragon -> HappyBuddha.  The scalar route has been
made fast under explicit route/regime boundaries, and X-HD has produced several
real generic RTDL system abstractions.  Exact paper input provenance, figure
matrices, denominator-aligned performance ratios, and explicit author -lb
status-stream parity remain open.  The current immediate plan is Goal5394:
probe the generic full-cover-to-author status-stream delta without hard-coding
X-HD constants.
```

## Forbidden Summaries

```text
Do not say X-HD full paper reproduction is complete.
Do not say RTDL matches author X-HD performance.
Do not say the public Stanford files are exact paper inputs.
Do not say Goal5211 produces exact per-source witnesses.
Do not say full-cover is correct explicit -lb.
Do not say the current bridge only needs to be made faster.
Do not say Figure 7 or Figure 11 is reproduced.
Do not say memory or performance denominators are aligned.
Do not say Goal5394 is complete until artifact, tests, report, and review packet exist.
```
