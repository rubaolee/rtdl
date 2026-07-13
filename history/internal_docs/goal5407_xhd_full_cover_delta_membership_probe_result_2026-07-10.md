# Goal5407 X-HD Full-Cover Delta Membership Probe Result

Date: 2026-07-10

Status:

```text
full_cover_delta_isolated__row_identity_or_feedback_semantics_still_open
```

## Purpose

Goal5406 proved that RTDL can generate the real full-public full-cover surface:

```text
RTDL full-cover rows     = 24,508,120 = 56 * 437,645
author Goal5387 raw rows = 27,133,990 = 62 * 437,645
delta                    = 2,625,870 = 6 * active_count
```

Goal5407 asks whether this gap is merely a uniform `+6 rows/active` count gap,
or whether author row identity differs from the RTDL full-cover surface.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5407_full_cover_delta_membership_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5407_full_cover_delta_membership_probe_pod.json
tests/goal5407_full_cover_delta_membership_probe_test.py
```

## POD Result

```text
schema  = rtdl.paper_reproduction.xhd.goal5407.full_cover_delta_membership_probe.v1
status  = full_cover_delta_isolated__row_identity_or_feedback_semantics_still_open
matched = true
```

Delta:

```text
active_count                     = 437,645
total_delta_rows                 = 2,625,870
delta_rows_per_active_if_uniform = 6
delta_rows_per_active_remainder  = 0
```

RTDL per-source full-cover distribution:

```text
row_count = 24,508,120
rows_per_active_histogram = {56: 437,645}
all_sources_have_same_row_count = true
```

Author sample membership in RTDL full-cover:

```text
source=11168,  author_cell=2924, present_in_rtdl_full_cover=false
source=210712, author_cell=17,   present_in_rtdl_full_cover=false
source=437119, author_cell=17,   present_in_rtdl_full_cover=false
```

Author state evidence:

```text
feedback_update_count = 294
cmin2_after_ray_hash = 10400538358226239013
cmin2_after_load_balance_hash = 10400538358226239013
cmin2_after_ray_equals_after_load_balance = true
status_count_miss = 0
status_count_completed = 0
status_count_aborted = 0
```

Classification:

```text
label = author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap
```

## Interpretation

The remaining gap is not only a row-count gap.  RTDL's full-cover surface is
uniformly 56 rows per active source, and the author stream is uniformly 62 rows
per active source, but sampled author `(source, cell)` rows are absent from the
RTDL full-cover surface.

Therefore explicit `-lb` remains unsupported.  The next problem is row identity:
cell-id namespace, status transition, feedback, or load-balance processing
semantics.

## Validation

Local focused regression:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5407_full_cover_delta_membership_probe_test `
  tests.goal5406_real_full_cover_surface_stream_gate_test `
  tests.goal5405_full_cover_delta_status_bridge_test `
  tests.goal5394_full_cover_delta_status_probe_test

Ran 18 tests in 2.977s
OK
```

## Claim Boundary

This goal proves:

```text
The real RTDL full-cover surface is uniform at 56 rows per active source.
The author delta is uniform at 6 rows per active source.
Sampled author rows are not a subset of the RTDL full-cover row set.
```

This goal does not prove:

```text
explicit -lb support;
row/hash parity against Goal5387;
Figure 7 or Figure 11 reproduction;
author performance parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Recommended Next Step

```text
Goal5408: full-cover row identity / cell-id namespace reconciliation.
```

Goal5408 should start by comparing author cell ids against RTDL compact cell
ids and original grid cell ids before changing native code.
