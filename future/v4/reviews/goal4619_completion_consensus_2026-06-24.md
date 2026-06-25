# `goal4619` Completion Consensus

Date: 2026-06-24
Author: Codex
Status: complete; No-Go for 3D fixed-radius device-array surface

## Goal

`goal4619` audited whether the 3D fixed-radius count-threshold family can
honestly become a V4 Python GPU-array Tier-2 surface.

## Final Verdict

`no_go_3d_fixed_radius_device_array_surface_defer_select_fallback`

The existing 3D fixed-radius count-threshold route must not be implemented or
marketed as:

- `v4_fixed_radius_count_threshold_3d_device_arrays`

Reason:

- it has device output columns
- it has a useful self-query prepared-search shortcut
- but it does not have caller-owned search device columns plus caller-owned
  query device columns plus caller-owned output columns in the measured hot path

## Evidence Packet

Primary packet:

- `future/v4/reviews/call_for_review_v4_goal4619_3d_fixed_radius_no_go_and_fallback_2026-06-24.md`

Claude review:

- `future/v4/reviews/claude_v4_goal4619_3d_fixed_radius_no_go_and_fallback_review_2026-06-24.raw.md`

## 3-AI Consensus

### Seat 1: Codex

Verdict:

- `no_go_3d_fixed_radius_device_array_surface_defer_select_fallback`

Reason:

- the 3D native ABI exposes `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs`, not a 3D device-query-column symbol
- Python metadata says `input_contract: "host_query_points_prepared_native_search_scene"`
- Python runtime metadata says `transfer_mode: "host_query_points_to_device_threshold_columns"`
- native C++ constructs `std::vector<GpuPoint3DHost> gpu_queries` and uploads it before launch

### Seat 2: Mendel Internal Independent Audit

Review source:

- Codex multi-agent subagent `019efbf8-1f9d-7b13-b483-38acc30eb30e`

Verdict:

- No-Go for `goal4619`

Reason:

- the current code supports 3D count-threshold output device columns for
  host-row query inputs, plus a self-query prepared-search shortcut
- it does not support the full V4 device-array contract for caller-owned query
  device columns

### Seat 3: Claude External Review

Review:

- `future/v4/reviews/claude_v4_goal4619_3d_fixed_radius_no_go_and_fallback_review_2026-06-24.raw.md`

Verdict:

- `accept_with_required_amendments`

Claude upheld the No-Go:

- "No-Go for goal4619 is upheld."
- "The No-Go is correct."
- "Promoting it would be a surface contract misrepresentation."

Claude conditionally accepted the fallback candidate for `goal4620`, but only
after required amendments are incorporated into the feasibility brief:

1. Algorithmic audit: prove `aggregate_tree_fused_weighted_vector_sum_2d` is a
   generic operator and not merely Barnes-Hut under a generic name.
2. Device-query-column audit: verify the fallback has an honest caller-owned
   device-array input contract before implementation proceeds.

## Authorization To Continue

`goal4619` is complete as a No-Go.

Codex may proceed to `goal4620` **only as a feasibility/protocol step** that
incorporates Claude's required amendments. No fallback implementation is
authorized yet.

## Non-Authorization

This completion does not authorize:

- V4 release
- broad V4 speedup wording
- whole-app speedup wording
- 3D fixed-radius device-array promotion
- aggregate-tree implementation
- true-zero-copy public wording
- Tier-3 callback support
- raw OptiX callbacks
- C ABI / embedding / non-Python host work
- app-specific native kernels
- CuPy performance claims
- OptiX 9.1 scope

