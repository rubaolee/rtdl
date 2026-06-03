# Goal3155 Fixed-Radius Graph Component Front Door

Date: 2026-06-03

Verdict: `accept-with-boundary`

## Purpose

Goal3154 refreshed the current-head A40 evidence for the RT-DBSCAN grouped-stream path and showed that the fast path is already generic underneath: OptiX emits a fixed-radius hit stream, the native path applies grouped union directly during traversal, and CuPy receives component-label columns without materializing neighbor rows or a full directed adjacency table.

Goal3155 turns that measured runtime shape into a v2.8-discoverable front door:

```python
rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(...)
rt.fixed_radius_graph_component_labels_3d_v2_8(...)
rt.plan_v2_8_fixed_radius_graph_component_continuation(...)
rt.describe_v2_8_fixed_radius_graph_component_front_door()
```

The goal is not a new speed claim. It is an API and contract cleanup so users see a fixed-radius graph component continuation instead of a benchmark-app mode label.

## What Changed

| File | Operation |
| --- | --- |
| `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py` | Added a thin v2.8 front door over the existing OptiX+CuPy grouped-stream continuation. |
| `src/rtdsl/__init__.py` | Exported the new front-door plan, prepare, run, describe, constants, and prepared-handle type. |
| `src/rtdsl/primitive_hierarchy.py` | Added discovery metadata to `continuation.fixed_radius_graph` while keeping it `internal_substrate`. |
| `docs/rtdl_primitive_catalog.md` | Regenerated from the hierarchy so the fixed-radius graph component primitive is discoverable. |
| `tests/goal3155_fixed_radius_graph_component_front_door_test.py` | Added regression coverage for explicit planning, no fallback, metadata, lower-adapter bridging, discovery, and claim boundaries. |

## Contract

Goal3155 exposes an explicit user-selected OptiX+CuPy grouped-stream contract.

The new front door is explicit and narrow:

- backend: `optix`
- partner: `cupy`
- strategy: `grouped_stream`
- input: host point rows for a prepared fixed-radius 3-D graph
- output columns: `point_ids`, `component_labels`, `is_core`, `neighbor_counts`
- public threshold name: `component_threshold`
- lower compatibility bridge: existing grouped-stream adapter path

Unsupported backend, partner, or strategy choices return `unsupported_explicit_user_choice` in the planner and do not select a fallback. The prepare path raises on unsupported choices.

## Boundary

This is still not a v2.8 release authorization. It preserves the standard red lines:

- no hidden dispatcher
- no automatic partner selection
- no app-specific native engine logic
- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

The lower compatibility adapter still has historical parameter vocabulary internally. Goal3155 hides that from the v2.8 public front door and metadata by exposing `component_threshold`; it does not rewrite the older compatibility API.

## Why This Matters

RTDL v2.8 is trying to make useful high-performance RT paths easier to find and compose. Before this goal, a user could reach the measured RT-DBSCAN path, but mostly through benchmark-app labels or lower adapter names. After this goal:

- primitive discovery can find `continuation.fixed_radius_graph` from phrases like "fixed radius graph component labels";
- users can plan the path without triggering execution or hidden partner choice;
- benchmark apps can migrate toward the generic API while keeping their app policy outside the engine;
- future v2.8 work can attach typed-result-stream and component-continuation metadata to one front-door contract.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3155_fixed_radius_graph_component_front_door_test tests.goal3154_rt_dbscan_current_head_a40_grouped_stream_refresh_test tests.goal3153_compact_mask_block_size_guard_test tests.goal3099_v2_7_semantic_search_preview_test tests.goal3094_v2_7_primitive_discovery_orchestration_closeout_test tests.goal3090_v2_7_discovery_metadata_backfill_test tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test
```

Result: 59 tests passed.

Pod validation should be a focused clean-checkout suite plus an optional tiny OptiX+CuPy execution, because Goal3155 does not change native code and Goal3154 already refreshed large-scale A40 performance evidence for the lower path.

## Next

The next useful step is to migrate the RT-DBSCAN benchmark app's preferred mode label onto this v2.8 front door while preserving its app-owned policy and validation signatures. That should be a separate goal because it changes benchmark-app routing rather than the reusable primitive contract.
