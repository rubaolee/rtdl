# Goal3542 - v2.9 Repeat/Resident Hook Coverage

Status: internal engineering milestone, not release evidence.

Goal3542 implements the first v2.9 performance-lane action from Goal3538: make the five Goal3536 partial rows measurable as resident hot-query loops instead of one-shot diagnostics dominated by setup, packing, or wrapper process overhead.

Scope note: the hooks are implemented in the current tree. An authoritative v2.3-vs-current timing rerun still needs a same-contract v2.3 evidence checkout that can expose the same measurement-only repeat protocol. The dry-run below uses the current tree for both lanes to validate planner coverage, not to claim final v2.3 evidence.

## What Changed

The following apps now expose explicit repeat controls for the hot prepared query path. Newly wired rows use `--repeat`/`--warmup`; robot already had a compatible `--repeats` control and now participates in the corrected planner.

| App row | Hook added | Primary metric after this goal |
| --- | --- | --- |
| `hausdorff_optix_threshold` | repeat `count_threshold_reached` on an existing prepared fixed-radius threshold handle | median prepared threshold query time |
| `spatial_rayjoin_optix_prepared_full_route` | repeat prepared OptiX count/raw route phases without rebuilding the prepared route | median prepared route query time |
| `barnes_hut_optix_node_coverage` | repeat body-query threshold probes on an existing prepared node-coverage handle | median prepared node-coverage query time |
| `librts_optix_aabb_index` | repeat prepared AABB count operations on resident static/query columns | summed median query time across requested AABB operations (`query_summed_median_sec`, kept compatible as `query_median_sec`) |
| `robot_collision_optix_prepared_device_buffers` | pre-existing repeat hook now participates in the corrected planner | median prepared collision query time |

The same controls are wired into the Goal2626 benchmark registry, so Goal3536 can plan 10-second steady-state rows without inventing wrapper repetition. LibRTS now reports `run_phases.query_median_sec` as its primary metric instead of total wall time, matching the prepared/resident comparison contract.

## Planner Result

Dry planning against the Goal3536 A5000 seed artifact, using the current instrumented tree for both lanes, now marks all five formerly partial rows as `internal_repeat_knob` for both lanes:

```text
hausdorff_optix_threshold                  v2.3 internal_repeat_knob / v2.8 internal_repeat_knob
spatial_rayjoin_optix_prepared_full_route  v2.3 internal_repeat_knob / v2.8 internal_repeat_knob
robot_collision_optix_prepared_device_buffers v2.3 internal_repeat_knob / v2.8 internal_repeat_knob
barnes_hut_optix_node_coverage             v2.3 internal_repeat_knob / v2.8 internal_repeat_knob
librts_optix_aabb_index                    v2.3 internal_repeat_knob / v2.8 internal_repeat_knob
```

This is a measurement-readiness result only. It does not replace the required A5000/pod rerun that must actually execute the planned repeats and produce fresh timing artifacts. It also does not by itself prove that the historical v2.3 evidence checkout has the same repeat controls; that is a required setup check for the next timing goal.

Claude review intake: the initial external review flagged two hygiene items. The RayJoin repeated raw-view path now validates stable row counts across measured repeats, and LibRTS now exposes `query_summed_median_sec` alongside the existing compatible `query_median_sec` field to clarify that the all-operation metric is a sum of per-operation medians.

## Design Boundary

This goal does not add app-specific native engine logic. The native/RT side still exposes generic prepared handles and generic count/raw query operations; the app wrappers only control how many times a prepared query is invoked for measurement.

The repeat protocol intentionally separates:

- one-time setup/build/packing/validation;
- hot prepared query medians;
- measured total query time across repeats;
- warmup iterations.

This avoids claiming that setup disappeared while giving us the right evidence surface for resident workloads.

## Claim Boundary

Goal3542 does not authorize:

- v2.9 release;
- public speedup claims;
- broad RT-core acceleration claims;
- whole-app speedup claims;
- true zero-copy claims;
- paper reproduction claims.

The next required step is a post-review pod/A5000 rerun of the complete v2.3-vs-current steady-state packet using the new repeat hooks. Before running the timing packet, the v2.3 evidence checkout must either contain the same measurement-only repeat hooks or be wrapped by a documented same-contract measurement adapter that changes timing methodology but not v2.3 implementation semantics. The run then needs external review before any performance positioning is accepted.
