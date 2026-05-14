# Goal2017 Claude Review: Goal2016 Torch Vectorized Exact Witness Filter

Date: 2026-05-14

Reviewer: Claude (external review)

Verdict: **accept-with-boundary**

---

## Files Inspected

- `src/rtdsl/partner_adapters.py` (lines 2340–2457, 2819–3045)
- `docs/reports/goal2016_torch_vectorized_exact_witness_filter_2026-05-14.md`
- `docs/reports/goal2016_pod_smoke/road_hazard_prepared_torch_exact_filter_2048.json`
- `tests/goal2016_torch_vectorized_exact_witness_filter_test.py`

---

## Checkpoint 1: Native OptiX remains app-agnostic and candidate-only

**Pass.**

Every code path that calls into the native engine sets:

```
"native_engine_row_contract": "generic_ray_primitive_candidate_witness_pairs"
"native_exact_row_semantics_authorized": False
```

The native scene object (`_PartnerPreparedTriangleScene`) delegates
`write_device_any_hit_all_witnesses` transparently to the wrapped native scene
with no modification. No new native entry point was added. The pod artifact
confirms `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
in both the unprepared and prepared Torch metadata blocks.

---

## Checkpoint 2: Torch exact filtering is performed in the partner layer, not native

**Pass.**

`_torch_exact_segment_triangle_witness_pairs` (lines 2340–2457) is a pure Python
function in `partner_adapters.py` that uses Torch tensor ops for all geometry
work. The native engine fires first; the partner layer receives the candidate
witness IDs via `witness_result["witness_ray_ids"]` and then applies the exact
filter using `orient`, `point_in_triangle`, `on_segment`, and `segments_intersect`
— all implemented as batched Torch operations in float64.

The metadata correctly distinguishes the layers:

- `app_exact_filter: torch_vectorized_segment_triangle_filter_from_generic_witness_candidates`
- `app_exact_filter_device_materialization: true`
- `native_exact_row_semantics_authorized: False`

---

## Checkpoint 3: Pod artifact supports only a partner-parity/correctness claim

**Pass.**

The artifact (`road_hazard_prepared_torch_exact_filter_2048.json`) explicitly
encodes all speedup claims as false:

```json
"broad_rt_core_speedup_claim_authorized": false,
"package_install_claim_authorized": false,
"whole_app_speedup_claim_authorized": false,
"v2_0_release_authorized": false
```

The timing rows confirm the Torch path is slower than the v1.8 prepared native
baseline at count 2048:

| Path | Median (s) | Ratio vs v1.8 prepared |
|---|---:|---:|
| v1.8 prepared native OptiX | 0.002813 | 1.000x |
| v2.0 unprepared Torch exact | 0.005988 | 2.128x slower |
| v2.0 prepared Torch exact | 0.005290 | 1.880x slower |

`partner_output_columns_true_zero_copy_authorized: true` is the only
authorized positive claim, and it is correctly scoped to partner output columns.

---

## Checkpoint 4: Report clearly states parity/correctness gap, not performance gap

**Pass.**

The report states explicitly:

> "This goal closes a partner-parity and correctness gap, not a performance gap."

The status line is `pod-pass-with-boundary` and the report makes no speedup
claim. The Boundary section is present and correct.

Minor formatting note: the report contains two `## Boundary` headers (one
empty, before "Pod Evidence"). This is cosmetic and does not affect the
boundary semantics, but a future cleanup pass could collapse them.

---

## Checkpoint 5: Implementation risks with vectorized Torch geometry predicates

The following risks are noted. None block acceptance at this boundary, but
each should be tracked before any v2.0 or broader claim is made.

**Risk A — float64 cast may diverge from CuPy RawKernel.**
All coordinate tensors are cast to `torch.float64` before geometry evaluation
(lines 2399–2408). The CuPy RawKernel path is not visible in this excerpt
but typically runs in float32. If source columns are float32, the Torch path
evaluates predicates at higher precision and may accept or reject borderline
pairs differently. This is not a correctness defect at this goal's scope
(parity is measured against priority flags, not per-pair membership), but
it is a semantic difference that should be documented before exact-result
parity is claimed.

**Risk B — JIT warmup spike visible in artifact.**
The first unprepared sample is 0.282 s vs. subsequent samples of ~6 ms. This
is expected PyTorch CUDA JIT/kernel compilation overhead, but the median is
computed over all five samples (iteration 1 is the outlier). The summary uses
median correctly, so reported timing is not distorted, but operators comparing
min/max latency could be surprised.

**Risk C — Vectorized materialization peak memory.**
The implementation materializes all candidate coordinate tensors simultaneously
(sx, sy, ex, ey, ax, ay, bx, by, cx, cy — nine float64 tensors, each of length
`emitted_count`). For large candidate counts the memory footprint is O(9N×8
bytes). The CuPy RawKernel path processes one pair at a time on-GPU and has a
lower peak footprint. This is not a concern at count 2048 but should be
evaluated if the contract is exercised at significantly larger counts.

**Risk D — `safe_pos` clamping precedes geometry evaluation on invalid candidates.**
Invalid candidates (where `ray_indices` or `triangle_indices` equals -1) are
clamped to index 0 before geometry columns are gathered (lines 2396–2397).
This means invalid candidates evaluate geometry against the column-0 triangle,
which may produce an arbitrary true/false result. The `valid` gate in
`exact_mask = valid & (...)` (line 2446) correctly suppresses these, so the
final filter output is sound. However, if `valid` itself were ever incorrectly
set, the clamped-0 geometry result would leak through silently. The current
logic is correct; this is a fragility note for future maintainers.

**Risk E — Artifact `goal` field references Goal1869, not Goal2016.**
The JSON artifact contains `"goal": "Goal1869"` and `"goal_extension": "Goal1889"`.
The `source_commit_label` correctly names the Goal2016 branch, but tooling
that indexes artifacts by the `goal` field will not associate this artifact
with Goal2016. This is a metadata gap that should be corrected if the artifact
schema is used for automated lineage tracking.

---

## Summary

All five review checkpoints pass. The implementation correctly keeps exact
filtering in the partner layer, the native engine is untouched, and the pod
artifact and report are internally consistent. The boundary is properly stated
and no unauthorized claims are present.

The five risks above (float64/float32 divergence, JIT spike, peak memory at
scale, clamped-0 fragility, and artifact goal field mismatch) are not blockers
at this parity/correctness scope, but should be resolved before this path is
used to support an exact-result or performance claim.

Verdict: **accept-with-boundary**
