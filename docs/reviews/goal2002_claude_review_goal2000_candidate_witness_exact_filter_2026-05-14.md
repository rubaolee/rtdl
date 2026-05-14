# Goal2002 - Claude Review: Goal2000 Candidate Witness Exact-Filter Pod Audit

Verdict: accept-with-boundary

Date: 2026-05-14

Reviewer: Claude (claude-sonnet-4-6), external read-only review

---

## Scope of Review

Files examined:

- `docs/reports/goal2000_optix_candidate_witness_exact_filter_pod_audit_2026-05-14.md`
- `tests/goal2000_optix_candidate_witness_exact_filter_pod_audit_test.py`
- `src/rtdsl/optix_runtime.py` (bounded all-witness validation, lines 3036-3045)
- `src/rtdsl/partner_adapters.py` (exact-filter function, contract metadata, lines 1874-1940, 2044-2137)
- `scripts/goal1856_segment_polygon_v2_partner_perf.py`
- `docs/reports/goal2000_pod_smoke/*.json` (all three artifacts)
- Updated boundary tests: Goal1850, Goal1861, Goal1865, Goal1997

---

## Q1: Float64 Ray-Column Bug Fix

**Finding: Correctly fixed, with one minor wording note.**

The validation in `optix_runtime.py` (lines 3039-3044) now rejects any bounded
all-witness ray column (`ox`, `oy`, `dx`, `dy`, `tmax`) whose dtype is not
`float32` or `float`. The error message reads:

```
"partner device bounded all-witness ray column {name!r} must use dtype float32"
```

The perf script `goal1856_segment_polygon_v2_partner_perf.py` builds all five ray
coordinate columns as `runtime["float32"]` (lines 65-69), and `tmax` is also
`float32` (line 69). No `float64` reference remains for those columns.

The test suite verifies both sides: `test_runtime_fails_closed_on_float64_all_witness_rays`
in the Goal2000 test file and `test_all_witness_contract_rejects_float64_ray_columns`
in the Goal1997 test file check the runtime wording and the perf script column types.

**Minor wording note**: The general `_require_partner_device_ray_column_layout`
function (lines 2560-2566) still accepts `float64`/`double` for ox/oy/dx/dy/tmax —
this is used by other code paths that do not go through the bounded all-witness
kernel. The distinction is intentional and correct: only the all-witness path
carries the float32 constraint from the C kernel ABI. The separation is accurate
but a future reader could be confused by the two validators co-existing. No action
required for this review; worth a comment when the all-witness path grows.

**Assessment: correct and well-tested.**

---

## Q2: Generic Candidate-Witness Contract Clarification

**Finding: Correctly clarified, consistently propagated.**

The adapter (`partner_adapters.py`, lines 1879-1883 and 1933-1937) now emits:

```python
"native_engine_row_contract": "generic_ray_primitive_candidate_witness_pairs",
"app_exact_filter": "host_segment_triangle_filter_from_generic_witness_candidates",
"native_exact_row_semantics_authorized": False,
"app_exact_row_semantics_authorized": True,
"whole_app_true_zero_copy_authorized": False,
```

This correctly separates what the native engine guarantees (generic candidate pairs)
from what the adapter guarantees (exact app rows after host filtering). The metadata
appears in both the early-return empty-input path and the main execution path, so
there is no path that can silently omit it.

The Goal1861 and Goal1865 reports have been updated to use this terminology, and
the Goal1865 test explicitly asserts `generic_ray_primitive_candidate_witness_pairs`
in the native contract.

**One terminology inconsistency**: The Goal1850 pod smoke artifact
(`goal1850_segment_polygon_partner_adapter_pod_smoke.json`) still records
`"native_engine_row_contract": "generic_ray_primitive_witness_pairs"` (without
"candidate_"), because that artifact predates Goal2000. The Goal1850 test at
line 213 reads that older key from the artifact and passes. The current adapter
code now emits `generic_ray_primitive_candidate_witness_pairs`. This artifact/code
divergence does not break anything and is a known historical boundary, but it
should be noted so a future reviewer does not treat the two strings as interchangeable
in new work.

**Assessment: correctly clarified and consistently propagated in live code;
historical artifact uses older terminology, which is acceptable.**

---

## Q3: Host Exact-Filter Boundary Honesty

**Finding: Honest. The demotion of `whole_app_true_zero_copy_authorized` to false
is correct.**

The `_exact_segment_triangle_rows_from_witness_columns` function (lines 2044-2137)
does the following:

1. Pulls device witness IDs to host via `to_host_int` (a CPU materialization).
2. Pulls ray coordinate columns to host via `to_host_float`.
3. Pulls triangle columns to host via `to_host_float`.
4. Filters candidate pairs using `_finite_ray_hits_triangle` in a Python loop.
5. Returns a sorted tuple of exact `{segment_id, polygon_id}` dicts.

Step 1-3 are explicit host materializations. Setting `whole_app_true_zero_copy_authorized: false`
is therefore correct and necessary. The report is explicit that this is the next
optimization target: moving the exact filter to a CuPy RawKernel.

The Goal1861 report was updated to reflect `app_count_host_materialization: true`
and `whole_app_true_zero_copy_authorized: false`, which is consistent with the
adapter code. The Goal1861 test asserts both.

**One gap**: The perf script at line 276 includes `"whole_app_true_zero_copy_authorized": False`
in the `claim_boundary` dict. All three pod JSON artifacts are missing this key
from their `claim_boundary` objects — they contain only:
`broad_rt_core_speedup_claim_authorized`, `package_install_claim_authorized`,
`same_contract_timing_row`, `v2_0_release_authorized`, `whole_app_speedup_claim_authorized`.

This means the artifacts were generated on an older version of the perf script that
did not yet have `whole_app_true_zero_copy_authorized` in `claim_boundary`. The
test `test_pod_artifacts_preserve_strict_parity_and_boundaries` does not check for
this key in the artifact `claim_boundary`, so the tests pass. The report narrative
makes the boundary clear, but the artifact JSON does not carry the machine-readable
flag. This is a minor artifact-script divergence. New artifacts should be regenerated
with the current script to close this gap.

**Assessment: boundary is honest; artifact `claim_boundary` is missing one flag
that the current perf script would produce.**

---

## Q4: A5000 Pod Artifacts — Parity and Claim Scope

**Finding: Parity evidence is solid; timing evidence is limited and partially
unfavorable.**

All three artifacts carry:

- `status: pass`
- `gpu: NVIDIA RTX A5000, 570.211.01`
- `strict_rows_match: true` for the expected row count
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `broad_rt_core_speedup_claim_authorized: false`

Row parity holds at all three scales (256, 2048, 8192). The overflow check passes
at all three scales (tight capacity correctly triggers the overflow error). This
is the evidence the report claims, and the claims match the evidence.

**Timing concerns** — the artifacts reveal a non-monotonic performance profile
that the audit report does not fully discuss:

| count | v1.8 median (s) | v2.0 CuPy median (s) | ratio |
|-------|-----------------|----------------------|-------|
| 256   | 0.406           | 0.00869              | 0.021x |
| 2048  | 0.0257          | 0.0514               | **2.001x** |
| 8192  | 0.715           | 0.124                | 0.174x |

The count-2048 run shows v2.0 CuPy as approximately **2× slower than v1.8 native
OptiX**. The report cites only the count-8192 result as "the strongest timing row"
and does not discuss the count-2048 regression. This is the largest analytical gap
in the audit report.

The count-256 v1.8 baseline shows an extreme bimodal distribution: 0.810s on
iteration 1, then 0.0014s on iteration 2 — a 570× swing in 2 samples. This is
driver/kernel JIT warmup behavior. The count-8192 baseline similarly shows 1.11s
and 0.32s over 2 iterations. Two-iteration timing rows are too sparse to report
medians with confidence. The count-2048 run used 3 iterations, which is marginally
better but still sparse.

These timing observations do not undermine the parity evidence or the correctness
of the boundary claims, but they should be explicitly acknowledged in the report
so that the count-2048 regression is not later cited as evidence for v2.0 performance.

**Assessment: parity evidence is solid and correctly scoped; timing evidence
has a material gap (count-2048 regression unreported) and insufficient iteration
counts for statistical confidence.**

---

## Q5: Remaining Risks That Should Block v2.0

The following items should block v2.0 release for this lane:

**1. Host exact-filter bottleneck (primary blocker)**
The `_exact_segment_triangle_rows_from_witness_columns` function materializes
device buffers to host Python for every query. This is proportional to the
candidate witness count, which is worst-case O(rays × triangles). At count=8192
the output capacity is 67,108,864 entries (8192²). No v2.0 performance claim can
be made while this path exists. The adapter itself correctly demotes
`whole_app_true_zero_copy_authorized` to false.

**2. Count-2048 regression**
The pod shows v2.0 CuPy is 2× slower than v1.8 native OptiX at count=2048.
This regression is unexplained and unreported in the audit. It may be due to
the host exact-filter dominating at intermediate scale, or to the dense output
capacity (4M entries), or to host Python loop overhead at that candidate count.
Understanding this regression is prerequisite to any positive performance claim.

**3. Artifact `claim_boundary` key gap**
Artifacts generated by earlier script revisions are missing `whole_app_true_zero_copy_authorized: false`
from the JSON `claim_boundary` object. New pod runs should regenerate artifacts
with the current script to ensure machine-readable boundary consistency.

**4. Insufficient timing statistics**
Count-256 and count-8192 runs used only 2 iterations. The v1.8 baseline at
count-256 shows extreme JIT warmup variance. Minimum 5 warmed iterations are
needed before timing ratios can be treated as evidence.

**5. Single-app, single-scale coverage**
Only the segment/polygon path has pod timing. Road hazard priority flags (Goal1865)
and the generic witness-pair paging adapter (Goal1997) have no pod timing. The app
coverage matrix is incomplete.

**6. Quadratic output buffer allocation**
`output_capacity` defaults to `count * count`. For count=8192, this allocates 256M
uint32 slots (≈512MB for two witness ID buffers). This is not feasible for
production workloads and represents an un-addressed scalability concern beyond
the exact-filter bottleneck.

---

## Summary Assessment

Goal2000 makes two genuine and correctly implemented correctness fixes: the
float64→float32 ray-column dtype guard and the explicit separation of the generic
native witness contract from app-layer exact rows. Both fixes are well-tested and
honestly bounded. The pod demonstrates that the A5000 can build and execute the
library with CUDA 12.8 stacks, and the parity evidence is real.

The primary gaps are:

- The count-2048 regression (v2.0 2× slower) is unacknowledged in the audit report.
- Pod artifacts are missing one `claim_boundary` key that the current perf script
  would produce.
- Timing sample counts are too low for statistical confidence.

None of these gaps invalidate the correctness work or the boundary claims. The
report is honest about what is blocked. The verdict is **accept-with-boundary**:
the correctness fixes and contract clarifications are accepted; the timing evidence
requires follow-up before any forward performance claim can be made, and the
host exact-filter bottleneck remains the clear next implementation target.

---

## Accepted Claims (Carry Forward)

- A5000 pod environment (CUDA 12.8, driver 570.211.01, OptiX SDK) is validated
  for building and running `librtdl_optix.so`.
- The bounded all-witness path now fails closed on float64 ray-column inputs.
- The native engine emits generic candidate witnesses; the adapter is responsible
  for app-layer exact filtering.
- Same-contract strict-row parity holds at counts 256, 2048, and 8192 with CuPy;
  counts 256 and 2048 also hold with Torch.

## Blocked Claims (Do Not Carry Forward)

- v2.0 release authorization.
- Whole-application acceleration or speedup claims.
- True whole-app zero-copy for exact segment/polygon rows.
- Broad RT-core speedup claims.
- Any positive performance claim derived from the count-2048 or count-8192 timing
  rows without further investigation of the count-2048 regression and without
  warmed multi-iteration baselines.
