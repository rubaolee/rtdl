# Goal2608 GPU-RMQ Generic Grouped-Argmin Kernel Fusion

Date: 2026-05-25

Repo HEAD during work: `dc6b91d29a37ad335e2ebe0cf553cd01606530fc` with uncommitted Goal2594-2608 working tree changes.

Pod evidence host: `root@203.57.40.101 -p 10082`, key `~/.ssh/id_ed25519_rtdl_codex`.

OptiX SDK on pod: `/workspace/optix-8.1`.

OptiX library on pod: `/workspace/rtdl_goal2598/build/librtdl_optix.so`.

## Purpose

After Goal2607, GPU-RMQ grouped queries use one app-side combined scene and one generic prepared grouped-argmin call. The remaining cost is mostly the generic post-traversal reduction pipeline. This goal improves that pipeline without adding GPU-RMQ semantics to native code.

## Implementation

Two bounded changes were made.

1. App-side lazy readiness guard:
   - `query_prepared_batch_arrays` now returns directly to compact arrays for `query_count < 2048`.
   - This avoids grouped-readiness probing on small compact runs.

2. Prepared-reuse threshold tuning:
   - The grouped path threshold is now explicit as `_PAPER_RT_GROUPED_ARGMIN_QUERY_THRESHOLD`.
   - After combined-scene lowering plus kernel fusion, grouped prepared-reuse is faster than compact arrays even for small query batches.
   - The default threshold is therefore lowered from `2048` to `1`.

3. Native generic grouped-argmin fusion:
   - The non-unique grouped-argmin path previously launched `init`, `min_key`, `min_index`, and `materialize`.
   - `closest_hit_grouped_argmin_min_index` now also writes `group_has_value` and `group_value` when it observes a row whose value key equals the per-group best key.
   - The separate `materialize` launch is removed from prepared and non-prepared grouped-argmin workloads.
   - The earlier redundant clear before the non-unique prepared path remains removed; the non-unique path initializes outputs through `init`.

This is a generic closest-hit grouped argmin optimization. Native code still sees only rows, ray-group IDs, candidate values, candidate indices, and output arrays.

## Validation

Local:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/optix_runtime.py examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py
PYTHONPATH=src:. python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2598_optix_generic_closest_hit_contract_test -v
Ran 21 tests: OK, 1 skipped locally because numpy is optional.
git diff --check: clean for active GPU-RMQ/native files.
```

Pod:

```text
make build-optix OPTIX_PREFIX=/workspace/optix-8.1
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal2598/build/librtdl_optix.so python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2598_optix_generic_closest_hit_contract_test -v
Ran 21 tests: OK.
```

## Performance Evidence

Prepared-reuse timings use 12 query repeats. Medians are query-only timings.

| Workload | Goal2606 median | Goal2607 median | Goal2608 median | Correct | Path |
|---|---:|---:|---:|---|---|
| repeated, 4K values, 1K queries, block 64 | 0.5588 ms | 0.5450 ms | 0.2534 ms | yes | combined scene grouped argmin |
| random, 16K values, 4K queries, block 256 | 0.6475 ms | 0.4933 ms | 0.4642 ms | yes | combined scene grouped argmin |
| repeated, 64K values, 8K queries, block 512 | 1.2724 ms | 1.0572 ms | 1.0338 ms | yes | combined scene grouped argmin |

Relative to Goal2606:

- 4K/1K prepared-reuse path improved by about 54.7%.
- 16K/4K grouped path improved by about 28.3%.
- 64K/8K grouped path improved by about 18.8%.

Relative to Goal2607:

- 4K/1K prepared-reuse path improved by about 53.5% because it now uses combined grouped argmin rather than compact arrays.
- 16K/4K grouped path improved by about 5.9%.
- 64K/8K grouped path improved by about 2.2%.

Threshold probe:

```text
Mixed/full-block 4K values, block 64:
1 query: grouped 0.1583 ms, compact 0.3198 ms
64 queries: grouped 0.2321 ms, compact 0.4248 ms
1000 queries: grouped 0.2361 ms, compact 0.5375 ms

Same-block-heavy 4K values, block 64:
16 queries: grouped 0.1711 ms, compact 0.2151 ms
128 queries: grouped 0.2251 ms, compact 0.2805 ms
1000 queries: grouped 0.2666 ms, compact 0.3450 ms
```

Final pod run:

```json
{"dataset":"repeated","value_count":4096,"query_count":1000,"block_size":64,"matches":true,"median_ms":0.2534,"combined_scene":true,"two_source_merge":false}
{"dataset":"random","value_count":16384,"query_count":4000,"block_size":256,"matches":true,"median_ms":0.4642,"combined_scene":true,"two_source_merge":false}
{"dataset":"repeated","value_count":65536,"query_count":8000,"block_size":512,"matches":true,"median_ms":1.0338,"combined_scene":true,"two_source_merge":false}
```

## Conclusion

Goal2608 should be kept. It removes a generic kernel launch from the non-unique grouped-argmin path, preserves correctness on the GPU-RMQ prepared-reuse matrix, and does not move any app-specific logic into the native engine.

The next larger optimization would require a new prepared grouped schedule or a packed key/value representation to reduce the remaining `min_key` plus `min_index` two-pass structure. That is more invasive and should be treated as a separate runtime primitive design task, not as an app-specific GPU-RMQ patch.
