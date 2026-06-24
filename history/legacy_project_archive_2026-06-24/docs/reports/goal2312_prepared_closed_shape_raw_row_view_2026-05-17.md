# Goal2312 Prepared Closed-Shape Raw Row View

## Purpose

Goal2301/Goal2303 made the prepared closed-shape membership traversal fast by
replacing the infinite point probe with a bounded point probe. The remaining
visible RayJoin-style PIP gap was no longer the RT traversal itself: positive
row output still paid Python dictionary materialization even when the caller
only needed a low-level row stream or row count.

Goal2312 adds the same generic row-view surface that prepared segment-pair
intersection already had:

```python
PreparedOptixPointClosedShapeMembership2D.run_raw(points, result_mode="positive_hits")
```

This returns an `OptixRowView` over
`(point_id, shape_id, membership)` rows. The higher-level `run()` API remains
unchanged and still returns Python dictionaries for learner-facing code.

## Design Boundary

- The native ABI is unchanged.
- The engine remains app-agnostic: point, closed shape, membership, and row view
  vocabulary only.
- No RayJoin-specific primitive, PIP-specific ABI, county/map naming, or
  spatial-join continuation was added.
- This is a Python boundary optimization for generic prepared row access. It is
  not a true zero-copy claim and not a device-resident continuation claim.

## Pod Evidence

Artifact:

- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json`

Environment:

- GPU: NVIDIA RTX A5000, driver 570.211.01
- Same RayJoin-exported 100,000-query streams used by the Goal2305 current
  comparison.
- The timing script reused `scripts/goal2292_rayjoin_current_prepared_comparison.py`
  after switching PIP positive-row timing to `prepared.run_raw(...)`.

Current medians:

| Row | Median seconds | Expected rows |
| --- | ---: | ---: |
| LSI raw witness rows | 0.010123 | 8,921 |
| LSI scalar count | 0.009986 | 8,921 |
| PIP positive raw row view | 0.008657 | 8,686 |
| PIP scalar count | 0.008476 | 8,686 |

Compared with Goal2305, PIP positive-row timing improved from `0.023158s` to
`0.008657s`, a 2.68x improvement, while preserving the exact 8,686 positive
memberships.

## Interpretation

This is the point where the RTDL RayJoin-style path is plausibly "working at
that level" for the scoped same-query streams: LSI and PIP both run in
single-digit milliseconds after preparation, exact row counts match the
CPU-verified artifacts, and the accepted route remains a generic RTDL primitive
stack rather than an app-custom engine path.

That phrase is deliberately bounded. This report does not claim:

- RTDL beats the RayJoin paper implementation.
- The RayJoin paper benchmark has been reproduced.
- Whole-app speedup.
- True zero-copy or device-resident continuation.
- v2.0 release authorization.

## Next Technical Gap

The next meaningful improvement is not another Python dictionary cleanup. It is
a generic device-resident row-stream / continuation contract so partner code can
reduce or consume prepared RTDL row streams without host-visible copyback and
host exact-refinement boundaries.

For v2.x hardening, keep this as app-agnostic output-stream work, not RayJoin
specialization.
