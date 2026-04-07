## Verdict

The package is largely accurate and the fallback boundary is documented clearly. Two issues were worth fixing before treating this as a closed audit: a timing anomaly in the stress artifact that could undermine the "same underlying execution" claim, and a raw-mode rejection test that covered only one of the two Jaccard workloads instead of both.

## Findings

**1. Timing anomaly contradicts the fallback narrative (technical honesty)**
The stress results showed Embree/OptiX/Vulkan consistently 3–7% faster than CPU at both sizes. The runtime code routes all three backends to the same `run_cpu(compiled, **inputs)` path for Jaccard workloads, so the table needed an explicit note that these differences should be treated as measurement noise or wrapper-overhead variation, not backend-specific benefit.

**2. Raw-mode rejection test covered only one workload (repo accuracy)**
The original `test_raw_mode_is_rejected_for_wrapper_fallback_backends` exercised `polygon_set_jaccard` for all three backends, but not `polygon_pair_overlap_area_rows`. The implementation already handled both names, so the right fix was to extend the test, not to change the runtime boundary.

**3. Fallback boundary is stated correctly and consistently (passes)**
The package states the wrapper-fallback boundary clearly and does not overclaim native RT-core or prepared-path maturity.

## Summary

After adding the timing-interpretation note and extending the raw-mode rejection test to both workloads, the package is acceptable as a bounded Goal 146 result: backend-wrapper closure plus Linux stress consistency for the narrow Jaccard line, not native backend maturity.
