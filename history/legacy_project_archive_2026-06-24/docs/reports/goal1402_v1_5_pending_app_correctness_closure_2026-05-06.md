# Goal1402: v1.5 Pending App Correctness Closure

Date: 2026-05-06

## Decision

The four apps that were pending in the v1.5 standalone correctness matrix now
have local app-contract correctness tests:

- `road_hazard_screening`
- `segment_polygon_hitcount`
- `hausdorff_distance`
- `barnes_hut_force_app`

This closes the `same_contract_per_app_correctness` release gate for local
contract evidence. It does not close benchmark evidence, public wording, or
`COLLECT_K_BOUNDED` resolution.

## Evidence Added

`tests.goal1402_v1_5_pending_app_correctness_closure_test` verifies:

- segment/polygon hit-count CPU, Embree, and OptiX-facing rows use the same
  compact hit-count contract
- road-hazard CPU, Embree, and OptiX-facing summary outputs agree on priority
  segment count and ids
- Hausdorff Embree directed summary and OptiX threshold summary agree with the
  deterministic oracle decision
- Barnes-Hut Embree candidate summary and OptiX node-coverage summary agree
  with the deterministic oracle decision

Local OptiX native library is not built in this environment, so the OptiX-facing
tests use app-level mocks for the prepared summary calls. Real NVIDIA runtime
timing and benchmark evidence remains assigned to the benchmark gate and should
be collected from a pod when needed.

## Release-Gate Impact

Passed gates now include:

- `primitive_packet_prerequisite`
- `roadmap_consensus`
- `app_migration_classification`
- `same_contract_per_app_correctness`

Failed gates remain:

- `collect_k_bounded_resolution`
- `same_contract_per_app_benchmarks`
- `test_backed_support_maturity_matrix`
- `release_docs_and_public_wording`

## Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1402_v1_5_pending_app_correctness_closure_test \
  tests.goal1401_v1_5_standalone_correctness_matrix_test \
  tests.goal1400_v1_5_standalone_app_classification_test \
  tests.goal1398_v1_5_standalone_release_gate_test
```
