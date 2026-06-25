# Call For Review: `goal4620` Aggregate-Tree Fallback Feasibility Protocol

Date: 2026-06-24
Author: Codex
Status: protocol review request before implementation

## Background

`goal4619` ended with a reviewed No-Go for
`v4_fixed_radius_count_threshold_3d_device_arrays`.

Claude upheld the No-Go and conditionally accepted aggregate-tree
weighted-vector sum as the `goal4620` fallback candidate **only if** the
feasibility brief is amended with two mandatory audits:

1. Algorithmic genericity audit: prove this is not Barnes-Hut or another app
   kernel hidden under a generic name.
2. Device-query-column audit: prove it has an honest caller-owned device-array
   input/output contract before implementation proceeds.

This packet incorporates those amendments and asks reviewers whether Codex may
begin the `goal4620` feasibility audit.

## Proposed Candidate

Candidate generic operator name:

- `AGGREGATE_TREE_WEIGHTED_VECTOR_SUM_2D`

Existing contract/source:

- `src/rtdsl/aggregate_tree_reference.py`
- `aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract`
- `validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract`

Existing Python native wrapper:

- `src/rtdsl/optix_runtime.py`
- `prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix`
- `PreparedOptixAggregateTreeFusedWeightedVectorSum2D.run_device_columns`

Existing native symbols:

- `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d`
- `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d`
- `rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d`

## Known Facts Before Audit

### Positive signals

The native ABI already accepts source columns by device pointer:

- `source_ids_device_ptr`
- `source_x_device_ptr`
- `source_y_device_ptr`
- `source_weight_device_ptr`

The native ABI also accepts target columns by device pointer at prepare time:

- `target_ids_device_ptr`
- `target_x_device_ptr`
- `target_y_device_ptr`
- `target_weight_device_ptr`

The Python wrapper exposes:

- `PreparedOptixAggregateTreeFusedWeightedVectorSum2D.run_device_columns(...)`

The run output is device-column shaped:

- `vector_x_device_ptr`
- `vector_y_device_ptr`
- `visited_counts_device_ptr`
- `aggregate_counts_device_ptr`
- `exact_counts_device_ptr`

### Negative / risk signals

The current contract text is algorithmically suspicious for generic V4:

- it uses `theta`
- it accepts aggregate tree nodes
- it accepts `softening`
- it skips self-pairs
- it accumulates `target_weight * displacement / softened_distance_cubed`
- native code computes `source_weight * node.mass * inv_dist^3`

Those are Barnes-Hut / N-body style semantics unless proven otherwise.
Renaming them as "generic weighted-vector sum" is not enough.

The current contract also says:

- `status: "implemented_cuda_device_accumulation_not_rt_core"`
- `uses_optix_trace: False`

So it is not RT-core evidence. It may still be a V4 Tier-2 fused device-array
operator candidate, but it must not be described as RT-core acceleration.

The prepare path is not pure true-zero-copy:

- Python converts target rows to CuPy arrays from host iterables.
- Python passes tree nodes/CSR arrays as host ctypes arrays.
- Native downloads target ids/weights during prepare to validate/build internal
  lookup structures.

This may be acceptable for a prepared-session surface if the **measured hot run
path** uses caller-owned source device columns and native/device output columns,
but it cannot authorize public true-zero-copy wording.

## Required Audit A: Algorithmic Genericity

The audit must answer one binary question:

Can `AGGREGATE_TREE_WEIGHTED_VECTOR_SUM_2D` be honestly described as a generic
operator, or is it Barnes-Hut/N-body logic under a generic name?

Acceptance requires all of:

1. The operator is defined as a generic tree-aggregated weighted vector
   transform with clear mathematical inputs/outputs independent of an app name.
2. The API and docs do not use app identities such as Barnes-Hut, N-body,
   gravity, force simulation, clustering, or particle simulation as the surface
   identity.
3. Any domain-shaped parameters (`theta`, `softening`) are either:
   - renamed and specified as generic approximation parameters, or
   - explicitly scoped as making this a non-V4.0 candidate.
4. The implementation does not embed app-specific policies beyond the generic
   operator contract.
5. Reviewers can inspect the native computation and still agree it is an
   app-name-free continuation operator.

No-Go if:

- the acceptance/opening rule is inseparable from Barnes-Hut approximation
  semantics
- `softening` and `inverse distance cubed` are essential app/domain semantics
  rather than generic operator parameters
- the only truthful description is "Barnes-Hut fused kernel"

## Required Audit B: Device-Array Contract

The audit must answer one binary question:

Can this become an honest V4 Python GPU-array surface without hiding host
materialization in the measured hot path?

Acceptance requires all of:

1. Search/target value columns enter as caller-owned CUDA/Torch device arrays or
   the surface clearly says the prepared target/tree data is RTDL-owned native
   state, similar to point-group.
2. Source/query value columns enter as caller-owned Torch CUDA device arrays.
3. Output columns are caller-owned or RTDL-owned device columns returned without
   host result-table materialization.
4. The hot measured run path does not materialize per-source frontier rows or
   weighted contribution rows on host.
5. The surface metadata explicitly records:
   - `prepared_tree_owned_by_rtdl`
   - `source_columns_created_from: caller_torch_cuda_device_arrays`
   - `output_columns_device_resident: true`
   - `true_zero_copy_authorized: false`
   - `rt_core_acceleration_authorized: false`
6. POD evidence must compare the new route against the older V3/V2.x route it
   replaces, with correctness parity against a reference.

No-Go if:

- source/query values are repacked from Python rows in the measured run path
- output vectors are downloaded to host inside the claimed hot path
- the route only works through CuPy-created arrays from host examples and cannot
  accept caller Torch CUDA device arrays
- the implementation is only a V3 prepared-session helper without a clean V4
  front-door contract

## Required Audit C: RT-Core Claim Boundary

The current implementation is inside the OptiX backend library but launches a
CUDA kernel and records:

- `uses_optix_trace: False`
- `bvh_build_seconds: 0.0`
- `continuation_seconds: 0.0`

Therefore:

- it may be a fused device-array operator candidate
- it is not RT-core acceleration evidence
- it must not be used to claim "RTDL uses RT cores for this operator"
- it must not be used as support for broad V4 speedup wording

If V4.0 requires every measured Tier-2 surface to be RT-core-backed, this
candidate should be rejected now. If V4.0 allows generic fused device-array
operators that are CUDA-native but not RT-core-backed, it may continue with
explicit scope.

## `goal4620` Exit Gates

One of:

### Go

All audits pass:

- genericity passes
- device-array contract passes
- RT-core boundary is explicitly scoped as not RT-core
- feasibility evidence says implementation risk is bounded

Then Codex may start a narrowly scoped implementation of a V4 candidate surface,
but not measured-catalog promotion.

### No-Go: Algorithmic

The operator is Barnes-Hut/N-body/app-domain logic under a generic name.

Then Codex must reject this fallback and select another candidate from the V2/V2.x
inventory before implementation.

### No-Go: Device Contract

The operator cannot accept caller-owned source/query device arrays or cannot
keep output/device results resident in the measured hot path.

Then Codex must reject this fallback and select another candidate.

### No-Go: Scope

The project decides V4.0 Tier-2 must be RT-core-backed, and CUDA-only fused
operators are out of scope.

Then Codex must reject this fallback for V4.0, though it may remain an internal
or V4.x candidate.

## What Is Not Authorized Yet

This protocol review does not authorize:

- implementation
- measured-catalog promotion
- V4 release
- broad V4 speedup wording
- whole-app speedup wording
- public true-zero-copy wording
- RT-core acceleration wording for this operator
- app-specific native kernels
- Tier-3 callbacks
- C ABI / embedding / non-Python host work
- CuPy performance claims
- OptiX 9.1 scope

## Reviewer Questions

1. Does this protocol correctly incorporate Claude's two required amendments?
2. Is the aggregate-tree candidate still acceptable as the next feasibility
   target under these stricter gates?
3. Should CUDA-only fused device-array operators be allowed in V4.0 Tier-2, or
   must V4.0 Tier-2 be RT-core-backed only?
4. Are the Go/No-Go gates sharp enough to prevent relabeling Barnes-Hut as a
   generic surface?
5. Are the device-array gates sharp enough to prevent repeating the 3D
   fixed-radius host-query mistake?
6. May Codex begin the `goal4620` feasibility audit under this protocol?

