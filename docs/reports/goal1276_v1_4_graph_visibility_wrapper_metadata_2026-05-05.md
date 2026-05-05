# Goal1276 v1.4 Graph Visibility Wrapper Metadata

Date: 2026-05-05

Status: implemented locally for the first v1.4 compatibility-wrapper slice.
This is not public RTX wording and does not retire the existing OptiX prepared
summary path.

## Change

The graph `visibility_edges` app section now attaches a `primitive_contract`
payload that records the accepted v1.3 lowering for the first v1.4 slice:

- `app_row`: `graph_analytics.visibility_edges`;
- `primitive`: `ANY_HIT`;
- summary primitive: `COUNT_HITS`, with `REDUCE_INT(COUNT)` recorded as the
  alternate accepted lowering;
- active v1.4 backend scope: Embree plus OptiX;
- mode: `prepared` for the existing OptiX prepared-summary path, `one_shot`
  for row-materializing compatibility paths;
- migration status: `compatibility_wrapper_metadata_only`.

The wrapper does not change traversal behavior. It delegates to the current
graph app paths and preserves the existing JSON shape, counts, phase counters,
and `native_continuation_backend` values.

## Boundary

This metadata covers only candidate graph edges lowered to ray/triangle
any-hit and optional aggregate count. It excludes BFS, triangle counting,
shortest path, graph databases, frontier bookkeeping, and graph reductions.

Vulkan, HIPRT, and Apple RT implementation remain untouched before v2.1. The
metadata may describe inactive backends as inactive, but active v1.4
engineering remains Embree plus OptiX only.

## Verification

Focused local verification:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test \
  tests.goal1275_v1_4_first_wrapper_slice_plan_test \
  tests.goal1274_v1_3_primitive_contract_test \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal1129_graph_phase_split_contract_test
```

Result: 43 tests passed.

## Next Step

The next implementation slice should route the graph visibility summary path
through a generic wrapper function while continuing to delegate to the current
OptiX prepared any-hit count implementation. No pod is required until local
metadata and routing are stable; the next pod run should validate parity and
phase counters before any performance conclusion is recorded.
