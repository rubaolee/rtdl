# X-HD Comprehensive Midterm Status After Goal5375

Date: 2026-07-10

This report supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5373_goal5374_in_progress_2026-07-10.md
```

It records the current X-HD paper-reproduction position after Goal5374 and
Goal5375.  It is intended as a handoff document for future agents, reviewers,
and the project owner.

## Executive Summary

The X-HD line has made real progress, but the full paper reproduction is not
complete.

Current strongest result:

```text
Level-B public Stanford Dragon -> HappyBuddha representative route:
  RTDL matches the author HDResult on the same public pair.
  Best current fresh route evidence is about 0.849s after Goal5211.
  Full total including load after Goal5212 is about 1.531s.
  Explicit-warm diagnostic case total is about 0.288s.
```

But this is not full paper reproduction because:

```text
exact paper input files / hashes are not available;
Figures 5 / 7 / 8 / 9 / 10 / 11 are not reproduced;
author internal Running.AvgTime, author process wall, RTDL route wall, and RTDL
total are different denominators;
the current X-HD `-lb` / heavy-offload semantics are still not supported by
RTDL;
Goal5211's early-break route is exact-value-only for directed HD / max-nearest:
  many per-source witnesses may be approximate.
```

The newest hard result is negative but important:

```text
Goal5374 builds an author-side `-lb` status-machine oracle:
  author OffloadingSize = 27,133,990 rows
  author-width bytes    = 217,071,920 bytes

Goal5375 proves no current RTDL surface matches that oracle:
  inline kind2 current surface       = 21,006,960 rows
  inline + global-bound current      = 21,006,960 rows
  no-inline raw kind2 current        = 304,981,889 rows
  old Goal5365 behavior-gate surface = 24,508,120 rows

Therefore explicit `-lb` remains unsupported.
```

The next real implementation target is:

```text
Goal5376: implement or probe a real RTDL status-machine mode against the
Goal5374 author oracle.
```

## Claim Boundary

Allowed summaries:

```text
Bounded same-input X-HD value reproduction is complete and reviewed through
Goal5126.

RTDL extracted generic nearest / witness / max-nearest pipeline pieces through
Goals5127-5128.

The public Dragon -> HappyBuddha Level-B representative route matches the
author scalar HDResult and has improved substantially as a generic RTDL route.

Goal5374 provides a real author-side `-lb` status-machine oracle.

Goal5375 proves current RTDL surfaces do not yet match that oracle.
```

Forbidden summaries:

```text
Full X-HD paper reproduction is complete.
RTDL reproduces Figure 5 / 7 / 8 / 9 / 10 / 11.
RTDL has author-performance parity.
The 0.288s explicit-warm diagnostic is the default paper result.
Goal5211 gives exact per-source witnesses.
RTDL supports author-compatible explicit `-lb`.
Current RTDL raw kind2 rows equal author OffloadingSize.
Existing RTDL global-bound early-break equals author cmax2 abort semantics.
The instrumented author Goal5374 timing is a performance baseline.
```

## Completion State By Level

### Level A - Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

What was established:

```text
author hd_exec bounded JSON gates run;
RTDL exact columnar route matches author HDResult;
directed-vs-symmetric ambiguity is closed by a discriminating fixture:
  directed A->B = 0.5
  directed B->A = 9.0
  symmetric     = 9.0
author and RTDL both match directed A->B.
```

Boundary:

```text
This is value-level bounded correctness, not algorithm reproduction and not a
performance claim.
```

### Level A-System - Generic RTDL Extraction

Status:

```text
complete and externally reviewed through Goals5127-5128
```

What became system work:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest / service-radius style reduction;
non-Hausdorff facility-service-radius consumer.
```

Meaning:

```text
Hausdorff remains an app-level composition.
RTDL gains reusable nearest / witness / reduction primitives.
The system principle is preserved: no X-HD primitive is added to core.
```

### Level B - Same-Source Representative Public Inputs

Status:

```text
strong but not full paper reproduction;
many goals implemented / review pending after 5130.
```

Strongest graphics line:

```text
Dragon -> HappyBuddha public Stanford pair:
  Goal5186 author hd_exec matches paper-branch author-log HDResult.
  Goal5187 RTDL matches the author HDResult on the same pair.
```

Performance-route progress on this representative line:

```text
Goal5187 initial full-public route:        about 8.31s
Goal5189 local-grid seed:                  about 5.98s
Goal5191 inline512 / empty-frontier route: about 3.65s
Goal5195 intersection-current-best prune:  about 2.6s
Goal5196 dense local-grid lookup:          about 2.26s
Goal5203 NumPy matrix input front door:    about 1.238-1.239s
Goal5204 linear max-nearest reducer:       about 1.17-1.18s
Goal5211 global-bound early-break route:   about 0.849s fresh route
Goal5212 full total including load:        about 1.531s
Goal5212 explicit-warm measured case:      about 0.288s diagnostic
```

Critical caveat:

```text
Goal5211 is exact for the final directed-HD scalar value, but per-source
witnesses may be approximate because many sources early-abort.  It is a
directed-HD / max-nearest contract, not a generic exact nearest-witness default.
```

### Level C - Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Reason:

```text
exact paper input files / hashes are not available;
public reconstructed inputs may match values or statistics but cannot be
promoted to exact paper datasets without file/hash provenance.
```

Important dataset findings:

```text
Stanford graphics public candidates are available and useful for Level-B.
BraTS is access-gated.
OSM / Census / TIGER-like geo inputs remain provenance / snapshot / filtering
blocked for exact paper identity.
```

### Level D - Full Figure / Performance Reproduction

Status:

```text
not complete
```

Figure status:

```text
Figure 5:
  Several Level-B value-matched graphics / bounded geo candidates exist.
  No full Figure 5 matrix and no denominator-aligned performance ratio.

Figure 7:
  Author source/log semantics audited.
  Exact author lb0/lb256 matrix is missing.
  Current `-lb` route remains unsupported in RTDL.

Figure 8:
  Author radius-tuning scripts exist, but checked-in tune-radius logs are
  missing.  Not reproduced.

Figure 9:
  Author script expects four auto-tune variants, but current logs have only
  two variants.  Not reproduced.

Figure 10:
  Scalability scripts exist, but checked-in scalability logs are missing and
  exact inputs are unavailable.  Not reproduced.

Figure 11:
  Author memory logs were extracted and RTDL native telemetry exists, but
  denominator is not aligned.  Not reproduced.
```

## Major Work Already Completed

### 1. Provenance And Bounded Gates

Completed:

```text
Goal5110 X-HD scaffold/provenance.
Goals5111-5126 bounded same-input value gates.
Goal5126 directed-vs-symmetric discriminating fixture.
```

Result:

```text
bounded value correctness is closed and reviewed.
```

### 2. Generic System Extraction

Completed:

```text
Goals5127-5128 generic nearest / witness / max-nearest pipeline extraction and
non-Hausdorff consumer.
```

Result:

```text
RTDL gained reusable generic pieces; X-HD did not become a core primitive.
```

### 3. Representative Public Graphics Route

Completed / implemented:

```text
Goals5130-5188 build the target matrix, provenance matrix, public graphics
bridge, author gate, RTDL gate, and phase-boundary matrix.
Goals5189-5212 improve the generic route and document regimes.
```

Result:

```text
The Dragon -> HappyBuddha public route matches the author scalar HDResult.
RTDL route performance improved by roughly one order of magnitude in route
time on that representative line, but no author ratio is authorized.
```

### 4. Figure / Dataset Audits

Completed / implemented:

```text
Goals5272-5283: Figure 11 memory denominator audit and native telemetry line.
Goals5284-5287: Figure 9 auto-tune log/source audit.
Goal5288: Figure 5 denominator audit.
Goals5289-5300: additional graphics candidate probes.
Goals5301-5309: geo provenance and bounded WKT gates.
```

Result:

```text
Many paper-adjacent claims were narrowed or rejected.  This prevented false
Figure reproduction claims and clarified which data/denominators are missing.
```

### 5. Radius / Tune-Radius / Queue Semantics

Completed / implemented:

```text
Goals5357-5362: bounded and nonterminal author-like queue / tune-radius mapping.
Goal5362: narrow internal adaptive tune-radius option mapping ready.
```

Result:

```text
The queue-state shape is better understood, but this does not authorize general
author tune_radius support or Figure 8 reproduction.
```

### 6. `-lb` / Heavy-Offload Semantics

Completed / implemented:

```text
Goals5363-5368: heavy-offload and raw kind-count audits.
Goal5369: machine-checked lb queue-state requirements.
Goal5370: bounded author-like queue-state reference.
Goal5371: inline/global-bound lb probes.
Goal5372: author shader status-machine gap matrix.
Goal5373: RTDL telemetry surface audit.
Goal5374: author-side lb status-trace oracle.
Goal5375: RTDL status-machine counterpart assessment.
```

Result:

```text
We now know exactly why current RTDL does not yet support author-compatible
explicit `-lb`: current RTDL surfaces do not reproduce the author
status-machine denominator.
```

## Current `-lb` Evidence

Author oracle from Goal5374:

```text
Input pair: Dragon -> AsianDragon
lb = 256
iteration = 3

ActiveInQueueSize               = 437645
StatusInitCount                 = 437645
OffloadingSize                  = 27133990
RawOffloadRowsBeforeSortReduce  = 27133990
StatusOffloadingAppendCount     = 27133990
RawOffloadRowsAuthorWidthBytes  = 217071920
StatusCmax2MbrAbortCount        = 0
StatusPointLoopEarlyBreakCount  = 0
```

RTDL candidate surfaces from Goal5375:

| Candidate | Rows | Ratio vs author | Parity |
|---|---:|---:|---|
| author-radius inline kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius inline + global-bound kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius no-inline raw kind2 | 304,981,889 | 11.2398467384 | false |
| old full-cover lb256 behavior gate | 24,508,120 | 0.9032258065 | false |

Conclusion:

```text
No existing RTDL surface matches author OffloadingSize.
Explicit `-lb` must stay unsupported.
```

## What Has Been Solved

Solved:

```text
bounded value correctness;
directed-vs-symmetric Hausdorff definition;
generic nearest/witness/max-nearest extraction;
public Level-B Dragon->HappyBuddha scalar match;
route-local performance for that representative line;
many false figure/dataset/performance claims have been ruled out;
author-side `-lb` status-machine denominator is now measured.
```

Partially solved:

```text
Figure 5: several Level-B scalar matches exist, but no full matrix / exact
inputs / fair ratio.

Figure 11: author memory fields and RTDL telemetry exist, but denominators
remain non-aligned.

Tune-radius: a narrow internal adaptive mapping exists, but no general author
option support or Figure 8 reproduction.
```

Not solved:

```text
exact paper dataset identity;
full paper Figure reproduction;
author RT-core algorithm parity;
same-denominator performance comparison;
explicit author-compatible `-lb`;
RTDL status-machine counterpart for author OffloadingSize.
```

## Key Architecture / System Lessons

1. X-HD is an app, not a core primitive.

```text
RTDL core should expose generic nearest / witness / frontier / worklist /
status-machine primitives.
The X-HD app owns author wrappers, input provenance, comparators, tolerances,
and figure-specific claims.
```

2. Route-local performance can improve while paper performance remains
unclaimed.

```text
The representative route improved materially, but author Running.AvgTime,
author wall time, RTDL route wall, and RTDL total are separate denominators.
```

3. `-lb` is not just a heavy-cell count.

```text
Author OffloadingSize depends on shader payload state:
  in_queue index;
  dynamic cmin2/current-best;
  status bits;
  cmax2 abort;
  miss/offload queue updates;
  loadBalanceProcessing feedback.
```

4. Current RTDL telemetry is real but insufficient.

```text
RTDL has raw frontier kind counts, inline stats, global-bound diagnostics, and
native memory telemetry.  It does not yet expose author-compatible status
counts, miss queue, cmax2 abort count, or row parity against OffloadingSize.
```

## Review Status

Reviewed / approved:

```text
Goal5110
Goals5111-5126
Goals5127-5128
Goal5129 with amendment incorporated
```

Implemented / review pending:

```text
Goals5130-5212
Goals5272-5309
Goals5357-5375
```

Important:

```text
Do not silently upgrade implemented goals to externally reviewed/approved.
Reports and call-for-review files exist, but review debt remains for the later
goals.
```

## Immediate Next Plan

### Goal5376 - RTDL Status-Machine Mode / Probe

Purpose:

```text
Build or probe a real RTDL status-machine counterpart against the Goal5374
author oracle.
```

Minimum required fields:

```text
active_in_queue_size
raw_offload_rows_before_sort_reduce
raw_offload_rows_author_width_bytes
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Required comparison:

```text
author rows        = 27133990
author-width bytes = 217071920
```

Likely implementation paths:

```text
Path A - RTDL experimental native/app diagnostic mode:
  carry author-like active queue, current-best/cmin2, status bits, and raw
  offload emission semantics through the cell-MBR traversal.

Path B - stronger author oracle + RTDL comparison:
  instrument author further to expose raw row contents / per-source cmin2 and
  compare RTDL against that oracle before attempting public support.
```

Expected outputs:

```text
Either establish row-count parity against Goal5374, or produce a precise
denominator mismatch and keep explicit -lb fail-closed.
```

### Goal5377 - Explicit `-lb` Option Surface Decision

Only after Goal5376:

```text
If parity is achieved:
  decide whether to expose a narrow app-owned explicit `-lb` compatibility mode.

If parity is not achieved:
  keep `-lb` fail-closed and document missing semantics.
```

### Goal5378 - Figure 7 / Figure 11 Re-entry Gate

Only after `-lb` status-machine parity or an externally reviewed denominator
decision:

```text
reopen Figure 7 load-balance comparison;
reopen Figure 11 memory comparison;
require same-denominator author and RTDL fields;
do not report ratios until denominators are accepted.
```

### Parallel Review Work

Recommended review batches:

```text
Batch A:
  Goals5211-5212 early-break / no-copy selection.
  Critical question: exact-value-only contract and approximate witnesses.

Batch B:
  Goals5272-5309 figure/data/provenance audits.
  Critical question: are blocked / no-go states honestly recorded?

Batch C:
  Goals5357-5375 radius / tune-radius / lb status-machine packet.
  Critical question: does Goal5375 correctly force real status-machine work?
```

## POD Usage Expectation

Current known POD endpoint:

```text
host = 213.173.108.24
port = 13502
gpu  = NVIDIA RTX 4000 Ada Generation
```

Use only the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Do not use naked SSH.

Expected POD use for Goal5376:

```text
local:
  inspect / edit RTDL native + Python app route;
  run focused unit tests;
  build artifacts.

POD:
  rebuild native OptiX if native fields change;
  run Dragon -> AsianDragon lb=256 diagnostic;
  compare RTDL emitted rows/bytes/status counts to Goal5374 author oracle.
```

Known POD paths:

```text
remote RTDL workspace = /tmp/rtdl_goal5364
author source         = /tmp/xhd-goal5112/author
author build          = /tmp/xhd-goal5112/build-gcc11-optix77-fast
Dragon PLY            = /tmp/xhd_goal5234/data/dragon.ply
AsianDragon PLY       = /tmp/xhd_goal5234/data/asian_dragon.ply
```

Do not use:

```text
/tmp/xhd-goal5222_author_paper
```

for RT author instrumentation; it is incomplete/cropped.

## Time / Effort Estimate

The following estimates are for engineering sequencing, not calendar promises.

```text
Goal5376 status-machine implementation/probe:
  1-3 focused implementation cycles if a diagnostic approximation can be
  added to existing cell-MBR traversal;
  more if exact author current-best / queue feedback must be reconstructed.

Goal5377 option-surface decision:
  1 short goal after Goal5376 evidence exists.

Goal5378 Figure 7/11 re-entry:
  only if Goal5376 succeeds or if review accepts a different denominator.
  Otherwise it should remain blocked.
```

Expected risk:

```text
High.  This is no longer a wrapper or telemetry-label problem.  The hard part
is semantic: author `-lb` uses a traversal payload status machine and
load-balance post-processing.  RTDL must either model that state generically or
continue to fail closed.
```

## Recommended Next Action

Proceed with Goal5376.

First concrete step:

```text
inspect the native cell-MBR frontier path and X-HD app route;
decide where an experimental status-machine diagnostic can be added without
promoting X-HD app semantics into RTDL core;
define the exact JSON fields matching Goal5374 before writing performance or
support claims.
```

Files to inspect:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5375_rtdl_status_machine_counterpart_assessment.json
```

Exit labels:

```text
rtdl_status_machine_matches_author_lb_oracle__explicit_lb_gate_can_be_considered
rtdl_status_machine_probe_fails_author_lb_oracle__explicit_lb_remains_fail_closed
```
