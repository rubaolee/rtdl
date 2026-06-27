I have read all referenced files. Now I'll write the formal review.

---

## Formal Review: V4 Goal4648 — Partner Promotion Contract With Numeric Bars

**Date:** 2026-06-25
**Reviewer:** Claude (Sonnet 4.6)
**Branch:** codex/v4-tier2-section8
**Verdict:** `accept_goal4648_complete`

---

### Scope

This review covers:

- `future/v4/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.md`
- `future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json`
- `src/rtdsl/v4_partner_promotion_contract.py`
- `src/rtdsl/v4.py` (diff and full file)
- `tests/v4_goal4648_partner_promotion_contract_test.py`
- `future/v4/reviews/goal4647_completion_consensus_and_review_debt_2026-06-25.md` (predecessor chain)

Chain continuity confirmed: Goal4647 closed with `goal4647_complete__goal4648_may_start`, which directly authorizes this work.

---

### Answers to the 7 Questions

**Q1. Is Goal4648 complete enough to start Goal4649?**

Yes. The contract module exists at `src/rtdsl/v4_partner_promotion_contract.py`, exports are wired through `src/rtdsl/v4.py`, numeric bars are frozen as module-level constants, candidate IDs are enumerated, telemetry fields are specified, and the test suite passes. Goal4649 has a complete, code-visible checklist to run against. No design work remains for Goal4649 to invent.

**Q2. Are the CuPy device-array front-door contract and telemetry requirements concrete enough?**

Yes. The `cupy` entry (`device_array_frontdoor_certification`) specifies:

- Four concrete candidate IDs: `cupy_grouped_reduction_device_columns_262144`, `cupy_grouped_reduction_device_columns_524288`, `cupy_segment_polygon_hitcount_prepared_scaling`, `cupy_hausdorff_witness_continuation`.
- Six accepted dtypes: `float32`, `float64`, `int32`, `int64`, `uint64`, `bool`.
- Layout: contiguous 1D or column-major, no Python rows.
- Ownership: caller-owned CuPy CUDA device arrays, same device as V4 session.
- Stream: caller must declare default-stream or explicit-stream mode before the run; Goal4649 must record mode and sync points.
- Output: V4-allocated or caller-provided CuPy device outputs; no hot host materialization.
- Eight required telemetry fields including `host_materialization_in_hot_path`, `stream_mode`, and `output_ownership`.

Tests at lines 19–36 of the test file directly assert the numeric bars and key telemetry fields. These are concrete enough for Goal4649 to execute without re-negotiating scope.

**Q3. Are the fixed Numba continuation boundaries concrete enough, with arbitrary callbacks still blocked?**

Yes. The `numba_fixed` entry (`fixed_continuation_certification`) sets `fixed_operator_only=True`, `arbitrary_callback_supported=False`, and `arbitrary_numba_callback_claim_authorized=False` as frozen dataclass fields. The single accepted signature is `fixed_radius_graph_component_union_3d(device columns) -> component labels`. Compile/cache timing is separated from the hot path. Tests at lines 38–52 assert all of this, including the `compile_cache_timing_boundary` value. Arbitrary callbacks cannot be sneaked in through Goal4650 without overriding a frozen dataclass.

`numba` without `fixed=True` raises `ValueError` (tested at line 59). Barnes-Hut and Tier-3 PTX spike rows are explicitly absent from the `numba_fixed` candidate list and the candidate allowlist test at lines 86–92 confirms they are rejected.

**Q4. Are numeric bars frozen before measurement?**

Yes. The three bars are defined as module-level constants before any measurement:

```python
V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR = 1.20
V4_PARTNER_PROMOTION_PARITY_FLOOR = 0.98
V4_PARTNER_PROMOTION_CORRECTNESS_PARITY = 1.0
```

These are burned into frozen dataclasses (`frozen=True`) at module import time. The JSON records the same values under `default_bars`. Goal4649 and Goal4650 cannot lower or re-negotiate these bars after seeing results because they are not arguments; they are compiled constants. The report states explicitly: "Rows that only prove partner migration or partner parity cannot contribute to `formal_high_performance_v4_supported`."

**Q5. Does the code/test surface prevent partner migration or parity from becoming a fake V4 speed claim?**

Yes. Every contract has `partner_migration_counts_as_v4_speed_win=False` as a frozen field. The test at line 32 asserts `assertFalse(contract["partner_migration_counts_as_v4_speed_win"])` for CuPy, and the test at line 119 loops over all returned contracts asserting `assertFalse(row["partner_migration_counts_as_v4_speed_win"])`. The report reproduces the AM1 lock verbatim: "Partner migration is not a V4 speed win." The JSON encodes the same under `claim_boundaries.partner_migration_counts_as_v4_speed_win: false`. There is no code path that would let a Goal4649/4650 runner bypass these checks without modifying the frozen dataclass definition itself.

**Q6. Does current planner/catalog behavior still fail closed for unmeasured CuPy?**

Yes. The operator catalog at `v4_operator_catalog.py` lists CuPy only as `declared_unmeasured_partners` across all operator surfaces (verified in the grep output). The test at lines 94–100 asserts that `plan_v4_operator_request("grouped_i64", partner="cupy")` returns `status="tier2_declared_unmeasured_partner"`, `api_surface=None`, `measured_partner=False`, `cupy_performance_claim_authorized=False`, and `broad_v4_speedup_claim_authorized=False`. No CuPy API surface is exposed. Goal4648 added no new planner logic that widens this gate.

**Q7. Are there any blocking issues before Goal4649 CuPy certification work starts?**

No blocking issues. The contract is code-visible and tested, bars are frozen, candidate IDs and telemetry requirements are enumerated, and 31 tests pass. One incidental observation: Goal4648 also changed `V4_AUTHORIZED_RELEASE_LABEL` from "formal high-performance generic RT-core operator release" to "bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines." This is a tightening (it names a specific operator count and explicit comparison baseline), not an expansion. It does not create a blocking issue.

---

### Non-Authorization Confirmation

| Prohibited claim | Code field | Value confirmed |
|---|---|---|
| Public release/tag wording | `release_claim_authorized` | `False` in both contracts and JSON |
| Broad V4 speedup language | `broad_v4_speedup_claim_authorized` | `False` in both contracts and JSON |
| App-level V4-vs-V2.14/V3 claims | `whole_app_speedup_claim_authorized` | `False` in both contracts and JSON |
| CuPy performance claims | `cupy_performance_claim_authorized` | `False` in both contracts and JSON |
| Arbitrary Numba callback claims | `arbitrary_numba_callback_claim_authorized` / `arbitrary_callback_supported` | `False` in both contracts and JSON |
| C ABI / embedding claims | `embedding_c_abi_claim_authorized` | `False` in existing `claim_boundary_v4()` front-door (unchanged by Goal4648) |
| POD benchmark spending | `pod_spend_authorized` | `False` in JSON `claim_boundaries` block |
| Partner migration/parity as V4 speed evidence | `partner_migration_counts_as_v4_speed_win` | `False` in both contracts, in JSON, and asserted over all rows in tests |

All eight prohibited items are confirmed non-authorized. None are introduced or unlocked by Goal4648.

---

### Observations (non-blocking)

1. The `v4_partner_promotion_candidate_allowed` function iterates all contracts when `partner="numba"` and skips non-`numba_fixed` keys. The logic is correct but would silently pass through any future numba contract key not named `numba_fixed`. This is low-risk because the key set is small and frozen at this goal, but Goal4650 should not introduce a second Numba key without revisiting this function.

2. The CuPy `fixed_operator_only=True` field in the contract is technically true for what Goal4649 will measure, but CuPy is not a fixed-operator system in the same sense as the Numba `fixed_continuation_certification`. This field should not be relied upon to make categorical claims about CuPy's general capability scope in future goals.

Neither observation is a defect requiring correction before Goal4649 starts.

---

### Verdict

`accept_goal4648_complete`

Goal4648 produced a code-visible, test-covered partner promotion contract with frozen numeric bars before any partner certification run. All seven questions are answered affirmatively. Non-authorization boundaries are confirmed in the contract code, JSON evidence, and test assertions. Goal4649 CuPy certification work may start against the frozen contract.
