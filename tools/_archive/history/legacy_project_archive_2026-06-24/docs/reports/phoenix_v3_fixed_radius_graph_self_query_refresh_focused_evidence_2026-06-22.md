# Phoenix V3 Fixed-Radius Graph Self-Query Refresh Focused Evidence

Date: 2026-06-22
Status: `focused_generic_runtime_contract_fix_validated_no_material_speedup`

## Summary

This packet records the same-pod A/B for the Phoenix V3 generic fixed-radius
graph self-query refresh.

The change is runtime-contract work, not app-specific tuning:

- `src/rtdsl/partner_adapters.py`
  - `PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run`
  - `_run_cupy_grouped_stream_same_stream_evidence`
  - `PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D._refresh_core_flags`

These paths now refresh core flags with
`fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns`
instead of repacking the prepared scene's same point rows as host query input.

- `src/rtdsl/optix_runtime.py`
  - Fixes `write_device_count_threshold_self_columns` so the no-stream
    self-query API does not reference an undefined `cuda_stream_ptr`.
- `tests/goal4486_rt_dbscan_self_count_threshold_test.py`
  - Adds a regression test proving the no-stream self-query columns API does
    not reference the on-stream variable.
- `tests/v3_phoenix_fixed_radius_graph_self_query_refresh_test.py`
  - Guards the grouped-stream refresh source paths.

This should stay as V3 runtime-contract cleanup. It does not authorize release
or broad V3-over-V2 performance wording.

## Evidence Boundary

Remote run:

```text
run_id: phoenix_v3_self_query_refresh_ab_20260622_153305
pod: root@213.173.108.14 -p 11592
remote_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_self_query_refresh_ab_20260622_153305
local_artifact_dir: docs/rebuild/v3/evidence/phoenix_v3_self_query_refresh_ab_20260622_153305/
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

Partner runtime environment:

```text
venv: /root/rtdl_v3_rebuild_20260620/venv_partner_py312
cupy: 14.1.1
numba: 0.65.1
numpy: 2.1.2
```

Important environment finding:

```text
system python before venv:
  cupy: missing
  numba: missing

baseline_without_partner_venv:
  all grouped-stream partner rows failed before code execution with missing CuPy/Numba
```

This explains why some earlier RTDBSCAN OptiX grouped-stream evidence rows were
`failed` on this pod. Partner-enabled evidence must use the recorded venv or an
equivalent environment.

## Validation

Local validation:

```text
py_compile optix_runtime.py and partner_adapters.py: OK
self-query / fixed-radius focused tests: 11 OK
release/readiness/wording gates: 11 OK
```

Remote validation after sync:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/venv_partner_py312/bin/python -m unittest \
  tests.goal4486_rt_dbscan_self_count_threshold_test \
  tests.v3_phoenix_fixed_radius_graph_self_query_refresh_test \
  tests.v3_phoenix_prepared_fixed_radius_symbol_cache_test

Ran 11 tests
OK
```

Patched source hashes on pod:

```text
src/rtdsl/partner_adapters.py dd7717a14b827db1aaf2aede6cb03d877429a0ec55d0d85592d7155e909ea132
src/rtdsl/optix_runtime.py 8ba0321b54081c26a64ddc9b2bbf9df8d4999a7b151b72e8be234cfb1c2cbc64
src/rtdsl/embree_runtime.py 7b166ca9494f3a2f85803c8dc367eefcec5a04a595b90c8d786deb8007fb8b09
tests/goal4486_rt_dbscan_self_count_threshold_test.py f654e713735a54a6d412f532b03b672c725ec0e98e1765b4441ac480caf1b913
tests/v3_phoenix_fixed_radius_graph_self_query_refresh_test.py e3ea3c66a09fd8d6eb522ed74661516396dbf05ac9068fabbe050d1fbbdc107c
```

## A/B Rows

Command shape:

```text
app: examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
dataset: clustered3d
partner: cupy
repeat: 4
warmup: 1
validation: disabled for performance row
```

Comparison:

| case | before sec | after sec | after vs before | signature same | count adapter before | count adapter after |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `blocked_cupy_16384` | 0.038496 | 0.038194 | 1.008x | true | `fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns` | `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns` |
| `blocked_cupy_65536` | 0.460801 | 0.461920 | 0.998x | true | `fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns` | `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns` |
| `unblocked_cupy_16384` | 0.018836 | 0.019053 | 0.989x | true | `fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns` | `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns` |

Aggregate:

```text
CuPy row count: 3
signature mismatches: 0
geomean after-vs-before speedup: 0.998x
material performance gain: no
```

Contract metadata change:

| field | before | after |
| --- | --- | --- |
| `input_contract` | `host_query_points_prepared_native_search_scene` | `prepared_native_self_query_device_search_scene` |
| `transfer_mode` | `host_query_points_to_device_threshold_columns` | `prepared_device_search_points_self_count_threshold_columns` |
| `host_query_point_upload_avoided` | absent / null | true |
| `host_query_point_repack_avoided` | absent / null | true |

Native count-threshold timing moved slightly in the right direction, but the
full grouped-stream row did not materially improve:

| case | native count sec before | native count sec after |
| --- | ---: | ---: |
| `blocked_cupy_16384` | 0.001394 | 0.001279 |
| `blocked_cupy_65536` | 0.004986 | 0.004121 |
| `unblocked_cupy_16384` | 0.001376 | 0.001265 |

## Negative Controls And Failures

Numba grouped-stream row remains blocked by the pod CUDA toolkit/PTX mismatch:

```text
numba.cuda.cudadrv.driver.CudaAPIError: [222] CUDA_ERROR_UNSUPPORTED_PTX_VERSION
ptxas application ptx input, line 9; fatal: Unsupported .version 8.7; current version is '8.4'
```

This is not a V3 speed result. It is an environment blocker for Numba partner
evidence on this pod unless the toolkit/Numba stack is aligned.

The first post-sync attempt failed for all rows because
`write_device_count_threshold_self_columns` referenced an undefined
`cuda_stream_ptr`. That failure is preserved in:

```text
docs/rebuild/v3/evidence/phoenix_v3_self_query_refresh_ab_20260622_153305/after_self_query_patch_partner_venv/
```

The final post-sync evidence after the stream fix is:

```text
docs/rebuild/v3/evidence/phoenix_v3_self_query_refresh_ab_20260622_153305/after_self_query_patch_stream_fix_partner_venv/
```

## Interpretation

This is a real V3 runtime-contract cleanup:

- It removes an avoidable host query-point repack/upload from grouped-stream
  core-flag refresh.
- It keeps signatures unchanged.
- It makes metadata correctly report the prepared self-query device-search
  path.
- It adds a regression test for the no-stream self-query API bug.

It is not a performance win:

- The three successful CuPy rows have 0.998x geomean after-vs-before speed.
- One row is slightly faster, two are slightly slower.
- This is within noise and not a basis for a broad V3 claim.

Release decision remains:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

## Next Engineering Action

Do not spend more Phoenix V3 time trying to extract a speed claim from this
patch. Keep it as a contract/device-residency improvement.

The next V3 performance work should target a reusable primitive where the hot
path still dominates user-visible runtime:

- prepared execution/session runner that actually routes selected generic
  primitives;
- fixed-radius grouped continuation only if it changes the dominant grouped
  union work, not just the small count-refresh phase;
- AABB/topology stream or grouped reduction only when the same primitive can
  serve multiple benchmark apps.

## Goal-Level Decision Audit

1. Was I foolish?
   Partly. It was correct to run the A/B, but foolish that earlier testing did
   not catch missing partner dependencies and the undefined stream bug before
   pod timing.
2. If yes, what actions made the decision foolish?
   I relied too much on static tests and did not first enforce a partner-runtime
   smoke test on the pod.
3. Was there another possible path?
   Yes. Provision and record the partner venv first, then run a tiny runtime
   smoke before any performance row.
4. Can I now try a different path that truly solves the problem?
   Yes. The path now records environment readiness, keeps this as a contract
   fix only, and moves performance effort back to dominant reusable engine
   primitives rather than polishing tiny overheads.
