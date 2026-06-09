# Goal4173: Declared All-Predicate RT-DBSCAN 2M Probe

Status: accepted bounded pod evidence; no route promotion.

## Purpose

Goal4172 added an explicit caller-declared all-predicate RT-DBSCAN route:

`partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d`

Goal4173 measures that route on the road-like 2M benchmark shape. The route is
only valid when the caller externally proves that every predicate flag is true.
It skips the OptiX count-threshold predicate measurement phase and feeds
caller-declared all-true predicate columns into the existing generic predicate
direct-status continuation.

## Pod Evidence

Consolidated artifact:

`docs/reports/goal4173_declared_all_predicate_rtdbscan_2m_probe_pod.json`

Raw per-route artifacts:

- `docs/reports/goal4173_current_grouped_warmed_2m_probe_pod.json`
- `docs/reports/goal4173_measured_alltrue_warmed_2m_probe_pod.json`
- `docs/reports/goal4173_declared_warmed_2m_probe_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `0ec736408af952a61485680865c7f760fb406799`
- Dataset: `road3d`
- Point count: 2,097,152
- Seed: `20260519`
- Partition cell factor: `0.25`
- Repeat/warmup: repeat 1, warmup 0
- Runtime prewarm: a 4,096-point tiny route-specific warmup before each 2M
  measurement, to avoid charging CUDA/Numba JIT compilation to the first route.

## Result

| Route | 2M elapsed (s) | Wall (s) | Same signature | Notes |
| --- | ---: | ---: | --- | --- |
| current grouped-stream Numba | 34.298750 | 48.443038 | reference | conservative current route |
| measured all-true predicate direct-status | 25.003688 | 39.748933 | yes | executes RT count-threshold phase |
| declared all-true predicate direct-status | 20.642251 | 30.469879 | yes | skips RT count-threshold phase; external proof required |

Elapsed speedups:

- Measured all-true versus current: `1.372x`
- Declared all-true versus current: `1.662x`
- Declared all-true versus measured all-true: `1.211x`

## Interpretation

The declared route does what it was designed to do: it removes the
count-threshold predicate-measurement overhead when the caller already has a
valid all-true predicate proof. It preserves the exact RT-DBSCAN component-size
signature on this all-predicate row:

`cluster_sizes = {1: 2097152}, core_count = 2097152, noise_count = 0`

This is not a broad RT-core speedup claim. In the declared route,
`rt_count_threshold_executed` is false and `rt_core_accelerated` is false for
the declared-predicate subpath. The performance win is from avoiding redundant
predicate measurement and reusing the existing generic direct-status
continuation, not from a new RT traversal.

An earlier un-warmed declared 2M probe was killed after several minutes, and a
65K declared smoke charged CUDA/Numba compilation into the measured run. This
report therefore uses a tiny warmup before each 2M route timing. The cold-run
behavior is recorded as a deployment concern, not as accepted route timing.

## Boundary

Goal4173 does not promote this route as the default. The route remains an
explicit external-proof option in the advisor. It does not solve mixed-predicate
RT-DBSCAN rows, does not authorize automatic route selection, automatic partner
selection, automatic factor selection, release, public speedup wording, broad
RT-core wording, whole-app benchmark claims, paper-reproduction claims,
app-specific engine logic, native ABI additions, AMD performance claims, or
true-zero-copy claims.
