# Goal3521: v2.8 Final Validation Packet

Date: 2026-06-05

Status: internal validation packet; not release authorization.

## Purpose

Goal3521 collects local and RTX pod evidence at one clean commit after the
Goal3517 prepared-execution pattern, Goal3518 benchmark matrix, Goal3519 learner
docs cleanup, and Goal3520 claim-boundary audit.

This packet is intentionally scoped. It validates the current v2.8 internal
closeout state and the targeted matrix gaps. It does not authorize a public
release, package-install claim, broad speedup claim, broad RT-core claim, true
zero-copy claim, full paper reproduction claim, hidden partner selection, or
app-specific native-engine behavior.

## Commit

Validated commit:

```text
9ad59f1e7abbe0b2a97e785b28f7358aaa14d6c8
```

Pod workspace:

```text
/root/rtdl_goal3521
```

Pod GPU:

```text
NVIDIA RTX A5000, 580.126.09
```

The pod checkout used a clean clone at the validated commit. It reused the
already-built OptiX library from `/root/rtdl/build/librtdl_optix.so` because the
post-Goal3511 closeout changes were docs, tests, examples, and Python
prepared-execution/reporting changes, not native OptiX source changes.

## Local Validation

Focused local gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3070_v2_7_primitive_discovery_core_test \
  tests.goal3094_v2_7_primitive_discovery_orchestration_closeout_test \
  tests.goal3108_v2_8_typed_result_stream_contract_test \
  tests.goal3149_v2_8_front_door_completion_packet_test \
  tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test \
  tests.goal3156_rt_dbscan_v2_8_front_door_route_test \
  tests.goal3160_hausdorff_generic_max_nearest_front_door_alias_test \
  tests.goal3161_v2_8_runtime_gap_hausdorff_generic_alias_refresh_test \
  tests.goal3162_raydb_grouped_reduction_typed_stream_front_door_test \
  tests.goal3163_v2_8_runtime_gap_raydb_typed_stream_refresh_test \
  tests.goal3165_rtnn_ranked_summary_typed_stream_front_door_test \
  tests.goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_test \
  tests.goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test \
  tests.goal3170_v2_8_runtime_gap_barnes_hut_vector_stream_refresh_test \
  tests.goal3171_direct_compact_mask_typed_stream_front_door_test \
  tests.goal3172_v2_8_runtime_gap_compact_mask_refresh_test \
  tests.goal3173_direct_bounded_collect_typed_stream_front_door_test \
  tests.goal3174_v2_8_runtime_gap_bounded_collect_refresh_test \
  tests.goal3177_v2_8_runtime_gap_raydb_typed_producer_refresh_test \
  tests.goal3179_v2_8_runtime_gap_rt_dbscan_typed_metadata_refresh_test \
  tests.goal3183_shape_pair_relation_active_count_test \
  tests.goal3447_shape_pair_active_relation_device_columns_test \
  tests.goal3511_overlay_area_steady_state_relation_stream_test \
  tests.goal3517_prepared_execution_user_pattern_test \
  tests.goal3518_v2_8_benchmark_matrix_test \
  tests.goal3519_v2_8_learner_docs_cleanup_test \
  tests.goal3520_v2_8_claim_boundary_stale_audit_test

Ran 112 tests in 0.314s
OK (skipped=5)
```

An initial attempt included `tests.goal3117_v2_8_explicit_partner_consumer_front_door_test`,
but that module does not exist. The corrected focused gate above is the
reproducible validation command.

## Pod Validation Commands

Robot collision:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3521/build/librtdl_optix.so \
OPTIX_PREFIX=/root/vendor/optix-sdk \
.venv_goal3521/bin/python scripts/goal2485_robot_collision_matrix_pod_runner.py \
  --skip-build-optix \
  --output-dir docs/reports/goal3521_pod_artifacts/robot_collision \
  --pose-count 256 --obstacle-count 32 --link-count 3 --repeats 7 --warmup 2
```

Contact manifold:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3521/build/librtdl_optix.so \
OPTIX_PREFIX=/root/vendor/optix-sdk \
.venv_goal3521/bin/python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py \
  --mode aabb_broadphase_collect_k \
  --dataset grid --grid-count 4096 --witness-capacity 4096 \
  --backend optix --discovery-backend optix --discovery-warmup 2 --discovery-repeat 5
```

RT-DBSCAN:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3521/build/librtdl_optix.so \
OPTIX_PREFIX=/root/vendor/optix-sdk \
.venv_goal3521/bin/python scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py \
  --point-count 32768 --point-count 65536 --point-count 131072 \
  --repeat-count 3 \
  --raw-output-dir docs/reports/goal3521_pod_artifacts/rt_dbscan_raw \
  --output docs/reports/goal3521_pod_artifacts/rt_dbscan_grouped_stream.json
```

Spatial RayJoin overlay steady-state:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3521/build/librtdl_optix.so \
OPTIX_PREFIX=/root/vendor/optix-sdk \
.venv_goal3521/bin/python scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py \
  --left-cdb /root/rtdl/data/rayjoin_public_cdb/br_county.cdb \
  --right-cdb /root/rtdl/data/rayjoin_public_cdb/br_county_start256_count1024.cdb \
  --payload-cache-dir docs/reports/goal3521_pod_artifacts/overlay_cache \
  --payload-cache-mode read --payload-cache-format binary --payload-cache-evidence \
  --bounds-positive-filter --device-active-shape-ordinals --device-tile-task-planner \
  --component-bounds-filter --resident-cupy-inputs --active-shapes-only \
  --payload-workers 8 --relation-column-warmup-repeats 3 \
  --relation-stream-steady-state-evidence --executor-repeats 3 \
  --device-planner-repeats 3 --progress-every 500 \
  --output docs/reports/goal3521_pod_artifacts/overlay_steady_state_read.json
```

The overlay binary cache was generated in the same pod checkout before the
read-mode run. The cache files themselves are not committed; the JSON evidence
records the cache-read timing and correctness.

## Pod Results

| Row | Result |
| --- | --- |
| Robot collision | CPU reference tail median `3.4537386205s`; OptiX prepared tail median `0.0353194466s`; prepared scene reused; public claims remain false. The Embree row errored in the clean pod checkout because no Embree library was configured there; RTX evidence is still valid for this packet. |
| Contact manifold | `grid_4096` with OptiX AABB discovery matches CPU reference; scene build `0.573764368s`, RT traversal median `0.027931150s`, exact app refinement `0.009864520s`, materialization `0.010725705s`; native collision/contact logic remains disallowed. |
| RT-DBSCAN | Status `pass`; signatures match; grouped stream is RT-core accelerated and avoids neighbor-row/full-adjacency materialization. Speedup versus prepared CuPy grid: `4.080x` at 32K, `4.691x` at 65K, `4.897x` at 131K. |
| Spatial RayJoin overlay | Schema `rtdl.goal3511.overlay_area_steady_state_relation_stream.v1`; relation rows `4543`; positive rows `1086/1086`; total area absolute error `9.227797193034348e-09`; active relation device columns `0.003779787s` after warmup; cache load `0.175631035s`; device planner `0.236281021s`; tile executor `0.057250103s`. |

## Artifacts

- `docs/reports/goal3521_pod_artifacts/robot_collision/summary.json`
- `docs/reports/goal3521_pod_artifacts/contact_manifold_grid4096_optix.json`
- `docs/reports/goal3521_pod_artifacts/rt_dbscan_grouped_stream.json`
- `docs/reports/goal3521_pod_artifacts/rt_dbscan_raw/`
- `docs/reports/goal3521_pod_artifacts/overlay_steady_state_refresh.json`
- `docs/reports/goal3521_pod_artifacts/overlay_steady_state_read.json`

## Validation Guard

`tests/goal3521_v2_8_final_validation_packet_test.py` checks the report and
artifact packet. It enforces:

- all promoted pod artifacts exist;
- artifact commits match `9ad59f1e7abbe0b2a97e785b28f7358aaa14d6c8`;
- robot collision has a valid OptiX prepared row and blocked claim boundary;
- contact manifold exposes the phase split and keeps engine semantics generic;
- RT-DBSCAN passes correctness/signature checks and preserves claim boundaries;
- overlay preserves exact-area correctness and a warmed resident relation-stream
  timing below `0.01s`.

## Verdict

`accept-with-boundary`

Goal3521 provides a focused final validation packet for the v2.8 internal
closeout sequence. It closes the local and targeted RTX evidence needed by the
current benchmark matrix. It remains an internal packet only and does not press
the release button.

The next step is Goal3522: write the final v2.8 internal closeout packet and
seek fresh Claude + Gemini review before the 3-AI closeout consensus.
