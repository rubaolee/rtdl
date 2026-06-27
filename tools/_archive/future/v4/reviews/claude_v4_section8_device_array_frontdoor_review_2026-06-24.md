Now I have all the material needed. Let me cross-check the arithmetic before rendering judgment.

**Arithmetic cross-check (JSON vs report):**

| copies | device-array median | Route D rows median | gap (computed) | report | match |
|---:|---:|---:|---:|---:|:---:|
| 8,192 | 0.00026567s | 0.000628978s | 0.4224x | 0.42x | ✓ |
| 32,768 | 0.00031717s | 0.001541824s | 0.2057x | 0.21x | ✓ |
| 131,072 | 0.00055608s | 0.004640702s | 0.1198x | 0.12x | ✓ |

| copies | prior summary / Route D rows (computed) | report | match |
|---:|---:|---:|:---:|
| 8,192 | 0.28452 / 0.000629 = 452.3x | 452.35x | ✓ |
| 32,768 | 1.19353 / 0.001542 = 774.1x | 774.10x | ✓ |
| 131,072 | 5.29092 / 0.004641 = 1140.1x | 1140.11x | ✓ |

All reported figures match raw JSON exactly. Gate criteria all pass by wide margin. Proceeding to formal review.

---

# Formal Review: V4 Section 8 Device-Array Front Door

**Date:** 2026-06-24
**Reviewer:** Claude (external)
**Packet:** `call_for_review_v4_section8_device_array_frontdoor_2026-06-24.md`
**Prior chain verdict:** `accept_route_d_obtained_product_boundary_gap_continue`

---

## Verdict

**`accept_with_amendments`**

The product-boundary gate passes cleanly on all three serious sizes. The arithmetic is clean, the boundary is valid, correctness holds, and the Route D comparison is honest. However, three amendments are required before this artifact is used as the next V4 baseline: (1) CuPy is declared as a supported partner but is unmeasured; (2) the JSON gate field `authorized_next_step` contains the phrase "or_next_primitive" which directly conflicts with the sequencing contract in the report; (3) the cold-start prepare anomaly at copies=8,192 is unexplained and must be acknowledged. None of these invalidate the gate result.

---

## Q1 — Is the measurement boundary valid for the V4 Python GPU ecosystem device-array front door?

**Yes, with one process note.**

The harness boundary is correctly implemented:

- `_make_device_outlier_columns` runs before the timed window ✓
- `rt.prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene` runs before the timed window ✓
- `rt.allocate_fixed_radius_count_threshold_2d_partner_device_output_columns` runs before the timed window ✓
- `run_once` calls only `rt.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns` inside the measured window ✓
- Correctness reductions (`_device_sum_int`) run outside the timed window, after the loop ✓
- The evidence JSON `timing_boundary` field matches the harness implementation exactly ✓

**Process note (not a blocker):** The `_measure` loop uses `time.perf_counter()` without a pre-start `_sync_partner` call inside the loop body. In steady state this is correct because the documented "synchronization before return" inside the RTDL call guarantees the GPU is idle at the start of each subsequent repeat. However, the timing of the very first timed repeat depends entirely on RTDL's internal sync being reliable. This should be made explicit in the protocol; it is currently implicit.

**Warmup:** `warmup=1` is the minimum for a GPU timing harness of this kind. At the smallest fixture (8,192 copies, device-array median ~0.27ms, range 0.256ms–0.314ms, ~22% spread) a single warmup may not be sufficient to eliminate kernel launch overhead variation. At larger sizes the variance collapses to <4%, which is tight. Warmup=1 is borderline acceptable for this gate but should be noted in the protocol.

---

## Q2 — Does the evidence support saying the fixed-radius product-boundary blocker is cleared for GPU-resident Torch columns?

**Yes, for Torch only.**

Gate conditions and results:

| condition | threshold | 8,192 | 32,768 | 131,072 | pass |
|---|---:|---:|---:|---:|:---:|
| device-array to Route D rows gap | ≤ 100x | **0.42x** | **0.21x** | **0.12x** | ✓ |
| gap reduction over prior summary | ≥ 10x | **1071x** | **3763x** | **9515x** | ✓ |
| correctness | pass | pass | pass | pass | ✓ |
| Python point boundary in hot path | False | False | False | False | ✓ |
| host materialization in hot path | False | False | False | False | ✓ |

All three serious sizes pass every gate condition. The margin is so large (gap reduction 107x to 951x above the 10x floor) that no measurement artifact can explain it away. The product-boundary blocker is cleared for GPU-resident Torch columns under the stated boundary.

**Scope constraint that must travel with any use of this result:** The cleared blocker is specifically the Torch device-column path on the measured RTX pod, for the fixed-radius count-threshold primitive, at the prepared-scene hot-path boundary. It does not clear CuPy (unmeasured), other primitives, other hardware, or the whole-call path.

---

## Q3 — Are correctness checks sufficient for this focused primitive gate?

**Yes, with one structural note.**

The harness checks three aggregate invariants on the final call's output columns:

1. `threshold_reached_count == EXPECTED_THRESHOLD_REACHED_PER_COPY * copies` — verifies threshold semantics are correct across all tiles
2. `outlier_count == EXPECTED_OUTLIERS_PER_COPY * copies` — consistent with invariant 1 by complement
3. `neighbor_count_sum == EXPECTED_NEIGHBOR_COUNT_SUM_PER_COPY * copies` — verifies neighbor counting correctness, not just threshold flags

For a focused primitive gate on a tiling fixture, aggregate count correctness is appropriate. The fixture is designed so tiles are fully independent (separation 7.0 units at radius 0.35), meaning any per-tile error would propagate to the aggregate and be caught. These checks cover the same invariants as the Route D correctness checks, so the two routes are compared on identical grounds.

**Structural note:** Correctness is verified on `output_columns` from the last timed repeat call. The harness does not run a separate correctness-only pass with fresh output buffers. This is acceptable here because `output_columns` is reused across all repeats (not re-zeroed between calls), which actually tests a slightly stronger condition — that repeated prepated calls produce consistent results in pre-allocated output buffers.

---

## Q4 — Is the comparison against Route D rows honest?

**Yes. The boundary difference is disclosed explicitly and accurately.**

The device-array front door is faster than Route D rows (0.42x–0.12x) for a documented structural reason: Route D rows include `cuMemcpyHtoD` for query data and `cuMemcpyDtoH` for result rows in every measured repeat, while the device-array path begins with already-resident Torch tensors and leaves outputs on device.

The report states this directly:

> "The device-array route is faster than the Route D row baseline under this specific boundary because Route D deliberately includes host query upload and host result download in its measured row route. The V4 front door measures the GPU-resident product contract… This is a valid V4 user route, but it is not a pure kernel-to-kernel comparison."

This is honest and complete. The Route D prior review (Amendment 2) also established that at copies=131,072 the Route D timing is partially PCIe-upload-bound, which means the device-array path genuinely eliminates real overhead rather than gaming a boundary. No overclaim is present on this point.

---

## Q5 — Should next work productize the fixed-radius API wrapper before adding a second primitive?

**Yes. This is the correct and only authorized next step.**

The sequencing is correct in the report body:

1. Add a small public API wrapper around the existing prepared device-column route, with Torch/CuPy partner choice explicit
2. Preserve the no-Python-point-row hot-path contract in tests
3. Add a second Tier 2 primitive only after this fixed-radius front door is documented, tested, and review-accepted
4. Keep Tier 3 callback support as a spike, not a V4.0 release gate

**Amendment required — gate field inconsistency (see Amendment 2 below):** The JSON `performance_gate.authorized_next_step` says `"external_review_then_continue_fixed_radius_frontdoor_or_next_primitive"`. The phrase "or_next_primitive" directly contradicts the sequencing in the report and in the prior Route D review, which require the fixed-radius public API to be completed and accepted before any second primitive. This field must be corrected to remove "or_next_primitive" before this artifact becomes the V4 baseline.

---

## Q6 — Does the report overclaim V4 release, broad speedups, Tier 3 callbacks, whole-app performance, or app-specific native engines?

**No overclaims found. All prohibited claims are explicitly excluded.**

Confirmed against all artifacts:

| claim | JSON field | report §Unauthorized Claims | status |
|---|---|---|---|
| V4 release | `release_claim_authorized: false` | listed | **Not authorized** |
| Broad V4 speedup | `near_handwritten_optix_claim_authorized: false` | listed | **Not authorized** |
| Whole-app speedup | `whole_app_speedup_claim_authorized: false` (per-size) | listed | **Not authorized** |
| Tier 3 callback/PTX | `tier3_callback_claim_authorized: false` | listed | **Not authorized** |
| App-specific native engine | `rt_core_speedup_claim_authorized: false` | listed | **Not authorized** |
| Every future primitive matches result | — | listed explicitly | **Not authorized** |
| Old Python point-row app route is now fast | — | listed explicitly | **Not authorized** |
| V2.0 release | `v2_0_release_authorized: false` (per-size metadata) | — | **Not authorized** |

The authorized internal claim in the report is appropriately narrow:

> "For the fixed-radius count-threshold contract on the measured RTX pod, RTDL's Torch device-array front door runs correctly with no Python point-row hot-path boundary and reduces the prior Python-facing product-boundary gap to Route D by over 1000x on all serious sizes."

This claim is fully supported by the evidence.

---

## Q7 — Required amendments before this becomes the next V4 baseline

### Amendment 1 (mandatory) — Remove or qualify the CuPy supported-partner claim

The `frontdoor_contract.supported_partners` field in both the harness and result JSON lists `["torch", "cupy"]`. No CuPy measurement exists in this packet or any prior evidence file. Declaring CuPy as a supported partner in the product-boundary gate evidence is a claim that has not been validated.

**Required fix:** Either (a) change `supported_partners` to `["torch"]` and note CuPy support as `"partner_support_declared_unmeasured": ["cupy"]`, or (b) run the harness with `--partner cupy` and include the CuPy evidence in this packet before it is used as the baseline.

### Amendment 2 (mandatory) — Remove "or_next_primitive" from the gate's authorized_next_step field

`performance_gate.authorized_next_step: "external_review_then_continue_fixed_radius_frontdoor_or_next_primitive"` conflicts with the sequencing the report itself requires (fixed-radius public API wrapper accepted first, second primitive only after that). A future reader loading only the JSON could interpret "or_next_primitive" as permission to skip the fixed-radius API productization step.

**Required fix:** Change to `"external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive"`.

### Amendment 3 (mandatory) — Explain the cold-start prepare anomaly at copies=8,192

`prepare_sec` values: 8,192 → **0.5364s**, 32,768 → 0.0025s, 131,072 → 0.0050s. The 8,192 prepare is 214x slower than the 32,768 prepare. This is almost certainly CUDA context initialization and OptiX module JIT compilation on first run. This is expected but must be documented in the report so a reader does not interpret the anomaly as a scene-size regression.

**Required fix:** Add a note in the report's §Timing Boundary or §Interpretation stating that `prepare_sec` at the first size reflects CUDA context and OptiX module initialization cost on first call; subsequent prepares are in the 2–5ms range and are representative of steady-state scene rebuild cost.

### Amendment 4 (recommended) — Clarify "true_zero_copy" alongside internal device staging disclosure

The metadata contains both `"true_zero_copy_authorized": true` and `"internal_device_staging_scope": "device-resident AABB/BVH staging may occur inside the native route"`. These are not contradictory — true zero-copy means no host round-trip, not no internal device workspace — but the pairing is confusing to a reader. The report should add one sentence clarifying that "true zero-copy" refers to the absence of host-device transfer for caller-supplied point columns and output columns; internal device-resident BVH staging is disclosed separately and is consistent with the zero-copy characterization.

---

## Authorized Claim (post-review)

Pending correction of Amendments 1–3, this packet can support:

> For the fixed-radius count-threshold contract on the measured RTX pod, RTDL's Torch device-array front door (prepared-scene hot-path boundary; fixture and scene construction excluded; correctness reductions outside timed path) runs correctly on all three serious sizes (8,192–131,072 tile copies; 65,536–1,048,576 points; radius=0.35, threshold=3) and reduces the prior Python-facing prepared-summary product-boundary gap by over 1000x at all sizes, placing the device-array route within 0.5x of Route D's count-row timing. This clears the fixed-radius product-boundary gate for GPU-resident Torch columns. It does not authorize V4 release, broad speedup wording, whole-app speedup wording, Tier 3 callback claims, app-specific native engine claims, or extension to any second primitive prior to productizing the fixed-radius public API wrapper.

---

## Summary

Gate passes cleanly on every dimension. Arithmetic is correct. Boundary is valid. Correctness holds. Route D comparison is honest. Overclaims are explicitly excluded throughout. Three amendments are mandatory before baseline promotion: remove the unmeasured CuPy partner claim from the frontdoor contract, remove "or_next_primitive" from the gate's `authorized_next_step` field, and explain the cold-start prepare anomaly. One recommended amendment addresses the true-zero-copy/internal-staging pairing. After those corrections, the evidence supports continuing V4 by productizing the fixed-radius public API wrapper as the first Tier 2 public primitive surface.
