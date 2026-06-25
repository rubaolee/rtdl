I now have enough information to write the full review. Let me compile my findings.

---

## External Review: V4 Primitive Grouped-I64 Tier-2 Candidate
**Reviewer**: External (Claude Sonnet 4.6)
**Date**: 2026-06-24
**Candidate surface**: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
**Source primitive**: `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`

---

## Verdict

**`accept_with_required_amendments_before_catalog_decision`**

The candidate is a well-formed generic Tier-2 operator, the POD evidence is credible, and claim boundaries are structurally sound. The surface is correctly held outside the measured catalog. However, four code-level amendments must be completed before a catalog-promotion decision can be validly made: (1) the GPU-mode regression gate must include the candidate; (2) the measured-partner status must be updated in both the catalog and claim-boundary code; (3) OptiX 9.1 ABI status must be formally addressed; and (4) the frontdoor quickstart surface count must update from 3 to 4.

---

## Findings By Severity

### REQUIRED (block catalog promotion until resolved)

**R1 — Candidate is absent from GPU-mode catalog regression gate**
`scripts/v4_catalog_regression_gate.py:144–155` explicitly bars the candidate in GPU mode:
```python
elif name == "primitive_grouped_i64_reduction_candidate":
    if mode != "dry-run":
        failures.append("candidate_not_allowed_in_gpu_release_catalog_gate")
```
The three measured surfaces go through an RTX GPU-mode gate (`_example_commands`, mode=`gpu`). The grouped-i64 candidate is only exercised in dry-run. For catalog promotion, it must be added to the GPU-mode gate command list and the `_validate_payload` branch updated to accept it as a measured surface (not a candidate). Until that change ships and passes, no valid promotion decision can be made.

**R2 — `measured_partners` stays `()` in catalog code; Torch must be promoted when candidate is promoted**
`v4_operator_catalog.py:42` and `v4_ray_triangle.py:108` correctly leave `measured_partners=()` for the candidate status. But when the promotion decision is made, both files must be updated atomically:
- `V4_TIER2_CANDIDATE_OPERATOR_SURFACES[V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION]` → move to `V4_TIER2_OPERATOR_SURFACES` with `measured_partners=("torch",)`
- `primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4` must mirror the pattern used by `closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4` (i.e., Torch moves to measured, CuPy stays declared-unmeasured, `partner_claim_status` changes from `"pod_measured_candidate_external_review_required"` to `"measured_on_v4_section8_pod"`)
- The planner branch for the candidate (`V4_TIER2_CANDIDATE_OPERATOR_SURFACES`) must be removed and replaced by the standard `V4_TIER2_OPERATOR_SURFACES` branch so `plan.status` returns `"tier2_measured_ready"` for Torch

**R3 — OptiX 9.1 ABI was not tested; scope must be formally stated before promotion**
The POD evidence (`v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md`, line 24–25) discloses that OptiX 9.1 was rejected on driver 570.195.03 and OptiX 8.0 was used instead. For an operator that is promoted to the measured catalog, the maximum-validated OptiX ABI must be an explicit scope statement in the promotion-decision packet. Either (a) re-run on a machine that accepts OptiX 9.1, or (b) document the 8.0 maximum as a hard scope boundary and carry it into the catalog entry.

**R4 — Quickstart surface count assertion must update from 3 to 4 on promotion**
`scripts/v4_catalog_regression_gate.py:161–163` and `tests/v4_catalog_regression_gate_test.py:62` assert `measured_surface_count == 3`. When the candidate is promoted, both must be updated to 4. Because the test runs in CI, this will fail on the promotion PR if forgotten — but it must be listed as a required amendment because the test currently asserts the catalog has exactly 3 surfaces, not 4.

---

### ADVISORY (must be documented in the promotion packet, not blocking candidate acceptance)

**A1 — Group-width coverage is narrow**
Both the local gate and the POD gate used `group_width=16` exclusively (`v4_primitive_grouped_i64_device_outputs_validation.py:22`). No variation was tested. For a measured catalog surface, the promotion packet should either (a) test multiple group widths (e.g., 1, 16, 256), or (b) explicitly state that `group_width=16` is the validated configuration and other widths remain uncovered.

**A2 — Resource leak risk if `primitive_payload` prepare raises after `ray_batch` succeeds**
`v4_ray_triangle.py:555–563`:
```python
prepared_scene = prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns)
try:
    ray_batch = prepared_scene.prepare_ray_batch_device_columns(ray_columns)
    primitive_payload = prepare_optix_primitive_grouped_i64_payload_3d(...)
except Exception:
    prepared_scene.close()
    raise
```
If `ray_batch` succeeds but `primitive_payload` raises, `prepared_scene.close()` is called but `ray_batch._handle` is not explicitly closed. The same pattern appears in the `closest_hit` front door (`v4_ray_triangle.py:499–516`), making this a pre-existing pattern issue rather than a new regression. Whether `prepared_scene.close()` transitively frees all associated ray batch C handles needs confirming before promotion. As-is, this is a latent leak, not a correctness issue in the hot path.

**A3 — Single GPU family in POD evidence**
All RTX A5000 POD evidence was collected from a single hostname (`0256b71980f1`). This is the same limitation as the other three measured surfaces' evidence. For catalog promotion, explicitly note that the RTX A5000 (Ampere) is the sole validated RT-core family; other architectures (Turing, Ada) are unvalidated.

**A4 — `partner_support_declared_unmeasured` includes Torch in a way that may confuse the catalog**
`v4_ray_triangle.py:108–112` lists both `torch` and `cupy` in `partner_support_declared_unmeasured` for all requests against this candidate surface. This is technically correct (Torch is not a *measured catalog* partner yet) but creates an apparent contradiction: the POD evidence uses Torch, yet Torch is listed as declared-unmeasured. A comment on lines 108–112 explaining this is a candidate-status artifact would prevent future confusion.

---

### INFORMATIONAL (out of scope; note for follow-up)

**I1 — Any-hit test asserts `true_zero_copy_authorized: True` in fake scene**
`tests/v4_ray_triangle_device_array_api_test.py:123` — the `_FakeAnyHitScene` returns `true_zero_copy_authorized: True`, and the test asserts this. The any-hit surface documentation (`ray_triangle_device_array_frontdoor.md:182–188`) explicitly disclaims a true-zero-copy public claim for grouped-argmin but does not repeat this for any-hit. If the any-hit real runtime path also returns `true_zero_copy_authorized: True`, the claim boundary for that surface must be explicitly audited before V4 release. This is outside the scope of the current grouped-i64 review.

---

## Answers to the Five Review Questions

**Q1. Is this truly a V4 Tier-2 generic operator candidate, not an app-specific kernel?**

Yes. The operator name, native symbol, and catalog classification are all app-name-free. The native symbol `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs` describes the operation (static triangle scene, prepared ray batch, prepared i64 payload, device outputs) without any app identity. The inventory (`v2_primitives_to_v4_tier2_inventory_2026-06-24.md:23–32`) states the architectural rule explicitly: the operator must be app-name-free, which it is. The primitive is explicitly listed as a generic continuation operator alongside count-threshold, argmin, and any-hit in the V4 catalog design. No Barnes-Hut, DBSCAN, RayDB, or join language appears in any surface code. The operator catalog planner routes this via `continuation_class: "grouped_i64_reduction"` — a generic class, not an app shape. **Finding: passes Tier-2 generic boundary test.**

**Q2. Is it correct to keep it outside the measured V4.0 release catalog until review and release decision, even though POD evidence now exists?**

Yes, and the implementation enforces this correctly at multiple layers:
- `v4_operator_catalog.py:37–46` keeps it in `V4_TIER2_CANDIDATE_OPERATOR_SURFACES`, not `V4_TIER2_OPERATOR_SURFACES`
- The planner returns `tier2_fused_operator_candidate` (not `tier2_measured_ready`) for this surface, meaning no caller will receive a `measured_ready` routing signal
- `v4_catalog_regression_gate.py:150–155` bars it from GPU-mode gate runs
- `v4_catalog_regression_gate_test.py:62` asserts that the frontdoor quickstart reports exactly 3 measured surfaces
- The JSON evidence records `candidate_status: "candidate_measured_requires_external_review_before_release_scope"` and `release_claim_authorized: false` throughout
- This external review is itself one of the gates

POD evidence alone is not promotion. This packet correctly names the missing gates (external review, release decision) before the candidate can enter the measured catalog. **Finding: the exclusion from the measured catalog is correctly enforced in code, not just in documentation.**

**Q3. Are the claim boundaries strong enough around no broad speedup, no whole-app claim, no true-zero-copy, no Tier-3 callback, and payload prepared once/not direct per-run caller payload?**

Largely yes, with one annotation gap:

- **No broad speedup**: `broad_v4_speedup_claim_authorized: false` is present at every layer (claim boundary function, session metadata, native call result, JSON evidence, catalog entry). The evidence JSON `interpretation` field reads "candidate gate only; this same-contract comparison does not authorize V4 public performance claims, whole-app claims, or release promotion." The comparison is correctly framed as same-contract (same prepared primitive, different output route).
- **No whole-app claim**: `whole_app_speedup_claim_authorized: false` throughout.
- **No true-zero-copy**: `true_zero_copy_authorized: false` and `ray_columns_true_zero_copy_authorized: false` in the transfer metadata at `optix_runtime.py:23430`. The claim boundary function does not include a `true_zero_copy` key at all, which is correct — absence of the claim is cleaner than a `false` entry.
- **No Tier-3 callback**: `tier3_callback_claim_authorized: false` throughout. The planner correctly routes Tier-3 scalar callbacks to spike-only status and action-shaped callbacks to rejected status, independent of this surface.
- **Payload prepared once**: `primitive_payload_prepare_is_hot_path: false`, `primitive_group_ids_uploaded_each_run: false`, `primitive_values_uploaded_each_run: false`, `prepared_primitive_payload_used: true` in evidence. The Python session class (`V4PrimitiveGroupedI64Reduction3DDeviceArraySession`) separates `prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4()` (which calls `prepare_optix_primitive_grouped_i64_payload_3d()` once) from `session.run()`. The payload handle is reused across hot runs.

**Gap (advisory, not blocking)**: The claim boundary function at `v4_ray_triangle.py:98–125` does not include `native_app_api: False` or `result_materialization_in_measured_window: False` at the Python boundary level (those appear only in the native call's `claim_boundary` sub-dict). The other two surfaces have the same omission. It would strengthen the boundary audit trail to surface these at the Python claim boundary level too.

**Finding: claim boundaries are strong and enforced in code. One advisory annotation gap.**

**Q4. Is the POD gate sufficient to continue to a catalog-promotion decision packet?**

Yes, with the understanding that R1–R4 amendments are prerequisites for the decision itself.

The POD gate is methodologically sound:
- Environment is fully disclosed (RTX A5000, driver 570.195.03, Torch 2.8.0+cu128, CUDA 12.8, OptiX 8.0)
- Protocol: 7 repeats, 2 warmups, median reported — consistent with the existing three measured surfaces' evidence methodology
- Parity checked against: (a) the legacy host-output primitive for the same prepared handles, and (b) an analytic fixture computed from deterministic inputs — two independent correctness gates
- All four output columns (`counts`, `sums`, `mins`, `maxs`) validated, with `sum_count` testing `counts` and `sums` together
- Metadata confirms `prepared_primitive_payload_used: true`, `prepared_ray_batch_used: true`, `group_rows_downloaded_to_host_in_hot_path: false`
- The comparison ratio (9.237x at 32K, 19.244x at 131K) is plausible and scales correctly with size (larger batches show higher ratio because legacy host materialization cost grows with row count while the device output path does not)
- `direct_device_pointer_observed: true` confirms the native side received actual CUDA device pointers, not host-side buffers

The gate is **sufficient to proceed to a decision packet**, not sufficient by itself to make the decision. The four required amendments (R1–R4) are what the decision packet must deliver.

**Q5. What must be amended before any catalog promotion?**

In priority order:

1. **(R1)** Add the candidate to `_example_commands` in `v4_catalog_regression_gate.py` for GPU mode and update `_validate_payload` to accept it as a measured surface (not a candidate) in GPU mode. Run the GPU-mode gate on the POD machine and capture JSON evidence.

2. **(R2)** Atomically update `v4_operator_catalog.py` to move `primitive_grouped_i64_reduction` from `V4_TIER2_CANDIDATE_OPERATOR_SURFACES` to `V4_TIER2_OPERATOR_SURFACES` with `measured_partners=("torch",)`, and update `v4_ray_triangle.py:primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4` to mirror the pattern used by the other two ray-triangle surfaces.

3. **(R3)** Either test the native build against OptiX 9.1 on suitable hardware or write a formal scope statement in the promotion-decision packet that declares the maximum validated ABI as OptiX 8.0 and documents the ABI rejection observed on driver 570.

4. **(R4)** Update `v4_catalog_regression_gate.py:163` and `tests/v4_catalog_regression_gate_test.py:62` to assert `measured_surface_count == 4`.

5. **(A1 — advisory)** Expand the gate test matrix to include at least two group widths, or explicitly scope the catalog entry to the validated group_width=16 configuration.

6. **(A4 — advisory)** Add a comment at `v4_ray_triangle.py:108–112` explaining that Torch appears in `partner_support_declared_unmeasured` only because the surface is still a candidate; the comment should note what to change at promotion time.

---

## Explicit Non-Authorization Block

This review does **not** authorize any of the following:

- V4 release or V4.0 release announcement
- Adding this candidate to the measured V4.0 catalog (that requires the release decision, after the amendments above are complete)
- Broad V4 speedup wording
- Whole-application speedup wording
- RT-core public performance wording or RT-core speedup claims
- True-zero-copy public wording for this surface
- Tier-3 callback/PTX support for any surface
- Raw OptiX callback support
- CuPy performance claims
- Embedding/C-ABI claims
- Non-Python host binding claims
- App-specific native engine kernels
- Measured-partner status for Torch on this surface (that change must happen at promotion time, per R2 above, not as a consequence of this review)

---

*Review complete. The candidate may continue to the catalog-promotion decision packet once required amendments R1–R4 are implemented and a GPU-mode gate pass is captured on RTX hardware.*
