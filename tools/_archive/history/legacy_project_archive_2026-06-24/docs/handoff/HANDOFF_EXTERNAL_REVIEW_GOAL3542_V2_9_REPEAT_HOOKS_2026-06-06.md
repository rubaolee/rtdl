# Handoff - Goal3542 v2.9 Repeat/Resident Hook Coverage Review

Please perform an independent review of Goal3542, the first v2.9 performance-lane engineering step.

## Context

Goal3536 closed v2.8 with only 6/11 target-compliant 10-second rows. The five partial rows were partial because their benchmark commands could not cleanly repeat only resident hot-query phases:

- `hausdorff_optix_threshold`
- `spatial_rayjoin_optix_prepared_full_route`
- `robot_collision_optix_prepared_device_buffers`
- `barnes_hut_optix_node_coverage`
- `librts_optix_aabb_index`

Goal3542 adds or wires repeat/resident hooks so Goal3536 can plan all five as `internal_repeat_knob` rows when the current instrumented tree is used for both lanes. This is measurement readiness only; it is not new A5000 timing evidence and does not authorize release or public speedup claims.

Important boundary: an authoritative v2.3-vs-current timing rerun still needs a same-contract v2.3 evidence checkout with these measurement-only repeat controls backported or otherwise exposed through a documented measurement adapter. Do not treat the current-tree dry-run as final historical v2.3 evidence.

## Files To Inspect

- `docs/reports/goal3542_v2_9_repeat_resident_hook_coverage_2026-06-06.md`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `scripts/goal2626_benchmark_embree_optix_baseline.py`
- `scripts/goal3536_v2_8_vs_v2_3_10s_steady_state.py`
- `tests/goal3536_v2_8_vs_v2_3_10s_steady_state_test.py`
- `tests/goal3542_v2_9_repeat_resident_hook_coverage_test.py`

## Checks To Run

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3536_v2_8_vs_v2_3_10s_steady_state_test tests.goal3542_v2_9_repeat_resident_hook_coverage_test
```

Optional compile check:

```powershell
py -3 -m py_compile examples\v2_0\research_benchmarks\hausdorff_xhd\rtdl_hausdorff_distance_app.py examples\v2_0\apps\simulation\rtdl_barnes_hut_force_app.py examples\v2_0\research_benchmarks\barnes_hut\rtdl_barnes_hut_benchmark_app.py examples\v2_0\research_benchmarks\librts_spatial_index\rtdl_librts_spatial_index_benchmark_app.py examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py scripts\goal2626_benchmark_embree_optix_baseline.py scripts\goal3536_v2_8_vs_v2_3_10s_steady_state.py
```

## Review Questions

1. Do the new repeat hooks measure hot prepared query phases rather than rebuilding scenes, subprocesses, or app setup?
2. Are repeated raw-view paths safe, meaning views are closed each iteration and counts/results are stable?
3. Does the Goal3536 planner correctly retain the wall-time guard while removing only the artificial high-setup shortcut?
4. Does the Goal2626 registry use the right primary metric paths for resident query measurements, especially LibRTS?
5. Does the report avoid release/speedup/RT-core/zero-copy overclaiming?
6. What must be fixed before Goal3543 pod timing evidence?
7. Does the report clearly distinguish current-tree repeat-hook coverage from authoritative historical v2.3 baseline evidence?

## Expected Outputs

Claude output path:

`docs/reviews/goal3543_claude_review_goal3542_v2_9_repeat_hooks_2026-06-06.md`

Gemini output path:

`docs/reviews/goal3544_gemini_review_goal3542_v2_9_repeat_hooks_2026-06-06.md`

Use one of the project verdict values: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
