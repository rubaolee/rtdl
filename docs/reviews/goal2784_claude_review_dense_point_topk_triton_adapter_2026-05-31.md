# Independent Review — Goal2784: Dense Point Top-K Triton Adapter Kernel

**Reviewer:** Claude (independent, read-only)
**Date:** 2026-05-31
**Verdict: `accept-with-boundary`**

---

## Scope

This is an independent review of Goal2784 against the five questions in the
handoff document. Evidence inspected:

- `src/rtdsl/triton_partner_continuation.py` — adapter implementation and kernel
- `src/rtdsl/partner_adapters.py` — public adapter front door
- `src/rtdsl/v2_5_partner_selection_guidance.py` — refreshed planner guidance
- `src/rtdsl/v2_5_triton_app_migration.py` — refreshed app migration plan
- `tests/goal2784_dense_point_topk_triton_adapter_kernel_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `docs/reports/goal2784_dense_point_topk_triton_adapter_kernel_2026-05-31.md`
- `docs/reports/goal2784_pod_artifacts/goal2784_dense_point_topk_triton_adapter_pod_69_30_85_171_2026-05-31.json`

---

## Question 1: Does Goal2784 preserve the same exact dense 2D point top-k contract as the Torch branch?

**Finding: Yes.**

The adapter front door `top_k_nearest_points_2d_partner_columns`
(partner_adapters.py:1856) produces identical columns regardless of whether
`partner="triton"` or `partner="torch"`: `query_ids`, `neighbor_ids`,
`distances` (Euclidean, not squared), and `neighbor_rank` (1-indexed). Both
branches share the same `tie_break: "distance_then_candidate_id"` contract.

The Triton kernel (`_triton_dense_point_topk_2d_kernel`,
triton_partner_continuation.py:1820) implements the tie-break correctly: for
each rank it finds `best_score = tl.min(...)` over unselected candidates, then
`best_id = tl.min(cids where score==best_score)` for exact ties. This matches
the Torch branch which stable-sorts by distance after pre-sorting candidates by
id ascending.

The POD artifact confirms `same_neighbor_ids: true`, `same_neighbor_rank: true`,
`same_query_ids: true` for all four measured shapes (2/3/k=2, 256/512/k=8,
512/1024/k=8, 1024/2048/k=8). Floating-point distance differences are at or
below double-precision epsilon (max_distance_abs_error ≤ 1.39e-17).

The CUDA conformance test `test_dense_adapter_kernel_matches_torch_same_contract_when_cuda_available`
independently verifies this on live hardware.

---

## Question 2: Does the Triton adapter kernel actually avoid dense score materialization?

**Finding: Yes.**

The Torch branch materializes a full `(query_count × candidate_count)` score
matrix (`dx * dx + dy * dy`, partner_adapters.py:1901). The Triton kernel
avoids this entirely. Each program receives one query and loads the full
candidate array into a single Triton block (`offsets = tl.arange(0, BLOCK_SIZE)`
where `BLOCK_SIZE = next_power_of_2(candidate_count)`). Squared distances are
computed in-register on the block and reduced with `tl.min` and `tl.where` —
no intermediate matrix is written to global memory.

The result metadata explicitly records `"score_materialization": "none"`
(triton_partner_continuation.py:1269), which the test
`test_dense_adapter_kernel_is_present_without_rt_traversal_claims` asserts
and which the POD artifact confirms as `v2_5_triton_score_materialization: "none"`.

One honest limit: the kernel requires `block_size = next_power_of_2(candidate_count)`,
and raises a hard error if this exceeds `max_candidate_block_size` (default
4096). This bounds the adapter to small-to-medium dense candidate sets, which
is consistent with the stated scope and is a correctness guard rather than a
deficiency.

---

## Question 3: Is the performance evidence recorded honestly, including the fact that Triton improved substantially over Goal2780 but remains slower than Torch?

**Finding: Yes. The evidence is honest and complete.**

The POD artifact (RTX A5000, torch 2.8.0+cu128) shows:

| Query | Candidates | k | Triton median (s) | Torch median (s) | Ratio |
|------:|----------:|--:|------------------:|-----------------:|------:|
|     2 |         3 | 2 | 0.003876          | 0.000400         | 9.68x |
|   256 |       512 | 8 | 0.003960          | 0.000402         | 9.85x |
|   512 |      1024 | 8 | 0.004068          | 0.000405         | 10.04x |
|  1024 |      2048 | 8 | 0.004248          | 0.000866         | 4.91x |

The report names the improvement directly: "removes dense score materialization
and cuts the old Goal2780 slowdown from 47x-151x to 4.9x-10.0x on the
measured RTX A5000 shapes." The guidance row records `measured_partner_slower_min_ratio=4.91`
and `measured_partner_slower_max_ratio=10.04`, matching the POD table.

The report decision is `accept-with-boundary` with explicit text: "It is not
promoted as the selected dense top-k performance path because Torch remains
faster." No gap is papered over.

The improvement is genuine and non-trivial (roughly 5–15x from the Goal2780
baseline), but the remaining gap vs Torch (5–10x) is faithfully recorded as an
ongoing constraint. No selective reporting is observed.

---

## Question 4: Does the refreshed Goal2782/Goal2783 planner guidance remain advisory only?

**Finding: Yes. Advisory-only is structurally enforced.**

`V25PartnerSelectionGuidanceRow.__post_init__` (v2_5_partner_selection_guidance.py:40)
raises `ValueError` if any of `auto_select_measured_partner_allowed`,
`promoted_performance_path`, `public_speedup_claim_authorized`,
`rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`,
`true_zero_copy_claim_authorized`, or `release_readiness_authorized` is `True`.
This makes advisory-only a hard invariant at the data-class level, not just
a documentation convention.

At the guidance aggregate level: `planner_policy: "advisory_only_explicit_app_partner_choice"`,
`no_partner_forced: True`, all claim flags `False`.

The refreshed Goal2782 row now records `evidence_goal: "Goal2784"` (replacing
the older Goal2780 reference) with ratios 4.91–10.04x. The recommendation
explicitly says "Do not auto-select Triton for dense exact top-k ranking."

The Goal2783 migration plan correctly propagates this negative guidance into
the `rtnn` app plan: `measured_negative_preview_guidance_count: 1`,
`auto_select_preview_partner_allowed: False`. The `barnes_hut` app likewise
carries its Goal2781 negative guidance. Apps without measured guidance
(`raydb_style`, `spatial_rayjoin`, `hausdorff_xhd`, `rt_dbscan`) correctly
have `partner_selection_guidance: ()` — no false claims are inherited.

Tests `test_guidance_validates_and_keeps_claims_blocked` and
`test_migration_plan_consumes_partner_selection_guidance` exercise the full
validation pipeline.

---

## Question 5: Are RT-core, true-zero-copy, whole-app, public speedup, and release claims still blocked?

**Finding: Yes. All five remain blocked at every layer.**

**Kernel/dispatcher layer** (`_triton_run_result`, triton_partner_continuation.py:1446):
every Triton continuation result unconditionally sets
`rt_core_speedup_claim_authorized: False`, `replaces_rt_traversal: False`,
`promoted_performance_path: False`. The dense adapter result inherits these.

**Descriptor layer** (`_base_triton_descriptor`, line 440): sets
`replaces_rt_traversal: False`, `promoted_performance_path: False`. No
`rt_core_speedup_claim_authorized: True` anywhere in the file.

**Adapter metadata layer** (partner_adapters.py:1969-1972):
`rt_core_speedup_claim_authorized: False`, `direct_device_handoff_authorized: False`,
`v2_0_release_authorized: False`, `whole_app_speedup_claim_authorized: False`.

**POD artifact** (claim_boundary block): all five claim flags are explicitly
`false` in the recorded JSON.

**Report** (boundary section): explicitly lists what this goal does not
authorize, including "public speedup claims", "RT-core speedup claims",
"true zero-copy claims", "whole-app speedup claims", "v2.5 release readiness".
The statement "This is not an RT-core speedup claim" appears in the final
paragraph.

**Group validation** (`validate_v2_5_partner_selection_guidance`,
v2_5_partner_selection_guidance.py:198): checks every top-level claim field and
returns `status: "reject"` if any are non-False. The test suite confirms
`status: "accept"`.

No escalation toward any of the five blocked claim categories is observed.

---

## Additional Observations

**Kernel correctness boundary:** The `tl.static_range(0, K)` loop iterates
over ranks at compile time with K as `tl.constexpr`. For each rank it scans
the entire candidate block, so the kernel is `O(K × candidate_count)` per
query program. This is correct and sufficient for the measured shapes, but it
means Triton's JIT cache will have one compiled variant per distinct K value.
Not a defect, but worth noting for future scaling.

**`true_zero_copy_claim_authorized`:** All group-id-bounds validation metadata
blocks (`_triton_group_id_bounds_validation_metadata`, line 1485) explicitly
set `true_zero_copy_claim_authorized: False` regardless of mode. The dense
point top-k adapter uses `TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE` (no group-id
bounds involved) and the claim remains blocked there too.

**No RT-traversal entanglement:** The kernel metadata sets
`native_engine_row_contract: "not_called_partner_reference_only"` and
`replaces_rt_traversal: False`. The adapter takes caller-supplied point columns,
never calls into the RTDL/OptiX native engine, and is correctly labeled as a
partner-side-only path.

---

## Verdict

**`accept-with-boundary`**

Goal2784 delivers a genuine, correctly bounded improvement: the dense point
top-k adapter now avoids score materialization and reaches 4.9x-10x of the
Torch baseline, down from the 47x-151x of Goal2780. The same-contract output
is verified on pod. The evidence is recorded honestly. All five blocked claim
categories remain blocked. The planner guidance is advisory-only and
structurally enforced. The boundary is clearly drawn and coherent.

The goal should not be promoted beyond `accept-with-boundary` because Torch
remains substantially faster (4.9x-10x) on the measured shapes, and the
adapter is correctly classified as a preview improvement, not a promoted
performance path.
