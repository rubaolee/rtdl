# Goal2607 GPU-RMQ Combined-Scene Grouped Argmin

Date: 2026-05-24

Repo HEAD during work: `dc6b91d29a37ad335e2ebe0cf553cd01606530fc` with uncommitted Goal2594-2607 working tree changes.

Pod evidence host: `root@203.57.40.101 -p 10082`, key `~/.ssh/id_ed25519_rtdl_codex`.

OptiX library on pod: `/workspace/rtdl_goal2598/build/librtdl_optix.so`.

## Purpose

Goal2606 removed the Python cross-source merge by adding a generic native two-source grouped merge. This goal tests whether GPU-RMQ can go one step further without adding app-specific native code: lower both element-phase rays and full-block rays into one app-side combined triangle scene, then call the existing generic prepared-scene grouped-argmin primitive once.

The native engine still sees only:

- one prepared static triangle scene,
- one prepared ray batch,
- caller-owned ray group IDs,
- caller-owned candidate values,
- caller-owned candidate tie-break indices.

No GPU-RMQ vocabulary or app-specific arithmetic was added to the native engine.

## Implementation

App-side combined scene:

- Element triangles keep their original triangle IDs and candidate-array positions.
- Block-summary triangles are appended with triangle IDs offset by `value_count`.
- Candidate values are concatenated as `[element_values, block_min_values]`.
- Candidate indices are concatenated as `[element_indices, block_arg_indices]`.
- Element rays and element triangles are shifted by a small `z` offset of `3.0`.
- Block-summary geometry remains near zero so its tiny selector coordinates keep float32 precision.

The first attempted design shifted block-summary `y/z` coordinates by a large slab offset. That was rejected because block selector gaps are about `1 / (1 << 23)`, so large-coordinate float32 precision caused wrong full-block hits. A second attempt shifted element `y/z`; it fixed random data but produced one repeated-data off-by-one tie due left-boundary `y` precision. The accepted design shifts only element `z`, preserving original `y` boundary precision and separating the two geometry slabs.

The prepared app handle now also prepares scenes lazily:

- Compact small-query runs prepare only element/block scenes.
- Grouped combined-scene runs prepare the combined scene and combined grouped inputs first.
- Element/block prepared fallback artifacts are not built when the combined path is already ready.

## Validation

Local:

```text
PYTHONPATH=src:. python3 -m py_compile examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py
PYTHONPATH=src:. python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2598_optix_generic_closest_hit_contract_test -v
Ran 21 tests: OK, 1 skipped locally because numpy is optional.
git diff --check: clean for active GPU-RMQ files.
```

Pod:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal2598/build/librtdl_optix.so python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2598_optix_generic_closest_hit_contract_test -v
Ran 21 tests: OK.
```

## Performance Evidence

Prepared-reuse timings use 12 query repeats. The first repeat can include runtime/JIT effects; medians are reported.

| Workload | Previous Goal2606 median | Goal2607 median | Correct | Path |
|---|---:|---:|---|---|
| repeated, 4K values, 1K queries, block 64 | 0.5588 ms | 0.5450 ms | yes | compact arrays, combined scene not used |
| random, 16K values, 4K queries, block 256 | 0.6475 ms | 0.4933 ms | yes | combined scene grouped argmin |
| repeated, 64K values, 8K queries, block 512 | 1.2724 ms | 1.0572 ms | yes | combined scene grouped argmin |

Relative to Goal2606:

- 16K/4K grouped path improved by about 23.8%.
- 64K/8K grouped path improved by about 16.9%.
- 4K/1K remains on compact arrays because the grouped path threshold is `query_count >= 2048`; the small difference is not treated as a combined-scene claim.

Final pod run:

```json
{"dataset":"repeated","value_count":4096,"query_count":1000,"block_size":64,"matches":true,"median_ms":0.5450,"combined_scene":false,"two_source_merge":false}
{"dataset":"random","value_count":16384,"query_count":4000,"block_size":256,"matches":true,"median_ms":0.4933,"combined_scene":true,"two_source_merge":false}
{"dataset":"repeated","value_count":65536,"query_count":8000,"block_size":512,"matches":true,"median_ms":1.0572,"combined_scene":true,"two_source_merge":false}
```

## Conclusion

The accepted Goal2607 path is worth keeping as the GPU-RMQ default for grouped prepared-reuse queries. It removes one OptiX traversal/reduction launch by app-side lowering into one combined generic scene, improves the two grouped benchmark cases, and preserves the native engine boundary.

The precision lesson is important for future RTDL lowering work: when app-side geometry uses tiny selector gaps, scene fusion must avoid translating those tiny coordinates into a large float32 magnitude range. The regression test `test_combined_scene_preserves_block_selector_precision` records this contract.
