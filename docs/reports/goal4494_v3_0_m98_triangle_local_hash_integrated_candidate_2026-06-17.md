# Goal4494 / V3 M98 Triangle Integrated Local-Hash Candidate

## Conclusion

Goal4494 implements the complete integrated version of the Goal4493 idea inside the Triangle Counting app: source groups with at most 2,048 two-hop rows go through a Numba CUDA shared-memory local-hash unique/count branch, and the large tail falls back to the current duplicate-key fill plus CuPy sort/RLE unique/count branch.

The candidate is correct, but it is rejected. It matches the expected triangle counts on all three paper-scale rows, but it is slower than the current `numba_direct_sort_rle` route on both target decision metrics: `run_backend_ms` and `segment_ray_build_total_ms`.

The reason is now clear. The M97 prototype measured a batched small-group local-hash kernel in isolation. The integrated app path pays source-group planning, small/large partitioning, concatenation/decode, and many per-segment kernel launches/synchronizations. Those costs erase the local-hash micro-kernel win and are especially bad on `soc-LiveJournal1`.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Numba CUDA toolchain: packaged CUDA 12.4 `ptxas`:

```text
Build cuda_12.4.r12.4/compiler.34097967_0
```

Artifacts:

- `docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.json`
- `docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.jsonl`
- `docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17/`

Parameters:

- app mode: current segmented RT-2A1 route per dataset;
- baseline builder: `numba_direct_sort_rle`;
- candidate builder: `numba_direct_sort_rle_local_hash_2048`;
- segment max two-hop rows: 15,000,000;
- scene max directed edges: 2,000,000;
- query schedule: `prepared_segment_replay`;
- warmup/repeat: `w0/r1`;
- telemetry: synchronized segment-ray build subphases.

| Dataset | Baseline backend | Hybrid backend | Backend ratio | Baseline segment build | Hybrid segment build | Segment-build ratio | Total ratio | Count | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `com_lj` | 3.767s | 4.526s | 0.83x | 1.585s | 2.308s | 0.69x | 0.89x | 177,820,130 | reject |
| `soc_livejournal1` | 5.440s | 14.260s | 0.38x | 2.049s | 11.044s | 0.19x | 0.59x | 285,730,264 | reject |
| `com_orkut` | 22.956s | 24.147s | 0.95x | 10.909s | 12.576s | 0.87x | 1.02x | 627,584,181 | reject |

Ratios are baseline over hybrid; values below 1.0 mean the hybrid candidate is slower. `com_orkut` has a small total-time ratio above 1.0 in this single `w0/r1` run, but that does not promote the candidate because the target bottleneck metrics both regress. The total includes non-target process and run-envelope variance, while the optimization was specifically meant to reduce segment-ray construction and backend time.

## Reading

This closes the immediate local-hash optimization debt:

- keep `numba_direct_sort_rle` as the current complete Triangle Counting route;
- keep `numba_direct_sort_rle_local_hash_2048` as an explicit internal candidate for reproduction, not as a default;
- do not claim a Triangle Counting public RT-core speedup from this row;
- do not add app-specific native engine callbacks or Triangle-specific OptiX logic;
- do not spend the next cycle on this exact per-segment local-hash branch.

If Triangle Counting is revisited, the next credible direction is a coarser-batched segmented unique/count strategy with fewer per-segment kernel launches, or a reusable segmented reduction primitive. The lesson is that a correct local shared-memory kernel is not enough; the app route has to preserve batching and avoid extra materialization and synchronization.

Claim boundary:

- internal candidate matrix only;
- route changed: false;
- public speedup claim authorized: false;
- native engine customization: false;
- app-specific native engine callback: false.
