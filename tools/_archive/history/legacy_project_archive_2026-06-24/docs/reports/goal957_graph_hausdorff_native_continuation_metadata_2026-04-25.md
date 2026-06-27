# Goal957: Graph and Hausdorff Native-Continuation Metadata

Date: 2026-04-25

## Verdict

Local implementation complete; peer review pending at the time this report was written.

Goal957 closes the remaining public app metadata gap where apps had
`rt_core_accelerated` fields but no uniform `native_continuation_active` /
`native_continuation_backend` fields.

## Scope

Touched apps:

- `examples/rtdl_graph_analytics_app.py`
- `examples/rtdl_hausdorff_distance_app.py`

Touched tests/docs:

- `tests/goal957_graph_hausdorff_native_continuation_metadata_test.py`
- `examples/README.md`
- `docs/application_catalog.md`

## Implementation

### Graph Analytics

The unified graph app now aggregates native-continuation metadata from its
sections:

- BFS summary sections already report `native_continuation_backend: oracle_cpp`.
- Triangle-count summary sections already report
  `native_continuation_backend: oracle_cpp`.
- `visibility_edges` with `--backend optix` now reports
  `native_continuation_backend: optix_visibility_pair_rows`.

The top-level `graph_analytics` payload now reports:

- `native_continuation_active: true` if any selected section reports native continuation
- `native_continuation_backend` as a `+`-joined list of selected native section backends

This preserves existing RT-core honesty: top-level `rt_core_accelerated` remains
true only for `--backend optix --scenario visibility_edges`.

### Hausdorff Distance

The Hausdorff app now reports native-continuation metadata for the two compact
native paths:

- `--backend embree --embree-result-mode directed_summary` reports
  `native_continuation_backend: embree_directed_hausdorff`.
- `--backend optix --optix-summary-mode directed_threshold_prepared` reports
  `native_continuation_backend: optix_threshold_count`.

Default KNN-row mode reports:

- `native_continuation_active: false`
- `native_continuation_backend: none`

This preserves the existing boundary: OptiX threshold mode is an RT-core
Hausdorff <= radius decision path, not an exact Hausdorff KNN speedup claim.

## Inventory Check

After this change, no public example file contains `rt_core_accelerated` without
also containing `native_continuation_active`.

## Verification

Focused gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal949_graph_native_summary_continuation_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal817_cuda_through_optix_claim_gate_test

Ran 27 tests in 0.574s
OK
```

Syntax gate:

```text
python3 -m py_compile \
  examples/rtdl_graph_analytics_app.py \
  examples/rtdl_hausdorff_distance_app.py \
  tests/goal957_graph_hausdorff_native_continuation_metadata_test.py
```

Whitespace gate:

```text
git diff --check -- \
  examples/rtdl_graph_analytics_app.py \
  examples/rtdl_hausdorff_distance_app.py \
  tests/goal957_graph_hausdorff_native_continuation_metadata_test.py \
  examples/README.md \
  docs/application_catalog.md
```

Syntax and whitespace gates passed with no output.

## Honesty Boundary

Allowed wording:

- Graph top-level metadata now propagates native-continuation status from
  selected graph sub-sections.
- Graph `visibility_edges` maps candidate edges to ray/triangle visibility
  traversal and reports `optix_visibility_pair_rows` on OptiX.
- Hausdorff Embree directed-summary mode reports native Embree directed-summary
  continuation.
- Hausdorff OptiX threshold mode reports native threshold-count continuation
  for the decision form only.

Disallowed wording:

- Full graph database acceleration.
- Shortest path, distributed graph analytics, or broad graph speedup claims.
- Exact Hausdorff KNN speedup on OptiX.
- Whole-app performance claims without same-semantics artifact review.
