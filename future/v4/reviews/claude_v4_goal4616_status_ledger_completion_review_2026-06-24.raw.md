---

## Verdict: `accept_goal4616_implementation_complete_pending_3ai_debt`

### Exit Gate: Pass

All three goal4616 exit conditions are satisfied:

1. **Status ledger exists and matches code/catalog evidence.** Cross-checked `v4_operator_catalog.py` (3 measured surfaces with `measured_partners: ("torch",)`, 2 candidates with `measured_partners: ()`), `v4.py` front door (3 measured, 2 candidates, all claim flags False), `tier2_operator_catalog.md`, `README.md`. No discrepancies.

2. **Dry-run catalog gate passed.** Confirmed from the JSON evidence: `status: "passed"`, `release_authorized: false`, `measured_surface_count: 3`, `candidate_surface_count: 2`. All 9 examples passed including both candidates.

3. **No claim-status changes introduced.** Ledger makes no promotions, no release assertions, no speedup claims.

### No Classification Drift

Grouped-i64 stays candidate with R1–R4 open. Point-group stays candidate; amendment closure ≠ promotion. Catalog code and ledger are consistent.

### Non-Blocking Wording-Debt Nuance (carry to `goal4621`)

The ledger characterizes the `true_zero_copy_authorized` issue as "sub-field wording debt" but the reality is sharper: when `prepare_optix_fixed_radius_count_threshold_2d_device_search_columns` is called (the live V4 device-array factory at `optix_runtime.py:9165`), it sets `_search_scene_true_zero_copy = True`, causing the hot-path to emit **top-level `true_zero_copy_authorized: True`** from the measured fixed-radius surface. This is not dead code. It is pre-existing, not introduced by goal4616, and the ledger correctly flags it as requiring audit before promotion or release. But it should be addressed explicitly — not just as sub-field debt — in `goal4621` or before any fixed-radius promotion gate.

### 3-AI Consensus Status

- Codex seat: present
- Claude seat: **this review** (second seat)
- Third seat: open debt

### Goal4617 Authorization

**Codex may begin `goal4617`** after recording third-seat debt for `goal4616`. The two-seat consensus pattern established for `goal4615` applies here identically.
: false`
- All 9 examples passed: 3 measured, 2 candidates, frontdoor quickstart,
  tier2 planning, scalar-callback (tier3_spike_only), complex-callback
  (rejected_action_shaped_callback_deferred)

### 3. Local unit tests (35) claimed passed

Accepted as stated in the ledger. No GPU execution is required for this
dry-run-only goal. The test suite composition (v4_operator_catalog_test,
v4_frontdoor_test, v4_ray_triangle_device_array_api_test,
v4_point_group_device_array_api_test, v4_scope_gate_test,
v4_release_candidate_packet_test, v4_catalog_regression_gate_test,
v4_point_group_nearest_witness_device_outputs_validation_test) covers the
surface boundaries this goal audits.

### 4. No claim-status changes introduced

Verified. The ledger does not:
- promote grouped-i64 or point-group from candidate to measured
- increase measured surface count from 3
- assert any release, speedup, true-zero-copy, Tier-3, or C-ABI claim

## Grouped-I64 R1–R4 Debt: Correctly Recorded

The ledger records R1–R4 from the earlier Claude grouped-i64 candidate review
without marking them resolved. This is correct. R1–R4 remain open and are
gated on `goal4617`.

## Point-Group Amendment Closure: Correctly Recorded

The ledger records A1–A3 closure from the Claude amendment closure review
without treating it as automatic promotion. Amendment closure ≠ promotion. The
ledger states this explicitly. Correct.

## Non-Blocking Wording-Debt Nuance (Carry Forward to `goal4619`/`goal4621`)

The ledger characterizes the wording debt as "some grouped-union and
fixed-radius paths still contain older `*_true_zero_copy_authorized`
sub-field wording." This is slightly soft.

What the code actually shows (`optix_runtime.py` lines 9185, 9242):

When `prepare_optix_fixed_radius_count_threshold_2d_device_search_columns`
is called — which is the V4 device-array factory for the measured
`v4_fixed_radius_count_threshold_2d_device_arrays` surface — it sets
`_search_scene_true_zero_copy = True`. This causes the hot-path metadata at
lines 5939, 6097 to emit `"true_zero_copy_authorized": True`, and
sub-fields `query_point_columns_true_zero_copy_authorized: True` and
`output_columns_true_zero_copy_authorized: True` also fire (lines 5935, 5937,
6092, 6094).

This is not just old dead-code wording. It is the top-level
`true_zero_copy_authorized: True` emitted from the live measured V4 surface
when the device-search-column prepare path is used. The goals plan forbids
the public "true zero-copy" wording without a separate authorizing review.
The current wording is in internal runtime metadata rather than public-facing
documentation, and `rt_core_speedup_claim_authorized: False` is correctly
set alongside it. However, this should be explicitly addressed — not just
characterized as sub-field debt — before the fixed-radius surface is included
in any promotion or release wording review.

This is pre-existing, not introduced by `goal4616`. The ledger discloses it
as requiring audit before promotion or release wording, which is correct. It
does not block `goal4616`. It should be explicitly addressed in `goal4621`
(Tier-2 catalog hardening) or earlier if the fixed-radius surface is involved
in a promotion gate before that.

## Claim-Status Classification Drift: None

No classification drift detected. The catalog code, front door, catalog
markdown, README, and dry-run evidence are internally consistent. All surfaces
that are candidate in the ledger are candidate in the code; all that are
measured in the ledger are measured in the code.

## 3-AI Completion Consensus Status

- Codex implementation/audit seat: present
- Claude external completion review: this document (second seat)
- Third external completion review: open debt

`goal4616` is implementation-complete with two-seat consensus. Third-seat
debt must be recorded before `goal4616` is marked fully closed. This follows
the same debt-allowed pattern established for `goal4615`.

## Authorization Boundary

This review authorizes:
- Recording `goal4616` as implementation-complete pending third-seat debt
- Codex beginning `goal4617`

This review does not authorize:
- V4 release
- Measured-catalog promotion of grouped-i64 or point-group
- Broad V4 speedup wording
- Whole-app speedup wording
- True-zero-copy public wording
- Tier-3 callback support
- Raw OptiX callback support
- Embedding/C-ABI/non-Python host work
- App-specific native kernels
