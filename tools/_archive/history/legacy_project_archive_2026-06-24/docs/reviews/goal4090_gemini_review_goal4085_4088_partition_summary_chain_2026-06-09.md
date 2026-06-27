# Gemini Review: Goals4085-4088 Partition Summary Chain

Date: 2026-06-09
Verdict: `accept-with-boundary`

## Summary

This review covers the RT-DBSCAN fixed-radius grouped-union partition-summary chain, consisting of feasibility studies (Goals 4085-4087) and a targeted runtime optimization (Goal4088). The work successfully identifies the performance bottlenecks of the current partition-aware candidate and implements a significant host-side optimization without compromising the app-agnostic runtime boundary.

## Question Responses

### 1. Does Goal4088 preserve the app-agnostic runtime boundary while removing only unused host work for device-backed partition enumeration?

**Yes.** The optimization in `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py` surgicaly limits host-side AABB reconstruction and `cupy.asnumpy` transfers to cases where the `pair_enumeration` strategy actually requires them (i.e., the `"host"` branch). For device-backed enumeration, the necessary AABB data is already resident in device columns. This removal of redundant work is a generic runtime improvement and does not introduce app-specific logic.

### 2. Do the pod artifacts justify the claim that build time improved 1.6x-2.3x without changing pair/status counts?

**Yes.** The pod artifacts for Goal4088 (`docs/reports/goal4088_partition_summary_build_after_host_aabb_skip_pod.json`) compared against the Goal4085 baseline confirm the following median build time improvements at 65,536 points:

- `clustered3d`: 0.219861s -> 0.103282s (2.13x)
- `road3d`: 0.201510s -> 0.088037s (2.29x)
- `ngsim_dense`: 0.367637s -> 0.223795s (1.64x)

The pair and status counts (safe-full, ambiguous, safe-skip) remained identical to the baseline, as verified by `tests/goal4088_device_partition_summary_host_aabb_skip_test.py`.

### 3. Is the default-route policy correct: keep the current RTDL/OptiX grouped stream plus Numba route, and keep partition convergence explicit/unpromoted?

**Yes.** Despite the significant build-time improvement in Goal4088, the partition-summary build cost alone (e.g., 0.103s for clustered) still exceeds or is comparable to the *total* execution time of the current recommended route (0.093s for clustered, 0.036s for road). Furthermore, Goal4086 confirms that the current OptiX grouped-union ABI lacks the necessary fields to consume partition work streams efficiently. Promoting the partition-convergence route as the default is therefore premature.

### 4. Does Goal4087 correctly bound prepared reuse as a repeated-run niche rather than a default route?

**Yes.** The evidence in Goal4087 shows that for `road3d`, replay is slower than the current route, meaning it never breaks even. For `clustered3d`, the break-even point is ~11.04 runs (improved to ~8.48 runs in Goal4088). This clearly restricts the utility of the current prepared-summary implementation to repeated-run research or specific clustered workloads, rather than a general-purpose default.

### 5. Is the next engineering direction correct: cheaper native/device producer or fused safe-full/ambiguous work stream, not more wrapper tuning?

**Yes.** The feasibility chain proves that the "thin wrapper" approach over the CuPy preview is nearing its limit. The primary bottleneck is the materialization of the complete partition-pair table and the overhead of the Python/CuPy orchestration. Future performance gains must come from a native producer that avoids full materialization or a fused kernel that directly consumes partition-level metadata.

## Validation Results

The following tests were reviewed and their logic verified against the claims:

- `tests/goal4085_partition_summary_build_feasibility_test.py`: PASSED (verified metric recording and boundaries).
- `tests/goal4086_grouped_union_native_api_feasibility_after_partition_probe_test.py`: PASSED (verified current OptiX ABI limitations).
- `tests/goal4087_prepared_partition_summary_reuse_threshold_test.py`: PASSED (verified reuse break-even logic).
- `tests/goal4088_device_partition_summary_host_aabb_skip_test.py`: PASSED (verified 1.6x-2.3x speedup and count stability).

## Boundary Confirmation

This review confirms that the work adheres to the following mandates:
- **No** authorized release or public speedup wording.
- **No** broad RT-core or whole-app acceleration claims.
- **No** automatic partner selection or hidden dispatch.
- **No** app-specific native-engine logic (e.g., no "DBSCAN" in native params).
- **No** true-zero-copy wording.
- **Accepted** the explicit, unpromoted status of the `partition_convergence_hybrid` candidate.
