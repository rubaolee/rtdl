# Goal 1406: v1.5 Same-Contract Benchmark Evidence Matrix

Date: 2026-05-06

## Decision

The v1.5 same-contract per-app benchmark evidence gate is closed for the
standalone Embree+OptiX language/runtime scope.

This gate does not authorize public release wording, whole-app speedup wording,
or a v1.5 tag. It only records that the included v1.5 apps have existing
same-contract benchmark contracts and evidence references sufficient for the
internal v1.5 release gate. Public wording remains a separate release-doc gate.

## Scope

The benchmark evidence matrix covers all 18 public apps:

- 14 apps are included in standalone v1.5.
- 4 apps are excluded from standalone v1.5: `apple_rt_demo`,
  `hiprt_ray_triangle_hitcount`, `polygon_set_jaccard`, and
  `segment_polygon_anyhit_rows`.

The included v1.5 apps are checked against both active release backends:
Embree and OptiX. The excluded apps are counted as release-gate pass-by-scope,
not as benchmark-supported standalone v1.5 apps.

## Implementation

Added `src/rtdsl/v1_5_benchmark_evidence.py` with:

- `v1_5_benchmark_evidence_matrix()`
- `v1_5_benchmark_evidence_summary()`
- `validate_v1_5_benchmark_evidence_matrix()`
- `validate_v1_5_benchmark_evidence_summary()`

The validator requires each included app to have:

- standalone v1.5 inclusion from the app-classification matrix
- benchmark readiness status `ready_for_rtx_claim_review`
- non-empty same-contract benchmark evidence references
- non-empty benchmark contract text
- passing support/maturity status for the v1.5 release gate

The standalone release gate now treats
`same_contract_per_app_benchmarks` as complete and keeps
`release_docs_and_public_wording` as the only remaining failed gate.

## Release Boundary

This gate is evidence accounting, not new GPU timing. It relies on the existing
per-app benchmark contract/evidence references already recorded in the app
support matrix.

The next release action is to refresh the v1.5 release documentation and public
wording so it accurately reflects:

- v1.5 standalone Embree+OptiX language/runtime scope
- 14 included apps and 4 explicit exclusions
- `COLLECT_K_BOUNDED` exclusion in v1.5
- `COLLECT_K_BOUNDED` promotion deferred to v1.5.1
- no broad speedup wording beyond reviewed evidence boundaries

## Verification

Command:

```sh
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1406_v1_5_benchmark_evidence_matrix_test \
  tests.goal1398_v1_5_standalone_release_gate_test
```

Expected result: all tests pass.
