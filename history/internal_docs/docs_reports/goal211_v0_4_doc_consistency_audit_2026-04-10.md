# Goal 211 Report: v0.4 Doc Consistency Audit

## Summary

Goal 211 removes stale language from the live `v0.4` language/feature docs.
Before this slice, some pages still described `fixed_radius_neighbors` and
`knn_rows` as merely planned or not yet lowered/runtime-backed even though the
current preview line already includes DSL, truth-path, CPU/oracle, Embree, and
bounded external-baseline support.

## Files Updated

- `/Users/rl2025/rtdl_python_only/docs/rtdl/llm_authoring_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/features/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/knn_rows/README.md`

## Decisions

- `fixed_radius_neighbors` and `knn_rows` are now both described as active
  `v0.4` preview surfaces in the live docs
- live docs now say explicitly that both workloads have:
  - DSL/lowering
  - Python truth path
  - native CPU/oracle
  - Embree
  - bounded SciPy / PostGIS baseline support
- OptiX / Vulkan remain honestly outside the current `v0.4` preview acceptance
  package

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality tests.rtdsl_language_test tests.goal208_nearest_neighbor_examples_test tests.goal209_nearest_neighbor_scaling_note_test tests.goal207_knn_rows_external_baselines_test tests.goal206_knn_rows_embree_test tests.goal205_knn_rows_cpu_oracle_test tests.goal200_fixed_radius_neighbors_embree_test`
  - `Ran 136 tests`
  - `OK`
- `python3 -m compileall /Users/rl2025/rtdl_python_only/docs/rtdl /Users/rl2025/rtdl_python_only/docs/features /Users/rl2025/rtdl_python_only/docs/workloads_and_research_foundations.md`
  - `OK`

## Honest Boundary

- this slice updates live docs only
- historical reports remain preserved as they were written
- the final all-of-`v0.4` audit is still a separate step
