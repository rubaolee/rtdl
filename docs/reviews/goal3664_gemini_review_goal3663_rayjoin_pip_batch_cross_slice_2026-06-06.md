# Independent Gemini Review: Goal3663 RayJoin PIP Batch Cross-Slice Review

**Date:** 2026-06-06

**Reviewer:** Gemini

**This is an independent Gemini review, distinct from Codex. It authorizes no public release, public speedup claims, or RTDL-beats-RayJoin claims.**

## Verdict: accept-with-boundary

The evidence presented in Goal3663, along with the supporting artifacts and reports, consistently confirms the cross-slice support for the batched repeated-request PIP throughput contract. The documentation maintains clear boundaries, preventing overclaiming.

## Findings

### 1. Cross-Slice Support for Batched Throughput (Question 1)

Goal3663 correctly demonstrates cross-slice support for the batched repeated-request PIP throughput contract. The report `docs/reports/goal3663_rayjoin_pip_batch_executor_cross_slice_2026-06-06.md` explicitly states its purpose to verify this contract beyond the initial 512-row slice, and its interpretation confirms that "The larger 4096-slice result confirms that Goal3660 was not a one-slice accident." The comparative results show consistent RTDL/OptiX performance benefits across both the 512 and 4096 public-CDB slices, with RTDL/RayJoin query ratios of 0.178x and 0.111x, respectively, indicating significantly lower `ms/request` for RTDL.

### 2. Internal Consistency and Cleanliness of Artifacts (Question 2)

Both the `summary.json` artifacts for the 512-row (`docs/reports/goal3660_rayjoin_pip_batch_executor_throughput_a5000/summary.json`) and 4096-row (`docs/reports/goal3663_rayjoin_pip_batch_executor_cross_slice_a5000/summary_4096.json`) slices are internally consistent and clean.
- Both artifacts show `source_dirty: []`, confirming a clean source tree during the runs.
- The `rtdl.pip.counts.last` values (1417 for 512 and 11331 for 4096) precisely match the "Exact count" reported in `docs/reports/goal3663_rayjoin_pip_batch_executor_cross_slice_2026-06-06.md`.
- The `pip_timing_contract` field in both summaries is consistently set to `"batched_repeated_request_throughput_not_one_shot_latency"`, reinforcing the specific nature of the measured performance.
- Key parameters like `pip_batch_request_count: 100`, `pip_batch_stream_count: "auto"`, and `internal_query_repeat: 30000` are consistent, as verified by `tests/goal3663_rayjoin_pip_batch_executor_cross_slice_test.py`.

### 3. Clear Boundary Definitions in Report (Question 3)

The report `docs/reports/goal3663_rayjoin_pip_batch_executor_cross_slice_2026-06-06.md` meticulously defines the boundaries of the findings. It explicitly states that the contract is for "batched repeated-request throughput" and is "not one-shot latency, not full RayJoin paper reproduction, and not public RTDL-beats-RayJoin wording." The "Boundary" section further enumerates what Goal3663 does not authorize, such as "public v2.9 release wording," "public speedup wording," and "whole-app RayJoin speedup wording." The `claim_boundary` field in both `summary.json` files uniformly sets all related authorization flags to `false`, aligning with the report's conservative claims.

### 4. Goal3602 Status Refresh Accuracy (Question 4)

The `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md` report correctly updates the RayJoin PIP reading without overclaiming.
- It differentiates between one-shot/sequential PIP (where RTDL is "still slower than RayJoin `query_exec`") and batched repeated-request PIP (where RTDL shows "Strong throughput evidence").
- The "Engineering Reading" section provides a balanced perspective, acknowledging RTDL/OptiX wins in specific areas while clearly stating remaining gaps like "one-shot RTDL-vs-RayJoin latency and second-GPU confirmation."
- The "Boundary" section for Goal3602 also explicitly denies authorization for public speedup or whole-app acceleration claims, reinforcing the cautious interpretation of results.

### 5. Generic/App-Agnostic Native/Runtime Story (Question 5)

The native/runtime story consistently remains generic and app-agnostic, rather than a RayJoin-specific engine path.
- The terminology used throughout `docs/reports/goal3663_rayjoin_pip_batch_executor_cross_slice_2026-06-06.md` (e.g., "reusable generic prepared point/closed-shape batch count executor") emphasizes the general applicability of the solution.
- The `interpretation` sections within the `summary.json` artifacts describe parameters like `rtdl_pip_batch_request_count` as enabling "reusable generic prepared point/closed-shape count executor" and clarify that features like segment/point reordering are "generic locality probes, not a RayJoin-specific native engine path."
- Both Goal3663 and Goal3602 reports explicitly state that the work "does not authorize: ... app-specific native-engine logic," further solidifying the generic nature of the implementation.

## Validation Command Execution

The validation command for this review was optional. Gemini's local tool session could not execute it. This review is therefore based on file and artifact inspection, supplemented by the Codex-provided focused test result (10 tests OK).
