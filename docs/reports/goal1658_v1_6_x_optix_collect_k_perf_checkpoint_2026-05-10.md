# Goal1658 v1.6.x OptiX Collect-K Performance Checkpoint

## Verdict

`keep_fastest_solution_and_freeze_new_optimization_studies_until_v2_5`

The accepted fastest OptiX `COLLECT_K_BOUNDED` solution remains the opt-in
`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` path. It uses the CUB tiled
row-width-2 path, extended 128-tile capacity, and the existing binary compact
merge chain:

`row_width2_bounded_multi_tile_sort_merge`

No more collect-k optimization studies before v2.5. Future work before v2.5
should productize Python+RTDL app purity, documentation, gates, and migration
instead of opening new OptiX collect-k performance candidates.

## Accepted Solution

The retained implementation is the Goal1650 fastest-candidate capacity fix:

- `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` automatically enables the extended
  128-tile capacity for row-width-2 bounded collection.
- The accepted long-workload path is
  `row_width2_bounded_multi_tile_sort_merge`.
- The accepted high-count scope includes `candidate_count=196608` and
  `candidate_count=262144` on the A4500 pod evidence package.
- Parity was accepted for the retained fastest-candidate runs.

Representative retained timings from the accepted/repeated A4500 evidence:

| Artifact | Scope | Total |
| --- | --- | --- |
| `docs/reports/goal1650_post_fastest_196608.md` | `candidate_count=196608`, 128-tile fastest path | `total_ms=0.553565` |
| `docs/reports/goal1650_post_fastest_262144.md` | `candidate_count=262144`, 128-tile fastest path | `total_ms=0.683538` |
| `docs/reports/goal1652_fastest_cub_262144.md` | `candidate_count=262144`, fastest CUB control | `total_ms=0.675769` |
| `docs/reports/goal1653_fastest_262144.md` | `candidate_count=262144`, fastest control rerun | `total_ms=0.680568` |
| `docs/reports/goal1654_min_cap_4096_262144.md` | `candidate_count=262144`, default compact threshold | `total_ms=0.673688` |
| `docs/reports/goal1655_baseline_262144.md` | `candidate_count=262144`, repeated baseline | `total_ms=0.637297` |

These are exact-subpath measurements, not whole-application measurements.
The `0.637297 ms` row is retained as the fastest repeated baseline observation,
but the checkpoint should use the whole table rather than overclaiming one run
as a universal device constant.

## Rejected Candidates

The following later optimization candidates were studied and rejected:

- Full cooperative merge-chain fusion was rejected by the residency gate.
- Fused materialize+mark regressed to `total_ms=1.042890` at
  `candidate_count=262144`.
- Non-CUB 4096-tile sorting regressed to `total_ms=73.328500`.
- Deferred merge synchronization did not beat the accepted control path.
- Raised parallel compact thresholds regressed sharply; the default threshold
  remained best in the tested sweep.
- Skipping tile-overflow metadata reduced metadata work but did not improve
  measured total time.
- The four-way merge probe preserved parity in diagnostic scope but was slower
  for production-relevant group counts and is not enabled by the fastest path.

## Claim Boundary

This checkpoint does not authorize public speedup wording, whole-application
speedup wording, broad RTX/GPU acceleration wording, stable
`COLLECT_K_BOUNDED` promotion, v2.5 release action, or release tag action. It
does not promote `COLLECT_K_BOUNDED` to stable.

`COLLECT_K_BOUNDED` remains experimental. The fastest path is an opt-in
performance implementation to keep, not a public-language promotion by itself.
