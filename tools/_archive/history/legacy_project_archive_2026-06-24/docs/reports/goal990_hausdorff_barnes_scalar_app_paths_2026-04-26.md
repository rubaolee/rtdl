# Goal990 Hausdorff/Barnes-Hut Scalar Prepared App Paths

Date: 2026-04-26

## Scope

Goal990 continues the no-cloud pre-RTX cleanup for public apps that already had prepared OptiX decision sub-paths in the phase profiler, but still exposed row materialization in the app path.

Apps covered:

- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_barnes_hut_force_app.py`

## Changes

### Hausdorff decision sub-path

The OptiX `directed_threshold_prepared` app path now calls:

```python
prepared.count_threshold_reached(source, radius=radius, threshold=1)
```

instead of:

```python
prepared.run(source, radius=radius, threshold=1)
```

The app returns a scalar decision summary:

- `covered_source_count`
- `within_threshold`
- `summary_mode: scalar_threshold_count`
- `row_count: None`

This preserves the intended RTDL role: OptiX answers the bounded Hausdorff decision question "does every source point have at least one target within radius?"

### Barnes-Hut node-coverage sub-path

The OptiX `node_coverage_prepared` app path now calls:

```python
prepared.count_threshold_reached(_body_points(bodies), radius=radius, threshold=1)
```

instead of:

```python
prepared.run(_body_points(bodies), radius=radius, threshold=1)
```

The app returns a scalar decision summary:

- `covered_body_count`
- `all_bodies_have_node_candidate`
- `summary_mode: scalar_threshold_count`
- `row_count: None`

This preserves the intended RTDL role: OptiX answers the bounded node-coverage decision question "does every body have at least one candidate quadtree node within radius?"

## Honesty Boundaries

The scalar paths intentionally do not emit full witness rows.

- Hausdorff scalar mode does not identify exact violating source IDs when the scalar decision fails. It returns `violating_source_ids: None` and `identity_parity_available: False`.
- Barnes-Hut scalar mode does not identify exact uncovered body IDs when the scalar decision fails. It returns `uncovered_body_ids: None` and `identity_parity_available: False`.
- Exact Hausdorff distance, KNN ranking, Barnes-Hut opening-rule evaluation, force-vector reduction, and full N-body solving remain outside the RT-core claim.
- This goal does not authorize any public speedup claim. Existing RTX claim gates still control public wording.

## Tests

Focused local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal882_barnes_hut_node_coverage_optix_subpath_test \
  tests.goal887_prepared_decision_phase_profiler_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal817_cuda_through_optix_claim_gate_test
```

Result after adding explicit scalar failure-boundary tests recommended by Gemini:

```text
Ran 23 tests in 0.954s
OK
```

Compile check:

```text
python3 -m py_compile \
  examples/rtdl_hausdorff_distance_app.py \
  examples/rtdl_barnes_hut_force_app.py \
  tests/goal879_hausdorff_threshold_rt_core_subpath_test.py \
  tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py \
  tests/goal957_graph_hausdorff_native_continuation_metadata_test.py
```

Result: OK.

## Files Changed

- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_barnes_hut_force_app.py`
- `tests/goal879_hausdorff_threshold_rt_core_subpath_test.py`
- `tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py`
- `tests/goal957_graph_hausdorff_native_continuation_metadata_test.py`
- `docs/app_engine_support_matrix.md`

## Review Follow-Up

Gemini accepted the first review pass and recommended explicit failure-path tests for the scalar witness boundary. Those tests were added before closure:

- Hausdorff scalar failure now verifies `violating_source_ids: None` and `identity_parity_available: False`.
- Barnes-Hut scalar failure now verifies `uncovered_body_ids: None` and `identity_parity_available: False`.

## Status

Codex verdict: ACCEPT after Gemini recommendation follow-up. Second-AI review and consensus closure are required before calling the goal closed.
