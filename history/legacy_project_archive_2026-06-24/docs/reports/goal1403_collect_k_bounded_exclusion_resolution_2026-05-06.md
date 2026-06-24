# Goal1403: COLLECT_K_BOUNDED v1.5 Exclusion Resolution

Date: 2026-05-06

## Decision

`COLLECT_K_BOUNDED` is resolved for standalone v1.5 by explicit exclusion, not
by stable promotion.

The primitive remains experimental and public wording remains blocked. The
standalone v1.5 surface excludes row-returning collection-dependent apps:

- `polygon_set_jaccard`
- `segment_polygon_anyhit_rows`

This closes the `collect_k_bounded_resolution` release gate because the v1.5
scope is no longer ambiguous. It does not authorize row-returning app claims or
future bounded-collection promotion.

## Preserved Boundaries

- `COLLECT_K_BOUNDED` status remains `experimental_diagnostic_only`.
- Stable promotion remains unauthorized.
- Public speedup wording remains unauthorized.
- Native Embree/OptiX fail-closed collection gates remain future promotion
  gates.
- Jaccard and segment/polygon pair-row apps remain outside standalone v1.5.

## Release-Gate Impact

Passed gates now include:

- `primitive_packet_prerequisite`
- `roadmap_consensus`
- `collect_k_bounded_resolution`
- `app_migration_classification`
- `same_contract_per_app_correctness`

Failed gates remain:

- `same_contract_per_app_benchmarks`
- `test_backed_support_maturity_matrix`
- `release_docs_and_public_wording`

## Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1399_collect_k_bounded_resolution_test \
  tests.goal1398_v1_5_standalone_release_gate_test \
  tests.goal1400_v1_5_standalone_app_classification_test \
  tests.goal1401_v1_5_standalone_correctness_matrix_test
```
