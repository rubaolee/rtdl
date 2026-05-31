# Goal2781 Claude Review - Grouped Vector-Sum Adapter

Date: 2026-05-31
Reviewer: Claude (Sonnet 4.6) — independent read-only
Verdict: **accept-with-boundary**

---

## Scope

Narrow v2.5 adapter-integration review only. This is not a release gate, not a
performance promotion review, and not an audit of the underlying Triton kernel
implementation.

Files read:
- `src/rtdsl/partner_adapters.py` (lines 247–288, 1694–1769)
- `src/rtdsl/__init__.py` (lines 1–816 and grep for `grouped_vector_sum`)
- `src/rtdsl/adapters/reductions.py`
- `tests/goal2781_grouped_vector_sum_adapter_test.py`
- `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md`
- `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`
- `docs/research/future_version_to_do_list.md` (grouped_vector_sum entries)

---

## Q1 — Does `grouped_vector_sum_2d_partner_columns` remain generic and app-agnostic?

**Pass.**

The function signature uses only generic names: `group_ids`, `values_x`,
`values_y`. The secondary lookup aliases (`source_ids`, `vector_x`, `vector_y`)
are also generic. The docstring says "generic grouped 2D vector rows." No
app-specific vocabulary (force, N-body, Barnes-Hut, accumulation, field) appears
anywhere inside the function body or its metadata block.

The `input_contract` metadata field reads `"caller_supplied_grouped_vector_rows_2d"`
and `partner_reference_contract` reads `"generic_grouped_vector_sum_f64x2"`. Both
stay below any application layer.

The `future_version_to_do_list.md` entry at line 693–697 references Barnes-Hut
and N-body only as an example of a *future promotion gate*, not as a label on the
current adapter surface. That is the correct placement for such vocabulary.

---

## Q2 — Does the Triton branch route through `grouped_vector_sum_f64x2` without replacing RTDL/OptiX traversal?

**Pass.**

At `partner_adapters.py:257–266`:

```python
result = run_triton_partner_continuation(
    "grouped_vector_sum_f64x2",
    {
        "group_ids": keys.to(runtime["int64"]),
        "values_x": values_x,
        "values_y": values_y,
        "group_count": group_count,
    },
)
```

The operation name `"grouped_vector_sum_f64x2"` matches the declared v2.5
continuation operation. No OptiX or native engine call appears in the Triton
path. The metadata block at `partner_adapters.py:1754` records
`native_engine_row_contract: "not_called_partner_continuation_only"`, which is an
explicit runtime-visible marker confirming the absence of native RT traversal.

The test at line 74 verifies `metadata["v2_5_partner_continuation_operation"] ==
"grouped_vector_sum_f64x2"`, so the operation label is asserted by the test suite.

---

## Q3 — Do the Torch/CuPy branches preserve same-contract partner-owned column behavior without implying Torch is the neutral buffer protocol?

**Pass.**

Torch branch (`partner_adapters.py:267–276`): allocates zero tensors, calls
`scatter_add_` over partner-owned device tensors. No cross-partner copy, no
pointer handoff, no neutral-buffer seam invoked.

CuPy branch (`partner_adapters.py:277–286`): same pattern via `cupy.add.at`. Both
branches return partner-owned tensors in the same shape contract as the Triton
branch.

The default partner for `grouped_vector_sum_2d_partner_columns` is
`partner="triton"` (line 1698), not `"torch"`. This is the correct default to
avoid accidentally signaling that Torch is the canonical or neutral path. The
metadata field `partner` records the actual runtime choice without elevating any
single partner to protocol-level status.

No "neutral buffer protocol" language appears in the implementation.

---

## Q4 — Is the negative pod performance evidence recorded honestly?

**Pass.**

The pod JSON (`..._pod_69_30_85_171_2026-05-31.json`) reports three measurement
rows:

| rows | groups | Triton median (s) | Torch median (s) | ratio |
|---:|---:|---:|---:|---:|
| 8,192 | 512 | 0.002952 | 0.000178 | 16.6x |
| 262,144 | 4,096 | 0.003292 | 0.000490 | 6.7x |
| 1,048,576 | 8,192 | 0.003644 | 0.000890 | 4.1x |

`correctness_match: true` for all rows. Max absolute error values (3.5e-15 to
4.9e-14) are consistent with float64 floating-point accumulation — no precision
concern at this scale.

The report explicitly states: *"This is intentionally recorded as negative
performance evidence for the current Triton preview kernel."* The metadata in
every measured row carries `v2_5_triton_preview_kernel_status:
"preview_not_promoted"`. The to-do list records the same finding without
softening it.

The description "4x-17x slower than Torch" in the report and to-do list matches
the measured range (4.1x–16.6x). No rounding or selective presentation was
detected.

---

## Q5 — Are all public speedup, RT-core, true-zero-copy, whole-app, and release claims still blocked?

**Pass.**

The pod JSON `claim_flags` block:

```json
"public_speedup_claim_authorized": false,
"rt_core_speedup_claim_authorized": false,
"true_zero_copy_claim_authorized": false,
"v2_5_release_authorized": false,
"whole_app_speedup_claim_authorized": false
```

The implementation metadata block at `partner_adapters.py:1756–1760`:

```python
"direct_device_handoff_authorized": False,
"rt_core_speedup_claim_authorized": False,
"v2_5_release_authorized": False,
"whole_app_speedup_claim_authorized": False,
```

The test at lines 76–79 asserts all four `False` values at runtime. The report
section "Boundary" lists each blocked claim explicitly. All five blocked-claim
categories in the review question are covered.

---

## Q6 — Are the tests sufficient for this narrow adapter wiring slice?

**Adequate with minor gaps; not blocking at preview scope.**

Three tests total:

1. **`test_generic_adapter_is_exported_without_app_specific_engine_path`** —
   Text-scan structural test. Confirms the operation string
   `"grouped_vector_sum_f64x2"`, sentinel strings `"not_called_partner_continuation_only"`
   and `"preview_not_promoted"` appear in the adapter source. Confirms both names
   appear in `__init__.py` and `adapters/reductions.py`.

2. **`test_report_records_claim_boundary_and_negative_public_flags`** — Report
   text presence. Confirms "no public speedup claim" and "no true zero-copy claim"
   appear in the report.

3. **`test_triton_adapter_matches_torch_same_contract_when_cuda_available`** —
   Functional runtime test. Validates six-row, four-group input including one
   zero-count group. Checks expected numerics for both Triton and Torch. Asserts
   cross-partner equivalence. Asserts all four blocked-claim flags.

Pod ran all 3 tests in 2.973s on NVIDIA RTX A5000. Local Windows ran 3 tests in
0.018s (1 skipped — CUDA not available locally).

**Gaps (not blocking):**

- The empty-input fast-paths at `partner_adapters.py:271` (Torch) and line 281
  (CuPy) are not covered by any test case.
- The CuPy path is not tested (acceptable: CuPy is unavailable in the local
  Windows environment and is not a primary preview target for this goal).
- `partner_group_vector_sum_2d_by_key` is tested only transitively through
  `grouped_vector_sum_2d_partner_columns`, not directly.
- Negative `group_count` validation is not tested.

None of these gaps affect the narrow wiring-slice verdict given the preview scope.

---

## Summary

| Question | Finding |
|---|---|
| Q1 — App-agnostic | Pass |
| Q2 — Triton routes through `grouped_vector_sum_f64x2` | Pass |
| Q3 — Torch/CuPy same-contract without Torch elevation | Pass |
| Q4 — Negative performance evidence honest | Pass |
| Q5 — All public claims blocked | Pass |
| Q6 — Tests sufficient for narrow slice | Adequate (minor gaps, not blocking) |

**Verdict: `accept-with-boundary`**

The adapter is correctly wired, the claim boundary is machine-visible and
test-asserted, the negative performance evidence is complete and honestly labeled,
and no public claim has been authorized. The test coverage is adequate for a
preview wiring slice. The empty-input fast-paths and CuPy path are appropriate
candidates for coverage in a later goal if these paths become part of a promoted
surface.
