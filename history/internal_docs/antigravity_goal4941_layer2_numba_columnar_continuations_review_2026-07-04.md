# Goal4941 Technical Review: Layer 2 Numba Columnar Continuations

Date: 2026-07-04

## Verdict Label
**`approve_goal4941_layer2_generic_numba_continuations`**

***

## Findings & Answers to Review Questions

### 1. Did Goal4941 correctly reuse the existing v2.5 Numba partner-continuation mechanism rather than creating a parallel partner API?
Yes. Goal4941 correctly integrated the new operations into the existing v2.5 partner-continuation architecture:
* It registered the new operations (`adjacent_midpoint_candidates_i64x2_by_key`, `consecutive_dedupe_mask_f64x2`, and `range_has_sorted_values_i64`) directly inside the `V2_5_PARTNER_CONTINUATION_OPERATIONS` schema in [partner_continuation_protocol.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_continuation_protocol.py#L138-L164).
* It mapped them to the Numba partner fallback path by adding them to `V2_5_NUMBA_PREVIEW_OPERATIONS` (in [partner_continuation_protocol.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_continuation_protocol.py#L288-L290)).
* It implemented standard Numba partner descriptors (e.g. `describe_numba_adjacent_midpoint_candidates_i64x2_by_key`) and runners (e.g. `run_numba_adjacent_midpoint_candidates_i64x2_by_key`) inside [numba_partner_continuation.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/numba_partner_continuation.py).
* No duplicate hooks, parallel APIs, or bypass paths were created. All new entrypoints are exposed via standard package-level imports in [__init__.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/__init__.py).

### 2. Are the three operations app-neutral, or do they smuggle RayJoin/overlay semantics into RTDL core?
They are completely app-neutral. The operations are defined purely in terms of typed columns and mathematical array manipulations, completely free of application-layer vocabulary:
* `adjacent_midpoint_candidates_i64x2_by_key`: Computes integer-truncating midpoints for adjacent rows that share the same int64 key.
* `consecutive_dedupe_mask_f64x2`: Filters out consecutive exact float64 coordinate pairs.
* `range_has_sorted_values_i64`: Uses binary search to check if a sorted int64 array intersects a set of half-open ranges.
* The test `test_operations_are_registered_as_numba_preview_without_rayjoin_identity` in [goal4941_layer2_numba_columnar_continuations_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal4941_layer2_numba_columnar_continuations_test.py#L49-L72) programmatically checks [numba_partner_continuation.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/numba_partner_continuation.py) to assert that terms like `rayjoin`, `overlay`, and `polygon` do not exist in the source code.
* No geometry, face, boundary, chain, or polygon concepts are smuggled into the RTDL core package.

### 3. Does the history audit correctly identify that similar app-layer helpers existed before, especially Goal4897/4899, and that Goal4941 promotes only the generic numeric shape?
Yes. The Historical Reuse Audit in the completion report correctly notes:
* RayJoin-specific app-layer JIT helpers existed previously in Goal4897 and Goal4899.
* Previous milestones (Goal4930, Goal4939, Goal4940) identified output assembly as a dominant Python writer bottleneck, and proved that continuing Layer 3 host-columnar Python micro-patches is not viable.
* Goal4941 extracts these helper concepts and promotes only their generic, math-neutral, numeric shapes to the RTDL core Layer 2 interface, keeping RayJoin mapping purely as a downstream consumer of these generic operations.

### 4. Does the POD evidence prove real CUDA execution for the new operations?
Yes. The smoke-test artifact [layer2_numba_continuations_smoke.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4941_pod_artifacts/layer2_numba_continuations_smoke.json) shows:
* `numba_cuda_available: true` is verified.
* Execution ran successfully on a physical NVIDIA RTX 4000 Ada Generation GPU.
* The operations processed a scale of 1,000,000 rows (250,000 ranges) and recorded real timings (midpoint: 0.251s, dedupe: 0.045s, range check: 0.058s).
* The record explicitly confirms `host_column_materialization_used: false` for all three operations, proving that the arrays remained resident on the CUDA device and executed entirely on the GPU without intermediate host-to-device transfers.

### 5. Is it correct that no RayJoin speedup or public performance claim is authorized by this goal?
Yes. This is correct and is strictly enforced:
* The completion report verdict is `completed_layer2_generic_numba_columnar_continuations__no_speedup_claim`.
* The core protocol contract constants (`V2_5_PERFORMANCE_PATH_AUTHORIZED = False` and `V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False`) in [partner_continuation_protocol.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_continuation_protocol.py#L39-L44) remain `False`.
* `plan_v2_5_partner_support` returns `public_speedup_claim_authorized = False` and `true_zero_copy_claim_authorized = False` for all three operations.
* All timings are treated as capability verification metrics, not public performance speedup claims.

### 6. Is the stated next step correct: Layer 1 device-column row-buffer carrier before claiming hot-path speedup?
Yes. The next step is correct:
* Even though these JIT kernels execute efficiently on GPU device arrays, the RTDL primitive producers (LSI/PIP) do not currently emit columns directly into device-resident memory.
* If a client application has to upload host-side NumPy arrays to device memory just to invoke these operations, the PCIe transfer overhead is likely to erase any performance benefit.
* Implementing a generic Layer 1 device-column row-buffer carrier (e.g. `Goal4942`) is the necessary bridge to keep the entire execution pipeline on-device. Without it, these operations are useful capabilities, but do not yield an end-to-end hot-path speedup.

***

## Non-Authorization Boundaries (Preserved)

This review strictly enforces the following non-authorization boundaries:
1. **RayJoin Speedup Claims:** No end-to-end, hot-path, or public performance speedup claims are authorized.
2. **Release and Versioning Claims:** No V3/V4 public release claims or release tags are authorized.
3. **App-Local Device Resident Proving:** Treating app-local array upload/download as proof of a device-resident hot path is prohibited.
4. **Smuggling App Semantics:** Adding RayJoin output-chain, polygon-geometry, or overlay semantics to the RTDL core is prohibited.
5. **Layer 3 Patches:** Continuing Python host-columnar writer micro-patches at Layer 3 remains halted.
