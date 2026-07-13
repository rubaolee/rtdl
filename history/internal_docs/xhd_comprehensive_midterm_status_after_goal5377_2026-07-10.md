# X-HD Comprehensive Midterm Status After Goal5377

Date: 2026-07-10

This is the current handoff and midterm-status report for the X-HD paper
reproduction line.  It supersedes the day-to-day status role of:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5376_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5375_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5373_goal5374_in_progress_2026-07-10.md
```

Those files remain historical evidence.  This document is the concise current
state: what has been completed, what is only implemented/review-pending, what
major problems have been solved, what remains unsolved, and what the next
planned work should be.

## Executive Summary

The X-HD line has achieved a strong **bounded and Level-B representative value
reproduction** and has extracted real generic RTDL system assets from the app.
It has **not** achieved full paper reproduction.

Current truthful summary:

```text
RTDL can reproduce directed X-HD HDResult values on bounded same-input cases
and on strong same-source representative public inputs.  RTDL has also gained
generic nearest / witness / max-nearest / cell-MBR frontier machinery from the
work.  Full X-HD paper reproduction remains blocked by exact input provenance,
missing figure matrices, non-aligned performance denominators, and especially
author-compatible explicit -lb / heavy-offload status-machine semantics.
```

Latest hard result:

```text
Goal5377 tested an experimental generic frontier_status_probe_mode
("heavy-before-inline-prune") against the Goal5374 author -lb oracle.

It is a no-go:
  author OffloadingSize rows        = 27,133,990
  RTDL default kind2 rows           = 21,006,960
  RTDL heavy-before-inline rows     = 304,981,889

The probe moves from under-counting to severe over-counting.  It does not
explain the author -lb denominator and must remain diagnostic/non-default.
```

## Current One-Line Position

```text
Value correctness is strong; reusable RTDL system extraction is real; full
paper reproduction is still unfinished; the main remaining semantic mountain is
author -lb / heavy-offload status-machine equivalence.
```

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

Goal5377 rejects the simple "classify heavy/offload before inline prune"
hypothesis.
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
Goal5377 is explicit -lb support.
```

## Completion State By Level

### Level A - Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

Closed evidence:

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

System assets extracted:

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

These are route-local RTDL numbers for the public Dragon -> HappyBuddha
representative line.  They are not author-vs-RTDL ratios.

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

## Major Completed Work

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
Goals5138-5212 generic grid/cell-MBR/frontier/nearest-state route work.
```

Result:

```text
RTDL gained reusable generic nearest, frontier, row-table, coordinate-matrix,
and max-nearest reduction pieces.  X-HD did not become a core primitive.
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
Goal5377 frontier status probe mode no-go.
```

Result:

```text
We now have a measured author oracle, a generic RTDL telemetry contract, and one
negative RTDL probe.  RTDL still does not reproduce the author -lb denominator.
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

Current RTDL surfaces:

| Candidate | Rows | Ratio vs author | Parity |
|---|---:|---:|---|
| author-radius inline kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius inline + global-bound kind2 | 21,006,960 | 0.7741935484 | false |
| author-radius no-inline raw kind2 | 304,981,889 | 11.2398467384 | false |
| old full-cover lb256 behavior gate | 24,508,120 | 0.9032258065 | false |
| Goal5377 heavy-before-inline-prune probe | 304,981,889 | 11.2398467384 | false |

Goal5376 status:

```text
status_candidate_contract_ready = true
author_lb_row_parity_established = false
explicit_lb_support_authorized = false
```

Goal5377 status:

```text
exit_label = heavy_before_inline_prune_probe_no_go__author_lb_row_parity_still_missing
```

Interpretation:

```text
Goal5376 makes RTDL's status-shaped telemetry visible.
Goal5377 proves a simple branch-order change is not enough.
Explicit -lb remains fail-closed.
```

## Major Problems Solved

Solved:

```text
bounded same-input value correctness;
directed-vs-symmetric Hausdorff definition;
generic nearest / witness / max-nearest extraction;
public Level-B Dragon -> HappyBuddha scalar match;
route-local performance on that representative line;
author-side -lb OffloadingSize oracle;
generic status-shaped RTDL telemetry surface for future comparison;
negative evidence that "heavy before inline prune" is not the missing author
denominator.
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

## Architecture Lessons

### 1. X-HD Is An App, Not A Core Primitive

RTDL core should expose generic spatial/dataflow building blocks:

```text
nearest rows;
witness rows;
max-nearest reduction;
grid / cell MBR descriptors;
cell-MBR frontier rows;
status-shaped traversal telemetry;
generic active-query / worklist machinery if needed.
```

The X-HD app owns:

```text
paper input provenance;
author hd_exec wrappers;
paper figure labels;
author option compatibility;
tolerance policy;
comparators;
claim boundaries.
```

### 2. Value Reproduction Is Not Algorithm Reproduction

The final scalar HDResult can match while internal witness rows, per-source
state, or author RT status-machine behavior differ.  Goal5211 and the current
`-lb` work both make this distinction unavoidable.

### 3. Performance Requires Denominator Discipline

Author `Running.AvgTime`, author process wall, RTDL route wall, RTDL total, and
explicit-warm measured case time are different denominators.  They must remain
separate unless a specific review authorizes a matched ratio.

### 4. `-lb` Is A Traversal Payload State-Machine Problem

Author `OffloadingSize` is controlled by:

```text
in_queue index;
dynamic cmin2/current-best payload state;
status bits;
cmax2 abort;
miss/offload queue updates;
loadBalanceProcessing feedback.
```

It is not explained by:

```text
all heavy cells;
scalar radius only;
host row materialization;
existing RTDL global-bound early-break;
classifying heavy cells before inline prune.
```

### 5. Goal5377 Narrows The Search

Goal5377 is a useful negative result. It shows the next solution must be a
stateful active-query/worklist model, not another branch-order tweak.

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
Goals5357-5377
```

Important:

```text
Do not silently upgrade implemented goals to externally reviewed/approved.
Review debt remains for the later goals even when tests and artifacts exist.
```

## Next Planned Work

### Goal5378 - Status-Machine Direction Decision

Purpose:

```text
Decide whether to build a stronger generic RTDL status-machine model or keep
author -lb fail-closed for X-HD.
```

Inputs:

```text
Goal5372 author status-machine requirement matrix;
Goal5374 author lb oracle;
Goal5375 current RTDL surface mismatch;
Goal5376 generic status telemetry contract;
Goal5377 heavy-before-inline-prune no-go.
```

Decision choices:

```text
Option A - Build generic active-query / status-machine model:
  per-query current-best / cmin2 by query row;
  active in_queue index namespace;
  generic offload and miss queues;
  generic status transitions;
  load-balance continuation / feedback step.

Option B - Keep author -lb fail-closed:
  record that RTDL value routes can match, but explicit author-compatible -lb
  remains unsupported until a future generic state-machine design is approved.
```

Recommended decision:

```text
Proceed only with a generic active-query/worklist/status-machine design.
Do not continue one-off branch-order probes.
```

Exit labels:

```text
authorize_generic_active_query_status_machine_design
author_lb_fail_closed_for_now__full_xhd_reproduction_blocked
```

### Goal5379 - Generic Active-Query Status-Machine Reference

Only if Goal5378 authorizes implementation.

Purpose:

```text
Build a CPU/NumPy reference executor over a bounded fixture that has nonterminal
offload, miss/active queue updates, and current-best feedback.
```

Acceptance:

```text
generic names only;
no X-HD core primitive;
matches an app-owned expected queue trace;
reports active queue size, offload rows, miss rows, cmin2/current-best state,
and terminal/completed rows.
```

### Goal5380 - Native / OptiX Prototype Against Author Oracle

Only after Goal5379 semantics are pinned.

Purpose:

```text
Prototype a native status-machine probe against the Goal5374 Dragon ->
AsianDragon author oracle.
```

Acceptance:

```text
compare raw_offload_rows_before_sort_reduce directly to 27133990;
compare author-width bytes directly to 217071920;
report row_count_parity explicitly;
keep explicit -lb unsupported unless parity is achieved and reviewed.
```

### Goal5381 - Option Surface / Figure Re-entry

Only after Goal5380.

If row parity is achieved:

```text
consider a narrow app-owned explicit -lb compatibility surface;
reopen Figure 7 and Figure 11 only with same-denominator fields.
```

If row parity is not achieved:

```text
keep -lb fail-closed;
record full X-HD paper reproduction as blocked on author RT-core status-machine
semantics.
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
  Goals5357-5377 radius / tune-radius / lb status-machine packet.
  Critical question: does Goal5377 correctly stop short of claiming -lb?
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
uses local changes, explicitly sync/build the changed files.
```

Expected POD use for the next implementation phase:

```text
Goal5378:
  no POD required if it is a decision/design goal.

Goal5379:
  likely local only if it is CPU/NumPy reference semantics.

Goal5380:
  POD required for native / OptiX probe;
  must sync changed files, rebuild OptiX, and compare directly to Goal5374.
```

## Expected Effort

These are engineering-cycle estimates, not promises.

```text
Goal5378 decision/design:
  0.5-1 focused cycle.

Goal5379 CPU/NumPy reference:
  1-2 focused cycles if the bounded trace fixture is already sufficient;
  longer if a new nonterminal fixture/oracle must be constructed.

Goal5380 native / OptiX prototype:
  2-5 focused cycles depending on whether the active-query state can be kept
  generic and whether POD iteration remains stable.
```

Main risk:

```text
High.  The remaining issue is semantic, not just telemetry or formatting.  The
author -lb path is a shader payload status machine plus load-balance
post-processing.  RTDL must model enough of that generically or continue to
fail closed.
```

## Recommended Next Action

Proceed with Goal5378.

First concrete output should be:

```text
history/internal_docs/goal5378_xhd_lb_status_machine_direction_decision_2026-07-10.md
history/internal_docs/call_for_review_goal5378_xhd_lb_status_machine_direction_decision_2026-07-10.md
```

Goal5378 should not write a new route kernel.  It should decide, based on the
evidence through Goal5377, whether the next real implementation is a generic
active-query/worklist/status-machine model or whether explicit author `-lb`
stays fail-closed for now.

## Bottom Line

The project is in a productive but unfinished state:

```text
value correctness: strong;
system extraction: real;
representative route performance: much improved;
paper figure reproduction: not complete;
exact paper inputs: not proven;
author -lb status-machine semantics: current hard blocker.
```

The next meaningful step is not another scalar value gate and not another
branch-order tweak. It is a decision and design step for generic active-query /
status-machine execution, followed by a reference implementation if approved.
