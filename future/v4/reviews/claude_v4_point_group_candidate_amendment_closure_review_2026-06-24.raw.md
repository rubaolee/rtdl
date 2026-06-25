I now have all the information needed. Here is the external review.

---

## External Review: Point-Group Nearest-Witness Candidate Amendment Closure

**Reviewer:** Claude Sonnet 4.6 (external)  
**Date:** 2026-06-24  
**Subject:** `v4_point_group_nearest_witness_2d_device_arrays` — Amendment Closure

---

## Verdict

**`accept_amendments_closed_continue_to_promotion_decision`**

All three required amendments are verifiably closed for this candidate path. The evidence and code are mutually consistent. No blocking finding was identified.

---

## Explicit Answers to the Five Questions

### Q1: Are A1, A2, and A3 actually closed for the point-group candidate?

**Yes, all three are closed.**

**A1 — Sub-field naming:**  
`optix_runtime.py:9821–9823` (hot path) and `9753–9755` (empty-shortcut path) both emit:
```python
"query_point_columns_direct_device_read_confirmed": True,
"output_columns_direct_device_write_confirmed": True,
"true_zero_copy_authorized": False,
```
Neither occurrence uses the old `query_point_columns_true_zero_copy_authorized` or `output_columns_true_zero_copy_authorized` field names. The evidence JSON confirms both fields appear in the POD repeat gate output and the include-candidates catalog gate output exactly as expected.

**A2 — Partner classification:**  
`v4_point_group.py:13,14` defines:
```python
V4_POINT_GROUP_POD_CANDIDATE_PARTNERS = ("torch",)
V4_POINT_GROUP_DECLARED_UNMEASURED_PARTNERS = ("cupy",)
```
The claim-boundary function at line 39–42 returns `measured_partners: ()`, `pod_candidate_partners: ("torch",)`, `partner_support_declared_unmeasured: ("cupy",)`. The evidence JSON confirms `"measured_partner": false`, `"pod_candidate_partners": ["torch"]`, `"partner_support_declared_unmeasured": ["cupy"]`.

`v4_operator_catalog.py:48–57` shows the candidate entry correctly has `"measured_partners": ()` and `"pod_candidate_partners": ("torch",)` — Torch is not in the measured set.

**A3 — Non-trivial fixture:**  
`scripts/v4_point_group_nearest_witness_device_outputs_validation.py:62–119` applies `pattern = torch.remainder(ids_i64, 4)` to construct four interleaved row types in equal counts:
- `pattern == 0`: exact match (distance 0.0)
- `pattern == 1`: positive-offset nonzero (query x += 0.30)
- `pattern == 2`: no-hit (query y = 10.0, outside radius 0.5) — expected `neighbor_id: 0xFFFFFFFF`, `distance: float32_max`
- `pattern == 3`: negative-offset nonzero (query x -= 0.25)

The evidence JSON `fixture_shape` at both sizes shows equal counts (8192 each at 32K, 32768 each at 131K). `parity.passed: true` at both sizes with `neighbor_ids_match: true`, `distances_match: true`. The row sample confirms the interleaved sentinel pattern is present. **A3 is closed.**

---

### Q2: Are remaining `*_true_zero_copy_authorized` fields outside this candidate path a blocker?

**No — separate wording debt, not a blocker here.**

The following occurrences of `output_columns_true_zero_copy_authorized: True` remain in `optix_runtime.py`:
- Lines 7737, 7842: `PreparedOptixFixedRadiusCountThreshold3D` methods
- Lines 8427–8428, 8519–8520, 8600, 8869, 9126–9127: grouped-union operation methods

None of these code paths are reachable from `write_device_nearest_witness_columns_from_device_query_columns`. They are on entirely different classes with different measured-surface statuses. These are wording-debt items for those surfaces' own promotion reviews, not a defect in the point-group candidate closure.

One instance in the catalog regression gate JSON (the fixed-radius example `native_metadata` at lines 58–61) also uses `query_point_columns_true_zero_copy_authorized: true` — that surface has a top-level `"true_zero_copy_authorized": true` which makes the sub-field consistent, not misleading.

---

### Q3: Does the mixed fixture sufficiently exercise no-hit and nonzero-distance correctness for this candidate's scope?

**Yes, for the current promotion-review scope.**

The fixture explicitly verifies:
- The `0xFFFFFFFF` no-hit sentinel ID is produced for rows where the query is outside the search radius (y=10.0, radius=0.5)
- `float32_max` (`3.4028234663852886e+38`) is produced as the no-hit distance
- Nonzero distances (≈0.30 positive, 0.25 negative) are produced and verified with `allclose(rtol=1e-5, atol=1e-5)`
- Exact matches (distance 0.0) are verified with `equal()`

The parity check (`_check_device_parity`) compares device output columns against expected tensors computed on the same device. The legacy-row parity check (`_check_legacy_rows`) independently verifies the same values through the host-row route, providing a cross-check.

The fixture is adequate for a candidate POD gate. It does not need to cover edge cases like empty groups or overflow pages at this stage, and that scope limitation is honestly disclosed (`candidate_status` field throughout).

---

### Q4: Is the same-contract ratio wording honest?

**Yes.**

Both timings call the same underlying prepared native structure (`rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns` for the device path; `nearest_witness_rows` for the legacy path) on the same fixture with the same prepared search data. The measurement explicitly isolates the cost of host query-row materialization and host result-row download that the legacy path incurs but the device path avoids.

The ratio grows from 663x at 32K to 1868x at 131K, consistent with a host-materialization cost that is super-linear (Python dict construction per row) vs. a device path where the native kernel time dominates at both sizes (native median ~105–141 µs vs. end-to-end Python-layer median ~507–529 µs).

The metadata discloses the comparison scope precisely:
- `measured_partner: false` — Torch is only a candidate partner
- `release_claim_authorized: false`
- `broad_v4_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `public_speedup_claim_authorized: false`

The call-for-review document reinforces: "It does not authorize broad V4 speedup wording, whole-application speedup wording, or release promotion." The ratio wording is honest.

---

### Q5: Does acceptance authorize measured-catalog promotion?

**No — and this review explicitly does not authorize it either.**

The closure document states: "candidate still requires external closure review before any promotion decision." The call-for-review states: "This packet asks only whether the required amendments are closed. It does not request release authorization or measured-catalog promotion." Acceptance of this closure only permits proceeding to a separate promotion-decision review requiring external consensus. No shortcut to catalog membership is implied or authorized.

---

## Findings by Severity

### INFO — No Action Required

**I-1: `output_columns_true_zero_copy_authorized: True` on grouped-union and fixed-radius 3D surfaces**  
Lines `optix_runtime.py:7737, 7842, 8427–8428, 8519–8520, 8600, 8869, 9126–9127` retain the old sub-field naming with `true_zero_copy_authorized: False` at the top level. These are on non-candidate paths; they are wording inconsistencies on other surfaces that should be resolved in those surfaces' own promotion reviews. They do not affect the point-group candidate closure.

**I-2: Python-layer claim boundary does not enumerate `direct_device_*` sub-fields**  
`v4_point_group.py:34–58` returns a claim-boundary dict that omits `query_point_columns_direct_device_read_confirmed` and `output_columns_direct_device_write_confirmed`. Those fields originate from the native-layer `write_device_nearest_witness_columns_from_device_query_columns` result and are merged at `V4PointGroupNearestWitness2DDeviceArraySession.run()`. The merged metadata in the evidence confirms the fields are present. This is an acceptable architecture given how the layers compose, but a future hardening pass could echo these fields through the Python boundary explicitly.

**I-3: No-hit geometry only tested via y-offset in a planar (y=0) structure**  
The fixture places no-hit queries at y=10.0 against a planar search set at y=0 with radius=0.5. This is a correct and simple geometric no-hit proof, but it tests a single axis of the 2D geometry. For a candidate gate this is acceptable; a full pre-release coverage review should include no-hit rows from non-axis misses.

### LOW — Wording Debt (Not Blocking)

**L-1: `measured_partner: false` with `direct_device_handoff_authorized: true` could be misread**  
The metadata simultaneously records `measured_partner: false` and `direct_device_handoff_authorized: true`. The interpretation is correct (handoff is technically proven but Torch is not yet a measured/released partner), but the coexistence of these fields could mislead readers into inferring release-readiness. This is mitigated by the explicit `partner_claim_status: "candidate_pod_repeat_gate_passed_requires_external_review_before_release_scope"` field. Worth addressing before any catalog promotion language is drafted.

---

## Non-Authorization Block

This review:

- **Does not authorize V4 release** of any surface
- **Does not authorize measured-catalog promotion** of `v4_point_group_nearest_witness_2d_device_arrays`; that requires a separate external consensus decision
- **Does not authorize broad V4 speedup wording** or whole-application speedup wording
- **Does not authorize true-zero-copy public wording** on this or any other surface; the `true_zero_copy_authorized: false` boundary stands
- **Does not authorize CuPy performance claims**; CuPy remains `partner_support_declared_unmeasured`
- **Does not authorize Tier-3 callback/PTX support**
- **Does not authorize embedding/C-ABI, non-Python host bindings, or app-specific native kernels**
- **Does not authorize release of any other V4 candidate surface** under review concurrently

---

## Summary

The three required amendments (A1: field-name rename on the candidate path; A2: explicit Torch/CuPy partner separation; A3: non-trivial fixture with no-hit and nonzero-distance rows) are all verifiably closed in code and confirmed by evidence. Remaining `*_true_zero_copy_authorized` sub-fields elsewhere in the codebase are wording debt on separate surfaces and are not a blocker here. The fixture is sufficient for the current candidate scope. The same-contract ratio is honestly disclosed. Acceptance authorizes proceeding to a separate measured-catalog promotion decision — nothing further.
