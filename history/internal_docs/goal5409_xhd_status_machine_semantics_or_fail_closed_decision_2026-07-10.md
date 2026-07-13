# Goal5409 X-HD Status-Machine Semantics Or Fail-Closed Decision

Date: 2026-07-10

Status:

```text
generic_statused_hit_stream_probe_authorized__explicit_lb_still_unsupported
```

## Purpose

Goal5407 showed that the explicit `-lb` gap is not just a uniform count
difference.  Goal5408 then ruled out the simplest compact/original cell-id
namespace explanation.

Goal5409 decides what to do next:

```text
Branch A: authorize one more generic semantic probe.
Branch B: fail-close explicit -lb under the current RTDL execution model.
```

The chosen branch is **Branch A**, but with a narrow contract and hard
fail-closed gates.

## Inputs

Goal5387 author trace v2:

```text
active queries                      = 437,645
author raw rows before sort/reduce  = 27,133,990 = 62 * active_count
author raw row hash                 = 4333109858711462591
author raw sample point ids         = [11168, 210712, 437119]
author raw sample cell ids          = [2924, 17, 17]
feedback_update_count               = 294
cmin2_after_ray == cmin2_after_lb   = true
```

Goal5406 RTDL full-cover surface:

```text
RTDL full-cover rows  = 24,508,120 = 56 * active_count
RTDL row hash         = 9732286907904247845
row count parity      = false
row hash parity       = false
```

Goal5407 membership result:

```text
classification = author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap
```

Goal5408 namespace result:

```text
classification = author_sample_cell_ids_exist_globally_but_not_for_author_sources
compact/original namespace remap explains author samples = false
```

Decision artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5409_status_machine_semantics_decision.json
```

## Author Source Evidence

POD source inspection used:

```text
/tmp/xhd-goal5387/author/src/rt/shaders/shaders_nn_uniform_grid.cu
/tmp/xhd-goal5387/author/src/hd_impl/hausdorff_distance_rt.h
```

The author raw offload stream is generated in the OptiX shader before
`loadBalanceProcessing`:

```text
offloading_point_ids.Append(in_q_idx)
offloading_cell_ids[tail] = mbr_id
```

This happens for large cells:

```text
np_in_cell > processing_threshold
```

but only after traversal/prune/current-best state has already affected the
intersection program:

```text
min_dist2 > radius^2 or min_dist2 >= cmin2  -> return
max_dist2 <= cmax2                          -> abort/status update
large cell                                  -> append offload row
small cell                                  -> scan points/update cmin2
```

After the raw stream is captured, `loadBalanceProcessing` sorts by active query,
groups rows, restores the shader-computed `cmin2`, scans deferred large cells,
and may update global `cmax2`.

## Decision

The remaining gap should not be treated as:

```text
add 6 rows per active;
rename compact/original cell ids;
patch the three sampled author rows;
directly call author-specific native logic.
```

Instead, one more semantic probe is justified because the author source shows a
generic-looking execution pattern:

```text
statused_large_cell_deferral_stream
```

Definition:

```text
A traversal-stage stream of deferred large-cell hits emitted under a generic
payload status machine: active query id, cell id, current-best state,
prune/abort/completed/miss status, and optional grouped continuation.
```

Why it is generic:

```text
It describes a spatial traversal/control-flow pattern, not X-HD itself.
It can apply to nearest/coverage pipelines that defer oversized cells.
It can be tested on app-neutral synthetic fixtures before X-HD traces.
```

## Required Next Goal

```text
Goal5410_generic_statused_large_cell_deferral_stream_probe
```

Goal5410 must implement no direct X-HD fix. It must first prove the generic
contract and only then attempt an X-HD bounded/full author-trace comparison.

Required gates:

1. **Synthetic app-neutral status stream gate**

   A non-X-HD fixture must exercise init/offload/abort/completed/miss style
   status transitions and large-cell deferral rows without paper names or
   author constants.

2. **Bounded X-HD author sample-row gate**

   A bounded X-HD trace must recover sampled author source/cell rows by
   semantics, not by hard-coded row counts or sample ids.

3. **Full Goal5387 row-identity gate**

   A full-public gate must compare:

   ```text
   row count;
   row hash;
   sampled point/cell ids;
   status counts;
   feedback_update_count;
   cmin2 hashes.
   ```

4. **Fail-closed exit**

   If the candidate requires X-HD-only constants or cannot recover row
   identity, explicit `-lb` remains unsupported and the status-stream line
   stops.

## Claim Boundary

Goal5409 authorizes:

```text
one generic semantic probe;
one bounded-to-full evidence ladder;
one fail-closed exit if row identity does not recover.
```

Goal5409 does **not** authorize:

```text
explicit -lb support;
row/hash parity against Goal5387;
Figure 7 or Figure 11 reproduction;
author-vs-RTDL performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction;
X-HD-specific logic in RTDL core/native.
```

## Validation

Local focused regression:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5409_status_machine_semantics_decision_test `
  tests.goal5408_cell_namespace_reconciliation_test `
  tests.goal5407_full_cover_delta_membership_probe_test

Ran 17 tests OK
```
