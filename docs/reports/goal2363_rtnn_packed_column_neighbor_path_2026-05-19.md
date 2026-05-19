# Goal2363 - Packed-Column 3D Neighbor Path for RTNN Campaign

Date: 2026-05-19

Status: implemented in the benchmark harness and pod-tested.

## Purpose

Goal2361 showed that the native `fixed_radius_neighbors_3d` phases are already fast relative to the full `rt.run_optix(...)` wall time. The expensive part was not the generic uniform-cell CUDA count/compact kernels; it was the user-facing Python record path repeatedly normalizing and packing tuple-of-dict point records.

Goal2363 adds a packed-column input mode to the RTNN comparison harness. This uses the existing RTDL public data path:

```python
rt.pack_points(ids=ids, x=xs, y=ys, z=zs, dimension=3)
```

It is not a native RTNN hook, not an app-specific primitive, and not a new engine ABI. It is the intended v2.x lesson: serious RTDL applications should keep large data in column/packed form instead of repeatedly presenting millions of Python dictionaries to the runtime.

## Implementation

`scripts/goal2348_rtnn_v2_2_external_runner.py` now accepts:

```text
run-rtdl-current-3d-neighbors-smoke --input-mode records
run-rtdl-current-3d-neighbors-smoke --input-mode packed-columns
```

The default remains `records` for compatibility with earlier artifacts. The packed-column mode loads CSV columns once, packs them through RTDL's generic `PackedPoints` contract, and then runs the same `fixed_radius_neighbors_3d` kernel with the same result mode, radius, and K.

The runner records:

- `input_mode`;
- `input_pack_sec`;
- `phase_timings`;
- existing claim-boundary flags.

## Pod Evidence

| Item | Value |
| --- | --- |
| SSH endpoint | `ssh root@69.30.85.236 -p 22170 -i id_ed25519_rtdl_codex` |
| GPU | NVIDIA RTX A5000 |
| OptiX SDK | `/root/vendor/optix-sdk-9.0` |
| Existing native build | Goal2361 `make build-optix` pass |
| Runner test | `tests.goal2348_rtnn_v2_2_external_runner_test`: 8/8 pass |

Artifacts:

```text
docs/reports/goal2361_rtdl_3d_neighbor_phase/
```

## Results

Same synthetic 3D points, radius 0.02, K=50, raw result mode, repeat=3, warm last run.

| Input | Record-mode wall sec | Packed-column warm sec | Packed one-time pack sec | Record to packed warm delta | Row count |
| --- | ---: | ---: | ---: | ---: | ---: |
| 65,536 points | 0.775476 | 0.011291 | 0.104972 | 68.68x faster | 206,168 |
| 262,144 points | 3.329380 | 0.128015 | 0.457984 | 26.01x faster | 2,510,258 |

Comparison to the collected RTNN warm rows from Goal2357:

| Input | RTNN warm sec | RTDL packed warm sec | RTDL packed warm vs RTNN | RTDL packed including one-time pack | Including pack vs RTNN |
| --- | ---: | ---: | ---: | ---: | ---: |
| 65,536 points | 1.357491 | 0.011291 | 120.23x faster | 0.116263 | 11.68x faster |
| 262,144 points | 1.527938 | 0.128015 | 11.94x faster | 0.586000 | 2.61x faster |

## Interpretation

This does not mean RTDL has reproduced RTNN's full paper system. It means the current generic RTDL uniform-cell neighbor primitive becomes competitive once the app feeds it data in a scalable RTDL form.

The important design lesson is now clear:

- tuple-of-dict records are fine for learner examples and correctness;
- column/packed inputs are the high-performance v2.x path;
- future prepared bounded-neighbor work should make this policy explicit and reusable, rather than letting users accidentally benchmark Python record normalization.

## Claim Boundary

This goal authorizes a narrow claim that RTDL's generic packed-column path dramatically reduces Python-side overhead for the RTNN-inspired 3D fixed-radius neighbor benchmark on the tested RTX A5000 rows.

This goal does not authorize:

- a broad RT-core speedup claim;
- a claim that the default path is RT-core accelerated;
- a full RTNN reproduction claim;
- a v2.2 release claim.

## Next Step

Promote this from a benchmark harness option into a documented v2.x primitive/runtime pattern:

```text
prepared_bounded_neighbor_search_3d
```

That primitive should expose explicit prepared packed inputs, phase telemetry, result-mode policy, and row-continuation choices so high-performance user code gets the packed path by construction.
