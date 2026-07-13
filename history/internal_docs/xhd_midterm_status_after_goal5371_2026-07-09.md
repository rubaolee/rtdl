# X-HD Midterm Status After Goal5371

Date: 2026-07-09

Status: `midterm_report__full_reproduction_not_complete__lb_status_machine_next`

Postscript after initial report: Goal5372 has now implemented the author shader
status-machine gap matrix described in this report's next-work section. The
current next gate is therefore concretely named:

```text
author_shader_status_machine_lb_trace
```

Goal5372 remains implemented / review pending and does not authorize explicit
`-lb` support.

Second postscript: Goal5373 has now audited the current RTDL generic cell-MBR
frontier telemetry surface against the Goal5372 minimum fields. The current
surface is real but insufficient:

```text
missing_count = 8
partial_count = 3
ready_for_author_shader_status_machine_lb_trace = false
```

Goal5373 remains implemented / review pending and further confirms that the
next valid work is either a generic native status-machine probe or author
instrumentation; it does not authorize explicit `-lb` support.

## One-Line Status

X-HD has become a serious paper-reproduction and RTDL-system-extraction line:
bounded same-input value reproduction is reviewed complete, the generic
nearest/witness/max-nearest pipeline has been extracted into RTDL, and the
strongest Level-B public Dragon -> HappyBuddha route matches the author scalar
HD value while improving RTDL route time from about `7.30s` to about `0.849s`
fresh route / about `0.362s` explicit-warm route under the Goal5211
exact-value-only contract.

Full X-HD paper reproduction is still not complete. Exact paper input identity,
full figure matrices, author RT-core option parity, same-denominator memory
figures, and author-vs-RTDL performance ratios remain unclosed.

The current active hard blocker is no longer plain Hausdorff value correctness.
It is author RT-core semantic parity for `-lb` / heavy-cell offload:
`OffloadingSize` depends on author shader payload/status-machine state
(`cmin2`, `cmax2` abort, `in_queue_idx`, miss/offload queue updates), not merely
on scalar radius, raw kind2 rows, host materialization, or RTDL's existing
global-bound flag.

## Active Objective

The active objective remains:

```text
Complete X-HD paper reproduction: the Python/RTDL/partner implementation should
provide the same functionality as the paper author's original C++/CUDA/OptiX
implementation, and should provide comprehensive performance evaluation.
User-facing target: besides language, everything else is the same.
```

This objective is not yet achieved. The current work is still progress toward
that objective, not a narrowed replacement for it.

## Evidence Levels

### Level A - Bounded Same-Input Value Reproduction

Status: complete and externally reviewed through Goal5126.

What is proved:

```text
author hd_exec builds and runs on bounded fixtures;
RTDL bounded 2-D and 3-D routes match author HDResult;
directed-vs-symmetric Hausdorff semantics were disambiguated;
author and RTDL both compute directed input1 -> input2 on the discriminating
fixture, not symmetric Hausdorff.
```

What is not proved:

```text
full paper dataset reproduction;
author RT-core algorithm parity;
paper figure reproduction;
author-vs-RTDL performance parity.
```

### System Extraction From X-HD

Status: externally reviewed through Goals5127-5128.

Extracted generic RTDL assets:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest / covering-radius reducer;
non-Hausdorff consumer proof through facility-service-radius / worst-served
demand.
```

Meaning:

```text
Hausdorff remains an app-level composition.
RTDL core exposes generic nearest / witness / reduction primitives.
```

### Level B - Same-Source Representative Public Workloads

Status: strongest current functional evidence, but not exact paper input
identity.

Primary public Level-B candidate:

```text
source = Stanford Dragon public mesh
target = Stanford HappyBuddha public mesh
```

Key facts:

```text
author rerun HDResult = 0.12572988867759705
RTDL route distance   = 0.12572988629271128
author-vs-RTDL abs diff ~= 2.4e-9
```

Important boundary:

```text
The public data still differs from the paper-branch log by about 1.937e-7.
Therefore this is representative same-source evidence, not byte-identical exact
paper input evidence.
```

Important Goal5211 caveat:

```text
Goal5211 global-bound early break is exact for the final directed-HD scalar
value, but per-source witnesses may be approximate.

per_source_witness_exact = false
early_aborted_sources    = 409376 / 437645
```

Allowed summary:

```text
One Level-B same-source representative workload, Dragon -> HappyBuddha,
matches the author rerun HD scalar on public data. This is exact for the
directed-HD maximum value, but not for per-source witnesses and not for exact
paper input identity.
```

Forbidden summary:

```text
Full paper reproduction is complete.
RTDL matches the paper log exactly.
RTDL reproduces exact per-source witnesses at scale under Goal5211.
RTDL has author performance parity.
```

## Performance Progress Snapshot

No author-vs-RTDL ratio is authorized. These are RTDL route/regime numbers only.

Representative Level-B Dragon -> HappyBuddha route evolution:

```text
Goal5188: initial full-public RTDL route wall about 7.30s
Goal5191: inline512 route wall about 3.65s
Goal5195: intersection-stage current-best pruning about 2.6s
Goal5196: dense local-grid lookup about 2.26s
Goal5203: direct NumPy matrix input about 1.238-1.239s
Goal5204: linear max-nearest reduction about 1.17-1.18s
Goal5205: full gate total about 2.06s, route about 1.16-1.17s
Goal5207: explicit warm measured route about 0.626s after separate warmup
Goal5211: fresh route about 0.849s, explicit-warm route about 0.362s
Goal5212: full total including load about 1.531s,
          explicit-warm measured case total about 0.288s
```

Current interpretation:

```text
The RTDL route became much faster through generic system work, but the strongest
fast route is exact-value-only under a max-nearest / directed-HD contract.  It
must not be described as exact per-source witness reproduction.
```

Performance ratio remains unauthorized because the denominators are not aligned:

```text
author internal Running.AvgTime;
author process wall;
RTDL route wall;
RTDL full case total;
cold process;
warm long-lived process;
explicit warmup / measured case.
```

## Current Paper Figure Status

```text
Figure 5:
  Level-B graphics and bounded geo candidates exist;
  Dragon -> HappyBuddha is the strongest value-matched graphics candidate;
  no full figure matrix reproduction;
  no exact input status;
  no author-vs-RTDL ratio.

Figure 6:
  pruning / route diagnostics exist;
  no full paper figure reproduction.

Figure 7:
  author lb audit and Level-B lb diagnostics exist;
  exact lb comparison matrix is not reproduced.

Figure 8:
  tune_radius source / trace semantics partially mapped;
  narrow diagnostic adaptive mapping exists;
  no full Figure 8 add/double/adaptive matrix reproduction.

Figure 9:
  current author logs do not provide the required four-variant matrix;
  checked-in PDF is evidence, not a reproducible denominator.

Figure 10:
  source/scripts audited;
  checked-in scalability logs are missing;
  not reproduced.

Figure 11:
  memory denominator audit completed;
  RTDL generic offload telemetry exists;
  same-denominator author Figure 11 memory parity remains false.
```

## Already Completed And Reviewed

Externally reviewed:

```text
Goal5110: X-HD scaffold/provenance.
Goals5111-5126: bounded same-input author JSON and RTDL route gates, including
                 directed-vs-symmetric discriminating fixture.
Goals5127-5128: generic nearest pipeline extraction and non-Hausdorff consumer.
Goal5129: full-reproduction plan reviewed with amendment incorporated.
```

These are stable enough to cite as reviewed foundations.

## Implemented / Review Pending

Large parts of the active X-HD work are implemented but still review pending.
Do not silently upgrade them to externally approved.

Notable implemented/review-pending groups:

```text
Goals5130-5174:
  Level-B dataset mapping, route construction, native 3-D cell-MBR route, and
  multi-scale route matrices.

Goals5175-5212:
  paper-log indexing, full-public Dragon -> HappyBuddha Level-B route, route
  optimizations, global-bound early-break, and no-copy runner hygiene.

Goals5272-5283:
  Figure 11 memory / worklist telemetry and denominator closeout.

Goals5284-5298:
  Figure 9/5/7/8/10 source/log audits, candidate input acquisition, and graphics
  value prechecks.

Goals5299-5314:
  additional graphics / geo Level-B bounded or full-public value checks.

Goals5354-5362:
  tune_radius / radius queue semantics and narrow adaptive diagnostic mapping.

Goals5363-5371:
  lb / heavy-cell offload semantics, behavior gates, denominator reconciliation,
  raw telemetry, queue-state requirements, and inline/global-bound probes.
```

## Major Problems Solved

1. Bounded same-input X-HD value reproduction is reviewed complete.
2. Directed Hausdorff semantics are settled by a discriminating fixture.
3. Hausdorff has been reduced to generic RTDL primitives rather than a core
   X-HD primitive.
4. A non-Hausdorff consumer proved the generic nearest / max-nearest pipeline.
5. Public Level-B Dragon -> HappyBuddha scalar value match is strong.
6. The scalable route avoids full pairwise materialization at large public
   scale.
7. Route-local performance improved by almost an order of magnitude on the
   representative Level-B route, while preserving the scalar HDResult.
8. The app-owned PLY front door and generic coordinate matrix reuse removed
   large Python row/tuple costs.
9. `tune_radius` semantics are partially mapped through a narrow internal
   diagnostic path.
10. `lb` source semantics are pinned from author code.
11. RTDL can preserve author HD values under lb0/lb256-style behavior gates.
12. Generic raw frontier kind telemetry now gives count-only native diagnostics
    without materializing hundreds of millions of rows.
13. Goal5369 prevents repeated false explanations by recording exact runtime
    state required for the next `-lb` denominator gate.
14. Goal5370 gives a concrete app-owned queue-state reference shape.
15. Goal5371 rejects host materialization and existing RTDL global-bound as the
    missing `OffloadingSize` explanation.

## Major Problems Not Yet Solved

1. Exact paper input files / hashes remain unavailable or unproven.
2. Full paper figure matrices are not reproduced.
3. The fast Goal5211 route is exact-value-only; per-source witnesses may be
   approximate.
4. Author-vs-RTDL performance ratio remains unauthorized.
5. Author RT-core algorithm parity remains unproved.
6. General author `tune_radius` support remains unauthorized.
7. Explicit `-lb` support remains unauthorized.
8. `-lb` row-count parity is not established.
9. Same-denominator Figure 11 memory parity remains false.
10. Many recent goals are implemented / review pending, not externally approved.
11. The current `-lb` blocker has moved from value correctness to author shader
    payload/status-machine semantics.

## Active `-lb` / Heavy-Cell Offload State

Author Dragon -> AsianDragon Level-B pair:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
preprocessing = translate_each_input_to_min_bound
exact_paper_dataset_identity_proven = false
```

Author `lb0`:

```text
HDResult       = 52.453487396240234
OffloadingSize = 0
WL Heavy Peak  = 0
```

Author `lb256`:

```text
HDResult       = 52.453487396240234
OffloadingSize = 27133990
WL Heavy Peak  = 217071920
Radius         = 79.2156982421875
NumInputPoints = 437645
```

RTDL facts so far:

```text
lb0 / disabled counterpart:
  HDResult matches within tolerance;
  heavy_offload_peak_rows = 0.

lb256 / full-cover counterpart:
  HDResult matches within tolerance;
  heavy_offload_peak_rows = 24508120;
  author-width bytes      = 196064960;
  row-count parity        = false.

author-radius materialized rows:
  21006960.

author-radius no-inline raw kind2 rows:
  304981889.

author-radius inline count-only kind2:
  21006960.

author-radius inline + existing global-bound count-only:
  21006960.
```

Rejected explanations:

```text
byte formula mismatch;
scalar radius mismatch alone;
materialized RTDL heavy/offload rows;
all raw same-radius kind2 rows;
host materialization / sort artifact;
existing RTDL global-bound as author cmax2 abort proxy.
```

Current conclusion:

```text
Author OffloadingSize is an iterative shader/status-machine denominator.
The next work must align dynamic cmin2/current-best state, cmax2 abort status,
active in_queue_idx, miss/offload queue updates, and raw offload rows before
sort/reduce.
```

## Recent Goals 5369-5371

### Goal5369 - Queue-State Requirements

Status: `implemented_review_pending`

Result:

```text
status = lb_queue_state_requirements_ready__implementation_requires_queue_state_reconstruction_or_author_instrumentation
exit_label = lb_queue_state_requirements_ready__no_explicit_lb_support_yet
```

Minimum next-gate state:

```text
active_in_queue_indices;
per_source_current_best_or_cmin2;
per_iteration_radius_schedule;
raw_offload_row_shape;
author_width_memory_view.
```

### Goal5370 - Author-Like Queue-State Reference

Status: `implemented_review_pending`

Result:

```text
status = bounded_author_like_queue_state_reference_ready
exit_label = bounded_queue_state_reference_matches_author_rows__dragon_lb_still_unimplemented
```

State shape:

```text
active_source_ids;
active_in_queue_indices;
nearest_target_ids;
nearest_distances;
current_best_sq;
confirmed_source_ids;
unresolved_source_ids;
cmax2_before;
cmax2_after.
```

Boundary:

```text
This is a bounded terminal one-iteration fixture. It proves state shape, not
Dragon -> AsianDragon lb denominator parity.
```

### Goal5371 - Inline / Global-Bound lb Probe

Status: `implemented_review_pending`

Result:

```text
status = inline_and_global_bound_lb_probes_ready__author_denominator_still_unmatched
exit_label = inline_payload_and_existing_global_bound_do_not_explain_author_offloading_size
```

Key numbers:

```text
author OffloadingSize                      = 27133990
RTDL author-radius materialized rows       = 21006960
RTDL author-radius inline count-only kind2 = 21006960
RTDL inline + global-bound count-only      = 21006960
RTDL no-inline raw kind2 from Goal5368     = 304981889
```

Meaning:

```text
The 21006960 count is native inline behavior, not host materialization.
Existing RTDL global-bound early break does not fire here and does not model
author cmax2 abort.
```

## Planned Work

### P0 - Strict review packet

Send the current `-lb` packet for strict review:

```text
history/internal_docs/call_for_review_goal5369_xhd_lb_queue_state_requirements_2026-07-09.md
history/internal_docs/call_for_review_goal5370_xhd_author_like_queue_state_reference_2026-07-09.md
history/internal_docs/call_for_review_goal5371_xhd_inline_global_bound_lb_probe_2026-07-09.md
```

Also keep the earlier packet visible:

```text
history/internal_docs/call_for_review_goals5363_5368_xhd_lb_heavy_offload_packet_2026-07-09.md
```

### P1 - Author shader/status-machine gap matrix

Next technical goal should explicitly map author shader states to RTDL route
state. It should cite author source and produce a field-by-field matrix for:

```text
per-ray status: init / offloading / aborted / miss;
dynamic cmin2 current best;
cmax2 abort condition;
offload append condition;
miss-queue update semantics;
active in_queue_idx semantics;
raw offload rows before sort/reduce.
```

Exit labels:

```text
status_machine_requirements_ready__implement_probe_next
status_machine_requires_author_instrumentation
```

### P2 - Author-queue-aligned `lb` trace

Implement one of two routes:

```text
Route A:
  reconstruct RTDL queue/current-best state through prior iterations, then run
  count-only raw offload telemetry under that active queue and status state.

Route B:
  instrument/regenerate author to expose active in_queue_idx, per-source cmin2,
  raw offload rows, and per-batch OffloadingSize contributions, then compare
  RTDL against that oracle.
```

Minimum artifact fields:

```text
author_offloading_size;
rtdl_raw_offload_rows_under_status_machine;
row_count_parity;
cmax2_abort_count;
offloading_status_count;
miss_status_count;
current_best_state_source;
author_width_bytes.
```

### P3 - Explicit `-lb` option decision

Only after P2:

```text
decide whether explicit -lb can be exposed under a narrow internal diagnostic
route or must remain fail-closed.
```

Value match alone is insufficient. The decision must address row denominator
and status-machine semantics.

### P4 - Continue full-paper dataset / figure work

Continue under these labels:

```text
Level B representative public data != exact paper input.
paper-log value match != file/hash provenance.
checked-in author PDF != reproducible denominator.
```

Priority:

```text
1. exact dataset provenance if available;
2. otherwise clearly labeled Level-B representative matrices;
3. no figure-level claims without exact or externally accepted denominator.
```

### P5 - Fair performance matrix after semantic alignment

Separate:

```text
author Running.AvgTime;
author process wall;
RTDL route time;
RTDL total time;
load/setup/output;
cold process;
warm long-lived process;
explicit warmup / measured case.
```

Only report a ratio after a review accepts the denominator.

## POD Use Plan

Use only the wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 upload <local> <remote>
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 download <remote> <local>
```

Known current remote state:

```text
remote workspace = /tmp/rtdl_goal5364
data              = /tmp/xhd_goal5234/data/dragon.ply
                    /tmp/xhd_goal5234/data/asian_dragon.ply
GPU               = NVIDIA RTX 4000 Ada Generation
native build      = OptiX build recently completed in /tmp/rtdl_goal5364
```

Expected next POD use:

```text
1. preflight wrapper;
2. upload only touched native/Python files;
3. rebuild OptiX only if src/native changed;
4. run Dragon -> AsianDragon status-machine / queue-aligned probes;
5. download JSON artifacts into Paper-reproduction-apps/x-hd-paper/results/;
6. write goal report and call-for-review before changing any claim status.
```

## Expected Timeline

This is an engineering estimate, not a promise:

```text
Next 1 goal:
  author shader/status-machine gap matrix, no large code change.

Next 1-2 goals:
  implement bounded or diagnostic status-machine probe, or author
  instrumentation if RTDL-only reconstruction is underdetermined.

Next 1 goal:
  run POD Dragon -> AsianDragon queue-aligned count probe and compare against
  author OffloadingSize.

Decision node:
  if row parity or a reviewed denominator explanation is achieved, decide
  narrow explicit -lb support;
  otherwise keep -lb fail-closed and document the remaining author RT-core gap.
```

## Current Claim Boundary

Allowed now:

```text
RTDL matches author HD values on bounded gates and selected same-source
representative public workloads.

RTDL has generic nearest / witness / frontier / telemetry primitives extracted
from X-HD pressure.

For Dragon -> AsianDragon lb256, RTDL preserves the author HD scalar and has a
compatible byte formula shape, but row-count parity is not established.

Goal5371 shows that neither host materialization nor existing RTDL global-bound
early break explains author OffloadingSize.
```

### Goal5372 - Author Shader Status-Machine Gap Matrix

Status: `implemented_review_pending`

Result:

```text
status = author_shader_status_machine_gap_matrix_ready__implementation_or_author_instrumentation_next
exit_label = status_machine_requirements_ready__lb_support_still_unauthorized
```

Goal5372 verifies the author source-level state machine:

```text
payload_0 = in_q_idx
payload_1 = n_hits
payload_2 = n_compared_pairs
payload_3 = status
payload_4/5 = cmin2

status bits = kInit / kOffloading / kAborted

critical branches:
  radius_or_cmin2_prune
  cmax2_mbr_abort
  heavy_cell_offload
  point_loop_early_break
  valid_complete_source
  miss_source

loadBalanceProcessing:
  sorts/reduces by in_q_idx, restores shader cmin2, and can update cmax2.
```

Next gate:

```text
author_shader_status_machine_lb_trace
```

Minimum fields:

```text
active_in_queue_size
raw_offload_rows_before_sort_reduce
raw_offload_rows_author_width_bytes
status_count_init/offloading/aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Not allowed:

```text
Full X-HD paper reproduction is complete.
Exact paper dataset identity is proven.
Figure 5/6/7/8/9/10/11 reproduction is complete.
Author RT-core algorithm parity is proven.
Explicit -lb support is complete.
Row-count parity for OffloadingSize is proven.
Same-denominator memory parity is proven.
RTDL/author performance ratio is fair or final.
Per-source witnesses are exact under the Goal5211 early-break route.
```

## Bottom Line

The project has made real progress: the X-HD app has driven reusable RTDL
nearest/frontier/telemetry APIs, a scalable Level-B route, route-local
performance improvements, and app-owned compatibility machinery for author
options. But the active `-lb` line has exposed the central remaining hard
problem: author X-HD is not just "count all heavy cells." It is a shader
payload state machine with dynamic current-best state, aborts, and queues.

The next serious work is therefore not another scalar tweak. It is either a
generic status-machine-compatible RTDL probe or author instrumentation that
reveals the raw queue oracle. Until that passes, explicit `-lb`, Figure 7,
Figure 11, author RT-core parity, and full X-HD reproduction must remain
unclaimed.
