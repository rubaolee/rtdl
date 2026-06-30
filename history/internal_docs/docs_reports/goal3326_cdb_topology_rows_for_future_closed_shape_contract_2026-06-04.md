# Goal3326 - CDB Topology Rows For Future Closed-Shape Contract

Date: 2026-06-04

## Purpose

Goal3324 added a candidate primitive for topology-aware closed-shape membership/count. Goal3326 adds a small Python-side data-preparation helper:

```python
rtdsl.chains_to_topology_rows(dataset)
```

The helper exposes CDB chain topology as normalized rows:

- `chain_id`;
- `point_count`;
- `first_point_id`;
- `last_point_id`;
- `left_face_id`;
- `right_face_id`;
- `has_left_face`;
- `has_right_face`.

## Boundary

This helper does not reconstruct faces, classify point membership, choose boundary ownership, or encode RayJoin paper semantics. It only exposes generic topology columns already present in the CDB input.

That makes it useful input metadata for the future candidate primitive without moving app policy into the native engine.

## Validation

The focused test verifies:

- topology rows preserve left/right face IDs;
- `limit_chains` is honored;
- the helper is exported from `rtdsl`;
- the helper does not replace `chains_to_polygons` or `chains_to_polygon_refs`.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false

