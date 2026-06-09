# Goal4226 Claude Review: Goal4222–4225 Route Policy And Current Scale Packet

Date: 2026-06-09

Reviewer: Claude (independent reviewer, distinct from Codex authoring)

Verdict: **accept-with-boundary**

---

## Summary

The Goal4222–4225 chain is internally consistent, well-scoped, and correctly bounded.
All four goals answer specific route-policy questions with measured evidence from a
clean pod, preserve count parity or signature correctness where applicable, and
carry no claim flags set to true. The target map (Goal4224) and the current-scale
packet (Goal4225) correctly reflect the chain's conclusions. No defects found.
Remaining release work is correctly identified and not glossed over.

---

## Question 1 — Goal4222: Does The Blocked-vs-Unblocked Map Justify Keeping The Unblocked Default?

Yes.

The evidence is direct: all six dataset/scale pairs (clustered3d, road3d, ngsim_dense ×
65 536 and 262 144 points) show the unblocked single-pass grouped-stream execution wins by
3.1x–5.2x. The recommendation to keep `single_pass_candidate_root_rebased` as the current
default and to keep blocked grouped stream explicit is well-supported by the data.

Supporting observations:

- Both modes report identical canonical boundary assignment policy
  (`single_pass_candidate_root_rebased`), confirming the comparison is apples-to-apples.
- Cluster signatures are identical between modes for all rows, confirming semantic
  equivalence even though `--no-validation` is passed (which is acceptable for a profile
  comparison).
- The `blocked_vs_unblocked_elapsed_ratio` is computed from the same `elapsed_sec` fields
  that appear in individual row records; the script logic (`_ratio`) is sound.
- Source commit `63289bbc`, no dirty files.
- Repeat=5, warmup=1 is sparse but the margins are far too large (floor 3.1x) for warmup
  noise to reverse the conclusion. A reviewer asking for more repeats would be right in
  principle but wrong to block on it at these margins.

One minor methodological note: the script runs unblocked before blocked in each pair, which
could give blocked a marginally warmer GPU state. Given the 3–5x margins this has no
practical consequence, but future work comparing shapes within 1.5x should randomize order.

**Conclusion on Q1:** The blocked grouped stream is slower by a factor of 3–5x across all
tested profiles. Keeping unblocked as the default and blocked as explicit/profile-specific
is the correct engineering decision, fully supported by the evidence.

---

## Question 2 — Goal4223: Does The RayJoin Contract Map Justify The Route Split Policy?

Yes.

Seven contract/scale rows with count parity confirmed on each:

- PIP one-shot (bounded public-CDB slice, 246k candidate pairs): Numba is 3.6x faster than
  RTDL/OptiX (`rtdl_optix_speedup_vs_numba = 0.28`). The small slice does not benefit from
  prepared RTDL traversal overhead. Route → Numba. Correct.
- LSI scalar count (12M–136M candidate pairs, three slice sizes): RTDL/OptiX wins by
  25x–262x with growing speedup as candidate volume increases. Route → RTDL/OptiX. Correct.
- Overlay active-count (14k–234k candidate pairs, three slice sizes): RTDL/OptiX wins by
  67x–314x. Route → RTDL/OptiX. Correct.

The speedup magnitudes for LSI and overlay are striking, but they reflect the prepared
RTDL/OptiX session reuse advantage over a per-call Numba JIT path at candidate-pair volumes
where RTDL primitives are well-matched to the workload shape. Count parity on all seven rows
confirms the routes produce the same output. Repeat=20, warmup=3 is adequate for hot-median
stability.

The route is never auto-selected: `recommended_route` is a label on each row, not a
dispatch hook. `automatic_partner_selection_authorized = false` throughout.

**Conclusion on Q2:** The contract map justifies the split. PIP one-shot → Numba at
bounded slice scale. LSI and overlay scalar-count → prepared RTDL/OptiX. The evidence is
consistent with the Goal4218 conclusions and extends them across three slice sizes per
contract type.

---

## Question 3 — Goal4224: Does The Target Map Correctly Classify The Current State?

Yes.

The seven-row target map covers all five required status values and is enforced at the
dataclass level (`__post_init__` raises ValueError if any claim flag is set to true). The
mapping is accurate:

| Target | Assigned Status | Assessment |
| --- | --- | --- |
| `ten_app_current_route_health` | `done_internal_evidence` | Correct. Goal4215 is referenced. |
| `rayjoin_contract_split_route_policy` | `done_internal_evidence` | Correct. Goals4218 + 4223. |
| `rtdbscan_profile_aware_boundary_policy` | `done_internal_evidence` | Correct. Goal4222. |
| `prepared_session_residency_surface` | `available_explicit_not_default` | Correct. Explicit user-owned cache exists; not default. |
| `release_grade_long_run_packet` | `needs_broader_evidence` | Correct. No formal release matrix exists. |
| `amd_hiprt_functional_parity` | `blocked_pending_hardware` | Correct. No AMD pod. |
| `major_release_candidate_packet` | `pending_user_release_decision` | Correct. User decision required. |

The claim boundary string in the module is well-formed and enumerates every forbidden claim
type explicitly. The `validate_current_major_performance_targets` function checks all 5 required
statuses are present and that no target carries any forbidden true flag; the test confirms
this returns `status = "accept"` with no errors.

**Conclusion on Q3:** The map is correct. Route-policy items are correctly marked done.
Release, hardware parity, and long-run matrix items are correctly marked as remaining work.

---

## Question 4 — Goal4225: Is The Ten-App Current Scale Packet Valid And Boundary-Compliant?

Yes.

All ten benchmark front doors pass on a clean pod at commit `0d9786ca` (no dirty files,
confirmed by `working_tree_clean = True` and empty `git_status_short`). The semantic stdout
scan found no claim flag violations in any of the ten stdout payloads. The test confirms this
at two levels: the packet-level flags and each individual stdout payload via recursive
`_forbidden_true_paths`.

The packet correctly uses `internal_current_scale_not_claim_grade` status, not a release
grade. The test checks that this status is present, preventing a silent promotion.

Key policy confirmations visible in the packet:
- RT-DBSCAN: `boundary_assignment_canonical_policy = single_pass_candidate_root_rebased`,
  `grouped_stream_continuation_pass_count = 1` — confirms the unblocked default from
  Goal4222 is live.
- RayJoin: `numba_contracts = ["pip_one_shot"]`, LSI and overlay in
  `rtdl_optix_contracts`, `lsi_scalar_count.rtdl_optix_speedup_vs_numba > 100x` — confirms
  the Goal4223 route split is live.
- `automatic_dispatch = false` and `user_route_choice_visible = true` in the RayJoin
  recommended route summary.

The four scene-heavy rows (hausdorff_xhd, librts_spatial_index, rtnn,
triangle_counting) carry prepared-session residency metadata. The residency record is
correctly labelled `internal_contract_not_release_authorization`.

The commit used for Goal4225 (`0d9786ca`) differs from the commit used for Goal4222/4223
(`63289bbc`). The report explains this: `0d9786ca` is the post-Goal4223 head, and the
runner is `goal3828_current_benchmark_scale_profile_runner.py` which runs the existing
benchmark front doors unchanged. This is the expected production health recheck pattern —
not a mismatch that invalidates the evidence.

**Conclusion on Q4:** The ten-app packet is valid current-state health evidence. It avoids
all forbidden claim types. It confirms the route-policy updates from Goals4222 and 4223 are
active in the production benchmark surface.

---

## Question 5 — Are The Tests Strong Enough To Catch Regressions?

Adequate for the stated scope, with one minor coverage gap.

**Strengths:**

- Goal4222 test: verifies file existence, 6-row scope, correct datasets and scales, canonical
  boundary policy on both modes, unblocked wins every row (ratio > 3.0 threshold), unblocked
  has exactly 1 continuation pass and blocked has the expected 16 or 64. Also loads each
  stdout file and checks `boundary_assignment_policy` there. This is thorough.
- Goal4223 test: verifies 7-row scope, exact recommended_route_counts, PIP speedup < 1.0,
  LSI > 20x, overlay > 60x, count parity on every row, and a boundary string check. The
  threshold assertions would catch route-swap regressions.
- Goal4219/4224 test: verifies all 5 required statuses are present, enforces 7-target count,
  and tests every target for no forbidden true flags. The dataclass enforcement provides
  defence-in-depth.
- Goal4225 test: end-to-end packet check plus per-payload recursive claim-flag scan. The
  test also directly asserts specific policy fields from the rayjoin and rt_dbscan stdout
  payloads, which would catch a silent route regression.

**Minor coverage gap:**

- Goal4222 test does not re-derive `blocked_vs_unblocked_elapsed_ratio` from
  `unblocked.elapsed_sec` and `blocked.elapsed_sec`. If the script had a bug in ratio
  computation that inflated the stored ratio while the raw elapsed values disagreed with the
  3.0 threshold check, the test would not catch it. This is low-risk because the test also
  asserts `unblocked.elapsed_sec < blocked.elapsed_sec` directly, but a tighter test would
  compute `blocked_elapsed / unblocked_elapsed` and compare it to the stored ratio within a
  small tolerance.

- Goal4223 test sets overlay threshold at `> 60.0` for the smallest overlay slice
  (`overlay_county128_soil128`, actual speedup 66.75x). If speedup dropped to 61x this would
  still pass. A tighter bound (e.g., > 50x) would give more headroom without being fragile.
  Not blocking.

**Conclusion on Q5:** Tests are strong enough to catch the most likely overclaim and
route-policy regressions. The minor coverage gap is low-risk and does not require blocking.

---

## Question 6 — What Should Be The Next Major Engineering Target Before A Formal Release Packet?

The target map correctly identifies this. In priority order:

1. **Release-grade long-run timing matrix**: The current evidence is directionally strong but
   each row is measured with 3–20 repeats at short wrapper durations. A formal release packet
   needs longer per-row timing (minutes, not seconds), stability verification across multiple
   pod sessions, and explicit claim wording reviewed at the row level.

2. **Docs and public claim audit**: The benchmark reports and any user-facing documentation
   must be audited for claim wording before any public release. The internal boundary language
   must not leak into published material.

3. **Multi-AI consensus over exact release claims**: The project has used Gemini review
   alongside Claude review during development. A release packet should repeat this over the
   exact public claim wording, not just over internal evidence packets.

4. **AMD/HIPRT functional parity**: Hardware-blocked, but this is the first task once an AMD
   pod is available. No AMD performance claim is permissible before same-contract evidence
   exists on AMD hardware.

The one thing the team should **not** do next is build automatic dispatch. The evidence
establishes where each route wins; the correct next step is to make those boundaries
visible to users via well-documented explicit choice, not hidden heuristics.

---

## Boundary Compliance Check

This review has not authorized:

- Release action
- Public speedup wording
- Whole-app acceleration wording
- Broad RT-core wording
- Paper-reproduction wording (RT-DBSCAN IPDPS 2023 or RayJoin)
- True-zero-copy wording
- Automatic partner selection
- AMD performance wording
- App-specific native-engine logic

---

## Verdict

**accept-with-boundary**

The Goal4222–4225 chain is valid internal route-policy and current-state health evidence.
It may be used as a planning reference for internal engineering decisions. It does not
authorize release action or any public claim. The next required major step before any
formal release packet is a longer-duration timing matrix, a docs/public-claim audit, and
multi-AI consensus over the exact release claim wording.
