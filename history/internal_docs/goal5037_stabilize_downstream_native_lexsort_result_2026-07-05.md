# Goal5037 Result: Stabilize Prepared Query-Batch Performance, Decompose Downstream, Fix Native Lexsort

Date: 2026-07-05

## Verdict

`completed_stable_70ms_prepared_query_batch_binary_route__native_lexsort_fixed`

This goal completed the three requested actions:

1. Stabilize the prepared query-batch hot-body number.
2. Decompose the remaining downstream floor.
3. Resolve the POD native CUDA lexsort toolchain issue.

## Product Regime

The result is for this regime only:

```text
prepared LSI base session
+ six distinct chain-contiguous query batches
+ writer-free binary route
+ prepared per-batch LSI query workspaces
+ device-resident carrier
+ native CUDA/Thrust lexsort
```

It is not:
- cold CLI one-shot;
- paper text output;
- same-input result replay;
- author-performance parity;
- full Section 5.7 paper-input timing.

## Input

Top4 County x Zipcode representative input:

```text
Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb
Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb
```

All N=5 runs share identical structural anchors:

```text
lsi_row_counts:         [21424, 56228, 66414, 67840, 88490, 127926]
descriptor_pair_counts: [2756, 2873, 2987, 3058, 4723, 6316]
```

## 1. Stabilized Performance

### Numba Sort Fallback, N=5

This validates that Goal5036's `~0.089s` number is stable.

| Metric | Median | Min | Max | Mean |
|---|---:|---:|---:|---:|
| writer-free hot | 0.089694s | 0.089125s | 0.102557s | 0.092192s |
| LSI phase | 0.002044s | 0.001978s | 0.002327s | 0.002091s |
| downstream floor | 0.086990s | 0.086568s | 0.100595s | 0.089830s |

Artifacts:

```text
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_1_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_2_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_3_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_4_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_5_top4.json
```

### Native CUDA/Thrust Lexsort, N=5

After rebuilding the OptiX library with an explicit Ada SASS target, native lexsort works on the POD and is faster.

| Metric | Median | Min | Max | Mean |
|---|---:|---:|---:|---:|
| writer-free hot | 0.070311s | 0.069247s | 0.070590s | 0.070171s |
| LSI phase | 0.001870s | 0.001787s | 0.001990s | 0.001880s |
| downstream floor | 0.068286s | 0.067474s | 0.068775s | 0.068293s |

Artifacts:

```text
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_1_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_2_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_3_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_4_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_5_top4.json
```

### Current Best Number

The current best stabilized number is:

```text
0.07031s
```

This is the N=5 median writer-free hot body for the prepared query-batch binary route with native CUDA/Thrust lexsort.

## 2. Downstream Floor Decomposition

After LSI query-batch workspace warmup, LSI is no longer the hot-body bottleneck:

```text
LSI phase:        ~0.00187s
downstream floor: ~0.06829s
```

Native lexsort N=5 medians-of-medians:

| Component | Median |
|---|---:|
| device carrier construction | 0.024965s |
| vertex PIP map1-in-map0 | 0.012715s |
| descriptor-pair count consumer | 0.011365s |
| vertex PIP map0-in-map1 | 0.005067s |
| sort map0 | 0.003282s |
| sort map1 | 0.003231s |
| intersection reprojection | 0.002506s |
| midpoint face scatter map0 | 0.000177s |
| midpoint face scatter map1 | 0.000125s |

The next real optimization targets are therefore:

1. carrier construction, about 25ms;
2. PIP, about 17.8ms combined;
3. descriptor consumer, about 11.4ms;
4. remaining sort, about 6.5ms combined.

The old LSI scaled-cache workspace mountain is gone in this regime.

## 3. Native Lexsort Toolchain Issue

### Failure

On the POD, native lexsort initially failed with:

```text
cudaErrorUnsupportedPtxVersion
```

It failed even with CUDA 12.4 NVRTC/NVVM libraries first in `LD_LIBRARY_PATH`, because the native helper is compiled from:

```text
src/native/optix/rtdl_optix_cuda_helpers.cu
```

and uses:

```text
thrust::sort(thrust::device, ...)
```

The issue was not the app route. It was the native helper build target.

### Fix

Rebuild the OptiX backend with an explicit Ada SASS target:

```text
make build-optix \
  OPTIX_PREFIX=/root/vendor/optix-dev \
  CUDA_PREFIX=/usr/local/cuda-12.8 \
  NVCC=/usr/local/cuda-12.8/bin/nvcc \
  OPTIX_CUDA_ARCH=sm_89
```

After this rebuild:

```text
rtdl_cuda_sort_i64_f64_i64_i64_lex
```

works on the POD.

Minimal native lexsort validation:

```text
input edge: [3, 1, 2, 1]
input dist: [0.3, 0.1, 0.2, 0.0]
input tie:  [0, 0, 0, 1]
input ord:  [0, 1, 2, 3]

sorted edge: [1, 1, 2, 3]
sorted dist: [0.0, 0.1, 0.2, 0.3]
sorted tie:  [1, 0, 0, 0]
sorted ord:  [3, 1, 2, 0]
```

Full RayJoin route native lexsort N=5 then completed successfully.

## Integrity

No RTDL core/native source code was changed in this goal. The native fix was a build configuration fix on the POD.

Existing Goal5036 code/test checks remain valid:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5036_prepared_lsi_query_workspace_test tests.goal5035_public_perf_boundary_guard_test tests.goal5034_device_carrier_atomic_append_test
git diff --check
```

Previously passed locally:

```text
Ran 7 tests in 0.004s
OK
```

## Not Authorized

This goal does not authorize:

- using 0.07031s as a cold CLI one-shot number;
- using 0.07031s for paper text output;
- comparing 0.07031s to an author full-overlay or text-output denominator without matching regime;
- claiming all RayJoin Section 5.7 pairs;
- claiming full device-resident overlay is complete beyond this binary descriptor route.

## Practical Conclusion

The current fastest honest top4 number is:

```text
0.07031s
```

It is stable across N=5 in the prepared query-batch, writer-free binary route with native lexsort. The remaining hot-body mountain is no longer LSI. It is the downstream device carrier/PIP/consumer stack.
