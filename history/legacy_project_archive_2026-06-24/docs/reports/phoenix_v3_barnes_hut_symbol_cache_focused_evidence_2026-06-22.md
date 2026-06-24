# Phoenix V3 Barnes-Hut Symbol-Cache Focused Evidence

Date: 2026-06-22
Status: `focused_generic_runtime_fix_validated_not_release`

## Summary

This packet records a focused Phoenix V3 runtime fix and same-pod rerun for the
largest serious V2.14 vs V3 regression found in the all-app paired evidence:
Barnes-Hut OptiX prepared fixed-radius node coverage.

The fix is generic runtime work, not app-specific benchmark tuning:

- `src/rtdsl/optix_runtime.py`
  - `PreparedOptixFixedRadiusCountThreshold2D` now caches the loaded OptiX
    library and optional native symbols on the prepared scene.
  - Hot query methods no longer reload the library and resolve the same symbol
    on every prepared query.
- `tests/goal757_prepared_optix_fixed_radius_count_test.py`
  - Adds a regression test proving one prepared handle resolves each hot symbol
    once while running repeated `count_threshold_reached` queries.

This does not authorize V3 release or broad V3-over-V2 performance wording. It
does repair one concrete generic prepared-query regression.

## Evidence

Remote run:

```text
run_id: phoenix_v3_barnes_hut_symbol_cache_focused_20260622_135158
pod: root@213.173.108.14 -p 11592
remote_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_barnes_hut_symbol_cache_focused_20260622_135158
hardware: NVIDIA RTX 4000 Ada Generation
case_repeat: 3
scope: Barnes-Hut only, goal2626 large and goal2636 stress
```

Local copied artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_symbol_cache_focused_20260622_135158/
```

Remote backup hashes before patch:

```text
optix_runtime.py.before_symbol_cache 463b9689a968140d930f443b74e82256d229ce5df57b1e611ab3352dc23d1fe9
goal757_prepared_optix_fixed_radius_count_test.py.before_symbol_cache 0314e242392d9a58707ddfc3b1782f2f6605cc4d25b4e07aef3d0bd78d238e52
```

Patched current hashes on pod:

```text
src/rtdsl/optix_runtime.py c84c782a54c4191a6abb82f89b2db29f041e2f999c77c79d45283377da608d45
tests/goal757_prepared_optix_fixed_radius_count_test.py a2d170378e5253223ddcd5c4de332987bc016a6050d6a0983d70072413ccc38d
```

Remote validation:

```text
PYTHONPATH=src python3 -m unittest tests.goal757_prepared_optix_fixed_radius_count_test
Ran 16 tests in 2.399s
OK
```

## Focused Results

Metric:
`node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec`

| row | old V3 vs V2.14 | patched V3 vs V2.14 | interpretation |
| --- | ---: | ---: | --- |
| `goal2626_large / optix node coverage` | 0.622x | 0.999x | largest large-row regression recovered to parity |
| `goal2636_stress / optix 32768 bodies` | 0.591x | 1.038x | largest stress-row regression recovered to slight win |
| `goal2636_stress / optix 131072 bodies` | 0.961x | 0.990x | remaining small loss reduced toward parity |
| `goal2626_large / embree node coverage` | 1.016x | 1.032x | CPU path stayed near parity |
| `goal2636_stress / embree 32768 bodies` | 1.002x | 0.990x | CPU path stayed near parity |
| `goal2636_stress / embree 131072 bodies` | 1.007x | 1.006x | CPU path stayed near parity |

Raw focused timings:

| row | V2.14 sec | patched V3 sec |
| --- | ---: | ---: |
| `goal2626_large embree` | 0.133403 | 0.129311 |
| `goal2626_large optix` | 0.042311 | 0.042335 |
| `goal2636_stress embree 32768` | 0.127330 | 0.128669 |
| `goal2636_stress optix 32768` | 0.043710 | 0.042118 |
| `goal2636_stress embree 131072` | 0.553822 | 0.550357 |
| `goal2636_stress optix 131072` | 0.295190 | 0.298128 |

## Release Impact

This focused fix changes the engineering diagnosis:

- The Barnes-Hut app geomean regression in the serious all-app run was heavily
  driven by a generic prepared OptiX Python binding hot-path cost.
- The fix recovers Barnes-Hut prepared OptiX parity on the same RT hardware.
- This is evidence that Phoenix V3 still has meaningful generic runtime work
  available; it is not only documentation or app polish.

Post-hoc projection if these focused Barnes-Hut rows supersede the old serious
Barnes-Hut rows only:

```text
overall geomean: 1.012x -> 1.033x
Barnes-Hut app geomean: 0.844x -> 1.009x
remaining app geomean below 0.95x: librts_spatial_index at 0.937x
remaining row-level losses below 0.95x:
  librts_spatial_index / goal2626_large / embree aabb_index_all_count_only: 0.869x
  spatial_rayjoin / goal2636_stress / optix rayjoin_lsi_authored_tiled_x2048: 0.888x
  rtnn / goal2636_stress / embree rtnn_clustered_262144_ranked_summary: 0.946x
```

It does not change the release decision by itself:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The serious all-app gate remains blocked until a new all-app paired run proves
material broad V2.x superiority after enough generic runtime fixes.

## Decision Audit

Decision: accept the symbol-cache patch as a valid focused generic runtime fix,
but do not treat it as V3 release authorization.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? None for this decision; the
   foolish path would be claiming release success from a Barnes-Hut-only rerun.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: a full all-app rerun could be launched immediately, but that would spend
   pod time before fixing the other known app-level regressions.
4. Can I now try a different path that actually solves the problem? Yes. Continue
   the same pattern: identify the next generic runtime bottleneck from the
   serious paired evidence, make a bounded runtime fix, run focused same-pod
   evidence, then rerun the full all-app gate only when enough blockers move.
