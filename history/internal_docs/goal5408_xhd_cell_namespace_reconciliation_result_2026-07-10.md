# Goal5408 X-HD Cell Namespace Reconciliation Result

Date: 2026-07-10

Status:

```text
cell_namespace_reconciliation_complete__sample_rows_not_recovered
```

## Purpose

Goal5407 showed that sampled author raw offload rows are absent from the RTDL
full-cover surface.  Goal5408 asks a narrower question before changing native
code:

```text
Are the missing author sample rows merely a compact-cell-id vs original-grid-cell-id
namespace mismatch?
```

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5408_cell_namespace_reconciliation.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5408_cell_namespace_reconciliation_pod.json
tests/goal5408_cell_namespace_reconciliation_test.py
```

## POD Execution

POD preflight:

```text
POD_OK
hostname = 45c502cfccb5
GPU      = NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

POD focused tests:

```text
python3 -m unittest \
  tests.goal5408_cell_namespace_reconciliation_test \
  tests.goal5407_full_cover_delta_membership_probe_test

Ran 11 tests in 0.497s
OK (skipped=1)
```

POD real full-public runner:

```text
status  = cell_namespace_reconciliation_complete__sample_rows_not_recovered
matched = true
```

Local validation after artifact download:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5408_cell_namespace_reconciliation_test \
  tests.goal5407_full_cover_delta_membership_probe_test \
  tests.goal5406_real_full_cover_surface_stream_gate_test \
  tests.goal5405_full_cover_delta_status_bridge_test

Ran 20 tests
OK
```

## Result

Grid identity contract:

```text
cell_id_contract  = compact_zero_based_with_original_cell_ids
grid_shape        = [96, 60, 72]
cell_count        = 14,710
compact id range  = [0, 14,709]
original id range = [3,406, 413,966]
```

Goal5407 delta preserved:

```text
active_count           = 437,645
RTDL full-cover rows   = 24,508,120
author raw rows        = 27,133,990
delta rows             = 2,625,870
delta rows per active  = 6
RTDL rows per active   = exactly 56 for every active source
RTDL row hash          = 9732286907904247845
author row hash        = 4333109858711462591
```

Author sample namespace reconciliation:

```text
source=11168, author_cell=2924:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact?  false
  present for this source as original? false
  compact 2924 maps to original 126733

source=210712, author_cell=17:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact?  false
  present for this source as original? false
  compact 17 maps to original 12047

source=437119, author_cell=17:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact?  false
  present for this source as original? false
  compact 17 maps to original 12047
```

Classification:

```text
author_sample_cell_ids_exist_globally_but_not_for_author_sources
```

Decision fields:

```text
compact_original_namespace_remap_explains_author_samples = false
explicit_lb_support_authorized = false
direct_native_fix_authorized = false
recommended_next_goal = Goal5409_status_machine_semantics_or_fail_closed_decision
```

## Interpretation

Goal5408 rules out the simplest namespace explanation.

The author sample cell ids are not RTDL original grid cell ids. They do exist
as RTDL global compact ids, but for the sampled author sources those compact
cells are not part of the RTDL full-cover surface. Therefore a simple
compact/original id remap is insufficient.

This pushes the remaining explicit `-lb` gap toward status-machine / feedback /
load-balance semantics, or toward an author/RTDL grid traversal semantic
difference deeper than id naming.

## Claim Boundary

This goal proves:

```text
The current RTDL compact/original cell-id mapping does not recover the sampled
author raw offload rows for their source ids.
```

This goal does not prove:

```text
explicit -lb support;
author row/hash parity;
Figure 7 or Figure 11 reproduction;
performance parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Recommended Next Step

```text
Goal5409: status-machine semantics or fail-closed decision.
```

Goal5409 should decide whether one more generic semantic probe is justified, or
whether explicit `-lb` should be closed as unsupported under the current RTDL
execution model.

Minimum inputs to Goal5409:

```text
Goal5387 author trace v2 oracle
Goal5406 real full-cover surface
Goal5407 sample-membership probe
Goal5408 compact/original namespace reconciliation
```

Goal5409 must not hard-code 6 rows per active, 62 rows per active, X-HD option
names, paper figure semantics, or author-only logic into RTDL core/native.
