# X-HD Comprehensive Midterm Status After Goal5409

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__full_cover_surface_real__cell_namespace_remap_not_enough__statused_hit_stream_probe_authorized__explicit_lb_unsupported__full_paper_not_complete
```

This report supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5408_2026-07-10.md
```

## 1. Executive Summary

X-HD remains the active full-paper-reproduction project.

Current state:

```text
bounded same-input value reproduction       = complete and externally reviewed
generic nearest/witness system extraction   = complete and externally reviewed
Level-B public scalar line                  = strong
exact paper datasets                        = not proven
full paper reproduction                     = not complete
explicit -lb / raw author offload stream    = unsupported
```

The strongest scalar Level-B line remains public Stanford
Dragon -> HappyBuddha:

```text
author hd_exec HDResult = 0.12572988867759705
RTDL route distance     = 0.12572988629271128
absolute difference     ~= 2.38e-9
```

The strongest fast scalar route remains:

```text
fresh route                         ~= 0.849s
fresh total including input load    ~= 1.531s
explicit-warm route median          ~= 0.362s
explicit-warm measured case total   ~= 0.288s
```

Boundary:

```text
This fast scalar route is exact for final directed-Hausdorff / max-nearest
value, but early-aborted per-source witnesses may be approximate.
```

Newest decision:

```text
Goal5409 authorizes exactly one more generic semantic probe:
statused_large_cell_deferral_stream.
```

This does not mean explicit `-lb` is supported. It means the remaining row
identity gap has a plausible app-neutral execution-model explanation worth one
bounded-to-full probe before fail-closing.

## 2. Completed Foundation

Completed and externally reviewed:

```text
Goal5110: X-HD scaffold / provenance.
Goals5111-5126: bounded same-input author JSON and RTDL route gates, including
                 directed-vs-symmetric discrimination.
Goals5127-5128: generic nearest pipeline extraction and non-Hausdorff consumer.
Goal5129: full-reproduction plan with review amendment incorporated.
```

This establishes bounded value reproduction and the author contract:

```text
Hausdorff direction = directed input1 -> input2
```

X-HD has produced app-neutral RTDL assets:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest / directed-Hausdorff reducer;
grid-cell descriptors;
cell-MBR candidate/frontier rows;
nearest-state seed/frontier contracts;
native 3-D cell-MBR OptiX traversal front doors;
coordinate-matrix front-door convention;
linear finite max-nearest reduction;
active-query status-stream contracts and native smoke.
```

Hausdorff itself remains an app-level composition, not a core primitive.

## 3. Not Complete

Still not complete:

```text
exact paper input file/hash provenance;
full Figure 5-11 reproduction;
Figure 7 load-balance / explicit -lb parity;
Figure 11 same-denominator memory parity;
author-vs-RTDL performance ratio;
full X-HD paper reproduction.
```

Dataset boundary:

```text
matching counts, bounding boxes, Gini, or HDResult is not exact input identity.
exact dataset status requires file/hash or equivalent provenance.
```

## 4. Explicit `-lb` Evidence So Far

Author Goal5387 trace v2:

```text
active queries                      = 437,645
author raw rows before sort/reduce  = 27,133,990 = 62 * active_count
author raw row hash                 = 4333109858711462591
feedback_update_count               = 294
```

RTDL explored surfaces:

```text
bridge rows             = 2,188,225
native v7 status rows   = 2,600,727
default raw kind2 rows  = 21,006,960
full-cover rows         = 24,508,120 = 56 * active_count
author raw rows         = 27,133,990 = 62 * active_count
```

Full-cover is the closest RTDL surface, but not parity.

## 5. Goal5406 / 5407 / 5408

Goal5406 generated the real RTDL full-cover surface:

```text
RTDL full-cover rows       = 24,508,120
author raw rows            = 27,133,990
delta                      = 2,625,870 = 6 * active_count
RTDL full-cover row hash   = 9732286907904247845
author raw row hash        = 4333109858711462591
hash parity                = false
```

Goal5407 proved the gap is not merely a count delta:

```text
rows per active = exactly 56 for every active source

source=11168,  author_cell=2924, present in RTDL full-cover=false
source=210712, author_cell=17,   present in RTDL full-cover=false
source=437119, author_cell=17,   present in RTDL full-cover=false
```

Goal5408 ruled out simple compact/original cell-id remapping:

```text
source=11168, author_cell=2924:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact/original? false / false

source=210712, author_cell=17:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact/original? false / false
```

Interpretation:

```text
The current gap is row identity / status-stream semantics, not count-only and
not compact/original namespace naming.
```

## 6. Goal5409 Decision

Goal5409 inspects the author execution semantics and authorizes one more
generic semantic probe.

Author source evidence:

```text
/tmp/xhd-goal5387/author/src/rt/shaders/shaders_nn_uniform_grid.cu
/tmp/xhd-goal5387/author/src/hd_impl/hausdorff_distance_rt.h
```

Observed author semantics:

```text
The OptiX shader appends raw offload rows before loadBalanceProcessing.
Large cells are appended when they survive prune/current-best checks and
np_in_cell > processing_threshold.
The shader carries init/offloading/aborted status through OptiX payload.
loadBalanceProcessing later groups rows by active query and may update cmax2.
```

Decision:

```text
Authorize Goal5410_generic_statused_large_cell_deferral_stream_probe.
```

Generic candidate:

```text
statused_large_cell_deferral_stream
```

Meaning:

```text
A traversal-stage stream of deferred large-cell hits emitted under a generic
payload status machine: active query id, cell id, current-best state,
prune/abort/completed/miss status, and optional grouped continuation.
```

Why not fail-close immediately:

```text
The author raw stream is not just an X-HD output format. It is a generic
control-flow shape: traversal defers oversized cells into a continuation queue.
This deserves one app-neutral bounded-to-full probe before closing the line.
```

Why explicit `-lb` is still unsupported:

```text
No row-count parity.
No row-hash parity.
No sampled row parity.
No status/feedback parity.
No Figure 7/11 claim.
```

## 7. Required Goal5410 Gates

Goal5410 must pass these gates or fail-close:

1. **Synthetic app-neutral status stream**

   ```text
   Non-X-HD fixture; no paper names; no author constants.
   ```

2. **Bounded X-HD author sample-row gate**

   ```text
   Recover sampled author rows by semantics, not hard-coded source/cell ids.
   ```

3. **Full Goal5387 row identity gate**

   Compare:

   ```text
   row count;
   row hash;
   sampled point/cell ids;
   status counts;
   feedback_update_count;
   cmin2 hashes.
   ```

4. **Fail-closed exit**

   ```text
   If the candidate needs X-HD constants or cannot recover row identity,
   explicit -lb remains unsupported and the status-stream line stops.
   ```

## 8. Validation

Goal5409 local focused regression:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5409_status_machine_semantics_decision_test `
  tests.goal5408_cell_namespace_reconciliation_test `
  tests.goal5407_full_cover_delta_membership_probe_test

Ran 17 tests OK
```

## 9. POD Usage Expectation

Goal5410 will require POD only once it moves from local contract/test work to
native/status-stream execution.

Use only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Do not use naked SSH.

## 10. Claim Boundary

Allowed:

```text
X-HD has strong Level-B scalar evidence and real generic RTDL system
extraction. Goal5409 authorizes one generic statused hit-stream probe because
the remaining explicit -lb row identity gap is not explained by count or
cell-id namespace.
```

Forbidden:

```text
full X-HD paper reproduction;
exact paper dataset reproduction;
Figure 7 reproduction;
Figure 11 reproduction;
explicit -lb support;
row/hash parity with author raw stream;
author-vs-RTDL performance ratio;
warm/diagnostic numbers as default fresh performance;
X-HD-specific logic in RTDL core/native.
```
