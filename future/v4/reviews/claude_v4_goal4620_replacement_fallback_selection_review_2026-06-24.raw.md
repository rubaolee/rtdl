accept_with_required_amendments

---

## Findings

### Identity Check: Is Candidate A Genuinely New?

Pass. The two already-promoted surfaces are:
- `goal4617`: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` — grouped-i64 reduction
- `goal4618`: `v4_point_group_nearest_witness_2d_device_arrays` — nearest-witness 2D

Candidate A is `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` — any-hit weighted sum with caller-owned weights and device-output accumulator. The operation, output type, and input contract are distinct from both. No double-counting. The packet also explicitly labels the subagent's erroneous recommendation (goal4617 re-use) as double-counting and rejects it. Self-audit is honest.

### RT-Core Lane Compliance

Pass. The native symbol set (`_prepare_graph_executor` / `_launch_graph_executor_on_stream` / `_release_graph_executor`) follows the same lifecycle as the previously accepted goal4617 path. The packet asserts the path uses `optixLaunch`/`optixTrace`, not a CUDA-only kernel relabeled as Tier-2. The graph executor metadata (`device_output_used: True`, `query_rays_uploaded_each_run: False`, `ray_weights_uploaded_each_run: False`) is consistent with the V4 caller-owned GPU-array contract.

Contrast with the rejected aggregate-tree: that candidate's kernel was Barnes-Hut/N-body, making it an application-identity kernel regardless of OptiX wrapping. Weighted sum has no embedded force law or physics identity. The weight is fully caller-supplied. This is a generic reduction, not an app kernel.

### Existing Infrastructure Honesty

Conditionally pass, with a required pre-implementation check (see amendments). The packet claims `prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor` exists in `PreparedOptixStaticTriangleScene3D` with specific metadata flags. Historical scripts (M134, M140) and V3 tests (M78, M134) are cited as evidence the lower route works, but they are explicitly labeled "not V4 user-facing surfaces yet." This is the correct framing. The packet does not overstate the V3 evidence as V4 readiness.

### Claim Boundary Metadata

Pass. The POD gate metadata is complete and consistent with the V4 claim-boundary discipline established in goal4617 and goal4618:
- `true_zero_copy_authorized: false` — correctly bounded
- `public_speedup_claim_authorized: false` — correctly bounded
- `device_output_used: true` — distinguishes this from the Python-scalar-return variants

No prohibited wording is present.

### Scope

Pass. The packet does not reopen C ABI, embedding, multi-language host, OptiX 9.1, CuPy performance claims, Tier-3 callbacks, or app-specific kernels. CuPy is correctly marked declared-unmeasured or absent.

### POD Gate

Pass. Two non-toy sizes (32768 and 131072) are specified, correctness parity against the existing host-scalar route is required, and evidence must go under `future/v4/evidence/` in the established format. This matches the pattern from goal4617 and goal4618 gates.

### Deferred Candidates

- **B (hit-count-sum)**: Correctly deferred. The device-output graph executor variant is not currently visible for this path. Adding it in the same goal risks scope creep. Defer.
- **C (closed-shape membership)**: Correctly deferred. Current front door uses host point inputs or RTDL-owned prepared point state. This is the exact failure mode that triggered the goal4619 No-Go.
- **D (shape-pair relation)**: Correctly deferred. Host-side left polygon structures — repeating the goal4619 mistake.
- **E (segment-pair left-id count)**: Correctly deferred. Host-side left segments and RayJoin-specific relation work.

All deferrals are honest and consistent with the goal4619 No-Go criteria.

---

## Required Amendments

These must be addressed before or during implementation; the candidate selection is accepted but implementation is blocked until amendment 1 is verified.

**Amendment 1 (implementation blocker):** Before writing any V4 front-door code, Codex must verify that `PreparedOptixStaticTriangleScene3D.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor` exists in the current Python source with the metadata flags exactly as claimed (`device_output_used: True`, `host_scalar_read_before_consumer: False`, `host_row_materialization_before_consumer: False`, `query_rays_uploaded_each_run: False`, `ray_weights_uploaded_each_run: False`). If the method is absent, the flags are different, or the flags are runtime-mutable rather than structural metadata, Codex must return for re-review with corrected evidence before proceeding.

**Amendment 2 (claim-boundary metadata):** The V4 front-door implementation must include an explicit claim-boundary field documenting scene-preparation ownership: whether the triangle scene is caller-initiated (caller calls a V4 scene-preparation API) or opaque RTDL-managed state. This field does not block the candidate from being listed as `candidate`, but it must appear in the surface's claim-boundary metadata so the promotion review has a complete record.

**Amendment 3 (output scalar allocation):** The implementation tasks say "caller-owned or RTDL-allocated" for the `uint64[1]` output scalar. Pin one primary path for the candidate surface. The recommended choice is: RTDL provides an allocator/helper (the packet already names this task), and caller-owned output is supported as an optional override. The claim-boundary metadata must record which path was actually exercised during the POD gate run.

---

## Answers to Reviewer Questions

**Q1. Do you accept Candidate A?**
Yes, subject to the three amendments above.

**Q2. Is lower family breadth acceptable?**
Yes. After aggregate-tree rejection (app-specific kernel) and goal4619 No-Go (host-side query inputs), a narrower but genuinely clean path is stronger evidence than a broader but shakier one. Lower breadth is not a defect here.

**Q3. Is the device-output graph executor strong enough for a V4 candidate surface?**
Yes, provided: (a) candidate status is preserved and not upgraded to measured without a separate promotion review, (b) no true-zero-copy wording appears anywhere in the front door or documentation, and (c) amendment 1 verification confirms the executor exists as claimed.

**Q4. Should Candidate B be implemented as a backup in the same goal?**
No. Defer B. If its device-output path becomes visible in a later goal, it can be promoted then. Adding B to goal4620 scope increases the risk of one failing gate blocking the other.

**Q5. Are C, D, and E correctly deferred?**
Yes. Their current front doors have host-side inputs, which is the exact disqualifying condition identified in goal4619. They are not suitable V4 Tier-2 proof targets until their input contracts are converted to caller-owned device arrays.

**Q6. If you reject Candidate A, should Codex record goal4620 No-Go and move to goal4621?**
Moot — Candidate A is accepted. But the packet's proposed answer is correct: if A were rejected, record goal4620 No-Go with reasons and proceed to goal4621 catalog hardening. Do not enter another broad architecture search.

---

## Explicit Non-Authorization Boundaries

This review authorizes candidate selection only. It does not authorize:

- `goal4620` implementation before amendment 1 is verified
- measured-catalog promotion of any surface
- V4 release or V4 release-candidate status
- true-zero-copy wording anywhere in the front door, documentation, or metadata
- whole-app or broad V4 speedup claims
- OptiX 9.1 scope
- CuPy performance claims
- Tier-3 callback work
- C ABI, embedding, or non-Python-host work
- app-specific native kernels
- Candidate B, C, D, or E implementation under goal4620
- closing goal4620 without a separate 3-AI consensus review (or recorded review debt) of the completion packet
