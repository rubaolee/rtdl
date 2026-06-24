# Phoenix V3 M43 Grouped Reduction Technical Review

**Date:** 2026-06-23  
**Verdict:** `accept_m43_original_shape_hot_gate_cleared_continue_step2`  

## Executive Summary
This document provides a critical external technical review of the Phoenix V3 M43 grouped-reduction CuPy Warp Prepared Runner work. The review evaluates the local-only grouped-reduction fix implemented in M43 after the M42 diagnostics showed Numba offset kernel limitations.

---

### Questions and Explicit Answers

#### 1. Is M43 generic runtime work rather than app-specific tuning?
**Yes.** The improvements introduced in M43 are generic to the runtime trunk and are not tuned or hardcoded for app-specific shapes:
- **Numba Auto Strategy Selection:** The selection between `thread_per_group_serial` and `warp_per_group_tiled` strategies is decided dynamically based on the structure of the incoming shape (specifically, the group count and rows-per-group metrics).
- **CuPy Prepared Session Integration:** The support for `partner='cupy'` is implemented generic to the columnar interfaces inside `prepare_grouped_vector_sum_2d_partner_columns_session` and `run_grouped_vector_sum_2d_prepared_session`.
- **CuPy RawKernel Strategy:** The CuPy RawKernel dynamically selects the `warp_per_group_tiled` route based on a threshold (`rows_per_group_mean >= 32`).

#### 2. Does the CuPy prepared-session route preserve explicit partner choice and claim boundaries?
**Yes.** The implementation requires explicit partner specification (`partner='cupy'`). The claim boundaries are strictly preserved and enforced in both the metadata dictionary returned by the session runner and the JSON evidence files (`summary.json`). Specifically, the metadata and summaries restrict the scope to Step-2 local harness evidence and explicitly assert that release, paid-POD spend, public speedup wording, and broad V3-over-V2 claims are not authorized.

#### 3. Does the original blocked shape (`262144` rows x `1024` groups) now clear the CPU-hot inversion gate?
**Yes.** The original blocked shape fails to clear the CPU-hot inversion gate under the Numba tiled strategies (resulting in speedups of `0.62x` and `0.67x` relative to CPU control). However, under the productized CuPy RawKernel warp prepared runner, the CPU-hot inversion gate is successfully cleared:
- **CuPy Prepared Runner (Original):** `3.454x` speedup over CPU-hot.
- **CuPy Prepared Runner (Trusted Offsets):** `3.634x` speedup over CPU-hot.

#### 4. Does the trusted-offset follow-up fairly identify the runner-vs-legacy-wall regression as row-offset validation overhead, and is explicit --trust-row-offsets acceptable as a prevalidated-data mode?
**Yes.** 
- **Identification:** In the first CuPy prepared run, inclusive wall time was dominated by the prepare step (`prepare_sec = 0.0858s`), which caused the runner to run at `0.8786x` of the legacy CuPy one-shot wall time. The investigation correctly traced this to the prepared-session branch ignoring the `validate_row_offsets` flag and performing a synchronous host-device check at prepare time.
- **Acceptability:** The introduction of the explicit `--trust-row-offsets` flag is acceptable as a prevalidated-data mode. Because it is explicitly passed by the caller, it ensures that offset validation is only bypassed for caller/generated data that has already been validated, rather than introducing unsafe implicit or automatic bypasses. Under this mode, the wall time caveat is resolved, delivering a speedup of `15.409x` over legacy wall time.

#### 5. Are launch metadata fields sufficient for future review?
**Yes.** The launch metadata fields recorded through the runner—including `partner`, `kernel_strategy`, `program_count`, `groups_per_block`, `threads_per_group`, `rows_per_group_mean`, and residency/materialization flags—are comprehensive and capture all essential parameters. This provides sufficient detail for future performance auditing and validation.

#### 6. Does the report correctly avoid release, all-app, paid POD, public speedup, broad V3-over-V2, V4, embedding, C ABI, and true-zero-copy authorization?
**Yes.** The report and its corresponding JSON evidence files strictly avoid any such authorizations. They include explicit non-authorization clauses to preserve these boundaries:
- `release_authorized: false`
- `all_app_pod_spend_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_v3_faster_than_v2_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`
- `v4_work_authorized: false`
- `embedding_work_authorized: false`
- `c_abi_work_authorized: false`

#### 7. What exact next step is authorized: Step-2 grouped-reduction closure, local wall-followup, another family, or no-go?
The authorized next step is **Step-2 grouped-reduction closure and continuation to Step 2 review**. No further local wall-followup is required since the trusted-offset follow-up has already been executed and verified. No paid POD spend or V3 release is authorized at this stage.

---

### Non-Authorization Boundaries
As a critical boundary of this Step-2 technical review, the following actions are explicitly **NOT** authorized:
- V3 release
- All-app benchmarking runs
- Paid POD spend
- Public speedup wording
- Broad V3-over-V2 claims
- V4 work
- Embedding integration
- C ABI implementation
- True zero-copy claims
