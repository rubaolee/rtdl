# V4 Point-Group Nearest-Witness Candidate POD Smoke

Status: generated development evidence, not a release authorization

Superseding repeat-gate evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`

## Result

| Surface | Queries | Status | Correctness | Wrapper elapsed | Native elapsed |
| --- | ---: | --- | --- | ---: | ---: |
| `v4_point_group_nearest_witness_2d_device_arrays` | 8,192 | `measured_candidate` | true | 0.000964s | 0.000138s |

## Boundary

- Candidate status: `candidate_pod_repeat_gate_passed_requires_external_review_before_release_scope`
- Native symbol: `rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns`
- Native execution path: `prepared_rt_core_point_group_nearest_witness_2d_device_query_columns`
- `host_query_upload_in_hot_path`: false
- `materializes_neighbor_rows`: false
- `native_direct_device_output_columns`: true
- `true_zero_copy_authorized`: false

This is a POD smoke result. The superseding repeat gate above is the stronger
performance evidence. Neither file is a measured V4.0 release-surface promotion
or broad V4 speedup authorization.

Source JSON:

- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`
