# X-HD Comprehensive Midterm Status After Goal5389

Date: 2026-07-10

## Verdict

```text
midterm_status__full_paper_not_complete__level_b_and_lb_trace_work_in_progress
```

This is the current day-to-day status report for the X-HD paper reproduction
line after Goal5389. It supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5386_goal5387_in_progress_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5385_2026-07-10.md
```

The project has made substantial progress, but the honest status is still:

```text
bounded same-input correctness: complete and externally reviewed through Goal5126
generic nearest/witness/max-nearest extraction: externally reviewed through Goals5127-5128
Level-B representative scalar correctness: strong for several public candidates
full X-HD paper reproduction: not complete
explicit X-HD -lb support: not complete
Figure-level reproduction: not complete
same-denominator author/RTDL performance parity: not authorized
```

## Core Objective

The full project objective is:

```text
Reproduce X-HD as a paper app while extracting reusable RTDL system features.
```

That objective has two equal parts:

1. Paper reproduction evidence:
   bounded correctness, same-source representative correctness, author
   contract alignment, dataset provenance, and fair phase/performance evidence.

2. RTDL system improvement:
   app-neutral spatial/dataflow primitives, generic native front doors,
   status/trace contracts, and reusable execution patterns.

The principle remains:

```text
RTDL core exposes generic spatial/dataflow primitives.
X-HD app code owns paper-specific inputs, hd_exec wrappers, tolerances,
comparators, author-log mapping, figure labels, and claim boundaries.
```

## Current Completion Level

### Level A: Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

What this means:

```text
small controlled inputs;
author hd_exec JSON contract exercised;
RTDL route matches directed input1 -> input2 HDResult;
directed-vs-symmetric ambiguity resolved by an asymmetric fixture;
no paper figure or performance claim.
```

Important boundary:

```text
bounded correctness is not full paper reproduction.
```

### Level B: Same-Source Representative Correctness

Status:

```text
partially complete; strongest line is Stanford graphics Dragon -> HappyBuddha
```

Strongest public Level-B scalar evidence:

```text
source = Stanford Dragon, 437645 points
target = Stanford HappyBuddha, 543652 points
author HDResult = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs diff ~= 2.38e-9
```

This is the current strongest scalar representative line because it matches the
paper-branch author-log value within the accepted scalar tolerance. It is still
not exact paper dataset reproduction because input bytes/hashes from the paper
run are unavailable.

Other same-source / bounded evidence exists:

```text
graphics ThaiStatuette-scaled -> HappyBuddha: scalar match
graphics ThaiStatuette-scaled -> AsianDragon-scaled: scalar match
bounded County-ZCTA WKT fixture: scalar match
bounded WaterBodies-BlockGroups WKT fixture: scalar match
```

These are evidence-bearing fixtures, not figure reproduction.

### Level C: Exact Paper Dataset Reproduction

Status:

```text
not complete
```

Reason:

```text
exact paper input bytes / file hashes are still unavailable for the major
graphics, geo, BraTS, and OSM/TIGER categories.
```

Important decision:

```text
matching counts, MBRs, Gini, or HDResult values is not enough to call an input
an exact paper dataset.
```

Exact paper dataset status requires file/hash provenance or an externally
reviewed deterministic reconstruction path.

### Level D: Figure-Level Reproduction

Status:

```text
not complete
```

Current figure-specific disposition:

```text
Figure 5: strongest graphics Level-B candidate exists, but no full matrix and
          no exact-input / same-denominator performance claim.
Figure 7: load-balance / -lb matrix missing exact author denominator and RTDL
          explicit -lb support.
Figure 8: radius strategy logs missing; source scripts audited but matrix not
          regenerated.
Figure 9: auto-tune logs/scripts do not provide the full expected variant
          matrix.
Figure 10: scalability / overlap logs missing exact matrix.
Figure 11: memory denominator not aligned; RTDL generic frontier/worklist
           telemetry is not author WL / WL Heavy Peak.
```

## System Features Completed Or Extracted

### Generic Nearest / Witness / Max-Nearest Pipeline

Externally reviewed through Goals5127-5128:

```text
pairwise_l2_distance_candidate_rows_numpy_columns
nearest_witness_numpy_columns
max_nearest_distance_witness_numpy_columns
directed Hausdorff as an app-level composition
non-Hausdorff facility-service-radius consumer proving genericity
```

This established that Hausdorff is not a hard-coded RTDL primitive. It is an
application-level composition over reusable nearest/witness/reduction pieces.

### Generic Grid / Cell-MBR / Frontier Route

Extracted by the Goal5138-5212 line:

```text
grid cell descriptors;
nearest-state frontiers;
cell-MBR row-table ABI;
backend-assisted AABB / OptiX front doors;
native 3-D cell-MBR frontier collector;
inline nearest payload state;
payload current-best pruning;
intersection-stage current-best pruning;
coordinate_matrix front-door reuse;
linear max-nearest reduction;
explicit warmup protocol.
```

Best representative scalar route evidence on Dragon -> HappyBuddha:

```text
Goal5187 initial all-source scalable route: about 7.30s route wall
Goal5191 inline-nearest threshold 512: about 3.65s route wall
Goal5195 intersection-stage current-best prune: about 2.6s route wall
Goal5196 dense local-grid lookup: about 2.26s route wall
Goal5203 NumPy matrix input front door: about 1.24s route wall
Goal5204 linear max-nearest reduction: about 1.17-1.18s route wall
Goal5211 global-bound early-break: about 0.849s fresh route
Goal5212 no all-source subset materialization: full total including load about 1.531s
Goal5207 explicit warm measured route: about 0.626s
Goal5211 explicit warm route median: about 0.362s
Goal5212 explicit warm measured case total: about 0.288s
```

Boundary:

```text
Goal5211/5212 are exact-value/max-nearest wins only.
per_source_witness_exact = false for early-aborted sources.
409376 / 437645 sources were early aborted in the key run.
```

Therefore:

```text
allowed: exact directed HD scalar value route under the max-nearest contract
forbidden: claiming exact per-source witness rows under early-break
```

### Generic Heavy / Offload Worklist And Memory Telemetry

Goal5279-5283 line:

```text
generic heavy/offload row schema;
active/miss/deferred rows;
queue/peak telemetry at CPU-reference and native ABI levels;
bounded mapping to author-shaped Figure 11 candidate fields.
```

Outcome:

```text
Figure 11 remains not reproduced.
same_denominator_author_figure11 = false.
```

Reason:

```text
author WL = in_queue + miss_queue;
author WL Heavy Peak = heavy-cell offload queue peak;
RTDL current WL/frontier capacity is not the same denominator.
```

### Generic Active-Query Status Machine

Goal5379-5389 line:

```text
generic active query rows;
per-active-query current best state;
offload / miss / completed / aborted row tables;
multi-round reference requirements;
status trace summary contract;
hash/sample summary over generic offload rows.
```

This is the current active system line because explicit X-HD `-lb` requires
status-machine semantics rather than another single-pass frontier count probe.

## The `-lb` / Load-Balance Line

### What Is Known From The Author

Goal5374 count oracle established:

```text
ActiveInQueueSize = 437645
RawOffloadRowsBeforeSortReduce = 27133990
StatusOffloadingAppendCount = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
```

Goal5387 upgraded this to author trace v2:

```text
schema = rtdl.goal5385.author.lb_status_trace.v2
HDResult = 52.453487396240234
active_in_queue_size = 437645
raw_offload_rows_before_sort_reduce = 27133990
status_count_offloading_append = 27133990
status_count_init = 437645
load_balance_input_row_count = 27133990
load_balance_group_count = 437645
load_balance_feedback_update_count = 294
raw_offload_row_hash = 4333109858711462591
raw_offload_row_sample_point_ids = [11168, 210712, 437119]
raw_offload_row_sample_cell_ids = [2924, 17, 17]
```

This is an author-side oracle. It is not RTDL `-lb` support.

### What Current RTDL Surfaces Produce

Known failed or partial probes:

```text
Goal5381 bridge offload rows = 2188225
Goal5383 active-initial-best bridge offload rows = 2188225
Goal5389 source-limited bridge offload rows = 320
Goal5389 source-limited active queries = 64
Goal5389 source-limited raw hash = 6439553744306743619
```

Goal5389 proves only:

```text
the bridge can emit generic status-trace summary fields from actual RTDL rows.
```

Goal5389 does not prove:

```text
full active query count parity;
raw offload row count parity;
hash/sample parity;
explicit -lb support.
```

### Current `-lb` Gap

The decisive gap is semantic, not just speed:

```text
author raw offload rows = 27133990
current full RTDL bridge rows = 2188225
source-limited smoke rows = 320
```

The next work must produce a native or bounded generic status stream that
matches the author v2 trace denominator and row identity evidence. Bridge
optimization alone is not enough while the row denominator is wrong.

## Completed Work Since The Last Major Review Node

### Goal5386: Author Trace V2 Patch Plan

Status:

```text
implemented / review pending
```

Output:

```text
all_hooks_found = true
all_required_fields_covered = true
```

It validated author source hook anchors but did not execute the trace.

### Goal5387: Author Trace V2 Execution

Status:

```text
implemented / review pending
```

Output:

```text
author_v2_trace_executed_on_pod = true
author v2 count oracle preserves Goal5374
raw offload row hash/sample added
status and feedback counts added
```

### Goal5388: Generic Status Trace Summary Contract

Status:

```text
implemented / review pending
```

System API:

```text
active_query_status_trace_summary_numpy_columns
ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT
contract = generic_active_query_status_trace_summary_v1
```

Purpose:

```text
generic row_count / active_query_count / status_count_offloading /
hash / sample summary over active-query offload rows.
```

### Goal5389: Bridge Trace Summary Smoke

Status:

```text
implemented / review pending
```

Output:

```text
source_limit = 64
rtdl active_query_count = 64
rtdl offload row_count = 320
rtdl raw_offload_row_hash = 6439553744306743619
rtdl sample source_ids = [0, 32, 63]
rtdl sample cell_ids = [6279, 6286, 6145]
row_count_parity = false
hash_parity = false
```

This is the first smoke showing that actual RTDL bridge rows can emit the same
generic trace-summary shape needed to compare against Goal5387. It intentionally
does not claim full parity.

Focused tests:

```text
Goal5387: Ran 24 tests OK
Goal5388: Ran 15 tests OK
Goal5389: Ran 13 tests OK
```

## Key Challenges Already Solved

1. Directed-vs-symmetric Hausdorff ambiguity:

   ```text
   Goal5126 proves author and RTDL both use directed input1 -> input2.
   ```

2. Hausdorff app/core boundary:

   ```text
   Hausdorff is an app composition over generic nearest/witness/reduction APIs.
   ```

3. Full public scalar feasibility:

   ```text
   RTDL can run the full public Dragon -> HappyBuddha Level-B route and match
   author HDResult without all-pair materialization.
   ```

4. Naive all-pair route rejection:

   ```text
   437645 x 543652 pairs would be about 237.9B pairs and terabytes of rows.
   ```

5. Several false optimization paths were closed:

   ```text
   lower inline thresholds;
   static cell order;
   trace tmax scalar bound;
   explicit native CUDA local-grid seed wrapper;
   accel-build caching;
   more single-pass prune-mode variants for -lb.
   ```

6. Author `-lb` count oracle upgraded:

   ```text
   Goal5387 adds row hash/sample and status/feedback counts beyond count-only
   evidence.
   ```

7. RTDL trace comparison shape now exists:

   ```text
   Goal5388/5389 provide generic trace-summary shape and bridge plumbing.
   ```

## Major Problems Still Open

### P1. Exact Paper Inputs Are Missing

Exact input status remains blocked:

```text
public candidates can be Level B;
exact paper reproduction requires input file/hash provenance or deterministic
author reconstruction.
```

This blocks full paper reproduction and most figure-level claims.

### P2. Explicit `-lb` Is Not Supported

Current RTDL does not match the author `-lb` status-machine denominator:

```text
author raw rows = 27133990
current full RTDL bridge rows = 2188225
```

Goal5389 is source-limited plumbing only:

```text
source-limited rows = 320
```

### P3. Figure-Level Performance Denominators Are Not Aligned

No author-vs-RTDL performance ratio is authorized because the denominators
differ:

```text
author internal Running.AvgTime;
author process wall;
RTDL route wall;
RTDL total including load/setup;
cold process vs warm process vs explicit warmup.
```

### P4. Global-Bound Early Break Has Witness Caveats

It is valid for directed-HD/max-nearest scalar value, but not for generic exact
per-source witness APIs:

```text
per_source_witness_exact = false
early aborted sources = 409376 / 437645
```

### P5. Review Debt Exists

The current status contains many `implemented / review pending` goals. The most
important current review candidates are:

```text
Goal5386: author trace v2 patch plan
Goal5387: author trace v2 execution
Goal5388: generic status trace summary contract
Goal5389: bridge trace summary smoke
```

## POD Status And Expected Use

Current known POD:

```text
host = 213.173.108.24
port = 13502
container = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Rule:

```text
use scripts/current_pod_ssh.py
do not use naked ssh
```

Expected POD use for the next phase:

```text
1. full or bounded native status-stream parity gate against Goal5387;
2. no new source-limited smoke unless it has a bounded semantic purpose;
3. no bridge runtime optimization until row denominator and hash/sample parity
   are semantically closer;
4. if the next full gate cannot match author fields, collect enough evidence to
   fail-close explicit -lb honestly.
```

## Planned Work

### Goal5390: Full Or Bounded Native Status-Stream Parity Gate

Purpose:

```text
produce RTDL status rows comparable to Goal5387 author trace v2.
```

Required comparisons:

```text
active_query_count == 437645, or an explicitly bounded source count with a
  justified bounded author oracle;
raw offload row count against author 27133990 for the full gate;
raw row hash and samples when comparable;
status_count_offloading / miss / completed / aborted;
feedback update counts or a documented reason the RTDL status stream cannot
  model them yet.
```

Exit labels:

```text
native_status_stream_parity_candidate_ready
native_status_stream_denominator_mismatch__lb_remains_unsupported
bounded_status_stream_gate_ready__full_gate_still_required
```

### Goal5391: Review Packet For Goals5386-5390

Purpose:

```text
send the author oracle / RTDL counterpart sequence for strict external review.
```

The packet should ask whether:

```text
Goal5387 author trace v2 is a valid oracle;
Goal5388/5389 generic trace summary is app-neutral and useful;
Goal5390 either genuinely advances parity or proves fail-closed status.
```

### Goal5392: `-lb` Decision Closeout

Depending on Goal5390:

```text
If parity improves materially:
  continue native status-machine implementation.

If parity still fails:
  close explicit -lb as unsupported under current generic route and document
  the exact missing transitions.
```

No partial success should be promoted to explicit `-lb` support.

### Goal5393: Figure Claim Matrix Refresh

After the `-lb` decision:

```text
refresh Figures 5/7/8/9/10/11 status;
separate Level-B value matches from exact paper reproduction;
separate memory shape candidates from same-denominator memory claims;
refuse ratios where denominators do not align.
```

### Goal5394: System API Consolidation

Consolidate what X-HD legitimately added to RTDL:

```text
nearest/witness/max-nearest pipeline;
grid/cell descriptors and cell-MBR traversal ABI;
native inline-nearest payload and current-best pruning;
active-query status reference;
status-trace summary helper;
heavy/offload worklist telemetry.
```

Also list what remains app-owned:

```text
hd_exec wrappers;
paper-log mapping;
input provenance;
tolerances;
figure labels;
author instrumentation;
X-HD option names such as -lb.
```

## Expected Completion Path

Short-term:

```text
complete Goal5390 and strict review packet;
decide whether explicit -lb can continue or must fail-close;
update the figure matrix accordingly.
```

Medium-term:

```text
if exact paper inputs appear, rerun the Level-C exact-input gate;
otherwise keep current evidence at Level B representative status.
```

Long-term:

```text
full paper reproduction requires exact inputs, author/RTDL route parity for
the relevant options, figure denominator alignment, and external review.
```

## Forbidden Summaries

Do not summarize this state as:

```text
X-HD full paper reproduction is complete.
RTDL supports X-HD -lb.
RTDL reproduces Figure 7 or Figure 11.
RTDL is faster/slower than author by ratio X.
Goal5389 proves author trace parity.
Goal5211 proves exact per-source witnesses.
Public Stanford / ArcGIS inputs are exact paper datasets.
```

## Allowed Summary

Allowed concise summary:

```text
X-HD bounded same-input correctness and generic nearest-system extraction are
complete/reviewed.  The strongest current full-scale evidence is Level-B
same-source scalar correctness on public Dragon -> HappyBuddha, with a fast
generic RTDL route that preserves the directed HD scalar value but has
early-break witness caveats.  Exact paper inputs, figure-level denominators,
and explicit -lb support remain open.  The active hard problem is now the
generic active-query/status-stream counterpart to the author -lb trace v2
oracle: author emits 27133990 raw offload rows, while current RTDL surfaces do
not match that denominator.  Goal5389 proves trace-summary plumbing only; the
next gate must test full or bounded native status-stream parity.
```
