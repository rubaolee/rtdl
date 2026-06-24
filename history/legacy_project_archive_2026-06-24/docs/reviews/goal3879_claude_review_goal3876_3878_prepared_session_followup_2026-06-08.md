# Claude Review: Goal3876-3878 Prepared-Session Follow-Up

Date: 2026-06-08

Reviewer: Claude (independent read-only review)

Verdict: **accept-with-boundary**

## Summary

This is a follow-up review of the work that landed after my Goal3875 review of
the Goal3872-3874 prepared-session chain
(`docs/reviews/goal3875_claude_review_goal3872_3874_prepared_session_chain_2026-06-08.md`).
Goal3876 attaches the Goal3874 prepared-session residency profiles to the
existing scale-profile runner as metadata, with A5000 evidence. Goal3877 adds
a small, caller-owned `get_or_prepare_explicit_session(...)` helper on top of
the Goal3873 contract. Goal3878 widens the app-specific-term denylist in
direct response to the minor robustness note I raised in Goal3875. I inspected
all eight named files plus `rtdsl/__init__.py` exports, `git show` for all
three commits (`6531d666`, `ac2047d8`, `01d412f4`), and the
`V2_8_PROMOTED_BENCHMARK_APPS` registry the new denylist terms are checked
against.

## Validation

I could not run the requested unittest invocation — every form of `py -3 ...`
and `PYTHONPATH=...` in this session was blocked by the sandbox before
execution (same obstacle noted in the Goal3875 review). I instead
cross-checked the A5000 artifact directly with `grep` against the
field-by-field assertions in `tests/goal3876_..._test.py` (see Finding 2) and
read the Goal3877/3878 test sources line by line against the implementation.
This is a residual verification gap, not a defect in the work.

## Findings (ordered by severity)

No correctness or honesty issues found.

1. **(Info) Goal3876 is genuinely metadata-only — no command or cache-behavior
   change.** `git show 6531d666` shows the runner gained one map-building
   helper (`_prepared_session_profile_map`, restricted to `selected_row_ids`
   so it only resolves profiles for rows actually selected by `--only`) and
   one attach helper (`_attach_prepared_session_profile`,
   `scripts/goal3828_..._runner.py:192-209`) that sets
   `prepared_session_residency_profile` (the profile dict or `None`) and
   `prepared_session_residency_profiled` (a bool) on each row result. Both the
   live and dry-run code paths call `_attach_prepared_session_profile` on
   every row (`:282-285` for dry-run, `:308-313` for live), so unprofiled
   rows explicitly carry `profile=None, profiled=False` rather than omitting
   the keys — confirmed in the artifact (e.g.
   `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` at
   artifact line 289 carries `prepared_session_residency_profiled: false`).
   The diff touches nothing in `_run_row` or the subprocess invocation that
   actually executes benchmark commands — "the command execution path is
   unchanged" (report line 24) is accurate. `_prepared_session_profile_map`
   reads from the existing `current_prepared_session_residency_profiles()`
   registry on every invocation; it builds no cache, stores no state across
   runs, and constructs nothing — there is no hidden cache here, only a
   read-and-attach.

2. **(Info) The A5000 artifact backs every test assertion, and I independently
   verified the claim-boundary fields with `grep`.** I confirmed directly
   against `docs/reports/goal3876_..._a5000/summary.json`:
   `all_pass: true` (line 2), `json_pass_count: 10` (line 7),
   `selected_prepared_session_residency_profile_count: 4` (line 1306),
   `prepared_session_residency_summary.geomean_prepare_to_hot_query_ratio:
   425.19260550877135` (line 14, > 400 as the test requires),
   `prepared_session_residency_validation.status` reachable and consistent
   with `release_authorized: false` at both top level (line 39) and inside
   every attached profile (lines 154, 744, 975, 1190). The four profiled rows
   (`hausdorff_xhd_scale_default_optix_threshold`,
   `librts_spatial_index_optix_scale_default_32768`,
   `rtnn_prepared_optix_scale_default_65536`,
   `triangle_counting_optix_rt_graph_2a1_scale_default_2048` — artifact lines
   227, 817, 1052, 1259) each carry `prepared_session_residency_profiled:
   true` with a profile whose `scale_profile_row_id` matches the row's own
   `row_id`, and every `automatic_partner_selection_authorized`,
   `true_zero_copy_claim_authorized`, and
   `app_specific_native_engine_logic_allowed` field I found in the artifact
   (28 occurrences across nested profile/policy/timing layers) is `false`.
   The remaining six selected rows
   (`spatial_rayjoin_*`, `rt_dbscan_*`, `robot_collision_*`,
   `contact_manifold_*`, `raydb_style_*`, `barnes_hut_*`) all carry
   `prepared_session_residency_profiled: false` with `profile: null` — exactly
   the "explicitly false, not missing" behavior
   `test_selected_unprofiled_row_records_false_not_missing` checks. No claim
   leaks found.

3. **(Info) Goal3877's helper does what the report and tests claim, with
   correctly fail-closed edge cases.** `get_or_prepare_explicit_session`
   (`prepared_session_residency.py:408-446`) type-checks the cache
   (`isinstance(cache, ExplicitPreparedSessionCache)`), requires the caller's
   key to match the policy's key (`policy.cache_key != key` raises
   `ValueError`), calls `prepare_session()` only on a cache miss, type-checks
   that `prepare_session` is callable before invoking it, and returns an
   `RtdlPreparedSessionReuseResult` whose `cache_hit` flag and
   `cache_event_log` make hit/miss visible. I traced
   `test_get_or_prepare_calls_prepare_once_then_reuses` line by line: first
   call → `cache_hit=False`, `calls == ["prepare"]`; second call (same key) →
   `cache_hit=True`, `calls` still `== ["prepare"]`, `second.value is
   first.value`, and the cumulative event log is exactly `("miss", "put",
   "hit")` — this matches `ExplicitPreparedSessionCache.get`/`.put` event
   bookkeeping (`:295-314`) precisely. `RtdlPreparedSessionReuseResult` mirrors
   the same hardcoded-`False` claim-property pattern as
   `RtdlPreparedSessionResidencyPolicy` (compare `:375-389` to `:189-207`):
   `release_authorized`, `public_speedup_claim_authorized`,
   `true_zero_copy_claim_authorized`, and
   `automatic_partner_selection_authorized` are all read-only properties
   returning `False`, not settable fields, so a caller cannot construct a
   "true" claim through this path either. The helper never selects a
   `primitive`, `backend`, `partner`, or `device` — those all come from the
   caller-constructed `key` — and `make_prepared_session_cache_key` (the only
   key constructor) still funnels every `primitive` string through
   `_validate_no_app_terms`.

4. **(Info) Goal3878 directly closes the gap I flagged in Goal3875, and closes
   it completely.** My prior review's minor-robustness note named four
   `V2_8_PROMOTED_BENCHMARK_APPS` entries that substring matching would have
   missed: `robot_collision`, `contact_manifold`, `raydb_style`,
   `librts_spatial_index` (caught only via `librts`), `rtnn`, and
   `triangle_counting` (caught only via `triangle`, which wasn't on the list).
   `git show 01d412f4` adds exactly the missing terms — `hausdorff_xhd`,
   `xhd`, `spatial_rayjoin`, `rt_dbscan`, `barnes_hut`, `raydb`,
   `raydb_style`, `robot_collision`, `contact_manifold`, `librts`,
   `librts_spatial_index`, `rtnn`, `triangle_counting` — and pairs the change
   with a new `subTest` loop in
   `Goal3873PreparedSessionResidencyContractTest` that iterates every entry in
   `V2_8_PROMOTED_BENCHMARK_APPS` and asserts
   `make_prepared_session_cache_key(primitive=f"{app_handle}_prepared_path",
   ...)` raises `ValueError`
   (`tests/goal3873_..._test.py:72-79`). I confirmed by hand that all ten
   `V2_8_PROMOTED_BENCHMARK_APPS` entries
   (`hausdorff_xhd, spatial_rayjoin, rt_dbscan, robot_collision,
   contact_manifold, raydb_style, barnes_hut, librts_spatial_index, rtnn,
   triangle_counting`) now match at least one denylist substring — the test's
   `for app_handle in V2_8_PROMOTED_BENCHMARK_APPS` loop is therefore a
   genuine regression guard against the registry drifting ahead of the
   denylist again, not a tautology, since each `f"{app_handle}_prepared_path"`
   string is checked against the *literal denylist constant*, independent of
   how the list was derived. This is exactly "widen … in a later goal", the
   remedy I suggested, done thoroughly rather than minimally.

## What Remains Before User-Facing Runtime Ergonomics

The framing in both reports — "metadata integration only" (Goal3876) and "this
is still explicit prepared-session reuse, not hidden dispatch" (Goal3877) — is
accurate, and the same gaps I listed in Goal3875 mostly still apply:

- **The scale runner now surfaces residency context, but still as metadata
  riding alongside results, not as runtime behavior** — `cache_enabled` stays
  governed by the Goal3874 profiles' `cache_enabled_by_default=False`, and the
  runner does not construct or use an `ExplicitPreparedSessionCache`.
- **A real example of `get_or_prepare_explicit_session` in a benchmark app
  context would still be the natural next ergonomics step.** I noticed that
  `git log -1` shows a newer commit, `325916fa "Goal3880 add RTNN
  prepared-session residency metadata"`, has already modified
  `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` and
  added `tests/goal3880_rtnn_prepared_session_residency_metadata_test.py` —
  this looks like exactly that next step landing. It is **out of scope for
  this review** (not in the requested file list, and postdates the
  Goal3876-3878 work this review covers); it should get its own independent
  read before being relied upon.
- **A release packet is still required** before any prepare/hot-query ratio
  (the geomean is now 425x, consistent with the four Goal3872 measurements)
  could become public amortization or speedup wording. Every layer continues
  to hardcode that authorization to `false` — `release_authorized`,
  `public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, and
  `automatic_partner_selection_authorized` are all still read-only properties
  returning `False` across `RtdlPreparedSessionResidencyPolicy`,
  `RtdlPreparedSessionTimingRecord`, `ExplicitPreparedSessionCache`, and the
  new `RtdlPreparedSessionReuseResult` — and that should stay true until such
  a packet exists.

## Boundary (if accepted)

This review covers Goal3876 (scale-runner prepared-session profile
integration and A5000 evidence), Goal3877 (the explicit prepared-session reuse
helper), and Goal3878 (the widened app-term denylist) only. It does **not**
authorize: release action, public speedup wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic. Every claim-authorization flag I inspected across the
runner integration, the artifact, the new helper, and the contract module is
hardcoded `False`, derived from a `False`-returning read-only property, or
asserted `False` and structurally validated — this review confirms that the
chain's own framing matches its code and evidence; it does not grant any new
authorization beyond what the modules themselves already (and correctly) deny
themselves.

## Note on Validation

I was unable to run
`tests.goal3877_explicit_prepared_session_reuse_helper_test`,
`tests.goal3876_scale_runner_prepared_session_profile_integration_test`,
`tests.goal3874_current_prepared_session_residency_profiles_test`, or
`tests.goal3873_prepared_session_residency_contract_test` in this session —
every invocation of `py -3 ...` and `py --version`, with or without
`PYTHONPATH`, was blocked by the sandbox requiring approval before it could
run (the same obstacle as in Goal3875). I instead independently re-derived the
artifact-level assertions with `grep` against
`docs/reports/goal3876_scale_runner_profile_integration_a5000/summary.json`
(see Finding 2) and traced the Goal3877/3878 test bodies against the
implementation line by line (Findings 3-4). A live run by a reviewer with an
unsandboxed shell would close this residual gap.
