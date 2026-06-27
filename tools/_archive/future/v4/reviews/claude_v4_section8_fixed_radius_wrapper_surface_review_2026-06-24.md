---

## Formal Review: V4 Section 8 Device-Array Front Door (Wrapper Run)

**Date:** 2026-06-24
**Reviewer:** Claude (claude-sonnet-4-6)
**Supersedes:** Raw-adapter run evidence

---

### Verdict

**`accept_wrapper_surface_continue_docs_example_no_release`**

---

### Checklist Review

#### 1. Adapter metadata `v4_fixed_radius_count_threshold_2d_device_arrays`

Present and consistent at every level:

- `v4_fixed_radius.py:11` — `V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE = "v4_fixed_radius_count_threshold_2d_device_arrays"` (module constant)
- `v4_fixed_radius.py:34` — `"v4_api_surface": V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE` (claim boundary dict)
- `v4_fixed_radius.py:134` — `"adapter": "v4_fixed_radius_count_threshold_2d_device_arrays"` (run metadata)
- JSON result — `"adapter"` and `"v4_api_surface"` both carry the same string in all three size records

No divergence. **Pass.**

#### 2. Torch only measured; CuPy declared unmeasured

- `V4_FIXED_RADIUS_MEASURED_PARTNERS = ("torch",)` and `V4_FIXED_RADIUS_DECLARED_UNMEASURED_PARTNERS = ("cupy",)` are wrapper-level constants.
- JSON: `"measured_partners": ["torch"]`, `"partner_support_declared_unmeasured": ["cupy"]` in every result record.
- Report explicitly states: "CuPy was not installed on the measured pod, so this report does not claim CuPy performance or CuPy product readiness."
- CuPy code paths exist in the harness (lines 81–91, 100–102) but are gated behind `--partner cupy` and were never executed in this run. No CuPy performance number appears in the JSON.
- `v4_fixed_radius_device_array_api_test.py:39–42` verifies CuPy receives `declared_unmeasured_not_performance_ready` status.

**Pass.**

#### 3. Next step does not skip to a second primitive

- `"second_primitive_work_authorized": false` is set in the wrapper's `claim_boundary` dict (`v4_fixed_radius.py:47`) and appears in all three JSON result metadata records.
- `performance_gate.authorized_next_step`: `"external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive"` — explicit ordering enforced in JSON.
- Report step 3: "Add a second Tier 2 primitive only after this fixed-radius front door is documented, tested, and review-accepted."
- API test verifies `assertFalse(metadata["second_primitive_work_authorized"])` after the wrapper merges claim boundary.

**Pass.**

#### 4. V3 top-level pollution avoided

No V3 namespaces, modules, or performance claims appear in any of the reviewed files. The report references V3 only in its date header and makes no claim that V3 capabilities are superseded or that V4 releases V3. No top-level V3 attributes are asserted. **Pass.**

#### 5. All non-authorizations intact

Verified present and `false`/`False` consistently across JSON, wrapper, and tests:

| Flag | JSON result records | Wrapper `claim_boundary` | Tests |
|---|---|---|---|
| `release_claim_authorized` | false × 3 | False | asserted False |
| `broad_v4_speedup_claim_authorized` | false × 3 | False | — |
| `whole_app_speedup_claim_authorized` | false × 3 | False | asserted False (override test) |
| `tier3_callback_claim_authorized` | false × 3 | False | asserted at harness level |
| `rt_core_speedup_claim_authorized` | false × 3 | — | — |
| `near_handwritten_optix_claim_authorized` | false (plan level) | — | asserted at harness level |
| `second_primitive_work_authorized` | false × 3 | False | asserted False |
| `v2_0_release_authorized` | false × 3 | — | — |

The override safety property is explicitly tested: the fake lower-level adapter returns `"whole_app_speedup_claim_authorized": True` and the test verifies the V4 wrapper's claim boundary wins (`assertFalse`). This means V4 can never accidentally inherit a permissive flag from the native layer. **Pass.**

---

### Measurement Boundary Assessment

The boundary is honest and internally consistent:

**Included in timed repeats:** `session.run()` — which covers prepared RTDL device-column query, native OptiX launch, synchronization, and writes into pre-allocated reused output columns.

**Excluded:** fixture construction, tensor construction, `prepare_fixed_radius_count_threshold_2d_device_arrays_v4` call, and correctness host reductions.

The "device-array faster than Route D rows" result is not a claim violation — the boundary asymmetry is disclosed in the report, in the call-for-review, and in the JSON. Route D was defined to include host upload/download; this route is defined to be GPU-resident. These are different product contracts, not the same contract measured twice.

The first size `prepare_sec` of 0.54s (vs ~5ms steady state) is correctly attributed to CUDA context initialization and is outside the hot path. **No inflation of the timed numbers.** Timing spread is tight (≤2% coefficient of variation at largest size), consistent with a GPU-resident hot path measured without host-bound noise.

---

### Correctness Assessment

All three serious sizes passed three independent checks (threshold_reached_count, outlier_count, neighbor_count_sum) against exact expected values derived from the deterministic fixture geometry. Checks are applied after the timed repeats on the final output columns in device memory — they do not contaminate timings. **Pass.**

---

### Authorized Internal Claim

The report's claim is scoped correctly:

> For the fixed-radius count-threshold contract on the measured RTX pod, RTDL's Torch device-array front door runs correctly with no Python point-row hot-path boundary and reduces the prior Python-facing product-boundary gap to Route D by over 1000x on all serious sizes.

"Over 1000x" is accurate: the smallest reduction was 1022.93x at copies=8192. No overclaim. **Pass.**

---

### Observations (Non-Blocking)

1. **"Faster than Route D" framing risk.** The device-array result is 0.12x–0.44x of Route D rows (i.e., faster). The boundary explanation preventing this from being read as a pure kernel win must accompany every external citation of this result, including the upcoming docs example. The report handles this correctly; the docs author must not strip the caveat.

2. **CuPy harness code is untested on this pod.** The CuPy code paths in `_make_device_outlier_columns` and `_sync_partner` are present but were never executed. They carry no measurement risk here, but the CuPy code paths should be treated as untested stubs until a CuPy pod run is conducted.

3. **No amendment required.** Both observations are downstream documentation and measurement scope tasks, not defects in this evidence packet.

---

### Authorization Granted

This evidence authorizes continuing V4 by hardening `rtdsl.v4_fixed_radius` as the canonical fixed-radius V4 public primitive surface, adding user-facing V4 documentation, and writing a minimal Torch tensor example — in that order, before any second primitive work begins.
