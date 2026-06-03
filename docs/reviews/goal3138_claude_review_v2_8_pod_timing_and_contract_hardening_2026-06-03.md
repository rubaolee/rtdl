# Goal3138: Claude Independent Review — v2.8 Pod Timing and Contract Hardening (Goals 3132, 3136, 3137)

Date: 2026-06-03

Reviewer: Claude (claude-sonnet-4-6), independent

Verdict: **accept-with-boundary**

---

## Summary

Goals 3132, 3136, and 3137 together form a coherent three-part response to the
Goal3133 `accept-with-boundary` verdict: 3132 closes the correctness gap on pod
hardware, 3136 correctly localizes the Numba grouped-arg performance debt, and
3137 addresses three of the four medium findings from Goal3133. All claim
boundaries remain intact. The chain is internally consistent and correctly scoped.

Three low observations are recorded. None require immediate rework, but two
should be addressed before any schema-level partner-coverage claim is made.

---

## Findings by Severity

### Low

**L1 — Canonicalized argmin/argmax/topk schema has no fresh pod evidence**

Goal3132 ran on commit `2809a45b`, before Goal3137's canonicalization. The pod
JSON artifact shows `grouped_argmin_f64` and `grouped_argmax_f64` partner outputs
as `{group_ids, item_ids, scores}` — without `missing_group_ids`. After
Goal3137, `_canonical_ranked_summary_columns` now requires `missing_group_ids` in
the helper's output and enforces `{group_ids, item_ids, scores, missing_group_ids}`
as the canonical schema for argmin/argmax, and `{group_ids, item_ids, scores,
ranks, row_offsets, missing_group_ids}` for top-k.

The Numba implementation (`numba_partner_continuation.py` lines 836–845) does
include `missing_group_ids` in its `outputs` dict, and the `_torch_grouped_arg_topk`
helper includes `ranks`, `row_offsets`, and `missing_group_ids`. The
canonicalization is therefore consistent with the underlying implementations. The
mock-based unit tests in `goal3111_v2_8_segmented_typed_stream_adapter_test.py`
lines 404–512 verify the filter logic correctly. However, no fresh pod run has
exercised the canonicalized schema end-to-end. Before any output-schema coverage
claim is made for these three operations, a pod re-run on the post-Goal3137 code
is needed.

**L2 — `compact_mask_i64` asymmetry rationale remains undocumented (carried from M4)**

Goal3137 explicitly lists `compact_mask_i64` as a deliberate non-change and
correctly leaves it reference-only. However, the rationale for the asymmetry (the
operation has no group semantics in the partner front door, or is simply deferred)
is still not recorded anywhere in the contract, the report, or a code comment.
A future contributor could add partner support without understanding whether the
exclusion is intentional or incomplete. This was M4 in Goal3133 and remains open.

**L3 — `segmented_min_f64` and `segmented_max_f64` partner smoke still absent (carried from M2)**

Both operations remain in `V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS` and
are handled by `_reference_inputs_for_plan`, but are absent from
`V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS` and have no
partner-consumer smoke on any hardware. Goal3137 correctly treats this as a
non-change requiring actual smoke evidence. Before any operation-surface coverage
claim includes these two operations, partner smoke must be produced.

---

## Claim Boundary Assessment

All claim boundaries remain correctly implemented and machine-checkable.

**Structural guards** — unchanged by Goals 3132, 3136, 3137:
- `V28TypedResultStreamContract.__post_init__` raises `ValueError` for any of
  seven prohibition flags set `True`.
- `V28GroupedContinuationPlan.__post_init__` raises `ValueError` for six
  prohibition flags.
- `V28SegmentedTypedStreamAdapterResult.__post_init__` raises `ValueError` for
  ten prohibition flags including the three promotion flags.

**Propagation** — every `to_metadata()` and every `execute_*` return dict
explicitly records all flags as `False` and carries both claim-boundary string
constants.

**Pod artifact** (`goal3132_pod_artifacts/v2_8_partner_front_door_pod_smoke_2026-06-03.json`)
records `release_authorized`, `public_speedup_claim_authorized`,
`rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`,
`hidden_dispatch_allowed`, `automatic_partner_selection_allowed`, and
`app_specific_engine_logic_allowed` as `false` at the machine level.

No regression to any claim boundary was introduced by any of the three goals.

---

## Files Inspected

| File | Role |
| --- | --- |
| `src/rtdsl/v2_8_typed_result_stream.py` | Core stream/continuation contract |
| `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` | Reference adapter and partner front door |
| `src/rtdsl/partner_adapters.py` | Partner helper implementations |
| `src/rtdsl/numba_partner_continuation.py` | Numba kernel implementations |
| `tests/goal3108_v2_8_typed_result_stream_contract_test.py` | Contract unit tests |
| `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py` | Adapter / front-door unit tests |
| `docs/reports/goal3132_v2_8_partner_front_door_pod_smoke_2026-06-03.md` | Goal3132 report |
| `docs/reports/goal3132_pod_artifacts/v2_8_partner_front_door_pod_smoke_2026-06-03.json` | Goal3132 machine artifact |
| `docs/reports/goal3136_v2_8_numba_grouped_arg_timing_split_2026-06-03.md` | Goal3136 report |
| `docs/reports/goal3136_pod_artifacts/numba_grouped_arg_timing_split_2026-06-03.json` | Goal3136 machine artifact |
| `docs/reports/goal3137_v2_8_front_door_contract_hardening_after_claude_review_2026-06-03.md` | Goal3137 report |
| `docs/reviews/goal3133_claude_review_v2_8_partner_front_door_chain_3108_3131_2026-06-03.md` | Prior review |

---

## Answers to Review Questions

**Q1. Did Goal3132 correctly close the healthy-pod functional smoke gap for all seven currently supported v2.8 front-door operations?**

Yes. The JSON artifact confirms that on an RTX 4000 Ada pod (commit `2809a45b`,
Numba 0.65.1, CuPy 14.1.1, Torch 2.12.0+cu130):

| Operation | Partner | Pod Result |
| --- | --- | --- |
| `segmented_count_i64` | CuPy | passed |
| `segmented_sum_f64` | CuPy | passed |
| `grouped_vector_sum_f64x2` | CuPy | passed |
| `grouped_argmin_f64` | Numba | passed |
| `grouped_argmax_f64` | Numba | passed |
| `grouped_topk_f64` | Torch | passed |
| `bounded_collect_finalize_i64` | Torch | passed |

The Numba sanity kernel passed (`[1, 2, 3, 4, 5, 6, 7, 8]`). The unit gate
(27 tests) ran clean. All claim flags are `false` in the artifact.

The correctness gap from Goal3133 is closed. The gap noted in L1 above — that
the pod ran on pre-canonicalization code — does not invalidate the correctness
finding; it limits the schema-level claim that can be made.

**Q2. Does Goal3136 correctly localize the Numba grouped-arg performance debt to the current grouped-arg partner implementation rather than the v2.8 wrapper?**

Yes, clearly. The timing matrix across three sizes (65K, 262K, 1M rows) at
group counts that scale proportionally shows:

- Direct kernel vs. partner adapter: essentially identical steady-state medians
  at every size (within 1–4 ms, well within measurement noise from occasional
  spike repetitions).
- Validation + compaction overhead vs. no-validate/dense: approximately 40%
  slower, scaling consistently across all three sizes.
- Even the fastest path (no-validate, dense output) remains ~0.135–0.143 s
  while the Python reference is ~0.055 s.
- Numba emitted under-occupancy warnings; grid sizes (4, 16, 64 blocks for
  65K/262K/1M rows respectively) confirm that the kernel launches far too few
  threads for these problem sizes.

The v2.8 front-door wrapper is exonerated. The multi-kernel score/item tie-break
path plus host-visible compaction metadata in the current Numba implementation is
the root cause. Goal3136 documents this correctly and makes no performance claim.

**Q3. Does Goal3137 adequately address the Goal3133 findings about top-k semantics, explicit-partner sentinel rejection, and ranked-summary output canonicalization?**

Yes, for the three findings that were mechanical contract gaps.

*M1 (top-k ordering direction):* Addressed. `V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS`
now explicitly states:
- `grouped_topk_f64`: "select the k lowest scores per group in ascending score
  then item_id order"
- `grouped_argmin_f64`: "select the lowest score per group; ties choose the
  lowest item_id"
- `grouped_argmax_f64`: "select the highest score per group; ties choose the
  lowest item_id"

The semantics propagate through `V28GroupedContinuationPlan.to_metadata()` and
through the `plan_segmented_typed_stream_partner_continuation` dry-run response.
The `test_grouped_continuation_requires_user_selected_partner` test asserts the
semantics are present in plan metadata for `grouped_argmax_f64`.

*L1 (sentinel partner rejection):* Addressed. `V28GroupedContinuationPlan.__post_init__`
now rejects `"explicit_user_choice_required"` at line 243, matching the existing
rejection of `""` and `"auto"`. `validate_grouped_continuation_plan` performs the
same check at line 444. The test at lines 119–135 covers the `"auto"` and
default-sentinel cases via `assertRaises`.

*M3 (ranked-summary partner output canonicalization):* Addressed. The new
`_canonical_ranked_summary_columns` helper at lines 689–697 is called for all
three ranked-summary operations:
- `grouped_argmin_f64` and `grouped_argmax_f64`: canonicalized to
  `{group_ids, item_ids, scores, missing_group_ids}`.
- `grouped_topk_f64`: canonicalized to
  `{group_ids, item_ids, scores, ranks, row_offsets, missing_group_ids}`.

The helper raises `ValueError` for any missing canonical column, enforcing the
schema structurally rather than relying on empirical pass-through. The mock-based
tests at lines 404–512 verify both the inclusion of canonical columns and the
exclusion of helper-only columns (`dense_item_ids`, `dense_scores`, `counts`).

Two Goal3133 findings were correctly not addressed:

*M2 (segmented_min/max smoke)*: Still open. See L3 above.

*M4 (compact_mask_i64 rationale)*: Still open. See L2 above.

**Q4. Is it correct that `segmented_min_f64` and `segmented_max_f64` should remain deferred from the v2.8 front-door supported set until explicit smoke evidence exists?**

Yes. The deferral is correct and well-reasoned.

Both operations appear in `V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS` (the
vocabulary of all operations the typed result stream can generate continuation
plans for) and are handled by `_reference_inputs_for_plan` (the Python reference
path). They are absent from
`V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS` (the set for
which the explicit partner front door is advertised as operable).

Adding these operations to the supported set by metadata edit alone — without
partner-consumer smoke demonstrating that an actual partner kernel exists and
produces correct output — would be an unsupported surface expansion. Goal3137
correctly holds this boundary.

**Q5. Are all release/speedup/zero-copy/hidden-dispatch/auto-partner/app-specific native-engine/user-shader-injection claim boundaries still intact?**

Yes. All seven categories of prohibited claims are:

1. Blocked structurally in three independent dataclasses via `__post_init__`
   guards that raise `ValueError` if any flag is set `True`.
2. Propagated as explicit `False` values through every `to_metadata()` output,
   every dry-run response, and every execution-result dict.
3. Carried as string constants (`V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY` and
   `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY`) in every metadata
   payload.
4. Recorded at the machine level in the pod artifacts for Goals 3132 and 3136
   (both JSON files contain explicit `false` entries for each prohibited flag).
5. Restated in the "Claim Boundary" sections of all three goal reports.

No regression to any of these guards was introduced by Goals 3132, 3136, or 3137.

---

## What Remains Open Before Stronger Claims

In roughly ascending order of effort:

1. **Re-run pod smoke on post-Goal3137 code** to produce canonical-schema
   evidence for `grouped_argmin_f64`, `grouped_argmax_f64`, and `grouped_topk_f64`
   (L1 above). This is required before any output-schema coverage claim is made
   for these three operations.

2. **Document `compact_mask_i64` asymmetry rationale** — one sentence in the
   contract constant or in the Goal3137 report. Required before any
   "reference coverage == partner coverage" claim is published (L2 above).

3. **Add `segmented_min_f64` / `segmented_max_f64` partner smoke**, or record
   them as explicitly deferred with a rationale in the supported-operations table
   (L3 above, carried from M2).

4. **Numba grouped-arg performance hardening**. The current Numba path is
   demonstrably slower than the Python reference at all tested sizes. The
   under-occupancy root cause is documented. No speedup or performance claim can
   be made until an optimized path is validated under pod-class conditions with
   the same contract evidence.

5. **Release and public-speedup claims remain fully blocked** pending items 1–4
   above and a full pod-class validation sweep of any optimized implementation.

---

## Verdict

**accept-with-boundary**

Goals 3132, 3136, and 3137 are accepted as a coherent and correctly scoped
response to the Goal3133 `accept-with-boundary` verdict. The pod correctness gap
is closed. The Numba performance debt is correctly localized and documented. The
three mechanical contract gaps (top-k semantics, sentinel rejection,
argmin/argmax/topk canonicalization) are correctly implemented with structural
enforcement and test coverage.

The chain does not authorize release, public speedup, broad RT-core wording,
true-zero-copy wording, hidden dispatch, automatic partner selection,
app-specific native-engine behavior, or user-defined shader injection. The three
low observations above should be addressed before any output-schema, operation-
surface, or partner-coverage claim is published.
