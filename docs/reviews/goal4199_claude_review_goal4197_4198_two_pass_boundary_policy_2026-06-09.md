# Goal4199: Claude Review — Goal4197/Goal4198 Two-Pass Boundary Policy

Date: 2026-06-09
Reviewer: Claude (claude-sonnet-4-6), independent read-only review
Verdict: **accept-with-boundary**

---

## Scope

This review covers the Goal4197/Goal4198 chain: the addition of an explicit
`boundary_assignment_policy="lowest_component_root_two_pass"` option to the
generic OptiX+Numba fixed-radius grouped-stream front door, and the RTX 4000
Ada pod evidence that the policy executes and records pass count `2`.

Files inspected:

- `docs/reports/goal4197_predicate_boundary_lowest_root_two_pass_policy_2026-06-09.md`
- `docs/reports/goal4198_predicate_boundary_two_pass_policy_pod_evidence_2026-06-09.md`
- `docs/reports/goal4198_predicate_boundary_two_pass_policy_pod_rtx4000ada/two_pass_clustered_smoke.stdout.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `tests/goal4197_predicate_boundary_lowest_root_two_pass_policy_test.py`
- `tests/goal4198_predicate_boundary_two_pass_policy_pod_evidence_test.py`

---

## Question 1: Native Engine App-Agnosticism

**Finding: Pass.**

The native kernel struct is `FixedRadiusGroupedUnion3DRtParams` with fields
`predicate_flags`, `parent_out`, `fallback_candidate_out` — all generic. A
full search of `rtdl_optix_core.cpp` for `dbscan`, `DBSCAN`, `clustering`,
`cluster`, and `app_specific` returned zero matches. The exported native
symbol used by both policies is:

```
rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs
```

The boundary-policy names (`lowest_candidate_then_root`,
`lowest_component_root_two_pass`) are Python-layer metadata annotations in
`partner_adapters.py`. They are never embedded in any native ABI name,
kernel parameter, or C++ symbol. The `find_grouped_union_root_readonly`
function and `atomicMin(params.fallback_candidate_out + source, target_root)`
write path are purely geometric: they refer to component roots, not to any
application concept.

No issue.

---

## Question 2: Policy Explicitness and No Hidden Dispatch

**Finding: Pass.**

Three independent enforcement layers prevent accidental activation:

1. **Dataclass guard** (`V28FixedRadiusGraphComponentPlan.__post_init__`,
   `v2_8_fixed_radius_graph_component_front_door.py:189-195`): the policy
   string must be in the admitted tuple; `lowest_component_root_two_pass`
   raises `ValueError` when `partner != "numba"`.

2. **PreparedOptixNumba constructor guard** (`partner_adapters.py:7103-7108`):
   independently re-validates the policy string at construction time.

3. **CuPy negative test** (`goal4197_…_test.py:34-44`): asserts that passing
   `partner="cupy"` with the two-pass policy raises `ValueError` with message
   `"requires partner='numba'"`.

The plan metadata fields `automatic_partner_selection_allowed=False` and
`hidden_dispatch_allowed=False` are structurally enforced: the dataclass
`__post_init__` loop (`v2_8_fixed_radius_graph_component_front_door.py:198-210`)
raises `ValueError` if any of these authorization flags is set to `True`.

The default remains `"lowest_candidate_then_root"` at every call site. The
`describe_v2_8_fixed_radius_graph_component_front_door()` surface
(`front_door.py:310-311`) correctly exposes both supported policies in
`supported_boundary_assignment_policies`.

No issue.

---

## Question 3: Goal4198 Evidence Scope

**Finding: Pass.**

Both policy records in `two_pass_clustered_smoke.stdout.json` carry:

```json
"public_speedup_claim_authorized": false,
"true_zero_copy_claim_authorized": false
```

The Goal4198 report includes an explicit **Timing Boundary** section that
states: *"Goal4198 does not use them as performance evidence. The default
policy ran first and paid setup/JIT costs, while the two-pass policy ran
after warmup."* The test `test_report_states_timing_is_not_perf_evidence`
verifies this disclaimer is present and the key phrases are in the report.

The report's **Release Boundary** section explicitly excludes release
authorization, speedup claims (public, RT-core, whole-app), zero-copy claims,
automatic partner selection, and app-specific logic.

The claims made are confined to:
- the policy executes on RTX 4000 Ada against the rebuilt OptiX library;
- the native pass-count metadata is recorded correctly.

These are the minimal and appropriate claims for a first pod smoke run.

One observation on the timing data: the `prepare_elapsed_sec` values diverge
significantly (`0.836 s` default vs `0.034 s` two-pass). The two-pass policy
ran after JIT warmup, so the default appears more expensive than it actually
is at steady state. The report correctly flags this. No claim boundary
violation, but reviewers should not use these numbers for any downstream
comparison without a re-run in randomized order.

No issue.

---

## Question 4: Artifact Credibility

**Finding: Pass with one observation.**

The clustered artifact provides the following for both policies against the
same 16,384-point `clustered3d` fixture at radius `0.035`, threshold `16`:

| | Default | Two-pass |
|---|---|---|
| `native_boundary_assignment_pass_count` | 1 | 2 |
| `flag_true_count` | 16,314 | 16,314 |
| `negative_label_count` | 2 | 2 |
| `component_count` | 4 | 4 |
| `largest_component_size` | 4,096 | 4,096 |
| `label_count_signature_head` | [4094, 4096, 4096, 4096] | [4094, 4096, 4096, 4096] |
| `same_counts_only_signature` | (combined) | true |
| `native_symbol` | same | same |

The pass counts are exactly as designed in `partner_adapters.py` (lines
7250-7264 for query-blocked path, 7307-7342 for full path): the two-pass
branch calls the native RT continuation twice with a workspace reset between
them.

**Observation — `native_lowest_component_root_after_two_prepared_rt_passes: null`**

This field appears in both policy records with value `null`. In the code
(`partner_adapters.py:7340`) the string
`"lowest_component_root_after_two_prepared_rt_passes"` is the
`fallback_candidate_policy` label for the two-pass route. Its appearance as
a standalone JSON key with `null` under the default policy record suggests
the smoke script included the field unconditionally regardless of which policy
ran. This is a minor artifact-structure inconsistency — not a functional issue,
but it could mislead a reader who expects this field to be absent under the
default policy. It has no bearing on the pass-count evidence.

The artifact is credible evidence for the stated scope: the native route
records pass count `1` under the default policy and `2` under the two-pass
policy, both using the same symbol, with identical counts-only signature.

---

## Question 5: Requirements Before Policy Promotion

The following are required before `lowest_component_root_two_pass` can become
a promoted default or a release-facing RT-DBSCAN route:

**Correctness (required, not yet demonstrated):**

1. **Same-contract validation against the Goal4194 reference on the pod.**
   The pod run confirmed counts-only signature parity. It did not run the
   `predicate_aware_boundary_union` reference contract from Goal4194 against
   the two-pass output. The correctness of individual boundary-point
   assignments relative to the reference is unverified on hardware. This is
   the single most important gap.

2. **Component-size signature match (not just counts-only).** Goal4190
   established that counts-only parity is insufficient — component-size
   signatures can diverge while counts match. A promotion-gating test must
   compare component-size signatures between the two-pass policy and the
   Goal4194 reference on both dense and sparse fixtures.

3. **Multi-run determinism check.** The atomic operations in
   `find_grouped_union_root_readonly` / `atomicMin` can produce different
   root states across runs if the BLAS traversal order is non-deterministic.
   A minimum of three repeated runs should confirm identical output columns.

**Performance (required for default promotion, not for preview continuation):**

4. **Randomized-order repeated benchmark** on dense and sparse distributions,
   fully warmed, with the default policy and the two-pass policy alternating
   to eliminate JIT-cost bias. The current artifact timing is not usable for
   this comparison.

5. **Comparison against the counts-only shortcut from Goal4190.** The
   two-pass policy adds a second RT pass; the counts-only route avoids
   boundary assignment entirely. The tradeoff must be quantified before a
   default policy decision is made.

**Structural (informational, not blocking preview continuation):**

6. The `native_lowest_component_root_after_two_prepared_rt_passes: null`
   field in the default-policy artifact record should be removed or set
   conditionally, to avoid reader confusion in future artifact comparisons.

---

## Summary

Goal4197 correctly adds an explicit, user-selected boundary-assignment policy
knob to the generic grouped-stream front door without embedding any
app-specific concept in the native ABI. Goal4198 correctly records first pod
evidence that the policy activates and records pass count `2`, while keeping
all claim boundaries false.

The work is well-scoped and the evidence is appropriate for a preview policy.
The remaining gap before promotion — same-contract validation on hardware
against the Goal4194 reference — is accurately described in both reports as
"next pod work."

**Verdict: accept-with-boundary**

Accept the chain as a preview policy addition. Require same-contract
validation against Goal4194, component-size signature parity, multi-run
determinism, and a fair timing comparison before the two-pass policy is
considered for default or release promotion.
