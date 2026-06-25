# Call For Review: `goal4619` 3D Fixed-Radius Device-Array Feasibility

Date: 2026-06-24
Author: Codex
Status: feasibility verdict request

## Verdict Proposed By Codex

`no_go_3d_fixed_radius_device_array_surface_defer_select_fallback`

Codex proposes **No-Go** for implementing or marketing
`v4_fixed_radius_count_threshold_3d_device_arrays` as the next V4 surface.

Reason: the existing 3D fixed-radius count-threshold route has device output
columns and a self-query prepared-search shortcut, but it does **not** have the
full V4 Python GPU-array contract:

- caller-owned search point device columns
- caller-owned query point device columns
- caller-owned output device columns
- no host query-row materialization in the measured hot path

## Goal4619 Requirement

The approved goals document says `goal4619` must determine whether 3D
fixed-radius can honestly become a V4 Python GPU-array Tier-2 surface, or must
remain a narrower prepared-search/device-output candidate.

It explicitly forbids:

- marketing the existing 3D host-query route as V4 device-array input
- implementation before the feasibility verdict is reviewed

## Findings

### 1. Current V4 fixed-radius front door is 2D-only

`src/rtdsl/v4_fixed_radius.py` defines:

- `V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE =
  "v4_fixed_radius_count_threshold_2d_device_arrays"`

It imports and uses:

- `prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene`
- `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns`

There is no implemented `v4_fixed_radius_count_threshold_3d_device_arrays`
front door.

### 2. 2D has the real V4 device-query symbols

Native 2D symbols exist:

- `rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns`
- `rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns_on_stream`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream`

Python 2D route uses:

- `pack_optix_fixed_radius_count_threshold_2d_device_point_inputs(...)`
- direct device pointer/DLPack handoff for query columns
- direct device output columns

This is why the existing 2D surface is honest as a V4 device-array surface.

### 3. 3D count-threshold lacks the equivalent device-search and device-query ABI

Native 3D symbols found:

- `rtdl_optix_prepare_fixed_radius_count_threshold_3d`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_self_device_outputs`
- `rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d`

POD `nm` confirmed the same symbol set in:

- `/root/rtdl_v4_candidate_pod/build/librtdl_optix.so`

Missing 3D equivalents:

- no `rtdl_optix_prepare_fixed_radius_count_threshold_3d_device_search_columns`
- no `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_query_columns`
- no 3D on-stream device-query variant

### 4. Current 3D prepared partner route materializes query rows on host

`src/rtdsl/partner_adapters.py`:

- `fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(...)`
  accepts `query_points`, not query device columns
- its metadata says:
  - `input_contract: "host_query_points_prepared_native_search_scene"`

`src/rtdsl/optix_runtime.py`:

- `PreparedOptixFixedRadiusCountThreshold3D.write_device_count_threshold_columns(...)`
  calls:
  - `pack_points(records=query_points, dimension=3)`
- its metadata says:
  - `transfer_mode: "host_query_points_to_device_threshold_columns"`
  - `true_zero_copy_authorized: False`

Native code:

- `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs`
  takes `const RtdlPoint3D* query_points`
- `write_prepared_fixed_radius_count_threshold_3d_device_outputs_optix(...)`
  builds `std::vector<GpuPoint3DHost> gpu_queries` and uploads it to a device
  buffer before launch

That is not a V4 device-query-column hot path.

### 5. Self-query is useful but not a general V4 device-array surface

The 3D self-query path is stronger than the generic query route:

- `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_self_device_outputs`

Metadata says:

- `query_source: "prepared_search_points_self_query_device"`
- `prepared_search_device_buffer_reused_as_query: True`
- `host_query_point_repack_avoided: True`
- `host_query_point_upload_avoided: True`

But this only covers the special case where query points are the prepared search
scene itself. It does not accept caller-owned query point device columns, so it
cannot be the general `*_device_arrays` surface.

### 6. 3D neighbors/ranked-summary symbols do not close this gap

There are many 3D ranked-summary/native aggregate symbols, including:

- `rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d`
- `rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch`
- `rtdl_optix_aggregate_self_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch`

These are valuable future assets, but they inherit the same feasibility concern
until a true caller query device-column path is proved. They should not be used
to smuggle 3D fixed-radius into V4 as a device-array surface.

## Independent Internal Audit

Codex spawned an internal independent explorer (`Mendel`) to audit the same
question. It returned:

- Recommendation: No-Go for `goal4619`
- Reason: current code supports 3D count-threshold output device columns for
  host-row query inputs plus self-query prepared-search shortcut, but not the
  full V4 device-array contract.

This is not being counted as the final external review, but it agrees with
Codex's direct audit.

## Proposed Fallback For `goal4620`

Codex proposes that `goal4620` **not** implement 3D fixed-radius.

Preferred fallback candidate for review:

- generic weighted-vector aggregation over an aggregate tree
- existing source: `aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract`
- native symbols:
  - `rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d`
  - `rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d`
  - `rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d`

Reason:

- it is a generic fused continuation operator if framed as weighted-vector
  aggregation, not as a Barnes-Hut app kernel
- it directly exercises the V4 design thesis: push a recognized reduce/aggregate
  operator into the native RT path
- it already has prior native contract tests and V3-era scaffolding

Hard boundary for the fallback:

- do not call it Barnes-Hut
- do not add an app-specific kernel
- do not claim release or broad speedup
- before implementation, run a separate feasibility audit that verifies whether
  its input/output contract can honestly become a V4 Python GPU-array surface

Alternative fallback candidates:

- ranked fixed-radius summary/top-k only if the query-device-column boundary is
  audited and not inherited from host-row query paths
- another generic app-name-free fused operator from the V2/V2.x inventory

## Reviewer Questions

1. Do you agree with the `goal4619` No-Go verdict for
   `v4_fixed_radius_count_threshold_3d_device_arrays`?
2. Is the evidence sufficient that 3D fixed-radius has output device columns and
   self-query residency, but lacks a true caller query device-column V4 contract?
3. Is Codex right to forbid wrapping the current host-query route as a V4
   device-array surface?
4. Do you approve selecting generic aggregate-tree weighted-vector sum as the
   fallback candidate for a separate `goal4620` feasibility/implementation path?
5. If not, what fallback should be selected and why?
6. Does this packet preserve all claim boundaries?

## Non-Authorization

This packet does not authorize:

- V4 release
- broad V4 speedup wording
- whole-app speedup wording
- 3D fixed-radius device-array promotion
- true-zero-copy public wording
- Tier-3 callback support
- raw OptiX callbacks
- C ABI / embedding / non-Python host work
- app-specific native kernels
- CuPy performance claims
- OptiX 9.1 scope

