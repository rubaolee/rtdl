# Goal3773 HIPRT Point-Group Nearest Witness

## Purpose

Goal3773 adds a generic HIPRT prepared `point_group_nearest_witness_2d` contract:

- `rtdl_hiprt_prepare_point_group_nearest_witness_2d`
- `rtdl_hiprt_run_prepared_point_group_nearest_witness_2d`
- `rtdl_hiprt_reduce_prepared_point_group_nearest_max_distance_2d`
- `rtdl_hiprt_destroy_prepared_point_group_nearest_witness_2d`

This is the next AMD/HIPRT parity slice after RTNN. It targets the Hausdorff/X-HD benchmark pressure point without putting Hausdorff vocabulary or app logic inside the HIPRT native engine.

The contract is a point-group nearest witness primitive, not a Hausdorff-specific endpoint.

## Design

The new prepared handle builds HIPRT custom AABB geometry over generic 2D point groups. A query point traverses candidate group bounds, and the any-hit path scans each hit group's contiguous point span to choose the nearest point by:

1. smaller squared distance;
2. lower neighbor id on exact ties.

The witness row contract is the existing generic `RtdlFixedRadiusNeighborRow` shape:

- `query_id`
- `neighbor_id`
- `distance`

The scalar reducer composes over those rows and returns the maximum nearest distance, with deterministic tie-breaking by query id and neighbor id. Rows without a witness are treated as infinity in the reduction, matching the OptiX point-group contract.

## Scope Boundary

This goal closes the HIPRT-side grouped max-distance reduction gap for the Hausdorff/X-HD lane, but it does not add device-column output. Therefore the v2.10 AMD/HIPRT parity row for `hausdorff_xhd` remains `needs_generic_hiprt_extension` with `nearest_witness_output_columns` still missing.

## Validation

Planned focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3773_hiprt_point_group_nearest_witness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Pod validation will build HIPRT on the NVIDIA CUDA/Orochi route and run the same focused suite. That is useful functional evidence for the HIPRT implementation, but it is not AMD hardware evidence.

## Claim Boundary

This goal does not authorize AMD performance claims, release claims, public speedup wording, broad RT-core wording, paper-reproduction wording, whole-app acceleration wording, or any claim that the Hausdorff/X-HD HIPRT lane is complete. Device-column parity and AMD hardware validation remain pending.
