# Goal1957 Partner Identity-Payload Contract

Date: 2026-05-14

Status: implementation checkpoint, external review requested

## Problem

Goal1956 showed that the v2.0 CuPy RawKernel continuation path can be much faster
than the v1.8 Python+RTDL path for database and graph control apps, but the two
polygon rows became slower on the L4 OptiX pod:

- `polygon_pair_overlap_area_rows`: v2/v1.8 ratio `15.103x`
- `polygon_set_jaccard`: v2/v1.8 ratio `17.936x`

That is not a failure of RT candidate discovery by itself. The slow path came
from the continuation contract: after RTDL found candidate identity, the Python
side rebuilt dense per-polygon cell masks on the CPU, copied those masks to
CuPy, and then launched a RawKernel over `candidate_pairs x global_cell_count`.
The partner received too much rematerialized shape data and too little compact
identity-preserving payload.

## Contract Direction

The general v2.0 fix is not to special-case the polygon examples. The engine
should hand partner code a compact, app-agnostic table with:

- stable hit or candidate identity columns;
- primitive or payload row indices;
- group or reduction keys when a continuation needs grouped aggregation;
- partner-visible payload columns already arranged for device execution;
- explicit shape/row counts and claim-boundary metadata.

The important design shift is:

```text
RTDL discovery result -> identity-preserving payload table -> partner continuation
```

instead of:

```text
RTDL discovery result -> Python rebuilds app data -> dense CPU table -> partner continuation
```

This preserves the v2.0 boundary: RTDL remains responsible for generic
acceleration and candidate identity, while the partner handles user continuation
work through a documented table contract.

## First Implementation Slice

`examples/rtdl_control_apps_cupy_rawkernel.py` now includes a
`PartnerPairPayloadTable` for the polygon control apps. The table stores compact
candidate pair indices plus axis-aligned extent and area payload columns for the
authored bounded-shape cases. The CuPy continuation consumes those columns
directly through `POLYGON_EXTENT_RAWKERNEL_SOURCE`.

This replaces the prior default CuPy continuation that built dense `left_masks`
and `right_masks` and scanned every cell for every candidate pair.

The slice is deliberately bounded:

- It is a first v2 partner-contract prototype for identity-preserving payload
  handoff.
- It is valid for the authored axis-aligned bounded-shape control apps.
- It does not claim arbitrary polygon overlay acceleration.
- It does not claim true engine-level zero-copy yet; the columns are still
  prepared by Python before CuPy receives them.
- It does not authorize v2.0 release performance claims without pod retesting and
  external consensus.

## Why This Is General Enough To Keep

The table shape is generic even though this first reducer is bounded-shape
specific. Database columns, graph frontier rows, hitcount rows, and polygon
candidate pairs can all use the same pattern:

1. RTDL emits identity and payload columns.
2. Partner code accepts column arrays by name and row count.
3. User continuation code chooses a reducer appropriate for its semantics.
4. The runtime records which part is RTDL evidence and which part is user/partner
   continuation evidence.

The lesson for v2.0 is that partner acceleration depends at least as much on the
handoff schema as on the downstream GPU kernel.

## Current Validation

Local non-GPU validation:

- `py -3 -m py_compile examples/rtdl_control_apps_cupy_rawkernel.py`
- `py -3 -m unittest tests.goal1953_control_apps_cupy_rawkernel_v2_test tests.goal1955_rawkernel_control_app_perf_test`

Both pass before pod retesting.

## Next Evidence Needed

Before using this as v2.0 performance evidence:

1. Run the Goal1956 pod runner again with `--partner cupy` and
   `--candidate-backend optix`.
2. Compare the polygon rows against the Goal1956 OptiX v8 L4 baseline.
3. Require an external Claude review of the contract and retest result.
4. Keep `v2_0_release_authorized`, `whole_app_speedup_claim_authorized`, and
   `broad_rt_core_speedup_claim_authorized` false until final v2.0 consensus.

