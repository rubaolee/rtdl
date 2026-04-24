# Goal882 Barnes-Hut Node Coverage OptiX Sub-Path

Date: 2026-04-24

## Result

Goal882 adds an explicit OptiX traversal-backed decision mode to the Barnes-Hut
force approximation app:

```bash
PYTHONPATH=src:. python3 examples/rtdl_barnes_hut_force_app.py \
  --backend optix \
  --optix-summary-mode node_coverage_prepared \
  --node-radius 10.0 \
  --require-rt-core
```

This mode answers the bounded node-coverage query:

```text
For every body, is there at least one quadtree node candidate within radius?
```

It uses `prepare_optix_fixed_radius_count_threshold_2d(...)` over quadtree node
centers and runs body points with `threshold=1`. The app computes an oracle
node-coverage decision in Python for correctness validation.

## Boundary

This is not Barnes-Hut opening-rule evaluation, not candidate-row generation,
not force-vector reduction, and not a fully native N-body solver. The existing
full, candidate-summary, and force-summary modes remain separate from the
prepared OptiX node-coverage decision. Goal882 only promotes the node-coverage
decision sub-problem to a prepared OptiX traversal path.

No public speedup claim is authorized until a phase profiler, same-semantics
baselines, a real RTX artifact, and independent review exist.

## Manifest Update

The Goal759 RTX cloud manifest was refreshed so recently promoted prepared
decision sub-paths are deferred entries rather than stale exclusions:

- Hausdorff threshold decision
- ANN candidate-coverage decision
- Facility service-coverage decision
- Barnes-Hut node-coverage decision

They are still not active cloud jobs; each requires a future phase profiler and
same-semantics RTX artifact before promotion.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal882_barnes_hut_node_coverage_optix_subpath_test \
  tests.goal504_barnes_hut_force_app_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal817_cuda_through_optix_claim_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `52 tests OK`.

Other checks:

- `py_compile`: OK for the app, new test, Goal759 manifest script, and Goal824
  readiness gate.
- `git diff --check`: OK.
- public command audit: `valid=True`.

