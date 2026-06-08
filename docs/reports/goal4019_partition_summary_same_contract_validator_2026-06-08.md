# Goal4019 Partition Summary Same-Contract Validator

Date: 2026-06-08

## Purpose

Goal4016 defined a typed stream contract for `fixed_radius_partition_convergence_summary_3d`, and Goal4017 added a small Python reference builder for the compressed occupied-partition summary. Goal4019 adds the missing acceptance gate between that reference and a future native producer:

`validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(...)`.

This is deliberately a validator, not a promoted runtime route. It lets future OptiX/native work prove that produced columns match the app-agnostic reference before the route can be considered for performance evidence.

## Contract Checked

The validator rebuilds the reference summary from the same point rows, radius, cell factor, and pair capacity, then compares the candidate columns:

- `point_partition_ids`
- `occupied_partition_keys_x/y/z`
- `partition_offsets`
- `partition_counts`
- `partition_aabb_min/max_x/y/z`
- `near_pair_left_partition_ids`
- `near_pair_right_partition_ids`
- `near_pair_status`

It also checks partition/pair counts, visible-pair count, overflow, optional status counts, typed-stream validity when provided, and claim-boundary flags.

## Boundary

This goal does not add a native ABI. It does not make `partition_convergence_hybrid` executable. It does not authorize public speedup wording, RT-core speedup wording, whole-app benchmark wording, release wording, or true zero-copy wording.

The intended next step is a narrow native producer slice that must pass this same-contract validator on small deterministic inputs before any large pod timing is meaningful.

