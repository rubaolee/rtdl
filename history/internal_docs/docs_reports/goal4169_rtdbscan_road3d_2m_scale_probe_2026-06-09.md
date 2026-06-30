# Goal4169: RT-DBSCAN Road3D 2M Scale Probe

Status: accepted bounded scale evidence; no route promotion.

## Purpose

Goal4169 extends the RT-DBSCAN road-like scale evidence from 1,048,576 points to
2,097,152 points after the Goal4168 policy-aware route registry refresh.

This is a scale probe, not a new implementation goal. It answers one narrow
question: does the current explicit all-predicate/direct-status family stay
useful on the weak road-like profile at 2M points?

## Pod Evidence

Artifact:

`docs/reports/goal4169_rtdbscan_road3d_2m_scale_probe_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `72a4aedc6425646e00cf903c395c6b007cbd3dcc`
- Dataset: `road3d`
- Point count: 2,097,152
- Partition cell factor: `0.25`
- Repeat/warmup: repeat 2, warmup 1

## Result

| Route | Measured run (s) | Same RT-DBSCAN signature | Notes |
| --- | ---: | --- | --- |
| current grouped-stream Numba | 28.948369 | reference | conservative current route |
| prepared direct-status component signature | 20.278547 | generic component schema only | 1.428x faster, but not the RT-DBSCAN app signature shape |
| predicate all-true direct-status wrapper | 20.513675 | yes | 1.411x faster, fast path observed |

The plain prepared direct-status row returns the generic component-size
signature schema. It has one component of size 2,097,152, matching the component
size meaning of the reference, but it does not include the RT-DBSCAN
`cluster_sizes/core_count/noise_count` app signature shape.

The predicate all-true row wraps that same generic component structure as the
RT-DBSCAN signature. It matches the current grouped-stream signature exactly,
observes `all_predicate_fast_path: true`, and records
`border_candidate_updates: 0`.

## Interpretation

The road-like 2M result is useful because it was the profile whose direct-status
replay ratio had been weakest at 1M. The all-predicate wrapper remains above
parity at 2M (`1.411x` measured-run speedup over the current grouped-stream
route), so the all-predicate route remains credible as an explicit user-selected
route for rows whose predicate flags are known or measured all true.

This does not solve mixed-predicate rows. Goals4165-4168 still stand: mixed
predicate component-size contracts require an explicit border-assignment policy,
and hidden route, factor, or policy selection remains blocked.

## Boundary

This report does not authorize automatic route selection, automatic partner
selection, automatic factor selection, release, public speedup wording, broad
RT-core wording, whole-app benchmark claims, paper-reproduction claims,
app-specific engine logic, native ABI additions, AMD performance claims, or
true-zero-copy claims.
