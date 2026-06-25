# Call For Review: V4 Point-Group Nearest-Witness Device-Output Candidate

Date: 2026-06-24
Requested verdict label: one of

- `accept_candidate_continue_to_catalog_promotion_decision`
- `accept_with_required_amendments_before_catalog_decision`
- `reject_candidate_wrong_v4_boundary`
- `blocked_insufficient_evidence`

## Context

V4 is the Python GPU-array RT-core lane. The current measured V4 catalog has
three Torch CUDA Tier-2 surfaces. This change promotes one V2/V2.x generic
point-group primitive into a V4 candidate surface, but does not add it to the
measured V4.0 release catalog.

New candidate surface:

`v4_point_group_nearest_witness_2d_device_arrays`

Source primitive:

`POINT_GROUP_NEAREST_WITNESS_2D`

## Files To Review

- `src/rtdsl/v4_point_group.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/optix_runtime.py`
- `scripts/v4_point_group_nearest_witness_device_outputs_validation.py`
- `scripts/v4_catalog_regression_gate.py`
- `future/v4/examples/point_group_nearest_witness_torch_device_arrays.py`
- `future/v4/point_group_device_array_frontdoor.md`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/README.md`

Evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.md`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`

## What Changed

1. Added V4 candidate API:
   `prepare_point_group_nearest_witness_2d_device_arrays_v4`.
2. Reused the existing native OptiX prepared point-group nearest-witness route
   with device query columns and direct device output columns:
   `rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns`.
3. Added catalog/planner candidate visibility, intentionally separate from the
   measured V4 release catalog.
4. Added a repeatable same-contract validation script and a user-facing
   candidate example.
5. Updated the catalog regression gate so GPU mode can include candidate
   examples only when explicitly requested with `--include-candidates`.

## POD Results

RTX A5000 POD:

- OptiX headers: `/workspace/vendor/optix-dev-8.0.0`
- CUDA: `/usr/local/cuda-12.8`
- Native library: `/root/rtdl_v4_candidate_pod/build/librtdl_optix.so`
- POD validation gate passed for 32,768 and 131,072 query points.

Summary:

| Queries | Parity | Direct device-output median | Legacy host-row median | Same-contract ratio |
| ---: | --- | ---: | ---: | ---: |
| 32,768 | pass | 0.000529401s | 0.351068474s | 663.143x |
| 131,072 | pass | 0.000506975s | 0.947073404s | 1868.088x |

The validation fixture is non-trivial. For each query-count run it contains
equal counts of exact matches, positive-offset nonzero nearest distances,
no-hit rows, and negative-offset nonzero nearest distances. No-hit rows are
checked against neighbor id `0xFFFFFFFF` and float32 max distance.

The ratio is `legacy_host_rows / direct_device_output` for the same prepared
native point-group primitive and fixture. It measures removal of host query-row
and host result-row materialization for this candidate front door. It does not
authorize broad V4 speedup wording, whole-application speedup wording, or
release promotion.

## Boundary

- The prepared search points and point groups are RTDL-owned native data.
- Query point columns are caller-owned Torch CUDA arrays in the hot run.
- Output columns are caller-owned Torch CUDA arrays in the hot run.
- This is not a public true-zero-copy claim because the prepared search/group
  data are native-owned, not caller-owned device arrays.
- Candidate metadata records `pod_candidate_partners: ["torch"]` separately
  from `partner_support_declared_unmeasured: ["cupy"]`.
- Candidate metadata uses direct-device handoff fields such as
  `query_point_columns_direct_device_read_confirmed`, not public
  true-zero-copy sub-claim fields.
- This is a generic point-group nearest-witness primitive, not a Hausdorff,
  collision, or app-specific native kernel.

## Questions For Reviewer

1. Is this truly a V4 Tier-2 generic operator candidate, not an app-specific
   kernel?
2. Is the same-contract comparison against the older host-row route valid and
   sufficiently disclosed?
3. Is it correct to keep it outside the measured V4.0 release catalog until
   external review and release decision, despite the strong POD repeat-gate
   ratio?
4. Are the claim boundaries strong enough, especially around:
   - no broad speedup claim
   - no whole-app claim
   - no true-zero-copy claim
   - no Tier-3 callback claim
   - native-owned prepared search/group inputs
5. What must be amended before any catalog promotion?

## Non-Authorization

This packet does not authorize:

- V4 release
- adding this candidate to the measured V4.0 catalog
- broad V4 speedup wording
- whole-application speedup wording
- RT-core POD performance wording
- true-zero-copy public wording
- Tier-3 callback/PTX support
- CuPy performance claims
- embedding/C-ABI or non-Python host claims
- app-specific native engine kernels
