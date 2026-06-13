# Goal4345: Backend Comparison Campaign Closeout

Date: 2026-06-11

Status: internal closeout; not release or public speedup authorization.

## Verdict

- NVIDIA RT cores: yes, internally ready for the current OptiX benchmark routes; Goal4342 found no obvious remaining high-leverage RT-core implementation work.
- Intel Embree CPUs: yes, internally ready for the native Embree primitive rows with contract boundaries; Goal4343 now reports zero missing same-contract scale rows.
- Serious comparison: yes, as a bucketted internal packet; the v2.12 packet separates clean query ratios, RTNN, RT-DBSCAN, and Barnes-Hut scoped paired rows, and boundary-limited phase rows. No promoted benchmark app remains in the contract-choice blocker bucket.

## Answers

### ready_to_use_high_performance_nvidia_rt_cores

- Answer: `yes_internal_current_optix_paths`
- Evidence: Goal4342 found no obvious remaining high-leverage OptiX/RT-core implementation optimization for the current campaign.
- Boundary: This is internal readiness for current benchmark routes, not release authorization or public speedup wording.

### ready_to_use_high_performance_intel_embree_cpus

- Answer: `yes_for_native_embree_primitive_rows_with_contract_boundaries`
- Evidence: Goal4340 fixed LibRTS AABB_INDEX_QUERY_2D; Goal4344 supplies the five previously missing Embree scale rows; Goal4343 now reports zero missing same-contract scale pairs.
- Boundary: No promoted benchmark app currently requires a contract choice before an internal OptiX-vs-Embree ratio. Spatial RayJoin, RTNN, RT-DBSCAN, and Barnes-Hut now have scoped internal-only paired rows.

### serious_comparison_ready

- Answer: `yes_as_an_internal_bucketted_packet`
- Evidence: The v2.12 packet separates one fully optimized LibRTS pair, three clean same-contract query-ratio scale rows, the RTNN same-contract raw-row pair, the RT-DBSCAN same configured-route RTDL+Numba pair, the Barnes-Hut native node-coverage pair, and two boundary-limited phase rows.
- Boundary: No public speedup, release, or whole-app claim is authorized.

## Comparison Buckets

| Bucket | Count |
| --- | ---: |
| `fully_optimized_measured_pair_count` | 1 |
| `fresh_scale_comparison_row_count` | 5 |
| `clean_internal_query_ratio_count` | 8 |
| `boundary_limited_phase_ratio_count` | 2 |
| `contract_choice_blocker_count` | 0 |
| `embree_scale_artifact_count` | 5 |
| `rt_core_remaining_high_leverage_work_count` | 0 |
| `embree_same_contract_scale_pair_needed_count` | 0 |

## Partner Policy

- Default: `do_not_force_numba_universally`
- Pure RTDL table: Compare OptiX and Embree only on the native RTDL primitive/query phase with no app-level partner continuation in the timed metric.
- Configured-route table: When the benchmark contract genuinely includes a continuation, hold the continuation contract fixed and label the row as RTDL+partner. Numba is acceptable for CPU/portable continuations when both sides use the same Numba work; GPU-resident CuPy/Triton continuations belong in explicitly labeled configured-route rows.
- Partner-only rows: A partner-only row, such as the current Barnes-Hut Numba exact-force scale row, is not an OptiX-vs-Embree backend comparison.
- Automatic partner selection authorized: `False`

## Boundary

Goal4345 closes the current internal RTDL OptiX-vs-Embree comparison campaign by summarizing the RT-core closeout, Embree scale closeout, and optimized comparison packet. It does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, Intel GPU performance wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic.

Validation status: `accept`.
