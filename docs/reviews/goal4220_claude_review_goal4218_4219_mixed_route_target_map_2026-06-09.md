# Goal4220 Claude Review: Goals4218–4219 Mixed-Route Evidence And Major Target Map

Date: 2026-06-09

Reviewer: Claude (claude-sonnet-4-6), independent review

Verdict: **accept-with-boundary**

---

## Files Reviewed

- `docs/reports/goal4218_mixed_route_focus_after_policy_2026-06-09.md`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/summary_manifest.json`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/rayjoin/summary.json`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/rtdbscan/optix_rt_core_grouped_stream_numba_column_signature_3d.json`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/rtdbscan/optix_rt_core_grouped_stream_blocked_numba_column_signature_3d.json`
- `tests/goal4218_mixed_route_focus_after_policy_test.py`
- `src/rtdsl/current_major_performance_targets.py`
- `docs/reports/goal4219_major_performance_target_map_after_goal4218_2026-06-09.md`
- `tests/goal4219_major_performance_target_map_test.py`

---

## Review Question 1: RayJoin as Contract-Split Route Evidence

**Finding: PASS**

The report, JSON artifacts, and test all correctly scope the RayJoin result as
per-contract route evidence over bounded public-CDB slices. Specific checks:

- `rayjoin/summary.json` carries an explicit `"boundary"` string: "This is not a
  RayJoin paper reproduction, not automatic dispatch, not a public speedup
  claim, and not release evidence."
- The `recommended_route_summary` has `"automatic_dispatch": false` and
  `"user_route_choice_visible": true`.
- The four contracts (PIP one-shot, PIP repeated, LSI scalar count, overlay
  active count) are reported separately with distinct recommended routes; the
  recommended routes differ across contracts, which is the defining property of
  contract-split evidence.
- `rayjoin_paper_reproduction_claim_authorized: false` in all claim-boundary
  blocks.
- The test `test_rayjoin_contract_split_remains_visible` explicitly checks
  `all_contract_counts_match`, the 4-contract count, the Numba vs RTDL/OptiX
  split, and runs `_forbidden_true_paths(summary)` over the full JSON tree.

No whole-app or paper-reproduction language appears anywhere in the artifacts.

---

## Review Question 2: RT-DBSCAN Unblocked vs Blocked for 65k Clustered3D

**Finding: PASS**

The artifact data is internally consistent and supports the stated reading:

| Mode | elapsed_sec | pass_count |
| --- | ---: | ---: |
| unblocked (`grouped_stream_continuation_pass_count = 1`) | 0.096189 | 1 |
| blocked (`grouped_stream_continuation_pass_count = 16`) | 0.436252 | 16 |

Ratio: 0.436252 / 0.096189 ≈ **4.535x** slower for the blocked variant. The
report states this number correctly. Both rows confirm
`boundary_assignment_policy = single_pass_candidate_root_rebased` and
`boundary_assignment_canonical_policy = single_pass_candidate_root_rebased`,
so the canonical-policy state is identical between the two modes; the timing
difference is attributable entirely to the blocked query structure (16 range
passes vs 1 full-item pass).

The test guard `assertGreater(blocked["elapsed_sec"] / unblocked["elapsed_sec"], 4.0)`
matches the observed ratio.

The report correctly qualifies this as a single-profile, single-scale
observation ("for the 65,536 clustered3d scale-profile row") and does not
generalize to all profiles or scales.

---

## Review Question 3: Goal4219 Direction at Generic Language/Runtime Level

**Finding: PASS**

Each entry in `current_major_performance_targets.py` keeps next actions at the
language/runtime or broader evidence level:

- `rayjoin_contract_split_route_policy`: "use larger/non-dense same-contract
  route evidence… do not chase app-only tricks or claim whole RayJoin
  reproduction."
- `rtdbscan_profile_aware_boundary_policy`: "broader profile/scale evidence or
  advisor logic; do not promote blocked/partitioned variants by default without
  shape-specific proof."
- `prepared_session_residency_surface`: "must not enable hidden global caching
  or automatic backend/partner selection."
- `amd_hiprt_functional_parity`: gated on AMD hardware availability, not an
  NVIDIA micro-optimization.
- `major_release_candidate_packet`: gated on user decision and multi-AI
  consensus.

The goal report echoes this: "The purpose is to keep the project focused on
language/runtime improvements, not app micro-tuning."

No target points toward app-specific engine additions or narrow benchmark
micro-tuning as a next action.

---

## Review Question 4: Explicit User Partner Choice Preserved

**Finding: PASS**

Multiple layers enforce this:

1. `CurrentMajorPerformanceTarget.__post_init__` raises `ValueError` if
   `automatic_partner_selection_authorized` or `app_specific_native_engine_logic_allowed`
   is set to True for any target. This is a hard structural constraint; it
   cannot be accidentally bypassed.
2. `validate_current_major_performance_targets` checks every row in the matrix
   for the same flags and returns `status: "reject"` on violation.
3. The test `test_no_target_authorizes_release_or_hidden_dispatch` asserts
   `assertFalse(row["automatic_partner_selection_authorized"])` and
   `assertFalse(row["app_specific_native_engine_logic_allowed"])` for all six
   rows.
4. Both RT-DBSCAN JSON artifacts have `"automatic_partner_selection_allowed": false`
   and `"automatic_hidden_dispatcher": false` in metadata.
5. The RayJoin summary has `"automatic_dispatch": false`.

The `prepared_session_residency_surface` next-action text explicitly calls out
the prohibition on hidden global caching and auto backend/partner selection.

---

## Review Question 5: All Claim Boundaries Remain Closed

**Finding: PASS**

Checked at every artifact layer:

**Manifest (`summary_manifest.json` top-level `claim_boundary`):**
All nine named flags are `false`: `release_authorized`,
`public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`,
`broad_rt_core_speedup_claim_authorized`, `rayjoin_paper_reproduction_claim_authorized`,
`rt_dbscan_paper_reproduction_claim_authorized`, `true_zero_copy_claim_authorized`,
`automatic_partner_selection_authorized`, `app_specific_native_engine_logic_allowed`.

**RayJoin `summary.json`:** The `claim_boundary` object and the
`representative_hot_path_summary` both have all forbidden flags false. The test
`_forbidden_true_paths(summary)` scans the full nested tree for any of the
eleven forbidden keys set to True; result must be empty.

**RT-DBSCAN JSONs:** Both unblocked and blocked payloads carry `claim_boundary`
objects and inline metadata with all forbidden flags false. `_forbidden_true_paths`
scans both full payloads in the test.

**Goal4219 targets:** The dataclass `__post_init__` enforces all eight boundary
flags remain False. The `summarize_current_major_performance_targets` summary
explicitly emits all eight flags as `false` at the top level, independent of
individual row values.

One structural note: the manifest uses `broad_rt_core_speedup_claim_authorized`
while the test's FORBIDDEN_TRUE_FLAGS set also covers `broad_rt_core_claim_authorized`.
The RayJoin summary carries both variants; both are false. The recursive
`_forbidden_true_paths` scan catches either name wherever it appears as True,
so the coverage is complete.

---

## Summary Assessment

Goals4218 and4219 form a coherent, well-bounded internal evidence pair.

Goal4218 correctly scopes the RayJoin measurement as per-contract route
evidence over a bounded public-CDB slice, not as a whole-app or paper-reproduction
result. It correctly shows the unblocked grouped stream outperforms the blocked
variant by ~4.5x on the current 65k clustered3d profile, with both variants
confirmed on the canonical policy.

Goal4219 correctly maps the next major performance directions at the
language/runtime layer, preserves explicit user partner choice as a structural
property enforced in code, and keeps all release and public-claim flags closed
at every layer.

**Verdict: accept-with-boundary**

The "with-boundary" qualifier reflects the proper self-limitation of the
evidence: the RayJoin evidence covers a single public-CDB scale slice; the
RT-DBSCAN comparison covers one dataset and scale profile. Goal4219 correctly
marks both as `needs_broader_evidence`. No additional boundary corrections are
required; the artifacts are internally consistent with the boundaries as stated.
