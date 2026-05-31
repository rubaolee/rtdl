# Independent Review - Goal2785 Presegmented Vector-Sum Offsets

Date: 2026-05-31
Reviewer: Gemini CLI

## Review Summary

This review assesses Goal2785, which introduces a presegmented row-offset vector-sum path for Triton, aiming to avoid global atomic additions present in the previous generic Triton grouped vector-sum preview. The goal explicitly focuses on a generic contract, without embedding application-specific force logic (e.g., Barnes-Hut).

## Files Inspected

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `tests/goal2785_presegmented_vector_sum_triton_offsets_test.py`
- `docs/reports/goal2785_presegmented_vector_sum_triton_offsets_2026-05-31.md`
- `docs/reports/goal2785_pod_artifacts/goal2785_presegmented_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json`
- `docs/research/future_version_to_do_list.md`

## Review Questions & Answers

1.  **Does Goal2785 add a generic presegmented row-offset vector-sum contract without embedding Barnes-Hut/app force logic?**
    Yes. The `run_triton_grouped_vector_sum_f64x2_by_offsets` function in `triton_partner_continuation.py` and its integration in `partner_adapters.py` clearly define a generic contract based on `row_offsets`. The report explicitly states that this is a generic prepared-row contract and does not authorize embedding Barnes-Hut or force-law logic. This is also confirmed by the `test_presegmented_offsets_kernel_is_generic_and_atomic_free` test.

2.  **Does the offsets kernel avoid global atomic adds when row offsets are used?**
    Yes. The `_triton_grouped_vector_sum_f64x2_offsets_kernel` uses `tl.sum(vals_x, axis=0)` followed by `tl.store(output_x + group, ...)`. This pattern performs a local sum per group and stores the result, effectively avoiding global atomic additions within the kernel's logic. The report's metadata (`global_atomic_add_used: false`) and the corresponding test assertion confirm this.

3.  **Is the performance evidence recorded honestly, including the small improvement versus the atomic Triton path and the remaining loss to Torch?**
    Yes. The performance report and JSON artifact clearly demonstrate the timing comparisons. The "Offsets / Atomic" ratios (approx. 0.9x-0.99x) show a small improvement, while the "Offsets / Torch" ratios (approx. 4.3x-14.6x) frankly indicate that Torch remains substantially faster. Both the report's conclusion and the `future_version_to_do_list.md` accurately reflect these findings, stating that Triton is not yet a promoted performance path for vector sums compared to Torch.

4.  **Are RT-core, true-zero-copy, whole-app, public speedup, and release claims still blocked?**
    Yes. The "Boundary" section of the report explicitly disallows all these claims. Furthermore, the metadata within the code (`triton_partner_continuation.py`, `partner_adapters.py`) and the JSON artifact consistently show these flags (e.g., `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `v2_5_release_authorized`, `whole_app_speedup_claim_authorized`) as `false` or `preview_not_promoted`.

5.  **Are the tests and report sufficient for this bounded preview step?**
    Yes. The provided `tests/goal2785_presegmented_vector_sum_triton_offsets_test.py` includes tests to verify the generic nature of the kernel, the absence of global atomics, and numerical correctness by comparing against the Torch implementation. The report details local and pod validation steps, complete with specific performance metrics. Given that this is described as a "bounded preview step," the current level of testing and reporting is appropriate and sufficient to validate the defined scope of the goal.

## Verdict

`accept-with-boundary`

The implementation successfully delivers a generic, atomics-free presegmented row-offset vector-sum contract as specified. The performance characteristics, showing a modest improvement over the previous Triton approach but still trailing Torch, are transparently documented. All stated boundary conditions and restrictions on public claims are upheld. The testing and reporting are adequate for this bounded preview.