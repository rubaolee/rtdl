# X-HD Comprehensive Midterm Status After Goal5376

Date: 2026-07-10

This report is the current handoff document for the X-HD paper-reproduction
line. It supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5375_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5373_goal5374_in_progress_2026-07-10.md
```

It records what is complete, what is implemented but still review-pending, what
is planned next, and which claims remain forbidden.

## Executive Summary

The X-HD line has made substantial progress, but full paper reproduction is not
complete.

The strongest completed/reviewed foundation is:

```text
bounded same-input HDResult reproduction through Goal5126;
generic nearest / witness / max-nearest extraction through Goals5127-5128;
full-reproduction plan reviewed through Goal5129.
```

The strongest current representative route evidence is:

```text
Level-B public Stanford Dragon -> HappyBuddha route:
  author hd_exec rerun matches the paper-branch author-log HDResult within 1e-6;
  RTDL matches the author rerun HDResult on the same public pair;
  best current fresh route evidence after Goal5211 is about 0.849s;
  fresh full total including load after Goal5212 is about 1.531s;
  explicit-warm measured case total is about 0.288s, diagnostic only.
```

The latest system work is:

```text
Goal5376 adds a generic RTDL status-machine candidate telemetry contract for
the cell-MBR frontier producer and forwards it through the public columnar
front door.
```

The latest hard blocker is:

```text
explicit X-HD -lb / heavy-offload support remains unsupported.
Goal5374 gives a real author-side lb status-machine oracle.
Goal5375 proves current RTDL surfaces fail that oracle.
Goal5376 makes the mismatch observable in a generic telemetry contract, but
does not close the mismatch.
```

## Current One-Sentence Status

RTDL can reproduce X-HD directed Hausdorff scalar values on bounded and strong
Level-B representative inputs, and has extracted reusable system APIs from that
work; it has not yet reproduced the full X-HD paper because exact paper inputs,
figure matrices, denominator-aligned performance, and author-compatible `-lb`
status-machine semantics remain unresolved.

## Claim Boundary

Allowed summaries:

```text
Bounded same-input X-HD value reproduction is complete and externally reviewed
through Goal5126.

Generic nearest / witness / max-nearest extraction is complete and externally
reviewed through Goals5127-5128.

The public Dragon -> HappyBuddha Level-B route matches the author scalar
HDResult and has materially improved as a generic RTDL route.

Goal5374 provides an author-side -lb status-machine oracle.

Goal5375 proves current RTDL surfaces do not match that author oracle.

Goal5376 exposes a generic, app-neutral status-shaped telemetry surface for
future RTDL/author -lb comparison.
```

Forbidden summaries:

```text
Full X-HD paper reproduction is complete.
RTDL reproduces Figures 5 / 7 / 8 / 9 / 10 / 11.
RTDL has author-performance parity.
The explicit-warm 0.288s diagnostic is the default paper result.
Goal5211 gives exact per-source witnesses.
RTDL supports author-compatible explicit -lb.
Current RTDL raw kind2 / heavy rows equal author OffloadingSize.
Existing RTDL global-bound early-break is the same as author cmax2 abort.
Goal5376 is explicit -lb support.
```

## Completion State By Level

### Level A - Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

What is closed:

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
This is value-level bounded correctness, not full paper reproduction, not
author RT-core algorithm equivalence, and not a performance claim.
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
RTDL gained reusable nearest / witness / reduction primitives.
No X-HD primitive was added to RTDL core.
```

### Level B - Same-Source Representative Public Inputs

Status:

```text
strong representative evidence;
implemented goals after Goal5130 mostly remain review pending;
not exact paper dataset reproduction.
```

Strongest current line:

```text
Dragon -> HappyBuddha public Stanford pair:
  Goal5186 author hd_exec rerun matches the paper-branch author-log HDResult
    within 1e-6;
  Goal5187 RTDL route matches the author rerun HDResult on the same public pair;
  Goal5188 records separate phase denominators and refuses a performance ratio.
```

Important caveat:

```text
This is one public representative workload, not the full paper dataset matrix.
The author rerun is the direct comparator; any paper-log comparison remains
bounded by the fact that public files are not proven byte-identical paper inputs.
```

### Level C - Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Reason:

```text
Exact paper input files / hashes are not available.
Statistics, point counts, MBRs, Gini values, and matching HDResult values are
useful evidence but do not prove exact input identity.
```

Current dataset findings:

```text
Stanford graphics public candidates are useful Level-B same-source evidence.
BraTS remains access-gated.
OSM / Census / TIGER-like geo inputs remain snapshot, conversion, and exact
provenance blocked for Level C.
```

### Level D - Full Figure / Performance Reproduction

Status:

```text
not complete
```

Figure status:

```text
Figure 5:
  Level-B value-matched graphics and bounded geo candidates exist.
  Full Figure 5 matrix, exact inputs, and denominator-aligned ratio do not.

Figure 7:
  Author source/log semantics audited.
  Exact author lb=0 / lb=256 matrix is missing.
  RTDL explicit -lb support remains unsupported.

Figure 8:
  Radius/tune-radius scripts exist, and narrow internal adaptive diagnostic
  mapping exists, but checked-in tune-radius logs are missing. Not reproduced.

Figure 9:
  Author script expects four auto-tune variants; current logs provide only two.
  Not reproduced.

Figure 10:
  Scalability scripts exist, but checked-in scalability logs are missing and
  exact inputs are unavailable. Not reproduced.

Figure 11:
  Author memory fields and RTDL telemetry exist, but denominators are not
  aligned. Not reproduced.
```

## Performance Evolution On The Strongest Level-B Route

These numbers are route-local RTDL numbers for the public
Dragon -> HappyBuddha representative line. They are not author-vs-RTDL ratios.

| Stage | Route / Total Evidence | Meaning |
|---|---:|---|
| Goal5187 initial full-public route | ~8.31s route | first all-source Level-B scalar match |
| Goal5189 local-grid seed | ~5.98s route | generic seed avoids all-cell MBR scan |
| Goal5191 inline512 / empty frontier | ~3.65s route | native inline consumes frontier work |
| Goal5195 intersection current-best prune | ~2.6s route | prunes before report-intersection |
| Goal5196 dense local-grid lookup | ~2.26s route | removes repeated cell lookup search |
| Goal5203 NumPy matrix input front door | ~1.238-1.239s route | removes tuple-row front-door cost |
| Goal5204 linear max-nearest reducer | ~1.17-1.18s route | reducer no longer full-array lexsort |
| Goal5211 global-bound early-break | ~0.849s fresh route | exact final value; many witnesses approximate |
| Goal5212 no all-source subset copy | ~1.531s fresh full total incl. load | app-runner hygiene |
| Goal5212 explicit warm diagnostic | ~0.288s measured case total | diagnostic only, not default paper result |

Critical Goal5211 caveat:

```text
The route preserves the final directed-HD / max-nearest scalar value, but many
per-source witnesses may be approximate due to early aborts.  It is not a
generic exact nearest-witness default.
```

## Major Work Already Completed

### 1. Provenance, Bounded Gates, And Directed Definition

Completed:

```text
Goal5110 X-HD scaffold/provenance.
Goals5111-5126 bounded same-input value gates.
Goal5126 directed-vs-symmetric discriminating fixture.
```

Result:

```text
Bounded value correctness is closed and reviewed.
Directed input1 -> input2 semantics are pinned.
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

Implemented:

```text
Goals5130-5188 target matrix, provenance matrix, public graphics bridge,
author gate, RTDL gate, and phase-boundary matrix.
Goals5189-5212 route improvements and regime diagnostics.
```

Result:

```text
The public Dragon -> HappyBuddha route matches the author scalar HDResult.
Route-local RTDL time improved substantially.
No author ratio is authorized.
```

### 4. Figure / Dataset Audits

Implemented:

```text
Goals5272-5283 Figure 11 memory denominator audit and native telemetry line.
Goals5284-5287 Figure 9 auto-tune log/source audit.
Goal5288 Figure 5 denominator audit.
Goals5289-5300 additional graphics candidate probes.
Goals5301-5309 geo provenance and bounded WKT gates.
```

Result:

```text
Many tempting but false paper claims were narrowed or rejected.  Figure-level
reproduction remains blocked on missing exact inputs, missing logs/matrices, or
denominator mismatch.
```

### 5. Radius / Tune-Radius / Queue Semantics

Implemented:

```text
Goals5357-5362 bounded and nonterminal author-like queue / tune-radius mapping.
Goal5362 narrow internal adaptive tune-radius option mapping.
```

Result:

```text
The queue-state shape and a narrow adaptive diagnostic mapping are understood.
This does not authorize general author tune_radius support or Figure 8
reproduction.
```

### 6. `-lb` / Heavy-Offload Semantics

Implemented:

```text
Goals5363-5368 heavy-offload and raw kind-count audits.
Goal5369 machine-checked lb queue-state requirements.
Goal5370 bounded author-like queue-state reference.
Goal5371 inline/global-bound lb probes.
Goal5372 author shader status-machine gap matrix.
Goal5373 RTDL telemetry surface audit.
Goal5374 author-side lb status-trace oracle.
Goal5375 RTDL status-machine counterpart assessment.
Goal5376 RTDL status-machine candidate telemetry contract.
```

Result:

```text
We now have a measured author oracle and a generic RTDL telemetry contract, but
RTDL still does not reproduce the author -lb denominator.
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

Current RTDL candidates from Goal5375:

| Candidate | Rows | Ratio vs author | Parity |
|---|---:|---:|---|
| author-radius inline kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius inline + global-bound kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius no-inline raw kind2 | 304,981,889 | 11.2398467384 | false |
| old full-cover lb256 behavior gate | 24,508,120 | 0.9032258065 | false |

Goal5376 status:

```text
status_candidate_contract_ready = true
author_lb_row_parity_established = false
explicit_lb_support_authorized = false
```

Interpretation:

```text
Goal5376 lets RTDL expose app-neutral status-shaped telemetry.
It does not implement the missing author status machine.
Explicit -lb remains fail-closed.
```

## What Has Been Solved

Solved:

```text
bounded same-input value correctness;
directed-vs-symmetric Hausdorff definition;
generic nearest / witness / max-nearest extraction;
public Level-B Dragon -> HappyBuddha scalar match;
route-local performance on that representative line;
author-side -lb OffloadingSize oracle;
generic status-shaped RTDL telemetry surface for future comparison.
```

Partially solved:

```text
Figure 5:
  Level-B scalar matches exist, but no full matrix / exact inputs / fair ratio.

Figure 11:
  author memory fields and RTDL telemetry exist, but denominators remain
  non-aligned.

tune_radius:
  narrow internal adaptive mapping exists; no general author option support.

-lb:
  behavior and byte-shape evidence exists; row-count parity does not.
```

Not solved:

```text
exact paper dataset identity;
full paper figure reproduction;
author RT-core algorithm parity;
same-denominator performance comparison;
explicit author-compatible -lb support;
RTDL status-machine counterpart for author OffloadingSize;
general author option-surface compatibility.
```

## Key Architecture / System Lessons

1. X-HD remains an app, not a core primitive.

```text
RTDL core should expose generic nearest / witness / frontier / worklist /
status-machine primitives.
The X-HD app owns author wrappers, input provenance, comparators, tolerances,
figure names, and claim boundaries.
```

2. Value reproduction is not algorithm reproduction.

```text
The final scalar HDResult can match while per-source witnesses or internal
author RT state differ.  Goal5211 and the current -lb line both make this
distinction important.
```

3. Performance must stay denominator-labeled.

```text
Author Running.AvgTime, author process wall, RTDL route wall, RTDL total, and
explicit-warm measured case time are different denominators.
```

4. `-lb` is a traversal payload state-machine problem.

```text
Author OffloadingSize is controlled by in_queue index, dynamic cmin2/current
best, status bits, cmax2 abort, miss/offload queue updates, and
loadBalanceProcessing feedback. It is not merely "count all heavy cells."
```

5. Goal5376 is the right kind of system move, but only a first move.

```text
The telemetry surface is app-neutral and reusable.  It makes the missing state
visible.  It does not yet implement author-equivalent state.
```

## Review Status

Externally reviewed / approved:

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
Goals5357-5376
```

Important:

```text
Do not silently upgrade implemented goals to externally reviewed/approved.
Review debt remains for the later goals even when tests and artifacts exist.
```

## Immediate Next Plan

### Goal5377 - Real RTDL Status-Machine Probe Or Fail-Closed Decision

Purpose:

```text
Implement or probe a real RTDL status-machine mode against the Goal5374 author
oracle, or prove that current RTDL should keep explicit -lb fail-closed.
```

Minimum comparison target:

```text
active_in_queue_size == 437645
raw_offload_rows_before_sort_reduce == 27133990
raw_offload_rows_author_width_bytes == 217071920
status_count_init == 437645
status_count_offloading == 27133990
```

Required fields to account for:

```text
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Likely implementation options:

```text
Option A - native branch-order/status probe:
  add an experimental generic mode in the cell-MBR frontier collector that
  changes status/offload classification order and emits status telemetry.

Option B - active queue/current-best reconstruction:
  carry author-like active in_queue indices and current-best/cmin2 state into
  the RTDL probe before counting offload rows.

Option C - stronger author oracle:
  instrument author further to dump raw row contents and per-source state if
  RTDL cannot reconstruct the denominator from existing artifacts.
```

Exit labels:

```text
rtdl_status_machine_matches_author_lb_oracle__explicit_lb_gate_can_be_considered
rtdl_status_machine_probe_fails_author_lb_oracle__explicit_lb_remains_fail_closed
```

### Goal5378 - Option Surface Decision

Only after Goal5377:

```text
If row parity is established:
  decide whether a narrow app-owned explicit -lb compatibility surface can be
  accepted.

If row parity is not established:
  keep -lb fail-closed and record the mismatch as a hard semantic blocker.
```

### Goal5379 - Figure 7 / Figure 11 Re-entry Gate

Only after row parity or an externally reviewed denominator decision:

```text
reopen Figure 7 load-balance comparison;
reopen Figure 11 memory comparison;
require same-denominator author and RTDL fields;
refuse ratios until denominator review passes.
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
  Goals5357-5376 radius / tune-radius / lb status-machine packet.
  Critical question: does Goal5376 correctly stop short of claiming -lb?
```

## POD Usage Expectation

Current known POD:

```text
host = 213.173.108.24
port = 13502
gpu  = NVIDIA RTX 4000 Ada Generation
```

Use only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Do not use naked SSH.

Known remote paths:

```text
remote RTDL workspace = /tmp/rtdl_goal5364
author source         = /tmp/xhd-goal5112/author
author build          = /tmp/xhd-goal5112/build-gcc11-optix77-fast
Dragon PLY            = /tmp/xhd_goal5234/data/dragon.ply
AsianDragon PLY       = /tmp/xhd_goal5234/data/asian_dragon.ply
```

Important remote caveat:

```text
/tmp/rtdl_goal5364 exists but is not a git checkout.  Before any POD probe that
uses Goal5376 or later local changes, explicitly sync/build the changed files.
```

Expected POD work for Goal5377:

```text
1. wrapper preflight;
2. sync changed RTDL native / Python files to the remote workspace;
3. rebuild native OptiX if the ABI/kernel changes;
4. run Dragon -> AsianDragon lb=256 diagnostic;
5. compare emitted RTDL rows/bytes/status fields to Goal5374 author oracle;
6. write artifact, result report, tests, and call-for-review.
```

## Time / Effort Estimate

These are engineering-cycle estimates, not promises.

```text
Goal5377 status-machine probe:
  1-3 focused cycles if a diagnostic branch-order/status mode is enough;
  more if author-like current-best / in_queue reconstruction is needed.

Goal5378 option-surface decision:
  1 short goal after Goal5377 evidence exists.

Goal5379 Figure 7 / 11 re-entry:
  only if Goal5377 succeeds or if an external review accepts a different
  denominator. Otherwise this should remain blocked.
```

Main risk:

```text
High.  The remaining issue is semantic, not just telemetry or formatting.  The
author -lb path is a shader payload status machine plus load-balance
post-processing. RTDL must model enough of that generically or continue to fail
closed.
```

## Recommended Next Action

Proceed with Goal5377.

First concrete step:

```text
inspect native cell-MBR frontier code and Python front doors;
choose the smallest generic experimental mode that can test whether current
RTDL branch order / status counting explains the author row denominator;
define JSON fields before claiming support;
run local focused tests first;
then sync/build on POD and compare against Goal5374.
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
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5376_status_machine_candidate_contract.json
```

## Bottom Line

The project is in a good but unfinished state:

```text
value correctness: strong;
system extraction: real;
representative route performance: much improved;
paper figure reproduction: not complete;
exact paper inputs: not proven;
author -lb status-machine semantics: current hard blocker.
```

The next meaningful work is not another scalar value gate. It is the real
status-machine probe that either closes the author `-lb` denominator gap or
formally keeps that surface unsupported.
