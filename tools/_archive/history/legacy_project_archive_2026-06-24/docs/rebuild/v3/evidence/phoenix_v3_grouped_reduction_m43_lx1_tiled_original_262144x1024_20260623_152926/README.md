# Phoenix V3 M41 Grouped-Reduction Local Harness

Status: `grouped_reduction_m41_local_run_complete_not_release`

This is local Step-2 harness evidence only. It does not authorize release, all-app POD, public speedup wording, V4, embedding, C ABI, or true-zero-copy claims.

## Summary

- row_count: `262144`
- group_count: `1024`
- failed_check_count: `0`
- comparisons: `{"all_variant_vector_sum_signatures_allclose": true, "all_variant_vector_sum_signatures_hash_match": false, "all_variant_vector_sum_signatures_match": true, "material_performance_claim_authorized": false, "runner_vs_cpu_hot_speedup": 0.6216966017370773, "runner_vs_legacy_hot_speedup": 4.039521882114849, "runner_vs_legacy_wall_speedup": 83.19784693903458, "status": "computed", "step2_local_runner_contract_candidate": true, "vector_sum_allclose_tolerance": {"atol": 1e-06, "rationale": "grouped vector sums are double-precision reductions; strict hash equality is diagnostic, while allclose tolerates valid floating-point accumulation-order differences across CPU and CUDA paths", "rtol": 1e-09}}`
