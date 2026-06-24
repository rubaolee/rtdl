# Goal4159 Mixed-Predicate Direct-Status Gap

Date: 2026-06-09

Status: diagnostic packet accepted; route promotion remains blocked.

## Purpose

Goal4158 made the predicate direct-status candidate fast when every point is predicate-true. That is useful, but it is not enough for RT-DBSCAN-like workloads with border/noise points. Goal4159 deliberately forced mixed predicate rows by overriding radius and min-neighbor thresholds, then compared:

- current grouped-stream Numba signature route
- predicate direct-status `until_stable`
- predicate direct-status `single_pass_candidate`

The pod artifact is:

- `docs/reports/goal4159_mixed_predicate_direct_status_scale_pod.json`
- Commit: `63cfbc9a`
- GPU: RTX 4000 Ada pod using the same CUDA 12.4 / OptiX environment as Goal4158
- Rows: 7 mixed parameter cases, 21 total runs, 14 comparisons

## Results

The packet found two separate behaviors:

1. Component label-order drift: clustered rows have different exact label ids, but the same core/noise counts and the same sorted component-size multiset.
2. Real border-assignment gap: the `road_sparse_many_noise` row has the same core/noise count, but a different sorted component-size multiset because one small border component is absorbed into a larger component under the predicate route's lowest-neighbor candidate policy.

| Case | Dataset | Points | Candidate | Exact signature | Canonical size signature | Ratio |
| --- | --- | ---: | --- | --- | --- | ---: |
| clustered half-radius high-threshold | clustered3d | 65,536 | until_stable | no | yes | 1.347x |
| clustered half-radius high-threshold | clustered3d | 65,536 | single_pass | no | yes | 2.357x |
| clustered half-radius high-threshold | clustered3d | 131,072 | until_stable | no | yes | 1.390x |
| clustered half-radius high-threshold | clustered3d | 131,072 | single_pass | no | yes | 2.550x |
| road sparse many-noise | road3d | 65,536 | until_stable | no | no | 0.341x |
| road sparse many-noise | road3d | 65,536 | single_pass | no | no | 0.516x |
| road mid-sparse mixed-clusters | road3d | 65,536 | until_stable | yes | yes | 0.318x |
| road mid-sparse mixed-clusters | road3d | 65,536 | single_pass | yes | yes | 0.507x |
| ngsim sparse many-noise | ngsim_dense | 65,536 | until_stable | yes | yes | 0.309x |
| ngsim sparse many-noise | ngsim_dense | 65,536 | single_pass | yes | yes | 0.530x |
| ngsim mid-sparse multicluster | ngsim_dense | 65,536 | until_stable | yes | yes | 0.420x |
| ngsim mid-sparse multicluster | ngsim_dense | 65,536 | single_pass | yes | yes | 0.749x |
| ngsim mid-sparse multicluster | ngsim_dense | 131,072 | until_stable | yes | yes | 0.599x |
| ngsim mid-sparse multicluster | ngsim_dense | 131,072 | single_pass | yes | yes | 1.106x |

Ratio is current grouped-stream elapsed time divided by candidate elapsed time. Values above 1.0 mean the predicate direct-status candidate is faster.

## Interpretation

The all-predicate fast path is not enough for mixed rows:

- Exact signature matches: 8/14 comparisons.
- Canonical size-signature matches: 12/14 comparisons.
- Border-candidate updates are present in all candidate rows, so the Goal4158 all-true shortcut did not apply.
- `until_stable` wins only the two clustered rows.
- `single_pass_candidate` wins the two clustered rows plus the 131k NGSIM mid-sparse row, but remains a candidate because convergence is explicitly not proven.

The key design issue is a generic border-assignment policy, not app-specific DBSCAN logic. The predicate route currently assigns non-predicate border points to the lowest predicate neighbor candidate it observes. The current grouped-stream route follows its existing component-labeling policy. Those can disagree for ambiguous border points that touch multiple predicate components.

## Boundary

Goal4159 blocks predicate direct-status route promotion for mixed predicate rows. It also blocks broad wording that the Goal4158 route solved RT-DBSCAN generally.

All claim flags in the artifact remain false:

- `route_promotion_authorized: false`
- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_rt_core_claim_authorized: false`
- `whole_app_claim_authorized: false`

## Next Engineering Step

Add a generic border-assignment contract for predicate component signatures. The route should expose an explicit policy such as `lowest_neighbor`, `lowest_component_root`, or `reference_grouped_stream_compatible`, and the benchmark should compare canonical component-size signatures when label ids are not semantically meaningful.
