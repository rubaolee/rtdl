# X-HD Comprehensive Midterm Status After Goal5379

Date: 2026-07-10

This is the current durable midterm report for the X-HD paper reproduction
line. It supersedes the day-to-day handoff role of:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5377_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5376_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5375_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5373_goal5374_in_progress_2026-07-10.md
```

Those files remain historical evidence. This document is the current status:
project goal, completed work, current performance, solved problems, remaining
hard blockers, planned next work, and POD expectations.

## Executive Summary

The X-HD paper reproduction line has made real progress, but it is not finished.

Current truthful status:

```text
RTDL can reproduce directed X-HD HDResult values on bounded same-input cases
and on one strong same-source public Level-B workload. RTDL has also gained
generic nearest / witness / max-nearest / grid-cell / cell-MBR / active-query
state-machine building blocks from the app work.

Full X-HD paper reproduction is still incomplete. The two main blockers are:
  1. exact paper dataset identity is still unproved;
  2. author-compatible explicit -lb / heavy-offload status-machine semantics
     are not yet reproduced.
```

Current reproduction position:

```text
Bounded same-input value reproduction: complete and externally reviewed.
Generic system extraction from bounded X-HD: complete and externally reviewed.
One Level-B public graphics workload: strong value match, implemented /
  review-pending after strict midterm amendments.
Exact paper dataset / Figure reproduction: not complete.
Explicit author-compatible -lb: not supported yet; still fail-closed.
```

Latest system step:

```text
Goal5379 adds a generic CPU/NumPy active-query status-machine reference.
It is the semantic baseline for a future native/OptiX active-query status
machine. It does not claim explicit -lb support or author row parity.
```

## Current Claim Boundary

Allowed summaries:

```text
Bounded same-input X-HD value reproduction is complete and externally reviewed
through Goal5126.

Generic nearest / witness / max-nearest extraction is complete and externally
reviewed through Goals5127-5128.

RTDL matched the author hd_exec rerun on one same-source public Level-B
workload: Stanford Dragon -> HappyBuddha.

The best Level-B route computes the directed-HD scalar value, but under
Goal5211 global-bound early break many per-source witnesses are approximate.

Goal5374 supplies the current author -lb status oracle.

Goals5375-5377 prove current RTDL row surfaces do not match that -lb oracle.

Goal5378 authorizes a generic active-query/status-machine direction.

Goal5379 implements the CPU/NumPy reference contract for that generic direction.
```

Forbidden summaries:

```text
Full X-HD paper reproduction is complete.
RTDL reproduces Figures 5 / 7 / 8 / 9 / 10 / 11.
RTDL has author-performance parity.
RTDL supports author-compatible explicit -lb.
RTDL matches author OffloadingSize / raw offload row count.
Current RTDL raw kind2 rows are the author offload rows.
Existing RTDL global-bound early break is the same as author cmax2 abort.
Goal5379 is a native backend or performance improvement.
Goal5211 produces exact per-source witnesses.
The public Dragon -> HappyBuddha files are proven byte-identical paper inputs.
```

## Current Objective

The current objective is no longer merely "compute a Hausdorff distance". That
bounded value route is already established. The active objective is:

```text
Turn X-HD from a bounded value reproduction into a fuller paper reproduction
without breaking the RTDL principle that the core is a generic spatial/dataflow
system and X-HD is only an app.
```

That means two parallel tracks:

```text
Reproduction track:
  reproduce author-visible values, paper workloads, and eventually phase /
  memory behavior under honest dataset and denominator boundaries.

System track:
  convert reusable parts into generic RTDL APIs rather than X-HD-specific
  primitives.
```

## Completion State By Level

### Level A - Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

Evidence:

```text
author hd_exec bounded JSON gates run;
RTDL exact columnar route matches author HDResult;
directed-vs-symmetric ambiguity closed by discriminating fixture:
  directed A->B = 0.5
  directed B->A = 9.0
  symmetric     = 9.0
author and RTDL both match directed A->B.
```

Boundary:

```text
This is value-level bounded correctness, not author RT-core algorithm
equivalence, not full paper reproduction, and not a performance claim.
```

### Level A-System - Generic RTDL Extraction

Status:

```text
complete and externally reviewed through Goals5127-5128
```

System assets:

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

### Level B - Same-Source Representative Public Workload

Status:

```text
strong implemented evidence, review pending after strict amendments;
not exact paper dataset reproduction.
```

Strongest current workload:

```text
Stanford Dragon -> HappyBuddha public pair.
```

Key evidence:

```text
Goal5186:
  author hd_exec rerun on the public pair matches the paper-branch author-log
  HDResult within 1e-6.

Goal5187:
  RTDL all-source route on the same public pair matches the author rerun
  HDResult with abs diff about 2.4e-9.

Goal5188:
  phase matrix separates author internal timing, author process wall, RTDL
  route, and RTDL total; it refuses a performance ratio.
```

Required caveats from strict review:

```text
This is one directed public graphics workload, not broad Level-B completion.

RTDL matches the author rerun, not the paper log directly. The author rerun
itself differs from the paper-branch log by about 1.9e-7, consistent with
public inputs not being byte-identical paper inputs.

Under Goal5211 global-bound early break, the directed-HD scalar is exact for
the matched value, but per-source witnesses are approximate for early-aborted
sources. Evidence records about 409,376 / 437,645 early-aborted sources.
```

### Level C - Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Reason:

```text
Exact paper input files / hashes are not available.
Matching counts, point statistics, MBRs, Gini values, or HDResult values is not
enough to prove exact paper dataset identity.
```

Current dataset position:

```text
Stanford graphics public meshes support Level-B same-source representative
evidence.
BraTS remains access-gated.
OSM / Census / TIGER-style geo inputs remain snapshot, conversion, and
provenance blocked for exact Level C.
```

### Level D - Figure / Performance Reproduction

Status:

```text
not complete
```

Reason:

```text
The paper figures require exact input matrix, algorithm-phase alignment,
author build/runtime denominator alignment, and in particular explicit -lb /
heavy-offload behavior. Those are not all available.
```

Current stance:

```text
Do not report author-vs-RTDL performance ratio unless dataset, hardware,
algorithmic phase, runtime regime, and included setup/output costs match.
```

## Performance Evolution

These are RTDL route-local numbers on the public Dragon -> HappyBuddha Level-B
line unless otherwise stated. They are not author-vs-RTDL speedup ratios.

| Milestone | Route / total status | Main meaning |
|---|---:|---|
| Goal5187 | about 8.31s route | First full public all-source RTDL match to author rerun |
| Goal5191 | about 3.65s route | Inline-nearest threshold 512 consumes all frontier rows |
| Goal5195 | about 2.6s route | Intersection-stage current-best pruning |
| Goal5196 | about 2.26s route | Dense local-grid lookup |
| Goal5203 | about 1.238-1.239s route | App-owned NumPy matrix input front door removes tuple rows |
| Goal5204 | about 1.17-1.18s route | Linear max-nearest reduction |
| Goal5205 | about 2.06s full gate total; route still about 1.16-1.17s | Fast ASCII PLY matrix loader lowers load time |
| Goal5207 | about 0.626s explicit-warm route | Warmup protocol; diagnostic, not fresh headline |
| Goal5211 | about 0.849s fresh route; about 0.362s explicit-warm route | Global-bound early break for directed-HD/max-nearest scalar |
| Goal5212 | about 1.531s fresh full total including load; about 0.288s explicit-warm measured case total | Removes all-source subset materialization in app runner |

Important boundaries:

```text
The 0.288s warm figure is not a default paper result.
The 0.849s route is exact-value-only under the Goal5211 contract.
The 1.531s full total includes load but is still not an author-vs-RTDL ratio.
```

## Completed Work Since The Previous Stable X-HD Scaffold

### 1. Provenance And Bounded Correctness

Completed / reviewed:

```text
Goal5110:
  X-HD scaffold and source provenance.

Goals5111-5126:
  bounded author JSON gates, RTDL route gates, and directed-vs-symmetric
  discriminating fixture.
```

Result:

```text
Bounded directed HD value correctness is closed at the bounded level.
```

### 2. Generic System Extraction

Completed / reviewed:

```text
Goals5127-5128:
  generic nearest pipeline extraction and non-Hausdorff consumer proof.
```

Result:

```text
RTDL core gained generic nearest/witness/reduction vocabulary; X-HD did not
become a core primitive.
```

### 3. Level-B Public Workload And Route Construction

Implemented / review pending:

```text
Goals5130-5212:
  paper target matrix, dataset provenance, public Stanford graphics route,
  generic grid-cell / cell-MBR / frontier / nearest continuation APIs, native
  OptiX row producers, production matrices, route optimizations, warmup
  protocol, and global-bound early-break experiment.
```

Result:

```text
One strong public Level-B directed workload matches the author rerun value and
has a materially improved RTDL route.
```

Boundary:

```text
Still not exact paper input reproduction, not broad paper figure reproduction,
and not an author-vs-RTDL ratio.
```

### 4. Explicit `-lb` / Heavy-Offload Investigation

Implemented / review pending:

```text
Goal5370:
  author-like queue-state reference direction.

Goal5371:
  inline global-bound / -lb probe.

Goal5372:
  author shader/status-machine gap analysis.

Goal5373:
  status-shaped RTDL telemetry surface.

Goal5374:
  author -lb status trace oracle.

Goal5375:
  RTDL counterpart assessment against that oracle.

Goal5376:
  generic status-machine candidate telemetry contract.

Goal5377:
  heavy-before-inline-prune diagnostic probe.

Goal5378:
  direction decision: stop small probes; design generic active-query status
  machine.

Goal5379:
  generic CPU/NumPy active-query status-machine reference.
```

Result:

```text
The project now has a concrete author -lb oracle and a generic RTDL reference
contract for active-query status-machine behavior. It does not yet have native
row parity or explicit author-compatible -lb support.
```

## Key Problems Already Solved

### Problem 1 - "Is X-HD only an app, or did RTDL need core support?"

Resolved:

```text
X-HD is an app-level Hausdorff composition.
RTDL core only gained generic nearest / witness / reduction / cell-MBR /
active-query pieces.
```

The principle remains intact:

```text
paper apps own paper inputs, wrappers, tolerances, comparators, and claims;
RTDL core owns app-neutral spatial/dataflow primitives.
```

### Problem 2 - Directed Vs Symmetric Hausdorff Definition

Resolved by Goal5126:

```text
directed A->B = 0.5;
directed B->A = 9.0;
symmetric     = 9.0;
author and RTDL match directed A->B.
```

### Problem 3 - Pairwise Exact Reference Route Is Not Enough

Resolved architecturally:

```text
The route moved from bounded exact columnar references toward generic
grid-cell and cell-MBR assisted candidate production, native OptiX row
production, and generic continuation/reduction stages.
```

### Problem 4 - Route Performance Was Dominated By Python Front Doors

Partially solved:

```text
tuple-row input loading was replaced by NumPy matrix front doors;
generic coordinate-matrix reuse was added;
max-nearest reduction became linear for finite distances;
all-source subset materialization was removed.
```

### Problem 5 - Existing `-lb` Probes Were Ambiguous

Solved negatively:

```text
Goal5374 gives the author denominator;
Goal5375 proves current RTDL surfaces do not match it;
Goal5377 proves heavy-before-inline-prune is not the missing semantic.
```

This negative result is important because it prevents false claims of explicit
`-lb` support.

### Problem 6 - There Was No Generic Status-Machine Vocabulary

Now partially solved:

```text
Goal5379 adds a generic CPU/NumPy active-query/status-machine reference with
active_queue_index, per-query current-best state, offload rows, miss rows,
completed rows, aborted rows, and continuation feedback.
```

This is a system improvement, not an X-HD shortcut.

## Unsolved Major Problems

### Unsolved Problem 1 - Exact Paper Dataset Identity

Status:

```text
open
```

Need:

```text
actual paper input files, hashes, or equivalent provenance proof.
```

Cannot solve with:

```text
matching HDResult alone;
matching point counts alone;
matching statistics alone;
public same-source files alone.
```

### Unsolved Problem 2 - Full Figure Matrix

Status:

```text
open
```

Need:

```text
more than one graphics pair;
MRI and geospatial datasets or honest blocked status;
author/RTDL phase and denominator alignment;
figure-specific workload matrix.
```

### Unsolved Problem 3 - Author-Compatible Explicit `-lb`

Status:

```text
open and currently the main semantic mountain
```

Author oracle from Goal5374:

```text
ActiveInQueueSize               = 437645
StatusInitCount                 = 437645
OffloadingSize                  = 27133990
RawOffloadRowsBeforeSortReduce  = 27133990
StatusOffloadingAppendCount     = 27133990
RawOffloadRowsAuthorWidthBytes  = 217071920
StatusCmax2MbrAbortCount        = 0
StatusPointLoopEarlyBreakCount  = 0
```

RTDL probes so far:

```text
author-radius inline kind2          = 21,006,960 rows
inline + global-bound kind2         = 21,006,960 rows
no-inline raw kind2                 = 304,981,889 rows
old full-cover lb256 behavior gate  = 24,508,120 rows
heavy-before-inline-prune           = 304,981,889 rows
```

Meaning:

```text
RTDL currently jumps between under-counting and severe over-counting. The
missing behavior is not a simple row classification switch. It is an active
query state machine with offload, miss/completed/aborted transitions, and
continuation feedback.
```

### Unsolved Problem 4 - Native Active-Query Status Machine

Status:

```text
not implemented
```

Goal5379 is only the CPU/NumPy semantic reference. The native/OptiX counterpart
still needs design and POD validation.

### Unsolved Problem 5 - Review Debt

Status:

```text
large implemented/review-pending surface
```

Important:

```text
Do not silently upgrade Goals5130-5212 or Goals5370-5379 from implemented to
externally reviewed.
```

## Next Planned Work

### Immediate Goal5380 - Native/OptiX Active-Query Status-Machine Prototype

Purpose:

```text
Use the Goal5379 generic active-query/status-machine contract as the semantic
baseline for a native/OptiX prototype and compare it against the Goal5374
author -lb oracle.
```

Minimum required outputs:

```text
raw offload row count compared to 27,133,990;
author-width byte count compared to 217,071,920;
active query count compared to 437,645;
status init/offload/miss/completed/aborted telemetry;
explicit row parity true/false;
fail-closed explicit -lb claim unless parity is proven.
```

Allowed:

```text
app-neutral native/Python names;
generic active-query/status-machine row vocabulary;
POD-only native probe;
negative result / no-go if row parity fails.
```

Forbidden:

```text
X-HD-specific RTDL core primitive;
claiming explicit -lb from telemetry only;
claiming author memory parity without row parity;
claiming Figure 7 or Figure 11 reproduction;
claiming full paper reproduction.
```

Expected outcome:

```text
Either:
  native_status_machine_oracle_probe_matches_author_rows
or:
  native_status_machine_probe_no_go_with_gap_classified
```

### Goal5381 - Option Surface Or Fail-Closed Closeout

Purpose:

```text
If Goal5380 proves parity, expose a narrowly documented app route option.
If it fails, keep explicit -lb fail-closed and document the gap.
```

Possible outcomes:

```text
explicit_lb_author_compatible_route_authorized
explicit_lb_remains_fail_closed_status_machine_gap_documented
```

### Goal5382 - Review Packet For Goals5378-5381

Purpose:

```text
Bundle the active-query/status-machine decision, CPU reference, native probe,
and explicit-lb option decision for external review.
```

Review questions should focus on:

```text
genericity;
row parity evidence;
failure to overclaim;
whether explicit -lb remains correctly fail-closed;
whether the active-query API belongs in RTDL core.
```

### Later Work After `-lb`

Only after the `-lb` question is classified:

```text
return to exact dataset provenance;
expand beyond the single Dragon -> HappyBuddha Level-B workload;
build figure-specific workload matrices;
decide if Level C exact paper reproduction is blocked or recoverable;
prepare final full-paper reproduction / bounded-reproduction closeout.
```

## POD Use Plan

The next meaningful work requires POD for native OptiX.

Use only the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Do not use naked `ssh`. The wrapper pins:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Expected POD steps for Goal5380:

```text
1. preflight wrapper;
2. sync changed local files to /tmp/rtdl_goal5364;
3. rebuild native OptiX library;
4. run the Dragon -> AsianDragon lb=256 probe against the Goal5374 oracle;
5. collect JSON evidence under Paper-reproduction-apps/x-hd-paper/results/;
6. write goal report and call-for-review.
```

POD assumptions:

```text
remote workspace: /tmp/rtdl_goal5364
GPU class previously observed: RTX 4000 Ada
driver previously observed: 550.127.05
```

If the POD fails:

```text
run wrapper preflight first;
record stdout/stderr;
do not declare the POD broken until the wrapper preflight fails;
do not fall back to local-only claims for native OptiX work.
```

## Expected Timeline

This is a goal-count estimate, not a calendar guarantee.

```text
Goal5380:
  1-2 focused implementation/probe cycles if the existing v6 frontier ABI can
  be extended cleanly;
  more if native state feedback requires a larger ABI change.

Goal5381:
  1 decision/report goal after Goal5380 evidence exists.

Goal5382:
  1 review-packet goal.

Exact dataset / figure matrix:
  open-ended; depends on input availability and whether explicit -lb can be
  matched or must be carried as unsupported.
```

## Current Risk Register

| Risk | Severity | Current handling |
|---|---|---|
| Exact paper inputs unavailable | High | Keep Level-C blocked; do not upgrade Level-B |
| Explicit `-lb` row parity fails | High | Goal5380 native probe; keep fail-closed until parity |
| Native state-machine becomes X-HD-specific | High | Use Goal5379 generic contract; app-neutral scans |
| Warm/diagnostic numbers become headlines | High | Keep fresh/warm/prepared separated |
| Exact scalar value hides approximate witnesses | Medium | Carry Goal5211 exact-value-only caveat |
| Review-pending goals misreported as approved | Medium | Keep implementation and review status separate |
| POD auth mistakes | Medium | Use wrapper preflight only |

## Stable Handoff Summary

If a new agent starts here, the shortest accurate handoff is:

```text
We have bounded and one-workload Level-B X-HD value reproduction, plus real
generic RTDL system extraction. We do not have full paper reproduction. The
current hard technical blocker is explicit author-compatible -lb: author
OffloadingSize is 27,133,990 rows for Dragon -> AsianDragon lb=256, and every
current RTDL surface misses that denominator. Goal5379 added a generic
CPU/NumPy active-query status-machine reference. Next is Goal5380: implement or
probe a native/OptiX active-query status-machine against the Goal5374 author
oracle, using POD, without claiming -lb unless row parity is proven.
```
