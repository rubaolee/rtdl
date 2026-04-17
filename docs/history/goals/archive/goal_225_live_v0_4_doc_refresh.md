# Goal 225: Live v0.4 Doc Refresh

## Why

After the `v0.4` line was reopened for GPU completion, several live user-facing
docs still reflected the earlier CPU/Embree-only shape or used wording that was
unnecessarily narrow or inconsistent.

This goal refreshes only the live `v0.4`-facing documentation. It is not a
whole-repo archive cleanup.

## Scope

Refresh the public/docs-front-door pages so they:

- describe the nearest-neighbor line as an active preview reopened for GPU completion
- state the real current backend surface for `fixed_radius_neighbors` and `knn_rows`
- avoid stale wording such as “accelerated support not implemented yet”
- keep example pages aligned with the actual backend choices
- keep the research-foundations page honest after the RTNN and pathology-paper corrections

## In Scope Files

- `README.md`
- `docs/README.md`
- `docs/features/fixed_radius_neighbors/README.md`
- `docs/features/knn_rows/README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/rtdl/dsl_reference.md`
- `docs/workloads_and_research_foundations.md`

## Out Of Scope

- archived goal reports
- old wiki drafts
- broad terminology expansion across every historical doc in the repo
- performance claims or benchmark refresh

## Acceptance

- live docs match the reopened `v0.4` GPU-required bar
- no obvious contradiction remains across the listed front-door pages
- the research-foundations page does not contradict its own workload-paper mapping
- review closure is recorded under at least `2+` AI consensus
